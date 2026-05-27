# Phase 5: Hardening, E2E Audit & Architecture Documentation (Verification & Compliance Layer)

This sub-plan covers implementing test cases for backoff resilience, running the backend/frontend audit loops to ensure zero compiler warnings, updating the core architectural documentation (02, 05, 07, 09), and performing legacy cleanup.

## Architectural Invariants (From Rules)
1. **Rule 1: No-String Mandate & Bilingual Decoupling** - Documentation updates must preserve the Bilingual Decoupling TDA exception rules and No-String Mandate.
2. **Rule 2: Flat MVC State & Optimistic UI Focus** - Document the exact mechanism of using Form's `onSaved` lifecycle and synchronous Riverpod state updating to prevent cursor jumps in reactive UI text areas.
3. **Rule 3: Strict Mode & Fail-Fast** - Ensure missing environment variables throw a clear `ConfigurationError` and that is documented.

## Proposed Changes

### Target Files (Modify)
- [02_domain_models.md](file:///c:/src/quorum/docs/architecture/02_domain_models.md)
- [05_llm_and_hooks.md](file:///c:/src/quorum/docs/architecture/05_llm_and_hooks.md)
- [07_desktop_first_flutter.md](file:///c:/src/quorum/docs/architecture/07_desktop_first_flutter.md)
- [09_data_persistence.md](file:///c:/src/quorum/docs/architecture/09_data_persistence.md)

### Target Files (New)
- [test_adaptive_retry.py](file:///c:/src/quorum/tests/unit/test_adaptive_retry.py)

### Context Files (Read-Only)
- [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)
- [model_registry_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/model_registry_view.dart)

---

## Milestones

### Milestone 1: Create Adaptive Retry Test
* **Source**: Epic Phase 5, Step 1
* **Files**: [test_adaptive_retry.py](file:///c:/src/quorum/tests/unit/test_adaptive_retry.py) [NEW]
* **Instructions**:
  Create a new unit test verifying the tenacity exponential backoff with jitter. Mock transient LLM errors (such as 429 status codes) and assert that they retry correctly and trigger the backoff log warning. Use `pytest-asyncio` for asynchronous test suites. Example:
  ```python
  import pytest
  from unittest.mock import AsyncMock, patch
  from backend_v2.llm.provider import LiteLLMProvider, _is_transient_llm_error
  from backend_v2.core.exceptions import ConfigurationError

  @pytest.mark.asyncio
  async def test_adaptive_retry_with_jitter():
      # Mock the LiteLLM router.acompletion to fail once with a rate limit error (429) then succeed
      # Assert retry logic runs, exponential backoff is scheduled, and eventual success is achieved.
      pass
  ```

### Milestone 2: Update 02_domain_models.md
* **Source**: Epic Phase 6, Step 1
* **Files**: [02_domain_models.md](file:///c:/src/quorum/docs/architecture/02_domain_models.md)
* **Instructions**:
  Add `additional_params` to the `ModelProfile` Pydantic class diagram and description text. Highlight that `additional_params` is a polymorphic dictionary containing provider-specific properties like `vertex_location` or `aws_region`.
  ```markdown
      class ModelProfile{
          ...
          +String caching_strategy
          +dict additional_params
          +bool is_active
      }
  ```

### Milestone 3: Update 05_llm_and_hooks.md
* **Source**: Epic Phase 6, Step 1
* **Files**: [05_llm_and_hooks.md](file:///c:/src/quorum/docs/architecture/05_llm_and_hooks.md)
* **Instructions**:
  Add a section describing "Universal Provider Decoupling & Dynamic Env Resolver" and "Resilient Exponential Jitter-Backoff". Detail how dynamic environment variable interpolation handles `${VAR_NAME}` and why the static rate limit cooldown was replaced by tenacious jitter backoff.

### Milestone 4: Update 07_desktop_first_flutter.md
* **Source**: Epic Phase 6, Step 1
* **Files**: [07_desktop_first_flutter.md](file:///c:/src/quorum/docs/architecture/07_desktop_first_flutter.md)
* **Instructions**:
  Document the new Admin Studio Model Registry UI parameters (`additional_params` and `caching_strategy`). Explain the UX/UI focus prevention strategy of using Form's `onSaved` lifecycle and Riverpod `saveRegistry` state retrieval to avoid cursor jumping inside reactive text areas during polymorphic JSON modifications.

### Milestone 5: Update 09_data_persistence.md
* **Source**: Epic Phase 6, Step 1
* **Files**: [09_data_persistence.md](file:///c:/src/quorum/docs/architecture/09_data_persistence.md)
* **Instructions**:
  Document the storage of dynamic configuration variables and environment parameters within `ModelProfile` records in the `seed_data.json` / TinyDB database, removing hardcoded cloud-location bindings from code.

---

## Testing & Quality Gate Plan

### Automated Tests
1. Run the newly created test:
   * Command: `uv run pytest tests/unit/test_adaptive_retry.py`
2. Run the complete backend audit loop:
   * Command: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
3. Run the complete frontend audit loop:
   * Command: `uv run python scripts/flutter_audit_loop.py client_app_v2`

---

## Session Handover
To proceed, mark the Tracker tasks as complete and close the loop:
```powershell
To execute this Epic iteratively, start a NEW chat session and run: /tier5-resume --target docs/epic/EPIC_62_tracker.md
```
