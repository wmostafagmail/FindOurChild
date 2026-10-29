-- Synthetic investigation only. No privileges on disabled biometric/custody tables.
CREATE TABLE platform.synthetic_workflow_scenarios (
 organization_id uuid NOT NULL REFERENCES app.organizations(id), id uuid NOT NULL,
 version text NOT NULL CHECK(version='fixture-2d-v1'), instance_id uuid NOT NULL,
 activation_epoch text NOT NULL CHECK(length(activation_epoch)=64),
 manifest jsonb NOT NULL CHECK(jsonb_typeof(manifest)='object'), manifest_digest text NOT NULL,
 expires_at timestamptz NOT NULL, revoked_at timestamptz,
 PRIMARY KEY(organization_id,id), CHECK(manifest_digest=encode(public.digest(manifest::text,'sha256'),'hex'))
);
CREATE TABLE platform.synthetic_workflow_grants (
 organization_id uuid NOT NULL, scenario_id uuid NOT NULL, principal_id uuid NOT NULL REFERENCES app.staff_principals(id),
 person_id uuid NOT NULL, conflict_clear boolean NOT NULL DEFAULT false,
 purpose text NOT NULL CHECK(purpose='synthetic_investigation'),
 actions text[] NOT NULL CHECK(actions<@ARRAY['view','run','cancel','review','collaborate','assign','peer','independent','audit']),
 expires_at timestamptz NOT NULL, revoked_at timestamptz,
 PRIMARY KEY(organization_id,scenario_id,principal_id),
 FOREIGN KEY(organization_id,scenario_id) REFERENCES platform.synthetic_workflow_scenarios(organization_id,id)
);
CREATE TABLE app.synthetic_matching_runs (
 organization_id uuid NOT NULL, id uuid NOT NULL DEFAULT gen_random_uuid(), case_id uuid NOT NULL, scenario_id uuid NOT NULL,
 requested_by uuid NOT NULL REFERENCES app.staff_principals(id), revision bigint NOT NULL DEFAULT 1,
 state text NOT NULL DEFAULT 'queued' CHECK(state IN ('queued','running','completed','held','failed','cancelled')),
 lease_token uuid, lease_until timestamptz, attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5),
 created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,case_id) REFERENCES app.cases(organization_id,id),
 FOREIGN KEY(organization_id,scenario_id) REFERENCES platform.synthetic_workflow_scenarios(organization_id,id)
);
CREATE TABLE app.synthetic_candidate_leads (
 organization_id uuid NOT NULL, id uuid NOT NULL DEFAULT gen_random_uuid(), run_id uuid NOT NULL,
 query_case_id uuid NOT NULL, candidate_case_id uuid NOT NULL, scenario_id uuid NOT NULL,
 internal_rank integer NOT NULL CHECK(internal_rank BETWEEN 1 AND 50), snapshot_hash text NOT NULL,
 revision bigint NOT NULL DEFAULT 1, review_state text NOT NULL DEFAULT 'pending' CHECK(review_state IN ('pending','held','rejected','escalated')),
 investigation_state text NOT NULL DEFAULT 'open' CHECK(investigation_state IN ('open','awaiting_independent_review','returned_for_evidence','workflow_reviewed','closed_without_conclusion')),
 first_person uuid, first_review uuid, peer_target uuid, PRIMARY KEY(organization_id,id),
 UNIQUE(organization_id,run_id,candidate_case_id), CHECK(query_case_id<>candidate_case_id),
 FOREIGN KEY(organization_id,run_id) REFERENCES app.synthetic_matching_runs(organization_id,id),
 FOREIGN KEY(organization_id,query_case_id) REFERENCES app.cases(organization_id,id),
 FOREIGN KEY(organization_id,candidate_case_id) REFERENCES app.cases(organization_id,id),
 FOREIGN KEY(organization_id,scenario_id) REFERENCES platform.synthetic_workflow_scenarios(organization_id,id)
);
CREATE TABLE app.synthetic_investigation_events (
 organization_id uuid NOT NULL, id uuid NOT NULL DEFAULT gen_random_uuid(), lead_id uuid NOT NULL,
 actor uuid NOT NULL REFERENCES app.staff_principals(id), person_id uuid NOT NULL, revision bigint NOT NULL,
 kind text NOT NULL CHECK(kind IN ('reviews','assignments','notes','peer-review-requests','independent-reviews')),
 payload jsonb NOT NULL, snapshot_hash text NOT NULL, occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 previous_hash text NOT NULL, event_hash text NOT NULL, PRIMARY KEY(organization_id,id), UNIQUE(organization_id,lead_id,revision),
 FOREIGN KEY(organization_id,lead_id) REFERENCES app.synthetic_candidate_leads(organization_id,id)
);
CREATE TABLE app.synthetic_investigation_tasks (
 organization_id uuid NOT NULL, id uuid NOT NULL DEFAULT gen_random_uuid(), lead_id uuid NOT NULL, event_id uuid NOT NULL,
 target uuid NOT NULL REFERENCES app.staff_principals(id), expires_at timestamptz NOT NULL,
 state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','completed','cancelled')),
 PRIMARY KEY(organization_id,id), FOREIGN KEY(organization_id,lead_id) REFERENCES app.synthetic_candidate_leads(organization_id,id),
 FOREIGN KEY(organization_id,event_id) REFERENCES app.synthetic_investigation_events(organization_id,id)
);
CREATE TABLE app.synthetic_investigation_assignments (
 organization_id uuid NOT NULL, id uuid NOT NULL DEFAULT gen_random_uuid(), task_id uuid NOT NULL, principal_id uuid NOT NULL REFERENCES app.staff_principals(id),
 event_id uuid NOT NULL, expires_at timestamptz NOT NULL, PRIMARY KEY(organization_id,id),
 FOREIGN KEY(organization_id,task_id) REFERENCES app.synthetic_investigation_tasks(organization_id,id),
 FOREIGN KEY(organization_id,event_id) REFERENCES app.synthetic_investigation_events(organization_id,id)
);
CREATE TABLE platform.synthetic_workflow_commands (
 organization_id uuid NOT NULL, principal_id uuid NOT NULL, aggregate_id uuid NOT NULL, operation text NOT NULL, command uuid NOT NULL,
 body_digest text NOT NULL, result jsonb NOT NULL, PRIMARY KEY(organization_id,principal_id,aggregate_id,operation,command)
);
DO $$ DECLARE t text; ns text; BEGIN
 FOREACH ns IN ARRAY ARRAY['app','platform'] LOOP
 FOR t IN SELECT tablename FROM pg_tables WHERE schemaname=ns AND tablename LIKE 'synthetic_%' LOOP
 EXECUTE format('ALTER TABLE %I.%I OWNER TO foc_owner',ns,t);
 EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY',ns,t);
 EXECUTE format('ALTER TABLE %I.%I FORCE ROW LEVEL SECURITY',ns,t);
 EXECUTE format('GRANT SELECT,INSERT ON %I.%I TO foc_policy',ns,t);
 IF t<>'synthetic_investigation_events' THEN EXECUTE format('GRANT UPDATE ON %I.%I TO foc_policy',ns,t); END IF;
 EXECUTE format('CREATE POLICY synthetic_internal ON %I.%I TO foc_policy USING(true) WITH CHECK(true)',ns,t);
 END LOOP; END LOOP;
