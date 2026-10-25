-- Phase 1C: synthetic intake, immutable claims, scoped staff commands and reporter capabilities.
-- Applied Phase 0–1B migrations are never modified.
CREATE ROLE foc_worker LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
GRANT USAGE ON SCHEMA platform TO foc_worker;
CREATE TABLE platform.intake_route (
 organization_id uuid PRIMARY KEY REFERENCES app.organizations(id),
 moderator uuid NOT NULL REFERENCES app.staff_principals(id), expires_at timestamptz NOT NULL
);
CREATE TABLE platform.intake_limits (scope_hash bytea PRIMARY KEY, window_at timestamptz NOT NULL, used integer NOT NULL CHECK(used>0));
CREATE TABLE platform.intake_challenges (hash bytea PRIMARY KEY CHECK(octet_length(hash)=32), browser_hash bytea NOT NULL, expires_at timestamptz NOT NULL, consumed_at timestamptz);
CREATE TABLE platform.report_submissions (
 organization_id uuid NOT NULL, case_id uuid NOT NULL, receipt_hash bytea UNIQUE NOT NULL CHECK(octet_length(receipt_hash)=32),
 contact_hash bytea NOT NULL, contact_ciphertext text NOT NULL, receipt_ciphertext text NOT NULL,
 contact_verified boolean NOT NULL DEFAULT false, contact_paused boolean NOT NULL DEFAULT false,
 PRIMARY KEY(organization_id,case_id), FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
CREATE TABLE platform.report_versions (
 organization_id uuid NOT NULL, case_id uuid NOT NULL, id uuid NOT NULL DEFAULT gen_random_uuid(), kind text NOT NULL CHECK(kind IN ('original','supplement','relay','moderation','transition','abuse')),
 actor_ref uuid, body_ciphertext text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(organization_id,id), FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
CREATE TABLE platform.report_codes (receipt_hash bytea PRIMARY KEY REFERENCES platform.report_submissions(receipt_hash), code_hash bytea NOT NULL, expires_at timestamptz NOT NULL, attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5), consumed_at timestamptz);
CREATE TABLE platform.report_sessions (hash bytea PRIMARY KEY CHECK(octet_length(hash)=32), organization_id uuid NOT NULL, case_id uuid NOT NULL, csrf_hash bytea NOT NULL, expires_at timestamptz NOT NULL, revoked_at timestamptz, access_id uuid NOT NULL, FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id), FOREIGN KEY(organization_id,access_id) REFERENCES app.report_access(organization_id,id));
CREATE TABLE platform.reporting_commands (scope text NOT NULL, command uuid NOT NULL, body_hash bytea NOT NULL, response jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(scope,command));
CREATE TABLE platform.upload_metadata (
 organization_id uuid NOT NULL, case_id uuid NOT NULL, intent_id uuid NOT NULL, object_id uuid NOT NULL, expected_hash bytea NOT NULL, expected_bytes bigint NOT NULL, expected_mime text NOT NULL,
 quarantine_version text, quarantine_key uuid NOT NULL, original_version text, derivative_version text, derivative_key uuid,
 wrapped_key text NOT NULL, metadata_ciphertext text NOT NULL, scan_engine text, scan_signature text, lease_token uuid,
 PRIMARY KEY(organization_id,intent_id), FOREIGN KEY(organization_id,intent_id) REFERENCES app.upload_intents(organization_id,id), FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id)
);
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['intake_route','intake_limits','intake_challenges','report_submissions','report_versions','report_codes','report_sessions','reporting_commands','upload_metadata'] LOOP
 EXECUTE format('ALTER TABLE platform.%I OWNER TO foc_owner',t);
 EXECUTE format('ALTER TABLE platform.%I ENABLE ROW LEVEL SECURITY',t);
 EXECUTE format('ALTER TABLE platform.%I FORCE ROW LEVEL SECURITY',t);
 EXECUTE format('GRANT SELECT,INSERT,UPDATE,DELETE ON platform.%I TO foc_policy',t);
 EXECUTE format('CREATE POLICY policy_internal ON platform.%I TO foc_policy USING(true) WITH CHECK(true)',t);
 END LOOP;
