CREATE FUNCTION platform.draft_command(token bytea,cipher text,expected bigint,cmd uuid,body_digest bytea) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
DECLARE scope_name text:='draft:'||encode(token,'hex'); prior platform.reporting_commands; next_revision bigint;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(scope_name||cmd::text,1));
 SELECT * INTO prior FROM platform.reporting_commands WHERE scope=scope_name AND command=cmd;
 IF FOUND THEN
 IF prior.body_hash<>body_digest THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF;
 IF platform.draft_read(token) IS NULL THEN RAISE EXCEPTION 'expired' USING ERRCODE='P0412'; END IF;
 RETURN (prior.response->>'revision')::bigint;
 END IF;
 next_revision:=platform.draft_store(token,cipher,expected);
 INSERT INTO platform.reporting_commands VALUES(scope_name,cmd,body_digest,jsonb_build_object('revision',next_revision),now());RETURN next_revision;
END $$;
ALTER FUNCTION platform.draft_command(bytea,text,bigint,uuid,bytea) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.draft_command(bytea,text,bigint,uuid,bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.draft_command(bytea,text,bigint,uuid,bytea) TO foc_api;
REVOKE EXECUTE ON FUNCTION platform.draft_store(bytea,text,bigint) FROM foc_api;
