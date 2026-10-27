-- Audit persistence can wait. Reauthorize using a fresh READ COMMITTED statement
-- after that wait, before returning a sensitive projection or committing a command.
-- Preserve every applied function body/privilege except these guarded additions.
DO $migration$
DECLARE definition text; needle text; replacement text;
BEGIN
 definition:=pg_get_functiondef('platform.sw_read(uuid,uuid,text)'::regprocedure);
 needle:=' RETURN result;';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_read definition'; END IF;
 replacement:=$body$ IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN result;$body$;
 EXECUTE replace(definition,needle,replacement);

 definition:=pg_get_functiondef('platform.sw_status(uuid)'::regprocedure);
 needle:=' RETURN jsonb_build_object(''data_class''';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_status definition'; END IF;
 replacement:=$body$ IF EXISTS(SELECT 1 FROM jsonb_array_elements(result) item WHERE NOT platform.sw_allowed(org,(item->>'id')::uuid,'view') OR NOT platform.sw_current(org,(item->>'id')::uuid) OR NOT platform.case_permission(org,(item->>'query_case_id')::uuid,'case.read')) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN jsonb_build_object('data_class'$body$;
 EXECUTE replace(definition,needle,replacement);

 definition:=pg_get_functiondef('platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid)'::regprocedure);
 needle:=E'\nBEGIN\n';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_event_command declaration'; END IF;
 definition:=replace(definition,needle,E'\nDECLARE final_result jsonb; final_scenario uuid; final_action text;\nBEGIN\n');
 needle:=' RETURN platform.sw_event_command_validated(org,lid,operation,payload,expected,command);';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_event_command return'; END IF;
 replacement:=$body$ final_result:=platform.sw_event_command_validated(org,lid,operation,payload,expected,command);
 SELECT scenario_id INTO final_scenario FROM app.synthetic_candidate_leads WHERE organization_id=org AND id=lid;
 final_action:=CASE operation WHEN 'reviews' THEN 'review' WHEN 'notes' THEN 'collaborate' WHEN 'assignments' THEN 'assign' WHEN 'peer-review-requests' THEN 'peer' WHEN 'independent-reviews' THEN 'independent' END;
 IF NOT platform.sw_pair(org,lid,'case.write') OR NOT platform.sw_allowed(org,final_scenario,final_action)
 OR NOT EXISTS(SELECT 1 FROM platform.synthetic_workflow_grants g WHERE g.organization_id=org AND g.scenario_id=final_scenario AND g.principal_id::text=current_setting('foc.principal',true) AND g.conflict_clear)
 OR (operation='assignments' AND NOT platform.active_member(org,'supervisor'))
 OR (operation='independent-reviews' AND NOT platform.active_member(org,'safeguarding'))
 OR (operation IN ('assignments','peer-review-requests') AND NOT platform.sw_target_valid(org,lid,(payload->>'principal_id')::uuid,(payload->>'expires_at')::timestamptz,operation='peer-review-requests'))
 THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN final_result;$body$;
 EXECUTE replace(definition,needle,replacement);

 definition:=pg_get_functiondef('platform.sw_run_command(uuid,uuid,text,jsonb,bigint,uuid)'::regprocedure);
 needle:=' RETURN result;';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_run_command definition'; END IF;
 replacement:=$body$ IF NOT platform.sw_allowed(org,r.scenario_id,CASE operation WHEN 'runs' THEN 'run' ELSE 'cancel' END)
 OR NOT platform.case_permission(org,r.case_id,'case.read') OR NOT platform.case_permission(org,r.case_id,'case.write')
 OR (operation='runs' AND NOT platform.case_permission(org,r.case_id,'matching.request'))
 OR (operation='cancellations' AND r.requested_by<>actor AND NOT platform.active_member(org,'supervisor'))
 THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN result;$body$;
 EXECUTE replace(definition,needle,replacement);

 definition:=pg_get_functiondef('platform.sw_finish(uuid,uuid,uuid)'::regprocedure);
 needle:=' RETURN true;';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_finish definition'; END IF;
 replacement:=$body$ IF NOT platform.sw_allowed(org,r.scenario_id,'run') OR NOT platform.sw_current(org,r.scenario_id)
 OR NOT platform.case_permission(org,r.case_id,'case.read') OR NOT platform.case_permission(org,r.case_id,'case.write') OR NOT platform.case_permission(org,r.case_id,'matching.request')
 THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN true;$body$;
 EXECUTE replace(definition,needle,replacement);
END
$migration$;
