-- Synthetic server-side recovery; no sensitive browser storage or public draft identifier.
CREATE TABLE platform.report_drafts(hash bytea PRIMARY KEY CHECK(octet_length(hash)=32),body_ciphertext text NOT NULL,revision bigint NOT NULL CHECK(revision>0),expires_at timestamptz NOT NULL);
ALTER TABLE platform.report_drafts OWNER TO foc_owner;
ALTER TABLE platform.report_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.report_drafts FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,UPDATE,DELETE ON platform.report_drafts TO foc_policy;
CREATE POLICY internal_drafts ON platform.report_drafts TO foc_policy USING(true) WITH CHECK(true);
CREATE FUNCTION platform.draft_read(token bytea) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform AS $$ SELECT jsonb_build_object('ciphertext',body_ciphertext,'revision',revision) FROM platform.report_drafts WHERE hash=token AND expires_at>now() $$;
CREATE FUNCTION platform.draft_store(token bytea,cipher text,expected bigint) RETURNS bigint LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
DECLARE prior platform.report_drafts;
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(encode(token,'hex'),2));
 SELECT * INTO prior FROM platform.report_drafts WHERE hash=token AND expires_at>now() FOR UPDATE;
 IF FOUND THEN
  IF prior.revision<>expected THEN RAISE EXCEPTION 'stale' USING ERRCODE='P0412'; END IF;
  UPDATE platform.report_drafts SET body_ciphertext=cipher,revision=revision+1,expires_at=now()+interval '7 days' WHERE hash=token;
  RETURN prior.revision+1;
 END IF;
 IF expected<>0 THEN RAISE EXCEPTION 'expired' USING ERRCODE='P0412'; END IF;
 INSERT INTO platform.report_drafts VALUES(token,cipher,1,now()+interval '7 days') ON CONFLICT(hash) DO UPDATE SET body_ciphertext=EXCLUDED.body_ciphertext,revision=1,expires_at=EXCLUDED.expires_at;
 RETURN 1;
END $$;
CREATE FUNCTION platform.draft_delete(token bytea) RETURNS void LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$ DELETE FROM platform.report_drafts WHERE hash=token $$;
CREATE FUNCTION platform.draft_expire() RETURNS void LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$ DELETE FROM platform.report_drafts WHERE expires_at<=now() $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.proname,p.oid::regprocedure AS signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('draft_read','draft_store','draft_delete','draft_expire') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature);EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature);EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',f.signature,CASE WHEN f.proname='draft_expire' THEN 'foc_worker' ELSE 'foc_api' END);
 END LOOP;
END $$;
