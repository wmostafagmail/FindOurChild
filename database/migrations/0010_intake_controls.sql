ALTER TABLE platform.intake_challenges ADD COLUMN command uuid;
CREATE FUNCTION platform.intake_authorize(token bytea,browser bytea,cmd uuid) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$
BEGIN
 UPDATE platform.intake_challenges SET consumed_at=coalesce(consumed_at,now()),command=cmd WHERE hash=token AND browser_hash=browser AND expires_at>now() AND (command IS NULL OR command=cmd);
 RETURN FOUND;
END $$;
ALTER FUNCTION platform.intake_authorize(bytea,bytea,uuid) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.intake_authorize(bytea,bytea,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.intake_authorize(bytea,bytea,uuid) TO foc_api;
CREATE TABLE platform.safeguarding_inbox(id uuid PRIMARY KEY DEFAULT gen_random_uuid(),body_ciphertext text NOT NULL,created_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE platform.safeguarding_inbox OWNER TO foc_owner;
ALTER TABLE platform.safeguarding_inbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.safeguarding_inbox FORCE ROW LEVEL SECURITY;
GRANT INSERT ON platform.safeguarding_inbox TO foc_policy;
CREATE POLICY internal_insert ON platform.safeguarding_inbox FOR INSERT TO foc_policy WITH CHECK(true);
CREATE FUNCTION platform.concern_append(cipher text) RETURNS void LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,platform AS $$ INSERT INTO platform.safeguarding_inbox(body_ciphertext) VALUES(cipher) $$;
ALTER FUNCTION platform.concern_append(text) OWNER TO foc_policy;
REVOKE ALL ON FUNCTION platform.concern_append(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION platform.concern_append(text) TO foc_api;
