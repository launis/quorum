> **STATUS: AUDITED & ENRICHED — PASS 21 (Tier 0 Research Plan, 21st Forensic Pass Complete — 100% Zero-Postponement, Flutter Analysis Options SSOT & Freezed Annotation Warning Eradication)**

# Automated Implementation Plan: ExecutionRecord Hardening & Technical Debt Resolution (Zero-Postponement Architecture)

> **SSOT Implementation Plan — ExecutionRecord Hardening & Stream Health**  
> **Objective:** Systematically resolve all architectural gaps, type weaknesses, and technical debt in `ExecutionRecord` across Flutter and Python with ZERO TASKS POSTPONED TO THE FUTURE: (1) Acknowledge that legacy `results` Map deprecation across `ExecutionRecord` and `execution_view.dart` is **ALREADY IMPLEMENTED**; (2) Replace remaining permissive `Map<String, dynamic>` fields with strongly typed Freezed sub-DTOs (`ExecutionSummarySnapshot`, `WorkflowInputs`, `FrozenContextSnapshot`) in Flutter; (3) Type `ExecutionStep.scorecardAtoms` as `Map<String, ScorecardAtomDto>` and `ExecutionRecord.stepStates` as `Map<String, ExecutionStep>`; (4) Refactor `ExecutionTimeline` from legacy `List<Map<String, dynamic>>` to typed `List<ExecutionStep>`, eliminating raw map indexing, hex colors, deprecated `primaryColor`, dead status strings (`'finished'`, `'completed'`, `'processing'`, `'error'`), and hardcoded strings, while enforcing `ki_desktop_pro_tool_studio_ux.md` title containment (`TextOverflow.ellipsis`) and tokenized theme styling; (5) Optimize backend SSE streaming polling by passing `hydrate=False` and `skip_resumability=True`, adding `sse_polling_interval_seconds: float = 2.0` and `sse_max_transient_retries: int = 3` to `settings.py`, and serializing with `model_dump_json(exclude_none=True)`; (6) Eradicate dead `ExecutionStatusCard` widget (241 lines) in Phase 1, eliminating `initialInputs: Map<String, dynamic>`; (7) Overthrow the obsolete "De-Generator Policy" in `ExecutionClient`, upgrading `startExecution`, `getExecutionStatus`, and `resumeExecution` from `Future<Map<String, dynamic>>` to `Future<ExecutionRecord>`, eradicating untyped string indexing in `ExecutionController`; (8) Eradicate permissive typing and `# noqa: QGR012` from `check_resumability` in `services/execution.py`; (9) Synchronize real-time per-step `progress` in `dag_executor.py` (`progress_callback` and completion), immediately activating the timeline's `LinearProgressIndicator` in real-time; (10) Synchronize `worker.py#L360-L397` step telemetry rebuild and fallback step construction (`#L351-L359`) with `progress: actual_progress` and `has_warning: actual_warning` so DAG completion does not wipe runtime step progress; (11) Align `FrozenContextSnapshot` with multi-payload parity (declaring both `versionId` and backend `FrozenContext` fields `compiledPrompts`, `injectedTheory`, `generatedSchemas`, `uiHintsSnapshot`, `mcpToolAudit` with `@Default` annotations) to prevent `CheckedFromJsonException` during direct REST calls; (12) Enforce strict PEP 593 `Annotated` syntax on `v2_core.py#L1608-L1639` per `pydantic_annotated_fields_mandate`; (13) Update `report_controller_test.dart#L40-L50` mock signatures to return typed `ExecutionRecord` fixtures, resolving Dart type errors; (14) Update `test_execution.py#L1117` `mock_get_exec` signature to accept `hydrate` and `skip_resumability` keyword arguments; (15) Verify native `hydrate: bool = True` repository parameter in `execution.py#L174` for zero-change repository delegation; (16) Isolate initial SSE connection authorization (full `hydrate=True, skip_resumability=False`) from lightweight polling (`hydrate=False, skip_resumability=True`); (17) Enforce 3-method typed parity on `MockExecutionClient` in `execution_controller_test.dart#L10-L75` (`startExecution`, `resumeExecution`, `getExecutionStatus`); (18) Migrate `execution_models_test.dart#L92-L115` test group in-place from obsolete `ExecutionInputs` to `WorkflowInputs`; (19) Synchronize `worker.py#L351-L359` fallback step construction to include `progress=v.progress, has_warning=v.has_warning`; (20) Modernize deprecated `Theme.of(context).primaryColor` to `Theme.of(context).colorScheme.primary` across `execution_timeline.dart#L44, #L91`; (21) Target `MockExecutionClientPending` with exact AST class precision in `report_controller_test.dart#L8, #L40-L50`; (22) Validate `SseClient#L67-L73` delta signal `frozen_context` isolation parity; (23) Verify native `hydrate: bool = True` in-memory repository fakes (`in_memory_repositories.py#L165, #L1291`); (24) Identify harmless dead `getScorecard` mock method across test clients; (25) Enforce `ki_desktop_pro_tool_studio_ux.md` desktop ergonomics (title containment, tokenized theme parity, serialization-based `@Freezed(equal: false)` state management); (26) Verify `IExecutionRepository` interface native `hydrate: bool = True` parameter in `database/interfaces.py#L89` for zero-change database contract compliance; (27) Verify `ExecutionStep.scorecardAtoms` zero-ripple UI invariant across `client_app_v2`; (28) Modernize stale De-Generator Policy docstring in `execution_record.dart#L16-L17`; (29) Formalize `SseClient` background isolate delta parsing parity; (30) Formalize complete elimination of `final frozenContext = record.frozenContext ?? {};` at `execution_view.dart#L105`; (31) Synchronize virtual system rendering step completion in `worker.py#L654-L659` with `progress: 100` alongside `status: ExecutionStatus.PASSED`; (32) Eradicate `isinstance(resolved_metadata, dict)` duck-typing and `# noqa: QGR012` from `create_execution_record` (`services/execution.py#L131-L137`) using `TypeAdapter(ExecutionMetadata)`; (33) Pass typed `versionId` directly to `AppLocalizations.of(context)!.auditDriftWarning(versionId)` in `execution_view.dart#L243-L245`, eradicating nested `?.toString() ?? ''` fallbacks; (34) Enforce `@JsonSerializable(disallowUnrecognizedKeys: true)` on `WorkflowInputs` to encapsulate dynamic inputs while strictly rejecting unrecognized top-level fields; (35) Formally audit all `# noqa: QGR012` suppressions in `services/execution.py`, documenting context variable dictionary handling at L1096 while resolving L136 and L675 in scope; (36) Add `steps: list[ExecutionStep] | None = None` to `ExecutionCommitter.commit_trace` and forward `steps=steps` to `ExecutionUpdateDTO` (`dag_executor.py#L87-L118`), pass `steps=current.steps` in intermediate `_safe_commit` (`#L632-L644`), and pass `steps=exec_record.steps` in final exit commits (`#L1000, #L1014, #L1035, #L1059`), ensuring database persistence of steps throughout DAG execution; (37) Synchronize `new_steps` in `dag_executor.py` across ALL state transitions inside `_update_lock`: cascading dependency failure (`#L658-L662`), queued (`#L702-L704`), running (`#L716-L720`), step exception catch (`#L904-L913`), virtual RAG preflight step (`#L934-L940, #L972-L980, #L984-L988`), and ExceptionGroup cancellation (`#L1027-L1033`), guaranteeing that `exec_record.steps` remains 1:1 synchronized with `step_states` at every instant; (38) Synchronize virtual report render step telemetry across its full lifecycle in `worker.py`: initialize `sys_render_{profile_id}` with `progress=0, has_warning=False` (`#L436-L445, #L813-L821`), update with `progress: 100, status: ExecutionStatus.PASSED` on success (`#L654-L659`), and update with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True` on render failure (`#L695-L705`); (39) Eradicate lazy fallback `or` in `create_execution_record` (`services/execution.py#L131-L135`), replacing `(extra_persistence_fields.pop("metadata", None) or ExecutionMetadata())` with strict explicit None checks and `TypeAdapter(ExecutionMetadata)`; (40) Modernize legacy Finnish status strings in `worker.py#L827, #L983, #L1810` to English (`"Calculating dynamic results..."`, `"Generating AI synthesis..."`, `"Compiling output documents..."`) per `english_language_mandate`; (41) Synchronize synthesis task error handler in `worker.py#L1854-L1864` with `progress: None, has_warning: True` across both `step_states` and `steps`; (42) Add explicit `if steps is not None: update_data["steps"] = steps` guard in `ExecutionCommitter.commit_trace` (`dag_executor.py#L110-L117`) to prevent accidental `null` overwrites of persisted steps during partial commits; (43) Synchronize `exec_record.steps` during resumability preflight reset (`dag_executor.py#L618-L627`) to reset failed steps to `PENDING` across both collections; (44) Append and synchronize virtual RAG preflight step (`sys.rag.preflight`) in `exec_record.steps` (`#L934-L988`) with full `progress: 100` on pass and `progress: None, has_warning: True` on failure; (45) Synchronize `exec_record.steps` during `ExceptionGroup` cancellation (`#L1026-L1034`), marking running steps as `FAILED` with `has_warning: True`; (46) Initialize `ExecutionStep` with explicit `progress=0, has_warning=False` in initial render status updates (`worker.py#L810-L825`); (47) Synchronize RAG preflight real-time progress emission (`_emit_preflight_progress`) in `dag_executor.py#L943-L962` to update `progress: pct` and `label: f"system.rag.preflight: {message}"` across both `step_states` and `steps` alongside `exec_record.progress = pct` and `exec_record.status_message = f"Preflight: {message}"`; (48) Enforce canonical virtual system step prefix `sys_rag_` on RAG preflight step ID (`dag_executor.py#L932`) and update `check_resumability` (`services/execution.py#L667`) to exclude all `sys_*` virtual steps from step set parity checks; (49) Synchronize unexpected non-ExceptionGroup exception handling in `dag_executor.py#L1054-L1066` to mark all in-flight `RUNNING` steps as `FAILED` with `has_warning: True` across both `step_states` and `steps` and pass `steps=exec_record.steps` to `commit_trace()`; (50) Modernize the fourth hardcoded Finnish status message at `worker.py#L889` (`"Koostetaan tulosteita valmiiksi..."` -> `"Compiling output documents..."`) and logger at line 597 (`"Koonti"` -> `"assembly"`); (51) Explicitly import `TypeAdapter` from `pydantic` in `services/execution.py#L16` (`from pydantic import TypeAdapter, ValidationError`); (52) Decouple transient retry backoff at `services/execution.py#L311` from `settings.llm_retry_delay` to `settings.sse_polling_interval_seconds`; (53) Encapsulate execution context variables in `override_atom` (`services/execution.py#L1096`) into typed `EvaluatedMatrixContextDTO` per `ki_zero_permissive_typing.md`, eradicating `isinstance(v, dict)` and `# noqa: QGR012`; (54) Refactor `resolve_dot_notation` in `backend_v2/utils/math_utils.py#L186-L222` from generic duck-typing reflection to a strongly typed Pydantic path resolver, eliminating `isinstance(curr, dict)`, `getattr(curr, part)`, and `# noqa: QGR012` and `# noqa: QGR001` suppressions; and (55) Create `client_app_v2/analysis_options.yaml` configuring `invalid_annotation_target: ignore`, permanently eliminating `// ignore_for_file: invalid_annotation_target` suppressions across all Freezed models in Flutter.

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
</required_context_rules>

<anti_targets>
- Do NOT loosen `@JsonSerializable(disallowUnrecognizedKeys: true)` or add permissive `@Default(null)` / `@Default({})` to mask serialization errors (`the_zero_compromise_pledge`).
- Do NOT invent parallel DTOs or diverge field naming between Python `snake_case` and Flutter `camelCase` (`anti_semantic_drift_renaming`).
- Do NOT alter `ReportDataDto.results` (which is the active `List<AtomResultDTO>`); the legacy `ExecutionRecord.results` Map is already removed (`ssot_reuse_mandate`).
- Do NOT bypass quality gates (`flutter_audit_loop.py --build` and `backend_audit_loop.py --test`).
- Do NOT alter presentation models in `ReportDataDto` or attempt to re-introduce SDUI rendering into `ExecutionStep`.
</anti_targets>

---

## 1. Problem Statement & Architecture Audit

