-- Cleanup acknowledgments follow successful version erasure, never before it.
ALTER TABLE platform.upload_metadata ADD COLUMN quarantine_purged boolean NOT NULL DEFAULT false;
CREATE FUNCTION platform.quarantine_cleanup_next() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb;
BEGIN
 SELECT jsonb_build_object('id',u.id,'key',m.quarantine_key,'version',m.quarantine_version) INTO result FROM app.upload_intents u JOIN platform.upload_metadata m ON m.organization_id=u.organization_id AND m.intent_id=u.id WHERE NOT m.quarantine_purged AND (u.state='ready' OR (u.expires_at<now()-interval '24 hours' AND u.state IN ('pending','uploaded','rejected'))) ORDER BY u.expires_at,u.id LIMIT 1 FOR UPDATE OF m SKIP LOCKED;
 RETURN result;
END $$;
CREATE FUNCTION platform.quarantine_cleanup_ack(iid uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 UPDATE platform.upload_metadata m SET quarantine_purged=true FROM app.upload_intents u WHERE u.organization_id=m.organization_id AND u.id=m.intent_id AND u.id=iid AND (u.state='ready' OR (u.expires_at<now()-interval '24 hours' AND u.state IN ('pending','uploaded','rejected')));
 UPDATE app.upload_intents u SET state='expired' FROM platform.upload_metadata m WHERE m.organization_id=u.organization_id AND m.intent_id=u.id AND u.id=iid AND m.quarantine_purged AND u.state IN ('pending','uploaded','rejected');
END $$;
CREATE FUNCTION platform.reporting_reconcile() RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app AS $$
BEGIN
 UPDATE app.jobs SET state='dead',error_code='LEASE_ATTEMPTS_EXHAUSTED' WHERE type='media.scan' AND state='leased' AND lease_until<now() AND attempts>=5;
 UPDATE app.upload_intents u SET state='rejected' FROM app.jobs j WHERE j.organization_id=u.organization_id AND j.aggregate_id=u.id AND j.type='media.scan' AND j.state='dead' AND u.state='scanning';
 UPDATE app.outbox_events SET state='dead',error_code='LEASE_ATTEMPTS_EXHAUSTED' WHERE state='leased' AND lease_until<now() AND attempts>=5;
END $$;
CREATE FUNCTION platform.case_list_audit(org uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 IF NOT platform.active_member(org,NULL) THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 PERFORM platform.reporting_audit(org,nullif(current_setting('foc.principal',true),'')::uuid,'case.list',org);
END $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.proname,p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('quarantine_cleanup_next','quarantine_cleanup_ack','reporting_reconcile','case_list_audit') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature); EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature); EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',f.signature,CASE WHEN f.proname='case_list_audit' THEN 'foc_api' ELSE 'foc_worker' END);
 END LOOP;
END $$;
REVOKE EXECUTE ON FUNCTION platform.upload_expired(),platform.upload_expired_ack(uuid) FROM foc_worker;
