-- Case commands retain optimistic revision, current grants, audit and outbox atomicity.
CREATE FUNCTION platform.staff_command(org uuid,cid uuid,operation text,payload jsonb,cipher text,expected bigint,command uuid,body_digest bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app,platform AS $$
DECLARE actor uuid:=nullif(current_setting('foc.principal',true),'')::uuid; current_case app.cases; prior platform.reporting_commands; scope_name text; result jsonb; target text; reference uuid:=gen_random_uuid(); recipient uuid; until_at timestamptz; evidence uuid;
BEGIN
 IF NOT platform.case_permission(org,cid,'case.read') THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF NOT platform.case_permission(org,cid,'case.write') OR NOT (platform.active_member(org,'reviewer') OR platform.active_member(org,'supervisor')) THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 scope_name:='staff:'||org::text||':'||actor::text||':'||cid::text||':'||operation;
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||command::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND reporting_commands.command=staff_command.command;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN prior.response; END IF;
 SELECT * INTO current_case FROM app.cases WHERE organization_id=org AND id=cid FOR UPDATE;
 IF current_case.revision<>expected THEN RAISE EXCEPTION 'stale' USING ERRCODE='P0412'; END IF;
 IF current_case.lifecycle='closed' AND operation<>'transition' THEN RAISE EXCEPTION 'closed' USING ERRCODE='P0409'; END IF;
 FOR evidence IN SELECT jsonb_array_elements_text(coalesce(payload->'evidence_refs','[]'))::uuid LOOP
 IF NOT EXISTS(SELECT 1 FROM app.evidence_documents e JOIN app.objects o ON o.organization_id=e.organization_id AND o.id=e.object_id WHERE e.organization_id=org AND e.case_id=cid AND e.id=evidence AND o.scan_status='clean') THEN RAISE EXCEPTION 'invalid evidence' USING ERRCODE='P0422'; END IF;
 END LOOP;
 IF operation='transition' THEN
  target:=payload->>'target';
  IF target NOT IN ('review','active','held','closed') OR (current_case.lifecycle='closed' AND (target<>'review' OR NOT platform.active_member(org,'supervisor'))) OR (current_case.lifecycle='quarantined' AND target NOT IN ('review','held','closed')) THEN RAISE EXCEPTION 'unsafe transition' USING ERRCODE='P0409'; END IF;
  IF target='active' AND (NOT EXISTS(SELECT 1 FROM platform.report_submissions WHERE organization_id=org AND case_id=cid AND contact_verified AND NOT contact_paused) OR EXISTS(SELECT 1 FROM app.upload_intents WHERE organization_id=org AND case_id=cid AND state NOT IN ('ready','expired'))) THEN RAISE EXCEPTION 'verification incomplete' USING ERRCODE='P0409'; END IF;
  UPDATE app.cases SET lifecycle=target,closed_reason=CASE WHEN target='closed' THEN 'staff_review' ELSE NULL END WHERE organization_id=org AND id=cid;
  IF target='closed' THEN
   UPDATE platform.report_sessions SET revoked_at=now() WHERE organization_id=org AND case_id=cid;
   UPDATE app.report_access SET revoked_at=now() WHERE organization_id=org AND case_id=cid;
   UPDATE app.jobs SET state='cancelled' WHERE organization_id=org AND case_id=cid AND state IN ('pending','leased');
   UPDATE app.outbox_events SET state='cancelled' WHERE organization_id=org AND case_id=cid AND state IN ('pending','leased');
  END IF;
 ELSIF operation='moderation' THEN
  IF payload->>'decision' NOT IN ('hold','review','reject','fraud') THEN RAISE EXCEPTION 'invalid moderation' USING ERRCODE='P0422'; END IF;
  IF payload->>'decision' IN ('fraud','reject') THEN
   UPDATE platform.report_submissions SET contact_paused=true WHERE organization_id=org AND case_id=cid;
   UPDATE platform.report_sessions SET revoked_at=now() WHERE organization_id=org AND case_id=cid;
   UPDATE app.report_access SET revoked_at=now() WHERE organization_id=org AND case_id=cid;
  END IF;
  UPDATE app.cases SET lifecycle=CASE WHEN payload->>'decision'='review' THEN 'review' ELSE 'held' END WHERE organization_id=org AND id=cid;
 ELSIF operation='assignment' THEN
  IF NOT platform.active_member(org,'supervisor') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
  recipient:=(payload->>'principal_id')::uuid; until_at:=(payload->>'grant_expires_at')::timestamptz;
  IF payload->>'purpose'<>'case_management' OR until_at<=now() OR until_at>now()+interval '30 days' OR NOT EXISTS(SELECT 1 FROM app.memberships m JOIN app.staff_principals p ON p.id=m.principal_id WHERE m.organization_id=org AND m.principal_id=recipient AND m.role IN ('reviewer','supervisor') AND m.starts_at<=now() AND m.expires_at>=until_at AND m.revoked_at IS NULL AND p.disabled_at IS NULL) THEN RAISE EXCEPTION 'invalid assignment' USING ERRCODE='42501'; END IF;
  UPDATE app.cases SET assigned_team_id=recipient WHERE organization_id=org AND id=cid;
  INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) SELECT org,cid,recipient,p,'case_management',actor,until_at FROM unnest(ARRAY['case.read','case.write','media.read']) p ON CONFLICT(organization_id,case_id,principal_id,permission,purpose) DO UPDATE SET expires_at=EXCLUDED.expires_at,revoked_at=NULL,granted_by=actor;
 ELSIF operation='note' THEN
  INSERT INTO app.notes(organization_id,id,case_id,author,body_ciphertext,evidence_refs,revision) VALUES(org,reference,cid,actor,convert_to(cipher,'UTF8'),ARRAY(SELECT jsonb_array_elements_text(payload->'evidence_refs')::uuid),current_case.revision+1);
 ELSIF operation='assertion' THEN
  IF payload->>'state'='verified' AND (jsonb_array_length(payload->'evidence_refs')=0 OR NOT platform.active_member(org,'supervisor')) THEN RAISE EXCEPTION 'verification incomplete' USING ERRCODE='42501'; END IF;
  IF payload->>'field' NOT IN ('name','birth_date','estimated_age','description','general_location','authority_reference') OR NOT EXISTS(SELECT 1 FROM platform.report_versions WHERE organization_id=org AND case_id=cid AND id=(payload->>'source_id')::uuid) THEN RAISE EXCEPTION 'invalid source' USING ERRCODE='P0422'; END IF;
  INSERT INTO app.assertions(organization_id,id,case_id,field_name,typed_value_ciphertext,precision,source_id,state,verified_by,verified_at) VALUES(org,reference,cid,payload->>'field',convert_to(cipher,'UTF8'),payload->>'precision',(payload->>'source_id')::uuid,payload->>'state',CASE WHEN payload->>'state'='verified' THEN actor END,CASE WHEN payload->>'state'='verified' THEN now() END);
 ELSE RAISE EXCEPTION 'unsupported' USING ERRCODE='42501';
 END IF;
 INSERT INTO platform.report_versions(organization_id,case_id,id,kind,actor_ref,body_ciphertext) VALUES(org,cid,reference,CASE WHEN operation='moderation' THEN 'moderation' ELSE 'transition' END,actor,cipher);
 UPDATE app.cases SET revision=revision+1 WHERE organization_id=org AND id=cid;
 PERFORM platform.reporting_audit(org,actor,'case.'||operation,cid);
 PERFORM platform.reporting_event(org,cid,'notification.requested',cid);
 result:=jsonb_build_object('id',cid,'revision',current_case.revision+1);
 INSERT INTO platform.reporting_commands VALUES(scope_name,command,body_digest,result,now());
 RETURN result;
