-- Bind sensitive human decisions to visible paired evidence and the corresponding reason.
CREATE OR REPLACE FUNCTION platform.sw_event_command(org uuid,lid uuid,operation text,payload jsonb,expected bigint,command uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF operation='reviews' AND payload->>'outcome' IN ('reject','escalate')
 AND NOT EXISTS(SELECT 1 FROM platform.synthetic_workflow_commands c WHERE c.organization_id=org AND c.principal_id::text=current_setting('foc.principal',true) AND c.aggregate_id=lid AND c.operation=sw_event_command.operation AND c.command=sw_event_command.command)
 AND (NOT ((payload->'rationale_codes') ? (CASE payload->>'outcome' WHEN 'reject' THEN 'CONTRADICTORY_FIXTURE_CLAIM' ELSE 'SUPPORTING_FIXTURE_CLAIM' END))
 OR NOT EXISTS(SELECT 1 FROM app.synthetic_candidate_leads l JOIN platform.synthetic_workflow_scenarios s ON s.organization_id=l.organization_id AND s.id=l.scenario_id CROSS JOIN jsonb_array_elements(s.manifest->'explanations') e WHERE l.organization_id=org AND l.id=lid AND (e->>'case_id')::uuid IN (l.query_case_id,l.candidate_case_id) AND e->>'kind'=CASE payload->>'outcome' WHEN 'reject' THEN 'contradictory' ELSE 'supporting' END AND e->>'source_ref' IN (SELECT jsonb_array_elements_text(payload->'evidence_refs'))))
 THEN RAISE EXCEPTION 'decision evidence incomplete' USING ERRCODE='P0422'; END IF;
 IF operation='reviews' AND payload->>'outcome'<>'hold' AND NOT EXISTS(SELECT 1 FROM platform.synthetic_workflow_commands c WHERE c.organization_id=org AND c.principal_id::text=current_setting('foc.principal',true) AND c.aggregate_id=lid AND c.operation=sw_event_command.operation AND c.command=sw_event_command.command) AND EXISTS(
 SELECT 1 FROM app.synthetic_candidate_leads current_lead JOIN app.synthetic_candidate_leads prior ON prior.organization_id=current_lead.organization_id AND prior.query_case_id=current_lead.query_case_id AND prior.candidate_case_id=current_lead.candidate_case_id AND prior.snapshot_hash=current_lead.snapshot_hash
 JOIN app.synthetic_investigation_events e ON e.organization_id=prior.organization_id AND e.lead_id=prior.id AND e.kind='reviews' AND e.payload->>'outcome'='reject'
 WHERE current_lead.organization_id=org AND current_lead.id=lid) THEN RAISE EXCEPTION 'new evidence required' USING ERRCODE='P0409'; END IF;
 RETURN platform.sw_event_command_validated(org,lid,operation,payload,expected,command);
END $$;
