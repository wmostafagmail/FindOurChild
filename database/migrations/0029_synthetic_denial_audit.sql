-- Record denied probes without guessed child identifiers, request bodies or rationale.
CREATE FUNCTION platform.sw_denial(org uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 IF platform.active_member(org,NULL) THEN
 PERFORM platform.reporting_audit(org,nullif(current_setting('foc.principal',true),'')::uuid,'synthetic.denied',org);
 END IF;
END $$;
ALTER FUNCTION platform.sw_denial(uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.sw_denial(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.sw_denial(uuid) TO foc_api;

CREATE OR REPLACE FUNCTION platform.sw_read(org uuid,lid uuid,view_name text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb; query_kind text; candidate_kind text;
BEGIN
 result:=platform.sw_read_base(org,lid,view_name);
 IF view_name='comparison' THEN
 result:=jsonb_set(result,'{result_source,photo_refs}',coalesce((SELECT jsonb_agg(p->'id') FROM jsonb_array_elements(result->'photos') p),'[]'::jsonb));
 result:=jsonb_set(result,'{explanations}',coalesce((SELECT jsonb_agg(e) FROM jsonb_array_elements(result->'explanations') e WHERE e->>'case_id' IN (result->>'query_case_id',result->>'candidate_case_id')),'[]'::jsonb));
 SELECT q.registry,c.registry INTO query_kind,candidate_kind FROM app.synthetic_candidate_leads l JOIN app.cases q ON q.organization_id=l.organization_id AND q.id=l.query_case_id JOIN app.cases c ON c.organization_id=l.organization_id AND c.id=l.candidate_case_id WHERE l.organization_id=org AND l.id=lid;
 result:=result||jsonb_build_object('query_registry',query_kind,'candidate_registry',candidate_kind);
 result:=result||jsonb_build_object('prior_reviews',coalesce((SELECT jsonb_agg(v) FROM (SELECT jsonb_build_object('event_id',e.id,'outcome',e.payload->>'outcome','rationale_codes',e.payload->'rationale_codes','occurred_at',e.occurred_at,'same_snapshot',e.snapshot_hash=current_lead.snapshot_hash) v FROM app.synthetic_candidate_leads current_lead JOIN app.synthetic_candidate_leads prior ON prior.organization_id=current_lead.organization_id AND prior.query_case_id=current_lead.query_case_id AND prior.candidate_case_id=current_lead.candidate_case_id JOIN app.synthetic_investigation_events e ON e.organization_id=prior.organization_id AND e.lead_id=prior.id AND e.kind='reviews' WHERE current_lead.organization_id=org AND current_lead.id=lid AND prior.id<>lid ORDER BY e.occurred_at DESC,e.id LIMIT 20) limited),'[]'::jsonb));
 END IF;
 RETURN result;
END $$;

ALTER FUNCTION platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid) RENAME TO sw_event_command_validated;
REVOKE EXECUTE ON FUNCTION platform.sw_event_command_validated(uuid,uuid,text,jsonb,bigint,uuid) FROM foc_api;
CREATE FUNCTION platform.sw_event_command(org uuid,lid uuid,operation text,payload jsonb,expected bigint,command uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF operation='reviews' AND payload->>'outcome'<>'hold' AND NOT EXISTS(SELECT 1 FROM platform.synthetic_workflow_commands c WHERE c.organization_id=org AND c.principal_id::text=current_setting('foc.principal',true) AND c.aggregate_id=lid AND c.operation=sw_event_command.operation AND c.command=sw_event_command.command) AND EXISTS(
 SELECT 1 FROM app.synthetic_candidate_leads current_lead JOIN app.synthetic_candidate_leads prior ON prior.organization_id=current_lead.organization_id AND prior.query_case_id=current_lead.query_case_id AND prior.candidate_case_id=current_lead.candidate_case_id AND prior.snapshot_hash=current_lead.snapshot_hash
 JOIN app.synthetic_investigation_events e ON e.organization_id=prior.organization_id AND e.lead_id=prior.id AND e.kind='reviews' AND e.payload->>'outcome'='reject'
 WHERE current_lead.organization_id=org AND current_lead.id=lid) THEN RAISE EXCEPTION 'new evidence required' USING ERRCODE='P0409'; END IF;
 RETURN platform.sw_event_command_validated(org,lid,operation,payload,expected,command);
END $$;
ALTER FUNCTION platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid) TO foc_api;

CREATE FUNCTION platform.sw_prior_rejection_hold() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM app.synthetic_candidate_leads l JOIN app.synthetic_investigation_events e ON e.organization_id=l.organization_id AND e.lead_id=l.id WHERE l.organization_id=NEW.organization_id AND l.query_case_id=NEW.query_case_id AND l.candidate_case_id=NEW.candidate_case_id AND l.snapshot_hash=NEW.snapshot_hash AND e.kind='reviews' AND e.payload->>'outcome'='reject') THEN NEW.review_state:='held'; END IF;
 RETURN NEW;
END $$;
ALTER FUNCTION platform.sw_prior_rejection_hold() OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.sw_prior_rejection_hold() FROM PUBLIC;
CREATE TRIGGER prior_rejection_hold BEFORE INSERT ON app.synthetic_candidate_leads FOR EACH ROW EXECUTE FUNCTION platform.sw_prior_rejection_hold();
