DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM project.project_workspaces LIMIT 1)
       OR EXISTS (SELECT 1 FROM project.project_workspace_mutations LIMIT 1)
       OR EXISTS (SELECT 1 FROM project.project_artifact_objects LIMIT 1)
       OR EXISTS (SELECT 1 FROM project.project_snapshots LIMIT 1) THEN
        RAISE EXCEPTION 'refusing to remove retained Project workspace data';
    END IF;
END;
$$;

DROP TRIGGER IF EXISTS project_snapshots_append_only ON project.project_snapshots;
DROP FUNCTION IF EXISTS project.reject_project_snapshot_mutation();
DROP TABLE project.project_snapshots;
DROP TABLE project.project_artifact_objects;
DROP TABLE project.project_workspace_mutations;
DROP TABLE project.project_workspaces;