END $$;
-- No generic API access to platform rows, and no reporter read of custody, staff notes or other reports.
GRANT SELECT,INSERT,UPDATE ON app.report_access,app.reporters,app.child_profiles,app.registry_events,app.legal_bases,app.upload_intents,app.objects,app.photographs,app.photo_derivatives,app.evidence_documents,app.assertions,app.notes,app.duplicate_links,app.jobs,app.outbox_events TO foc_policy;
GRANT INSERT,UPDATE ON app.cases,app.case_grants TO foc_policy;
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['report_access','reporters','child_profiles','registry_events','legal_bases','upload_intents','objects','photographs','photo_derivatives','evidence_documents','assertions','notes','duplicate_links','jobs','outbox_events'] LOOP
 EXECUTE format('CREATE POLICY reporting_internal ON app.%I TO foc_policy USING(true) WITH CHECK(true)',t);
 END LOOP;
END $$;
CREATE POLICY reporting_insert ON app.cases FOR INSERT TO foc_policy WITH CHECK(true);
CREATE POLICY reporting_update ON app.cases FOR UPDATE TO foc_policy USING(true) WITH CHECK(true);
CREATE POLICY reporting_grants_insert ON app.case_grants FOR INSERT TO foc_policy WITH CHECK(true);
CREATE POLICY reporting_grants_update ON app.case_grants FOR UPDATE TO foc_policy USING(true) WITH CHECK(true);

CREATE FUNCTION platform.intake_limit(scope bytea, maximum integer) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
DECLARE n integer;
BEGIN
 IF octet_length(scope)<>32 OR maximum NOT BETWEEN 1 AND 100 THEN RETURN false; END IF;
 INSERT INTO platform.intake_limits(scope_hash,window_at,used) VALUES(scope,now(),1)
 ON CONFLICT(scope_hash) DO UPDATE SET used=CASE WHEN intake_limits.window_at<now()-interval '10 minutes' THEN 1 ELSE intake_limits.used+1 END, window_at=CASE WHEN intake_limits.window_at<now()-interval '10 minutes' THEN now() ELSE intake_limits.window_at END RETURNING used INTO n;
 RETURN n<=maximum;
END $$;
CREATE FUNCTION platform.intake_challenge(token bytea,browser bytea) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 IF octet_length(token)<>32 OR octet_length(browser)<>32 THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 INSERT INTO platform.intake_challenges(hash,browser_hash,expires_at) VALUES(token,browser,now()+interval '10 minutes');
END $$;
CREATE FUNCTION platform.intake_consume(token bytea,browser bytea) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 UPDATE platform.intake_challenges SET consumed_at=now() WHERE hash=token AND browser_hash=browser AND expires_at>now() AND consumed_at IS NULL;
 RETURN FOUND;
END $$;
-- Internal append is not executable by runtime. Events contain opaque IDs only.
CREATE FUNCTION platform.reporting_audit(org uuid,actor uuid,action_name text,target uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app,public AS $$
DECLARE prior bytea; seq bigint; event uuid:=gen_random_uuid(); stamp timestamptz:=clock_timestamp();
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(org::text,0));
 SELECT event_hash,sequence INTO prior,seq FROM app.audit_events WHERE organization_id=org ORDER BY sequence DESC LIMIT 1;
 prior:=coalesce(prior,decode(repeat('00',32),'hex'));
 INSERT INTO app.audit_events(organization_id,sequence,event_id,actor_ref,action,target_ref,purpose,outcome,previous_hash,event_hash,occurred_at)
 VALUES(org,coalesce(seq,0)+1,event,actor,action_name,target,'case_management','allowed',prior,digest(prior||convert_to(jsonb_build_array(event,actor,action_name,target,'case_management','allowed',stamp)::text,'UTF8'),'sha256'),stamp);
