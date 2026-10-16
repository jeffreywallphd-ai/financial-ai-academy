DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM curriculum.project_brief_placements LIMIT 1
    ) THEN
        RAISE EXCEPTION
            'cannot roll back retained project brief placements'
            USING ERRCODE = '55000';
    END IF;
END;
$$;

DROP TRIGGER IF EXISTS curriculum_project_brief_placements_append_only
    ON curriculum.project_brief_placements;
DROP FUNCTION IF EXISTS curriculum.reject_project_brief_placement_mutation();
DROP TABLE curriculum.project_brief_placements;
