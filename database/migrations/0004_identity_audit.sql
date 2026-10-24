-- pgcrypto functions are used only by the restricted policy role; PUBLIC still cannot use schema public.
GRANT USAGE ON SCHEMA public TO foc_policy;
-- Login/logout are recorded per currently authorized organization. No tokens, contacts or request bodies.
CREATE OR REPLACE FUNCTION platform.session_create(hash bytea, pid uuid, ciphertext text, csrf bytea, expiry timestamptz) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform
AS $$
DECLARE org record;
BEGIN
 IF pid::text IS DISTINCT FROM current_setting('foc.principal',true) OR expiry<=now() THEN RAISE EXCEPTION 'authorization denied' USING ERRCODE='42501'; END IF;
 INSERT INTO platform.identity_sessions(token_hash,principal_id,encrypted_token,csrf_hash,expires_at) VALUES(hash,pid,ciphertext,csrf,least(expiry,now()+interval '30 minutes'));
 FOR org IN SELECT id FROM platform.identity_orgs() LOOP
  PERFORM set_config('foc.organization',org.id::text,true);
  PERFORM platform.audit_append(org.id,'identity.read',pid,'allowed');
 END LOOP;
END $$;
ALTER FUNCTION platform.session_create(bytea,uuid,text,bytea,timestamptz) OWNER TO foc_policy;
