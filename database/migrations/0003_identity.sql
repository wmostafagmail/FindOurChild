-- Identity metadata and narrowly scoped SECURITY DEFINER functions. No new child-data policies.
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
CREATE TABLE platform.identity_sessions (
 token_hash bytea PRIMARY KEY CHECK(octet_length(token_hash)=32),
 principal_id uuid NOT NULL REFERENCES app.staff_principals(id),
 encrypted_token text NOT NULL,
 csrf_hash bytea NOT NULL CHECK(octet_length(csrf_hash)=32),
 created_at timestamptz NOT NULL DEFAULT now(),
 last_seen timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 revoked_at timestamptz
);
ALTER TABLE platform.identity_sessions OWNER TO foc_owner;
ALTER TABLE platform.identity_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.identity_sessions FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,UPDATE ON platform.identity_sessions TO foc_policy;
CREATE POLICY identity_sessions_policy ON platform.identity_sessions TO foc_policy USING(true) WITH CHECK(true);
GRANT INSERT ON app.audit_events TO foc_policy;
GRANT USAGE ON SEQUENCE app.audit_events_sequence_seq TO foc_policy;
CREATE POLICY audit_append ON app.audit_events FOR INSERT TO foc_policy WITH CHECK(true);
CREATE POLICY audit_policy_read ON app.audit_events FOR SELECT TO foc_policy USING(true);
GRANT SELECT ON app.audit_events TO foc_policy;
GRANT INSERT,UPDATE ON app.memberships TO foc_policy;
CREATE POLICY membership_insert ON app.memberships FOR INSERT TO foc_policy WITH CHECK(true);
CREATE POLICY membership_update ON app.memberships FOR UPDATE TO foc_policy USING(true) WITH CHECK(true);
CREATE FUNCTION platform.identity_lookup(issuer text, subject text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,app
AS $$ SELECT id FROM app.staff_principals WHERE oidc_issuer=issuer AND oidc_subject=subject AND disabled_at IS NULL $$;
CREATE FUNCTION platform.active_member(org uuid, required_role text DEFAULT NULL) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,app
AS $$ SELECT EXISTS(SELECT 1 FROM app.memberships m JOIN app.organizations o ON o.id=m.organization_id JOIN app.staff_principals p ON p.id=m.principal_id WHERE m.organization_id=org AND org::text=current_setting('foc.organization',true) AND p.id::text=current_setting('foc.principal',true) AND p.disabled_at IS NULL AND o.approved_status='approved' AND o.suspended_at IS NULL AND m.starts_at<=now() AND m.expires_at>now() AND m.revoked_at IS NULL AND (required_role IS NULL OR m.role=required_role)) $$;
CREATE FUNCTION platform.identity_orgs() RETURNS TABLE(id uuid, role text)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,app
AS $$ SELECT m.organization_id,m.role FROM app.memberships m JOIN app.organizations o ON o.id=m.organization_id JOIN app.staff_principals p ON p.id=m.principal_id WHERE p.id::text=current_setting('foc.principal',true) AND p.disabled_at IS NULL AND o.approved_status='approved' AND o.suspended_at IS NULL AND m.starts_at<=now() AND m.expires_at>now() AND m.revoked_at IS NULL $$;
CREATE FUNCTION platform.session_create(hash bytea, pid uuid, ciphertext text, csrf bytea, expiry timestamptz) RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,platform
AS $$ INSERT INTO platform.identity_sessions(token_hash,principal_id,encrypted_token,csrf_hash,expires_at) SELECT hash,pid,ciphertext,csrf,least(expiry,now()+interval '30 minutes') WHERE pid::text=current_setting('foc.principal',true) $$;
CREATE FUNCTION platform.session_get(hash bytea) RETURNS TABLE(principal_id uuid,encrypted_token text,csrf_hash bytea)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,platform,app
AS $$ UPDATE platform.identity_sessions s SET last_seen=now() FROM app.staff_principals p WHERE s.token_hash=hash AND s.principal_id=p.id AND p.disabled_at IS NULL AND s.revoked_at IS NULL AND s.expires_at>now() AND s.last_seen>now()-interval '10 minutes' RETURNING s.principal_id,s.encrypted_token,s.csrf_hash $$;
CREATE FUNCTION platform.session_revoke(hash bytea) RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,platform
AS $$ UPDATE platform.identity_sessions SET revoked_at=now() WHERE token_hash=hash $$;
CREATE FUNCTION platform.audit_append(org uuid, action_name text, target uuid, result text) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app,public
AS $$
DECLARE prior bytea; event uuid:=gen_random_uuid(); actor uuid:=nullif(current_setting('foc.principal',true),'')::uuid; stamp timestamptz:=clock_timestamp();
BEGIN
 IF NOT platform.active_member(org,NULL) OR action_name NOT IN ('session.logout','identity.read','membership.grant','membership.revoke','case.permission.allowed','case.permission.denied','audit.read') OR result NOT IN ('allowed','denied') THEN RAISE EXCEPTION 'authorization denied' USING ERRCODE='42501'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(org::text,0));
 SELECT event_hash INTO prior FROM app.audit_events WHERE organization_id=org ORDER BY sequence DESC LIMIT 1;
 prior:=coalesce(prior,decode(repeat('00',32),'hex'));
 INSERT INTO app.audit_events(organization_id,event_id,actor_ref,action,target_ref,purpose,outcome,previous_hash,event_hash,occurred_at)
 VALUES(org,event,actor,action_name,target,'identity_security',result,prior,digest(prior||convert_to(jsonb_build_array(event,actor,action_name,target,'identity_security',result,stamp)::text,'UTF8'),'sha256'),stamp);
END $$;
CREATE FUNCTION platform.membership_change(org uuid, target uuid, desired_role text, expiry timestamptz, revoke boolean) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app
AS $$ BEGIN
 IF NOT platform.active_member(org,'org_admin') OR target::text=current_setting('foc.principal',true) OR desired_role NOT IN ('reviewer','supervisor') OR expiry<=now() OR expiry>now()+interval '30 days' OR NOT EXISTS(SELECT 1 FROM app.staff_principals WHERE id=target AND disabled_at IS NULL) THEN RAISE EXCEPTION 'authorization denied' USING ERRCODE='42501'; END IF;
 IF revoke THEN UPDATE app.memberships SET revoked_at=now() WHERE organization_id=org AND principal_id=target AND role=desired_role;
 ELSE INSERT INTO app.memberships(organization_id,principal_id,role,expires_at) VALUES(org,target,desired_role,expiry) ON CONFLICT(organization_id,principal_id,role) DO UPDATE SET expires_at=excluded.expires_at,starts_at=now(),revoked_at=NULL;
 END IF;
 PERFORM platform.audit_append(org,CASE WHEN revoke THEN 'membership.revoke' ELSE 'membership.grant' END,target,'allowed');
 END $$;
CREATE FUNCTION platform.audit_read(org uuid) RETURNS TABLE(sequence bigint,event_id uuid,action text,outcome text,previous_hash bytea,event_hash bytea,occurred_at timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,app
AS $$ SELECT a.sequence,a.event_id,a.action,a.outcome,a.previous_hash,a.event_hash,a.occurred_at FROM app.audit_events a WHERE a.organization_id=org AND platform.active_member(org,'org_admin') ORDER BY a.sequence DESC LIMIT 100 $$;
DO $functions$
DECLARE f record;
BEGIN
 FOR f IN SELECT p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('identity_lookup','active_member','identity_orgs','session_create','session_get','session_revoke','audit_append','membership_change','audit_read') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature);
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature);
 EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_api',f.signature);
 END LOOP;
END $functions$;
