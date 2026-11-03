-- Separate private V3 control-plane database. No application or research credentials.
-- Bootstrap/enabling is deliberately NOT provided. Empty, inactive authority is the default.
CREATE SCHEMA owner_only_demo;
REVOKE ALL ON SCHEMA owner_only_demo FROM PUBLIC;
DO $$ BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='foc_v3_service') THEN
  CREATE ROLE foc_v3_service NOLOGIN NOSUPERUSER NOBYPASSRLS;
 END IF;
END $$;
CREATE TABLE owner_only_demo.authority (
 instance uuid PRIMARY KEY, tenant uuid NOT NULL,
 enabled boolean NOT NULL DEFAULT false,
 activation_epoch bigint NOT NULL CHECK(activation_epoch>0),
 authority_epoch bigint NOT NULL CHECK(authority_epoch>0),
 revision bigint NOT NULL DEFAULT 0,
 checkpoint text NOT NULL CHECK(checkpoint ~ '^[0-9a-f]{64}$')
);
CREATE TABLE owner_only_demo.journal (
 instance uuid NOT NULL REFERENCES owner_only_demo.authority(instance), tenant uuid NOT NULL,
 kind text NOT NULL CHECK(kind IN ('draft','authorization','exposure','receipt','revocation','event','outbox','job')),
 key text NOT NULL CHECK(length(key) BETWEEN 1 AND 128),
 value jsonb NOT NULL CHECK(jsonb_typeof(value)='object'),
 digest text NOT NULL CHECK(digest ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 PRIMARY KEY(instance,kind,key)
);
-- Global project lineage survives new instances/tenants/authorization IDs.
-- Private control plane only: this table exposes no photograph, subject or score.
CREATE TABLE owner_only_demo.fixture_exposure (
 key text PRIMARY KEY CHECK(key ~ '^[0-9a-f]{64}$'),
 value jsonb NOT NULL CHECK(jsonb_typeof(value)='object'),
 digest text NOT NULL CHECK(digest ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
ALTER TABLE owner_only_demo.authority ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_only_demo.authority FORCE ROW LEVEL SECURITY;
ALTER TABLE owner_only_demo.journal ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_only_demo.journal FORCE ROW LEVEL SECURITY;
ALTER TABLE owner_only_demo.fixture_exposure ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_only_demo.fixture_exposure FORCE ROW LEVEL SECURITY;
CREATE POLICY global_lineage ON owner_only_demo.fixture_exposure TO foc_v3_service USING(true) WITH CHECK(true);
CREATE POLICY authority_scope ON owner_only_demo.authority TO foc_v3_service
 USING(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true))
 WITH CHECK(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true));
CREATE POLICY journal_scope ON owner_only_demo.journal TO foc_v3_service
 USING(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true))
 WITH CHECK(instance::text=current_setting('foc.v3_instance',true) AND tenant::text=current_setting('foc.v3_tenant',true));
CREATE FUNCTION owner_only_demo.reject_mutation() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog AS $$ BEGIN RAISE EXCEPTION 'immutable_v3_journal' USING ERRCODE='42501'; END $$;
CREATE TRIGGER immutable_v3 BEFORE UPDATE OR DELETE ON owner_only_demo.journal
 FOR EACH ROW EXECUTE FUNCTION owner_only_demo.reject_mutation();
CREATE TRIGGER immutable_v3_exposure BEFORE UPDATE OR DELETE ON owner_only_demo.fixture_exposure
 FOR EACH ROW EXECUTE FUNCTION owner_only_demo.reject_mutation();
REVOKE ALL ON ALL TABLES IN SCHEMA owner_only_demo FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA owner_only_demo FROM PUBLIC;
GRANT USAGE ON SCHEMA owner_only_demo TO foc_v3_service;
GRANT SELECT ON owner_only_demo.authority TO foc_v3_service;
GRANT UPDATE(revision,checkpoint) ON owner_only_demo.authority TO foc_v3_service;
GRANT SELECT,INSERT ON owner_only_demo.journal TO foc_v3_service;
GRANT SELECT,INSERT ON owner_only_demo.fixture_exposure TO foc_v3_service;
-- Runtime cannot enable/advance epochs, delete/rewrite a seal, create an authority, or enroll an owner.
