-- A stale worker may not erase objects adopted by a newer lease. Cleanup reads committed publication state.
CREATE OR REPLACE FUNCTION platform.quarantine_cleanup_next() RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE result jsonb;
BEGIN
 SELECT jsonb_build_object('id',u.id,'key',m.quarantine_key,'version',m.quarantine_version,'published',EXISTS(SELECT 1 FROM app.objects o WHERE o.organization_id=m.organization_id AND o.id=m.object_id AND o.bucket_class='original')) INTO result FROM app.upload_intents u JOIN platform.upload_metadata m ON m.organization_id=u.organization_id AND m.intent_id=u.id WHERE NOT m.quarantine_purged AND (u.state='ready' OR (u.expires_at<now()-interval '24 hours' AND u.state IN ('pending','uploaded','rejected'))) ORDER BY u.expires_at,u.id LIMIT 1 FOR UPDATE OF m SKIP LOCKED;
 RETURN result;
END $$;