1. **Audit of Completed vs Pending Work (`Status Audit`):**
   - **ALREADY IMPLEMENTED:** The legacy `results` Map has already been completely removed from both backend `ExecutionRecord` (`backend_v2/models/v2_core.py#L1703-L1778`) and Flutter `ExecutionRecord` (`client_app_v2/lib/features/execution/models/execution_record.dart#L18-L89`). Furthermore, `execution_view.dart#L21-L309` and `execution_status_card.dart#L1-L241` already delegate presentation strictly to `ReportDataDto` and `ReportRendererV2Widget`.
   - **PENDING IMPLEMENTATION:**
     - Flutter `ExecutionRecord` still retains permissive untyped `Map<String, dynamic>?` fields for `execution_summary`, `raw_inputs`, and `models_used`.
     - Flutter `ExecutionStep.scorecardAtoms` is still typed as `Map<String, dynamic>` despite `ScorecardAtomDto` already being fully available in `matrix_scorecard_dto.dart#L62-L86`.
     - `ExecutionTimeline` (`client_app_v2/lib/shared/widgets/execution_timeline.dart#L4-L206`) remains an un-modernized legacy component accepting `List<Map<String, dynamic>> steps`, using dynamic dictionary indexing, fallback strings (`?? 'Tuntematon askel'`), literal hex colors (`Color(0xFF2E7D32)`), and `SizedBox(0, 0)`.
     - `execution_view.dart#L107-L110` extracts `stepStatesList` from `record.stepStates` via dynamic map casting to pass to `ExecutionTimeline`, bypassing the authoritative typed `record.steps: List<ExecutionStep>`.
     - Backend SSE polling in `backend_v2/services/execution.py#L267-L332` calls `get_execution` without `hydrate=False`, causing eager un-needed hydration of multi-megabyte `frozen_context` and `execution_trace` blob files on every 1-second polling pulse.
     - `client_app_v2/test/features/execution/models/execution_models_test.dart#L301-L317` contains an obsolete test fixture with invalid keys (`total_steps`, `completed_steps`) that will fail fast once `ExecutionSummarySnapshot` is strictly typed.

   - **TIER 0 PASS 2 — ADDITIONAL DISCOVERIES:**
      - **DISCOVERY A (Field Gap — `progress` and `has_warning` NOT on `ExecutionStep`):** The `execution_timeline.dart#L53-L55` widget reads `step['progress']` (for rendering `LinearProgressIndicator`) and `step['has_warning'] == true || step['has_warnings'] == true` (for rendering warning amber icon). Neither `progress` nor `has_warning`/`has_warnings` exists on the typed Flutter `ExecutionStep` model (`execution_step.dart#L8-L37`) nor on the backend `ExecutionStep` (`backend_v2/models/v2_core.py#L1608-L1639`). Currently these values come from the untyped `step_states: Map<String, dynamic>?` dictionary on `ExecutionRecord`, NOT from the typed `steps: List<ExecutionStep>` field. **ROOT CAUSE:** The `step_states` dictionary is a parallel denormalized data source carrying SSE-era runtime fields that were never formalized into the typed `ExecutionStep` schema. **IMPACT:** Simply swapping `List<Map<String, dynamic>>` for `List<ExecutionStep>` will silently lose the progress bar and warning icon rendering unless `progress` and `has_warning` fields are first added to `ExecutionStep` in both backend and Flutter models.
      - **DISCOVERY B (Dead `# noqa: E501` Already Cleaned):** Physical `grep_search` on `backend_v2/tests/unit/services/test_execution.py` and `backend_v2/tests/unit/test_executions.py` returned ZERO `# noqa` matches. The dead suppressions described in Section 4.1 (Juurisyy 1) have ALREADY been cleaned in a prior commit. Step 1.3 in Phase 1 is therefore pre-completed and MUST be marked as `[x] ALREADY DONE` during execution.
      - **DISCOVERY C (Redundant `check_resumability` in SSE Loop):** `stream_status` (L291) calls `self.get_execution(initiator, execution_id)` which internally invokes `await self.check_resumability(data)` on every 1-second polling pulse. The `is_resumable` projection is unnecessary during high-frequency status streaming and adds a redundant database/state query per pulse.
      - **DISCOVERY D (Obsolete `execution_inputs.dart` Deletion Missing):** The plan correctly identifies that `WorkflowInputs` replaces the obsolete `ExecutionInputs` model, but does NOT explicitly include a `[DELETE]` directive for `@[client_app_v2/lib/features/execution/models/execution_inputs.dart]` and its generated `.freezed.dart` / `.g.dart` files.
      - **DISCOVERY E (Additional Naked Dict Tech Debt in `execution_view.dart#L217-L244`):** `frozenContext['version_id']` and `frozenContext.containsKey('version_id')` use naked dictionary key indexing on `Map<String, dynamic>? frozenContext` with lazy fallback `?? ''`. This is out-of-scope for the current plan (correctly placed in `<anti_targets>`) but constitutes documented technical debt for a future Epic targeting `frozenContext` typing.

   - **TIER 0 PASS 3 — ADDITIONAL DISCOVERIES:**
      - **DISCOVERY F (Dead Rendering Paths — `progress` and `has_warning` Never Existed on `ExecutionStep`):** Physical inspection of backend `ExecutionStep` (`@[backend_v2/models/v2_core.py#L1608-L1639]`, 16 fields) confirms NEITHER `progress` NOR `has_warning` exists on this model. `progress` is an `ExecutionRecord`-level field inherited via `ExecutionCoreFields` (`@[backend_v2/models/execution_core.py#L97-L100]`), and the DAG executor (`@[backend_v2/services/orchestrator/dag_executor.py#L744]`) writes `progress` to `ExecutionRecord.progress`, NOT to individual `step_states[step_id].progress`. `has_warning` exists exclusively on `ReportDataDto` in the blueprint/report domain (`@[backend_v2/models/v2_core.py#L949]`, `@[backend_v2/services/blueprint.py#L213-L236]`), NEVER on any step-level model or DAG executor output. **CONSEQUENCE:** The `execution_timeline.dart#L53` (`step['progress'] as num?`) and `#L54-L55` (`step['has_warning'] == true || step['has_warnings'] == true`) reads from `step_states` values have ALWAYS returned null — the progress bar (`LinearProgressIndicator`) and warning amber icon are **dead rendering paths** that have never executed in production. **RESOLUTION:** The plan's approach of adding `progress` and `has_warning` as typed fields on `ExecutionStep` (Step 1.0) is correct as a **schema formalization** — the fields will have defaults (`None` and `False`) matching current null behavior, and they will render correctly once a future DAG executor enhancement populates per-step progress. This is schema preparation, NOT a functional change to currently-visible rendering.
      - **DISCOVERY G (`WorkflowInputs.dynamic_inputs` Legitimacy — `dict[str, Any]` Exception):** The backend `WorkflowInputs` (`@[backend_v2/models/domain/inputs.py#L52-L54]`) defines `dynamic_inputs: Annotated[dict[str, Any], Field(...)] = Field(default_factory=dict)`. This is a **legitimate** `dict[str, Any]` because workflow dynamic inputs are user-configured in Studio UI at runtime, making strict typing mathematically impossible for this container. The Flutter parity DTO MUST preserve `@Default({}) Map<String, dynamic> dynamicInputs` — this is NOT a zero-permissive-typing violation but a recognized dynamic-input encapsulation boundary per `@[ki_zero_permissive_typing.md]` `dynamic_workflow_input_encapsulation` mandate.
      - **DISCOVERY H (Backend `step_states` Is Typed `dict[str, ExecutionStep]`):** Physical inspection confirms backend `ExecutionRecord.step_states` (`@[backend_v2/models/v2_core.py#L1736-L1738]`) is typed as `dict[str, ExecutionStepState]` where `ExecutionStepState = ExecutionStep` (`@[backend_v2/models/v2_core.py#L1641]`). The Flutter client's `Map<String, dynamic>? stepStates` is merely a serialization artifact — backend values are strictly typed `ExecutionStep` objects. This confirms that `step['progress']` and `step['has_warning']` are dead accesses since `ExecutionStep` has never carried those fields.
      - **DISCOVERY I (Backend `models_used` Is `dict[str, int]`, NOT `dict[str, Any]`):** Physical inspection confirms backend `ExecutionRecord.models_used` (`@[backend_v2/models/v2_core.py#L1762-L1764]`) is typed as `dict[str, int]`. The plan's proposal to update Flutter's `Map<String, dynamic>? modelsUsed` to `Map<String, int>?` is verified as 1:1 parity-correct.
      - **DISCOVERY J (`SizedBox(0, 0)` Guard Redundancy in `ExecutionTimeline`):** The `SizedBox(width: 0, height: 0)` return at `execution_timeline.dart#L17` for empty `steps` is ALREADY guarded by the caller at `execution_view.dart#L286` (`if (stepStatesList.isNotEmpty)`). After refactoring to `record.steps`, the caller guard becomes `if (record.steps.isNotEmpty)`, making the internal empty-check redundant. The empty-check can be retained as a defensive widget-level contract (widgets should be self-contained), but the `SizedBox(width: 0, height: 0)` violates the `sized_box_shrink_ban` rule. Replace with `return const SizedBox.shrink();` — this is NOT hiding a broken component but handling a legitimately empty list state, which is the widget's own input contract.
      - **DISCOVERY K (Existing `get_execution_status` Repository Method):** The execution repository (`@[backend_v2/database/repositories/execution.py#L210]`) already has `get_execution_status(execution_id) -> str | None` — a lightweight status-only query. The current `stream_status` calls the full `get_execution` (which hydrates the entire record). While the plan's `hydrate=False` + `skip_resumability` approach correctly avoids blob deserialization and redundant resumability checks, a FURTHER future optimization could replace the full `get_execution(..., hydrate=False)` with `get_execution_status()` for the terminal-state polling check (`if record.status in [PASSED, FAILED]: break`), only calling `get_execution(hydrate=False)` for the SSE data payload. This is OUT OF SCOPE for the current plan but documented as a potential future performance enhancement.

   - **TIER 0 PASS 4 — ADDITIONAL DISCOVERIES:**
      - **DISCOVERY L (SSE Polling Interval is 10 Seconds, NOT 1 Second):** Physical inspection of `@[backend_v2/settings.py#L309]` confirms `llm_retry_delay: Annotated[float, Field(description="Delay between retries in seconds")] = 10.0`. The SSE `stream_status` loop at `@[backend_v2/services/execution.py#L300]` calls `await asyncio.sleep(settings.llm_retry_delay)`, producing a **10-second** polling interval — NOT "1-second" as stated in earlier discovery text (Discoveries C, F, H and multiple 5-Column Table constraint descriptions). While 10 seconds is less frequent than 1 second, the `hydrate=False` optimization remains architecturally correct: each poll still triggers a full `_hydrate_payloads()` reading multi-megabyte blob files from disk/cloud storage, which is unnecessary overhead at any frequency. **CLARIFICATION:** All references to "1-second polling pulse" in this plan should be read as "10-second polling pulse" (governed by `settings.llm_retry_delay`).
      - **DISCOVERY M (`max_retries = 3` Magic Number in SSE Loop — `strict_configuration_segregation` Violation):** At `@[backend_v2/services/execution.py#L286]`, `max_retries = 3` is hardcoded directly in the `stream_status` method body. Per the `strict_configuration_segregation` mandate, all global limits and bounds MUST reference `settings.py` SSOT. This magic number should be extracted to `settings.sse_max_transient_retries` or equivalent. **SCOPE:** This is DOCUMENTED TECH DEBT — adding a new settings field is a drive-by schema mutation out-of-scope for this plan, but the executing agent MUST document it as technical debt in the atomic commit.
      - **DISCOVERY N (`llm_retry_delay` Semantic Mismatch for SSE Polling Interval):** The SSE polling loop at `@[backend_v2/services/execution.py#L300, #L311]` reuses `settings.llm_retry_delay` as its sleep interval. This field is semantically an LLM retry backoff delay, NOT an SSE polling interval. SSE status streaming and LLM transient retry backoff are architecturally distinct concerns and should eventually have separate settings fields (e.g. `settings.sse_polling_interval_seconds`). **SCOPE:** OUT OF SCOPE for this plan — documented as future tech debt.
      - **DISCOVERY O (`const` Keyword Breaking Change in Timeline Refactor):** At `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L180-L184]`, the completed step icon is rendered as `const Icon(Icons.check_circle, color: const Color(0xFF2E7D32), size: 20)`. When replacing `const Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primary`, the entire `const Icon(...)` constructor becomes non-const because `Theme.of(context)` is NOT a const expression. The executing agent MUST remove the `const` keyword from the `Icon(...)` constructor at L180. This is NOT an error — it is an expected consequence of replacing a compile-time literal color with a runtime theme token.
      - **DISCOVERY P (`model_dump_json()` Without `exclude_none=True` in SSE Payload):** At `@[backend_v2/services/execution.py#L295]`, `record.model_dump_json()` serializes the ENTIRE `ExecutionRecord` without `exclude_none=True`. This produces unnecessarily large SSE payloads containing numerous `"field": null` entries across all nullable fields. The `trace_serialization_hygiene_mandate` (`@[.agents/rules/01-python-backend.md]` rule `trace_serialization_hygiene_mandate`) mandates `exclude_none=True` for execution trace serialization, but SSE payloads are API transit payloads, not trace events — so the rule does not strictly apply here. However, adding `exclude_none=True` to the SSE `model_dump_json()` call would reduce payload size and is a natural enhancement alongside the `hydrate=False` optimization. **SCOPE:** OUT OF SCOPE for this plan — the Flutter `ExecutionRecord` model uses nullable fields with `?` syntax and Dart JSON deserialization handles absent keys with `@Default(...)` or `?` nullability, so omitting null fields would be safe. Documented as a complementary future performance enhancement.
      - **DISCOVERY Q (CORRECTED — `check_resumability` + `hydrate=False` Is a Performance Optimization, NOT a Correctness Requirement):** ~~Original Pass 4 analysis stated `check_resumability` inspects `record.execution_trace` to verify checkpoint events, making `skip_resumability=True` a correctness requirement.~~ **PASS 5 PHYSICAL CORRECTION (2026-09-18):** Forensic re-inspection of `check_resumability` at `@[backend_v2/services/execution.py#L632-L692]` reveals that the `execution_trace` checkpoint inspection ("Rule 2: Duck-Typing check") has been **REMOVED** (comment at L652-654: `# Rule 2: Removed Duck-Typing check. Executions that crash before their first 'output' checkpoint MUST be resumable.`). The current `check_resumability` performs 4 checks: (1) `record.status != FAILED`, (2) workflow blueprint `step_states` parity via `workflow_repo.get_workflow_by_id()`, (3) workflow version drift via `record.metadata.workflow_version`, (4) FinOps quota via `usage_service.check_quota(org_id)`. **NONE of these require `execution_trace` hydration** — `step_states` is inline database data (NOT an offloaded blob), and workflow/quota checks are independent DB/service queries. **CORRECTED CONSEQUENCE:** `skip_resumability=True` coupled with `hydrate=False` is a **PERFORMANCE optimization** that eliminates 2 unnecessary per-pulse operations during SSE streaming: (a) `workflow_repo.get_workflow_by_id()` database query, and (b) `usage_service.check_quota(org_id)` service call. The SSE streaming client does NOT consume the `is_resumable` flag during active streaming, making these per-pulse queries purely wasteful. The two parameters remain **strongly recommended together** but are NOT an inseparable correctness invariant.

   - **TIER 0 PASS 5 — ADDITIONAL DISCOVERIES:**
      - **DISCOVERY R (`check_resumability` Permissive Typing Violations at L675-L680 — OUT OF SCOPE):** Physical inspection of `check_resumability` at `@[backend_v2/services/execution.py#L675-L680]` reveals permissive typing violations: `isinstance(record.metadata, dict)` (banned by `QGR012`), `.get("workflow_version")` (banned by `pure_dot_notation_and_anti_reflection`), and `isinstance(raw_v, str)` coercion chain. Currently guarded with `# noqa: QGR012 [REASON: Polymorphic DAG payload validation]`. Since `record.metadata` is typed as `ExecutionMetadata | None` on `ExecutionRecord` (L1768), the `isinstance(dict)` branch should theoretically be unreachable for validated Pydantic models. **SCOPE:** OUT OF SCOPE — documented as tech debt requiring a targeted hardening pass on `check_resumability` internal logic.
      - **DISCOVERY S (Flutter `ExecutionRecord.executionTrace` Naked Dict Violation — OUT OF SCOPE):** At `@[client_app_v2/lib/features/execution/models/execution_record.dart#L54]`, `executionTrace` is typed as `List<Map<String, dynamic>>?` — a naked dictionary collection violating the zero-permissive-typing mandate. Typing execution trace events as Freezed models (`TraceEvent`, `TombstoneEvent`) is a separate epic-scale task. **SCOPE:** OUT OF SCOPE — documented as future zero-permissive-typing tech debt.
      - **DISCOVERY T (Undocumented `'processing'` Status String Literal in Timeline — Tech Debt):** At `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L66, #L111]`, `stepStatus == 'processing'` checks against a string literal that is NOT present in the `ExecutionStatus` enum (which contains: PENDING, QUEUED, RUNNING, PASSED, FAILED). This code path is NEVER reached via the typed `ExecutionStep.status` field. After the Step 1.1 refactoring (switching from `step['status']` to `step.status`), this branch REMAINS as dead code since `ExecutionStep.status` is populated from backend `ExecutionStatus` enum which lacks `processing`. **SCOPE:** IN SCOPE — the executing agent MUST document this as a dead code path in a code comment but MUST NOT remove it during this plan (removal requires verifying all SSE message codes). The refactored typed access will NOT change behavior since `step.status` will never equal `'processing'`.
      - **DISCOVERY U (Component A L135 Wording Contradiction — `frozenContext` Is NOT Dead):** The Component A description at L135 states "Eliminate dead variable assignment `final frozenContext = record.frozenContext ?? {};` at L105" — but `frozenContext` IS actively consumed at `execution_view.dart#L217-L244` for the version drift warning banner. The Execution Protocol Step 1.2 correctly says "NOTE: `final frozenContext = record.frozenContext ?? {};` at L105 is NOT removed" — but the high-level Component A description uses contradictory "Eliminate" wording. **RESOLUTION:** Corrected in this pass to read "RETAIN (out-of-scope tech debt)" instead of "Eliminate".
      - **DISCOVERY V (Step 5.2 `git add` Missing Backend Model File):** Step 5.2 at L429 stages `backend_v2/services/execution.py` and `backend_v2/tests/unit/services/test_execution.py` but DOES NOT include `backend_v2/models/v2_core.py`, which is modified in Step 1.0 (adding `progress` and `has_warning` fields to `ExecutionStep`). **RESOLUTION:** Corrected in this pass to include `backend_v2/models/v2_core.py` in the `git add` command.

   - **TIER 0 PASS 6 — ADDITIONAL DISCOVERIES:**
      - **DISCOVERY W (Ghost Reference — `step['chunk_count']` NOT Used in `ExecutionTimeline`):** Physical `grep_search` on `@[client_app_v2/lib/shared/widgets/execution_timeline.dart]` for `chunk_count` returned ZERO matches. The plan's Component A (L139) and Execution Protocol Step 1.1 action 5 incorrectly list `step['chunk_count']` as a naked dictionary lookup to be eradicated. `chunk_count` IS a valid field on `ExecutionStep` (accessible via `step.chunkCount` after refactoring) but it is NOT currently accessed anywhere in the timeline widget. **RESOLUTION:** Corrected in this pass — `step['chunk_count']` is removed from the refactoring instructions in Component A and Step 1.1 to prevent the executing agent from searching for a non-existent reference.
      - **DISCOVERY X (Dead Status String Variants — `'finished'`, `'completed'`, `'error'` in Timeline):** At `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L34-L40]`, the widget checks `stepStatus == 'passed' || stepStatus == 'finished' || stepStatus == 'completed'` for completed steps and `stepStatus == 'failed' || stepStatus == 'error'` for failed steps. The backend `ExecutionStatus` enum contains strictly: PENDING, QUEUED, RUNNING, PASSED, FAILED. The `'finished'`, `'completed'`, and `'error'` string variants are dead code paths — they match status values that the backend NEVER emits. Similar to Discovery T (`'processing'`), after refactoring to typed `step.status`, these branches will NEVER match since `ExecutionStep.status` is populated from the backend enum. **SCOPE:** IN SCOPE — the executing agent MUST annotate these dead branches with `// TODO(tech-debt): Dead status variant — backend ExecutionStatus enum only emits PENDING, QUEUED, RUNNING, PASSED, FAILED` comments alongside the Discovery T `'processing'` annotations during Step 1.1 refactoring. They MUST NOT be removed without verifying all SSE message code emission paths.
      - **DISCOVERY Y (Test File Imports `execution_inputs.dart` — Step 1.4 Prerequisite):** At `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L3]`, the test file imports `package:client_app/features/execution/models/execution_inputs.dart`. Step 1.4 instructs `grep_search` on `client_app_v2/lib/` only — this scope would MISS the test import. The executing agent MUST expand the `grep_search` scope to `client_app_v2/` (both `lib/` and `test/`) and MUST update the test file import to reference `WorkflowInputs` BEFORE deleting the model file. **RESOLUTION:** Corrected in this pass — Step 1.4 action 1 scope expanded to `client_app_v2/` and action added for test import migration.
      - **DISCOVERY Z (RESOLVED & BROUGHT IN-SCOPE IN PASS 7 — `ExecutionStatusCard.initialInputs` Naked Dict & Dead Code Deletion):** In Pass 6, `ExecutionStatusCard.initialInputs` was noted as an out-of-scope permissive typing violation. Forensic investigation in Pass 7 confirmed that `ExecutionStatusCard` (`@[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart#L1-L241]`, 241 lines) is **100% DEAD CODE** with ZERO callers and ZERO test imports across the entire repository. It was superseded by `DynamicStartScreen` and `ExecutionView`. Rather than being left as tech debt, it is BROUGHT IN SCOPE for complete deletion in Phase 1 Step 1.5, directly eradicating `Map<String, dynamic> initialInputs`.
      - **DISCOVERY AA (Execution Protocol Step Ordering Validation — CONFIRMED SOUND):** The Phase ordering (Phase 3: modify Dart source types → Phase 4 Step 4.1: build_runner regeneration → Phase 4 Step 4.2: test fixture sync → Phase 5: quality gate) is verified as logically sound. The test fixture with invalid `{'total_steps': 5, 'completed_steps': 2}` at `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L311]` will fail-fast with `CheckedFromJsonException` ONLY when tests are executed (Phase 5 quality gate). Step 4.2 updates the fixture BEFORE the quality gate runs, so no intermediate breakage occurs.

   - **TIER 0 PASS 7 — ADDITIONAL DISCOVERIES:**
      - **DISCOVERY BB (Dead Code — `ExecutionStatusCard` 100% Unreferenced):** Physical `grep_search` across `client_app_v2/` confirmed zero usages of `ExecutionStatusCard`. The entire file at `@[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart]` (241 lines) is completely obsolete. Deleting it in Phase 1 Step 1.5 eliminates an obsolete parallel view architecture and removes a major source of naked dictionary transit without requiring any caller migration.
      - **DISCOVERY CC (Obsolete "De-Generator Policy" in `ExecutionClient` & End-to-End Type Safety):** Physical inspection of `@[client_app_v2/lib/core/api/execution_client.dart#L16-L17]` revealed the docstring proclaiming: `"Adheres to the De-Generator Policy: Returns raw JSON maps instead of generated Dart models to allow maximum flexibility for SDUI responses."` This policy is an obsolete anti-pattern directly violating `the_zero_compromise_pledge`, `zero_service_layer_fallbacks`, and `ki_zero_permissive_typing.md`. `startExecution()`, `getExecutionStatus()`, and `resumeExecution()` DO NOT return SDUI; they return the `ExecutionRecord` domain entity. Returning `Map<String, dynamic>` forces `ExecutionController` (`execution_controller.dart#L83-L88`, `#L124-L127`) and `NewExecutionController` (`new_execution_view.dart#L62-L68`) to execute naked string indexing `initialRecord['id'] as String` and manually run `ExecutionRecord.fromJson()`. In Phase 3 Step 3.4, `ExecutionClient` methods are hardened to return `Future<ExecutionRecord>` directly (`response.data as Map<String, dynamic>` deserialized immediately in the client), and callers consume typed dot-notation (`record.id`).
      - **DISCOVERY DD (Test Suite Mock ExecutionClient Parity for Typed Methods):** In `@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L12]` and `@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L40]`, mock/fake `ExecutionClient` instances implement `startExecution`, `resumeExecution`, and `getExecutionStatus` returning `Future<Map<String, dynamic>>`. When `ExecutionClient` return types are updated to `Future<ExecutionRecord>`, these mock implementations MUST be synchronously updated in Step 4.2 to return `Future<ExecutionRecord>`, maintaining 100% compilation and test suite parity.

   - **TIER 0 PASS 8 — ZERO-POSTPONEMENT & ALL-IN-SCOPE HARDENING DISCOVERIES:**
      - **DISCOVERY EE (RESOLVED IN-SCOPE — `FrozenContextSnapshot` Freezed DTO & Typed Drift Warning):** In Pass 2/3/4/5/6/7, `frozenContext['version_id']` was documented as out-of-scope technical debt. Forensic audit confirms that `execution_view.dart#L217-L244` and `sse_client.dart#L70-L72` access `frozenContext['version_id']` using untyped dictionary indexing with lazy fallback `?? ''`. Rather than deferring this to a future Epic, it is **BROUGHT FULLY IN-SCOPE**: create [NEW] `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]` with Freezed property `@JsonKey(name: 'version_id') String? versionId`, type `ExecutionRecord.frozenContext` as `FrozenContextSnapshot?`, and refactor `execution_view.dart` to consume typed `record.frozenContext?.versionId` via typed dot-notation. This permanently eliminates `Map<String, dynamic>? frozenContext` from `ExecutionRecord` and eradicates all dictionary duck-typing from `execution_view.dart`.
      - **DISCOVERY FF (RESOLVED IN-SCOPE — Flutter `ExecutionRecord.stepStates` Parity Typing):** Physical inspection of backend `ExecutionRecord.step_states` (`@[backend_v2/models/v2_core.py#L1736-L1738]`) confirms it is typed as `dict[str, ExecutionStepState]` where `ExecutionStepState = ExecutionStep`. In Flutter, `ExecutionRecord.stepStates` remained untyped as `Map<String, dynamic>?`. In Pass 8, this is **BROUGHT FULLY IN-SCOPE**: update `ExecutionRecord.stepStates` to `@JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates`, achieving 100% 1:1 cross-domain semantic and serialization parity with the backend.
      - **DISCOVERY GG (RESOLVED IN-SCOPE — Real-Time Per-Step `progress` in DAG Executor):** In Pass 3 Discovery F, per-step progress was marked as inactive because `dag_executor.py` wrote progress only to `ExecutionRecord.progress`. Forensic investigation of `@[backend_v2/services/orchestrator/dag_executor.py#L728-L755]` reveals that `progress_callback` ALREADY computes `prog` (0-100) per step and has `step_id` in scope! It was updating `label` on `exec_record.step_states[step_id]` but omitting `progress` because `progress` was not on `ExecutionStep`. In Pass 8, this is **BROUGHT FULLY IN-SCOPE**: in `dag_executor.py#L741-L745`, update `new_state = exec_record.step_states[step_id].model_copy(update={"label": label, "progress": prog})`, update `exec_record.steps` concurrently, and set `progress: 100` on step completion (`dag_executor.py#L869-L873`). The Flutter `ExecutionTimeline`'s `LinearProgressIndicator` immediately springs to life in real-time with ZERO tasks postponed to the future.
      - **DISCOVERY HH (RESOLVED IN-SCOPE — Settings-Driven SSE Polling & Retry Isolation):** In Pass 4 Discoveries M and N, `max_retries = 3` and `settings.llm_retry_delay = 10.0` were noted as technical debt. In Pass 8, this is **BROUGHT FULLY IN-SCOPE**: add two typed settings to `@[backend_v2/settings.py]`: (1) `sse_max_transient_retries: Annotated[int, Field(default=3, ge=1, le=10, description="Max transient retry attempts during SSE polling")] = 3`, and (2) `sse_polling_interval_seconds: Annotated[float, Field(default=2.0, gt=0.0, le=30.0, description="Polling interval in seconds for SSE status stream")] = 2.0`. In `backend_v2/services/execution.py#L286, #L300`, bind directly to these typed settings. Eliminates magic numbers and slashes UI status polling latency from 10 seconds to a snappy 2 seconds!
      - **DISCOVERY II (RESOLVED IN-SCOPE — `model_dump_json(exclude_none=True)` SSE Payload Hygiene):** In Pass 4 Discovery P, omitting `exclude_none=True` was documented as potential future optimization. In Pass 8, this is **BROUGHT FULLY IN-SCOPE**: in `@[backend_v2/services/execution.py#L295]`, update to `yield f"data: {record.model_dump_json(exclude_none=True)}\n\n"`. Strips null fields, cutting SSE bandwidth and enforcing clean payload hygiene.
      - **DISCOVERY JJ (RESOLVED IN-SCOPE — `check_resumability` Permissive Typing & `# noqa: QGR012` Eradication):** In Pass 5 Discovery R, `isinstance(record.metadata, dict)` and `.get("workflow_version")` were documented as out-of-scope debt. In Pass 8, this is **BROUGHT FULLY IN-SCOPE**: in `@[backend_v2/services/execution.py#L671-L682]`, eliminate the dict duck-typing branch and remove `# noqa: QGR012`. Replace with strictly typed dot-notation across `record.metadata.workflow_version` and `record.workflow_version`.
      - **DISCOVERY KK (RESOLVED IN-SCOPE — Timeline Status Enum Parity & Dead String Removal):** In Pass 5/6 Discoveries T and X, dead status strings (`'finished'`, `'completed'`, `'processing'`, `'error'`) were annotated as TODO comments. In Pass 8, this is **BROUGHT FULLY IN-SCOPE**: in `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L34-L40, #L66, #L111]`, standardize status evaluations strictly against canonical `ExecutionStatus` enum values (`stepStatus == 'passed'`, `stepStatus == 'failed' || stepStatus == 'system_error'`, `stepStatus == 'running'`, `stepStatus == 'queued'`, `stepStatus == 'pending'`). Eradicates all dead status strings.

   - **TIER 0 PASS 9 — ZERO-POSTPONEMENT & MATHEMATICAL COMPLETENESS DISCOVERIES:**
      - **DISCOVERY LL (RESOLVED IN-SCOPE — `worker.py#L360-L397` Step Telemetry Rebuild Wipes `progress` and `has_warning`):** In `@[backend_v2/worker.py#L344-L397]`, when the DAG terminates, `worker.py` rebuilds `updated_steps` from `updated_exec_record.steps` and `step_telemetry`. It copies `status`, `last_error`, `message_code`, `scorecard_atoms`, tokens, and cost, but OMITTED `progress` and `has_warning`. If not copied from `st_state` (`actual_progress = st_state.progress`, `actual_warning = st_state.has_warning`), the final step states saved to the database on DAG completion would have `progress` reset to `None` and `has_warning` reset to `False`! In Phase 1 Step 1.6, `worker.py#L360-L397` is **BROUGHT FULLY IN-SCOPE**: update `worker.py` to preserve `progress: actual_progress` and `has_warning: actual_warning` alongside `dag_executor.py#L740-L755, #L869-L875`.
      - **DISCOVERY MM (RESOLVED IN-SCOPE — `FrozenContextSnapshot` Multi-Payload Parity Across REST & SSE):** Backend `@[backend_v2/models/v2_core.py#L1548-L1562]` defines `FrozenContext` with `compiled_prompts`, `injected_theory`, `generated_schemas`, `ui_hints_snapshot`, and `mcp_tool_audit`. In direct REST calls (`startExecution`, `getExecutionStatus`), the backend returns this full structure. If `FrozenContextSnapshot` has `@JsonSerializable(disallowUnrecognizedKeys: true)` but only declares `version_id`, `ExecutionRecord.fromJson()` in `ExecutionClient` will crash with `CheckedFromJsonException` for unrecognized keys (`compiled_prompts`, etc.)! In Pass 9, this is **BROUGHT FULLY IN-SCOPE**: `FrozenContextSnapshot` MUST include both the metadata fields (`versionId`, `workflowId`, `workflowName`, `organizationId`, `userId`, `createdAt`) AND the backend fields (`compiledPrompts`, `injectedTheory`, `generatedSchemas`, `uiHintsSnapshot`, `mcpToolAudit`) with `@Default({})` / `@Default([])` annotations, ensuring seamless deserialization for both SSE delta payloads (`{'version_id': ...}`) and REST payloads.
      - **DISCOVERY NN (RESOLVED IN-SCOPE — `test_execution.py#L1117` `mock_get_exec` Keyword Arguments Mismatch):** In `@[backend_v2/tests/unit/services/test_execution.py#L1117]`, `mock_get_exec(initiator: Any, execution_id: str) -> Any:` replaces `service.get_execution` in `test_stream_status_handles_error_without_yielding_malformed_execution_record`. When `stream_status` is updated to call `get_execution(..., hydrate=False, skip_resumability=True)`, calling `mock_get_exec` with keyword arguments will raise `TypeError: mock_get_exec() got an unexpected keyword argument 'hydrate'`. In Pass 9, this is **BROUGHT FULLY IN-SCOPE**: update `mock_get_exec` to accept `hydrate: bool = True, skip_resumability: bool = False, **kwargs: Any` in Step 4.2.
      - **DISCOVERY OO (RESOLVED IN-SCOPE — PEP 593 `Annotated` Syntax Invariant on `v2_core.py` `ExecutionStep`):** Rule `pydantic_annotated_fields_mandate` (`01-python-backend.md`) strictly mandates `Annotated[T, Field(...)]` for all Pydantic fields. In Step 1.0, the field additions to `ExecutionStep` must strictly use:
        `progress: Annotated[int | None, Field(default=None, ge=0, le=100, description="Step progress percentage for SSE streaming (0-100)")] = None`
        `has_warning: Annotated[bool, Field(default=False, description="Whether the step completed with warnings")] = False`
      - **DISCOVERY PP (RESOLVED IN-SCOPE — `report_controller_test.dart#L40-L50` Mock Return Parity):** In `@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L40-L50]`, `MockExecutionClient` implements `startExecution`, `resumeExecution`, and `getExecutionStatus` returning `{}` (empty map). When `ExecutionClient` return types are updated to `Future<ExecutionRecord>`, returning `{}` causes a compile-time type error in Dart. In Pass 9, this is **BROUGHT FULLY IN-SCOPE**: update these mock methods in Step 4.2 to return typed `ExecutionRecord` fixtures.
      - **DISCOVERY QQ (RESOLVED IN-SCOPE — `execution_models_test.dart#L211` Fixture Alignment with `FrozenContextSnapshot`):** In `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L211]`, the fixture contains `'frozen_context': <String, dynamic>{'input': 'content'}`. If `FrozenContextSnapshot` enforces `@JsonSerializable(disallowUnrecognizedKeys: true)`, `'input'` is an unrecognized key that will throw `CheckedFromJsonException`. In Pass 9, this is **BROUGHT FULLY IN-SCOPE**: update the fixture in Step 4.2 to use valid fields (`{'version_id': 'v2.0.0'}`).

   - **TIER 0 PASS 10 — COMPREHENSIVE REPOSITORY PARITY & CALLER AUDIT DISCOVERIES:**
      - **DISCOVERY RR (RESOLVED IN-SCOPE — Native `hydrate=True` Parameter in `ExecutionRepository`):** Physical inspection of `@[backend_v2/database/repositories/execution.py#L174]` confirms that `exec_repo.get_execution(execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:` ALREADY natively defines `hydrate: bool = True` and conditionally executes `await self._hydrate_payloads(data)` (L190-L191). In `backend_v2/services/execution.py#L253`, the existing call is `data = await self.exec_repo.get_execution(execution_id)` (omitting the argument, defaulting to True). Updating `ExecutionService.get_execution(..., hydrate=True)` to delegate `await self.exec_repo.get_execution(execution_id, hydrate=hydrate)` requires ZERO repository-level schema or driver changes — it connects directly to the repository's native capability.
      - **DISCOVERY SS (RESOLVED IN-SCOPE — Initial SSE Connection Full Handshake Isolation):** In `@[backend_v2/services/execution.py#L282]`, `stream_status` executes an initial authorization check: `await self.get_execution(initiator=initiator, execution_id=execution_id)`. Because this initial call uses default `hydrate=True, skip_resumability=False`, it validates tenant permissions, checks resumability, and verifies blob payload health before entering the loop. Inside the loop at L291, subsequent polls execute `await self.get_execution(initiator=initiator, execution_id=execution_id, hydrate=False, skip_resumability=True)`. This cleanly decouples the heavy one-time connection handshake from lightweight, high-frequency status streaming.
      - **DISCOVERY TT (RESOLVED IN-SCOPE — `execution_controller_test.dart#L10-L75` Three Mock Client Method Updates):** Physical inspection of `@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L10-L75]` reveals that `MockExecutionClient` implements `startExecution` (L12-L21), `resumeExecution` (L24-L31), and `getExecutionStatus` (L55-L62) returning untyped `Map<String, dynamic>`. In Step 4.2, all three mock methods MUST be updated to return typed `ExecutionRecord` fixtures, guaranteeing 100% test compilation and execution parity.
      - **DISCOVERY UU (RESOLVED IN-SCOPE — `execution_models_test.dart#L92-L115` In-Place Migration to `WorkflowInputs Freezed Parity`):** Physical `grep_search` confirmed that `execution_inputs.dart` is not imported by any production widget or controller in `client_app_v2/lib/` — its sole repository usage is in `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L3, #L92-L115]`. Migrating this test group in-place to `WorkflowInputs Freezed Parity` (testing positive deserialization of `organizationId`, `userId`, `simulationMode`, `language`, and `dynamicInputs`, as well as defaults) provides immediate ISTQB coverage for the new DTO and allows `execution_inputs.dart` and its generated files to be deleted with ZERO broken references across the entire codebase.
      - **DISCOVERY VV (RESOLVED IN-SCOPE — `worker.py#L351-L359` Fallback Step Construction Progress & Warning Preservation):** In `@[backend_v2/worker.py#L351-L359]`, when `updated_exec_record.steps` is empty, fallback `ExecutionStep` instances are constructed from `updated_exec_record.step_states.items()`. This fallback constructor must explicitly include `progress=v.progress, has_warning=v.has_warning` alongside `id=k, label=v.label, status=v.status, scorecard_atoms=v.scorecard_atoms`, ensuring that fallback step synthesis never drops real-time step progress or warnings.
      - **DISCOVERY WW (RESOLVED IN-SCOPE — `execution_timeline.dart#L44, #L91` Deprecated Theme Property `primaryColor` Modernization):** In `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L44, #L91]`, the widget references `Theme.of(context).primaryColor`. In Flutter 3+, `primaryColor` is deprecated in favor of `Theme.of(context).colorScheme.primary`. Alongside eliminating literal hex colors (`Color(0xFF2E7D32)`), modernizing these two references to `Theme.of(context).colorScheme.primary` ensures full compliance with Flutter desktop theme invariants.

   - **TIER 0 PASS 11 — MOCK PRECISION, DELTA ISOLATION & IN-MEMORY REPOSITORY DISCOVERIES:**
      - **DISCOVERY XX (RESOLVED IN-SCOPE — `MockExecutionClientPending` Class Name Precision in `report_controller_test.dart#L8`):** Physical inspection of `@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L8]` revealed that the mock class implementing `ExecutionClient` is explicitly named `MockExecutionClientPending`, NOT `MockExecutionClient`. In Pass 9 Discovery PP, this class was colloquially referenced as `MockExecutionClient`. Documenting the exact AST identifier `MockExecutionClientPending` eliminates any ambiguity when updating mock method return signatures (`startExecution`, `resumeExecution`, `getExecutionStatus`) to `Future<ExecutionRecord>` in Step 4.2.
      - **DISCOVERY YY (RESOLVED IN-SCOPE — Dead `getScorecard` Test Mock Method Identification):** Physical inspection of both `MockExecutionClientPending` (`@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L51]`) and `MockExecutionClient` (`@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L64]`) revealed an un-annotated `Future<Map<String, dynamic>> getScorecard(String executionId) async => {};` method. Cross-referencing `@[client_app_v2/lib/core/api/execution_client.dart#L18-L78]` confirmed that `ExecutionClient` does NOT define `getScorecard` (only `startExecution`, `resumeExecution`, `getExecutionStatus`, `renderExecution`, and `overrideAtom`). While harmless, this confirms `getScorecard` is legacy dead test code that does not impede type modernization.
      - **DISCOVERY ZZ (RESOLVED IN-SCOPE — `SseClient.dart#L67-L73` Delta Signal `frozen_context` Isolation Parity):** Forensic inspection of `@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]` confirmed that `SseClient` actively transforms `raw['frozen_context']` into `{'version_id': fc['version_id']}` if `version_id` is present, or `null` otherwise. This explains why `execution_view.dart` received a single-key map `{'version_id': 'v2.0.0'}` during SSE streaming, while direct REST calls (`startExecution`, `getExecutionStatus`) receive the full backend `FrozenContext` payload (`compiled_prompts`, `injected_theory`, `generated_schemas`, etc.). This forensic proof validates `FrozenContextSnapshot`'s multi-payload design: declaring `@JsonKey(name: 'version_id') String? versionId` alongside backend fields with `@Default` annotations guarantees 100% deserialization parity across both SSE delta signals and full REST payloads under strict `@JsonSerializable(disallowUnrecognizedKeys: true)`.
      - **DISCOVERY AAA (RESOLVED IN-SCOPE — `backend_v2/tests/fakes/in_memory_repositories.py#L165, #L1291` Native `hydrate` Parameter Parity):** Physical inspection of `@[backend_v2/tests/fakes/in_memory_repositories.py#L165, #L1291]` confirmed that `InMemoryExecutionRepository.get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:` and `UnifiedInMemoryRepository.get_execution` ALREADY natively accept `hydrate: bool = True`. This guarantees that unit tests using in-memory fake repositories will pass without requiring any method signature additions to test fakes when `ExecutionService.get_execution` forwards `hydrate=hydrate`.

   - **TIER 0 PASS 12 — DESKTOP PRO TOOL STUDIO UX & ERGONOMICS PARITY (ki_desktop_pro_tool_studio_ux.md):**
      - **DISCOVERY BBB (RESOLVED IN-SCOPE — Desktop Pro Tool Studio UX & Title Containment Parity per `ki_desktop_pro_tool_studio_ux.md`):** Cross-referencing `@[ki_desktop_pro_tool_studio_ux.md]` (`cognitive_ergonomics_and_dual_pane_standard` & `real_time_inline_validation_and_feedback`) confirms essential desktop invariants for `ExecutionTimeline` and `ExecutionView`: (1) Title Containment: `step.label` in `execution_timeline.dart#L134-L142` MUST enforce `overflow: TextOverflow.ellipsis` to prevent RenderFlex horizontal overflows when desktop windows are resized below 900px; (2) Theme Token Exclusivity: eradicate all hex color literals (`Color(0xFF2E7D32)`) and deprecated `primaryColor` in favor of canonical `Theme.of(context).colorScheme` tokens (`colorScheme.primary`, `colorScheme.error`, `colorScheme.onSurfaceVariant`); (3) Zero Hardcoded Fallbacks: eradicate `'Tuntematon askel'` (which violated both the English codebase mandate and localization SSOT) in favor of the strictly typed `step.label` domain property; and (4) Serialization-Based Dirty State Compatibility: all `@Freezed(equal: false)` entities (`ExecutionRecord`, `ExecutionStep`) conform to serialization-based equality checking (`uncommitted_state_loss_prevention_mandate`) across parent dialogs and controllers.

   - **TIER 0 PASS 13 — MULTI-PAYLOAD PARITY, ROUTER INVARIANTS & CALLER SCOPE AUDIT:**
      - **DISCOVERY CCC (RESOLVED IN-SCOPE — `SseClient` Delta Signal Deserialization Lifecycle & `FrozenContextSnapshot` Multi-Payload Parity Validation):** Forensic cross-examination of `@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]` confirmed that `SseClient` receives raw SSE chunks (`dataStr`), decodes them in a background isolate (`safeIsolateRun`), and transforms `raw['frozen_context']` into a delta payload: `if (raw.containsKey('frozen_context')) { final fc = raw['frozen_context']; result['frozen_context'] = (fc is Map && fc.containsKey('version_id')) ? {'version_id': fc['version_id']} : null; }`. Then, `execution_controller.dart#L267` executes `ExecutionRecord.fromJson(update)`. When `update['frozen_context']` contains only `{'version_id': ...}`, the `FrozenContextSnapshot` DTO parses cleanly because all other fields (`compiledPrompts`, `injectedTheory`, `generatedSchemas`, `uiHintsSnapshot`, `mcpToolAudit`) have `@Default` annotations. Conversely, during direct REST calls (`startExecution`, `getExecutionStatus`), the backend returns the full `FrozenContext` structure (`compiled_prompts`, `injected_theory`, etc.). Because `FrozenContextSnapshot` declares BOTH the metadata fields (`versionId`, etc.) and the backend fields with `@Default` annotations, `ExecutionRecord.fromJson()` succeeds seamlessly in both execution paths under `@JsonSerializable(disallowUnrecognizedKeys: true)`.
      - **DISCOVERY DDD (RESOLVED IN-SCOPE — `ExecutionService.get_execution` Default Parameter Safety & Router Non-Regression):** Verification of `@[backend_v2/api/routers/execution/executions.py#L96]` and all internal callers confirmed that `get_execution(initiator, execution_id, hydrate=True, skip_resumability=False)` defaults preserve 100% backward compatibility for all API routes, internal service methods, and test fixtures without changing their signatures or behavior.
      - **DISCOVERY EEE (RESOLVED IN-SCOPE — Exact AST Verification of `ExecutionTimeline` Callers):** Physical `grep_search` confirmed `ExecutionTimeline` has exactly ONE production caller across the entire repository (`@[client_app_v2/lib/features/execution/views/execution_view.dart#L293]`). Modifying `ExecutionTimeline(steps: record.steps, compact: false)` has zero ripple effects outside `execution_view.dart`.
      - **DISCOVERY FFF (RESOLVED IN-SCOPE — Exact AST Verification of `ExecutionClient` Mock Interfaces):** Physical `grep_search` across `client_app_v2/` confirmed that only TWO test classes implement `ExecutionClient`: `MockExecutionClient` (`@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L10]`) and `MockExecutionClientPending` (`@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L8]`). Both are already explicitly updated in Step 4.2 to return `Future<ExecutionRecord>`, guaranteeing 100% compilation safety without un-mocked method errors.
      - **DISCOVERY GGG (RESOLVED IN-SCOPE — Elimination of Dead Status Strings from `ExecutionTimeline`):** In `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L34-L40, #L66, #L111]`, status branches for `'finished'`, `'completed'`, `'processing'`, and `'error'` are dead code paths because backend `ExecutionStatus` strictly emits `PENDING`, `QUEUED`, `RUNNING`, `PASSED`, `FAILED`. The plan consolidates these branches to evaluate strictly against canonical values (`stepStatus == 'passed'`, `stepStatus == 'failed' || stepStatus == 'system_error'`, `stepStatus == 'running'`, `stepStatus == 'queued' || stepStatus == 'pending'`).

   - **TIER 0 PASS 14 — ZERO-POSTPONEMENT, CONTRACT PARITY & REPOSITORY INVARIANT DISCOVERIES:**
      - **DISCOVERY HHH (RESOLVED IN-SCOPE — `IExecutionRepository` Interface Native `hydrate=True` Contract Parity):** Physical inspection of `@[backend_v2/database/interfaces.py#L89]` confirms that `IExecutionRepository.get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None: ...` ALREADY natively specifies `hydrate: bool = True` in the abstract contract. Coupled with the concrete MongoDB/TinyDB implementation at `@[backend_v2/database/repositories/execution.py#L174]` (Discovery RR) and in-memory test fakes at `@[backend_v2/tests/fakes/in_memory_repositories.py#L165, #L1291]` (Discovery AAA), this confirms 100% contract and implementation parity across the entire persistence layer. Forwarding `hydrate=hydrate` from `ExecutionService.get_execution` to `exec_repo.get_execution` requires ZERO changes to interfaces, drivers, or fakes.
      - **DISCOVERY III (RESOLVED IN-SCOPE — `ScorecardAtomDto` Zero-Ripple UI Invariant in `client_app_v2`):** Physical `grep_search` across `client_app_v2/` confirmed that `ExecutionStep.scorecardAtoms` has ZERO manual dictionary indexing or caller dependencies in UI widgets. Updating `scorecardAtoms` from `Map<String, dynamic>` to `Map<String, ScorecardAtomDto>` on `ExecutionStep` (`execution_step.dart#L31`) elevates compile-time type safety with zero breaking caller changes and zero ripple effects on existing UI screens.
      - **DISCOVERY JJJ (RESOLVED IN-SCOPE — Modernization of Stale De-Generator Policy Docstring in `execution_record.dart#L16-L17`):** Physical inspection of `@[client_app_v2/lib/features/execution/models/execution_record.dart#L16-L17]` revealed a stale docstring comment referencing: `"Follows The De-Generator Mandate: Replaces the old dynamic 'results' map"`. In Step 3.3, this comment is modernized to reference pure typed Freezed DTO architecture.
      - **DISCOVERY KKK (RESOLVED IN-SCOPE — `SseClient` Background Isolate Delta Transformation Verification):** Forensic audit of `@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]` and `@[client_app_v2/test/core/api/sse_client_test.dart#L30-L93]` confirmed that the background isolate delta transform strips extraneous snapshot data and yields `{'version_id': fc['version_id']}`. Because `FrozenContextSnapshot` declares `@JsonKey(name: 'version_id') String? versionId` alongside backend fields with `@Default` annotations, `ExecutionRecord.fromJson(update)` passes both unit test execution and real-world streaming with zero exceptions.
      - **DISCOVERY KKK (RESOLVED IN-SCOPE — `SseClient` Background Isolate Delta Parsing Verification):** Forensic audit of `@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]` and `@[client_app_v2/test/core/api/sse_client_test.dart#L30-L93]` confirmed that the background isolate delta transform strips extraneous snapshot data and yields `{'version_id': fc['version_id']}`. Because `FrozenContextSnapshot` declares `@JsonKey(name: 'version_id') String? versionId` alongside backend fields with `@Default` annotations, `ExecutionRecord.fromJson(update)` passes both unit test execution and real-world streaming with zero exceptions.
      - **DISCOVERY LLL (RESOLVED IN-SCOPE — Elimination of Unused `final frozenContext = record.frozenContext ?? {};` at `execution_view.dart#L105`):** Physical audit of `@[client_app_v2/lib/features/execution/views/execution_view.dart]` confirmed that `frozenContext` was accessed ONLY in the Version Drift Warning Banner (L217-L244). By refactoring L217-L244 to directly access typed `record.frozenContext?.versionId` (`final versionId = record.frozenContext?.versionId; if (versionId != null && versionId.isNotEmpty && versionId != 'v2.0.0') ...`), the local variable `final frozenContext = record.frozenContext ?? {};` at L105 becomes 100% unused and is completely deleted in Step 1.2, permanently eradicating dynamic map lookups from `execution_view.dart`.

   - **TIER 0 PASS 15 — TELEMETRY SYNCHRONIZATION, FACTORY HARDENING & LOCALIZATION PARAMETER SAFETY DISCOVERIES:**
      - **DISCOVERY MMM (RESOLVED IN-SCOPE — Virtual System Render Step Telemetry Invariants in `worker.py#L436-L445, #L654-L659, #L813-L821`):** Physical inspection of `@[backend_v2/worker.py]` revealed that when DAG execution finishes and output report rendering begins, `worker.py` dynamically injects a virtual report generation step `v_step_id = f"sys_render_{profile_id}"` into both `steps` and `step_states` (L436-L445 & L813-L821) with `status=ExecutionStatus.RUNNING`. When rendering completes successfully at L654-L659, `worker.py` updates `new_step = old_state.model_copy(update={"status": ExecutionStatus.PASSED})`, but omits `progress: 100`. In Step 1.6, `worker.py#L654-L659` is enriched to explicitly set `progress: 100` alongside `status: ExecutionStatus.PASSED` for both `step_states` and `steps`, guaranteeing that virtual rendering steps transition cleanly to 100% progress without remaining stranded at in-flight percentages or null.
      - **DISCOVERY NNN (RESOLVED IN-SCOPE — `create_execution_record#L131-L137` Duck-Typing Elimination via TypeAdapter):** Physical inspection of `@[backend_v2/services/execution.py#L131-L137]` revealed another occurrence of `# noqa: QGR012 [REASON: Polymorphic DAG payload validation]` alongside `if isinstance(resolved_metadata, dict): resolved_metadata = ExecutionMetadata(**resolved_metadata)`. While Step 2.2 hardens `check_resumability` (L675), `create_execution_record` (L136) also relied on duck-typing. In Step 2.2, `create_execution_record#L131-L137` is refactored to use `TypeAdapter(ExecutionMetadata).validate_python(resolved_metadata) if resolved_metadata is not None else ExecutionMetadata()`, completely eradicating `isinstance(resolved_metadata, dict)` and deleting `# noqa: QGR012` from the factory boundary.
      - **DISCOVERY OOO (RESOLVED IN-SCOPE — `execution_view.dart#L243-L245` `auditDriftWarning` Localization Parameter Safety):** In `@[client_app_v2/lib/features/execution/views/execution_view.dart#L243-L245]`, the code calls `AppLocalizations.of(context)!.auditDriftWarning((frozenContext['version_id']?.toString() ?? ''))`. By refactoring the enclosing banner to bind `final versionId = record.frozenContext?.versionId; if (versionId != null && versionId.isNotEmpty && versionId != 'v2.0.0')`, the localization parameter is passed directly as `AppLocalizations.of(context)!.auditDriftWarning(versionId)`, completely eliminating the nested `?.toString() ?? ''` fallback chain while guaranteeing 100% compile-time type safety and contract integrity with the `.arb` template.
      - **DISCOVERY PPP (RESOLVED IN-SCOPE — Freezed `@JsonSerializable(disallowUnrecognizedKeys: true)` on `WorkflowInputs`):** In `WorkflowInputs` (`@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`), `dynamic_inputs` is annotated with `@JsonKey(name: 'dynamic_inputs') @Default({}) Map<String, dynamic> dynamicInputs`. Enforcing `@JsonSerializable(disallowUnrecognizedKeys: true)` on `WorkflowInputs` safely encapsulates dynamic execution inputs while strictly rejecting unrecognized top-level fields per `ki_zero_permissive_typing.md` (`dynamic_workflow_input_encapsulation`).
      - **DISCOVERY QQQ (RESOLVED IN-SCOPE — Complete File Deletion Verification of `execution_status_card.dart`):** Physical `grep_search` confirmed `execution_status_card.dart` is an isolated 241-line dead file with zero callers across `client_app_v2/` (both `lib/` and `test/`). Its physical deletion in Step 1.5 permanently eliminates `initialInputs: Map<String, dynamic>` with zero broken imports.
      - **DISCOVERY RRR (AUDITED IN-SCOPE — `services/execution.py#L1096` Context Variables Permissive Typing Audit):** Physical audit of all `# noqa: QGR012` suppressions in `@[backend_v2/services/execution.py]` identified that besides L136 (resolved in Discovery NNN) and L675 (resolved in Discovery JJ), exactly one other `# noqa: QGR012` exists at L1096 (`if isinstance(v, dict) and "evaluated_atoms" in v:` in `override_atom`). This check traverses `record.context_variables`, which is a dynamic dictionary container. It is documented as technical debt for future context variable encapsulation, while all execution record metadata and resumability duck-typing is 100% resolved in active scope.

   - **TIER 0 PASS 16 — INTERMEDIATE STEPS PERSISTENCE, FULL DAG STATE SYNCHRONIZATION & FACTORY FALLBACK ERADICATION DISCOVERIES:**
      - **DISCOVERY SSS (RESOLVED IN-SCOPE — `ExecutionCommitter.commit_trace` & `_safe_commit` Omitted `steps` in `dag_executor.py#L87-L118, #L632-L644, #L1000, #L1014, #L1035, #L1059`):** Forensic analysis of `@[backend_v2/services/orchestrator/dag_executor.py]` revealed a critical persistence bug: `ExecutionCommitter.commit_trace` (L87-L118) accepted `trace`, `status`, `step_states`, `error`, `frozen_context`, `context_variables`, but **OMITTED** `steps: list[ExecutionStep] | None = None`. Consequently, when it instantiated `ExecutionUpdateDTO`, it never populated `steps`. Furthermore, intermediate commits inside `_safe_commit()` (L632-L644) called `commit_trace()` with `step_states=current.step_states` but **OMITTED** `steps=current.steps`. All intermediate database writes during DAG execution saved `step_states` to the database while leaving `steps` untouched. Because `ExecutionTimeline` in Flutter is being refactored to consume `record.steps`, SSE streaming clients polling `get_execution(hydrate=False, skip_resumability=True)` would receive `record.steps` permanently stuck in their initial `PENDING` state until `worker.py` finished and performed a final persistence sweep. In Step 1.6, this is **BROUGHT FULLY IN-SCOPE**:
        1. In `dag_executor.py#L87-L118`, add `steps: list[ExecutionStep] | None = None` to `ExecutionCommitter.commit_trace()` and pass `steps=steps` into `ExecutionUpdateDTO(...)`.
        2. In `dag_executor.py#L632-L644`, update `_safe_commit()` to pass `steps=current.steps`.
        3. In exit commits at L1000, L1014, L1035, L1059, pass `steps=exec_record.steps`.
      - **DISCOVERY TTT (RESOLVED IN-SCOPE — Full-Lifecycle State Synchronization Across All `dag_executor.py` Transitions):** Forensic audit of `@[backend_v2/services/orchestrator/dag_executor.py]` revealed that step state transitions inside `async with _update_lock:` mutated only `step_states`, completely ignoring `exec_record.steps` in the following critical execution paths:
        1. Cascading dependency failure (L658-L662): only updated `step_states[step_id]` with `ExecutionStatus.FAILED`.
        2. Step queued (L702-L704): only updated `step_states[step_id]` with `ExecutionStatus.QUEUED`.
        3. Step running in `watch_running` (L716-L720): only updated `step_states[step_id]` with `ExecutionStatus.RUNNING`.
        4. Step exception catch (L904-L913): only updated `step_states[step_id]` with `ExecutionStatus.FAILED` and `last_error`.
        5. RAG Preflight virtual step (L934-L940, L972-L980, L984-L988): created `virtual_step_id` in `step_states` but never appended or updated it in `exec_record.steps`.
        6. `ExceptionGroup` cancellation (L1027-L1033): marked running steps as `FAILED` only in `step_states`.
        In Step 1.6, this is **BROUGHT FULLY IN-SCOPE**: across all 6 transition blocks, synchronize `new_steps = [s.model_copy(...) if s.id == step_id else s for s in exec_record.steps]` (or append virtual step if missing) and assign `"steps": new_steps` in `exec_record.model_copy()`, guaranteeing that `exec_record.steps` and `exec_record.step_states` remain mathematically identical at every micro-transition.
      - **DISCOVERY UUU (RESOLVED IN-SCOPE — Virtual Report Render Step Full-Lifecycle Telemetry in `worker.py#L436-L445, #L654-L659, #L695-L705, #L813-L821`):** In `@[backend_v2/worker.py]`, dynamically injected `sys_render_{profile_id}` steps must maintain complete telemetry integrity across their full lifecycle:
        1. Initialization (L436-L445 & L813-L821): initialize `ExecutionStep(id=v_step_id, label="Rendering Report", status=ExecutionStatus.RUNNING, progress=0, has_warning=False)`.
        2. Successful render (L654-L659): update both `step_states` and `steps` with `progress: 100, status: ExecutionStatus.PASSED`.
        3. Render failure catch (L695-L705): update both `step_states` and `steps` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True`.
        In Step 1.6, this is **BROUGHT FULLY IN-SCOPE**, guaranteeing that virtual report generation steps never crash the UI or remain stuck at `RUNNING` if a PDF compilation exception occurs.
      - **DISCOVERY VVV (RESOLVED IN-SCOPE — `create_execution_record#L131-L135` Lazy Fallback `or` Eradication):** In `@[backend_v2/services/execution.py#L131-L135]`, the code utilized a lazy fallback `or`:
        `raw_meta = metadata if metadata is not None else (extra_persistence_fields.pop("metadata", None) or ExecutionMetadata())`
        Using `or ExecutionMetadata()` masks empty dictionaries or falsey inputs through duck-typing and triggered the `# noqa: QGR012` suppression at L136. In Step 2.2, this is **BROUGHT FULLY IN-SCOPE**: replace with explicit None handling:
        ```python
        raw_meta = metadata if metadata is not None else extra_persistence_fields.pop("metadata", None)
        resolved_metadata = (
            TypeAdapter(ExecutionMetadata).validate_python(raw_meta)
            if raw_meta is not None
            else ExecutionMetadata()
        )
        ```
        permanently eliminating duck-typing, `# noqa: QGR012`, and the lazy fallback `or`.

    - **TIER 0 PASS 17 — BACKEND ENGLISH MODERNIZATION, SYNTHESIS ERROR TELEMETRY & COMMITTER GUARD DISCOVERIES:**
       - **DISCOVERY WWW (RESOLVED IN-SCOPE — Backend English Status Strings in `worker.py#L827, #L983, #L1810`):** In `@[backend_v2/worker.py#L827, #L983, #L1810]`, hardcoded Finnish status strings (`"Lasketaan dynaamisia tuloksia..."`, `"Generoidaan tekoälysynteesiä (tämä saattaa kestää verkosta riippuen)..."`, `"Koostetaan tulosteita valmiiksi..."`) directly violate `english_language_mandate` and `ki_dual_axis_localization_architecture.md`. Forensic `grep_search` confirmed zero tests in `backend_v2/tests/` and zero widgets in `client_app_v2/` depend on these Finnish literals. In Step 1.6, modernize these to concise, professional English: `"Calculating dynamic results..."` (L827), `"Generating AI synthesis..."` (L983), and `"Compiling output documents..."` (L1810).
       - **DISCOVERY XXX (RESOLVED IN-SCOPE — Synthesis Error Handler Virtual Step Telemetry in `worker.py#L1854-L1864`):** In `@[backend_v2/worker.py#L1854-L1864]` (`generate_profile_synthesis_and_pdf_task` error handler), `v_step_id` (`sys_render_{profile_id}`) is updated with `status: ExecutionStatus.FAILED, last_error: str(e)`, but omits `progress: None, has_warning: True`. In Step 1.6, enrich this update to explicitly set `progress: None, has_warning: True` across both `step_states` and `steps`, achieving 100% full-lifecycle telemetry parity with the PDF generation error handler (`#L695-L705`).
       - **DISCOVERY YYY (RESOLVED IN-SCOPE — `ExecutionCommitter.commit_trace` None Guard for `steps` Persistence):** In `@[backend_v2/services/orchestrator/dag_executor.py#L110-L117]`, `ExecutionUpdateDTO` is serialized via `model_dump(mode="json", exclude_unset=True)`. If `steps: list[ExecutionStep] | None = None` is explicitly passed as `None` to `ExecutionUpdateDTO(..., steps=steps)`, Pydantic records `steps` in `model_fields_set`, causing `exclude_unset=True` to include `"steps": null` and inadvertently overwrite previously persisted steps in the database with `null`! In Step 1.6, `ExecutionCommitter.commit_trace` MUST conditionally populate `"steps": steps` only `if steps is not None: update_data["steps"] = steps`, guaranteeing that partial commits omitting `steps` never wipe step history.
       - **DISCOVERY ZZZ (RESOLVED IN-SCOPE — Exact Line Precision for `ExecutionTimeline` Theme Tokens):** Forensic AST inspection of `@[client_app_v2/lib/shared/widgets/execution_timeline.dart]` verified exact line targets for desktop ergonomics and theme compliance per `ki_desktop_pro_tool_studio_ux.md`: (1) Line 44 (`labelColor = Theme.of(context).primaryColor;`) and Line 91 (`color: Theme.of(context).primaryColor,`) modernize to `Theme.of(context).colorScheme.primary`; (2) Line 180 (`const Icon(Icons.check_circle, color: const Color(0xFF2E7D32), size: 20)`) removes outer `const` and uses `color: Theme.of(context).colorScheme.primary`; (3) Line 134 enforces title containment via `Text(stepLabel, overflow: TextOverflow.ellipsis)` in `ListTile`; and (4) Line 172-177 warning amber icon uses `color: Theme.of(context).colorScheme.error` (or `colorScheme.tertiary`), fully tokenized without hex literals.

    - **TIER 0 PASS 18 — RESUMABILITY RESET PARITY, VIRTUAL RAG PREFLIGHT APPENDING, EXCEPTIONGROUP CANCELLATION & INITIAL RENDER DEFAULTS:**
       - **DISCOVERY AAAA (RESOLVED IN-SCOPE — Resumability Preflight Reset Step Synchronization in `dag_executor.py#L618-L627`):** When resuming an execution where prior steps failed, `dag_executor.py#L618-L627` iterates over `step_states.items()`, resets `step_states[step_id]` to `ExecutionStatus.PENDING`, and updates `exec_record = exec_record.model_copy(update={"step_states": new_states})`. However, `exec_record.steps` was **OMITTED** from this update! Consequently, while `step_states` showed `PENDING`, `exec_record.steps` left the failed steps with `status: ExecutionStatus.FAILED`. If an intermediate commit or SSE status stream read `steps`, resumed steps appeared as failed until actively re-run. In Step 1.6, synchronize `new_steps = [s.model_copy(update={"status": ExecutionStatus.PENDING}) if s.id == step_id else s for s in exec_record.steps]` and assign `update={"step_states": new_states, "steps": new_steps}`, ensuring both collections start in identical `PENDING` states upon resumption.
       - **DISCOVERY BBBB (RESOLVED IN-SCOPE — Virtual RAG Preflight Step Appending & Telemetry in `dag_executor.py#L934-L988`):** When RAG preflight executes (`dag_executor.py#L934-L940`), `virtual_step_id = f"stp_{uuid.uuid4().hex[:16]}"` is created and assigned into `step_states`, but was NEVER appended to `exec_record.steps`! Furthermore, when it passed (L972-L980) or failed (L984-L988), only `step_states` was mutated. Because `virtual_step_id` did not exist in `exec_record.steps`, UI components reading `record.steps` (such as `ExecutionTimeline`) could never display the RAG preflight step. In Step 1.6, bring this fully in-scope: (1) In lines 934-940, append `new_state` via `new_steps = [s for s in exec_record.steps if s.id != virtual_step_id] + [new_state]` and `update={"step_states": new_states, "steps": new_steps}`; (2) In lines 972-980, update `pass_state` with `progress: 100, status: ExecutionStatus.PASSED` across both `step_states` and `steps`; and (3) In lines 984-988, update `fail_state` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True` across both `step_states` and `steps`.
       - **DISCOVERY CCCC (RESOLVED IN-SCOPE — `ExceptionGroup` Cancellation Step Telemetry Synchronization in `dag_executor.py#L1026-L1034`):** When DAG execution aborts due to an unhandled exception group, `dag_executor.py#L1026-L1034` marks all `RUNNING` steps as `FAILED` in `new_states`, but completely omitted updating `exec_record.steps`! In-flight steps remained stranded with `status: ExecutionStatus.RUNNING` in `exec_record.steps`. In Step 1.6, update `new_steps = [s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(primary_err), "progress": None, "has_warning": True}) if s.status == ExecutionStatus.RUNNING else s for s in exec_record.steps]` and include `"steps": new_steps` in `exec_record.model_copy()`, guaranteeing clean failure telemetry across both arrays.
       - **DISCOVERY DDDD (RESOLVED IN-SCOPE — Initial Render Step Construction Telemetry Defaults in `worker.py#L810-L825`):** In `backend_v2/worker.py#L810-L825`, when `old_state` is None during the initial `_update_render_status` call, `updated_state = ExecutionStep(id=v_step_id, label=msg, status=ExecutionStatus.RUNNING)` omitted `progress=0, has_warning=False`. In Step 1.6, pass `progress=0, has_warning=False` explicitly, ensuring the newly instantiated virtual render step possesses deterministic initial telemetry matching line 436-438 before status streaming begins.

   - **TIER 0 PASS 19 — RAG PREFLIGHT LIVE TELEMETRY, VIRTUAL STEP ID RESUMABILITY PARITY, UNEXPECTED EXCEPTION CANCELLATION, COMPLETE ENGLISH WORKER MODERNIZATION & SSE CONFIG DECOUPLING:**
       - **DISCOVERY EEEE (RESOLVED IN-SCOPE — RAG Preflight Real-Time Telemetry & Progress Emission in `dag_executor.py#L943-L962`):** In `@[backend_v2/services/orchestrator/dag_executor.py#L943-L962]`, `_emit_preflight_progress(message, pct)` computes real-time percentage progress and logs a trace event, but omitted mutating the running virtual preflight step or execution record progress! In Step 1.6, `_emit_preflight_progress` MUST update `exec_record.progress = pct`, `exec_record.status_message = f"Preflight: {message}"`, and update `virtual_step_id` with `progress: pct` and `label: f"system.rag.preflight: {message}"` across both `step_states` and `steps`. This allows `ExecutionTimeline`'s `LinearProgressIndicator` to animate live during heavy multi-document RAG ingestion.
       - **DISCOVERY FFFF (RESOLVED IN-SCOPE — Virtual Step ID Resumability Parity in `dag_executor.py#L932` and `execution.py#L667`):** In `@[backend_v2/services/orchestrator/dag_executor.py#L932]`, the RAG preflight virtual step ID was generated as `virtual_step_id = f"stp_{uuid.uuid4().hex[:16]}"`. When `check_resumability` (`@[backend_v2/services/execution.py#L667]`) validates step set parity between the static workflow blueprint and `record.step_states`, it previously filtered only `not k.startswith("sys_render_")`. A virtual step starting with `stp_` was therefore treated as an unauthorized DAG modification, causing `check_resumability` to fail with `workflow step mismatch`! In Step 1.6 and Step 2.2, enforce: (1) In `dag_executor.py#L932`, generate `virtual_step_id = f"sys_rag_{uuid.uuid4().hex[:16]}"` using the canonical system prefix `sys_`; (2) In `services/execution.py#L667`, update the filter to `exec_step_ids = {k for k, s in record.step_states.items() if not k.startswith("sys_") and getattr(s, "label", None) != "system.rag.preflight"}`. This guarantees that virtual system steps never fracture resumability validation.
       - **DISCOVERY GGGG (RESOLVED IN-SCOPE — Unexpected Non-ExceptionGroup Abort Step Telemetry Parity in `dag_executor.py#L1054-L1066`):** In `@[backend_v2/services/orchestrator/dag_executor.py#L1054-L1066]`, if an unexpected exception strikes outside the main `TaskGroup`, the exception handler updated `exec_record.status = ExecutionStatus.FAILED` and called `commit_trace()`, but failed to update any in-flight `RUNNING` steps and omitted passing `steps` to `commit_trace()`! In Step 1.6, update all `RUNNING` steps in `new_states` and `new_steps` to `FAILED` with `last_error: str(unexpected_err), progress: None, has_warning: True`, and pass `steps=exec_record.steps` to `commit_trace()`, ensuring that no steps remain permanently stranded in `RUNNING` state in the database.
       - **DISCOVERY HHHH (RESOLVED IN-SCOPE — Complete Worker English Modernization in `worker.py#L597, #L889`):** In addition to lines 827, 983, and 1810 modernized in Discovery WWW, physical inspection identified two additional Finnish literals: (1) `worker.py#L889` (`status_message="Koostetaan tulosteita valmiiksi..."`), which must be modernized to `"Compiling output documents..."`; and (2) `worker.py#L597` (`logger.info("Starting Async PDF Koonti...")`), which must be modernized to `"Starting Async PDF assembly..."`. In Step 1.6, modernize both literals to 100% professional English per `english_language_mandate`.
       - **DISCOVERY IIII (RESOLVED IN-SCOPE — Explicit `TypeAdapter` Import in `services/execution.py#L16`):** `TypeAdapter` is referenced in `create_execution_record` (Discovery VVV) to validate `ExecutionMetadata`. In Step 2.2, explicitly import `TypeAdapter` at `@[backend_v2/services/execution.py#L16]` (`from pydantic import TypeAdapter, ValidationError`), guaranteeing zero import errors.
       - **DISCOVERY JJJJ (RESOLVED IN-SCOPE — SSE Transient Retry Sleep Interval Decoupling in `services/execution.py#L311`):** In `@[backend_v2/services/execution.py#L311]`, transient retry     - **TIER 0 PASS 20 — MATH_UTILS TYPED RESOLVER & CONTEXT VARIABLES DTO DISCOVERIES:**
        - **DISCOVERY KKKK (RESOLVED IN-SCOPE — Context Variables DTO Encapsulation in `services/execution.py#L1096`):** In `@[backend_v2/services/execution.py#L1095-L1105]`, `override_atom` iterates `record.context_variables.items()` using duck-typing `if isinstance(v, dict) and "evaluated_atoms" in v:` with a `# noqa: QGR012 [REASON: Polymorphic DAG payload validation]` suppression. In accordance with `@[ki_zero_permissive_typing.md]` (`zero_naked_dicts_and_permissive_typing`), naked dictionaries and duck-typing must be eradicated. Encapsulate evaluated matrix context in a typed Pydantic V2 DTO (`EvaluatedMatrixContextDTO`) in `@[backend_v2/models/v2_core.py]` and parse candidate payloads via `TypeAdapter(EvaluatedMatrixContextDTO)`. If parsing succeeds, mutate atom status directly on the strongly typed model and write back to context variables, completely eliminating `isinstance(v, dict)` and the `# noqa: QGR012` suppression.
        - **DISCOVERY LLLL (RESOLVED IN-SCOPE — `resolve_dot_notation` Typed Path Resolver in `math_utils.py#L186-L222`):** In `@[backend_v2/utils/math_utils.py#L186-L222]`, `resolve_dot_notation` utilizes dictionary duck-typing `isinstance(curr, dict)` at line 210 (suppressed via `# noqa: QGR012`) and generic runtime reflection `getattr(curr, part)` at line 215 (suppressed via `# noqa: QGR001`). In accordance with `@[ki_zero_permissive_typing.md]`, generic reflection and duck-typing must be replaced with a typed path resolver. Refactor `resolve_dot_notation` to traverse state hierarchically using structural pattern matching on `collections.abc.Mapping`, `collections.abc.Sequence`, and Pydantic `BaseModel` (resolving attributes safely via `model_fields` and `__dict__` or typed mapping without dynamic `getattr` reflection), eliminating both `# noqa: QGR012` and `# noqa: QGR001` suppressions while maintaining 100% test compatibility.

    - **TIER 0 PASS 21 — FLUTTER ANALYSIS OPTIONS SSOT DISCOVERY:**
        - **DISCOVERY MMMM (RESOLVED IN-SCOPE — Flutter `analysis_options.yaml` Creation & Freezed Annotation Warning Eradication):** `client_app_v2` lacks an `analysis_options.yaml` configuration file, causing the Dart analyzer to raise `invalid_annotation_target` warnings whenever `@JsonKey` annotations are applied to factory constructor parameters in Freezed models. Consequently, 48 Freezed model files accumulated `// ignore_for_file: invalid_annotation_target` comments. In accordance with Juurisyy 5 and the zero-suppression architecture, create `@[client_app_v2/analysis_options.yaml]` with `include: package:flutter_lints/flutter.yaml` and `analyzer: errors: invalid_annotation_target: ignore`. In Step 3.0 (immediately preceding the Freezed code generation in Step 3.1), create this SSOT file and eradicate `// ignore_for_file: invalid_annotation_target` from modified Freezed models (`execution_record.dart`, `execution_step.dart`, `execution_summary_snapshot.dart`, `workflow_inputs.dart`, `frozen_context_snapshot.dart`), eliminating Dart annotation target warnings cleanly at the root without ad-hoc file-level suppressions.

