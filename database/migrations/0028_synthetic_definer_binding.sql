-- Renaming a PL/pgSQL function does not rewrite its qualified parameter labels.
-- Preserve the applied body and correct only those two labels, under an explicit guard.
DO $$ DECLARE definition text;
BEGIN
 SELECT pg_get_functiondef('platform.sw_event_command_base(uuid,uuid,text,jsonb,bigint,uuid)'::regprocedure) INTO definition;
 IF position('sw_event_command.operation' IN definition)=0 OR position('sw_event_command.command' IN definition)=0 THEN RAISE EXCEPTION 'Unexpected synthetic command body'; END IF;
 definition:=replace(replace(definition,'sw_event_command.operation','sw_event_command_base.operation'),'sw_event_command.command','sw_event_command_base.command');
 EXECUTE definition;
END $$;