END $$;

CREATE FUNCTION platform.sw_allowed(org uuid,sid uuid,action_name text) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
 SELECT current_database()='foc_synthetic' AND current_setting('foc.purpose',true)='case_management'
 AND platform.active_member(org,NULL) AND EXISTS(
 SELECT 1 FROM platform.synthetic_workflow_scenarios s JOIN platform.environment e ON e.instance_id=s.instance_id
 JOIN platform.synthetic_workflow_grants g ON g.organization_id=s.organization_id AND g.scenario_id=s.id
 WHERE s.organization_id=org AND s.id=sid AND s.revoked_at IS NULL AND s.expires_at>now()
 AND s.activation_epoch=current_setting('foc.workflow_epoch',true) AND e.data_class='synthetic'
 AND g.principal_id::text=current_setting('foc.principal',true) AND g.purpose='synthetic_investigation'
 AND action_name=ANY(g.actions) AND g.revoked_at IS NULL AND g.expires_at>now())
$$;
CREATE FUNCTION platform.sw_current(org uuid,sid uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform,app,public AS $$
 SELECT EXISTS(SELECT 1 FROM platform.synthetic_workflow_scenarios s WHERE s.organization_id=org AND s.id=sid
 AND s.manifest_digest=encode(digest(s.manifest::text,'sha256'),'hex')
 AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(s.manifest->'cases') item LEFT JOIN app.cases c ON c.organization_id=org AND c.id=(item->>'id')::uuid
 WHERE c.id IS NULL OR c.revision<>(item->>'revision')::bigint OR c.deletion_generation<>(item->>'generation')::bigint
 OR c.registry<>item->>'registry' OR c.deleted_at IS NOT NULL OR c.lifecycle IN ('closed','deleted')
 OR encode(digest(coalesce((SELECT string_agg(v.id::text||v.body_ciphertext,'' ORDER BY v.id) FROM platform.report_versions v WHERE v.organization_id=org AND v.case_id=c.id),''),'sha256'),'hex')<>item->>'claims_digest')
 AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(s.manifest->'photos') p LEFT JOIN app.objects o ON o.organization_id=org AND o.id=(p->>'id')::uuid
 LEFT JOIN platform.upload_metadata u ON u.organization_id=o.organization_id AND u.derivative_key=o.opaque_key
 WHERE o.id IS NULL OR o.case_id<>(p->>'case_id')::uuid OR o.bucket_class<>'derivative' OR o.scan_status<>'clean'
 OR encode(o.content_sha256,'hex')<>p->>'sha256' OR o.object_version<>p->>'object_version'
 OR u.scan_engine<>'ClamAV 1.5.4' OR u.scan_signature IS NULL OR u.intent_id IS NULL)
 )