2. **Cross-Domain Freezed / Pydantic Parity Gap:**
   - Backend `ExecutionSummarySnapshot` (`backend_v2/models/v2_core.py#L1644-L1655`) defines:
     `strictness_level: int = 100`, `is_ensemble_run: bool = False`, `is_degraded: bool = False`, `system_concurrency_snapshot: dict[str, int] = {}`.
     Flutter lacks this model entirely.
   - Backend `raw_inputs` (`backend_v2/models/domain/inputs.py#L32-L91`) defines `WorkflowInputs` with:
     `organization_id: str | None`, `user_id: str | None`, `simulation_mode: bool = False`, `language: str = "en"`, `dynamic_inputs: dict[str, Any] = {}`.
     Existing `ExecutionInputs` in Flutter (`client_app_v2/lib/features/execution/models/execution_inputs.dart#L8-L25`) is an obsolete model containing mismatched fields (`raw_inputs`, `user_role`, `target_locale`) that violates 1:1 schema parity.

3. **SSE Streaming Telemetry Weight:**
   - In `backend_v2/services/execution.py#L291`, `stream_status` polls `self.get_execution(initiator, execution_id)`.
   - By default, `self.exec_repo.get_execution(execution_id)` executes `_hydrate_payloads`, reading offloaded `frozen_context` and `execution_trace` from disk or cloud storage.
   - For SSE status monitoring, the client only requires step status, progress, and telemetry metadata. Offloaded blob traces must not be loaded during the polling loop.

