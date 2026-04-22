# Epic: Purge Repository Fallbacks (Zero-Compromise Pydantic V2)

## 1. Context & Goal

The current backend repository layer (`backend_v2/database/repository.py`) contains several legacy "fallback" and "shortcut" mechanisms left over from earlier architectural phases (V1 / early V2). These fallbacks attempt to magically resolve missing data by sweeping through nested objects (e.g., looking for steps inside workflows) or reaching out to the local disk (e.g., loading `.json` files if DB lookups fail). 

This completely violates the **Phase 9: Zero-Compromise** and **Strict SSOT (Single Source of Truth)** architectural principles. The goal of this Epic is to ruthlessly purge these fallbacks to enforce a pure Fail-Fast model. If data does not exist in the designated SSOT collection, the repository must immediately return `None`, delegating the responsibility to the Service layer to throw a 404 `AppException`.

## 2. Architectural Mandates Enforced (Rules Reference)
- **`the_zero_compromise_pledge` (`00-antigravity-core`):** Eradicate fallback chains (`if A missing, try B`) and Python language defaults (`v.get('field', '')`). Missing keys must raise explicit exceptions and crash.
- **`the_duct_tape_ban` (`00-antigravity-core`):** Stop returning `None`, empty arrays `[]`, or default dicts `{}` when real data goes missing. Fix the root cause in the database seeder or upstream data.
- **`zero_service_layer_fallbacks` (`00-antigravity-core`):** Eliminate `getattr()`, `.get()`, and `if value is None: value = default` from `repository.py`. Pydantic models must guarantee native value extraction natively.
- **`strict_pydantic_v2_rust` (`01-python-backend`):** Utilize strict validation. If the DB driver returns data that doesn't match the strict schema, it must throw `ValidationError`.

## 3. Implementation Phases

### Phase 1: Clean `repository.py`
Remove all fallback logic in `c:\src\quorum\backend_v2\database\repository.py`:
1. **`get_step_by_id`**: Remove the nested loop sweeping `workflows` for embedded steps. Steps must live strictly in the `steps` SSOT collection.
2. **`get_workflow_definition`**: Remove the `Disk Fallback (Critical for Dev)` that reads from `data/workflows/` using the OS file system.
3. **`get_prompt_template`**: Remove the secondary query fallback by `id` property when `doc_id` mismatch occurs.

### Phase 2: Test Suite Audit & Refactoring
Removing fallbacks will likely break existing unit tests that rely on them. 
1. **Audit Tests**: Run the full test suite (`uv run pytest`) and identify all failing tests caused by the removed fallbacks (specifically around `test_repository.py` or workflow definitions).
2. **Refactor Mocks**: Update test mocks to provide valid SSOT data directly, rather than relying on the repository's fallback sweeps to find nested data.
3. **Create Strict Verification Tests**: Write new unit tests that explicitly assert that the repository returns `None` (and *does not* attempt a fallback) when the exact SSOT document is missing.

### Phase 3: Final Validation
1. Run `uv run python scripts/backend_audit_loop.py backend_v2/database/repository.py` to verify syntax, linting, and coverage >90%.
2. Verify live backend boot does not crash due to missing disk fallbacks.

## 4. Testing & Verification Mandate (Synthesis.py Standard)

### Universal Synthesis.py Case Study Execution Standards
Every single code modification inside this Epic MUST strictly adhere to the exact same architectural rigor successfully pioneered in `backend_v2/hooks/synthesis.py`:
- **Eradicate God Blocks:** Destroy massive `try...except Exception:` blocks. If a function is wrapped in a catch-all that suppresses native `AppException` propagation or obscures the original HTTP status codes/`ErrorCodes`, blow it up immediately.
- **Pure Function Extraction:** Identify any deep dictionary mutation loops, arbitrary text compression, or O(N^2) search loops and aggressively rip them out into isolated, testable Pure Functions. Keep the main orchestrator as a simple, highly readable pipeline.
- **O(1) Map Pre-computation:** Nested iteration loops inside data pipelines must be replaced with O(1) pre-computed lookup dictionaries to resolve heavy schema references instantly.
- **Enum-Driven Configuration:** Replace arbitrary boolean toggles with strictly validated Pydantic Enums.
- **Zero-Compromise 100% Pytest Coverage:**
  - **Fail-Fast Safety Tests:** Write specific tests that feed missing or corrupted Pydantic metadata/locales to the orchestrator to verify that it immediately crashes with `400 Validation Error` or `404 Not Found` (Zero Graceful Degradation).
  - **Pure Function Isolation:** Every extracted helper function MUST have its own dedicated unit test validating corner cases without requiring Database or LLM mocks.
  - **Happy-Path Orchestrator Integration:** Use `MagicMock` and `PydanticModel.model_construct()` to bypass rigid instantiation overhead in the test suite, allowing the mock environment to simulate a flawless execution pipeline.
  - **Universal Quality Gate:** The refactored module MUST pass `ruff check`, `mypy`, and `pytest` with 0 warnings before being considered complete.

### Specific Epic Testing Mandates
1. Use `uv run python scripts/backend_audit_loop.py backend_v2/database/repository.py` to assure metrics.
2. Write explicitly failing Negative Unit Tests where incoming DB traces omit required keys. The tests MUST assert that an `AppException` is thrown, proving the pipeline crashes instead of searching deeply nested workflows for missing steps.
3. Validate OpenAPI schemas via `uv run python scripts/backend_audit_loop.py backend_v2/database/repository.py --openapi`.