$$;
CREATE FUNCTION platform.sw_pair(org uuid,lid uuid,permission_name text DEFAULT 'case.read') RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
 SELECT EXISTS(SELECT 1 FROM app.synthetic_candidate_leads l JOIN app.synthetic_matching_runs r ON r.organization_id=l.organization_id AND r.id=l.run_id
 WHERE l.organization_id=org AND l.id=lid AND r.state='completed' AND platform.sw_allowed(org,l.scenario_id,'view')
 AND platform.sw_current(org,l.scenario_id) AND platform.case_permission(org,l.query_case_id,permission_name)
 AND platform.case_permission(org,l.candidate_case_id,permission_name))
$$;
CREATE POLICY synthetic_run_read ON app.synthetic_matching_runs FOR SELECT TO foc_api USING(platform.sw_allowed(organization_id,scenario_id,'view') AND platform.case_permission(organization_id,case_id,'case.read'));
CREATE POLICY synthetic_lead_read ON app.synthetic_candidate_leads FOR SELECT TO foc_api USING(platform.sw_pair(organization_id,id));
CREATE POLICY synthetic_event_read ON app.synthetic_investigation_events FOR SELECT TO foc_api USING(platform.sw_pair(organization_id,lead_id));
CREATE POLICY synthetic_task_read ON app.synthetic_investigation_tasks FOR SELECT TO foc_api USING(platform.sw_pair(organization_id,lead_id));
CREATE POLICY synthetic_assignment_read ON app.synthetic_investigation_assignments FOR SELECT TO foc_api USING(EXISTS(SELECT 1 FROM app.synthetic_investigation_tasks t WHERE t.organization_id=synthetic_investigation_assignments.organization_id AND t.id=task_id));
GRANT SELECT ON app.synthetic_matching_runs,app.synthetic_candidate_leads,app.synthetic_investigation_events,app.synthetic_investigation_tasks,app.synthetic_investigation_assignments TO foc_api;
CREATE INDEX synthetic_queue ON app.synthetic_candidate_leads(organization_id,query_case_id,run_id,internal_rank,id);
CREATE INDEX synthetic_history ON app.synthetic_investigation_events(organization_id,lead_id,revision);
ALTER TABLE app.outbox_events DROP CONSTRAINT closed_event_type;
ALTER TABLE app.outbox_events ADD CONSTRAINT closed_event_type CHECK(type IN ('report.submitted','media.uploaded','media.ready','media.quarantined','subject.selected','embedding.ready','matching.requested','matching.completed','lead.reviewed','disclosure.approved','approval.revoked','reunification.recorded','deletion.requested','deletion.completed','notification.requested','synthetic.workflow.requested','synthetic.workflow.changed'));
ALTER TABLE app.synthetic_investigation_events ADD UNIQUE(organization_id,lead_id,id);
ALTER TABLE app.synthetic_investigation_tasks ADD FOREIGN KEY(organization_id,lead_id,event_id) REFERENCES app.synthetic_investigation_events(organization_id,lead_id,id);
ALTER TABLE app.synthetic_investigation_tasks ADD UNIQUE(organization_id,id,event_id);
ALTER TABLE app.synthetic_investigation_assignments ADD FOREIGN KEY(organization_id,task_id,event_id) REFERENCES app.synthetic_investigation_tasks(organization_id,id,event_id);
ALTER TABLE app.synthetic_candidate_leads ADD FOREIGN KEY(organization_id,id,first_review) REFERENCES app.synthetic_investigation_events(organization_id,lead_id,id) DEFERRABLE INITIALLY DEFERRED;

