-- Separate disposable cluster only. Never apply to the operational application database.
DO $$ BEGIN
  IF current_database() <> 'foc_qualification' THEN
    RAISE EXCEPTION 'synthetic qualification database required';
  END IF;
END $$;
COMMENT ON DATABASE foc_qualification IS 'FOC synthetic isolated qualification v1';
REVOKE CONNECT, TEMPORARY ON DATABASE foc_qualification FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE ROLE foc_qualification LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
GRANT CONNECT ON DATABASE foc_qualification TO foc_qualification;
CREATE SCHEMA qualification;
REVOKE ALL ON SCHEMA qualification FROM PUBLIC;
GRANT USAGE ON SCHEMA qualification TO foc_qualification;

CREATE TABLE qualification.protocols (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL,
  protocol_hash text NOT NULL CHECK (protocol_hash ~ '^[a-f0-9]{64}$'),
  data_class text NOT NULL CHECK (data_class = 'synthetic'),
  expires_at timestamptz NOT NULL, revoked_at timestamptz,
  UNIQUE (organization_id, id, protocol_hash)
);
CREATE TABLE qualification.datasets (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL, protocol_id uuid NOT NULL,
  protocol_hash text NOT NULL, manifest_hash text NOT NULL CHECK (manifest_hash ~ '^[a-f0-9]{64}$'),
  data_class text NOT NULL CHECK (data_class = 'synthetic'),
  provenance text NOT NULL CHECK (provenance = 'procedural-geometric-fixtures'),
  expires_at timestamptz NOT NULL, revoked_at timestamptz,
  FOREIGN KEY (organization_id, protocol_id, protocol_hash) REFERENCES qualification.protocols(organization_id,id,protocol_hash) ON DELETE CASCADE,
  UNIQUE (organization_id,id,protocol_hash)
);
CREATE TABLE qualification.grants (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL, dataset_id uuid NOT NULL,
  protocol_hash text NOT NULL, principal_id uuid NOT NULL,
  purpose text NOT NULL CHECK (purpose = 'synthetic-qualification'),
  expires_at timestamptz NOT NULL, revoked_at timestamptz,
  FOREIGN KEY (organization_id,dataset_id,protocol_hash) REFERENCES qualification.datasets(organization_id,id,protocol_hash) ON DELETE CASCADE
);
CREATE TABLE qualification.evaluations (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL, dataset_id uuid NOT NULL,
  protocol_hash text NOT NULL, source_hash text NOT NULL CHECK (source_hash ~ '^[a-f0-9]{64}$'),
  synthetic boolean NOT NULL CHECK (synthetic IS TRUE),
  recognition_accuracy_claim boolean NOT NULL CHECK (recognition_accuracy_claim IS FALSE),
  FOREIGN KEY (organization_id,dataset_id,protocol_hash) REFERENCES qualification.datasets(organization_id,id,protocol_hash) ON DELETE CASCADE
);
ALTER TABLE qualification.protocols ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification.protocols FORCE ROW LEVEL SECURITY;
ALTER TABLE qualification.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification.datasets FORCE ROW LEVEL SECURITY;
ALTER TABLE qualification.grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification.grants FORCE ROW LEVEL SECURITY;
ALTER TABLE qualification.evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification.evaluations FORCE ROW LEVEL SECURITY;

CREATE POLICY protocols_scope ON qualification.protocols FOR SELECT TO foc_qualification USING (
  organization_id::text = current_setting('foc.lab_organization',true)
  AND current_setting('foc.lab_principal',true) <> ''
  AND current_setting('foc.lab_purpose',true) = 'synthetic-qualification'
  AND expires_at > statement_timestamp() AND revoked_at IS NULL
);
CREATE POLICY grants_scope ON qualification.grants FOR SELECT TO foc_qualification USING (
  organization_id::text = current_setting('foc.lab_organization',true)
  AND principal_id::text = current_setting('foc.lab_principal',true)
  AND purpose = current_setting('foc.lab_purpose',true)
  AND expires_at > statement_timestamp() AND revoked_at IS NULL
);
CREATE POLICY datasets_scope ON qualification.datasets FOR SELECT TO foc_qualification USING (
  organization_id::text = current_setting('foc.lab_organization',true)
  AND expires_at > statement_timestamp() AND revoked_at IS NULL
  AND EXISTS (SELECT 1 FROM qualification.protocols p WHERE p.id=protocol_id AND p.organization_id=qualification.datasets.organization_id AND p.protocol_hash=qualification.datasets.protocol_hash)
  AND EXISTS (SELECT 1 FROM qualification.grants g WHERE g.dataset_id=qualification.datasets.id AND g.organization_id=qualification.datasets.organization_id AND g.protocol_hash=qualification.datasets.protocol_hash)
);
CREATE POLICY evaluations_scope ON qualification.evaluations FOR SELECT TO foc_qualification USING (
  EXISTS (SELECT 1 FROM qualification.datasets d WHERE d.id=dataset_id AND d.organization_id=qualification.evaluations.organization_id AND d.protocol_hash=qualification.evaluations.protocol_hash)
);
GRANT SELECT ON ALL TABLES IN SCHEMA qualification TO foc_qualification;
ALTER ROLE foc_qualification SET default_transaction_isolation TO 'read committed';
ALTER ROLE foc_qualification SET statement_timeout TO '5s';
ALTER ROLE foc_qualification SET idle_in_transaction_session_timeout TO '10s';
