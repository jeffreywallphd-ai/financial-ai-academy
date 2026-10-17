DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM personal_workspace.mutations LIMIT 1)
       OR EXISTS (SELECT 1 FROM personal_workspace.workspaces LIMIT 1) THEN
        RAISE EXCEPTION 'refusing to remove retained Personal workspace data';
    END IF;
END;
$$;

DROP TABLE personal_workspace.mutations;
DROP TABLE personal_workspace.workspaces;
DROP SCHEMA personal_workspace;
