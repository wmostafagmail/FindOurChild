-- A global identity sequence could reveal other organizations' audit activity through gaps.
-- Preserve existing events/hashes; allocate future sequence numbers under the existing per-org lock.
ALTER TABLE app.audit_events ALTER COLUMN sequence DROP IDENTITY;
CREATE OR REPLACE FUNCTION platform.audit_append(org uuid, action_name text, target uuid, result text) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,app,public
AS $$
DECLARE prior bytea; previous_sequence bigint; event uuid:=gen_random_uuid(); actor uuid:=nullif(current_setting('foc.principal',true),'')::uuid; stamp timestamptz:=clock_timestamp();
BEGIN
 IF NOT platform.active_member(org,NULL) OR action_name NOT IN ('session.logout','identity.read','membership.grant','membership.revoke','case.permission.allowed','case.permission.denied','audit.read') OR result NOT IN ('allowed','denied') THEN RAISE EXCEPTION 'authorization denied' USING ERRCODE='42501'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(org::text,0));
 SELECT event_hash,sequence INTO prior,previous_sequence FROM app.audit_events WHERE organization_id=org ORDER BY sequence DESC LIMIT 1;
 prior:=coalesce(prior,decode(repeat('00',32),'hex'));
 INSERT INTO app.audit_events(organization_id,sequence,event_id,actor_ref,action,target_ref,purpose,outcome,previous_hash,event_hash,occurred_at)
 VALUES(org,coalesce(previous_sequence,0)+1,event,actor,action_name,target,'identity_security',result,prior,digest(prior||convert_to(jsonb_build_array(event,actor,action_name,target,'identity_security',result,stamp)::text,'UTF8'),'sha256'),stamp);
END $$;
ALTER FUNCTION platform.audit_append(uuid,text,uuid,text) OWNER TO foc_policy;
