-- Authority must still be live after lock/audit waits. Transaction-start now()
-- cannot establish that. Preserve predicates/ownership/grants; use real time.
DO $migration$
DECLARE signature text; definition text; needle text; replacement text;
BEGIN
 FOREACH signature IN ARRAY ARRAY[
 'platform.case_permission(uuid,uuid,text)',
 'platform.active_member(uuid,text)',
 'platform.sw_allowed(uuid,uuid,text)',
 'platform.sw_target_valid(uuid,uuid,uuid,timestamp with time zone,boolean)',
 'platform.sw_event_command_base(uuid,uuid,text,jsonb,bigint,uuid)',
 'platform.sw_colleagues(uuid,uuid)',
 'platform.sw_queue(uuid,uuid,text,boolean,integer,integer)',
 'platform.sw_finish(uuid,uuid,uuid)',
 'platform.sw_lease()'
 ] LOOP
 definition:=pg_get_functiondef(signature::regprocedure);
 IF position('now()' IN definition)=0 THEN RAISE EXCEPTION 'unexpected expiry definition %',signature; END IF;
 EXECUTE replace(definition,'now()','clock_timestamp()');
 END LOOP;

 definition:=pg_get_functiondef('platform.sw_target_valid(uuid,uuid,uuid,timestamp with time zone,boolean)'::regprocedure);
 needle:=E'BEGIN\n SELECT * INTO l';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected target declaration'; END IF;
 EXECUTE replace(definition,needle,E'BEGIN\n IF expiry IS NULL OR expiry<=clock_timestamp() THEN RETURN false; END IF;\n SELECT * INTO l');

 definition:=pg_get_functiondef('platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid)'::regprocedure);
 needle:='DECLARE final_result jsonb; final_scenario uuid; final_action text;';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected event declaration'; END IF;
 definition:=replace(definition,needle,needle||' task_deadline timestamptz; new_independent boolean:=false;');
 needle:=' final_result:=platform.sw_event_command_validated(org,lid,operation,payload,expected,command);';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected event invocation'; END IF;
 replacement:=$body$ IF operation='independent-reviews' AND NOT EXISTS(
 SELECT 1 FROM platform.synthetic_workflow_commands c WHERE c.organization_id=org
 AND c.principal_id::text=current_setting('foc.principal',true) AND c.aggregate_id=lid
 AND c.operation=sw_event_command.operation AND c.command=sw_event_command.command) THEN
 new_independent:=true;
 SELECT max(t.expires_at) INTO task_deadline FROM app.synthetic_investigation_tasks t
 WHERE t.organization_id=org AND t.lead_id=lid AND t.target::text=current_setting('foc.principal',true) AND t.state='pending';
 IF task_deadline IS NULL OR task_deadline<=clock_timestamp() THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 END IF;
 final_result:=platform.sw_event_command_validated(org,lid,operation,payload,expected,command);$body$;
 definition:=replace(definition,needle,replacement);
 needle:=' RETURN final_result;';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected event completion'; END IF;
 replacement:=$body$ IF new_independent AND task_deadline<=clock_timestamp() THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN final_result;$body$;
 EXECUTE replace(definition,needle,replacement);

 definition:=pg_get_functiondef('platform.sw_finish(uuid,uuid,uuid)'::regprocedure);
 needle:=E' IF NOT platform.sw_allowed(org,r.scenario_id,''run'') OR NOT platform.sw_current(org,r.scenario_id)\n OR NOT platform.case_permission(org,r.case_id,''case.read'')';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected worker completion'; END IF;
 replacement:=E' IF r.lease_until IS NULL OR r.lease_until<=clock_timestamp() OR NOT platform.sw_allowed(org,r.scenario_id,''run'') OR NOT platform.sw_current(org,r.scenario_id)\n OR NOT platform.case_permission(org,r.case_id,''case.read'')';
 EXECUTE replace(definition,needle,replacement);
END
$migration$;
