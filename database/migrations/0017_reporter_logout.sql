CREATE FUNCTION platform.reporter_logout(token bytea) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE ctx jsonb:=platform.reporter_context(token);
BEGIN
 IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 UPDATE platform.report_sessions SET revoked_at=now() WHERE hash=token;
 UPDATE app.report_access SET revoked_at=now() WHERE organization_id=(ctx->>'organization_id')::uuid AND id=(ctx->>'access_id')::uuid;
 PERFORM platform.reporting_audit((ctx->>'organization_id')::uuid,(ctx->>'access_id')::uuid,'reporter.logout',(ctx->>'case_id')::uuid);
END $$;
ALTER FUNCTION platform.reporter_logout(bytea) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.reporter_logout(bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.reporter_logout(bytea) TO foc_api;
