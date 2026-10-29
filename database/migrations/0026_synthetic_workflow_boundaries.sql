-- Additional paired references, eligible colleagues and neutral recipient fencing.
ALTER TABLE app.synthetic_matching_runs ADD UNIQUE(organization_id,id,case_id,scenario_id);
ALTER TABLE app.synthetic_candidate_leads ADD FOREIGN KEY(organization_id,run_id,query_case_id,scenario_id) REFERENCES app.synthetic_matching_runs(organization_id,id,case_id,scenario_id);

CREATE FUNCTION platform.sw_target_valid(org uuid,lid uuid,target uuid,expiry timestamptz,independent boolean) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE actor text:=current_setting('foc.principal',true); l app.synthetic_candidate_leads; valid boolean;
BEGIN
 SELECT * INTO l FROM app.synthetic_candidate_leads WHERE organization_id=org AND id=lid;
 PERFORM set_config('foc.principal',target::text,true);
 valid:=platform.sw_pair(org,lid,'case.read') AND (NOT independent OR platform.sw_pair(org,lid,'case.write'))
 AND EXISTS(SELECT 1 FROM platform.synthetic_workflow_grants g WHERE g.organization_id=org AND g.scenario_id=l.scenario_id AND g.principal_id=target AND g.expires_at>=expiry AND g.revoked_at IS NULL AND g.conflict_clear AND (NOT independent OR ('independent'=ANY(g.actions) AND g.person_id IS DISTINCT FROM l.first_person)))
 AND EXISTS(SELECT 1 FROM app.memberships m WHERE m.organization_id=org AND m.principal_id=target AND m.starts_at<=now() AND m.expires_at>=expiry AND m.revoked_at IS NULL AND (NOT independent OR m.role='safeguarding'))
 AND NOT EXISTS(SELECT 1 FROM unnest(ARRAY[l.query_case_id,l.candidate_case_id]) cid WHERE NOT EXISTS(SELECT 1 FROM app.case_grants g WHERE g.organization_id=org AND g.case_id=cid AND g.principal_id=target AND g.permission='case.read' AND g.purpose='case_management' AND g.revoked_at IS NULL AND g.expires_at>=expiry));
 PERFORM set_config('foc.principal',coalesce(actor,''),true); RETURN coalesce(valid,false);
END $$;
ALTER FUNCTION platform.sw_event_command(uuid,uuid,text,jsonb,bigint,uuid) RENAME TO sw_event_command_base;
REVOKE EXECUTE ON FUNCTION platform.sw_event_command_base(uuid,uuid,text,jsonb,bigint,uuid) FROM foc_api;
CREATE FUNCTION platform.sw_event_command(org uuid,lid uuid,operation text,payload jsonb,expected bigint,command uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF operation IN ('assignments','peer-review-requests') AND NOT platform.sw_target_valid(org,lid,(payload->>'principal_id')::uuid,(payload->>'expires_at')::timestamptz,operation='peer-review-requests') THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN platform.sw_event_command_base(org,lid,operation,payload,expected,command);
END $$;
CREATE FUNCTION platform.sw_colleagues(org uuid,sid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE actor text:=current_setting('foc.principal',true); s platform.synthetic_workflow_scenarios; g record; result jsonb:='[]';
BEGIN
 IF NOT platform.sw_allowed(org,sid,'view') THEN RETURN '[]'::jsonb; END IF;
 SELECT * INTO s FROM platform.synthetic_workflow_scenarios WHERE organization_id=org AND id=sid;
 FOR g IN SELECT principal_id FROM platform.synthetic_workflow_grants WHERE organization_id=org AND scenario_id=sid AND expires_at>now() AND revoked_at IS NULL LOOP
 PERFORM set_config('foc.principal',g.principal_id::text,true);
 IF platform.sw_allowed(org,sid,'view') AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(s.manifest->'cases') c WHERE NOT platform.case_permission(org,(c->>'id')::uuid,'case.read')) THEN
 result:=result||jsonb_build_array(jsonb_build_object('id',g.principal_id,'role',CASE WHEN platform.active_member(org,'safeguarding') THEN 'safeguarding' ELSE 'reviewer' END));
 END IF;
 END LOOP;
 PERFORM set_config('foc.principal',coalesce(actor,''),true); RETURN result;
END $$;
CREATE FUNCTION platform.sw_recipient(org uuid,aggregate uuid,kind text,target uuid) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE actor text:=current_setting('foc.principal',true); lid uuid; sid uuid; query uuid; valid boolean:=false;
BEGIN
 PERFORM set_config('foc.principal',target::text,true); PERFORM set_config('foc.organization',org::text,true); PERFORM set_config('foc.purpose','case_management',true);
 IF kind='synthetic.workflow.changed' THEN
 SELECT e.lead_id INTO lid FROM app.synthetic_investigation_events e WHERE e.organization_id=org AND e.id=aggregate AND (e.actor=target OR e.payload->>'principal_id'=target::text);
 valid:=lid IS NOT NULL AND platform.sw_pair(org,lid);
 ELSIF kind='synthetic.workflow.requested' THEN
 SELECT scenario_id,case_id INTO sid,query FROM app.synthetic_matching_runs WHERE organization_id=org AND id=aggregate AND requested_by=target;
 valid:=sid IS NOT NULL AND platform.sw_allowed(org,sid,'view') AND platform.sw_current(org,sid) AND platform.case_permission(org,query,'case.read');
 END IF;
 PERFORM set_config('foc.principal',coalesce(actor,''),true); RETURN coalesce(valid,false);
END $$;
ALTER FUNCTION platform.outbox_next() RENAME TO outbox_next_1c;
REVOKE EXECUTE ON FUNCTION platform.outbox_next_1c() FROM foc_worker;
CREATE FUNCTION platform.outbox_next() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb; e app.outbox_events; recipients jsonb;
BEGIN
 result:=platform.outbox_next_1c();
 IF result IS NULL OR result ? 'cancelled' THEN RETURN result; END IF;
 SELECT * INTO e FROM app.outbox_events WHERE id=(result->>'event_id')::uuid;
 IF e.type LIKE 'synthetic.%' THEN
 SELECT coalesce(jsonb_agg(v),'[]'::jsonb) INTO recipients FROM jsonb_array_elements_text(result->'recipients') v WHERE platform.sw_recipient(e.organization_id,e.aggregate_id,e.type,v::uuid);
 result:=result||jsonb_build_object('recipients',recipients,'synthetic_workflow',true);
 END IF;
 RETURN result;
END $$;
ALTER FUNCTION platform.outbox_recipient_current(uuid,uuid,integer) RENAME TO outbox_recipient_current_1c;
REVOKE EXECUTE ON FUNCTION platform.outbox_recipient_current_1c(uuid,uuid,integer) FROM foc_worker;
CREATE FUNCTION platform.outbox_recipient_current(event uuid,recipient uuid,attempt integer) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
 SELECT platform.outbox_recipient_current_1c(event,recipient,attempt) AND EXISTS(SELECT 1 FROM app.outbox_events e WHERE e.id=event AND (e.type NOT LIKE 'synthetic.%' OR platform.sw_recipient(e.organization_id,e.aggregate_id,e.type,recipient)))
$$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.proname,p.oid::regprocedure signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname IN ('sw_target_valid','sw_event_command','sw_colleagues','sw_recipient','outbox_next','outbox_recipient_current') LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature); EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature);
 IF f.proname IN ('sw_event_command','sw_colleagues') THEN EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_api',f.signature);
 ELSIF f.proname IN ('outbox_next','outbox_recipient_current') THEN EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_worker',f.signature); END IF;
 END LOOP;
END $$;