END $$;
CREATE FUNCTION platform.reporting_event(org uuid,cid uuid,kind text,aggregate uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app AS $$
DECLARE rev bigint; gen bigint; eid uuid:=gen_random_uuid();
BEGIN
 SELECT revision,deletion_generation INTO rev,gen FROM app.cases WHERE organization_id=org AND id=cid AND deleted_at IS NULL;
 IF NOT FOUND THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 INSERT INTO app.outbox_events(organization_id,id,case_id,type,schema_version,aggregate_id,aggregate_revision,dedup_key,deletion_generation,aggregate_type,occurred_at,correlation_id,policy_version)
 VALUES(org,eid,cid,kind,1,aggregate,rev,eid,gen,CASE WHEN kind LIKE 'media.%' THEN 'photograph' ELSE 'case' END,now(),gen_random_uuid(),'synthetic-1c-v1');
END $$;
CREATE FUNCTION platform.reporting_create(org uuid,registry_name text,receipt bytea,contact bytea,contact_cipher text,receipt_cipher text,claims_cipher text,command uuid,body_digest bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app,platform AS $$
DECLARE cid uuid:=gen_random_uuid(); moderator_id uuid; result jsonb; scope_name text:='intake:'||encode(contact,'hex')||':'||registry_name; prior platform.reporting_commands;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||command::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND reporting_commands.command=reporting_create.command;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN prior.response; END IF;
 SELECT r.moderator INTO moderator_id FROM platform.intake_route r JOIN app.organizations o ON o.id=r.organization_id JOIN app.staff_principals p ON p.id=r.moderator WHERE r.organization_id=org AND r.expires_at>now() AND o.approved_status='approved' AND o.suspended_at IS NULL AND p.disabled_at IS NULL AND EXISTS(SELECT 1 FROM app.memberships m WHERE m.organization_id=org AND m.principal_id=r.moderator AND m.revoked_at IS NULL AND m.starts_at<=now() AND m.expires_at>now());
 IF moderator_id IS NULL OR registry_name NOT IN ('missing','found') OR octet_length(receipt)<>32 OR octet_length(contact)<>32 THEN RAISE EXCEPTION 'unavailable' USING ERRCODE='42501'; END IF;
 INSERT INTO app.cases(organization_id,id,registry) VALUES(org,cid,registry_name);
 INSERT INTO platform.report_submissions VALUES(org,cid,receipt,contact,contact_cipher,receipt_cipher,false,false);
 INSERT INTO platform.report_versions(organization_id,case_id,kind,body_ciphertext) VALUES(org,cid,'original',claims_cipher);
 INSERT INTO app.reporters(organization_id,case_id,contact_ciphertext) VALUES(org,cid,convert_to(contact_cipher,'UTF8'));
 INSERT INTO app.legal_bases(organization_id,case_id,processing_purpose,authority_type,notice_version,effective_from,effective_until) VALUES(org,cid,'intake','synthetic_only','synthetic-1c-v1',now(),now()+interval '30 days');
 INSERT INTO app.case_grants(organization_id,case_id,principal_id,permission,purpose,granted_by,expires_at) SELECT org,cid,moderator_id,p,'case_management',moderator_id,least(r.expires_at,now()+interval '30 days') FROM platform.intake_route r CROSS JOIN unnest(ARRAY['case.read','case.write','media.read']) p WHERE r.organization_id=org;
 PERFORM platform.reporting_audit(org,cid,'report.submitted',cid);
 PERFORM platform.reporting_event(org,cid,'report.submitted',cid);
 result:=jsonb_build_object('case_id',cid,'receipt_ciphertext',receipt_cipher);
 INSERT INTO platform.reporting_commands VALUES(scope_name,command,body_digest,result,now());
 RETURN result;
END $$;
CREATE FUNCTION platform.reporting_access_request(receipt bytea,contact bytea,code bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE s platform.report_submissions;
BEGIN
 SELECT r.* INTO s FROM platform.report_submissions r JOIN app.cases c ON c.organization_id=r.organization_id AND c.id=r.case_id JOIN app.organizations o ON o.id=c.organization_id WHERE r.receipt_hash=receipt AND r.contact_hash=contact AND NOT r.contact_paused AND c.deleted_at IS NULL AND c.lifecycle NOT IN ('closed','deleted') AND o.approved_status='approved' AND o.suspended_at IS NULL;
 IF NOT FOUND THEN RETURN NULL; END IF;
 INSERT INTO platform.report_codes(receipt_hash,code_hash,expires_at) VALUES(receipt,code,now()+interval '10 minutes') ON CONFLICT(receipt_hash) DO UPDATE SET code_hash=EXCLUDED.code_hash,expires_at=EXCLUDED.expires_at,attempts=0,consumed_at=NULL;
 RETURN jsonb_build_object('contact_ciphertext',s.contact_ciphertext,'case_id',s.case_id);
END $$;
CREATE FUNCTION platform.reporting_exchange(receipt bytea,code bytea,session bytea,csrf bytea) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE s platform.report_submissions; c platform.report_codes; aid uuid:=gen_random_uuid();
BEGIN
 SELECT * INTO c FROM platform.report_codes WHERE receipt_hash=receipt FOR UPDATE;
 IF NOT FOUND OR c.consumed_at IS NOT NULL OR c.attempts>=5 OR c.expires_at<=now() THEN RETURN false; END IF;
 UPDATE platform.report_codes SET attempts=attempts+1 WHERE receipt_hash=receipt;
 IF c.code_hash<>code THEN RETURN false; END IF;
 SELECT r.* INTO s FROM platform.report_submissions r JOIN app.cases x ON x.organization_id=r.organization_id AND x.id=r.case_id JOIN app.organizations o ON o.id=x.organization_id WHERE r.receipt_hash=receipt AND NOT r.contact_paused AND x.deleted_at IS NULL AND x.lifecycle NOT IN ('closed','deleted') AND o.approved_status='approved' AND o.suspended_at IS NULL;
 IF NOT FOUND THEN RETURN false; END IF;
 UPDATE platform.report_codes SET consumed_at=now() WHERE receipt_hash=receipt;
 UPDATE platform.report_submissions SET contact_verified=true WHERE receipt_hash=receipt;
 INSERT INTO app.report_access(organization_id,id,case_id,capability_hash,verified_contact_ref,expires_at) VALUES(s.organization_id,aid,s.case_id,session,aid,now()+interval '30 minutes');
 INSERT INTO platform.report_sessions VALUES(session,s.organization_id,s.case_id,csrf,now()+interval '30 minutes',NULL,aid);
 PERFORM platform.reporting_audit(s.organization_id,aid,'reporter.verified',s.case_id);
 RETURN true;
END $$;
CREATE FUNCTION platform.reporter_context(token bytea) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
 SELECT jsonb_build_object('organization_id',s.organization_id,'case_id',s.case_id,'access_id',s.access_id,'csrf_hash',encode(s.csrf_hash,'hex'),'expires_at',s.expires_at)
 FROM platform.report_sessions s JOIN app.report_access a ON a.organization_id=s.organization_id AND a.id=s.access_id JOIN app.cases c ON c.organization_id=s.organization_id AND c.id=s.case_id JOIN app.organizations o ON o.id=c.organization_id JOIN platform.report_submissions r ON r.organization_id=c.organization_id AND r.case_id=c.id
 WHERE s.hash=token AND s.expires_at>now() AND s.revoked_at IS NULL AND a.expires_at>now() AND a.revoked_at IS NULL AND c.deleted_at IS NULL AND c.lifecycle NOT IN ('closed','deleted') AND NOT r.contact_paused AND o.approved_status='approved' AND o.suspended_at IS NULL
$$;
CREATE FUNCTION platform.reporter_versions(token bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE ctx jsonb; result jsonb;
BEGIN
 ctx:=platform.reporter_context(token); IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 SELECT jsonb_build_object('id',c.id,'lifecycle',CASE WHEN c.lifecycle='quarantined' THEN 'received' ELSE 'in_review' END,'versions',coalesce((SELECT jsonb_agg(jsonb_build_object('id',v.id,'kind',v.kind,'ciphertext',v.body_ciphertext) ORDER BY v.created_at,v.id) FROM platform.report_versions v WHERE v.organization_id=c.organization_id AND v.case_id=c.id AND v.kind IN ('original','supplement')),'[]'::jsonb)) INTO result FROM app.cases c WHERE c.organization_id=(ctx->>'organization_id')::uuid AND c.id=(ctx->>'case_id')::uuid;
 RETURN result;
END $$;
-- Reporter append never edits verified facts, custody, staff notes, lifecycle or case grants.
CREATE FUNCTION platform.reporter_append(token bytea,kind_name text,cipher text,command uuid,body_digest bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE ctx jsonb; org uuid; cid uuid; vid uuid:=gen_random_uuid(); prior platform.reporting_commands; scope_name text;
BEGIN
 ctx:=platform.reporter_context(token); IF ctx IS NULL OR kind_name NOT IN ('supplement','relay') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 org:=(ctx->>'organization_id')::uuid; cid:=(ctx->>'case_id')::uuid; scope_name:='reporter:'||(ctx->>'access_id')||':'||kind_name;
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||command::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND reporting_commands.command=reporter_append.command;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN prior.response; END IF;
 INSERT INTO platform.report_versions(organization_id,case_id,id,kind,actor_ref,body_ciphertext) VALUES(org,cid,vid,kind_name,(ctx->>'access_id')::uuid,cipher);
 PERFORM platform.reporting_audit(org,(ctx->>'access_id')::uuid,'reporter.'||kind_name,cid);
 PERFORM platform.reporting_event(org,cid,'notification.requested',cid);
 INSERT INTO platform.reporting_commands VALUES(scope_name,command,body_digest,jsonb_build_object('id',vid),now());
 RETURN jsonb_build_object('id',vid);
END $$;
-- Explicit staff read functions: current live case grant is mandatory; no org-admin shortcut.
CREATE FUNCTION platform.staff_versions(org uuid,cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb;
BEGIN
 IF NOT platform.case_permission(org,cid,'case.read') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 SELECT jsonb_build_object('summary',jsonb_build_object('id',c.id,'registry',c.registry,'lifecycle',c.lifecycle,'revision',c.revision,'verification_status',c.verification_status),'assignment',c.assigned_team_id,'versions',coalesce((SELECT jsonb_agg(jsonb_build_object('id',v.id,'kind',v.kind,'ciphertext',v.body_ciphertext) ORDER BY v.created_at,v.id) FROM platform.report_versions v WHERE v.organization_id=org AND v.case_id=cid),'[]'::jsonb),'contact_verified',coalesce((SELECT contact_verified FROM platform.report_submissions WHERE organization_id=org AND case_id=cid),false),'contact_paused',coalesce((SELECT contact_paused FROM platform.report_submissions WHERE organization_id=org AND case_id=cid),false)) INTO result FROM app.cases c WHERE c.organization_id=org AND c.id=cid;
 PERFORM platform.reporting_audit(org,nullif(current_setting('foc.principal',true),'')::uuid,'case.read',cid);
 RETURN result;
END $$;
-- All functions owned by NOLOGIN policy role; unlisted internals are not callable by runtime.
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('intake_limit','intake_challenge','intake_consume','reporting_audit','reporting_event','reporting_create','reporting_access_request','reporting_exchange','reporter_context','reporter_versions','reporter_append','staff_versions') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature);
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature);
 IF f.signature::text NOT LIKE '%%reporting_audit%%' AND f.signature::text NOT LIKE '%%reporting_event%%' THEN EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_api',f.signature); END IF;
 END LOOP;
END $$;
