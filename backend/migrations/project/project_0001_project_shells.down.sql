DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM project.project_shells LIMIT 1) THEN
        RAISE EXCEPTION 'refusing to remove retained Project shells';
    END IF;
END;
$$;

DROP TRIGGER IF EXISTS project_shells_append_only ON project.project_shells;
DROP FUNCTION IF EXISTS project.reject_project_shell_mutation();
DROP TABLE project.project_shells;
DROP SCHEMA project;
