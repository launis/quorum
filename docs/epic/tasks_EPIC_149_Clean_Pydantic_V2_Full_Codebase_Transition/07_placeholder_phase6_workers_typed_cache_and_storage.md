# Phase 6: Background Workers, Typed Cache Boundary & Storage

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
  <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
</required_context_rules>

**Phase Title:** Phase 6: Background Workers, Typed Cache Boundary & Storage
**Objective:** Eliminate dict mutations in `worker.py` metadata handling, integrate generic `TypedCacheService` / Inbound Cache Hydration Firewall with auto-eviction on `ValidationError`, lock `ExecutionRecord.profile_syntheses` as `dict[str, RenderedSynthesisCache]` with `model_validate_json()` hydration, and modernize worker unit tests atomically.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L307-L318] (Phase 6: Background Workers, Typed Cache Boundary & Storage)

**Target Files** (exhaustive — 2 production files + 6 test suites):
- `[MODIFY]` @[backend_v2/worker.py#L98-L103] (`VarianceExplanationResult`)
- `[MODIFY]` @[backend_v2/worker.py#L117-L438] (`execute_workflow_job`)
- `[MODIFY]` @[backend_v2/worker.py#L441-L463] (`generate_pdf_job`)
- `[MODIFY]` @[backend_v2/worker.py#L466-L581] (`generate_pdf_task`)
- `[MODIFY]` @[backend_v2/worker.py#L584-L606] (`render_profile_job`)
- `[MODIFY]` @[backend_v2/worker.py#L609-L1350] (`generate_profile_synthesis_and_pdf_task`)
- `[MODIFY]` @[backend_v2/worker.py#L1356-L1417] (`startup`)
- `[MODIFY]` @[backend_v2/worker.py#L1441-L1453] (`WorkerSettings`)
- `[NEW]` @[backend_v2/services/cache/__init__.py]
- `[NEW]` @[backend_v2/services/cache/typed_cache.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis_hydration.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_dlq_fallback.py]
- `[MODIFY]` @[backend_v2/tests/test_worker_models_used.py]
- `[NEW]` @[backend_v2/tests/unit/services/cache/test_typed_cache.py]

---

### Five-Axis Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Worker Core & Execution Trace Extraction**<br>`@[backend_v2/worker.py#L117-L438]` | Banned untyped dictionary mutations in `execution_summary`, `step_metrics`, and `models_used`. Banned `.get()` fallback chains and loose `dict` iteration. | Update `ExecutionMetadata` fields cleanly via `.model_copy(update={...})` with typed DTO payloads. Access `exec_record.target_locale` directly without fallback chains. Standardize `AppException` error codes across job handlers. | Eliminate manual dict mutation passes over execution traces in favor of structured event iteration. | `uv run python scripts/_ast_guardrails.py backend_v2/worker.py --strict` passes with 0 violations. |
| **Typed Cache Service & Inbound Firewall**<br>`[NEW] @[backend_v2/services/cache/typed_cache.py]`<br>`[NEW] @[backend_v2/services/cache/__init__.py]` | Banned raw `json.loads` calls and loose dictionary caching in Redis datastreams. Banned silent `except Exception: pass` when deserializing cached models. | Implement `TypedCacheService` with generic `get_cached[T: BaseModel](key: str, model_cls: type[T]) -> T \| None` using Rust-level `.model_validate_json()`. Automatically log RFC 7807 structured warning and delete corrupted cache entries on `ValidationError` (auto-eviction firewall). | Eliminate ad-hoc serialization helpers across worker tasks; consolidate all Redis model caching in one sovereign SSOT (~60 LOC). | `uv run pytest backend_v2/tests/unit/services/cache/test_typed_cache.py` passes 100%. |
| **Synthesis Hydration & Caching**<br>`@[backend_v2/worker.py#L609-L1350]` | Banned `.get()` fallback chains (`cv.get()`, `trace_evt.content.get()`, `_raw_row_explanations.get()`), and raw dict mutations of `profile_syntheses`. | Store and deserialize `ExecutionRecord.profile_syntheses` strictly as `dict[str, RenderedSynthesisCache]`. Use direct key checks (`in`) and structured `AppException` error codes. | Remove manual dictionary unpacking wrappers around `RenderedSynthesisCache`. | `uv run pytest backend_v2/tests/unit/test_worker_synthesis_hydration.py` passes 100%. |
| **PDF Generation Task & Rendering**<br>`@[backend_v2/worker.py#L466-L581]` | Banned loose `.get()` calls for locale and profile resolution. Banned silent exception swallowing during render updates. | Access `execution_record.target_locale` and `execution_record.output_profile_id` directly. Update step states using strictly typed `ExecutionStepState.model_copy(update={...})`. | Eliminate ad-hoc dictionary builders for step state updates. | `uv run pytest backend_v2/tests/unit/test_worker.py -k "test_generate_pdf"` passes 100%. |
| **Atomic Worker Test Suites & Modernization**<br>`@[backend_v2/tests/unit/test_worker.py]`<br>`@[backend_v2/tests/unit/test_worker_synthesis.py]`<br>`@[backend_v2/tests/unit/test_worker_dlq_fallback.py]`<br>`@[backend_v2/tests/test_worker_models_used.py]`<br>`@[backend_v2/tests/unit/test_worker_synthesis_hydration.py]` | Banned legacy test fixtures instantiating `ExecutionRecord` without mandatory `target_locale="fi"` and `metadata=ExecutionMetadata(target_locale="fi")`, and legacy `json.loads()` loop tests. | Modernize all test fixtures to pass `target_locale="fi"` and `metadata=ExecutionMetadata(target_locale="fi")`. Assert clean Pydantic V2 discriminated union and cache hydration. | Eliminate outdated dictionary mock fixtures and legacy parsing test fixtures. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_hydration.py backend_v2/tests/unit/test_worker_dlq_fallback.py backend_v2/tests/test_worker_models_used.py --test` passes >90% coverage. |

---

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-FLIGHT VERIFICATION">
    <action>Look backward: Verify codebase state left by Phase 5. Verify service layer is strictly typed and AST Guardrails scan on services/hooks has 0 unsuppressed violations.</action>
    <action>Look forward: Verify worker and cache drivers in @[backend_v2/worker.py] and [NEW] @[backend_v2/services/cache/typed_cache.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document (@[docs/epic/EPIC_149_tracker.md]), and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS &amp; LEGACY FIXTURE REMEDIATION">
    <action>Pre-emptively remediate discovered AST violations and modernize legacy test fixtures across worker test suites:
      1. In @[backend_v2/tests/unit/test_worker.py] and @[backend_v2/tests/unit/test_worker_synthesis.py]: update all `ExecutionRecord` fixture instantiations (including helper `_setup_mock_repo_for_metrics`) to pass mandatory `target_locale="fi"` and `metadata=ExecutionMetadata(target_locale="fi")`.
      2. In @[backend_v2/tests/test_worker_models_used.py]: update `ExecutionRecord` instantiation to pass `target_locale="fi"` and `metadata=ExecutionMetadata(target_locale="fi")`.
      3. In @[backend_v2/tests/unit/test_worker_synthesis_hydration.py]: eliminate duct-tape `json.loads()` loop test; assert clean Pydantic V2 discriminated union hydration and `RenderedSynthesisCache.model_validate()`.</action>
    <constraint invariant="the_duct_tape_ban">Eliminate legacy missing target_locale fixtures and json.loads() parsing loops.</constraint>
  </step>

  <step id="2" name="TYPED CACHE SERVICE IMPLEMENTATION">
    <action>Create [NEW] @[backend_v2/services/cache/__init__.py] and [NEW] @[backend_v2/services/cache/typed_cache.py]:
      1. Implement `TypedCacheService` class with explicit constructor accepting Redis connection/pool (`redis: Any | None = None`).
      2. Implement generic `async def get_cached[T: BaseModel](self, key: str, model_cls: type[T]) -> T | None`:
         - If Redis is absent, return `None`.
         - Fetch raw value via `await self.redis.get(key)`. If None, return `None`.
         - Parse and validate via Rust-level `model_cls.model_validate_json(raw_val)`.
         - On `ValidationError`: execute RFC 7807 structured `logger.warning("Corrupted cache payload encountered for key %s, auto-evicting", key, extra={"error_code": ErrorCodes.VALIDATION_FAILED.name})`, automatically purge via `await self.redis.delete(key)`, and return `None` (auto-eviction firewall).
      3. Implement `async def set_cached(self, key: str, model: BaseModel, expire_seconds: int | None = None) -> None`:
         - If Redis is absent, return.
         - Serialize via `model.model_dump_json()`.
         - Set key in Redis with optional `ex=expire_seconds`.
      4. Implement `async def delete(self, key: str) -> None`:
         - If Redis is absent, return.
         - Purge key via `await self.redis.delete(key)`.
      5. Create [NEW] @[backend_v2/tests/unit/services/cache/test_typed_cache.py] with unit tests covering cache hit, cache miss, `set_cached`, `delete`, and auto-eviction on `ValidationError`.</action>
    <constraint invariant="strict_pydantic_v2_rust">Use Rust-based model_validate_json() for high-throughput cache deserialization.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">Log structured warning with ErrorCodes on cache validation corruption before auto-eviction.</constraint>
  </step>

  <step id="3" name="WORKER METADATA &amp; TRACE METRIC REFACTORING">
    <action>Refactor @[backend_v2/worker.py#L117-L438] (`execute_workflow_job`):
      1. Modernize execution metadata handling: construct typed `execution_summary` and update `updated_exec_record.metadata` via `.model_copy(update={...})` ensuring all fields (`dag_cost_usd`, `prompt_tokens`, `completion_tokens`, `cached_tokens`, `reasoning_tokens`, `step_metrics`, `execution_summary`) strictly align with `ExecutionMetadata`.
      2. Eliminate loose dictionary mutations when parsing `execution_trace`: iterate over typed `TraceEvent` objects, inspect `event.content["_step_metadata"]` safely using `in` checks without `.get()` fallback chains.
      3. Ensure `exec_record.target_locale` is evaluated directly without fallback chaining.
      4. Standardize `AppException` error codes across job handlers.</action>
    <constraint invariant="zero_service_layer_fallbacks">Never use .get(key, default) or untyped dictionary mutation passes in worker execution.</constraint>
    <constraint invariant="frozen_state_mutability">Mutate ExecutionRecord and ExecutionMetadata via .model_copy(update={...}).</constraint>
  </step>

  <step id="4" name="WORKER PROFILE SYNTHESIS &amp; TYPED CACHE INTEGRATION">
    <action>Refactor @[backend_v2/worker.py#L466-L581] (`generate_pdf_task`) and @[backend_v2/worker.py#L609-L1350] (`generate_profile_synthesis_and_pdf_task`):
      1. In `generate_profile_synthesis_and_pdf_task`: deserialize `execution.profile_syntheses` strictly as `dict[str, RenderedSynthesisCache]` (using `RenderedSynthesisCache.model_validate()` when hydrating from raw DB payload).
      2. In starvation check: replace `trace_evt.content.get("event_type") == "starvation"` with direct key check `"event_type" in trace_evt.content and trace_evt.content["event_type"] == "starvation"`.
      3. In linguistics and performativity extraction: eliminate `.get()` calls on `cv` and `event.content` in favor of guarded key indexing.
      4. In row explanations caching: replace `_raw_row_explanations.get(alias_id)` with direct dictionary lookup guarded by `in`.
      5. In cache persistence: serialize `dict_syntheses = {k: v.model_dump(mode="json") for k, v in current_syntheses.items()}` and update execution record.
      6. In `generate_pdf_task`: ensure locale and profile resolution use typed model properties directly without `.get()` fallbacks.</action>
    <constraint invariant="no_naked_dicts_in_state">Intercept datastreams with model_validate() and serialize with model_dump(mode='json').</constraint>
    <constraint invariant="the_duct_tape_ban">Eliminate all .get(key, default) and silent exception handlers in worker tasks.</constraint>
  </step>

  <step id="5" name="ATOMIC WORKER TEST SUITE MODERNIZATION &amp; QUALITY GATES">
    <action>Run and modernize all worker unit test suites:
      1. Run `uv run pytest backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_dlq_fallback.py backend_v2/tests/unit/test_worker_synthesis_hydration.py backend_v2/tests/test_worker_models_used.py [NEW] backend_v2/tests/unit/services/cache/test_typed_cache.py`.
      2. Verify 100% test pass rate across all worker and cache tests.
      3. Run full backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/worker.py [NEW] backend_v2/services/cache/ backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_hydration.py backend_v2/tests/unit/test_worker_dlq_fallback.py backend_v2/tests/test_worker_models_used.py --test`.
      4. Run AST Guardrails scan: `uv run python scripts/_ast_guardrails.py backend_v2/worker.py [NEW] backend_v2/services/cache/ --strict`.
      5. Run SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Run full backend audit loop across worker, cache service, and all test suites.</constraint>
    <constraint invariant="anti_happy_path_mandate">Verify at least 2 negative test cases per worker job (cancellation, missing execution, validation error auto-eviction).</constraint>
  </step>

  <dod_checklist>
    - [x] `backend_v2/services/cache/typed_cache.py` created with generic `get_cached[T: BaseModel]` providing Rust-level `model_validate_json()` hydration and auto-eviction on `ValidationError`.
    - [x] `worker.py` refactored to eliminate dictionary mutations in execution metadata and trace metrics.
    - [x] `ExecutionRecord.profile_syntheses` deserialized cleanly as `dict[str, RenderedSynthesisCache]`.
    - [x] `test_worker_synthesis_hydration.py` modernized to eliminate `json.loads` fallback loops.
    - [x] All worker test suites (`test_worker.py`, `test_worker_synthesis.py`, `test_worker_dlq_fallback.py`, `test_worker_models_used.py`, `test_typed_cache.py`) passing 100%.
    - [x] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/worker.py [NEW] backend_v2/services/cache/ backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_hydration.py backend_v2/tests/unit/test_worker_dlq_fallback.py [NEW] backend_v2/tests/unit/services/cache/test_typed_cache.py --test`.
  </dod_checklist>

  <touched_artifacts>
    <backend>@[backend_v2/worker.py]</backend>
    <backend>[NEW] @[backend_v2/services/cache/typed_cache.py]</backend>
    <backend>[NEW] @[backend_v2/services/cache/__init__.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_dlq_fallback.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis_hydration.py]</backend>
    <backend>@[backend_v2/tests/test_worker_models_used.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/services/cache/test_typed_cache.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `scripts/_ast_guardrails.py` in Phase 6 (reserved for Phase 7).
    - Do NOT use standard `json.loads()` for cache and storage deserialization.
    - Do NOT re-introduce `.get()` fallback chains in worker routines.
  </anti_targets>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/worker.py [NEW] backend_v2/services/cache/ backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_hydration.py backend_v2/tests/unit/test_worker_dlq_fallback.py [NEW] backend_v2/tests/unit/services/cache/test_typed_cache.py --test
  </validation_gate>
</execution_protocol>
```
