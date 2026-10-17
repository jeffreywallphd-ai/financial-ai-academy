# Learner Presentation Preferences v1

This Draft 2020-12 contract family records four explicit, safe presentation
choices owned by Learner model:

- `text_size`: `default` or `larger`;
- `text_spacing`: `default` or `increased`;
- `reading_width`: `standard` or `focused`; and
- `motion`: `system` or `reduce`.

Every profile is complete. A replacement supplies all four choices, while a
reset returns to `default`, `default`, `standard`, and `system`. History is
bounded and contains only revision, operation, time, and resulting digest.

These values are explicit learner input, not a diagnosis, inferred need,
Assessment evidence, competency, eligibility, permission, recommendation, or
financial signal. Browser-local light/dark/device theme is not part of this
family and has no headless meaning. Consuming presentation adapters must keep
browser zoom, forced colors, and protective reduced-motion behavior effective.

Run the focused contract and pure-core evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/learner_presentation_preferences backend/tests/unit/learner_model/test_presentation_preference_contract.py backend/tests/unit/learner_model/test_presentation_preferences.py
```
