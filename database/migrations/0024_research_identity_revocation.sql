-- Research permission is additional to active organization membership, never an alternative identity grant.
CREATE OR REPLACE FUNCTION platform.research_authorized(org uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
 SELECT current_setting('foc.purpose',true)='research_evaluation'
 AND current_setting('foc.organization',true)=org::text
 AND platform.active_member(org,NULL)
 AND EXISTS(SELECT 1 FROM app.memberships m WHERE m.organization_id=org AND m.principal_id::text=current_setting('foc.principal',true) AND m.starts_at<=statement_timestamp() AND m.expires_at>statement_timestamp() AND m.revoked_at IS NULL)
 AND EXISTS(SELECT 1 FROM platform.research_grants g WHERE g.organization_id=org AND g.principal_id::text=current_setting('foc.principal',true) AND g.revoked_at IS NULL AND g.expires_at>statement_timestamp())
$$;
