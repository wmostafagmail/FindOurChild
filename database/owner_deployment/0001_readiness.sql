-- Separate deployment/session store; no operational database credentials or campaign issuance.
CREATE SCHEMA owner_deployment;
REVOKE ALL ON SCHEMA owner_deployment FROM PUBLIC;
CREATE TABLE owner_deployment.sessions (
 instance uuid NOT NULL, tenant uuid NOT NULL, key text PRIMARY KEY CHECK(key ~ '^[0-9a-f]{64}$'),
 encrypted_token text NOT NULL CHECK(length(encrypted_token)<=32768),
 csrf text NOT NULL CHECK(csrf ~ '^[0-9a-f]{64}$'), expires bigint NOT NULL CHECK(expires>0),
 revoked boolean NOT NULL DEFAULT false, activation_epoch bigint NOT NULL, authority_epoch bigint NOT NULL
);
CREATE TABLE owner_deployment.proofs (
 instance uuid NOT NULL, tenant uuid NOT NULL, key text PRIMARY KEY CHECK(key ~ '^[0-9a-f]{64}$'),
 session_key text NOT NULL REFERENCES owner_deployment.sessions(key), config_digest text NOT NULL CHECK(config_digest ~ '^[0-9a-f]{64}$'),
 expires bigint NOT NULL, consumed boolean NOT NULL DEFAULT false
);
ALTER TABLE owner_deployment.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_deployment.sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE owner_deployment.proofs ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_deployment.proofs FORCE ROW LEVEL SECURITY;
CREATE POLICY session_scope ON owner_deployment.sessions TO foc_v3_service
 USING(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true))
 WITH CHECK(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true));
CREATE POLICY proof_scope ON owner_deployment.proofs TO foc_v3_service
 USING(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true))
 WITH CHECK(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true));
REVOKE ALL ON ALL TABLES IN SCHEMA owner_deployment FROM PUBLIC;
GRANT USAGE ON SCHEMA owner_deployment TO foc_v3_service;
GRANT SELECT,INSERT ON owner_deployment.sessions,owner_deployment.proofs TO foc_v3_service;
GRANT UPDATE(revoked) ON owner_deployment.sessions TO foc_v3_service;

CREATE TABLE owner_deployment.registry_commits (
 key text PRIMARY KEY CHECK(key ~ '^[0-9a-f]{64}$'), instance uuid NOT NULL, tenant uuid NOT NULL,
 config_digest text NOT NULL, activation_epoch bigint NOT NULL, authority_epoch bigint NOT NULL
);
ALTER TABLE owner_deployment.registry_commits ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_deployment.registry_commits FORCE ROW LEVEL SECURITY;
CREATE POLICY registry_scope ON owner_deployment.registry_commits TO foc_v3_service
 USING(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true));
REVOKE ALL ON owner_deployment.registry_commits FROM PUBLIC;
GRANT SELECT ON owner_deployment.registry_commits TO foc_v3_service;
CREATE TRIGGER immutable_registry_commit BEFORE UPDATE OR DELETE ON owner_deployment.registry_commits
 FOR EACH ROW EXECUTE FUNCTION owner_only_demo.reject_mutation();
CREATE FUNCTION owner_deployment.no_unrevoke() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
 BEGIN IF OLD.revoked AND NOT NEW.revoked THEN RAISE EXCEPTION 'session_revocation_is_permanent' USING ERRCODE='42501'; END IF; RETURN NEW; END $$;
REVOKE ALL ON FUNCTION owner_deployment.no_unrevoke() FROM PUBLIC;
CREATE TRIGGER irreversible_session_revocation BEFORE UPDATE ON owner_deployment.sessions
 FOR EACH ROW EXECUTE FUNCTION owner_deployment.no_unrevoke();
