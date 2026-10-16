DROP TRIGGER IF EXISTS curriculum_practice_review_targets_append_only
    ON curriculum.practice_review_targets;
DROP FUNCTION IF EXISTS curriculum.reject_practice_review_target_mutation();
DROP TABLE IF EXISTS curriculum.practice_review_targets;
