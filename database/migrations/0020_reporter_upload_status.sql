CREATE FUNCTION platform.reporter_upload_states(token bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE ctx jsonb:=platform.reporter_context(token);
BEGIN
 IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 RETURN coalesce((SELECT jsonb_agg(jsonb_build_object('id',u.id,'state',u.state) ORDER BY u.id) FROM app.upload_intents u WHERE u.organization_id=(ctx->>'organization_id')::uuid AND u.case_id=(ctx->>'case_id')::uuid),'[]'::jsonb);
END $$;
ALTER FUNCTION platform.reporter_upload_states(bytea) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.reporter_upload_states(bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.reporter_upload_states(bytea) TO foc_api;
