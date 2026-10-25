-- Immutable quarantine versions, leased jobs, fencing and reauthorization at publication/read.
CREATE FUNCTION platform.upload_create(token bytea,iid uuid,oid uuid,qkey uuid,expected_hash bytea,size bigint,mime text,wrapped text,meta text,command uuid,body_digest bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app,platform AS $$
DECLARE ctx jsonb:=platform.reporter_context(token); org uuid; cid uuid; scope_name text; prior platform.reporting_commands; result jsonb;
BEGIN
 IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 org:=(ctx->>'organization_id')::uuid; cid:=(ctx->>'case_id')::uuid; scope_name:='upload:'||(ctx->>'access_id');
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||command::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND reporting_commands.command=upload_create.command;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN prior.response; END IF;
 PERFORM 1 FROM app.cases WHERE organization_id=org AND id=cid FOR UPDATE;
 IF size NOT BETWEEN 1 AND 5242880 OR mime NOT IN ('image/jpeg','image/png','image/webp') OR octet_length(expected_hash)<>32 OR (SELECT count(*) FROM app.upload_intents WHERE organization_id=org AND case_id=cid AND state<>'expired')>=10 THEN RAISE EXCEPTION 'quota or format' USING ERRCODE='P0422'; END IF;
 INSERT INTO app.upload_intents(organization_id,id,case_id,owner_access_id,max_bytes,allowed_mime,nonce_hash,expires_at,state) VALUES(org,iid,cid,(ctx->>'access_id')::uuid,size,ARRAY[mime],digest(iid::text,'sha256'),now()+interval '10 minutes','pending');
 INSERT INTO platform.upload_metadata(organization_id,case_id,intent_id,object_id,expected_hash,expected_bytes,expected_mime,quarantine_key,wrapped_key,metadata_ciphertext) VALUES(org,cid,iid,oid,expected_hash,size,mime,qkey,wrapped,meta);
 result:=jsonb_build_object('id',iid,'expires_at',now()+interval '10 minutes');
 INSERT INTO platform.reporting_commands VALUES(scope_name,command,body_digest,result,now());
 PERFORM platform.reporting_audit(org,(ctx->>'access_id')::uuid,'upload.intent',cid);
 RETURN result;
END $$;
CREATE FUNCTION platform.upload_get(token bytea,iid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE ctx jsonb:=platform.reporter_context(token); result jsonb;
BEGIN
 IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 SELECT to_jsonb(m)||jsonb_build_object('state',u.state) INTO result FROM platform.upload_metadata m JOIN app.upload_intents u ON u.organization_id=m.organization_id AND u.id=m.intent_id WHERE m.organization_id=(ctx->>'organization_id')::uuid AND m.case_id=(ctx->>'case_id')::uuid AND m.intent_id=iid AND u.owner_access_id=(ctx->>'access_id')::uuid AND u.expires_at>now() AND u.state IN ('pending','uploaded','scanning','ready','rejected');
 IF result IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 RETURN result;
END $$;
CREATE FUNCTION platform.upload_bind(token bytea,iid uuid,version text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE m jsonb:=platform.upload_get(token,iid);
BEGIN
 IF m->>'state'<>'pending' OR version IS NULL OR length(version)>128 THEN RAISE EXCEPTION 'conflict' USING ERRCODE='P0409'; END IF;
 UPDATE app.upload_intents SET state='uploaded',object_version=version WHERE organization_id=(m->>'organization_id')::uuid AND id=iid AND state='pending';
 IF NOT FOUND THEN RAISE EXCEPTION 'conflict' USING ERRCODE='P0409'; END IF;
 UPDATE platform.upload_metadata SET quarantine_version=version WHERE organization_id=(m->>'organization_id')::uuid AND intent_id=iid;
END $$;
CREATE FUNCTION platform.upload_complete(token bytea,iid uuid,version text,checksum bytea) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE m jsonb:=platform.upload_get(token,iid); org uuid:=(m->>'organization_id')::uuid; cid uuid:=(m->>'case_id')::uuid; rev bigint; gen bigint;
BEGIN
 IF m->>'state' IN ('scanning','ready') AND version=m->>'quarantine_version' AND checksum=decode(substr(m->>'expected_hash',3),'hex') THEN RETURN; END IF;
 IF m->>'state'<>'uploaded' OR version<>m->>'quarantine_version' OR checksum<>decode(substr(m->>'expected_hash',3),'hex') THEN RAISE EXCEPTION 'version mismatch' USING ERRCODE='P0409'; END IF;
 SELECT revision,deletion_generation INTO rev,gen FROM app.cases WHERE organization_id=org AND id=cid AND deleted_at IS NULL FOR UPDATE;
 UPDATE app.upload_intents SET state='scanning' WHERE organization_id=org AND id=iid AND state='uploaded';
 IF NOT FOUND THEN RAISE EXCEPTION 'conflict' USING ERRCODE='P0409'; END IF;
 INSERT INTO app.jobs(organization_id,case_id,type,schema_version,aggregate_id,aggregate_revision,dedup_key,deletion_generation) VALUES(org,cid,'media.scan',1,iid,rev,iid,gen);
 PERFORM platform.reporting_event(org,cid,'media.uploaded',iid);
END $$;
CREATE FUNCTION platform.media_lease() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE j app.jobs; fence uuid:=gen_random_uuid(); result jsonb;
BEGIN
 SELECT * INTO j FROM app.jobs WHERE type='media.scan' AND ((state='pending' AND next_attempt_at<=now()) OR (state='leased' AND lease_until<now())) AND attempts<5 ORDER BY next_attempt_at,id LIMIT 1 FOR UPDATE SKIP LOCKED;
 IF NOT FOUND THEN RETURN NULL; END IF;
 UPDATE app.jobs SET state='leased',lease_until=now()+interval '90 seconds',attempts=attempts+1 WHERE organization_id=j.organization_id AND id=j.id;
 UPDATE platform.upload_metadata SET lease_token=fence WHERE organization_id=j.organization_id AND intent_id=j.aggregate_id;
 SELECT to_jsonb(m)||jsonb_build_object('job_id',j.id,'deletion_generation',j.deletion_generation,'lease_token',fence) INTO result FROM platform.upload_metadata m WHERE organization_id=j.organization_id AND intent_id=j.aggregate_id;
 RETURN result;
END $$;
CREATE FUNCTION platform.media_finish(jid uuid,fence uuid,outcome text,engine text,signature text,original_version text,derivative_version text,derivative_key uuid,derived_hash bytea,derived_bytes bigint) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE j app.jobs; m platform.upload_metadata; u app.upload_intents; cid uuid; org uuid; photo uuid:=gen_random_uuid(); did uuid:=gen_random_uuid(); basis uuid;
BEGIN
 SELECT * INTO j FROM app.jobs WHERE id=jid AND state='leased' AND lease_until>now() FOR UPDATE;
 IF NOT FOUND THEN RETURN false; END IF;
 SELECT * INTO m FROM platform.upload_metadata WHERE organization_id=j.organization_id AND intent_id=j.aggregate_id AND lease_token=fence FOR UPDATE;
 IF NOT FOUND THEN RETURN false; END IF;
 cid:=j.case_id; org:=j.organization_id;
 SELECT * INTO u FROM app.upload_intents WHERE organization_id=org AND id=j.aggregate_id FOR UPDATE;
 PERFORM 1 FROM app.cases c JOIN app.organizations o ON o.id=c.organization_id JOIN app.report_access a ON a.organization_id=c.organization_id AND a.case_id=c.id AND a.id=u.owner_access_id JOIN platform.report_submissions r ON r.organization_id=c.organization_id AND r.case_id=c.id WHERE c.organization_id=org AND c.id=cid AND c.deleted_at IS NULL AND c.lifecycle NOT IN ('closed','deleted') AND c.deletion_generation=j.deletion_generation AND o.approved_status='approved' AND o.suspended_at IS NULL AND a.expires_at>now() AND a.revoked_at IS NULL AND NOT r.contact_paused FOR UPDATE OF c;
 IF NOT FOUND THEN UPDATE app.jobs SET state='cancelled' WHERE organization_id=org AND id=jid; UPDATE app.upload_intents SET state='rejected' WHERE organization_id=org AND id=u.id; RETURN false; END IF;
 IF outcome='error' THEN
  UPDATE app.jobs SET state=CASE WHEN attempts>=5 THEN 'dead' ELSE 'pending' END,lease_until=NULL,next_attempt_at=now()+make_interval(secs=>least(300,5*(2^attempts)::integer)),error_code='SCANNER_UNAVAILABLE' WHERE organization_id=org AND id=jid;
  IF j.attempts>=5 THEN UPDATE app.upload_intents SET state='rejected' WHERE organization_id=org AND id=u.id; END IF;
  RETURN false;
 END IF;
 IF outcome='clean' THEN
  IF engine IS NULL OR signature IS NULL OR original_version IS NULL OR derivative_version IS NULL OR derivative_key IS NULL OR octet_length(derived_hash)<>32 OR derived_bytes NOT BETWEEN 1 AND 5242880 THEN RAISE EXCEPTION 'incomplete scan' USING ERRCODE='42501'; END IF;
  SELECT id INTO basis FROM app.legal_bases WHERE organization_id=org AND case_id=cid AND processing_purpose='intake' AND authority_type='synthetic_only' AND revoked_at IS NULL AND effective_until>now() LIMIT 1;
  IF basis IS NULL THEN RAISE EXCEPTION 'basis unavailable' USING ERRCODE='42501'; END IF;
  INSERT INTO app.objects(organization_id,id,case_id,bucket_class,opaque_key,object_version,content_sha256,bytes,detected_mime,encryption_key_ref,scan_status) VALUES(org,m.object_id,cid,'original',m.quarantine_key,original_version,m.expected_hash,m.expected_bytes,m.expected_mime,'synthetic-envelope-v1','clean'),(org,did,cid,'derivative',derivative_key,derivative_version,derived_hash,derived_bytes,'image/png','synthetic-envelope-v1','clean');
  INSERT INTO app.photographs(organization_id,id,case_id,original_object_id,source,legal_basis_id,synthetic) VALUES(org,photo,cid,m.object_id,'reporter_claim',basis,true);
  INSERT INTO app.photo_derivatives(organization_id,case_id,photo_id,object_id,transform_version,purpose,exif_removed) VALUES(org,cid,photo,did,'pillow-13.0.0-flat-png-v1','staff_review',true);
  INSERT INTO app.evidence_documents(organization_id,id,case_id,object_id,type,verification,content_sha256) VALUES(org,m.object_id,cid,m.object_id,'photograph','unverified',m.expected_hash);
  UPDATE platform.upload_metadata SET original_version=media_finish.original_version,derivative_version=media_finish.derivative_version,derivative_key=media_finish.derivative_key,scan_engine=engine,scan_signature=signature WHERE organization_id=org AND intent_id=u.id;
  UPDATE app.upload_intents SET state='ready' WHERE organization_id=org AND id=u.id;
  PERFORM platform.reporting_event(org,cid,'media.ready',photo);
 ELSE
  IF outcome NOT IN ('infected','invalid') THEN RAISE EXCEPTION 'invalid scan outcome' USING ERRCODE='42501'; END IF;
  UPDATE app.upload_intents SET state='rejected' WHERE organization_id=org AND id=u.id;
  UPDATE platform.upload_metadata SET scan_engine=engine,scan_signature=signature WHERE organization_id=org AND intent_id=u.id;
  PERFORM platform.reporting_event(org,cid,'media.quarantined',u.id);
 END IF;
 UPDATE app.jobs SET state='completed',lease_until=NULL,error_code=CASE WHEN outcome='clean' THEN NULL ELSE 'MEDIA_REJECTED' END WHERE organization_id=org AND id=jid;
 PERFORM platform.reporting_audit(org,u.owner_access_id,'media.'||outcome,cid);
 RETURN outcome='clean';
END $$;
CREATE FUNCTION platform.media_read(org uuid,media uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE obj app.objects; m platform.upload_metadata;
BEGIN
 SELECT o.* INTO obj FROM app.objects o JOIN app.photo_derivatives d ON d.organization_id=o.organization_id AND d.object_id=o.id AND d.exif_removed WHERE o.organization_id=org AND o.id=media AND o.bucket_class='derivative' AND o.scan_status='clean';
 IF NOT FOUND OR NOT platform.case_permission(org,obj.case_id,'case.read') OR NOT platform.case_permission(org,obj.case_id,'media.read') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 SELECT * INTO m FROM platform.upload_metadata WHERE organization_id=org AND case_id=obj.case_id AND derivative_key=obj.opaque_key;
 IF NOT FOUND THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 PERFORM platform.reporting_audit(org,nullif(current_setting('foc.principal',true),'')::uuid,'media.read',media);
 RETURN jsonb_build_object('key',obj.opaque_key,'version',obj.object_version,'wrapped_key',m.wrapped_key,'sha256',encode(obj.content_sha256,'hex'));
END $$;
CREATE FUNCTION platform.media_list(org uuid,cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF NOT platform.case_permission(org,cid,'case.read') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 RETURN coalesce((SELECT jsonb_agg(jsonb_build_object('id',u.id,'state',u.state,'media_id',o.id,'metadata_ciphertext',m.metadata_ciphertext,'scan_engine',m.scan_engine,'scan_signature',m.scan_signature)) FROM app.upload_intents u JOIN platform.upload_metadata m ON m.organization_id=u.organization_id AND m.intent_id=u.id LEFT JOIN app.objects o ON o.organization_id=m.organization_id AND o.opaque_key=m.derivative_key AND o.bucket_class='derivative' WHERE u.organization_id=org AND u.case_id=cid),'[]'::jsonb);
END $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.proname,p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('upload_create','upload_get','upload_bind','upload_complete','media_lease','media_finish','media_read','media_list') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature); EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature);
 EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',f.signature,CASE WHEN f.proname IN ('media_lease','media_finish') THEN 'foc_worker' ELSE 'foc_api' END);
 END LOOP;
END $$;
