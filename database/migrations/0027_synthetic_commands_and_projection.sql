-- Closed SQL inputs as well as HTTP DTOs, and permission-scoped photo provenance.
GRANT SELECT ON platform.environment TO foc_policy;
CREATE OR REPLACE FUNCTION platform.sw_event_command(org uuid,lid uuid,operation text,payload jsonb,expected bigint,command uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF jsonb_typeof(payload) IS DISTINCT FROM 'object' OR NOT payload ?& ARRAY['snapshot_hash','uncertainty_acknowledged','rationale_codes','evidence_refs']
 OR jsonb_typeof(payload->'rationale_codes') IS DISTINCT FROM 'array' OR jsonb_typeof(payload->'evidence_refs') IS DISTINCT FROM 'array'
 OR payload->>'snapshot_hash' IS NULL OR payload->>'snapshot_hash' !~ '^[a-f0-9]{64}$'
 OR EXISTS(SELECT 1 FROM jsonb_array_elements(payload->'rationale_codes') value WHERE jsonb_typeof(value) IS DISTINCT FROM 'string')
 OR EXISTS(SELECT 1 FROM jsonb_array_elements(payload->'evidence_refs') value WHERE jsonb_typeof(value) IS DISTINCT FROM 'string')
 OR (operation IN ('reviews','independent-reviews') AND payload->>'outcome' IS NULL)
 OR (operation='independent-reviews' AND payload->>'first_review_id' IS NULL)
 THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 IF operation IN ('assignments','peer-review-requests') AND NOT platform.sw_target_valid(org,lid,(payload->>'principal_id')::uuid,(payload->>'expires_at')::timestamptz,operation='peer-review-requests') THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN platform.sw_event_command_base(org,lid,operation,payload,expected,command);
END $$;
ALTER FUNCTION platform.sw_read(uuid,uuid,text) RENAME TO sw_read_base;
REVOKE EXECUTE ON FUNCTION platform.sw_read_base(uuid,uuid,text) FROM foc_api;
CREATE FUNCTION platform.sw_read(org uuid,lid uuid,view_name text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb;
BEGIN
 result:=platform.sw_read_base(org,lid,view_name);
 IF view_name='comparison' THEN
 result:=jsonb_set(result,'{result_source,photo_refs}',coalesce((SELECT jsonb_agg(p->'id') FROM jsonb_array_elements(result->'photos') p),'[]'::jsonb));
 END IF;
 RETURN result;
END $$;
ALTER FUNCTION platform.sw_read(uuid,uuid,text) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.sw_read(uuid,uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.sw_read(uuid,uuid,text) TO foc_api;
