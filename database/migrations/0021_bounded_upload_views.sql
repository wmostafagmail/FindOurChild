-- Keep summary DTOs within the ten active-intent quota; no provenance is deleted.
CREATE OR REPLACE FUNCTION platform.media_list(org uuid,cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
BEGIN
 IF NOT platform.case_permission(org,cid,'case.read') THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 RETURN coalesce((SELECT jsonb_agg(jsonb_build_object('id',u.id,'state',u.state,'media_id',o.id,'metadata_ciphertext',m.metadata_ciphertext,'scan_engine',m.scan_engine,'scan_signature',m.scan_signature)) FROM app.upload_intents u JOIN platform.upload_metadata m ON m.organization_id=u.organization_id AND m.intent_id=u.id LEFT JOIN app.objects o ON o.organization_id=m.organization_id AND o.opaque_key=m.derivative_key AND o.bucket_class='derivative' WHERE u.organization_id=org AND u.case_id=cid AND u.state<>'expired'),'[]'::jsonb);
END $$;
CREATE OR REPLACE FUNCTION platform.reporter_upload_states(token bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,platform,app AS $$
DECLARE ctx jsonb:=platform.reporter_context(token);
BEGIN
 IF ctx IS NULL THEN RAISE EXCEPTION 'denied' USING ERRCODE='42501'; END IF;
 RETURN coalesce((SELECT jsonb_agg(jsonb_build_object('id',u.id,'state',u.state) ORDER BY u.id) FROM app.upload_intents u WHERE u.organization_id=(ctx->>'organization_id')::uuid AND u.case_id=(ctx->>'case_id')::uuid AND u.state<>'expired'),'[]'::jsonb);
END $$;
