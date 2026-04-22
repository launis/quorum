# Epic 32: LLM Orchestrator Zero-Compromise Hardening

## 1. Description and Motivation
Following the cleanup of `BlueprintTransformer` (Epic 31), an audit of `backend_v2/services/orchestrator/strategies/llm.py` reveals the exact same architectural anti-patterns occurring at the core Map-Reduce execution boundary. The `LLMNodeStrategy` heavily manipulates trace outputs as naked `dict[str, Any]` objects instead of strict Pydantic structures. 

Specifically, the system uses recursive duck typing `_strip_heavy_keys` to arbitrarily delete keys (`obj.pop("quote", None)`) based on `isinstance(dict)`. Furthermore, the Map-Reduce chunk aggregation (around line ~440) performs primitive dictionary merging (`final_dict[k][s_key] += f" {s_val}"`) assuming everything inside a `matrix_` or `blk_` block is a string. This violates the **Zero-Compromise Pledge** and **No Naked Dicts in State** mandates, creating a fragile execution environment where an unexpected LLM list or number output crashes the dictionary merger with `TypeError: unorderable types`.

**Objective:** Refactor `LLMNodeStrategy` and `NodeStrategy.run_post_hooks` to strictly use Pydantic accumulators. Discard all `dict` mutations in favor of properly typed Pydantic models (e.g., `ChunkResultAccumulator.add(chunk)`).

## 2. Architectural Mandates Enforced (Rules Reference)
- **`no_naked_dicts_in_state` (`01-python-backend`):** Eliminating the passing of `final_dict: dict[str, Any]` through `run_post_hooks`. Data must be validated at the LLM boundary immediately and merged via domain models.
- **`the_duct_tape_ban` (`00-antigravity-core`):** Replacing the ad-hoc string concatenation (`+= " "`) with a deterministic, typed accumulator class.
- **`frozen_state_mutability` (`01-python-backend`):** `LLMNodeStrategy` recursively mutates objects in place via `_strip_heavy_keys`. This must be replaced with strict projection through a `Pydantic` filter (e.g. `FilterModel.model_validate(raw).model_dump(exclude_unset=True)`).

## 3. Implementation Phases

### Phase 1: Replacing `_strip_heavy_keys` with Pydantic Filtering
- **Target:** `_strip_heavy_keys` inside `execute`.
- **Action:** Delete the recursive dictionary mutation.
- **Reasoning:** In-place mutations of Any-typed dicts hide upstream schema drift and disable Rust validation.
- **Solution:** Define an `LLMContextFilter` Pydantic model with `@field_validator` hooks that explicitly drop `shuffled_atoms` and map `evaluations` into a flattened boolean list during the `.model_validate()` phase.

### Phase 2: Resolving Naked Dict Map-Reduce Aggregation
- **Target:** The `for t in tasks:` aggregator where map-reduce chunks are flattened into `final_dict`.
- **Action:** Purge the massive `isinstance(dict)` tree and string concatenations.
- **Reasoning:** Appending string traces with `+= ` inside dictionaries circumvents structural type-safety and crashes if the LLM output deviates from a string format.
- **Solution:** Create an `ExecutionChunk` model. Use an explicitly typed `ChunkAccumulator` service that natively knows how to merge XAI extensions using Python 3.10+ class mechanisms, rather than raw dictionary key-matching.

### Phase 3: Typing the Post-Hook State Boundary
- **Target:** `NodeStrategy.run_post_hooks` and `run_pre_hooks` in `base.py`.
- **Action:** Refactor `final_dict: dict[str, Any]` to `state_record: StatefulExecutionDTO`.
- **Reasoning:** The entire lifecycle guarantees state integrity EXCEPT where `LLMNodeStrategy` dumps a raw dictionary into the post-hooks.
- **Solution:** Wrap the Map-Reduce total output in a Pydantic record before sending it into the hook lifecycle.

### Phase 4: System Concurrency SSOT Enforcement
- **Target:** `LLMNodeStrategy.execute` map-reduce chunking loop.
- **Action:** Enforce strict adherence to `<rule_block id="system_concurrency_ssot">` from `05_llm_architecture.md`.
- **Solution:** While resolving chunking logic, verify that execution loops are strictly wrapped in `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)`. Absolutely no arbitrary or hardcoded API concurrency scaling is permitted.

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

### Specific Epic 32 Testing Mandates
1. Use `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py`
2. Write unit tests utilizing `backend_v2/llm/mock.py` to simulate fragmented chunking. Assert that the `ChunkAccumulator` exactly merges strings and matrix extensions without dropping data or triggering a Type error if encountering nested nodes.
3. Validate OpenAPI schemas via `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py --openapi`.
