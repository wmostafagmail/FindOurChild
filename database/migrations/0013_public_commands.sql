-- Public command keys bind the browser capability, operation and canonical request, not unverified contact claims.
CREATE FUNCTION platform.intake_command(browser bytea,org uuid,registry_name text,receipt bytea,contact bytea,contact_cipher text,receipt_cipher text,claims_cipher text,cmd uuid,body_digest bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE scope_name text:='browser-intake:'||encode(browser,'hex')||':'||registry_name; prior platform.reporting_commands; result jsonb;
BEGIN
 IF NOT EXISTS(SELECT 1 FROM platform.intake_route r JOIN app.organizations o ON o.id=r.organization_id JOIN app.staff_principals p ON p.id=r.moderator WHERE r.organization_id=org AND r.expires_at>now() AND o.approved_status='approved' AND o.suspended_at IS NULL AND p.disabled_at IS NULL) THEN RAISE EXCEPTION 'unavailable' USING ERRCODE='42501'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||cmd::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND command=cmd;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN prior.response; END IF;
 result:=platform.reporting_create(org,registry_name,receipt,contact,contact_cipher,receipt_cipher,claims_cipher,cmd,body_digest);
 INSERT INTO platform.reporting_commands VALUES(scope_name,cmd,body_digest,result,now());RETURN result;
END $$;
CREATE FUNCTION platform.access_request_command(browser bytea,receipt bytea,contact bytea,code bytea,delivery_cipher text,cmd uuid,body_digest bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE scope_name text:='browser-access:'||encode(browser,'hex'); prior platform.reporting_commands; result jsonb; allowed jsonb;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||cmd::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND command=cmd;
 IF FOUND THEN
  IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF;
  IF NOT EXISTS(SELECT 1 FROM platform.report_codes c JOIN platform.report_submissions r ON r.receipt_hash=c.receipt_hash JOIN app.cases x ON x.organization_id=r.organization_id AND x.id=r.case_id JOIN app.organizations o ON o.id=x.organization_id WHERE c.receipt_hash=receipt AND c.expires_at>now() AND c.consumed_at IS NULL AND c.attempts<5 AND NOT r.contact_paused AND x.deleted_at IS NULL AND x.lifecycle NOT IN ('closed','deleted') AND o.approved_status='approved' AND o.suspended_at IS NULL) THEN RETURN NULL; END IF;
  RETURN prior.response;
 END IF;
 allowed:=platform.reporting_access_request(receipt,contact,code);
 result:=jsonb_build_object('delivery_ciphertext',CASE WHEN allowed IS NULL THEN NULL ELSE delivery_cipher END);
 INSERT INTO platform.reporting_commands VALUES(scope_name,cmd,body_digest,result,now());RETURN result;
END $$;
CREATE FUNCTION platform.concern_command(browser bytea,cipher text,cmd uuid,body_digest bytea) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
DECLARE scope_name text:='browser-concern:'||encode(browser,'hex'); prior platform.reporting_commands;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||cmd::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND command=cmd;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN; END IF;
 PERFORM platform.concern_append(cipher);
 INSERT INTO platform.reporting_commands VALUES(scope_name,cmd,body_digest,'{}',now());
END $$;
CREATE FUNCTION platform.upload_complete_command(token bytea,iid uuid,version text,checksum bytea,cmd uuid,body_digest bytea) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
DECLARE ctx jsonb:=platform.reporter_context(token); scope_name text; prior platform.reporting_commands;
BEGIN
 IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 scope_name:='complete:'||(ctx->>'access_id')||':'||iid::text;
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||cmd::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND command=cmd;
 IF FOUND THEN IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; PERFORM platform.upload_get(token,iid);RETURN; END IF;
 PERFORM platform.upload_complete(token,iid,version,checksum);
 INSERT INTO platform.reporting_commands VALUES(scope_name,cmd,body_digest,'{}',now());
END $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('intake_command','access_request_command','concern_command','upload_complete_command') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature); EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature); EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_api',f.signature);
 END LOOP;
END $$;
-- Callers must use the guarded/idempotent wrappers. Helper routines retain only policy-role access.
REVOKE EXECUTE ON FUNCTION platform.reporting_create(uuid,text,bytea,bytea,text,text,text,uuid,bytea),platform.reporting_access_request(bytea,bytea,bytea),platform.concern_append(text),platform.upload_complete(bytea,uuid,text,bytea) FROM foc_api;
