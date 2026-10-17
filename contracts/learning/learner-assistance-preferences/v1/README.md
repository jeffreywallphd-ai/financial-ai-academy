# Learner Assistance Preferences v1

This Draft 2020-12 contract family records one explicit AI-help choice owned by
Learner model:

- `off`: do not offer learner-requested AI help;
- `on_request`: a later governed feature may offer help that the learner must
  start deliberately each time.

`on_request` does not enable or select a provider, grant permission to send a
data class, call a model, create output, or promise that AI help is available.
Provider admission, selection, credentials, and data permission remain separate
governed controls. No provider is enabled by default.

The complete profile is revision-bound and defaults to `off`. Replacement
supplies the whole choice, reset returns to `off`, and history retains at most
100 non-content summaries. The export is a portable record of explicit learner
intent, not provider consent, execution authority, evidence, or a recommendation.

Browser-local learning reminders are not part of this family and have no API or
headless meaning.

Run the focused contract and pure-core evidence from the repository root:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/learner_assistance_preferences backend/tests/unit/learner_model/test_assistance_preference_contract.py backend/tests/unit/learner_model/test_assistance_preferences.py
```
