DROP TRIGGER IF EXISTS curriculum_project_brief_placements_append_only
    ON curriculum.project_brief_placements;
DROP FUNCTION IF EXISTS curriculum.reject_project_brief_placement_mutation();
DROP TABLE curriculum.project_brief_placements;