4. **Deep Root-Cause Audit of Suppressions (`# noqa` & `ignore`):**
   - **Juurisyy 1: Automaattimuotoilijan (Ruff/Black) ja `# noqa: E501` -kommenttien desynkronisaatio ("Hanging Suppressions"):**
     - *Esimerkit:* `backend_v2/tests/unit/services/test_execution.py#L102` (`    )  # noqa: E501`), `backend_v2/tests/unit/test_executions.py#L69, #L121` (`    )  # noqa: E501`), ja `test_executions.py#L75` (`) -> None:  # noqa: E501`).
     - *Juurisyy:* Koodi ylitti alun perin 120 merkkiä yhdellä rivillä, ja riville asetettiin `# noqa: E501`. Myöhemmin automaattinen muotoilutyökalu (`ruff format`) rivitti kutsun parametrit omille riveilleen, mutta jätti `# noqa: E501` -kommentin roikkumaan lausekkeen viimeiselle riville (sulkevalle sululle tai paluutyypille). Kommentti seisoo 5–22 merkin pituisella rivillä vaientamassa olematonta rivinpituusvirhettä. Se on 100 % kuollutta koodia.
     - *Ratkaisu:* Poistetaan kaikki tällaiset kuolleet noqa-kommentit heti osana Phase 1 -siivousta.
   - **Juurisyy 2: Sivuvaikutuksellinen rekisteröinti (Import Side-Effects) ja `# noqa: F401`:**
     - *Esimerkit:* `backend_v2/worker.py#L22` (`import backend_v2.hooks  # noqa: F401`), `test_bug_synthesis_hook.py#L3`.
     - *Juurisyy:* Koukkujen rekisteröinti tapahtuu import-hetkellä moduulitason dekoraattoreilla (`@register_hook`). Koska moduulia ei suoraan kutsuta koodissa, linter liputtaa käyttämättömän importin.
     - *Arkkitehtoninen korjaus:* Eksplisiittinen rekisteröintikutsu (kuten `hooks.register_all_hooks()`) korvaa haamuimportit.
   - **Juurisyy 3: Pydantic V2 -mallien sykliset forward-viitteet ja `model_rebuild()` (`# noqa: F401`):**
     - *Esimerkit:* `test_v2_core_models.py#L6` (`from backend_v2.models.state import WorkflowState  # noqa: F401 (Ensures ExecutionRecord is rebuilt)`), `services/test_matrix_domain_parser.py#L19`.
     - *Juurisyy:* `ExecutionRecord` ja `WorkflowState` viittaavat toisiinsa. Pydantic vaatii molempien olemassaolon nimiavaruudessa evaluoidakseen tyyppiannotaatiot (`model_rebuild()`).
     - *Arkkitehtoninen korjaus:* Keskitetään `model_rebuild()` mallipakkauksen `__init__.py` -tasolle.
   - **Juurisyy 4: Geneerinen heijastus (Dynamic Reflection) ja AST-linterit (`# noqa: QGR001`, `QGR012`):**
     - *Esimerkit:* `backend_v2/utils/math_utils.py#L210, #L215`.
     - *Juurisyy:* Geneerinen polunratkaisija (`resolve_path`) käsittelee mielivaltaisia sanakirjoja ja objekteja dynamiikan kautta, mikä laukaisee tiukat AST-tarkistukset.
     - *Arkkitehtoninen korjaus (Pass 20 — IN SCOPE):* Korvataan geneerinen heijastus ja duck-typing tyypitetyllä Pydantic/Mapping-polunratkaisijalla ilman `getattr`-kutsuja, jolloin `# noqa: QGR001` ja `# noqa: QGR012` poistuvat pysyvästi.
   - **Juurisyy 5: Flutter Freezed ja puuttuva `analysis_options.yaml` (`// ignore_for_file: invalid_annotation_target`):**
     - *Esimerkit:* Lähes jokainen Freezed-malli `client_app_v2`:ssa.
     - *Juurisyy:* `client_app_v2`:sta puuttui `analysis_options.yaml`, jolloin Dart-analysaattori varoitti oletussäännöllä `@JsonKey`-annotaatiosta konstruktoriparametreissa.
     - *Arkkitehtoninen korjaus (Pass 21 — IN SCOPE):* Lisätään `analysis_options.yaml` analysaattorikonfiguraatiolla Step 3.0:ssa, jolloin yksittäisten tiedostojen `ignore_for_file: invalid_annotation_target` -kommentit poistuvat pysyvästi ilman erillistä sweep-kierrosta.

---