END $$;
CREATE FUNCTION platform.staff_evidence(org uuid,cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app AS $$
BEGIN
 IF NOT platform.case_permission(org,cid,'case.read') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 RETURN jsonb_build_object('evidence',coalesce((SELECT jsonb_agg(jsonb_build_object('id',e.id,'verification',e.verification,'type',e.type)) FROM app.evidence_documents e JOIN app.objects o ON o.organization_id=e.organization_id AND o.id=e.object_id WHERE e.organization_id=org AND e.case_id=cid AND o.scan_status='clean'),'[]'::jsonb),'notes',coalesce((SELECT jsonb_agg(jsonb_build_object('id',n.id,'author',n.author,'revision',n.revision,'ciphertext',convert_from(n.body_ciphertext,'UTF8')) ORDER BY n.revision) FROM app.notes n WHERE n.organization_id=org AND n.case_id=cid),'[]'::jsonb),'assertions',coalesce((SELECT jsonb_agg(jsonb_build_object('id',a.id,'field',a.field_name,'state',a.state,'source_id',a.source_id,'verified_by',a.verified_by,'ciphertext',convert_from(a.typed_value_ciphertext,'UTF8'))) FROM app.assertions a WHERE a.organization_id=org AND a.case_id=cid),'[]'::jsonb));
END $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('staff_command','staff_evidence') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature); EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature); EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_api',f.signature);
 END LOOP;
END $$;
