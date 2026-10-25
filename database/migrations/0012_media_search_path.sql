-- Qualify the already-reviewed pgcrypto location for upload nonce hashing.
ALTER FUNCTION platform.upload_create(bytea,uuid,uuid,uuid,bytea,bigint,text,text,text,uuid,bytea) SET search_path=pg_catalog,app,platform,public;
