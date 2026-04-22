# Epic 31: Blueprint Transformer Zero-Compromise Hardening

## 1. Description and Motivation
The `BlueprintTransformer` (`backend_v2/services/blueprint.py`) currently violates the **Zero-Compromise Pledge** and **Universal Fail-Fast** mandates defined in `00-antigravity-core` and `01-python-backend`. Serving as the final boundary between the Backend LLM synthesis pipeline and the Flutter Client UI, it exhibits severe cases of "defensive programming" (duct-tape code), graceful degradation, and duck typing (e.g., heavily utilizing `.get(key, default)`, `isinstance(val, dict)`, and `hasattr()`). 

These legacy survivorship mechanisms silently paper over upstream structural failures. If an LLM Hook produces a malformed dictionary or drops an extension, `BlueprintTransformer` hides the error by substituting empty arrays or parsing legacy V1 fallback keys (like `step_data.get("justification")` instead of crashing on the V2 extension). This masks critical data corruption, violates the architectural requirement for **Strict Pydantic V2 Rust Validation**, and leads to untraceable shadow-states when the Flutter UI renders empty components.

**Objective:** Cleanse the `BlueprintTransformer` and `StateProjector` of all duck typing and fallback logic. Enforce strict Pydantic V2 models for interpreting the `execution_trace`. Any deviation from the schema must trigger a 500 Fail-Fast `AppException` rather than propagating "duct-taped" empty data to the UI.

## 2. Architectural Mandates Enforced (Rules Reference)
- **`the_zero_compromise_pledge` (`00-antigravity-core`):** Eradicate fallback chains (`if A missing, try B`) and Python language defaults (`v.get('field', '')`). Missing keys must raise explicit exceptions and crash.
- **`the_duct_tape_ban` (`00-antigravity-core`):** Stop returning empty arrays `[]` or default dicts `{}` when real data goes missing. Fix the root cause in the upstream data hooks.
- **`zero_service_layer_fallbacks` (`00-antigravity-core`):** Eliminate `getattr()`, `.get()`, and `if value is None: value = default` from `blueprint.py`. Pydantic models must guarantee native value extraction natively.
- **`no_naked_dicts_in_state` (`01-python-backend`):** Ensure the `fold_trace` and subsequent accesses operate on strongly-typed Pydantic classes (e.g., `ReportAxisDTO`, `XaiHighlightItem`) instead of parsing naked `step_res` dictionaries. 
- **`strict_pydantic_v2_rust` (`01-python-backend`):** Utilize `.model_validate()` at the boundaries with `ConfigDict(extra='forbid', strict=True)` to reject unstructured AI outputs instantly.

## 3. Implementation Phases

### Phase 1: Eradicating `_extract_numeric_score` and Naked Dict Access
- **Target:** `_extract_numeric_score` in `BlueprintTransformer`.
- **Action:** Delete this static method. 
- **Reasoning:** It arbitrarily guesses whether a float score lives under `step_4_final_score` or `score`, and permits `Any` types with fallbacks. 
- **Solution:** Enforce that the step output natively arrives as a strict `EvaluationResult` Pydantic class where `.score` is a strongly typed `float`.

### Phase 2: Removing Duck Typing from the ReportAxis Layout Loop
- **Target:** The `for step_res in results.values():` and `for k, v in step_data.items():` loops constructing the `ReportAxisDTO`.
- **Action:** Purge the `isinstance(v, dict)` branching. Delete all legacy key lookups (e.g., falling back to `f"{k}_justification"` if `step_3_logical_friction` is missing). 
- **Reasoning:** Cross-contamination of V1 legacy data retrieval logic breaks the Fail-Fast mechanism. 
- **Solution:** `v` MUST explicitly map sequence outputs to a unified Pydantic Model (`AtomFlatteningResult` or similar). If a block fails validation, raise an `AppException(ErrorCodes.VALIDATION_FAILED)`.

### Phase 3: Hardening XAI Cache Extraction
- **Target:** `xai_highlights_cache` parsing.
- **Action:** Remove the `hasattr(highlight, "model_dump")` check. 
- **Reasoning:** The application relies on `isinstance(highlight, dict)` fallbacks.
- **Solution:** Cast elements rigorously utilizing `.model_validate()` from the corresponding Output Extension model. Assume objects are 100% Pydantic models. Missing an `extension_type` must fail naturally through Pydantic's underlying rust-validation (i.e. `ValidationError`), not manual python `if not type_name:` checks.

### Phase 4: Validating MCP Audit Trail Fail-Fast
- **Target:** The `f_context.get("mcp_tool_audit")` parsing logic.
- **Action:** Remove the defensive `isinstance(audit, dict)` checks.
- **Reasoning:** The code currently explicitly comments: `"Defensive parsing in case elements are Pydantic models vs dicts"`. This is highly illegal under the core V2 architecture.
- **Solution:** The state trace MUST yield `MCPAuditTrace` objects natively. Access attributes directly via dot notation (`audit.tool_id`).

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

### Specific Epic 31 Testing Mandates
1. Use `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test` to ensure coverage remains > 90%.
2. Write explicitly failing Negative Unit Tests where incoming DB `execution_traces` omit required keys. The tests MUST assert that a strict `ValidationError` or `AppException` is thrown, proving the pipeline crashes instead of rendering empty Flutter data sets.
3. Validate OpenAPI schemas via `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --openapi` after removing wildcard/Dict types from models.
