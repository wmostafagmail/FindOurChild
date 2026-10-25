-- Bound per-case journal growth in the synthetic MVP; never silently evict immutable claims.
CREATE FUNCTION platform.reporting_journal_quota() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended(NEW.organization_id::text||NEW.case_id::text,3));
 IF (SELECT count(*) FROM platform.report_versions WHERE organization_id=NEW.organization_id AND case_id=NEW.case_id)>=200 THEN RAISE EXCEPTION 'case journal quota reached' USING ERRCODE='P0422'; END IF;
 RETURN NEW;
END $$;
ALTER FUNCTION platform.reporting_journal_quota() OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.reporting_journal_quota() FROM PUBLIC;
CREATE TRIGGER journal_quota BEFORE INSERT ON platform.report_versions FOR EACH ROW EXECUTE FUNCTION platform.reporting_journal_quota();
