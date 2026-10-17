DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM learner_model.preference_mutations LIMIT 1)
       OR EXISTS (SELECT 1 FROM learner_model.preference_changes LIMIT 1)
       OR EXISTS (SELECT 1 FROM learner_model.preference_profiles LIMIT 1) THEN
        RAISE EXCEPTION 'refusing to remove retained learner preference data';
    END IF;
END;
$$;

DROP TABLE learner_model.preference_mutations;
DROP TABLE learner_model.preference_changes;
DROP TABLE learner_model.preference_profiles;
