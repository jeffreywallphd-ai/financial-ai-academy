# Learner Preferences v1

This additive Draft 2020-12 family defines explicit learner-entered learning
goals, self-described experience, interests, revision-bound mutations, bounded
change summaries, and a portable export.

Learner model owns these records. They are preferences and intentions only.
They are not Assessment evidence, competency or mastery state, Curriculum
requirements, Adaptation eligibility, permission, experiment consent,
financial suitability, or a recommendation. No field is inferred from
activity, assessment, provider, model, or third-party data.

The profile permits at most 20 goals, 20 experience entries, and 50 interests.
History exposes at most 100 non-content change summaries. Canonical profile
digests use compact sorted-key JSON encoded directly as UTF-8, exclude the
`profile_digest` field, and do not normalize Unicode implicitly.

The pure contract adapter performs no persistence, identity resolution,
authorization, clock, ID generation, network, provider, model, or cross-module
mutation. Later protected application/API work supplies those concerns under
server authority for browser and supported headless clients.

Run focused evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/learner_preferences backend/tests/unit/learner_model/test_preference_contract.py backend/tests/unit/learner_model/test_preferences.py
```
