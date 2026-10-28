-- Evaluate sealed-scenario freshness once per scenario in each statement,
-- retaining all live tenant, purpose, workflow and paired case permission checks.
-- Direct table RLS stays unchanged. The API calls this again after audit waits.
CREATE FUNCTION platform.sw_queue(org uuid,cid uuid,selected_state text,mine boolean,skip_count integer,page_size integer)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb;
BEGIN
 IF skip_count IS NULL OR page_size IS NULL OR mine IS NULL OR skip_count<0 OR page_size<0 OR page_size>101 OR selected_state IS NOT NULL AND selected_state NOT IN ('pending','held','rejected','escalated') THEN
 RAISE EXCEPTION 'invalid bounded queue' USING ERRCODE='22023'; END IF;
 IF platform.case_permission(org,cid,'case.read') IS NOT TRUE THEN
 RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 WITH allowed_scenarios AS MATERIALIZED (
 SELECT s.id FROM platform.synthetic_workflow_scenarios s
 WHERE s.organization_id=org AND s.manifest->>'query_case_id'=cid::text
 AND platform.sw_allowed(org,s.id,'view') AND platform.sw_current(org,s.id)
 ), visible AS MATERIALIZED (
 SELECT l.id,l.review_state,l.investigation_state,l.revision,l.run_id,r.created_at,l.internal_rank
 FROM app.synthetic_candidate_leads l
 JOIN app.synthetic_matching_runs r ON r.organization_id=l.organization_id AND r.id=l.run_id
 JOIN allowed_scenarios s ON s.id=l.scenario_id
 WHERE l.organization_id=org AND l.query_case_id=cid AND r.state='completed'
 AND platform.case_permission(org,l.candidate_case_id,'case.read')
 AND (selected_state IS NULL OR l.review_state=selected_state)
 AND (NOT mine OR EXISTS(SELECT 1 FROM app.synthetic_investigation_tasks t
 WHERE t.organization_id=org AND t.lead_id=l.id AND t.target::text=current_setting('foc.principal',true)
 AND t.state='pending' AND t.expires_at>now()))
 ), ordered AS (
 SELECT id,review_state,investigation_state,revision,run_id,
 row_number() OVER(ORDER BY created_at DESC,internal_rank,id) visible_rank FROM visible
 ), page AS (
 SELECT * FROM ordered ORDER BY visible_rank LIMIT page_size OFFSET skip_count
 )
 SELECT jsonb_build_object(
 'stamp',(SELECT encode(sha256(convert_to(coalesce(string_agg(id::text||revision::text,',' ORDER BY id),''),'UTF8')),'hex') FROM visible),
 'items',coalesce((SELECT jsonb_agg(jsonb_build_object('id',id,'review_state',review_state,
 'investigation_state',investigation_state,'revision',revision,'run_id',run_id,
 'visible_rank',visible_rank,'data_class','synthetic') ORDER BY visible_rank) FROM page),'[]'::jsonb)) INTO result;
 RETURN result;
END $$;
ALTER FUNCTION platform.sw_queue(uuid,uuid,text,boolean,integer,integer) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.sw_queue(uuid,uuid,text,boolean,integer,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.sw_queue(uuid,uuid,text,boolean,integer,integer) TO foc_api;
