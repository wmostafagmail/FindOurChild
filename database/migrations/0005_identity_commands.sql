-- Identity administration idempotency is principal/org scoped, independent of child cases.
CREATE TABLE platform.identity_commands (
 organization_id uuid NOT NULL REFERENCES app.organizations(id),
 principal_id uuid NOT NULL REFERENCES app.staff_principals(id),
 command_id uuid NOT NULL,
 body_hash bytea NOT NULL CHECK(octet_length(body_hash)=32),
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(organization_id,principal_id,command_id)
);
ALTER TABLE platform.identity_commands OWNER TO foc_owner;
ALTER TABLE platform.identity_commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.identity_commands FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON platform.identity_commands TO foc_policy;
CREATE POLICY identity_commands_policy ON platform.identity_commands TO foc_policy USING(true) WITH CHECK(true);
CREATE FUNCTION platform.membership_command(org uuid,target uuid,desired_role text,expiry timestamptz,revoke boolean,command uuid) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app,public
AS $$
DECLARE actor uuid:=nullif(current_setting('foc.principal',true),'')::uuid; expected bytea; prior bytea;
BEGIN
 IF NOT platform.active_member(org,'org_admin') OR actor IS NULL OR target=actor OR desired_role NOT IN ('reviewer','supervisor') THEN RAISE EXCEPTION 'authorization denied' USING ERRCODE='42501'; END IF;
 expected:=digest(convert_to(jsonb_build_array(target,desired_role,expiry,revoke)::text,'UTF8'),'sha256');
 PERFORM pg_advisory_xact_lock(hashtextextended(org::text||actor::text||command::text,1));
 SELECT body_hash INTO prior FROM platform.identity_commands WHERE organization_id=org AND principal_id=actor AND command_id=command;
 IF prior IS NOT NULL THEN
  IF prior<>expected THEN RAISE EXCEPTION 'idempotency conflict' USING ERRCODE='23505'; END IF;
  RETURN;
 END IF;
 PERFORM platform.membership_change(org,target,desired_role,expiry,revoke);
 INSERT INTO platform.identity_commands(organization_id,principal_id,command_id,body_hash) VALUES(org,actor,command,expected);
END $$;
ALTER FUNCTION platform.membership_command(uuid,uuid,text,timestamptz,boolean,uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.membership_command(uuid,uuid,text,timestamptz,boolean,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.membership_command(uuid,uuid,text,timestamptz,boolean,uuid) TO foc_api;
-- All API writes must enter through the idempotent wrapper. The policy owner may call the inner routine.
REVOKE EXECUTE ON FUNCTION platform.membership_change(uuid,uuid,text,timestamptz,boolean) FROM foc_api;
