-- Separate isolated control database only. NEVER apply to operational cases.
CREATE SCHEMA demo_governance;
REVOKE ALL ON SCHEMA demo_governance FROM PUBLIC;
CREATE TABLE demo_governance.authority (
 instance uuid PRIMARY KEY, enabled boolean NOT NULL DEFAULT false,
 epoch bigint NOT NULL CHECK(epoch>0), activation bigint NOT NULL CHECK(activation>0),
 expires timestamptz NOT NULL
);
CREATE TABLE demo_governance.jobs (
 id uuid PRIMARY KEY, instance uuid NOT NULL REFERENCES demo_governance.authority,
 organization uuid NOT NULL, token uuid NOT NULL, revision bigint NOT NULL CHECK(revision>0),
 state text NOT NULL CHECK(state IN ('running','cancelled','rejected','complete')),
 deadline timestamptz NOT NULL, epoch bigint NOT NULL, activation bigint NOT NULL,
 snapshot text NOT NULL CHECK(snapshot ~ '^[a-f0-9]{64}$'),
 UNIQUE(instance,organization,snapshot)
);
CREATE TABLE demo_governance.grants (
 job uuid NOT NULL REFERENCES demo_governance.jobs,
 kind text NOT NULL CHECK(kind IN ('key','model','image','case','media','purpose')),
 revision bigint NOT NULL CHECK(revision>0), active boolean NOT NULL DEFAULT false,
 expires timestamptz NOT NULL, PRIMARY KEY(job,kind)
);
CREATE TABLE demo_governance.audit (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, job uuid NOT NULL REFERENCES demo_governance.jobs,
 action text NOT NULL CHECK(action='synthetic.complete'), created timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE demo_governance.outbox(job uuid PRIMARY KEY REFERENCES demo_governance.jobs);
ALTER TABLE demo_governance.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE demo_governance.jobs FORCE ROW LEVEL SECURITY;
CREATE POLICY job_scope ON demo_governance.jobs USING (
 instance::text=current_setting('foc.demo_instance',true) AND organization::text=current_setting('foc.demo_organization',true)
) WITH CHECK (
 instance::text=current_setting('foc.demo_instance',true) AND organization::text=current_setting('foc.demo_organization',true)
);
-- The private runtime may only complete existing jobs; control-plane admission/
-- cancellation/revocation remains privileged. No public schema/search_path grants.
CREATE ROLE foc_demo_fence NOLOGIN NOSUPERUSER NOBYPASSRLS;
GRANT USAGE ON SCHEMA demo_governance TO foc_demo_fence;
GRANT SELECT ON demo_governance.authority,demo_governance.jobs TO foc_demo_fence;
REVOKE ALL ON ALL TABLES IN SCHEMA demo_governance FROM PUBLIC;
CREATE FUNCTION demo_governance.publish(j uuid,t uuid,e bigint,r bigint,i uuid,o uuid,s text)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,demo_governance AS $$
DECLARE a demo_governance.authority; w demo_governance.jobs; valid integer; expiry timestamptz;
BEGIN
 IF i::text IS DISTINCT FROM current_setting('foc.demo_instance',true)
 OR o::text IS DISTINCT FROM current_setting('foc.demo_organization',true)
 THEN RAISE EXCEPTION 'scope fence' USING ERRCODE='42501'; END IF;
 SELECT * INTO a FROM demo_governance.authority WHERE instance=i FOR UPDATE;
 IF NOT FOUND OR NOT a.enabled OR a.epoch<>e OR a.expires<=clock_timestamp()
 THEN RAISE EXCEPTION 'authority fence' USING ERRCODE='42501'; END IF;
 SELECT * INTO w FROM demo_governance.jobs WHERE id=j AND instance=i AND organization=o FOR UPDATE;
 IF NOT FOUND OR w.token<>t OR w.revision<>r OR w.state<>'running' OR w.epoch<>a.epoch
 OR w.activation<>a.activation OR w.snapshot<>s OR w.deadline<=clock_timestamp()
 THEN RAISE EXCEPTION 'job fence' USING ERRCODE='42501'; END IF;
 PERFORM 1 FROM demo_governance.grants WHERE job=j ORDER BY kind FOR UPDATE;
 SELECT count(*),min(expires) INTO valid,expiry FROM demo_governance.grants
 WHERE job=j AND active AND revision=r AND expires>clock_timestamp();
 IF valid<>6 THEN RAISE EXCEPTION 'grant fence' USING ERRCODE='42501'; END IF;
 INSERT INTO demo_governance.audit(job,action) VALUES(j,'synthetic.complete');
 -- Mandatory audit can block/fail; wall clock, not transaction-start now().
 IF w.deadline<=clock_timestamp() OR a.expires<=clock_timestamp() OR expiry<=clock_timestamp()
 THEN RAISE EXCEPTION 'deadline fence' USING ERRCODE='42501'; END IF;
 UPDATE demo_governance.jobs SET state='complete' WHERE id=j;
 INSERT INTO demo_governance.outbox(job) VALUES(j);
 RETURN true;
END $$;
REVOKE ALL ON FUNCTION demo_governance.publish(uuid,uuid,bigint,bigint,uuid,uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION demo_governance.publish(uuid,uuid,bigint,bigint,uuid,uuid,text) TO foc_demo_fence;