CREATE FUNCTION platform.sw_status(org uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb;
BEGIN
 SELECT jsonb_agg(jsonb_build_object('id',s.id,'version',s.version,'query_case_id',s.manifest->>'query_case_id','case_revision',s.manifest->>'query_revision')) INTO result
 FROM platform.synthetic_workflow_scenarios s WHERE s.organization_id=org AND platform.sw_allowed(org,s.id,'view') AND platform.sw_current(org,s.id)
 AND platform.case_permission(org,(s.manifest->>'query_case_id')::uuid,'case.read');
 IF result IS NULL THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 PERFORM platform.reporting_audit(org,nullif(current_setting('foc.principal',true),'')::uuid,'synthetic.status',org);
 RETURN jsonb_build_object('data_class','synthetic','provider','fixture-scenario-v1','operational_activation',false,'scenarios',result);
END $$;
CREATE FUNCTION platform.sw_read(org uuid,lid uuid,view_name text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE l app.synthetic_candidate_leads; s platform.synthetic_workflow_scenarios; result jsonb;
BEGIN
 IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 SELECT * INTO l FROM app.synthetic_candidate_leads WHERE organization_id=org AND id=lid;
 SELECT * INTO s FROM platform.synthetic_workflow_scenarios WHERE organization_id=org AND id=l.scenario_id;
 IF view_name='audit' AND (NOT platform.sw_allowed(org,l.scenario_id,'audit') OR NOT platform.sw_pair(org,lid,'audit.read')) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF view_name NOT IN ('comparison','investigation','audit') THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 PERFORM platform.reporting_audit(org,nullif(current_setting('foc.principal',true),'')::uuid,'synthetic.'||view_name,lid);
 result:=jsonb_build_object('lead_id',l.id,'revision',l.revision,'snapshot_hash',l.snapshot_hash,'data_class','synthetic','identity_determination','not_performed','review_state',l.review_state,'investigation_state',l.investigation_state,'usability','current');
 IF view_name='comparison' THEN
 RETURN result||jsonb_build_object('query_case_id',l.query_case_id,'candidate_case_id',l.candidate_case_id,
 'result_source',s.manifest->'result_source','explanations',s.manifest->'explanations',
 'photos',coalesce((SELECT jsonb_agg(p-'object_version'-'sha256') FROM jsonb_array_elements(s.manifest->'photos') p WHERE (p->>'case_id')::uuid IN (l.query_case_id,l.candidate_case_id) AND platform.case_permission(org,(p->>'case_id')::uuid,'media.read')),'[]'::jsonb));
 END IF;
 -- Bounded immutable history, paginated by the API's authenticated cursor.
 RETURN result;
END $$;

CREATE FUNCTION platform.sw_run_command(org uuid,cid uuid,operation text,payload jsonb,expected bigint,command uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app,public AS $$
DECLARE actor uuid:=nullif(current_setting('foc.principal',true),'')::uuid; s platform.synthetic_workflow_scenarios; r app.synthetic_matching_runs; previous platform.synthetic_workflow_commands; result jsonb; body_hash text:=encode(digest(payload::text||expected::text,'sha256'),'hex'); aggregate uuid:=cid;
BEGIN
 IF operation='runs' THEN
 SELECT * INTO s FROM platform.synthetic_workflow_scenarios WHERE organization_id=org AND id=(payload->>'scenario_id')::uuid;
 IF NOT FOUND OR s.manifest->>'query_case_id'<>cid::text OR NOT platform.sw_allowed(org,s.id,'run') OR NOT platform.sw_current(org,s.id)
 OR NOT platform.case_permission(org,cid,'case.read') OR NOT platform.case_permission(org,cid,'case.write') OR NOT platform.case_permission(org,cid,'matching.request') THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF payload<>jsonb_build_object('scenario_id',s.id,'scenario_version',s.version) THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 ELSE
 SELECT * INTO r FROM app.synthetic_matching_runs WHERE organization_id=org AND id=cid;
 IF NOT FOUND OR operation<>'cancellations' OR NOT platform.sw_allowed(org,r.scenario_id,'cancel') OR NOT platform.case_permission(org,r.case_id,'case.write') OR NOT platform.case_permission(org,r.case_id,'case.read') OR (r.requested_by<>actor AND NOT platform.active_member(org,'supervisor')) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 IF payload<>'{}'::jsonb THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(org::text||actor::text||aggregate::text||operation||command::text,41));
 SELECT * INTO previous FROM platform.synthetic_workflow_commands c WHERE c.organization_id=org AND c.principal_id=actor AND c.aggregate_id=aggregate AND c.operation=sw_run_command.operation AND c.command=sw_run_command.command;
 IF FOUND THEN IF previous.body_digest<>body_hash THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN previous.result; END IF;
 IF NOT platform.intake_limit(digest('sw:'||org::text||actor::text,'sha256'),100) THEN RAISE EXCEPTION 'rate' USING ERRCODE='P0429'; END IF;
 IF operation='runs' THEN
 PERFORM 1 FROM app.cases WHERE organization_id=org AND id=cid AND revision=expected FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'stale' USING ERRCODE='P0412'; END IF;
 INSERT INTO app.synthetic_matching_runs(organization_id,case_id,scenario_id,requested_by) VALUES(org,cid,s.id,actor) RETURNING * INTO r;
 ELSE
 SELECT * INTO r FROM app.synthetic_matching_runs WHERE organization_id=org AND id=cid FOR UPDATE;
 IF r.revision<>expected THEN RAISE EXCEPTION 'stale' USING ERRCODE='P0412'; END IF;
 IF r.state NOT IN ('queued','running') THEN RAISE EXCEPTION 'state' USING ERRCODE='P0409'; END IF;
 UPDATE app.synthetic_matching_runs SET state='cancelled',revision=revision+1,lease_token=NULL,lease_until=NULL WHERE organization_id=org AND id=cid RETURNING * INTO r;
 END IF;
 PERFORM platform.reporting_audit(org,actor,'synthetic.'||operation,r.id);
 PERFORM platform.reporting_event(org,r.case_id,'synthetic.workflow.requested',r.id);
 result:=jsonb_build_object('id',r.id,'revision',r.revision,'state',r.state);
 INSERT INTO platform.synthetic_workflow_commands VALUES(org,actor,aggregate,operation,command,body_hash,result);
 RETURN result;
END $$;

CREATE FUNCTION platform.sw_event_command(org uuid,lid uuid,operation text,payload jsonb,expected bigint,command uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app,public AS $$
DECLARE actor uuid:=nullif(current_setting('foc.principal',true),'')::uuid; l app.synthetic_candidate_leads; g platform.synthetic_workflow_grants; target_grant platform.synthetic_workflow_grants; prior platform.synthetic_workflow_commands; action_name text; result jsonb; body_hash text:=encode(digest(payload::text||expected::text,'sha256'),'hex'); eid uuid:=gen_random_uuid(); tid uuid:=gen_random_uuid(); previous_hash text; stamp timestamptz:=clock_timestamp(); ref text; expiry timestamptz; target uuid;
BEGIN
 IF NOT platform.sw_pair(org,lid) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 SELECT * INTO l FROM app.synthetic_candidate_leads WHERE organization_id=org AND id=lid;
 -- Canonical case lock order, followed by aggregate and idempotency locks.
 PERFORM 1 FROM app.cases WHERE organization_id=org AND id IN (l.query_case_id,l.candidate_case_id) ORDER BY id FOR UPDATE;
 SELECT * INTO l FROM app.synthetic_candidate_leads WHERE organization_id=org AND id=lid FOR UPDATE;
 action_name:=CASE operation WHEN 'reviews' THEN 'review' WHEN 'notes' THEN 'collaborate' WHEN 'assignments' THEN 'assign' WHEN 'peer-review-requests' THEN 'peer' WHEN 'independent-reviews' THEN 'independent' END;
 IF action_name IS NULL OR NOT platform.sw_allowed(org,l.scenario_id,action_name) OR NOT platform.sw_pair(org,lid,'case.write') THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 SELECT * INTO g FROM platform.synthetic_workflow_grants WHERE organization_id=org AND scenario_id=l.scenario_id AND principal_id=actor;
 IF NOT g.conflict_clear THEN RAISE EXCEPTION 'conflict unknown' USING ERRCODE='42501'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(org::text||actor::text||lid::text||operation||command::text,41));
 SELECT * INTO prior FROM platform.synthetic_workflow_commands c WHERE c.organization_id=org AND c.principal_id=actor AND c.aggregate_id=lid AND c.operation=sw_event_command.operation AND c.command=sw_event_command.command;
 IF FOUND THEN IF prior.body_digest<>body_hash THEN RAISE EXCEPTION 'conflict' USING ERRCODE='23505'; END IF; RETURN prior.result; END IF;
 IF l.revision<>expected OR payload->>'snapshot_hash' IS DISTINCT FROM l.snapshot_hash THEN RAISE EXCEPTION 'stale' USING ERRCODE='P0412'; END IF;
 IF payload->'uncertainty_acknowledged' IS DISTINCT FROM 'true'::jsonb OR jsonb_typeof(payload->'rationale_codes')<>'array' OR jsonb_array_length(payload->'rationale_codes') NOT BETWEEN 1 AND 5 OR jsonb_typeof(payload->'evidence_refs')<>'array' OR jsonb_array_length(payload->'evidence_refs')>20 THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 IF EXISTS(SELECT 1 FROM jsonb_object_keys(payload) k WHERE k NOT IN ('snapshot_hash','uncertainty_acknowledged','rationale_codes','evidence_refs','outcome','principal_id','expires_at','first_review_id')) THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 IF (operation='notes' AND (payload ? 'outcome' OR payload ? 'principal_id' OR payload ? 'expires_at' OR payload ? 'first_review_id'))
 OR (operation='reviews' AND (payload ? 'principal_id' OR payload ? 'expires_at' OR payload ? 'first_review_id'))
 OR (operation IN ('assignments','peer-review-requests') AND (payload ? 'outcome' OR payload ? 'first_review_id'))
 OR (operation='independent-reviews' AND (payload ? 'principal_id' OR payload ? 'expires_at')) THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 FOR ref IN SELECT jsonb_array_elements_text(payload->'rationale_codes') LOOP
 IF ref NOT IN ('INSUFFICIENT_AUTHORIZED_EVIDENCE','SUPPORTING_FIXTURE_CLAIM','CONTRADICTORY_FIXTURE_CLAIM','REQUEST_EVIDENCE','RECUSE_CONFLICT','SYNTHETIC_WORKFLOW_ONLY') THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 END LOOP;
 FOR ref IN SELECT jsonb_array_elements_text(payload->'evidence_refs') LOOP
 IF NOT EXISTS(SELECT 1 FROM platform.synthetic_workflow_scenarios s CROSS JOIN jsonb_array_elements(s.manifest->'explanations') e WHERE s.organization_id=org AND s.id=l.scenario_id AND e->>'source_ref'=ref AND (e->>'case_id')::uuid IN (l.query_case_id,l.candidate_case_id)) THEN RAISE EXCEPTION 'invalid evidence' USING ERRCODE='P0422'; END IF;
 END LOOP;
 IF operation='reviews' THEN
 IF payload->>'outcome' NOT IN ('hold','reject','escalate') OR (payload->>'outcome'<>'hold' AND jsonb_array_length(payload->'evidence_refs')=0) THEN RAISE EXCEPTION 'invalid' USING ERRCODE='P0422'; END IF;
 UPDATE app.synthetic_candidate_leads SET review_state=CASE payload->>'outcome' WHEN 'hold' THEN 'held' WHEN 'reject' THEN 'rejected' ELSE 'escalated' END,investigation_state='open',first_person=g.person_id,first_review=eid,peer_target=NULL WHERE organization_id=org AND id=lid;
 UPDATE app.synthetic_investigation_tasks SET state='cancelled' WHERE organization_id=org AND lead_id=lid AND state='pending';
 ELSIF operation IN ('assignments','peer-review-requests') THEN
 target:=(payload->>'principal_id')::uuid; expiry:=(payload->>'expires_at')::timestamptz;
 SELECT * INTO target_grant FROM platform.synthetic_workflow_grants WHERE organization_id=org AND scenario_id=l.scenario_id AND principal_id=target AND revoked_at IS NULL AND expires_at>=expiry AND conflict_clear AND 'view'=ANY(actions);
 IF NOT FOUND OR expiry<=now() OR expiry>now()+interval '1 hour' OR (operation='assignments' AND NOT platform.active_member(org,'supervisor')) THEN RAISE EXCEPTION 'not authorized' USING ERRCODE='42501'; END IF;
 PERFORM set_config('foc.principal',target::text,true);
 IF NOT platform.sw_pair(org,lid,'case.read') OR NOT platform.active_member(org,NULL) OR EXISTS(SELECT 1 FROM app.case_grants c WHERE c.organization_id=org AND c.case_id IN (l.query_case_id,l.candidate_case_id) AND c.principal_id=target AND c.permission IN ('case.read','case.write') AND c.expires_at<expiry) THEN RAISE EXCEPTION 'not authorized' USING ERRCODE='42501'; END IF;
 PERFORM set_config('foc.principal',actor::text,true);
 IF operation='peer-review-requests' THEN
 IF l.review_state<>'escalated' OR l.first_review IS NULL OR target_grant.person_id=l.first_person OR NOT 'independent'=ANY(target_grant.actions) THEN RAISE EXCEPTION 'independence denied' USING ERRCODE='42501'; END IF;
 UPDATE app.synthetic_candidate_leads SET investigation_state='awaiting_independent_review',peer_target=target WHERE organization_id=org AND id=lid;
 END IF;
 ELSIF operation='independent-reviews' THEN
 IF l.investigation_state<>'awaiting_independent_review' OR l.peer_target<>actor OR l.first_person=g.person_id OR payload->>'first_review_id' IS DISTINCT FROM l.first_review::text
 OR NOT EXISTS(SELECT 1 FROM app.synthetic_investigation_tasks t WHERE t.organization_id=org AND t.lead_id=lid AND t.target=actor AND t.state='pending' AND t.expires_at>now())
 OR payload->>'outcome' NOT IN ('return_for_evidence','disagree','recuse','workflow_review_complete') OR NOT platform.active_member(org,'safeguarding') THEN RAISE EXCEPTION 'independence denied' USING ERRCODE='42501'; END IF;
 UPDATE app.synthetic_candidate_leads SET investigation_state=CASE WHEN payload->>'outcome'='workflow_review_complete' THEN 'workflow_reviewed' ELSE 'returned_for_evidence' END WHERE organization_id=org AND id=lid;
 UPDATE app.synthetic_investigation_tasks SET state='completed' WHERE organization_id=org AND lead_id=lid AND state='pending';
 END IF;
 SELECT e.event_hash INTO previous_hash FROM app.synthetic_investigation_events e WHERE organization_id=org AND lead_id=lid ORDER BY revision DESC LIMIT 1;
 previous_hash:=coalesce(previous_hash,repeat('0',64));
 INSERT INTO app.synthetic_investigation_events VALUES(org,eid,lid,actor,g.person_id,l.revision+1,operation,payload,l.snapshot_hash,stamp,previous_hash,encode(digest(previous_hash||jsonb_build_array(eid,actor,g.person_id,l.revision+1,operation,payload,l.snapshot_hash,stamp)::text,'sha256'),'hex'));
 IF operation IN ('assignments','peer-review-requests') THEN
 INSERT INTO app.synthetic_investigation_tasks VALUES(org,tid,lid,eid,target,expiry,'pending');
 INSERT INTO app.synthetic_investigation_assignments(organization_id,task_id,principal_id,event_id,expires_at) VALUES(org,tid,target,eid,expiry);
 END IF;
 UPDATE app.synthetic_candidate_leads SET revision=revision+1 WHERE organization_id=org AND id=lid;
 PERFORM platform.reporting_audit(org,actor,'synthetic.'||operation,lid);
 PERFORM platform.reporting_event(org,l.query_case_id,'synthetic.workflow.changed',eid);
 result:=jsonb_build_object('id',eid,'revision',l.revision+1);
 INSERT INTO platform.synthetic_workflow_commands VALUES(org,actor,lid,operation,command,body_hash,result);
 RETURN result;
END $$;

-- The actual worker leases only closed fixture scenarios; no result JSON/model input is accepted.
CREATE FUNCTION platform.sw_lease() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE r app.synthetic_matching_runs;
BEGIN
 UPDATE app.synthetic_matching_runs SET state='failed',lease_token=NULL WHERE state='running' AND lease_until<now() AND attempts>=5;
 SELECT * INTO r FROM app.synthetic_matching_runs WHERE (state='queued' OR (state='running' AND lease_until<now())) AND attempts<5 ORDER BY created_at,id LIMIT 1 FOR UPDATE SKIP LOCKED;
 IF NOT FOUND THEN RETURN NULL; END IF;
 UPDATE app.synthetic_matching_runs SET state='running',lease_token=gen_random_uuid(),lease_until=now()+interval '30 seconds',attempts=attempts+1,revision=revision+1 WHERE organization_id=r.organization_id AND id=r.id RETURNING * INTO r;
 RETURN jsonb_build_object('id',r.id,'organization_id',r.organization_id,'token',r.lease_token);
END $$;
CREATE FUNCTION platform.sw_finish(org uuid,rid uuid,token uuid) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app,public AS $$
DECLARE r app.synthetic_matching_runs; s platform.synthetic_workflow_scenarios; item jsonb; candidate uuid; rank_value integer:=0; snapshot text;
BEGIN
 SELECT * INTO r FROM app.synthetic_matching_runs WHERE organization_id=org AND id=rid FOR UPDATE;
 IF NOT FOUND OR r.state<>'running' OR r.lease_token IS DISTINCT FROM token OR r.lease_until<=now() THEN RETURN false; END IF;
 PERFORM set_config('foc.principal',r.requested_by::text,true); PERFORM set_config('foc.organization',org::text,true); PERFORM set_config('foc.purpose','case_management',true);
 SELECT * INTO s FROM platform.synthetic_workflow_scenarios WHERE organization_id=org AND id=r.scenario_id;
 PERFORM 1 FROM app.cases c WHERE c.organization_id=org AND c.id IN (SELECT (v->>'id')::uuid FROM jsonb_array_elements(s.manifest->'cases') v) ORDER BY c.id FOR UPDATE;
 IF NOT platform.sw_allowed(org,r.scenario_id,'run') OR NOT platform.sw_current(org,r.scenario_id) OR NOT platform.case_permission(org,r.case_id,'case.write') OR NOT platform.case_permission(org,r.case_id,'matching.request') THEN
 UPDATE app.synthetic_matching_runs SET state='held',revision=revision+1,lease_token=NULL WHERE organization_id=org AND id=rid; RETURN false; END IF;
 IF jsonb_array_length(s.manifest->'candidates')>50 OR s.manifest->>'provider' IS DISTINCT FROM 'fixture-scenario-v1' THEN
 UPDATE app.synthetic_matching_runs SET state='failed',revision=revision+1,lease_token=NULL WHERE organization_id=org AND id=rid; RETURN false; END IF;
 FOR item IN SELECT value FROM jsonb_array_elements(s.manifest->'candidates') LOOP
 candidate:=(item->>'case_id')::uuid; rank_value:=rank_value+1;
 IF NOT EXISTS(SELECT 1 FROM app.cases q JOIN app.cases c ON c.organization_id=q.organization_id AND c.registry<>q.registry WHERE q.organization_id=org AND q.id=r.case_id AND c.id=candidate)
 OR NOT EXISTS(SELECT 1 FROM jsonb_array_elements(s.manifest->'cases') v WHERE v->>'id'=candidate::text) THEN RAISE EXCEPTION 'invalid fixture' USING ERRCODE='P0422'; END IF;
 snapshot:=encode(digest(s.manifest_digest||r.case_id::text||candidate::text||s.activation_epoch,'sha256'),'hex');
 INSERT INTO app.synthetic_candidate_leads(organization_id,run_id,query_case_id,candidate_case_id,scenario_id,internal_rank,snapshot_hash) VALUES(org,rid,r.case_id,candidate,s.id,rank_value,snapshot);
 END LOOP;
 UPDATE app.synthetic_matching_runs SET state='completed',revision=revision+1,lease_token=NULL,lease_until=NULL WHERE organization_id=org AND id=rid;
 PERFORM platform.reporting_audit(org,r.requested_by,'synthetic.completed',rid);
 RETURN true;
END $$;
DO $$ DECLARE f record; BEGIN
 FOR f IN SELECT p.proname,p.oid::regprocedure signature FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='platform' AND p.proname LIKE 'sw_%' LOOP
 EXECUTE format('ALTER FUNCTION %s OWNER TO foc_policy',f.signature);
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.signature);
 IF f.proname IN ('sw_lease','sw_finish') THEN EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_worker',f.signature);
 ELSE EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO foc_api',f.signature); END IF;
 END LOOP;
END $$;
