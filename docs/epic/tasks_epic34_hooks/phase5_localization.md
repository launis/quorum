# Phase 5: Localization & Validation Metadata Sovereignty

## 1. Description and Objective
**Epic 34: Global Hooks Zero-Compromise Hardening.**
The `validation.py` & `translation_hook.py` files use `.get("language")` and `.get("target_locale", "en")` fallbacks for state access. This violates the rule against arbitrary dictionary defaults. The objective is to define strict `HookStateMetadata` and `I18nStatePayload` Pydantic models.

## 2. File Scoping
- **TARGET (Modify):** 
  - `backend_v2/hooks/validation.py`
  - `backend_v2/hooks/translation_hook.py`
  - `backend_v2/models/dtos/state.py` (or appropriate model definitions file)
- **CONTEXT (Read-Only):** 
  - None

## 3. Implementation Steps
- [x] 1. **Define Models:** Create strict `HookStateMetadata` and `I18nStatePayload` Pydantic models.
- [x] 2. **Intercept State Early:** Both hooks must intercept `state.inputs` and `state.metadata` at the start of execution using `Model.model_validate()`.
- [x] 3. **Eradicate Fallbacks:** Remove `.get("language")` and `.get("target_locale", "en")` fallbacks.
- [x] 4. **Resolution Logic:** Leverage `I18nText.resolve()` logic to achieve Fail-Fast parity with the hardened `synthesis.py` hook.

## 4. Verification & Quality Gate Plan
- **Unit Testing:** Verify that `translation_hook.py` drops gracefully into an `AppException` (e.g. `400 Validation Error` or `404 Not Found`) if the `target_locale` is absent, rather than defaulting to English. Test pure functions in isolation.
- **Audit Loop Execution:** `uv run python scripts/backend_audit_loop.py backend_v2/hooks/validation.py backend_v2/hooks/translation_hook.py --test`
