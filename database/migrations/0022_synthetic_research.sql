-- Phase 2A offline synthetic research namespace only. No application biometric grants.
CREATE ROLE foc_research NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
GRANT USAGE ON SCHEMA platform TO foc_research;
CREATE TABLE platform.research_grants (
 organization_id uuid NOT NULL, principal_id uuid NOT NULL, protocol text NOT NULL CHECK(protocol='synthetic-2a-v1'),
 expires_at timestamptz NOT NULL, revoked_at timestamptz, PRIMARY KEY(organization_id,principal_id)
);
ALTER TABLE platform.research_grants OWNER TO foc_owner;
ALTER TABLE platform.research_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.research_grants FORCE ROW LEVEL SECURITY;
GRANT SELECT ON platform.research_grants TO foc_policy;
CREATE POLICY research_internal ON platform.research_grants TO foc_policy USING(true);
CREATE FUNCTION platform.research_authorized(org uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
 SELECT current_setting('foc.purpose',true)='research_evaluation'
 AND current_setting('foc.organization',true)=org::text
 AND EXISTS(SELECT 1 FROM platform.research_grants g WHERE g.organization_id=org AND g.principal_id::text=current_setting('foc.principal',true) AND g.revoked_at IS NULL AND g.expires_at>statement_timestamp())
$$;
ALTER FUNCTION platform.research_authorized(uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.research_authorized(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.research_authorized(uuid) TO foc_research;
CREATE TABLE platform.research_datasets (
 organization_id uuid NOT NULL, id uuid NOT NULL, synthetic boolean NOT NULL CHECK(synthetic),
 protocol text NOT NULL CHECK(protocol='synthetic-2a-v1'), expires_at timestamptz NOT NULL,
 generation bigint NOT NULL CHECK(generation>0), revoked_at timestamptz, PRIMARY KEY(organization_id,id), UNIQUE(organization_id,id,generation)
);
CREATE TABLE platform.research_photographs (
 organization_id uuid NOT NULL, dataset_id uuid NOT NULL, generation bigint NOT NULL, id uuid NOT NULL,
 case_ref uuid NOT NULL, subject_ref uuid NOT NULL, family_ref uuid NOT NULL,
 image_sha256 text NOT NULL CHECK(image_sha256 ~ '^[a-f0-9]{64}$'), registry text NOT NULL CHECK(registry IN ('missing','found')),
 partition text NOT NULL CHECK(partition IN ('development','calibration','test')), role text NOT NULL CHECK(role IN ('gallery','probe')),
 capture_lower date, capture_upper date, capture_precision text NOT NULL CHECK(capture_precision IN ('unknown','interval','day')),
 age_min_months integer, age_max_months integer, age_reference_lower date, age_reference_upper date,
 source text NOT NULL CHECK(source='procedural-geometric-fixture-v1'), synthetic boolean NOT NULL CHECK(synthetic),
 PRIMARY KEY(organization_id,dataset_id,id), UNIQUE(organization_id,dataset_id,image_sha256), UNIQUE(organization_id,dataset_id,id,generation),
 FOREIGN KEY(organization_id,dataset_id,generation) REFERENCES platform.research_datasets(organization_id,id,generation) ON DELETE CASCADE,
 CHECK((capture_lower IS NULL AND capture_upper IS NULL AND capture_precision='unknown') OR (capture_lower IS NOT NULL AND capture_upper IS NOT NULL AND capture_lower<=capture_upper AND capture_precision<>'unknown')),
 CHECK(capture_precision<>'day' OR capture_lower=capture_upper),
 CHECK((age_min_months IS NULL AND age_max_months IS NULL) OR (age_min_months IS NOT NULL AND age_max_months IS NOT NULL AND age_min_months>=0 AND age_min_months<=age_max_months AND age_max_months<=1500)),
 CHECK((age_reference_lower IS NULL AND age_reference_upper IS NULL) OR (age_reference_lower IS NOT NULL AND age_reference_upper IS NOT NULL AND age_reference_lower<=age_reference_upper))
);
CREATE TABLE platform.research_vectors_synthetic_v1 (
 organization_id uuid NOT NULL, dataset_id uuid NOT NULL, photo_id uuid NOT NULL,
 space_id text NOT NULL CHECK(space_id='a4b39dd8ee7e3e4a756d70981d91d8a84314975147893a5c68d28b30b00bf14b'), vector public.vector(128) NOT NULL,
 source_revision bigint NOT NULL CHECK(source_revision>0), created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(organization_id,dataset_id,photo_id,space_id),
 FOREIGN KEY(organization_id,dataset_id,photo_id,source_revision) REFERENCES platform.research_photographs(organization_id,dataset_id,id,generation) ON DELETE CASCADE,
 CHECK(abs(public.vector_norm(vector)-1)<0.00001)
);
-- Exact scoped retrieval is the baseline. HNSW remains unprovisioned until ANN parity is measured.
CREATE INDEX research_photo_scope ON platform.research_photographs(organization_id,dataset_id,registry,partition,role,case_ref);
CREATE FUNCTION platform.research_dataset_active(org uuid,ds uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
 SELECT EXISTS(SELECT 1 FROM platform.research_datasets d WHERE d.organization_id=org AND d.id=ds AND d.synthetic AND d.revoked_at IS NULL AND d.expires_at>statement_timestamp())
$$;
ALTER FUNCTION platform.research_dataset_active(uuid,uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.research_dataset_active(uuid,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.research_dataset_active(uuid,uuid) TO foc_research;
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['research_datasets','research_photographs','research_vectors_synthetic_v1'] LOOP
 EXECUTE format('ALTER TABLE platform.%I OWNER TO foc_owner',t);
 EXECUTE format('ALTER TABLE platform.%I ENABLE ROW LEVEL SECURITY',t);
 EXECUTE format('ALTER TABLE platform.%I FORCE ROW LEVEL SECURITY',t);
 EXECUTE format('GRANT SELECT ON platform.%I TO foc_policy',t);
 EXECUTE format('CREATE POLICY research_internal ON platform.%I TO foc_policy USING(true)',t);
 END LOOP;
END $$;
GRANT SELECT ON platform.research_datasets TO foc_research;
CREATE POLICY research_read ON platform.research_datasets TO foc_research USING(platform.research_authorized(organization_id) AND revoked_at IS NULL AND expires_at>statement_timestamp());
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['research_photographs','research_vectors_synthetic_v1'] LOOP
 EXECUTE format('GRANT SELECT,INSERT,DELETE ON platform.%I TO foc_research',t);
 EXECUTE format('CREATE POLICY research_scoped ON platform.%I TO foc_research USING(platform.research_authorized(organization_id) AND platform.research_dataset_active(organization_id,dataset_id)) WITH CHECK(platform.research_authorized(organization_id) AND platform.research_dataset_active(organization_id,dataset_id))',t);
 END LOOP;
END $$;
-- Security invoker: RLS applies to probe, each candidate photograph and every vector.
CREATE FUNCTION platform.research_exact_candidates(org uuid,ds uuid,probe uuid,k integer) RETURNS TABLE(case_ref uuid,similarity double precision) LANGUAGE plpgsql SET search_path=pg_catalog,platform AS $$
BEGIN
 IF k IS NULL OR k<1 OR k>50 THEN RAISE EXCEPTION 'invalid research budget' USING ERRCODE='22023'; END IF;
 RETURN QUERY WITH probe_row AS (
 SELECT p.registry,p.partition,v.vector FROM platform.research_photographs p JOIN platform.research_vectors_synthetic_v1 v ON v.organization_id=p.organization_id AND v.dataset_id=p.dataset_id AND v.photo_id=p.id
 WHERE p.organization_id=org AND p.dataset_id=ds AND p.id=probe AND p.role='probe'
 ), sampled AS (
 SELECT p.*,v.vector,row_number() OVER(PARTITION BY p.case_ref ORDER BY p.image_sha256) AS photo_rank
 FROM platform.research_photographs p JOIN platform.research_vectors_synthetic_v1 v ON v.organization_id=p.organization_id AND v.dataset_id=p.dataset_id AND v.photo_id=p.id
 WHERE p.organization_id=org AND p.dataset_id=ds AND p.role='gallery'
 ), scored AS (
 SELECT g.case_ref, max(1-(g.vector OPERATOR(public.<=>) q.vector)) AS similarity
 FROM sampled g CROSS JOIN probe_row q WHERE g.registry<>q.registry AND g.partition=q.partition AND g.photo_rank<=3 GROUP BY g.case_ref
 ) SELECT s.case_ref,s.similarity FROM scored s ORDER BY s.similarity DESC,s.case_ref LIMIT k;
END $$;
ALTER FUNCTION platform.research_exact_candidates(uuid,uuid,uuid,integer) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.research_exact_candidates(uuid,uuid,uuid,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.research_exact_candidates(uuid,uuid,uuid,integer) TO foc_research;