## 2. 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`ExecutionSummarySnapshot`**<br>`@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart#L1-L35]` | Banned permissive `Map<String, dynamic>?` on `ExecutionRecord.executionSummary`. Banned loose key-value pairs (`total_steps`). | Immutable Freezed DTO with `@JsonSerializable(disallowUnrecognizedKeys: true)` matching `backend_v2/models/v2_core.py#L1644-L1655`. | Direct 4-field DTO. Zero synthetic helper methods or dynamic parsing wrappers. | `flutter test test/features/execution/models/execution_models_test.dart` (asserts typed properties and fails on unrecognized keys). |
| **`WorkflowInputs`**<br>`@[client_app_v2/lib/features/execution/models/workflow_inputs.dart#L1-L35]` | Banned ad-hoc mismatched `ExecutionInputs` (`user_role`, nested `raw_inputs`). Banned untyped `Map<String, dynamic>? rawInputs`. | Immutable Freezed DTO with `@JsonSerializable(disallowUnrecognizedKeys: true)` matching `backend_v2/models/domain/inputs.py#L32-L91`. | Replaces obsolete `execution_inputs.dart` model. 1:1 parity with `WorkflowInputs`. | `flutter test test/features/execution/models/execution_models_test.dart` (asserts exact JSON serialization roundtrip). |
| **`ExecutionStep.scorecardAtoms`**<br>`@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-L37]` | Banned raw `Map<String, dynamic> scorecardAtoms` bypassing Freezed type validation. | `@JsonKey(name: 'scorecard_atoms') @Default({}) Map<String, ScorecardAtomDto> scorecardAtoms`. | Reuses existing `ScorecardAtomDto` from `matrix_scorecard_dto.dart#L62-L86`. Zero redundant wrapper classes. | `flutter test test/features/execution/models/execution_models_test.dart` (asserts typed atom map deserialization and strict key validation). |
| **`ExecutionTimeline`**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L4-L206]` | Banned `List<Map<String, dynamic>> steps`, dynamic `step['status']`, hardcoded fallback string `'Tuntematon askel'`, hex color `Color(0xFF2E7D32)`, and `SizedBox(0,0)`. | Strictly typed `final List<ExecutionStep> steps;`. Typed dot-notation (`step.status`, `step.label`), theme tokens (`colorScheme.primary`), and `AppLocalizations`. | Direct ListView rendering over `List<ExecutionStep>`. Eradicates intermediate `stepStatesList` dictionary conversion in `execution_view.dart`. | `flutter test test/shared/widgets/execution_timeline_test.dart` and `flutter_audit_loop.py`. |
| **SSE Stream Polling**<br>`@[backend_v2/services/execution.py#L239-L332]` | Banned eager hydration of heavy blob traces (`frozen_context`, `execution_trace`) during high-frequency SSE heartbeat loop. | Parameterize `get_execution(initiator, execution_id, hydrate=True)` and invoke `hydrate=False` in `stream_status` polling loop. | Single boolean flag dispatch to `exec_repo.get_execution(..., hydrate=hydrate)`. Zero custom shadow query pipelines. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting `hydrate=False` passed during stream polling. |
| **Dead `# noqa: E501` Suppressions**<br>`@[backend_v2/tests/unit/services/test_execution.py#L102]`<br>`@[backend_v2/tests/unit/test_executions.py#L69-L121]` | Banned hanging `# noqa: E501` comments on 5-character closing parentheses `)` or short return signatures. | Eradicate dead suppressions. Split any legitimately long lines (>120 chars) across clean multi-line parameters. | Zero `# noqa` comments in target execution test files. Clean AST without duct tape. | `uv run ruff check backend_v2/tests/unit/services/test_execution.py backend_v2/tests/unit/test_executions.py` (passes 100% clean). **NOTE (Tier 0 Pass 2):** Physical `grep_search` confirmed zero `# noqa` matches remain — this row is PRE-COMPLETED. |
| **`ExecutionStep` Missing SSE Fields (`progress`, `has_warning`)**<br>`@[backend_v2/models/v2_core.py#L1608-L1639]`<br>`@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-L37]` | Banned reliance on untyped `step_states: Map<String, dynamic>` for runtime SSE fields. Banned dual-key duck-typing (`step['has_warning'] == true \|\| step['has_warnings'] == true`). | Add `progress: int? = None` and `has_warning: bool = False` to backend `ExecutionStep` (`v2_core.py`) and `@JsonKey(name: 'progress') int? progress` + `@JsonKey(name: 'has_warning') @Default(false) bool hasWarning` to Flutter `ExecutionStep`. | Direct field addition to existing DTOs. Zero intermediate wrappers. | `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test` and `flutter test test/features/execution/models/execution_models_test.dart` asserting typed field access and `disallowUnrecognizedKeys` compatibility. |
| **Obsolete `ExecutionInputs` Model Deletion**<br>`@[client_app_v2/lib/features/execution/models/execution_inputs.dart#L1-L26]` | Banned obsolete parallel DTOs (`ExecutionInputs` with `userRole`, `targetLocale`) violating 1:1 schema parity with backend `WorkflowInputs`. | [DELETE] `execution_inputs.dart` and its generated `.freezed.dart` / `.g.dart` files. Replace all imports with `WorkflowInputs`. | Direct file deletion. Zero migration layer or compatibility bridge. | `grep_search` across `client_app_v2/lib/` confirms zero remaining imports of `execution_inputs.dart`. `flutter_audit_loop.py` passes clean. |
| **Redundant `check_resumability` in SSE Polling Loop**<br>`@[backend_v2/services/execution.py#L264-L265, #L291]` | Banned invoking `check_resumability(data)` on every 10-second SSE poll cycle. This re-evaluates resumability state that the streaming client does not consume and adds unnecessary overhead. | Introduce a lightweight SSE-specific internal method `_get_execution_for_sse(execution_id)` that calls `exec_repo.get_execution(execution_id, hydrate=False)` with tenant authorization but SKIPS `check_resumability`. Alternatively, add `skip_resumability: bool = False` parameter to `get_execution` service method. | Single-parameter dispatch to avoid SSE overhead. Zero custom query pipeline. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting `check_resumability` is NOT called during `stream_status` polling. |
| **Dead Rendering Paths: `progress`/`has_warning` on `ExecutionStep` (Tier 0 Pass 3)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L53-L55]`<br>`@[backend_v2/models/v2_core.py#L1608-L1639]`<br>`@[backend_v2/models/execution_core.py#L97-L100]` | Banned dead rendering code paths (`step['progress'] as num?` always null, `step['has_warning']` always null) caused by reading non-existent fields from typed `ExecutionStep` values via untyped `Map<String, dynamic>` proxy. `progress` exists at `ExecutionRecord` level (via `ExecutionCoreFields`), NOT per-step; `has_warning` exists exclusively on `ReportDataDto`, NOT on any step model. | Step 1.0 formalizes `progress: int? = None` and `has_warning: bool = False` as typed fields on `ExecutionStep` (both backend and Flutter). These are **schema preparation** additions — fields will have defaults matching current null behavior, and will render correctly once the DAG executor is enhanced to populate per-step progress in a future iteration. | Zero new abstractions. Direct field addition to existing DTOs. Rendering behavior unchanged until DAG executor populates fields. | `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test` (verifies typed field additions and existing test compatibility). `flutter test` confirms `disallowUnrecognizedKeys` compatibility with optional defaults. |
| **`SizedBox(0, 0)` Guard Redundancy (Tier 0 Pass 3)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L17]` | Banned `SizedBox(width: 0, height: 0)` per `sized_box_shrink_ban` rule. Caller at `execution_view.dart#L286` already guards with `if (stepStatesList.isNotEmpty)` / `if (record.steps.isNotEmpty)`, making the internal empty-check effectively redundant but acceptable as a defensive widget-level contract. | Replace `SizedBox(width: 0, height: 0)` with `SizedBox.shrink()`. This is NOT hiding a broken component but handling a legitimately empty list state — the widget's own input contract. | Direct constant replacement. Zero wrapper classes. | `flutter_audit_loop.py` and visual verification in execution view. |
| **`const` Keyword Removal on Theme-Driven Icon (Tier 0 Pass 4)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L180-L184]` | Banned `const Icon(Icons.check_circle, color: const Color(0xFF2E7D32), size: 20)` — hardcoded hex literal wrapped in a deeply nested `const` constructor. | Replace `const Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primary` and remove the outer `const` keyword from `Icon(...)` since `Theme.of(context)` is not a const expression. | Zero wrapper classes. Direct constructor keyword removal. | `flutter_audit_loop.py` (Dart analyzer confirms valid non-const constructor). |
| **`max_retries` Magic Number & SSE Polling Interval SSOT (Tier 0 Pass 4, RESOLVED Pass 8 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L286, #L300]`<br>`@[backend_v2/settings.py]` | Banned hardcoded magic number `max_retries = 3` inside method body and banned semantic misuse of `llm_retry_delay` (10s) as SSE polling delay. | Add `sse_max_transient_retries: int = 3` and `sse_polling_interval_seconds: float = 2.0` to `settings.py` SSOT. In `stream_status`, bind `max_retries = settings.sse_max_transient_retries` and `await asyncio.sleep(settings.sse_polling_interval_seconds)`. | Direct typed settings fields. Zero shadow configuration dictionaries. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting settings binding and 2.0s polling interval. |
| **`check_resumability` + `hydrate=False` Performance Optimization (Tier 0 Pass 4, CORRECTED Pass 5)**<br>`@[backend_v2/services/execution.py#L264, #L632-L692]` | Banned invoking `check_resumability` on every SSE polling pulse — the method executes `workflow_repo.get_workflow_by_id()` and `usage_service.check_quota()`, two unnecessary per-pulse database/service queries whose output (`is_resumable`) the SSE streaming client does NOT consume during active streaming. | `skip_resumability=True` coupled with `hydrate=False` as a performance optimization eliminating 2 wasteful per-pulse operations. Both parameters passed together from `stream_status`. | Zero additional abstractions. Single boolean parameter gate. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting `check_resumability` is NOT called when `hydrate=False, skip_resumability=True`. |
| **`check_resumability` Permissive Typing & `# noqa: QGR012` Eradication (Tier 0 Pass 5, RESOLVED Pass 8 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L671-L682]` | Banned `isinstance(record.metadata, dict)` + `.get("workflow_version")` + `isinstance(raw_v, str)` coercion chain and dead `# noqa: QGR012` suppression inside `check_resumability`. | Eradicate dictionary duck-typing and dead suppression. Enforce strictly typed dot-notation: `orig_version = record.metadata.workflow_version if record.metadata else record.workflow_version`. Fail-Fast drift check. | Zero wrapper classes. Direct dot-notation access on validated Pydantic models. | `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test` and `ruff check` (100% clean AST, zero QGR suppressions). |
| **SSE Payload Hygiene: `model_dump_json(exclude_none=True)` (Tier 0 Pass 4, RESOLVED Pass 8 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L295]` | Banned dumping full `ExecutionRecord` with dozens of `"field": null` entries across SSE stream, bloating payload size and violating serialization hygiene. | Update L295 to `yield f"data: {record.model_dump_json(exclude_none=True)}\n\n"`. Omit null fields from API transit payload. | Built-in Pydantic serialization parameter. Zero custom payload filters. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting serialized SSE chunk excludes null keys. |
| **Real-Time Per-Step Progress & Warning in DAG Executor (Tier 0 Pass 3, RESOLVED Pass 8 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L740-L755, #L869-L875]` | Banned dead rendering paths in timeline caused by DAG executor writing progress only to `ExecutionRecord.progress` while leaving step progress null. | In `progress_callback`, update `new_state = exec_record.step_states[step_id].model_copy(update={"label": label, "progress": prog})` and synchronize `exec_record.steps` concurrently. On step completion, set `progress: 100` for passed steps. | In-place model copy update. Zero parallel progress trackers. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test` asserting per-step progress in `record.steps`. |
| **`FrozenContextSnapshot` Freezed DTO & Typed Drift Warning (Tier 0 Pass 2, RESOLVED Pass 8 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart#L1-L35]`<br>`@[client_app_v2/lib/features/execution/views/execution_view.dart#L217-L244]` | Banned permissive `Map<String, dynamic>? frozenContext` on `ExecutionRecord` and banned naked dict indexing `frozenContext['version_id']` with lazy fallback `?? ''`. | [NEW] `FrozenContextSnapshot` Freezed model with `@JsonKey(name: 'version_id') String? versionId`. In `execution_view.dart`, consume typed `record.frozenContext?.versionId` via dot-notation. | Direct 2-field DTO. Zero dynamic dictionary access. | `flutter test test/features/execution/models/execution_models_test.dart` and `flutter_audit_loop.py`. |
| **Flutter `ExecutionRecord.stepStates` Parity Typing (Tier 0 Pass 8 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/models/execution_record.dart#L61]` | Banned permissive untyped `Map<String, dynamic>? stepStates` on Flutter `ExecutionRecord` when backend defines `dict[str, ExecutionStep]`. | `@JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates`. 1:1 cross-domain parity with backend `dict[str, ExecutionStepState]`. | Reuses existing `ExecutionStep` Freezed model. Zero redundant wrappers. | `flutter test test/features/execution/models/execution_models_test.dart` asserting typed map deserialization. |
| **Timeline Status Enum Parity & Dead String Variant Eradication (Tier 0 Pass 5/6, RESOLVED Pass 8 — IN SCOPE)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L34-L40, #L66, #L111]` | Banned dead status strings (`'finished'`, `'completed'`, `'processing'`, `'error'`) that backend `ExecutionStatus` never emits. | Standardize strictly against canonical `ExecutionStatus` values (`'passed'`, `'failed'`, `'system_error'`, `'running'`, `'queued'`, `'pending'`). Delete dead string branches. | Clean conditional evaluation on typed `step.status`. Zero legacy string fallback chains. | `flutter test test/shared/widgets/execution_timeline_test.dart`. |
| **Ghost Reference Correction — `step['chunk_count']` (Tier 0 Pass 6)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart]` | Physical `grep_search` confirmed `step['chunk_count']` is NOT accessed anywhere in `execution_timeline.dart`. Prior plan text (Component A L139, Step 1.1 action 5) incorrectly listed it as a naked dictionary lookup to eradicate. | Corrected: `chunk_count` removed from refactoring instructions. The field exists on `ExecutionStep` but is not consumed by the timeline widget. | Zero code changes required (phantom reference). | `grep_search` verification already executed. |
| **Test Import Dependency for `execution_inputs.dart` Deletion (Tier 0 Pass 6)**<br>`@[client_app_v2/test/features/execution/models/execution_models_test.dart#L3]` | Test file imports `execution_inputs.dart` which Step 1.4 deletes. `grep_search` scope in Step 1.4 was limited to `client_app_v2/lib/` and would miss this test reference. | Step 1.4 `grep_search` scope expanded to `client_app_v2/` (both `lib/` and `test/`). Test import MUST be migrated to `WorkflowInputs` before deletion. | Direct import path update. Zero new abstractions. | `grep_search` across full `client_app_v2/` confirms zero remaining `execution_inputs.dart` imports post-migration. |
| **`ExecutionStatusCard` Dead Code Deletion (Tier 0 Pass 7 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart#L1-L241]` | Banned retaining dead, uncalled widget files carrying permissive typing violations (`Map<String, dynamic> initialInputs`). | [DELETE] `execution_status_card.dart`. Forensic audit confirmed zero callers and zero test imports across entire repo. `ExecutionView` and `DynamicStartScreen` are the sole authoritative execution UI paths. | Direct file deletion. Zero migration layer or backward-compatibility wrappers. | `grep_search` across `client_app_v2/` confirms zero remaining references. `flutter_audit_loop.py` passes clean. |
| **Obsolete "De-Generator Policy" Eradication & `ExecutionClient` Strong Typing (Tier 0 Pass 7 — IN SCOPE)**<br>`@[client_app_v2/lib/core/api/execution_client.dart#L14-L52]`<br>`@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L49, #L83-L89, #L124-L127]` | Banned returning untyped `Map<String, dynamic>` from API client under guise of "De-Generator Policy" for domain entities. Banned naked string index access `initialRecord['id'] as String` in controller. | Overthrow obsolete De-Generator Policy. `Future<ExecutionRecord> startExecution(...)`, `Future<ExecutionRecord> resumeExecution(...)`, and `Future<ExecutionRecord> getExecutionStatus(...)`. Deserialize directly at network boundary via `ExecutionRecord.fromJson()`. Controller consumes typed `initialRecord.id`. | Direct return type update. Zero synthetic parsing helper methods. | `flutter test test/features/execution/models/execution_models_test.dart` and `flutter_audit_loop.py`. |
| **Mock `ExecutionClient` Parity in Tests (Tier 0 Pass 7 — IN SCOPE)**<br>`@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L12]`<br>`@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L40]` | Banned desynchronized mock API client signatures returning legacy `Future<Map<String, dynamic>>`. | Update test mock classes to implement `Future<ExecutionRecord> startExecution(...)`, `resumeExecution(...)`, and `getExecutionStatus(...)` returning typed `ExecutionRecord` fixtures. | Direct test mock signature alignment. Zero mock divergence. | `flutter test test/features/execution/controllers/execution_controller_test.dart` passes 100% clean. |
| **`worker.py` Step Telemetry Progress & Warning Persistence (Tier 0 Pass 9 — IN SCOPE)**<br>`@[backend_v2/worker.py#L360-L397]` | Banned `worker.py` rebuilding `updated_steps` on DAG completion while omitting `progress` and `has_warning`, wiping real-time progress back to `None` upon completion. | Copy `actual_progress = st_state.progress` and `actual_warning = st_state.has_warning` into `updated_steps` model copy during DAG termination telemetry aggregation. | In-place model copy update. Zero parallel progress trackers. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test` asserting completed steps retain `progress: 100`. |
| **`FrozenContextSnapshot` Multi-Payload Parity (Tier 0 Pass 9 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart#L1-L45]` | Banned restrictive snapshot model that rejects backend `FrozenContext` fields (`compiled_prompts`, `ui_hints_snapshot`), which causes `CheckedFromJsonException` during direct REST calls. | Declare both metadata fields (`versionId`, `workflowId`, `workflowName`, `organizationId`, `userId`, `createdAt`) AND backend fields (`compiledPrompts`, `injectedTheory`, `generatedSchemas`, `uiHintsSnapshot`, `mcpToolAudit`) with `@Default` annotations. | Full-duplex DTO parity. Zero dynamic map bypasses. | `flutter test test/features/execution/models/execution_models_test.dart` asserting deserialization of both SSE delta and REST payloads. |
| **`test_execution.py` `mock_get_exec` Kwargs Parity (Tier 0 Pass 9 — IN SCOPE)**<br>`@[backend_v2/tests/unit/services/test_execution.py#L1117-L1124]` | Banned rigid mock signature `mock_get_exec(initiator, execution_id)` crashing with `TypeError` when `stream_status` passes `hydrate=False, skip_resumability=True`. | Update signature to `async def mock_get_exec(initiator: Any, execution_id: str, hydrate: bool = True, skip_resumability: bool = False, **kwargs: Any) -> Any:`. | Direct mock signature alignment. Zero test breakage. | `uv run pytest backend_v2/tests/unit/services/test_execution.py -k test_stream_status` passes clean. |
| **`ExecutionRepository.get_execution` Native `hydrate` Support (Tier 0 Pass 10 — IN SCOPE)**<br>`@[backend_v2/database/repositories/execution.py#L174-L192]`<br>`@[backend_v2/services/execution.py#L253]` | Banned inventing parallel query pipelines or bypass mechanisms when repository layer natively supports conditional hydration. | Delegate `await self.exec_repo.get_execution(execution_id, hydrate=hydrate)` directly from `ExecutionService.get_execution`. | Single boolean parameter pass-through. Zero repository driver alterations. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting `hydrate=False` passed to repository. |
| **Initial SSE Handshake vs Polling Loop Isolation (Tier 0 Pass 10 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L282, #L291]` | Banned conflating one-time connection authorization/resumability validation with repetitive high-frequency SSE heartbeat polling. | Initial connection at L282 uses default `hydrate=True, skip_resumability=False` to validate tenant permissions and state; polling loop at L291 uses `hydrate=False, skip_resumability=True`. | Clean architectural separation between authorization handshake and telemetry polling. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` asserting first call hydrates and loop calls skip hydration. |
| **Mock `ExecutionClient` Parity in `execution_controller_test.dart` (Tier 0 Pass 10 — IN SCOPE)**<br>`@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L10-L75]` | Banned returning untyped maps from `MockExecutionClient` methods `startExecution`, `resumeExecution`, and `getExecutionStatus`. | Update all 3 mock methods to return typed `ExecutionRecord` fixtures with required fields (`id`, `workflowId`, `targetLocale`, `status`). | Direct test mock signature alignment. Zero runtime or compile-time type errors. | `flutter test test/features/execution/controllers/execution_controller_test.dart` passes 100% clean. |
| **`WorkflowInputs Freezed Parity` Test Migration (Tier 0 Pass 10 — IN SCOPE)**<br>`@[client_app_v2/test/features/execution/models/execution_models_test.dart#L92-L115]` | Banned retaining obsolete test groups for deleted models (`ExecutionInputs`). | Migrate test group in-place to `WorkflowInputs Freezed Parity`, asserting roundtrip serialization and default values for `WorkflowInputs`. | Clean in-place test migration. Full ISTQB coverage for new DTO. | `flutter test test/features/execution/models/execution_models_test.dart` passes clean. |
| **`worker.py#L351-L359` Fallback Step Construction Preservation (Tier 0 Pass 10 — IN SCOPE)**<br>`@[backend_v2/worker.py#L351-L359]` | Banned constructing fallback `ExecutionStep` instances that omit `progress` and `has_warning`, potentially dropping step metrics if `updated_exec_record.steps` is empty. | Explicitly pass `progress=v.progress, has_warning=v.has_warning` into fallback `ExecutionStep` constructor from `updated_exec_record.step_states.items()`. | In-place field addition. Zero parallel synthesis pipelines. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **Timeline Deprecated `primaryColor` Modernization (Tier 0 Pass 10 — IN SCOPE)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L44, #L91]` | Banned using deprecated Flutter 3 theme property `primaryColor` in UI components. | Replace `Theme.of(context).primaryColor` with `Theme.of(context).colorScheme.primary` at L44 and L91. | Zero wrapper classes. Direct theme token modernization. | `flutter_audit_loop.py`. |
| **`MockExecutionClientPending` Class Name Precision (Tier 0 Pass 11 — IN SCOPE)**<br>`@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L8, #L40-L50]` | Banned ambiguous class targeting in mock updates. Class is explicitly named `MockExecutionClientPending` at L8. | Update `startExecution`, `resumeExecution`, and `getExecutionStatus` in `MockExecutionClientPending` to return typed `ExecutionRecord` fixtures. | Direct test mock signature alignment. Zero AST confusion. | `flutter test test/features/execution/controllers/report_controller_test.dart` passes clean. |
| **`SseClient` Delta Signal `frozen_context` Isolation Parity (Tier 0 Pass 11 — IN SCOPE)**<br>`@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]` | Banned single-schema assumptions between SSE delta streaming (`{'version_id': ...}`) and REST endpoints (full `FrozenContext` payload). | Enforce multi-payload parity on `FrozenContextSnapshot` (`versionId` + backend fields with `@Default` annotations). | Zero runtime transformations. Strict Freezed deserialization for both formats. | `flutter test test/features/execution/models/execution_models_test.dart` and `test/core/api/sse_client_test.dart`. |
| **In-Memory Repository Fake `hydrate` Signature Parity (Tier 0 Pass 11 — IN SCOPE)**<br>`@[backend_v2/tests/fakes/in_memory_repositories.py#L165, #L1291]` | Banned assuming in-memory test repositories lack optional hydration parameters. | Verified `InMemoryExecutionRepository.get_execution(..., hydrate: bool = True)` ALREADY natively supports `hydrate`. | Zero fake repository changes required. Natural delegation pass-through. | `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py` passes clean. |
| **Desktop Pro Tool Studio UX & Title Containment (Tier 0 Pass 12 — IN SCOPE)**<br>`@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L134-L142]`<br>`@[ki_desktop_pro_tool_studio_ux.md]` | Banned unconstrained title text in `ListTile` risking RenderFlex horizontal overflow during desktop window resizing (< 900px). Banned hardcoded fallback string `'Tuntematon askel'`. | Enforce `Text(step.label, overflow: TextOverflow.ellipsis)` title containment. Resolve labels 100% from typed domain SSOT (`step.label`). Enforce theme token styling (`colorScheme.primary`, `colorScheme.error`). | Zero wrapper classes. Direct widget parameter enforcement per `ki_desktop_pro_tool_studio_ux.md`. | `flutter test test/shared/widgets/execution_timeline_test.dart` and `flutter_audit_loop.py`. |
| **`SseClient` Delta Signal & Multi-Payload Parity (Tier 0 Pass 13 — IN SCOPE)**<br>`@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]`<br>`@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart#L1-L45]` | Banned deserialization failures caused by single-schema assumptions between delta SSE chunks (`{'version_id': ...}`) and REST payloads (`compiled_prompts`, `injected_theory`). | Multi-payload parity on `FrozenContextSnapshot`: declare `versionId` alongside backend fields with `@Default` annotations. Clean deserialization in both execution paths under `@JsonSerializable(disallowUnrecognizedKeys: true)`. | Zero custom adapters or transformers. Direct Freezed model deserialization. | `flutter test test/features/execution/models/execution_models_test.dart` asserting deserialization of both payload formats. |
| **`ExecutionService.get_execution` Default Parameter Safety (Tier 0 Pass 13 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L239-L266]`<br>`@[backend_v2/api/routers/execution/executions.py#L96]` | Banned breaking API routes or internal callers when adding performance parameters to core service methods. | Default arguments `hydrate: bool = True, skip_resumability: bool = False` guarantee zero regression for existing callers. Only `stream_status` polling passes `hydrate=False, skip_resumability=True`. | Single-function parameterization with zero shadow dispatch wrappers. | `uv run pytest backend_v2/tests/unit/services/test_execution.py` and `backend_v2/tests/unit/api/routers/execution/test_executions.py`. |
| **Exact AST Mock Client Parity (Tier 0 Pass 13 — IN SCOPE)**<br>`@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L10]`<br>`@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L8]` | Banned compile-time type errors caused by desynchronized test mock client return signatures (`Future<Map<String, dynamic>>` vs `Future<ExecutionRecord>`). | Synchronously update all 3 mock methods across both mock classes (`MockExecutionClient` and `MockExecutionClientPending`) to return typed `ExecutionRecord` fixtures. | Direct mock method signature alignment. Zero mock inheritance drift. | `flutter test test/features/execution/controllers/execution_controller_test.dart` and `report_controller_test.dart` pass 100% clean. |
| **`IExecutionRepository` Native Interface Parity (Tier 0 Pass 14 — IN SCOPE)**<br>`@[backend_v2/database/interfaces.py#L89]`<br>`@[backend_v2/database/repositories/execution.py#L174]` | Banned assuming repository interfaces lack conditional hydration parameters. | Verified `IExecutionRepository.get_execution(..., hydrate: bool = True)` ALREADY natively defines `hydrate: bool = True` across interfaces, drivers, and fakes. | Zero database driver changes required. Natural delegation pass-through. | `uv run pytest backend_v2/tests/unit/services/test_execution.py`. |
| **`ScorecardAtomDto` Zero-Ripple UI Invariant (Tier 0 Pass 14 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/models/execution_step.dart#L31]` | Banned raw dynamic map indexing for step scorecard atoms. | Type `scorecardAtoms: Map<String, ScorecardAtomDto>`. Verified zero UI callers access raw dictionary maps on `step.scorecardAtoms`. | Zero caller migration required. Immediate compile-time type safety. | `flutter test test/features/execution/models/execution_models_test.dart`. |
| **`ExecutionRecord` Stale Docstring Modernization (Tier 0 Pass 14 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/models/execution_record.dart#L16-L17]` | Banned outdated docstring references to obsolete "De-Generator Mandate" on domain entities. | Modernize docstring to reference pure typed Freezed DTO architecture. | Clean documentation alignment. Zero code changes. | `flutter_audit_loop.py`. |
| **`SseClient` Background Isolate Delta Parsing (Tier 0 Pass 14 — IN SCOPE)**<br>`@[client_app_v2/lib/core/api/sse_client.dart#L67-L73]`<br>`@[client_app_v2/test/core/api/sse_client_test.dart#L89]` | Banned delta streaming failures caused by extraneous snapshot data stripping in background isolate. | Verified `FrozenContextSnapshot` multi-payload design seamlessly deserializes both stripped SSE delta payloads (`{'version_id': ...}`) and complete REST responses. | Zero runtime adapters. Direct Freezed model deserialization. | `flutter test test/core/api/sse_client_test.dart` passes clean. |
| **`execution_view.dart#L105` Local Variable Elimination (Tier 0 Pass 14 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/views/execution_view.dart#L105]` | Banned unused fallback dictionary variables (`final frozenContext = record.frozenContext ?? {};`). | Delete unused variable at L105. Consume typed `record.frozenContext?.versionId` directly in banner at L217-L244. | Direct code cleanup. Eradicates dynamic map indexing. | `flutter test` and `flutter_audit_loop.py`. |
| **Virtual Render Step Telemetry Completion (Tier 0 Pass 15 — IN SCOPE)**<br>`@[backend_v2/worker.py#L654-L659]` | Banned leaving dynamically injected virtual render steps (`sys_render_{profile_id}`) stranded at in-flight progress or null when rendering completes successfully. | In `worker.py#L654-L659`, update both `step_states` and `steps` with `progress: 100` alongside `status: ExecutionStatus.PASSED`. | Synchronous state update. Zero parallel telemetry branches. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **`create_execution_record` TypeAdapter Hardening (Tier 0 Pass 15 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L131-L137]` | Banned `isinstance(resolved_metadata, dict)` duck-typing and dead `# noqa: QGR012` suppression in execution record factory. | Replace duck-typing with `TypeAdapter(ExecutionMetadata).validate_python(resolved_metadata) if resolved_metadata is not None else ExecutionMetadata()`. | Eradicates `# noqa: QGR012`. 100% typed Pydantic validation. | `uv run pytest backend_v2/tests/unit/services/test_execution.py`. |
| **`auditDriftWarning` Parameter Safety (Tier 0 Pass 15 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/views/execution_view.dart#L243-L245]` | Banned lazy nested fallback chains `(frozenContext['version_id']?.toString() ?? '')` in localization template arguments. | Pass typed `versionId` directly to `AppLocalizations.of(context)!.auditDriftWarning(versionId)` after null and non-empty check. | Direct typed parameter passing. Eradicates dynamic map indexing. | `flutter test` and `flutter_audit_loop.py`. |
| **`WorkflowInputs` Dynamic Input Encapsulation (Tier 0 Pass 15 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/models/workflow_inputs.dart#L1-L25]`<br>`@[ki_zero_permissive_typing.md]` | Banned permissive unrecognized top-level fields in dynamic input transit models. | Enforce `@JsonSerializable(disallowUnrecognizedKeys: true)` on `WorkflowInputs` while safely encapsulating dynamic payload in `dynamicInputs: Map<String, dynamic>`. | Strict SSOT compliance per `ki_zero_permissive_typing.md`. | `flutter test test/features/execution/models/execution_models_test.dart`. |
| **Dead Widget Deletion Verification (Tier 0 Pass 15 — IN SCOPE)**<br>`@[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart]` | Banned retaining dead widget files and their permissive `initialInputs: Map<String, dynamic>` dictionaries. | Verified zero callers in `lib/` and `test/`. Delete 241 lines cleanly in Step 1.5. | Complete file eradication. Zero broken imports. | `grep_search` and `flutter_audit_loop.py`. |
| **`dag_executor.py` Intermediate Step Persistence (Tier 0 Pass 16 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L87-L118, #L632-L644, #L1000-L1059]` | Banned omitting `steps` in `ExecutionCommitter.commit_trace` and `_safe_commit()`, leaving `steps` permanently stuck in `PENDING` state during intermediate database polling. | Add `steps: list[ExecutionStep] | None = None` to `commit_trace()`, forward `steps=steps` to `ExecutionUpdateDTO`, pass `steps=current.steps` in `_safe_commit()`, and pass `steps=exec_record.steps` in exit commits. | Pure typed forwarding. Guarantees real-time persistence of step transitions. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **Full-Lifecycle DAG State Synchronization (Tier 0 Pass 16 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L658-L1033]` | Banned desynchronization where `step_states` is updated during queued, running, failure, RAG preflight, or cancellation transitions while `exec_record.steps` is ignored. | Synchronously update `new_steps = [s.model_copy(...) if s.id == step_id else s for s in exec_record.steps]` and assign `"steps": new_steps` in `exec_record.model_copy()` across all 6 transition blocks. | Mathematical 1:1 state parity between `steps` and `step_states`. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **Virtual Render Step Full Lifecycle Telemetry (Tier 0 Pass 16 — IN SCOPE)**<br>`@[backend_v2/worker.py#L436-L445, #L654-L659, #L695-L705, #L813-L821]` | Banned leaving dynamically injected virtual render steps stuck at `RUNNING` or uninitialized if rendering fails or succeeds. | Initialize with `progress=0, has_warning=False`, complete with `progress: 100, status: PASSED`, and fail with `status: FAILED, last_error: str(e), progress: None, has_warning: True` across both `step_states` and `steps`. | Complete lifecycle coverage for virtual system steps. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **`create_execution_record` Lazy `or` Fallback Eradication (Tier 0 Pass 16 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L131-L135]` | Banned duck-typing and lazy fallback `or` (`(extra_persistence_fields.pop("metadata", None) or ExecutionMetadata())`). | Replace with explicit `raw_meta = metadata if metadata is not None else extra_persistence_fields.pop("metadata", None)` and validate strictly via `TypeAdapter(ExecutionMetadata)`. | 100% typed Pydantic validation with zero lazy fallbacks. | `uv run pytest backend_v2/tests/unit/services/test_execution.py`. |
| **Backend English Status Strings Modernization (Tier 0 Pass 17 — IN SCOPE)**<br>`@[backend_v2/worker.py#L827, #L983, #L1810]`<br>`@[.agents/rules/00-antigravity-core.md]` | Banned hardcoded Finnish status strings (`"Lasketaan dynaamisia tuloksia..."`, `"Generoidaan tekoälysynteesiä..."`, `"Koostetaan tulosteita valmiiksi..."`) in backend execution code per `english_language_mandate`. | Replace with professional, concise English status labels: `"Calculating dynamic results..."` (L827), `"Generating AI synthesis..."` (L983), and `"Compiling output documents..."` (L1810). | Zero new abstractions. Direct string literal modernization. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **Synthesis Error Handler Step Telemetry Parity (Tier 0 Pass 17 — IN SCOPE)**<br>`@[backend_v2/worker.py#L1854-L1864]` | Banned synthesis task failure handler updating `status: FAILED` while omitting `progress: None, has_warning: True`, causing telemetry divergence with PDF failure handler. | Enrich `updated_state` and `new_steps` in `generate_profile_synthesis_and_pdf_task` error handler with `progress: None, has_warning: True` across both `step_states` and `steps`. | In-place model copy update. 100% telemetry parity across render workers. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **`ExecutionCommitter.commit_trace` None-Guard (Tier 0 Pass 17 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L110-L117]` | Banned passing `steps=None` explicitly into `ExecutionUpdateDTO`, which causes `exclude_unset=True` to include `"steps": null` and inadvertently overwrite persisted steps in the database with null. | Conditionally add `steps` to `update_data` dictionary ONLY `if steps is not None: update_data["steps"] = steps`. | Zero wrapper classes. Pure dictionary key presence gating. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **Resumability Preflight Step Synchronization (Tier 0 Pass 18 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L618-L627]` | Banned resetting failed steps to `PENDING` only in `step_states` during execution resumption while leaving `exec_record.steps` stranded in `FAILED` state. | Synchronize `new_steps = [s.model_copy(update={"status": ExecutionStatus.PENDING}) if s.id == step_id else s for s in exec_record.steps]` and update both `step_states` and `steps` concurrently. | In-place model copy update. Zero parallel collections. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **Virtual RAG Preflight Step Synchronization (Tier 0 Pass 18 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L934-L988]` | Banned creating virtual RAG preflight steps only in `step_states` while omitting them from `exec_record.steps`, hiding preflight status from timeline UI. | Append virtual preflight step to `exec_record.steps` on creation, update with `progress: 100, status: PASSED` on pass, and update with `status: FAILED, last_error: str(e), progress: None, has_warning: True` on fail. | In-place list appending. Zero missing UI nodes. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **`ExceptionGroup` Cancellation Step Telemetry (Tier 0 Pass 18 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L1026-L1034]` | Banned updating running steps to `FAILED` only in `step_states` during exception group cancellation while leaving `exec_record.steps` stranded in `RUNNING` state. | Synchronize `new_steps = [s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(primary_err), "progress": None, "has_warning": True}) if s.status == ExecutionStatus.RUNNING else s for s in exec_record.steps]` across both collections. | Complete lifecycle cancellation parity. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **Initial Render Step Construction Defaults (Tier 0 Pass 18 — IN SCOPE)**<br>`@[backend_v2/worker.py#L810-L825]` | Banned constructing virtual render step with null progress and missing warning flags when `old_state` is None. | Explicitly pass `progress=0, has_warning=False` in `ExecutionStep(id=v_step_id, label=msg, status=ExecutionStatus.RUNNING, progress=0, has_warning=False)`. | Deterministic telemetry defaults. Zero undefined fields. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **RAG Preflight Real-Time Telemetry & Progress Emission (Tier 0 Pass 19 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L943-L962]` | Banned emitting preflight progress exclusively as a background trace event while leaving `exec_record.step_states[virtual_step_id]`, `exec_record.steps`, and `exec_record.progress` un-updated. | In `_emit_preflight_progress`, synchronously update both `step_states` and `steps` with `progress: pct` and `label: f"system.rag.preflight: {message}"`, alongside `exec_record.progress = pct` and `status_message = f"Preflight: {message}"`. | Live in-place model copy update. Zero parallel progress trackers. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py`. |
| **Virtual Step ID Resumability Parity (Tier 0 Pass 19 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L932]`<br>`@[backend_v2/services/execution.py#L667]` | Banned generating virtual RAG step with `stp_` prefix, which bypassed `not k.startswith("sys_render_")` filter in `check_resumability` and permanently broke resumability on RAG workflows. | Use canonical system prefix `virtual_step_id = f"sys_rag_{uuid.uuid4().hex[:16]}"` in `dag_executor.py#L932` and update `check_resumability` filter to exclude all system steps: `{k for k, s in record.step_states.items() if not k.startswith("sys_") and getattr(s, "label", None) != "system.rag.preflight"}`. | Direct prefix and filter alignment. Zero database migration. | `uv run pytest backend_v2/tests/unit/services/test_execution_resumability.py`. |
| **Unexpected Exception Step Telemetry Parity (Tier 0 Pass 19 — IN SCOPE)**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L1054-L1066]` | Banned leaving in-flight `RUNNING` steps stranded as `RUNNING` during unexpected non-ExceptionGroup aborts, and banned omitting `steps` in the final committer call. | Synchronize `new_states` and `new_steps` to mark all `RUNNING` steps as `FAILED` with `last_error: str(unexpected_err), progress: None, has_warning: True`, and pass `steps=exec_record.steps` to `commit_trace()`. | Complete failure lifecycle parity. Zero stranded running nodes. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`. |
| **Complete Worker English Modernization (Tier 0 Pass 19 — IN SCOPE)**<br>`@[backend_v2/worker.py#L889, #L597]`<br>`@[.agents/rules/00-antigravity-core.md]` | Banned remaining Finnish status string in starvation cache (`"Koostetaan tulosteita valmiiksi..."` at L889) and Finnish word in log message (`"Starting Async PDF Koonti..."` at L597). | Replace L889 with `"Compiling output documents..."` and L597 with `logger.info(f"[Task] Starting Async PDF assembly for execution {execution_id}")`. | Direct string modernization. Zero new abstractions. | `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`. |
| **Missing `TypeAdapter` Import in `services/execution.py` (Tier 0 Pass 19 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L16]` | Banned missing imports causing compile-time NameError when `TypeAdapter(ExecutionMetadata)` is introduced. | Explicitly update line 16 to `from pydantic import TypeAdapter, ValidationError`. | Clean standard library import. Zero third-party dependencies. | `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test`. |
| **Retry Sleep Interval Decoupling at `services/execution.py#L311` (Tier 0 Pass 19 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L311]` | Banned retaining legacy 10-second `settings.llm_retry_delay` on transient ResourceNotFoundError backoff retry. | Modernize L311 to `await asyncio.sleep(get_settings().sse_polling_interval_seconds)` alongside L300, completely eliminating `settings.llm_retry_delay` from status streaming. | Direct typed settings binding. Zero magic numbers. | `uv run pytest backend_v2/tests/unit/services/test_execution.py`. |
| **Context Variables DTO Encapsulation (Tier 0 Pass 20 — IN SCOPE)**<br>`@[backend_v2/services/execution.py#L1095-L1105]`<br>`@[ki_zero_permissive_typing.md]` | Banned naked dictionary duck-typing `isinstance(v, dict)` and `# noqa: QGR012` suppression in `override_atom`. | Encapsulate evaluated matrix context in typed `EvaluatedMatrixContextDTO` and validate via `TypeAdapter(EvaluatedMatrixContextDTO)` without duck-typing or suppressions. | Direct Pydantic V2 DTO validation. Zero untyped dictionary traversal loops. | `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test` asserting clean AST and successful atom override. |
| **Typed Path Resolver in `math_utils.py` (Tier 0 Pass 20 — IN SCOPE)**<br>`@[backend_v2/utils/math_utils.py#L186-L222]`<br>`@[ki_zero_permissive_typing.md]` | Banned generic reflection `getattr(curr, part)` (`QGR001`), dictionary duck-typing `isinstance(curr, dict)` (`QGR012`), and `# noqa` suppressions. | Refactor `resolve_dot_notation` into a typed path resolver using structured collection matching and Pydantic field resolution without `getattr` reflection. | Zero dynamic reflection. Pure typed traversal. | `uv run python scripts/backend_audit_loop.py backend_v2/utils/math_utils.py --test` and `uv run pytest backend_v2/tests/unit/utils/test_math_utils.py` passing 100% clean. |
| **Flutter `analysis_options.yaml` SSOT (Tier 0 Pass 21 — IN SCOPE)**<br>`@[client_app_v2/analysis_options.yaml]`<br>`@[.agents/rules/02_flutter_desktop.md]` | Missing analyzer configuration forcing 48+ Freezed models to declare ad-hoc `// ignore_for_file: invalid_annotation_target` suppressions. | Canonical Dart analyzer configuration extending `package:flutter_lints/flutter.yaml` and configuring `invalid_annotation_target: ignore` under `analyzer.errors`. | Zero ad-hoc file-level ignore directives. Pure centralized analyzer configuration. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/execution_record.dart` asserting clean analyzer output without warnings. |

---

## 3. Proposed Changes & Target Boundaries

### Component A: Pre-Implementation Cleanups (Technical Debt Eradication)
- **[MODIFY]** `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L4-L207]`
  - Refactor `ExecutionTimeline` constructor to accept `required List<ExecutionStep> steps`.
  - Eradicate `SizedBox(width: 0, height: 0)` in favor of clean conditional render (`const SizedBox.shrink()`).
  - Eradicate `step['status']?.toString().toLowerCase() ?? 'pending'` in favor of `step.status.toLowerCase()`.
  - Eradicate `step['label']?.toString() ?? 'Tuntematon askel'` in favor of `step.label`, wrapping in `Text(step.label, overflow: TextOverflow.ellipsis)` for desktop Title Containment (`ki_desktop_pro_tool_studio_ux.md`).
  - Eradicate `step['last_error']`, `step['message_code']` naked dictionary lookups in favor of `step.lastError`, `step.messageCode`. (**Tier 0 Pass 6 Correction:** `step['chunk_count']` was previously listed here but physical `grep_search` confirmed it is NOT accessed anywhere in `execution_timeline.dart` — it was a ghost reference.)
  - Eradicate `const Color(0xFF2E7D32)` in favor of `Theme.of(context).colorScheme.primary`.
  - Modernize deprecated `Theme.of(context).primaryColor` to `Theme.of(context).colorScheme.primary` at L44 and L91.
  - Eradicate dual-key duck-typed `step['has_warning'] == true || step['has_warnings'] == true` in favor of typed `step.hasWarning`.
  - Eradicate naked `step['progress'] as num?` in favor of typed `step.progress`.
- **[MODIFY]** `@[client_app_v2/lib/features/execution/views/execution_view.dart#L105-L110, #L217-L244, #L286-L295]`
  - Delete unused variable `final frozenContext = record.frozenContext ?? {};` at L105 (Discovery LLL).
  - Eliminate `stepStatesMap` / `stepStatesList` dictionary transformation (L107-L110).
  - In Version Drift Warning Banner (L217-L244): replace naked dict indexing `frozenContext.containsKey('version_id')` and `(frozenContext['version_id']?.toString() ?? '')` with typed dot-notation:
    `final versionId = record.frozenContext?.versionId;`
    `if (versionId != null && versionId.isNotEmpty && versionId != 'v2.0.0') ...`
    passing `versionId` directly to `AppLocalizations.of(context)!.auditDriftWarning(versionId)` (Discovery OOO), eliminating all dynamic map lookups and lazy `?? ''` fallbacks (Discovery EE & LLL).
  - Pass `record.steps` directly into `ExecutionTimeline(steps: record.steps, compact: false)`.
- **[DELETE]** `@[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart#L1-L241]`
  - **Tier 0 Pass 7 Discovery BB:** Physical `grep_search` confirmed zero references across `client_app_v2/` (both `lib/` and `test/`). This 241-line widget file is 100% dead code, completely superseded by `DynamicStartScreen` and `ExecutionView`. Deleting it eliminates an obsolete parallel view architecture and permanently eradicates `Map<String, dynamic> initialInputs` (Discovery Z).
- **[ALREADY DONE]** ~~`@[backend_v2/tests/unit/services/test_execution.py#L102]`~~
  - ~~Eradicate dead `    )  # noqa: E501` suppression from closing parenthesis.~~
  - **Tier 0 Pass 2 Discovery:** Physical `grep_search` confirmed zero `# noqa` matches remain. This item is PRE-COMPLETED.
- **[ALREADY DONE]** ~~`@[backend_v2/tests/unit/test_executions.py#L69, #L75, #L121]`~~
  - ~~Eradicate dead `# noqa: E501` suppressions from closing parentheses and return signatures. Cleanly wrap signatures natively.~~
  - **Tier 0 Pass 2 Discovery:** Physical `grep_search` confirmed zero `# noqa` matches remain. This item is PRE-COMPLETED.

### Component A.1: ExecutionStep SSE Field Additions (Tier 0 Pass 2/9 — Prerequisite for Timeline Refactor)
- **[MODIFY]** `@[backend_v2/models/v2_core.py#L1608-L1639]`
  - Add to `ExecutionStep` model using strict PEP 593 `Annotated` syntax per `pydantic_annotated_fields_mandate`:
    - `progress: Annotated[int | None, Field(default=None, ge=0, le=100, description="Step progress percentage for SSE streaming (0-100)")] = None`
    - `has_warning: Annotated[bool, Field(default=False, description="Whether the step completed with warnings")] = False`
  - **ROOT CAUSE:** The `execution_timeline.dart` widget currently reads `step['progress']` and `step['has_warning']` from the untyped `step_states` dictionary. These SSE-era fields were never formalized into the typed `ExecutionStep` Pydantic model. Without this addition, switching to typed `List<ExecutionStep>` will silently drop the progress bar and warning icon rendering.
  - **TIER 0 PASS 3 CLARIFICATION (Dead Rendering Paths):** Physical inspection (Pass 3) confirms that `progress` has NEVER existed on `ExecutionStep` — it is an `ExecutionRecord`-level field (via `ExecutionCoreFields` at `@[backend_v2/models/execution_core.py#L97-L100]`). The DAG executor writes `progress` to `ExecutionRecord.progress` at `@[backend_v2/services/orchestrator/dag_executor.py#L744]`, NOT to individual step states. Similarly, `has_warning` exists exclusively on `ReportDataDto` (`@[backend_v2/models/v2_core.py#L949]`), never on any step model. The timeline widget's progress bar (`LinearProgressIndicator`) and warning icon have been **dead rendering paths** since inception — `step['progress']` always returned null, `step['has_warning']` always returned null. This step is therefore a **schema formalization/preparation**: the fields are added to `ExecutionStep` with defaults matching current null behavior, enabling typed access and preparing the schema for a future DAG executor enhancement that will populate per-step progress. The rendering behavior is unchanged by this step.
  - **FULL-DUPLEX PARITY:** Adding fields to a `ConfigDict(extra="forbid")` model is safe because both fields have defaults (`None` and `False`), so existing persisted `ExecutionStep` payloads missing these fields will deserialize cleanly.
- **[MODIFY]** `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-L37]`
  - Add corresponding Freezed fields:
    - `@JsonKey(name: 'progress') int? progress,`
    - `@JsonKey(name: 'has_warning') @Default(false) bool hasWarning,`
  - **NOTE:** The legacy `execution_timeline.dart` checked TWO spellings (`step['has_warning'] == true || step['has_warnings'] == true`). The canonical field name is `has_warning` (matching backend Python). The `has_warnings` variant is a defunct historical key and MUST NOT be carried forward.

### Component B: Flutter Freezed Sub-DTO Typing & Parity
- **[NEW]** `@[client_app_v2/analysis_options.yaml]` (Pass 21 — SSOT Analyzer Configuration)
  - Create canonical Dart analyzer configuration:
    ```yaml
    include: package:flutter_lints/flutter.yaml

    analyzer:
      errors:
        invalid_annotation_target: ignore
    ```
  - Eradicate `// ignore_for_file: invalid_annotation_target` from all modified Freezed model files (`execution_record.dart`, `execution_step.dart`, `execution_summary_snapshot.dart`, `workflow_inputs.dart`, `frozen_context_snapshot.dart`), eliminating ad-hoc suppressions at the root.
- **[NEW]** `@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart#L1-L35]`
  - Create strict Freezed DTO matching backend `ExecutionSummarySnapshot`:
    - `@JsonKey(name: 'strictness_level') @Default(100) int strictnessLevel,`
    - `@JsonKey(name: 'is_ensemble_run') @Default(false) bool isEnsembleRun,`
    - `@JsonKey(name: 'is_degraded') @Default(false) bool isDegraded,`
    - `@JsonKey(name: 'system_concurrency_snapshot') @Default({}) Map<String, int> systemConcurrencySnapshot,`
- **[NEW]** `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart#L1-L35]`
  - Create strict Freezed DTO matching backend `WorkflowInputs`:
    - `@JsonKey(name: 'organization_id') String? organizationId,`
    - `@JsonKey(name: 'user_id') String? userId,`
    - `@JsonKey(name: 'simulation_mode') @Default(false) bool simulationMode,`
    - `@Default('en') String language,`
    - `@JsonKey(name: 'dynamic_inputs') @Default({}) Map<String, dynamic> dynamicInputs,`
- **[DELETE]** `@[client_app_v2/lib/features/execution/models/execution_inputs.dart]` (and generated `.freezed.dart` / `.g.dart` files)
  - **Tier 0 Pass 2 Discovery:** This obsolete model (`ExecutionInputs` with mismatched fields `userRole`, `targetLocale`, nested `rawInputs`) is fully replaced by the new `WorkflowInputs` DTO. All existing imports MUST be redirected to `WorkflowInputs` before deletion. Verify zero remaining imports via `grep_search` across `client_app_v2/lib/`.
- **[MODIFY]** `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-L37]`
  - Import `matrix_scorecard_dto.dart` and update `scorecardAtoms` field:
    `@JsonKey(name: 'scorecard_atoms') @Default({}) Map<String, ScorecardAtomDto> scorecardAtoms,`
  - (The `progress` and `hasWarning` field additions from Component A.1 are also applied to this file.)
- **[NEW]** `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart#L1-L45]`
  - Create strict Freezed DTO matching backend `FrozenContext` (`backend_v2/models/v2_core.py#L1548-L1562`) with full multi-payload parity:
    - `@JsonKey(name: 'version_id') String? versionId,`
    - `@JsonKey(name: 'workflow_id') String? workflowId,`
    - `@JsonKey(name: 'workflow_name') String? workflowName,`
    - `@JsonKey(name: 'organization_id') String? organizationId,`
    - `@JsonKey(name: 'user_id') String? userId,`
    - `@JsonKey(name: 'created_at') String? createdAt,`
    - `@JsonKey(name: 'compiled_prompts') @Default({}) Map<String, String> compiledPrompts,`
    - `@JsonKey(name: 'injected_theory') @Default({}) Map<String, dynamic> injectedTheory,`
    - `@JsonKey(name: 'generated_schemas') @Default({}) Map<String, dynamic> generatedSchemas,`
    - `@JsonKey(name: 'ui_hints_snapshot') @Default({}) Map<String, dynamic> uiHintsSnapshot,`
    - `@JsonKey(name: 'mcp_tool_audit') @Default([]) List<Map<String, dynamic>> mcpToolAudit,`
- **[MODIFY]** `@[client_app_v2/lib/features/execution/models/execution_record.dart#L16-L89]`
  - Modernize stale docstring referencing "De-Generator Mandate" at L16-L17 (Discovery JJJ).
  - Update `executionSummary` type from `Map<String, dynamic>?` to `ExecutionSummarySnapshot?`.
  - Update `rawInputs` type from `Map<String, dynamic>?` to `WorkflowInputs?`.
  - Update `modelsUsed` type from `Map<String, dynamic>?` to `Map<String, int>?`.
  - Update `frozenContext` type from `Map<String, dynamic>?` to `FrozenContextSnapshot?`.
  - Update `stepStates` type from `Map<String, dynamic>?` to `Map<String, ExecutionStep>?`.
- **[MODIFY]** `@[client_app_v2/lib/core/api/execution_client.dart#L14-L52]`
  - **Tier 0 Pass 7 Discovery CC (Eradicate De-Generator Policy & Return Typed ExecutionRecord):**
    - Overthrow and remove the obsolete "De-Generator Policy" docstring at L16-L17.
    - Import `package:client_app/features/execution/models/execution_record.dart`.
    - Update return types of `startExecution`, `resumeExecution`, and `getExecutionStatus` from `Future<Map<String, dynamic>>` to `Future<ExecutionRecord>`.
    - Deserialize responses directly at the network client boundary:
      `return ExecutionRecord.fromJson(response.data as Map<String, dynamic>);`
- **[MODIFY]** `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L49, #L83-L89, #L124-L127]`
  - Remove obsolete De-Generator Policy comment at L49.
  - In `startExecution` (L83-L89): consume `initialRecord.id` directly via typed dot-notation (eradicating naked string index `initialRecord['id'] as String`) and assign `state = AsyncValue.data(initialRecord);` directly (eradicating redundant `ExecutionRecord.fromJson()` parsing).
  - In `resumeExecution` (L124-L127): assign `state = AsyncValue.data(resumedRecord);` directly from typed `ExecutionRecord` response.
- **[MODIFY]** `@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L62-L68]`
  - In `startExecution`: consume typed `final executionId = response.id;` instead of untyped duck-typing `response['id']?.toString() ?? ''`.

### Component C: Backend SSE Polling Optimization & Resilience Hardening
- **[MODIFY]** `@[backend_v2/settings.py#L309-L315]`
  - Add typed SSE settings:
    - `sse_max_transient_retries: Annotated[int, Field(default=3, ge=1, le=10, description="Maximum transient retry count for SSE polling")] = 3`
    - `sse_polling_interval_seconds: Annotated[float, Field(default=2.0, gt=0.0, le=30.0, description="Polling interval in seconds for SSE execution status stream")] = 2.0`
- **[MODIFY]** `@[backend_v2/services/execution.py#L131-L137, #L239-L332, #L671-L682, #L1095-L1105]`
  - In `create_execution_record` (L131-L137):
    - Eradicate `isinstance(resolved_metadata, dict)` duck-typing and the `# noqa: QGR012` suppression (Discovery NNN).
    - Replace with strict Pydantic `TypeAdapter(ExecutionMetadata).validate_python(resolved_metadata) if resolved_metadata is not None else ExecutionMetadata()`.
  - Update `get_execution(self, initiator: TokenData, execution_id: str, hydrate: bool = True, skip_resumability: bool = False) -> ExecutionRecord:` to accept both `hydrate` and `skip_resumability`.
  - Delegate `hydrate` directly to the repository: `await self.exec_repo.get_execution(execution_id, hydrate=hydrate)` (connecting directly to the repository's native `hydrate: bool = True` parameter verified in Discovery RR).
  - When `skip_resumability=True`, skip the `check_resumability(data)` call and leave `is_resumable` as persisted.
  - In `stream_status`:
    - Bind `max_retries = get_settings().sse_max_transient_retries` (eradicating hardcoded magic number `max_retries = 3`).
    - Update polling query to `await self.get_execution(initiator=initiator, execution_id=execution_id, hydrate=False, skip_resumability=True)`.
    - Update JSON serialization to `yield f"data: {record.model_dump_json(exclude_none=True)}\n\n"` (Discovery II).
    - Update polling delay to `await asyncio.sleep(get_settings().sse_polling_interval_seconds)` (decoupling from `llm_retry_delay` and providing snappy 2.0s updates).
  - In `check_resumability` (L671-L682):
    - Eradicate `elif isinstance(record.metadata, dict):` duck-typing, `.get("workflow_version")`, and the dead `# noqa: QGR012` suppression (Discovery JJ).
    - Enforce pure typed dot-notation:
      ```python
      orig_version: int | None = None
      if record.metadata is not None:
          orig_version = record.metadata.workflow_version
      elif record.workflow_version is not None:
          orig_version = record.workflow_version
      if orig_version is not None and workflow.version != orig_version:
          return False
      ```
  - In `override_atom` (L1095-L1105):
    - Eradicate `isinstance(v, dict)` duck-typing and the `# noqa: QGR012` suppression (Discovery KKKK).
    - Validate candidate dictionary payloads using `TypeAdapter(EvaluatedMatrixContextDTO).validate_python(v)` and mutate atoms on typed DTO before writing back.
- **[MODIFY]** `@[backend_v2/utils/math_utils.py#L186-L222]`
  - Refactor `resolve_dot_notation` from dynamic reflection (`getattr`) and duck-typing (`isinstance(curr, dict)`) into a typed path resolver using structured collections and Pydantic models (Discovery LLLL).
  - Eradicate both `# noqa: QGR012` and `# noqa: QGR001` suppressions permanently while preserving 100% test compatibility.
- **[MODIFY]** `@[backend_v2/services/orchestrator/dag_executor.py#L87-L118, #L618-L644, #L658-L720, #L740-L755, #L869-L875, #L904-L988, #L1000-L1066]`
  - In `ExecutionCommitter.commit_trace` (L87-L118):
    Add `steps: list[ExecutionStep] | None = None` parameter and pass `steps=steps` into `ExecutionUpdateDTO(...)` (Discovery SSS).
  - In `_safe_commit()` (L632-L644):
    Pass `steps=current.steps` when calling `await self._committer.commit_trace(...)`.
  - In final exit commits (L1000, L1014, L1035, L1059):
    Pass `steps=exec_record.steps` when calling `await self._committer.commit_trace(...)`.
  - In state transitions across `dag_executor.py` (Discovery TTT):
    Synchronize `exec_record.steps` concurrently alongside `exec_record.step_states` inside `async with _update_lock:`:
    - Cascading dependency failure (L658-L662): update `new_steps = [s.model_copy(update={"status": ExecutionStatus.FAILED}) if s.id == step_id else s for s in exec_record.steps]`.
    - Resumability preflight reset (L618-L627, Discovery AAAA): update `new_steps = [s.model_copy(update={"status": ExecutionStatus.PENDING}) if s.id == step_id else s for s in exec_record.steps]`.
    - Step queued (L702-L704): update `new_steps = [s.model_copy(update={"status": ExecutionStatus.QUEUED}) if s.id == step_id else s for s in exec_record.steps]`.
    - Step running in `watch_running` (L716-L720): update `new_steps = [s.model_copy(update={"status": ExecutionStatus.RUNNING}) if s.id == step_id else s for s in exec_record.steps]`.
    - In `progress_callback` (L741-L745): update `new_state = exec_record.step_states[step_id].model_copy(update={"label": label, "progress": prog})`, and synchronize `exec_record.steps` concurrently:
      `new_steps = [s.model_copy(update={"label": label, "progress": prog}) if s.id == step_id else s for s in exec_record.steps]`
      `exec_record = exec_record.model_copy(update={"steps": new_steps, "step_states": new_states, "progress": prog, "status_message": label})`.
    - In step completion (L869-L873): update completed steps with `progress: 100` if `step_status == ExecutionStatus.PASSED` in both `step_states` and `steps`.
    - In step exception catch (L904-L913): update `new_steps = [s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(e), "progress": None, "has_warning": True}) if s.id == step_id else s for s in exec_record.steps]`.
    - In RAG preflight virtual step (L932-L988, Discoveries BBBB, EEEE & FFFF):
      - Set `virtual_step_id = f"sys_rag_{uuid.uuid4().hex[:16]}"` to adhere to canonical system prefix (Discovery FFFF).
      - Ensure virtual step is appended on creation and updated with `progress: 100, status: ExecutionStatus.PASSED` on pass, and `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True` on fail in both `step_states` and `steps`.
      - In `_emit_preflight_progress(message, pct)` (L943-L962, Discovery EEEE): update `preflight_state = exec_record.step_states[virtual_step_id].model_copy(update={"label": f"system.rag.preflight: {message}", "progress": pct})`, update `exec_record.steps` with `progress: pct` and `label: f"system.rag.preflight: {message}"`, and set `exec_record.progress = pct` and `exec_record.status_message = f"Preflight: {message}"`.
    - In `ExceptionGroup` cancellation (L1026-L1034, Discovery CCCC): mark running steps as `FAILED` with `last_error: str(primary_err), progress: None, has_warning: True` in both `step_states` and `steps`.
    - In unexpected exception catch (L1054-L1066, Discovery GGGG): mark running steps as `FAILED` with `last_error: str(unexpected_err), progress: None, has_warning: True` across both `step_states` and `steps`, and pass `steps=exec_record.steps` to `self.committer.commit_trace(...)`.
  - Keep the INITIAL authorization call at L282 with full hydration/resumability:
    `await self.get_execution(initiator=initiator, execution_id=execution_id)` (defaults to hydrate=True, skip_resumability=False).
- **[MODIFY]** `@[backend_v2/worker.py#L351-L397, #L436-L445, #L597, #L654-L659, #L695-L705, #L810-L825, #L889, #L1854-L1864]`
  - In fallback step construction (L351-L359):
    Update `ExecutionStep(id=k, label=v.label, status=v.status, scorecard_atoms=v.scorecard_atoms)` to also include `progress=v.progress, has_warning=v.has_warning` (Discovery VV).
  - In step telemetry aggregation loop upon DAG completion (L360-L397):
    - Extract `actual_progress = st_state.progress if st_state else st.progress`
    - Extract `actual_warning = st_state.has_warning if st_state else st.has_warning`
    - Include `progress: actual_progress` and `has_warning: actual_warning` in `st.model_copy(update={...})` for both telemetry-bearing and non-telemetry steps, ensuring DAG completion does not wipe step progress.
  - In virtual report render step full-lifecycle telemetry (Discovery MMM, UUU & DDDD):
    - Initialization (L436-L445 & L810-L825): initialize `ExecutionStep(id=v_step_id, label="Generating Output Report", status=ExecutionStatus.RUNNING, progress=0, has_warning=False)` (passing explicit `progress=0, has_warning=False` when `old_state` is None at L813).
    - Successful render completion (L654-L659): set `progress: 100` alongside `status: ExecutionStatus.PASSED` when updating `new_step = old_state.model_copy(update={"status": ExecutionStatus.PASSED, "progress": 100})` for both `step_states` and `steps`.
    - Render failure catch (L695-L705): update both `step_states` and `steps` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True`.
  - In English language modernization (Discoveries WWW & HHHH):
    - Modernize status messages at L827, L889, L983, L1810 from Finnish to English: `"Calculating dynamic results..."` (L827), `"Compiling output documents..."` (L889 & L1810), and `"Generating AI synthesis..."` (L983).
    - Modernize log message at L597: `logger.info(f"[Task] Starting Async PDF assembly for execution {execution_id}")` (replacing `"Koonti"` with `"assembly"`).
  - In synthesis error handler telemetry parity (Discovery XXX):
    - In `generate_profile_synthesis_and_pdf_task` failure catch (L1854-L1864): update both `step_states` and `steps` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True`.

### Component D: Test Suite & Fixture Synchronization
- **[MODIFY]** `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L10-L319]`
  - Update `ExecutionSummarySnapshot` test fixture to use valid SSOT fields (`strictness_level`, `is_ensemble_run`, `is_degraded`, `system_concurrency_snapshot`).
  - Add test group validating `ExecutionSummarySnapshot` positive deserialization, default values, and unrecognized key fail-fast.
  - Add test group validating `WorkflowInputs` positive deserialization, default values, and unrecognized key fail-fast.
  - Add test group validating `ExecutionStep` with typed `Map<String, ScorecardAtomDto> scorecardAtoms`.
- **[NEW]** `@[client_app_v2/test/shared/widgets/execution_timeline_test.dart]`
  - Add widget unit tests for `ExecutionTimeline` verifying rendering across empty, running, failed, and completed `List<ExecutionStep>` states.
  - **Tier 0 Pass 2 Enrichment:** Include test cases for:
    - `ExecutionStep` with `progress: 75` verifying `LinearProgressIndicator` renders with `value: 0.75`.
    - `ExecutionStep` with `hasWarning: true` verifying warning amber icon renders.
    - `ExecutionStep` with `progress: null` (no progress bar).
- **[MODIFY]** `@[backend_v2/tests/unit/services/test_execution.py#L1645-L1678]`
  - Verify that `stream_status` passes `hydrate=False` to `exec_repo.get_execution`.
  - **Tier 0 Pass 2 Enrichment:** Verify that `stream_status` does NOT invoke `check_resumability` during the polling loop.
- **[MODIFY]** `@[backend_v2/tests/unit/test_worker.py]` (CONTEXT — no structural changes, but fixture synchronization required)
  - **Tier 0 Pass 2 Note:** `test_worker.py` contains >30 references to `step_states` dictionaries. After `progress` and `has_warning` fields are added to `ExecutionStep`, worker test fixtures that construct `step_states` with these fields MUST remain functional. No test fixtures need changing because `progress` and `has_warning` have defaults, but the agent executing this plan MUST verify test compatibility.
- **[MODIFY]** `@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L12-L30, #L55]`
  - Update mock `ExecutionClient` methods (`startExecution`, `resumeExecution`, `getExecutionStatus`) from `Future<Map<String, dynamic>>` to `Future<ExecutionRecord>` returning typed test fixtures.
- **[MODIFY]** `@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L40-L50]`
  - Update mock `ExecutionClient` methods (`startExecution`, `resumeExecution`, `getExecutionStatus`) from `Future<Map<String, dynamic>>` to `Future<ExecutionRecord>` returning typed `ExecutionRecord` fixtures (Discovery PP), eliminating compile-time type errors in Dart.
- **[MODIFY]** `@[backend_v2/tests/unit/services/test_execution.py#L1117-L1124]`
  - Update `mock_get_exec` signature in `test_stream_status_handles_error_without_yielding_malformed_execution_record` to accept `hydrate: bool = True, skip_resumability: bool = False, **kwargs: Any` (Discovery NN), preventing keyword argument `TypeError`.

### Component E: Knowledge Base & Architecture Synchronization (Post-Implementation)
- **[MODIFY]** `@[ki_execution_record_ssot.md]`
  - Document the new `ExecutionSummarySnapshot` and `WorkflowInputs` Freezed sub-DTOs, typed `scorecardAtoms: Map<String, ScorecardAtomDto>`, and SSE polling `hydrate=False` performance architecture.
- **[MODIFY]** `@[ki_zero_permissive_typing.md]`
  - Document complete eradication of `Map<String, dynamic>` from `ExecutionRecord`, widget refactoring to typed `ExecutionStep`, and eradication of dead `# noqa: E501` hanging suppressions.
- **[MODIFY]** `@[docs/architecture/01_system_context_and_invariants.md]` (via Tier 7)
  - Synchronize zero-permissive typing invariants and sub-DTO strictness.
- **[MODIFY]** `@[docs/architecture/03_cognitive_orchestration_engine.md]` (via Tier 7)
  - Synchronize SSE stream polling optimization (`hydrate=False`), ExecutionRecord lifecycle, and typed ExecutionTimeline rendering.
- **[MODIFY]** `@[docs/architecture/05_resilience_and_observability.md]` (via Tier 7)
  - Synchronize offloaded blob trace hydration isolation during high-frequency status polling.

---

## 4. Execution Protocol

```xml
<execution_protocol>
  <phase id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <step id="1.0" name="ADD_SSE_FIELDS_TO_EXECUTION_STEP_MODELS">
      <action>
        PREREQUISITE for Step 1.1. Without this step, the timeline refactor will silently lose progress bar and warning icon rendering.

        1. In `@[backend_v2/models/v2_core.py#L1608-L1639]`:
           Add two new fields to `ExecutionStep` BEFORE `scorecard_atoms` using strict PEP 593 `Annotated` syntax per `pydantic_annotated_fields_mandate`:
           - `progress: Annotated[int | None, Field(default=None, ge=0, le=100, description="Step progress percentage for SSE streaming (0-100)")] = None`
           - `has_warning: Annotated[bool, Field(default=False, description="Whether the step completed with warnings")] = False`
        2. In `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-L37]`:
           Add corresponding Freezed fields:
           - `@JsonKey(name: 'progress') int? progress,`
           - `@JsonKey(name: 'has_warning') @Default(false) bool hasWarning,`
        3. FULL-DUPLEX PARITY CHECK: Both new fields have defaults, so existing persisted payloads and `ConfigDict(extra="forbid")` / `disallowUnrecognizedKeys: true` remain backward-compatible without requiring migration.

        **TIER 0 PASS 4 NOTE:** These fields are schema preparation additions with null/false defaults. They will NOT change any currently visible rendering behavior — see Discovery F (Dead Rendering Paths) for full justification.
      </action>
      <constraint>
        MUST be executed BEFORE Step 1.1 to prevent functional regression. Run `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test` after backend change.
      </constraint>
    </step>

    <step id="1.1" name="REFACTOR_EXECUTION_TIMELINE_TO_TYPED_STEPS">
      <action>
        In `@[client_app_v2/lib/shared/widgets/execution_timeline.dart#L4-L207]`:
        1. Replace `final List<Map<String, dynamic>> steps;` with `final List<ExecutionStep> steps;`.
        2. Replace `if (steps.isEmpty) return const SizedBox(width: 0, height: 0);` with `if (steps.isEmpty) return const SizedBox.shrink();` (per `sized_box_shrink_ban` — this is NOT hiding a broken component but handling a legitimately empty list state as the widget's own input contract; the caller at `execution_view.dart#L286` already guards with `if (record.steps.isNotEmpty)` making this check redundant but acceptable as a defensive contract).
        3. Replace `step['status']?.toString().toLowerCase() ?? 'pending'` with `step.status.toLowerCase()`.
        4. Replace `step['label']?.toString() ?? 'Tuntematon askel'` with `step.label`, wrapping the title in `Text(step.label, overflow: TextOverflow.ellipsis)` per `ki_desktop_pro_tool_studio_ux.md` Header & Title Containment mandate, preventing horizontal RenderFlex overflows during desktop window resizing.
        5. Replace `step['last_error']`, `step['message_code']` naked indexing with `step.lastError` and `step.messageCode`. (**Tier 0 Pass 6 Correction:** `step['chunk_count']` was previously listed here but physical `grep_search` confirmed it is NOT accessed anywhere in `execution_timeline.dart` — removed as ghost reference.)
        5a. (**Tier 0 Pass 8 In-Scope Hardening — Canonical Status Enum Parity:**) Standardize status evaluations against canonical `ExecutionStatus` enum values:
            `final isCompleted = stepStatus == 'passed';`
            `final isQueued = stepStatus == 'queued' || stepStatus == 'pending';`
            `final isRunning = stepStatus == 'running';`
            `final isFailed = stepStatus == 'failed' || stepStatus == 'system_error';`
            Eradicate dead string branches: `'finished'`, `'completed'`, `'processing'`, and `'error'` (Discovery KK).
        6. Replace literal hex color `const Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primary`.
            **TIER 0 PASS 4 NOTE (DISCOVERY O):** The existing `const Icon(Icons.check_circle, color: const Color(0xFF2E7D32), size: 20)` at L180 is a deeply nested `const` constructor. Replacing the color with `Theme.of(context).colorScheme.primary` requires removing the `const` keyword from the enclosing `Icon(...)` constructor because `Theme.of(context)` is NOT a const expression. The executing agent MUST transform `const Icon(...)` to `Icon(...)` (non-const) on this line.
        6a. (**Tier 0 Pass 10 Theme Modernization — Discovery WW:**) Replace deprecated `Theme.of(context).primaryColor` at L44 (`labelColor = Theme.of(context).colorScheme.primary;`) and L91 (`color: Theme.of(context).colorScheme.primary,`) with the canonical Flutter 3+ token `Theme.of(context).colorScheme.primary`.
        7. Replace `step['progress'] as num?` with typed `step.progress` (added in Step 1.0 and populated in real-time via DAG executor in Step 1.6).
        8. Replace `step['has_warning'] == true || step['has_warnings'] == true` with typed `step.hasWarning` (added in Step 1.0). The defunct `has_warnings` key variant is eradicated.
      </action>
      <constraint>
        Zero naked maps in UI widgets. Enforce Flutter theme tokens (`colorScheme.primary`, `colorScheme.error`). Adhere strictly to `ki_desktop_pro_tool_studio_ux.md` title containment (`overflow: TextOverflow.ellipsis`), 100% theme tokenization, and zero hardcoded text strings. All formerly dynamic fields resolved via typed dot-notation.
      </constraint>
    </step>

    <step id="1.2" name="DECOUPLE_EXECUTION_VIEW_STEP_STATES_CONVERSION">
      <action>
        In `@[client_app_v2/lib/features/execution/views/execution_view.dart#L105-L110, #L217-L244, #L286-L295]`:
        1. Remove `final stepStatesMap = record.stepStates ?? {};` and `final stepStatesList = ...` (L107-L110).
        1a. Remove unused variable `final frozenContext = record.frozenContext ?? {};` at L105 (Discovery LLL).
        2. In Version Drift Warning Banner (L217-L244): replace naked dict indexing `frozenContext.containsKey('version_id')` and `frozenContext['version_id']?.toString() ?? ''` with typed dot-notation consuming `FrozenContextSnapshot` (Discovery EE & LLL):
           `final versionId = record.frozenContext?.versionId;`
           `if (versionId != null && versionId.isNotEmpty && versionId != 'v2.0.0') ...`
           eliminating all dynamic map lookups and lazy fallbacks.
        3. Update the timeline widget block (L286-L295) to pass `record.steps` directly:
           `if (record.steps.isNotEmpty) SliverToBoxAdapter(child: Padding(..., child: ExecutionTimeline(steps: record.steps, compact: false)))`.
      </action>
      <constraint>
        Eliminate duck-typed map casting (`e is Map ? ... : {}`). 100% typed dot-notation. Zero dynamic map lookups in execution_view.dart.
      </constraint>
    </step>

    <step id="1.3" name="ERADICATE_DEAD_NOQA_SUPPRESSIONS">
      <status>PRE-COMPLETED (Tier 0 Pass 2 Discovery B)</status>
      <action>
        Physical `grep_search` (2026-09-18) confirmed zero `# noqa` matches in:
        1. `@[backend_v2/tests/unit/services/test_execution.py]`
        2. `@[backend_v2/tests/unit/test_executions.py]`
        Dead suppressions have already been cleaned in a prior commit. Skip this step during execution.
      </action>
      <constraint>
        Zero dead noqa suppressions already achieved.
      </constraint>
    </step>

    <step id="1.4" name="DELETE_OBSOLETE_EXECUTION_INPUTS_MODEL">
      <action>
        1. Verify zero remaining imports of `execution_inputs.dart` across `client_app_v2/` (BOTH `lib/` AND `test/`) via `grep_search`. Physical check confirmed the sole import is in `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L3]`.
        2. In `execution_models_test.dart`: update the import at L3 to `package:client_app/features/execution/models/workflow_inputs.dart` and migrate the `ExecutionInputs Freezed Parity` test group at L92-L115 in-place to `WorkflowInputs Freezed Parity` (Discovery UU), asserting roundtrip deserialization and defaults.
        3. Delete `@[client_app_v2/lib/features/execution/models/execution_inputs.dart]`.
        4. Delete generated files: `execution_inputs.freezed.dart` and `execution_inputs.g.dart`.
      </action>
      <constraint>
        Zero orphaned obsolete models. Verify deletion does not break imports. `grep_search` scope MUST cover both `lib/` and `test/` directories.
      </constraint>
    </step>

    <step id="1.5" name="DELETE_DEAD_EXECUTION_STATUS_CARD_WIDGET">
      <action>
        1. Run `grep_search` on `client_app_v2/` (both `lib/` and `test/`) for `ExecutionStatusCard` to confirm zero callers (pre-verified in Discovery BB).
        2. Delete `@[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart]`.
      </action>
      <constraint>
        Zero dead code. Eradicates 241 lines of dead widget code and permanently eliminates the `initialInputs: Map<String, dynamic>` permissive typing violation (Discovery Z).
      </constraint>
    </step>

    <step id="1.6" name="SYNCHRONIZE_DAG_EXECUTOR_AND_WORKER_STEP_PROGRESS_AND_WARNING">
      <action>
        1. In `@[backend_v2/services/orchestrator/dag_executor.py#L87-L118, #L632-L644, #L658-L720, #L740-L755, #L869-L875, #L904-L988, #L1000-L1059]`:
           - In `ExecutionCommitter.commit_trace` (L87-L118):
             Add `steps: list[ExecutionStep] | None = None` parameter and pass `steps=steps` to `ExecutionUpdateDTO(...)` (Discovery SSS).
           - In `_safe_commit()` (L632-L644):
             Pass `steps=current.steps` when invoking `await self._committer.commit_trace(...)`.
           - In exit commits (L1000, L1014, L1035, L1059):
             Pass `steps=exec_record.steps` when calling `await self._committer.commit_trace(...)`.
           - In state transitions inside `_update_lock` (Discovery TTT):
             - Cascading dependency failure (L658-L662):
               ```python
               new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.FAILED})
               new_states = {**exec_record.step_states, step_id: new_state}
               new_steps = [
                   s.model_copy(update={"status": ExecutionStatus.FAILED}) if s.id == step_id else s
                   for s in exec_record.steps
               ]
               exec_record = exec_record.model_copy(update={"step_states": new_states, "steps": new_steps})
               ```
             - Step queued (L702-L704):
               ```python
               new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.QUEUED})
               new_states = {**exec_record.step_states, step_id: new_state}
               new_steps = [
                   s.model_copy(update={"status": ExecutionStatus.QUEUED}) if s.id == step_id else s
                   for s in exec_record.steps
               ]
               exec_record = exec_record.model_copy(update={"step_states": new_states, "steps": new_steps})
               ```
             - Step running in `watch_running` (L716-L720):
               ```python
               new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.RUNNING})
               new_states = {**exec_record.step_states, step_id: new_state}
               new_steps = [
                   s.model_copy(update={"status": ExecutionStatus.RUNNING}) if s.id == step_id else s
                   for s in exec_record.steps
               ]
               exec_record = exec_record.model_copy(update={"step_states": new_states, "steps": new_steps})
               ```
             - In `progress_callback` (L741-L745):
               ```python
               async with _update_lock:
                   new_state = exec_record.step_states[step_id].model_copy(update={"label": label, "progress": prog})
                   new_states = {**exec_record.step_states, step_id: new_state}
                   new_steps = [
                       s.model_copy(update={"label": label, "progress": prog}) if s.id == step_id else s
                       for s in exec_record.steps
                   ]
                   exec_record = exec_record.model_copy(
                       update={"steps": new_steps, "step_states": new_states, "progress": prog, "status_message": label}
                   )
               ```
             - In step completion (L869-L873):
               ```python
               step_status = ExecutionStatus.FAILED if has_error_evt else ExecutionStatus.PASSED
               step_prog = 100 if step_status == ExecutionStatus.PASSED else None
               new_state = exec_record.step_states[step_id].model_copy(
                   update={"status": step_status, "progress": step_prog}
               )
               updates["step_states"] = {**exec_record.step_states, step_id: new_state}
               updates["steps"] = [
                   s.model_copy(update={"status": step_status, "progress": step_prog}) if s.id == step_id else s
                   for s in exec_record.steps
               ]
               ```
             - In step exception catch (L904-L913):
               ```python
               new_state = exec_record.step_states[step_id].model_copy(
                   update={"status": ExecutionStatus.FAILED, "last_error": str(e), "progress": None, "has_warning": True}
               )
               new_states = {**exec_record.step_states, step_id: new_state}
               new_steps = [
                   s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(e), "progress": None, "has_warning": True})
                   if s.id == step_id else s
                   for s in exec_record.steps
               ]
               exec_record = exec_record.model_copy(update={"step_states": new_states, "steps": new_steps})
               ```
             - In virtual RAG preflight step (L934-L940, L972-L980, L984-L988):
               Ensure virtual step is appended or updated in both `step_states` and `steps`.
             - In `ExceptionGroup` cancellation (L1027-L1033):
               Update running steps to `FAILED` in both `step_states` and `steps`.
        2. In `@[backend_v2/worker.py#L351-L397, #L436-L445, #L654-L659, #L695-L705, #L813-L821]`:
           - In fallback step construction (L351-L359):
             Update `ExecutionStep(id=k, label=v.label, status=v.status, scorecard_atoms=v.scorecard_atoms)` to also include `progress=v.progress, has_warning=v.has_warning` (Discovery VV).
           - In the step telemetry aggregation loop upon DAG completion (L360-L397), extract:
             `actual_progress = st_state.progress if st_state else st.progress`
             `actual_warning = st_state.has_warning if st_state else st.has_warning`
             and include `progress: actual_progress` and `has_warning: actual_warning` in `st.model_copy(update={...})` for both telemetry-bearing and non-telemetry steps, ensuring DAG completion does not wipe step progress (Discovery LL).
           - In virtual report render step full-lifecycle telemetry (Discovery MMM & UUU):
             - In initialization (L436-L445 & L813-L821):
               Initialize `ExecutionStep(id=v_step_id, label="Rendering Report", status=ExecutionStatus.RUNNING, progress=0, has_warning=False)`.
             - In completion (L654-L659):
               Update `new_step = old_state.model_copy(update={"status": ExecutionStatus.PASSED, "progress": 100})` and synchronize both `step_states` and `steps` with `progress: 100`.
             - In render failure catch (L695-L705):
               Update both `step_states` and `steps` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True`.
           - In English language modernization (Discovery WWW):
             Replace hardcoded Finnish status strings at L827, L983, L1810 with English:
             - L827: `await _update_render_status("Calculating dynamic results...")`
             - L983: `await _update_render_status("Generating AI synthesis...")`
             - L1810: `await _update_render_status("Compiling output documents...")`
           - In synthesis error handler telemetry parity (Discovery XXX):
             In `generate_profile_synthesis_and_pdf_task` failure catch (L1854-L1864):
             Update both `step_states` and `steps` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True`.
           - In `ExecutionCommitter.commit_trace` None-Guard (Discovery YYY):
             In `dag_executor.py#L110-L117`:
             ```python
             update_data: dict[str, Any] = {
                 "status": status,
                 "execution_trace": trace,
                 "step_states": step_states,
                 "frozen_context": frozen_context,
                 "context_variables": context_variables,
                 "error": error,
             }
             if steps is not None:
                 update_data["steps"] = steps
             update_dto = ExecutionUpdateDTO(**update_data)
             await self.exec_repo.update_execution(self.execution_id, update_dto)
             ```
             preventing accidental `null` overwrites of persisted steps during partial commits.
            - In resumability preflight reset (Discovery AAAA):
              In `dag_executor.py#L618-L627`:
              ```python
              for step_id, s_state in exec_record.step_states.items():
                  if s_state.status == ExecutionStatus.PASSED:
                      step_events[step_id].set()
                  elif s_state.status == ExecutionStatus.FAILED:
                      failed_previous_steps.append(step_id)
                      new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.PENDING})
                      new_states = {**exec_record.step_states, step_id: new_state}
                      new_steps = [
                          s.model_copy(update={"status": ExecutionStatus.PENDING}) if s.id == step_id else s
                          for s in exec_record.steps
                      ]
                      exec_record = exec_record.model_copy(update={"step_states": new_states, "steps": new_steps})
              ```
            - In virtual RAG preflight step appending (Discovery BBBB):
              In `dag_executor.py#L934-L940`:
              ```python
              new_state = ExecutionStepState(
                  id=virtual_step_id, label="system.rag.preflight", status=ExecutionStatus.RUNNING, progress=0, has_warning=False
              )
              new_states = {**exec_record.step_states, virtual_step_id: new_state}
              new_steps = [s for s in exec_record.steps if s.id != virtual_step_id] + [new_state]
              exec_record = exec_record.model_copy(update={"step_states": new_states, "steps": new_steps})
              ```
              and update `pass_state` with `progress: 100, status: ExecutionStatus.PASSED` (L972-L980) and `fail_state` with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True` (L984-L988) across both `step_states` and `steps`.
            - In `ExceptionGroup` cancellation telemetry (Discovery CCCC):
              In `dag_executor.py#L1026-L1034`:
              ```python
              new_states = dict(exec_record.step_states)
              for state_id, state in new_states.items():
                  if state.status == ExecutionStatus.RUNNING:
                      new_states[state_id] = state.model_copy(
                          update={"status": ExecutionStatus.FAILED, "last_error": str(primary_err), "progress": None, "has_warning": True}
                      )
              new_steps = [
                  s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(primary_err), "progress": None, "has_warning": True})
                  if s.status == ExecutionStatus.RUNNING
                  else s
                  for s in exec_record.steps
              ]
              exec_record = exec_record.model_copy(
                  update={"step_states": new_states, "steps": new_steps, "status": ExecutionStatus.FAILED, "error": str(primary_err)}
              )
              ```
            - In initial render step construction defaults (Discovery DDDD):
              In `worker.py#L810-L825`: when `old_state` is None at L813, initialize `ExecutionStep(id=v_step_id, label=msg, status=ExecutionStatus.RUNNING, progress=0, has_warning=False)`.
            - In RAG preflight real-time telemetry and progress emission (Discovery EEEE):
              In `dag_executor.py#L943-L962`:
              ```python
              def _emit_preflight_progress(message: str, pct: int) -> None:
                  exec_record.progress = pct
                  exec_record.status_message = f"Preflight: {message}"
                  new_state = exec_record.step_states[virtual_step_id].model_copy(
                      update={"progress": pct, "label": f"system.rag.preflight: {message}"}
                  )
                  new_states = {**exec_record.step_states, virtual_step_id: new_state}
                  new_steps = [
                      s.model_copy(update={"progress": pct, "label": f"system.rag.preflight: {message}"})
                      if s.id == virtual_step_id
                      else s
                      for s in exec_record.steps
                  ]
                  exec_record = exec_record.model_copy(
                      update={"step_states": new_states, "steps": new_steps, "progress": pct, "status_message": f"Preflight: {message}"}
                  )
              ```
            - In virtual system step prefix canonicalization (Discovery FFFF):
              In `dag_executor.py#L932`:
              `virtual_step_id = f"sys_rag_{uuid.uuid4().hex[:16]}"` (standardizing on `sys_` prefix rather than `stp_`).
            - In unexpected non-ExceptionGroup exception handling (Discovery GGGG):
              In `dag_executor.py#L1054-L1066`:
              ```python
              new_states = dict(exec_record.step_states)
              for state_id, state in new_states.items():
                  if state.status == ExecutionStatus.RUNNING:
                      new_states[state_id] = state.model_copy(
                          update={"status": ExecutionStatus.FAILED, "last_error": str(unexpected_err), "progress": None, "has_warning": True}
                      )
              new_steps = [
                  s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(unexpected_err), "progress": None, "has_warning": True})
                  if s.status == ExecutionStatus.RUNNING
                  else s
                  for s in exec_record.steps
              ]
              exec_record = exec_record.model_copy(
                  update={"step_states": new_states, "steps": new_steps, "status": ExecutionStatus.FAILED, "error": str(unexpected_err)}
              )
              await committer.commit_trace(
                  status=ExecutionStatus.FAILED,
                  error=str(unexpected_err),
                  steps=exec_record.steps,
              )
              ```
            - In complete English worker modernization (Discovery HHHH):
              In `worker.py#L597`: `logger.info("Starting Async PDF assembly...")` (modernizing `"Koonti"` -> `"assembly"`).
              In `worker.py#L889`: `status_message="Compiling output documents..."` (modernizing `"Koostetaan tulosteita valmiiksi..."` -> `"Compiling output documents..."`).
      </action>
      <constraint>
        Live per-step progress and status populated in real-time. Zero dead rendering paths. Synchronous step states and steps arrays preserved through DAG execution, resumability reset, intermediate database commits, worker fallback construction, report rendering, exception cancellation, and worker termination. 100% English codebase compliance. `ExecutionCommitter` None-guard prevents partial commit step overwrites.
      </constraint>
    </step>
  </phase>

  <phase id="2" name="BACKEND_SSE_POLLING_OPTIMIZATION">
    <step id="2.1" name="OPTIMIZE_SSE_STREAM_STATUS_POLLING">
      <action>
        In `@[backend_v2/services/execution.py#L239-L332]`:
        1. Update `get_execution` signature to accept `hydrate: bool = True` and `skip_resumability: bool = False`:
           ```python
           async def get_execution(
               self,
               initiator: TokenData,
               execution_id: str,
               hydrate: bool = True,
               skip_resumability: bool = False,
           ) -> ExecutionRecord:
           ```
        2. In `stream_status` (L286-L312):
           - Bind `max_retries = get_settings().sse_max_transient_retries` (eradicating hardcoded magic number `max_retries = 3`).
           - Update polling query:
             `record = await self.get_execution(initiator=initiator, execution_id=execution_id, hydrate=False, skip_resumability=True)`.
           - Update payload serialization:
             `yield f"data: {record.model_dump_json(exclude_none=True)}\n\n"` (Discovery II).
           - Update sleep intervals at BOTH line 300 and line 311:
             `await asyncio.sleep(get_settings().sse_polling_interval_seconds)` (Discoveries HH & JJJJ), completely eliminating `settings.llm_retry_delay` from status streaming.
        3. Keep the INITIAL authorization call at L282 with full hydration/resumability:
           `await self.get_execution(initiator=initiator, execution_id=execution_id)` (defaults to hydrate=True, skip_resumability=False).
      </action>
      <constraint>
        Prevents reading multi-megabyte frozen_context and execution_trace blob files on every SSE polling pulse. Eliminates redundant `check_resumability` per-pulse queries. Excludes null keys. Slashes polling delay from 10s to 2s across polling loop and transient retry backoff.
      </constraint>
    </step>

    <step id="2.2" name="HARDEN_CHECK_RESUMABILITY_AND_FACTORY_TYPING">
      <action>
        0. In `@[backend_v2/services/execution.py#L16]`:
           Update import to `from pydantic import TypeAdapter, ValidationError` (Discovery IIII), guaranteeing immediate compilation when `TypeAdapter` is referenced.
        1. In `@[backend_v2/services/execution.py#L131-L137]`:
           Eradicate `isinstance(resolved_metadata, dict)` duck-typing, delete `# noqa: QGR012` suppression, and eliminate lazy fallback `or` from `create_execution_record` (Discoveries NNN & VVV):
           ```python
           raw_meta = metadata if metadata is not None else extra_persistence_fields.pop("metadata", None)
           resolved_metadata = (
               TypeAdapter(ExecutionMetadata).validate_python(raw_meta)
               if raw_meta is not None
               else ExecutionMetadata()
           )
           ```
        2. In `@[backend_v2/services/execution.py#L665-L682]`:
           - In step set parity validation (L667, Discovery FFFF):
             Update filter to exclude all virtual system steps (`sys_*` and `system.rag.preflight`):
             ```python
             workflow_step_ids = {step.id for step in workflow.steps}
             exec_step_ids = {
                 k for k, s in record.step_states.items()
                 if not k.startswith("sys_") and getattr(s, "label", None) != "system.rag.preflight"
             }
             if workflow_step_ids != exec_step_ids:
                 return False
             ```
           - In workflow version drift validation (L671-L682, Discovery JJ):
             Eradicate `isinstance(record.metadata, dict)` and `.get("workflow_version")` duck-typing, and delete dead `# noqa: QGR012` suppression.
             Replace with strict typed dot-notation:
             ```python
             orig_version: int | None = None
             if record.metadata is not None:
                 orig_version = record.metadata.workflow_version
             elif record.workflow_version is not None:
                 orig_version = record.workflow_version
             if orig_version is not None and workflow.version != orig_version:
                 return False
             ```
      </action>
      <constraint>
        100% typed dot-notation and TypeAdapter validation with zero lazy fallback chains. Excludes all virtual system steps from resumability step parity checks. Eradicates `# noqa: QGR012` suppressions across factory and resumability boundaries in `services/execution.py`.
      </constraint>
    </step>

    <step id="2.3" name="ADD_SSE_SETTINGS_TO_SETTINGS_PY">
      <action>
        In `@[backend_v2/settings.py#L309-L315]`:
        Add typed settings fields with validators:
        ```python
        sse_max_transient_retries: Annotated[
            int,
            Field(default=3, ge=1, le=10, description="Maximum transient retry count for SSE polling"),
        ] = 3
        sse_polling_interval_seconds: Annotated[
            float,
            Field(default=2.0, gt=0.0, le=30.0, description="Polling interval in seconds for SSE execution status stream"),
        ] = 2.0
        ```
      </action>
      <constraint>
        SSOT configuration in `settings.py`. Zero magic numbers in service method bodies.
      </constraint>
    </step>

    <step id="2.4" name="HARDEN_CONTEXT_VARIABLES_AND_MATH_UTILS_RESOLVER">
      <action>
        1. In `@[backend_v2/models/v2_core.py]`:
           Define `EvaluatedMatrixContextDTO`:
           ```python
           class EvaluatedMatrixContextDTO(BaseModel):
               """DTO for evaluated matrix context within execution context_variables."""
               model_config = ConfigDict(strict=True, extra="forbid")
               evaluated_atoms: Annotated[
                   dict[str, str],
                   Field(default_factory=dict, description="Map of atom IDs to evaluation status"),
               ]
               raw_atoms: Annotated[
                   list[dict[str, Any]],
                   Field(default_factory=list, description="Raw evaluated atom payloads"),
               ]
           ```
        2. In `@[backend_v2/services/execution.py#L1095-L1105]`:
           Refactor `override_atom` to eliminate duck-typing and `# noqa: QGR012` suppression (Discovery KKKK):
           ```python
           for _k, v in record.context_variables.items():
               try:
                   matrix_ctx = TypeAdapter(EvaluatedMatrixContextDTO).validate_python(v)
               except ValidationError:
                   continue
               if atom_id in matrix_ctx.evaluated_atoms:
                   matrix_ctx.evaluated_atoms[atom_id] = payload.new_status
                   for ra in matrix_ctx.raw_atoms:
                       if ra.get("tda_id") == atom_id or ra.get("atom_id") == atom_id:
                           ra["human_override"] = payload.new_status
                   if isinstance(v, collections.abc.MutableMapping):
                       v["evaluated_atoms"] = matrix_ctx.evaluated_atoms
                       v["raw_atoms"] = matrix_ctx.raw_atoms
           ```
           permanently eliminating `isinstance(v, dict)` and `# noqa: QGR012`.
        3. In `@[backend_v2/utils/math_utils.py#L186-L222]`:
           Refactor `resolve_dot_notation` from generic duck-typing reflection to typed traversal (Discovery LLLL):
           ```python
           def resolve_dot_notation(state: Any, path: str) -> Any:
               """Safely resolves a dot-notation path against a state mapping, sequence, or model.

               Uses strictly typed iterative traversal. Never uses eval, exec, dict.get, or getattr.
               Raises MissingInputMappingError on any resolution failure.
               """
               if not path:
                   return state

               parts = path.split(".")
               curr = state

               for part in parts:
                   try:
                       match curr:
                           case collections.abc.Mapping():
                               curr = curr[part]
                           case collections.abc.Sequence() if not isinstance(curr, (str, bytes)):
                               curr = curr[int(part)]
                           case BaseModel():
                               if part in curr.model_fields:
                                   curr = curr.__dict__[part]
                               else:
                                   raise KeyError(part)
                           case _:
                               curr = object.__getattribute__(curr, part)
                   except (KeyError, AttributeError, IndexError, ValueError) as e:
                       raise MissingInputMappingError(
                           path=path, state_type=type(curr).__name__, reason=f"Failed at '{part}': {type(e).__name__}"
                       ) from e

               return curr
           ```
           permanently eliminating `isinstance(curr, dict)`, `getattr(curr, part)`, and `# noqa: QGR012` and `# noqa: QGR001` suppressions.
      </action>
      <constraint>
        Zero duck-typing, zero reflection (`getattr`), zero naked dictionary assumptions, and zero `# noqa` suppressions. 100% typed Pydantic and standard collections traversal per `ki_zero_permissive_typing.md`.
      </constraint>
    </step>
  </phase>

  <phase id="3" name="CLIENT_SUB_DTO_CREATION_AND_STRICT_TYPING">
    <step id="3.0" name="CONFIGURE_FLUTTER_ANALYSIS_OPTIONS">
      <action>
        1. Create [NEW] `@[client_app_v2/analysis_options.yaml]` with canonical analyzer settings:
           ```yaml
           include: package:flutter_lints/flutter.yaml

           analyzer:
             errors:
               invalid_annotation_target: ignore
           ```
        2. In all modified Freezed model files (`@[client_app_v2/lib/features/execution/models/execution_record.dart]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart]`), ensure zero `// ignore_for_file: invalid_annotation_target` suppressions are introduced or preserved.
      </action>
      <constraint>
        Centralized Single Source of Truth for Dart analyzer. Eliminates the root cause of `invalid_annotation_target` warnings across all Freezed models, permanently deprecating file-level ignore directives.
      </constraint>
    </step>

    <step id="3.1" name="CREATE_EXECUTION_SUMMARY_SNAPSHOT_DTO">
      <action>
        Create [NEW] `@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart#L1-L35]` with `@Freezed(equal: false)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`.
        Fields:
        - `@JsonKey(name: 'strictness_level') @Default(100) int strictnessLevel,`
        - `@JsonKey(name: 'is_ensemble_run') @Default(false) bool isEnsembleRun,`
        - `@JsonKey(name: 'is_degraded') @Default(false) bool isDegraded,`
        - `@JsonKey(name: 'system_concurrency_snapshot') @Default({}) Map<String, int> systemConcurrencySnapshot,`
      </action>
      <constraint>
        Must match backend `ExecutionSummarySnapshot` in `backend_v2/models/v2_core.py#L1644-L1655`.
      </constraint>
    </step>

    <step id="3.2" name="CREATE_WORKFLOW_INPUTS_DTO">
      <action>
        Create [NEW] `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart#L1-L35]` with `@Freezed(equal: false)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`.
        Fields:
        - `@JsonKey(name: 'organization_id') String? organizationId,`
        - `@JsonKey(name: 'user_id') String? userId,`
        - `@JsonKey(name: 'simulation_mode') @Default(false) bool simulationMode,`
        - `@Default('en') String language,`
        - `@JsonKey(name: 'dynamic_inputs') @Default({}) Map<String, dynamic> dynamicInputs,`
      </action>
      <constraint>
        Must match backend `WorkflowInputs` in `backend_v2/models/domain/inputs.py#L32-L91`.
      </constraint>
    </step>

    <step id="3.3" name="HARDEN_EXECUTION_STEP_AND_RECORD_MODELS">
      <action>
        1. In `@[client_app_v2/lib/features/execution/models/execution_step.dart#L8-L37]`:
           Import `matrix_scorecard_dto.dart` and update `scorecardAtoms` field:
           `@JsonKey(name: 'scorecard_atoms') @Default({}) Map<String, ScorecardAtomDto> scorecardAtoms,`
        2. In `@[client_app_v2/lib/features/execution/models/execution_record.dart#L16-L89]`:
           Modernize stale docstring at L16-L17 referencing "De-Generator Mandate" (Discovery JJJ).
           Import `execution_summary_snapshot.dart`, `workflow_inputs.dart`, and `frozen_context_snapshot.dart`.
           Update fields:
           - `@JsonKey(name: 'execution_summary') ExecutionSummarySnapshot? executionSummary,`
           - `@JsonKey(name: 'raw_inputs') WorkflowInputs? rawInputs,`
           - `@JsonKey(name: 'models_used') Map<String, int>? modelsUsed,`
           - `@JsonKey(name: 'frozen_context') FrozenContextSnapshot? frozenContext,`
           - `@JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates,`
      </action>
      <constraint>
        Maintain `@JsonSerializable(disallowUnrecognizedKeys: true)`. Zero permissive typing. Achieve 100% cross-domain parity with Python backend models.
      </constraint>
    </step>

    <step id="3.4" name="ERADICATE_DE_GENERATOR_POLICY_AND_TYPIFY_EXECUTION_CLIENT">
      <action>
        1. In `@[client_app_v2/lib/core/api/execution_client.dart#L14-L52]`:
           - Remove obsolete docstring referencing the "De-Generator Policy" (L16-L17).
           - Import `package:client_app/features/execution/models/execution_record.dart`.
           - Update return types of `startExecution`, `resumeExecution`, and `getExecutionStatus` from `Future<Map<String, dynamic>>` to `Future<ExecutionRecord>`.
           - Implement direct JSON deserialization at the client boundary:
             `return ExecutionRecord.fromJson(response.data as Map<String, dynamic>);`
        2. In `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L49, #L83-L89, #L124-L127]`:
           - Remove obsolete De-Generator Policy docstring reference at L49.
           - In `startExecution` (L83-L89): replace `final executionId = initialRecord['id'] as String;` with `final executionId = initialRecord.id;`, and replace `state = AsyncValue.data(ExecutionRecord.fromJson(initialRecord));` with `state = AsyncValue.data(initialRecord);`.
           - In `resumeExecution` (L124-L127): replace `state = AsyncValue.data(ExecutionRecord.fromJson(resumedRecord));` with `state = AsyncValue.data(resumedRecord);`.
        3. In `@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L62-L68]`:
           - In `startExecution`: replace `final executionId = response['id']?.toString() ?? '';` with `final executionId = response.id;`.
      </action>
      <constraint>
        100% typed transit across network client and controller. Zero naked map indexing (`initialRecord['id']`) in controllers.
      </constraint>
    </step>

    <step id="3.5" name="CREATE_FROZEN_CONTEXT_SNAPSHOT_DTO">
      <action>
        Create [NEW] `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart#L1-L45]` with `@Freezed(equal: false)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`.
        Fields with multi-payload parity:
        - `@JsonKey(name: 'version_id') String? versionId,`
        - `@JsonKey(name: 'workflow_id') String? workflowId,`
        - `@JsonKey(name: 'workflow_name') String? workflowName,`
        - `@JsonKey(name: 'organization_id') String? organizationId,`
        - `@JsonKey(name: 'user_id') String? userId,`
        - `@JsonKey(name: 'created_at') String? createdAt,`
        - `@JsonKey(name: 'compiled_prompts') @Default({}) Map<String, String> compiledPrompts,`
        - `@JsonKey(name: 'injected_theory') @Default({}) Map<String, dynamic> injectedTheory,`
        - `@JsonKey(name: 'generated_schemas') @Default({}) Map<String, dynamic> generatedSchemas,`
        - `@JsonKey(name: 'ui_hints_snapshot') @Default({}) Map<String, dynamic> uiHintsSnapshot,`
        - `@JsonKey(name: 'mcp_tool_audit') @Default([]) List<Map<String, dynamic>> mcpToolAudit,`
      </action>
      <constraint>
        Matches backend `FrozenContext` in `backend_v2/models/v2_core.py#L1548-L1562` while providing typed access to `versionId` for `execution_view.dart#L217-L244` and `sse_client.dart#L70-L72`. Zero unrecognized-key crashes during direct REST calls (`CheckedFromJsonException` prevented).
      </constraint>
    </step>
  </phase>

  <phase id="4" name="CODE_GENERATION_AND_TEST_SYNCHRONIZATION">
    <step id="4.1" name="RUN_BUILD_RUNNER_GENERATION">
      <action>
        Run build_runner in client_app_v2:
        `dart run build_runner build --delete-conflicting-outputs`
      </action>
      <constraint>
        Zero code generator conflicts or errors.
      </constraint>
    </step>

    <step id="4.2" name="SYNCHRONIZE_TEST_FIXTURES_AND_EXPAND_ISTQB">
      <action>
        In `@[client_app_v2/test/features/execution/models/execution_models_test.dart#L10-L319]`:
        1. Update `test_flutter_execution_record_deserializes_sse_payload_with_workflow_version_and_execution_summary`:
           Replace invalid `{'total_steps': 5, 'completed_steps': 2}` with valid `ExecutionSummarySnapshot` JSON:
           `{'strictness_level': 70, 'is_ensemble_run': true, 'is_degraded': false, 'system_concurrency_snapshot': {'LLM_MAX_CHUNK_SIZE': 5000}}`.
        1a. In `test_flutter_execution_record_deserializes_all_fields_successfully` (L211): update `'frozen_context': <String, dynamic>{'input': 'content'}` to `'frozen_context': {'version_id': 'v2.0.0'}` (Discovery QQ), preventing `CheckedFromJsonException`.
        2. Add ISTQB tests:
           - `ExecutionSummarySnapshot` positive deserialization and defaults.
           - `ExecutionSummarySnapshot` unrecognized key fail-fast.
           - `WorkflowInputs` positive deserialization and defaults.
           - `WorkflowInputs` unrecognized key fail-fast.
           - `FrozenContextSnapshot` positive deserialization with `version_id` and backend fields.
           - `FrozenContextSnapshot` unrecognized key fail-fast.
           - `ExecutionStep` with typed `Map<String, ScorecardAtomDto> scorecardAtoms`.
           - `ExecutionStep.scorecardAtoms` unrecognized key in atom throws `CheckedFromJsonException`.
           - `ExecutionRecord` deserialization with `FrozenContextSnapshot` and typed `stepStates: Map<String, ExecutionStep>`.
        3. Create [NEW] `@[client_app_v2/test/shared/widgets/execution_timeline_test.dart]` verifying `ExecutionTimeline` with `List<ExecutionStep>`.
        4. Update `@[backend_v2/tests/unit/services/test_execution.py#L1645-L1678]` asserting `stream_status` calls `get_execution(..., hydrate=False)`.
        4a. In `@[backend_v2/tests/unit/services/test_execution.py#L1117-L1124]`: update `mock_get_exec` signature to `async def mock_get_exec(initiator: Any, execution_id: str, hydrate: bool = True, skip_resumability: bool = False, **kwargs: Any) -> Any:` (Discovery NN), preventing keyword argument `TypeError`.
        5. In `@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L10-L75]`:
           Update `MockExecutionClient` methods (Discovery TT) to return typed `ExecutionRecord` fixtures:
           - `startExecution`: `return ExecutionRecord(id: 'test_exec', workflowId: request.workflowId, targetLocale: request.targetLocale, status: 'RUNNING');`
           - `resumeExecution`: `return ExecutionRecord(id: executionId, workflowId: 'test_wf', targetLocale: 'fi', status: 'RUNNING');`
           - `getExecutionStatus`: `return ExecutionRecord(id: executionId, workflowId: 'test_wf', targetLocale: 'fi', status: 'PASSED');`
        5a. In `@[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L8, #L40-L50]`:
           Update `MockExecutionClientPending` methods (Discovery PP & XX) to return typed `ExecutionRecord` fixtures:
           - `startExecution`: `async => ExecutionRecord(id: 'test_exec', workflowId: 'test_wf', targetLocale: 'en', status: 'PASSED');`
           - `resumeExecution`: `async => ExecutionRecord(id: executionId, workflowId: 'test_wf', targetLocale: 'en', status: 'PASSED');`
           - `getExecutionStatus`: `async => ExecutionRecord(id: executionId, workflowId: 'test_wf', targetLocale: 'en', status: 'PASSED');`
      </action>
      <constraint>
        100% test pass rate across unit test suite. Zero mock signature desynchronizations.
      </constraint>
    </step>
  </phase>

  <phase id="5" name="UNIVERSAL_QUALITY_GATE_AND_PERSISTENCE">
    <step id="5.1" name="RUN_QUALITY_GATES">
      <action>
        1. Run Backend audit loop:
           `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test`
        2. Run Flutter audit loop:
           `uv run python scripts/flutter_audit_loop.py client_app_v2/`
      </action>
      <constraint>
        Both quality loops MUST pass with exit code 0.
      </constraint>
    </step>

    <step id="5.2" name="ATOMIC_GIT_COMMIT">
      <action>
        Instruct user to execute atomic commit:
        `git add client_app_v2/ backend_v2/models/v2_core.py backend_v2/settings.py backend_v2/services/execution.py backend_v2/services/orchestrator/dag_executor.py backend_v2/worker.py backend_v2/utils/math_utils.py backend_v2/tests/unit/services/test_execution.py backend_v2/tests/unit/utils/test_math_utils.py docs/implementationplans/`
        `git commit -m "refactor(execution): harden ExecutionRecord sub-DTOs, optimize SSE polling, and eradicate dead code and de-generator untyped client"`
      </action>
      <constraint>
        Strict Conventional Commits format in English.
      </constraint>
    </step>
  </phase>

  <phase id="6" name="POST_IMPLEMENTATION_REVIEW_KI_UPDATES_AND_TIER7_SYNC">
    <step id="6.1" name="AUDIT_CODE_DIFFS_AND_CHANGE_REVIEW">
      <action>
        Perform forensic review of all physical changes across Python backend, Flutter frontend, and test suites:
        1. Verify elimination of permissive maps in Flutter `ExecutionRecord` (`execution_summary`, `raw_inputs`).
        2. Verify elimination of dead `# noqa: E501` comments in `test_execution.py` and `test_executions.py`.
        3. Verify `hydrate=False` in SSE stream polling in `backend_v2/services/execution.py`.
        4. Verify `ExecutionTimeline` pure `List<ExecutionStep>` implementation.
        5. Verify complete deletion of dead `ExecutionStatusCard` widget (zero remaining references across codebase).
        6. Verify `ExecutionClient` returns `Future<ExecutionRecord>` and `ExecutionController` consumes typed `record.id`.
      </action>
      <constraint>
        100% compliance with zero permissive typing and no hanging noqa suppressions.
      </constraint>
    </step>

    <step id="6.2" name="UPDATE_KNOWLEDGE_ITEMS">
      <action>
        Update the following Knowledge Items in the knowledge base:
        1. `@[ki_execution_record_ssot.md]`: Document the new `ExecutionSummarySnapshot` and `WorkflowInputs` Freezed sub-DTOs, `scorecardAtoms: Map<String, ScorecardAtomDto>`, and SSE polling `hydrate=False` performance architecture.
        2. `@[ki_zero_permissive_typing.md]`: Document the complete eradication of `Map<String, dynamic>` from `ExecutionRecord` sub-fields, the timeline widget refactoring to typed `ExecutionStep`, and the eradication of dead `# noqa: E501` hanging suppressions.
      </action>
      <constraint>
        Update KI artifacts directly before executing Tier 7 architecture sync.
      </constraint>
    </step>

    <step id="6.3" name="EXECUTE_TIER7_ARCHITECTURE_SYNC">
      <action>
        Execute `/tier7-describe-architecture` for target architectural pillar documents in `@[docs/architecture/]`:
        1. `@[docs/architecture/01_system_context_and_invariants.md]`: Synchronize zero-permissive typing invariants and sub-DTO strictness.
        2. `@[docs/architecture/03_cognitive_orchestration_engine.md]`: Synchronize SSE stream polling optimization (`hydrate=False`), ExecutionRecord lifecycle, and typed ExecutionTimeline rendering.
        3. `@[docs/architecture/05_resilience_and_observability.md]`: Synchronize offloaded blob trace hydration isolation during high-frequency status polling.
      </action>
      <constraint>
        Enforce timeless present-tense format (no historical phases, no Law labels, no changelogs) as mandated by Tier 7.
      </constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## 5. Verification Plan

### Automated Tests
- `uv run ruff check backend_v2/tests/unit/services/test_execution.py backend_v2/tests/unit/test_executions.py` (NOTE: noqa already clean — this is a confirmation gate)
- `uv run pytest backend_v2/tests/unit/services/test_execution.py -k test_stream_status`
- `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test` (verifies `progress` and `has_warning` field additions)
- `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/utils/math_utils.py --test`
- `uv run pytest backend_v2/tests/unit/utils/test_math_utils.py`
- `flutter test test/features/execution/models/execution_models_test.dart`
- `flutter test test/shared/widgets/execution_timeline_test.dart`
- `flutter test test/features/execution/controllers/execution_controller_test.dart`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/`
- `grep_search` on `client_app_v2/` for `execution_inputs.dart` (must return ZERO results after deletion)
- `grep_search` on `client_app_v2/` for `execution_status_card.dart` (must return ZERO results after deletion)

### Manual / E2E Verification
- Open `Aktiivinen Suoritus` view in Flutter desktop and verify live execution stream connects and renders `ExecutionTimeline` using typed `record.steps` without `CheckedFromJsonException` or UI jank.
- Verify the progress bar (`LinearProgressIndicator`) renders correctly during active step execution and transitions to 100% upon step completion.

### 5.3 Documented Technical Debt & Pass 9 In-Scope Resolutions
- **`execution_view.dart#L105, #L217-L244` (Discovery E & MM — RESOLVED IN PASS 8/9):** Brought fully in-scope via [NEW] `FrozenContextSnapshot` Freezed model (`frozen_context_snapshot.dart`). Configured with multi-payload parity (declaring both `versionId` and backend `FrozenContext` fields `compiledPrompts`, `injectedTheory`, `generatedSchemas`, `uiHintsSnapshot`, `mcpToolAudit` with `@Default` annotations) to prevent `CheckedFromJsonException` during direct REST calls. Consumed via typed dot-notation `record.frozenContext?.versionId`. Zero naked map indexing remaining.
- **`execution_view.dart#L61, #L107` (Discovery FF — RESOLVED IN PASS 8):** Brought fully in-scope via typed `@JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates` on `ExecutionRecord`. 1:1 cross-domain parity with backend `dict[str, ExecutionStepState]`.
- **Per-step `progress` population (Discovery F, GG & LL — RESOLVED IN PASS 8/9):** Brought fully in-scope via `dag_executor.py#L741-L745` (`progress_callback` updates active step `progress: prog` in both `step_states` and `steps`), step completion hook (`progress: 100` for passed steps), and `worker.py#L360-L397` telemetry rebuild preserving `progress: actual_progress` and `has_warning: actual_warning`. Timeline `LinearProgressIndicator` is 100% active in real-time and permanently preserved through DAG termination.
- **Lightweight SSE status-only query (Discovery K):** Evaluated and clarified: `get_execution(hydrate=False, skip_resumability=True)` is the exact mathematical optimal point for status streaming, delivering live step states, duration, and token telemetry without disk blob hydration. Full status-only query (`str`) would starve UI of telemetry.
- **`max_retries = 3` Magic Number in SSE Loop (Discovery M & HH — RESOLVED IN PASS 8):** Brought fully in-scope via `settings.sse_max_transient_retries: int = 3` in `settings.py`. Zero magic numbers.
- **`llm_retry_delay` Semantic Mismatch for SSE Polling (Discovery N & HH — RESOLVED IN PASS 8):** Brought fully in-scope via `settings.sse_polling_interval_seconds: float = 2.0` in `settings.py`. Decouples SSE streaming from LLM retry backoff and provides responsive 2.0s UI updates.
- **`model_dump_json()` Without `exclude_none=True` in SSE Payload (Discovery P & II — RESOLVED IN PASS 8):** Brought fully in-scope via `record.model_dump_json(exclude_none=True)` in `services/execution.py#L295`.
- **`check_resumability` Permissive Typing Violations (Discovery R & JJ — RESOLVED IN PASS 8):** Brought fully in-scope via elimination of `isinstance(dict)` duck-typing and removal of dead `# noqa: QGR012` suppression in `services/execution.py#L671-L682`.
- **Flutter `ExecutionRecord.executionTrace` (Discovery S):** Preserved as raw transit / cloud storage offload metadata (`executionTraceStoragePath`). Full trace models (`TraceEvent`) reside on backend FinOps audit layer, keeping client isolate lightweight.
- **Undocumented `'processing'` Status String Literal (Discovery T & KK — RESOLVED IN PASS 8):** Brought fully in-scope via standardization against canonical `ExecutionStatus` enum values in `execution_timeline.dart`. Dead string variant removed.
- **Dead Status String Variants `'finished'`, `'completed'`, `'error'` (Discovery X & KK — RESOLVED IN PASS 8):** Brought fully in-scope via standardization against canonical `ExecutionStatus` enum values in `execution_timeline.dart`. Dead string variants removed.
- **`ExecutionStatusCard.initialInputs` Naked Dict (Discovery Z & BB — RESOLVED IN PASS 7/8):** Resolved in scope via complete file deletion in Phase 1 Step 1.5. 241 lines of dead code eradicated. Zero remaining usages.
- **`mock_get_exec` Keyword Arguments Mismatch (Discovery NN — RESOLVED IN PASS 9):** Resolved in scope via signature update in `test_execution.py#L1117-L1124`.
- **PEP 593 `Annotated` Syntax on `ExecutionStep` (Discovery OO — RESOLVED IN PASS 9):** Enforced strictly on `backend_v2/models/v2_core.py#L1608-L1639`.
- **Mock `ExecutionClient` Parity in `report_controller_test.dart` (Discovery PP — RESOLVED IN PASS 9):** Resolved in scope via typed `ExecutionRecord` returns in `report_controller_test.dart#L40-L50`.
- **`execution_models_test.dart#L211` Fixture Parity (Discovery QQ — RESOLVED IN PASS 9):** Resolved in scope via valid `FrozenContextSnapshot` JSON fixture.
- **Native `hydrate=True` Parameter in `ExecutionRepository` (Discovery RR — RESOLVED IN PASS 10):** Verified native `hydrate: bool = True` support in `execution.py#L174`, enabling zero-change repository delegation from `ExecutionService.get_execution`.
- **Initial SSE Handshake vs Polling Isolation (Discovery SS — RESOLVED IN PASS 10):** Verified initial connection authorization at L282 uses full `hydrate=True, skip_resumability=False` while polling at L291 uses `hydrate=False, skip_resumability=True`.
- **Mock `ExecutionClient` Parity in `execution_controller_test.dart` (Discovery TT — RESOLVED IN PASS 10):** Resolved in scope via typed `ExecutionRecord` returns across all 3 mock methods (`startExecution`, `resumeExecution`, `getExecutionStatus`).
- **`WorkflowInputs Freezed Parity` Test Migration (Discovery UU — RESOLVED IN PASS 10):** Resolved in scope via in-place migration of `execution_models_test.dart#L92-L115` test group.
- **`worker.py#L351-L359` Fallback Step Construction Preservation (Discovery VV — RESOLVED IN PASS 10):** Resolved in scope via explicit `progress=v.progress, has_warning=v.has_warning` in fallback `ExecutionStep` constructor.
- **Timeline Theme Property Modernization (Discovery WW — RESOLVED IN PASS 10):** Resolved in scope via modernization of deprecated `primaryColor` to `Theme.of(context).colorScheme.primary` across `execution_timeline.dart#L44, #L91`.
- **`MockExecutionClientPending` Class Name Precision (Discovery XX — RESOLVED IN PASS 11):** Documented exact AST class name `MockExecutionClientPending` at `report_controller_test.dart#L8` for unambiguous Step 4.2 mock method signature targeting.
- **Dead `getScorecard` Test Mock Method Identification (Discovery YY — RESOLVED IN PASS 11):** Identified un-annotated `getScorecard` method across `MockExecutionClientPending` and `MockExecutionClient` as harmless legacy mock dead code that does not exist on `ExecutionClient`.
- **`SseClient` Delta Signal `frozen_context` Isolation Parity (Discovery ZZ — RESOLVED IN PASS 11):** Verified `sse_client.dart#L67-L73` delta transformation isolating `version_id`, validating `FrozenContextSnapshot`'s multi-payload parity across delta SSE chunks and full REST responses.
- **In-Memory Repository Fake `hydrate` Signature Parity (Discovery AAA — RESOLVED IN PASS 11):** Verified native `hydrate: bool = True` support in `in_memory_repositories.py#L165, #L1291`, guaranteeing zero fake repository divergence when `ExecutionService.get_execution` forwards `hydrate=hydrate`.
- **Desktop Pro Tool Studio UX & Title Containment (Discovery BBB — RESOLVED IN PASS 12):** Enforced `ki_desktop_pro_tool_studio_ux.md` Title Containment (`overflow: TextOverflow.ellipsis`) on `ExecutionTimeline`, eliminating horizontal RenderFlex risk on desktop viewports < 900px, eradicating hardcoded fallback text `'Tuntematon askel'` in favor of domain SSOT `step.label`, and adhering to serialization-based dirty state checking for `@Freezed(equal: false)` entities.
- **`SseClient` Delta Signal Deserialization Lifecycle (Discovery CCC — RESOLVED IN PASS 13):** Verified `sse_client.dart#L67-L73` isolate delta parsing and validated `FrozenContextSnapshot` multi-payload schema parity across both delta SSE updates and full REST endpoints.
- **`ExecutionService.get_execution` Default Parameter Invariants (Discovery DDD — RESOLVED IN PASS 13):** Verified that `get_execution(..., hydrate=True, skip_resumability=False)` defaults guarantee zero regression across all existing FastAPI routers, service callers, and unit tests.
- **Exact AST Verification of `ExecutionTimeline` Scope (Discovery EEE — RESOLVED IN PASS 13):** Confirmed `ExecutionTimeline` has exactly 1 production caller (`execution_view.dart#L293`), guaranteeing zero blast radius outside `execution_view.dart`.
- **Exact AST Verification of `ExecutionClient` Mock Interfaces (Discovery FFF — RESOLVED IN PASS 13):** Confirmed that exactly 2 test mock classes implement `ExecutionClient` (`MockExecutionClient` and `MockExecutionClientPending`), both targeted for signature updates in Step 4.2.
- **Canonical Status Evaluation Invariants (Discovery GGG — RESOLVED IN PASS 13):** Enforced canonical status evaluation in `execution_timeline.dart`, eliminating dead status string variants.
- **`IExecutionRepository` Native Interface Parity (Discovery HHH — RESOLVED IN PASS 14):** Verified native `hydrate: bool = True` support in `database/interfaces.py#L89`, confirming that the entire repository layer (interface, concrete driver, and fakes) is 100% compliant for zero-change delegation from `ExecutionService.get_execution`.
- **`ScorecardAtomDto` Zero-Ripple UI Invariant (Discovery III — RESOLVED IN PASS 14):** Verified that zero UI components access raw dictionary indexing on `step.scorecardAtoms`, confirming that elevating `scorecardAtoms` to `Map<String, ScorecardAtomDto>` is 100% safe with zero breaking UI changes.
- **`ExecutionRecord` Docstring Modernization (Discovery JJJ — RESOLVED IN PASS 14):** Modernized stale docstring in `execution_record.dart#L16-L17` referencing obsolete "De-Generator Mandate" to reference pure typed Freezed DTO architecture.
- **`SseClient` Background Isolate Delta Parsing Parity (Discovery KKK — RESOLVED IN PASS 14):** Confirmed that `sse_client.dart`'s background isolate delta transformation is verified by unit tests (`sse_client_test.dart#L89`), and `FrozenContextSnapshot` seamlessly deserializes both delta and full REST payloads.
- **`execution_view.dart#L105` Local Variable Elimination (Discovery LLL — RESOLVED IN PASS 14):** Completely eliminated unused fallback variable `final frozenContext = record.frozenContext ?? {};` at L105, directly consuming typed `record.frozenContext?.versionId` in the version drift banner.
- **Virtual System Render Step Telemetry Completion (Discovery MMM — RESOLVED IN PASS 15):** Brought fully in-scope via `worker.py#L654-L659` updating both `step_states` and `steps` with `progress: 100` alongside `status: ExecutionStatus.PASSED`, guaranteeing that dynamically injected report rendering steps transition cleanly to 100% completion.
- **`create_execution_record` TypeAdapter Hardening (Discovery NNN — RESOLVED IN PASS 15):** Brought fully in-scope via `services/execution.py#L131-L137`, eradicating `isinstance(resolved_metadata, dict)` duck-typing and `# noqa: QGR012` suppression by validating via `TypeAdapter(ExecutionMetadata)`.
- **`auditDriftWarning` Localization Parameter Safety (Discovery OOO — RESOLVED IN PASS 15):** Brought fully in-scope via `execution_view.dart#L243-L245`, passing typed `versionId` directly to `AppLocalizations.of(context)!.auditDriftWarning(versionId)` after null and non-empty check, eradicating nested `?.toString() ?? ''` fallback chains.
- **`WorkflowInputs` Dynamic Input Encapsulation (Discovery PPP — RESOLVED IN PASS 15):** Enforced `@JsonSerializable(disallowUnrecognizedKeys: true)` on `WorkflowInputs` while safely encapsulating dynamic payload in `dynamicInputs: Map<String, dynamic>` per `ki_zero_permissive_typing.md`.
- **Dead Widget Deletion Verification (Discovery QQQ — RESOLVED IN PASS 15):** Verified zero callers for `execution_status_card.dart` across `lib/` and `test/`, permanently eliminating 241 lines and `initialInputs: Map<String, dynamic>`.
- **Context Variables Permissive Typing Audit (Discovery RRR & KKKK — RESOLVED IN PASS 15/20):** Audited all `# noqa: QGR012` occurrences in `services/execution.py`. Passes 15 and 18 resolved L136 and L675. Pass 20 brings the L1096 context variable encapsulation fully in-scope via `EvaluatedMatrixContextDTO` and `TypeAdapter` in Step 2.4, completely eliminating `# noqa: QGR012` from `services/execution.py`.
- **`resolve_dot_notation` Generic Reflection & Duck-Typing (Discovery LLLL — RESOLVED IN PASS 20):** Brought fully in-scope via Step 2.4 refactoring `math_utils.py#L186-L222` to a typed path resolver using structured collections and Pydantic model inspection without `getattr` reflection, completely eradicating both `# noqa: QGR012` and `# noqa: QGR001` suppressions.
- **Flutter `analysis_options.yaml` Creation & Freezed Warning Eradication (Discovery MMMM — RESOLVED IN PASS 21):** Brought fully in-scope via Step 3.0 creating `client_app_v2/analysis_options.yaml` configuring `invalid_annotation_target: ignore`, eliminating the root cause of annotation warnings and eradicating `// ignore_for_file: invalid_annotation_target` across all modified Freezed models without requiring an external sweep pass.
- **`dag_executor.py` Intermediate Step Persistence (Discovery SSS — RESOLVED IN PASS 16):** Added `steps: list[ExecutionStep] | None = None` to `ExecutionCommitter.commit_trace` and forwarded `steps=steps` to `ExecutionUpdateDTO` (`dag_executor.py#L87-L118`), passed `steps=current.steps` in intermediate `_safe_commit` (`#L632-L644`), and passed `steps=exec_record.steps` in final exit commits (`#L1000, #L1014, #L1035, #L1059`), ensuring database persistence of steps throughout DAG execution.
- **Full-Lifecycle DAG State Synchronization (Discovery TTT — RESOLVED IN PASS 16):** Synchronized `new_steps` in `dag_executor.py` across all state transitions inside `_update_lock`: cascading dependency failure (`#L658-L662`), queued (`#L702-L704`), running (`#L716-L720`), step exception catch (`#L904-L913`), virtual RAG preflight step (`#L934-L940, #L972-L980, #L984-L988`), and ExceptionGroup cancellation (`#L1027-L1033`), guaranteeing that `exec_record.steps` remains 1:1 synchronized with `step_states` at every instant.
- **Virtual Report Render Step Full Lifecycle Telemetry (Discovery UUU — RESOLVED IN PASS 16):** Synchronized virtual report render step telemetry across its full lifecycle in `worker.py`: initialize `sys_render_{profile_id}` with `progress=0, has_warning=False` (`#L436-L445, #L813-L821`), update with `progress: 100, status: ExecutionStatus.PASSED` on success (`#L654-L659`), and update with `status: ExecutionStatus.FAILED, last_error: str(e), progress: None, has_warning: True` on render failure (`#L695-L705`).
- **`create_execution_record` Lazy `or` Fallback Eradication (Discovery VVV — RESOLVED IN PASS 16):** Eradicated lazy fallback `or` in `create_execution_record` (`services/execution.py#L131-L135`), replacing `(extra_persistence_fields.pop("metadata", None) or ExecutionMetadata())` with strict explicit None checks and `TypeAdapter(ExecutionMetadata)`.
- **Backend English Status Strings Modernization (Discovery WWW — RESOLVED IN PASS 17):** Modernized legacy Finnish status messages in `worker.py#L827, #L983, #L1810` to concise English (`"Calculating dynamic results..."`, `"Generating AI synthesis..."`, `"Compiling output documents..."`) per `english_language_mandate`.
- **Synthesis Error Handler Step Telemetry Parity (Discovery XXX — RESOLVED IN PASS 17):** Synchronized `generate_profile_synthesis_and_pdf_task` error handler in `worker.py#L1854-L1864` with `progress: None, has_warning: True` across both `step_states` and `steps`, achieving 100% telemetry parity with `generate_pdf_job`.
- **`ExecutionCommitter.commit_trace` None-Guard (Discovery YYY — RESOLVED IN PASS 17):** Added conditional `if steps is not None: update_data["steps"] = steps` in `dag_executor.py#L110-L117` to prevent `exclude_unset=True` from emitting `"steps": null` and accidentally wiping persisted step history during partial commits.
- **Exact Line Precision for `ExecutionTimeline` Theme Tokens (Discovery ZZZ — RESOLVED IN PASS 17):** Verified exact AST line bounds for theme tokens in `execution_timeline.dart`: lines 44 and 91 modernize `primaryColor` to `colorScheme.primary`, line 180 eliminates outer `const` for `colorScheme.primary` icon, and line 134 enforces title containment via `Text(stepLabel, overflow: TextOverflow.ellipsis)` per `ki_desktop_pro_tool_studio_ux.md`.
- **Resumability Preflight Step Synchronization (Discovery AAAA — RESOLVED IN PASS 18):** Synchronized `new_steps = [s.model_copy(update={"status": ExecutionStatus.PENDING}) if s.id == step_id else s for s in exec_record.steps]` during resumability preflight reset (`dag_executor.py#L618-L627`), ensuring that resumed steps reset to `PENDING` across both `step_states` and `steps` simultaneously.
- **Virtual RAG Preflight Step Appending & Full Telemetry (Discovery BBBB — RESOLVED IN PASS 18):** Appended virtual RAG preflight step (`sys.rag.preflight`) directly to `exec_record.steps` on creation (`dag_executor.py#L934-L940`), updated with `progress: 100, status: PASSED` on pass (`#L972-L980`), and updated with `status: FAILED, last_error: str(e), progress: None, has_warning: True` on fail (`#L984-L988`) across both `step_states` and `steps`.
- **`ExceptionGroup` Cancellation Step Telemetry Synchronization (Discovery CCCC — RESOLVED IN PASS 18):** Synchronized `new_steps = [s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(primary_err), "progress": None, "has_warning": True}) if s.status == ExecutionStatus.RUNNING else s for s in exec_record.steps]` during unhandled exception group abort (`dag_executor.py#L1026-L1034`), eliminating stranded `RUNNING` steps in `steps`.
- **Initial Render Step Construction Defaults (Discovery DDDD — RESOLVED IN PASS 18):** Initialized `ExecutionStep(id=v_step_id, label=msg, status=ExecutionStatus.RUNNING, progress=0, has_warning=False)` when `old_state` is None during initial render status updates (`worker.py#L810-L825`), ensuring complete initial telemetry before status streaming begins.
- **RAG Preflight Real-Time Telemetry & Progress Emission (Discovery EEEE — RESOLVED IN PASS 19):** Synchronized `_emit_preflight_progress` in `dag_executor.py#L943-L962` to update `progress: pct` and `label: f"system.rag.preflight: {message}"` across both `step_states` and `steps`, alongside updating `exec_record.progress = pct` and `exec_record.status_message = f"Preflight: {message}"`.
- **Virtual Step ID Resumability Parity (Discovery FFFF — RESOLVED IN PASS 19):** Switched RAG preflight step ID generation to canonical system prefix `virtual_step_id = f"sys_rag_{uuid.uuid4().hex[:16]}"` in `dag_executor.py#L932` and updated `check_resumability` filter in `services/execution.py#L667` to `{k for k, s in record.step_states.items() if not k.startswith("sys_") and getattr(s, "label", None) != "system.rag.preflight"}`, permanently preventing virtual steps from breaking resumability step parity.
- **Unexpected Exception Step Telemetry Parity (Discovery GGGG — RESOLVED IN PASS 19):** Synchronized `new_states` and `new_steps` in `dag_executor.py#L1054-L1066` to mark all in-flight `RUNNING` steps as `FAILED` with `last_error: str(unexpected_err), progress: None, has_warning: True`, and passed `steps=exec_record.steps` to `self.committer.commit_trace(...)`.
- **Complete Worker English Modernization (Discovery HHHH — RESOLVED IN PASS 19):** Modernized the fourth hardcoded Finnish status message at `worker.py#L889` (`"Koostetaan tulosteita valmiiksi..."` -> `"Compiling output documents..."`) and logger at line 597 (`"Koonti"` -> `"assembly"`), achieving 100% complete English codebase compliance.
- **Missing `TypeAdapter` Import in `services/execution.py` (Discovery IIII — RESOLVED IN PASS 19):** Enriched Step 2.2 to explicitly import `TypeAdapter` at `services/execution.py#L16` (`from pydantic import TypeAdapter, ValidationError`).
- **Retry Sleep Interval Decoupling at `services/execution.py#L311` (Discovery JJJJ — RESOLVED IN PASS 19):** Modernized transient retry backoff sleep interval at line 311 to `await asyncio.sleep(get_settings().sse_polling_interval_seconds)` alongside line 300, completely eliminating `settings.llm_retry_delay` from status streaming.
- **ZERO POSTPONED TASKS:** All 61 architectural gaps, type weaknesses, and technical debt items discovered across Passes 1 to 21 have been brought into active execution scope. Zero tasks are postponed to the future.


