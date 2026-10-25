-- Follow-up controls, keeping earlier applied draft migrations checksum-stable.
CREATE OR REPLACE FUNCTION platform.intake_limit(scope bytea, maximum integer) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
DECLARE n integer; period interval:=CASE WHEN maximum=100 THEN interval '1 minute' ELSE interval '10 minutes' END;
BEGIN
 IF octet_length(scope)<>32 OR maximum NOT BETWEEN 1 AND 100 THEN RETURN false; END IF;
 INSERT INTO platform.intake_limits(scope_hash,window_at,used) VALUES(scope,now(),1)
 ON CONFLICT(scope_hash) DO UPDATE SET used=CASE WHEN intake_limits.window_at<now()-period THEN 1 ELSE intake_limits.used+1 END, window_at=CASE WHEN intake_limits.window_at<now()-period THEN now() ELSE intake_limits.window_at END RETURNING used INTO n;
 RETURN n<=maximum;
END $$;
CREATE TABLE platform.intake_restricted(organization_id uuid NOT NULL,case_id uuid NOT NULL,body_ciphertext text NOT NULL,PRIMARY KEY(organization_id,case_id),FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id));
ALTER TABLE platform.intake_restricted OWNER TO foc_owner;
ALTER TABLE platform.intake_restricted ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.intake_restricted FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON platform.intake_restricted TO foc_policy;
CREATE POLICY internal_restricted ON platform.intake_restricted TO foc_policy USING(true) WITH CHECK(true);
CREATE FUNCTION platform.restricted_intake_record(receipt bytea,cipher text) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 INSERT INTO platform.intake_restricted SELECT organization_id,case_id,cipher FROM platform.report_submissions WHERE receipt_hash=receipt ON CONFLICT DO NOTHING;
END $$;
ALTER FUNCTION platform.restricted_intake_record(bytea,text) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.restricted_intake_record(bytea,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.restricted_intake_record(bytea,text) TO foc_api;
-- Orphans expire under a lease-free metadata sweep; finalized evidence remains separate.
CREATE FUNCTION platform.upload_expired() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE u app.upload_intents; m platform.upload_metadata;
BEGIN
 SELECT x.* INTO u FROM app.upload_intents x WHERE x.expires_at<now()-interval '24 hours' AND x.state IN ('pending','uploaded','rejected') ORDER BY x.expires_at LIMIT 1 FOR UPDATE SKIP LOCKED;
 IF NOT FOUND THEN RETURN NULL; END IF;
 SELECT * INTO m FROM platform.upload_metadata WHERE organization_id=u.organization_id AND intent_id=u.id;
 RETURN jsonb_build_object('id',u.id,'key',m.quarantine_key,'version',m.quarantine_version);
END $$;
ALTER FUNCTION platform.upload_expired() OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.upload_expired() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.upload_expired() TO foc_worker;
-- Real local neutral-notification sink: no provider account or external delivery is configured.
GRANT SELECT,INSERT ON app.notification_deliveries TO foc_policy;
CREATE POLICY notification_internal ON app.notification_deliveries TO foc_policy USING(true) WITH CHECK(true);
CREATE FUNCTION platform.outbox_next() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app AS $$
DECLARE e app.outbox_events; recipients jsonb;
BEGIN
 SELECT * INTO e FROM app.outbox_events WHERE ((state='pending' AND next_attempt_at<=now()) OR (state='leased' AND lease_until<now())) AND attempts<5 ORDER BY occurred_at,id LIMIT 1 FOR UPDATE SKIP LOCKED;
 IF NOT FOUND THEN RETURN NULL; END IF;
 IF NOT EXISTS(SELECT 1 FROM app.cases c JOIN app.organizations o ON o.id=c.organization_id WHERE c.organization_id=e.organization_id AND c.id=e.case_id AND c.deleted_at IS NULL AND c.lifecycle NOT IN ('closed','deleted') AND c.deletion_generation=e.deletion_generation AND o.approved_status='approved' AND o.suspended_at IS NULL) THEN UPDATE app.outbox_events SET state='cancelled' WHERE organization_id=e.organization_id AND id=e.id; RETURN jsonb_build_object('cancelled',true); END IF;
 SELECT coalesce(jsonb_agg(g.principal_id),'[]'::jsonb) INTO recipients FROM app.case_grants g JOIN app.staff_principals p ON p.id=g.principal_id WHERE g.organization_id=e.organization_id AND g.case_id=e.case_id AND g.permission='case.read' AND g.purpose='case_management' AND g.revoked_at IS NULL AND g.expires_at>now() AND p.disabled_at IS NULL AND EXISTS(SELECT 1 FROM app.memberships m WHERE m.organization_id=g.organization_id AND m.principal_id=g.principal_id AND m.revoked_at IS NULL AND m.starts_at<=now() AND m.expires_at>now());
 UPDATE app.outbox_events SET state='leased',lease_until=now()+interval '30 seconds',attempts=attempts+1 WHERE organization_id=e.organization_id AND id=e.id;
 RETURN jsonb_build_object('event_id',e.id,'recipients',recipients,'attempt',e.attempts+1);
END $$;
CREATE FUNCTION platform.outbox_recipient_current(event uuid,recipient uuid,attempt integer) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,app AS $$
 SELECT EXISTS(SELECT 1 FROM app.outbox_events e JOIN app.cases c ON c.organization_id=e.organization_id AND c.id=e.case_id JOIN app.organizations o ON o.id=c.organization_id JOIN app.case_grants g ON g.organization_id=c.organization_id AND g.case_id=c.id JOIN app.staff_principals p ON p.id=g.principal_id WHERE e.id=event AND e.state='leased' AND e.attempts=attempt AND e.lease_until>now() AND c.deleted_at IS NULL AND c.lifecycle NOT IN ('closed','deleted') AND c.deletion_generation=e.deletion_generation AND o.approved_status='approved' AND o.suspended_at IS NULL AND g.principal_id=recipient AND g.permission='case.read' AND g.purpose='case_management' AND g.revoked_at IS NULL AND g.expires_at>now() AND p.disabled_at IS NULL AND EXISTS(SELECT 1 FROM app.memberships m WHERE m.organization_id=c.organization_id AND m.principal_id=recipient AND m.revoked_at IS NULL AND m.starts_at<=now() AND m.expires_at>now()))
$$;
CREATE FUNCTION platform.outbox_finish(event uuid,attempt integer) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app AS $$
BEGIN
 UPDATE app.outbox_events SET state='completed',lease_until=NULL WHERE id=event AND state='leased' AND attempts=attempt AND lease_until>now();RETURN FOUND;
END $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('outbox_next','outbox_recipient_current','outbox_finish') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature); EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature); EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_worker',f.signature);
 END LOOP;
END $$;

CREATE FUNCTION platform.upload_expired_ack(iid uuid) RETURNS void LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,app AS $$ UPDATE app.upload_intents SET state='expired' WHERE id=iid AND expires_at<now()-interval '24 hours' AND state IN ('pending','uploaded','rejected') $$;
ALTER FUNCTION platform.upload_expired_ack(uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.upload_expired_ack(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.upload_expired_ack(uuid) TO foc_worker;
