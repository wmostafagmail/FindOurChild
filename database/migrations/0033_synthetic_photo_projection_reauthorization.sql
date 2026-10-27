-- A comparison selected before an audit wait must not disclose photograph
-- identifiers/chronology after the corresponding media grant is withdrawn.
DO $migration$
DECLARE definition text; needle text;
BEGIN
 definition:=pg_get_functiondef('platform.sw_read(uuid,uuid,text)'::regprocedure);
 needle:=' RETURN result;';
 IF length(definition)-length(replace(definition,needle,''))<>length(needle) THEN RAISE EXCEPTION 'unexpected sw_read photo projection'; END IF;
 EXECUTE replace(definition,needle,$body$ IF view_name='comparison' AND EXISTS(SELECT 1 FROM jsonb_array_elements(result->'photos') p WHERE NOT platform.case_permission(org,(p->>'case_id')::uuid,'media.read')) THEN RAISE EXCEPTION 'not found' USING ERRCODE='42501'; END IF;
 RETURN result;$body$);
END
$migration$;
