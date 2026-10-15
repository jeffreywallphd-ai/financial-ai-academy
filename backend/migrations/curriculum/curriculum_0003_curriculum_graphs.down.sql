DROP TRIGGER IF EXISTS curriculum_graph_versions_append_only
    ON curriculum.curriculum_graph_versions;
DROP FUNCTION IF EXISTS curriculum.reject_curriculum_graph_version_mutation();
DROP TABLE IF EXISTS curriculum.curriculum_graph_versions;
