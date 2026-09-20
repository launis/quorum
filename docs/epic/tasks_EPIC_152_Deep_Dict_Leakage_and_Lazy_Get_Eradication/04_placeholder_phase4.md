<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# Phase 4: Hook Pipeline Hardening, Result Projector Segregation & Complete Emoji Eradication

**Overview:** Hardening the hook execution pipeline, result projection boundary, and worker error handling. Establishes the Two-Stage Separation Doctrine in `ResultProjector` by returning frozen `ProjectedResultsDTO` and `MatrixProjectionResultDTO` with zero anonymous tuples, isolates global context variables into typed `GlobalContextVarsDTO` across all 11 hook consumers and 5 orchestrator strategy/worker callers, hardens `HookDeltaDTO` into typed payload containers without dict-subscripting, eradicates in-place dictionary mutations, dummy matrix initializations, and all hardcoded emojis (specifically and exhaustively: `📍`, `💡`, `⚠️`, `🛠️` and their Unicode escapes `\U0001f4cd`, `\U0001f4a1`, `\u26a0\ufe0f`, `\U0001f6e0\ufe0f`) in `matrix_hook.py` and `llm_task_executor.py`, eliminates unraised exception logging and legacy comma exception syntax in `execution_worker.py`, `report_worker.py`, and `report_service.py`, updates 1-hop caller `override_service.py` to capture recalculate return values, and modernizes unit test suites with zero fixture reflection.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 4: Hook Pipeline Hardening, Result Projector Segregation & Error Swallowing Eradication

## Five-Axis Architectural Directives Table

| Target Scope & Boundaries | Eradicated Duct-Tape | Approved Best Practice | Pruned Over-Engineering (30% Deletion Test) | Verification & Fail-Fast (Proof Anchor) |
|---|---|---|---|---|
| `backend_v2/services/orchestrator/result_projector.py` (#L24-42, #L165-174) & `tda_engine.py` (#L120-134, #L200-210) | Anonymous 2-tuples `tuple[list[AtomResultDTO], dict[str, HydratedAtomDTO]]` unpacked via positional index access. | Return frozen `ProjectedResultsDTO` and `MatrixProjectionResultDTO` under `ConfigDict(strict=True, extra='forbid', frozen=True)`. Access fields via static dot notation. | Delete intermediate ad-hoc tuple unpackers and raw dict converters. | Unit tests in `test_result_projector.py` asserting `ProjectedResultsDTO` and `MatrixProjectionResultDTO` with zero tuple unpacking. |
| `backend_v2/models/dtos/hook_state.py` (#L44-76), `[NEW] global_context.py`, `[NEW] hook_delta.py` | Loose dictionary transit `vars: dict[str, Any]` in `GlobalContextVarsDTO` and `delta: dict[str, Any]` with `__getitem__` / `__contains__` in `HookDeltaDTO`. | Extract explicit typed fields into `GlobalContextVarsDTO` and closed union typed payloads in `HookDeltaDTO`. Re-export per PEP 484 with redundant aliases in `hook_state.py`. | Eradicate dynamic `__getitem__` and `__contains__` dict-emulation helper methods. | AST linter QGR018 verifying zero dict-subscripting on `HookDeltaDTO` across codebase. |
| `backend_v2/hooks/scoring/matrix_hook.py` (#L410-519, #L254-290, #L320-370) | `ev.model_dump()`, in-place mutations on `new_payload`, dummy `LightweightMatrixOutput(justification="[INITIALIZING]")`, and hardcoded emojis `📍`, `💡`, `⚠️`, `🛠️`. | Delegate analytical aggregation to `ResultProjector.project_matrix_results`, purge emojis, return `MatrixHookResultDTO` wrapped in `HookDeltaDTO`. | Purge markdown bullet generators and UI card dictionaries from analytical hook layer. | Unit test suite `[NEW] test_matrix_hook.py` asserting pure domain metrics, zero emojis, and zero in-place mutations. |
| `backend_v2/hooks/scoring/normalization_hook.py` (#L235-360) & `override_service.py` (#L190-211) | In-place dictionary mutation of `payload: dict[str, Any]` in `recalculate`, returning mutating state. | Enforce pure immutable transformation returning strongly typed `ScoringResultDTO`. Assign returned DTO explicitly in `override_service.py`. | Delete in-place dict mutation chains and legacy dictionary returns. | Unit tests in `test_scoring.py` verifying state immutability and typed scoring output. |
| All 11 Hook Consumers (`validation.py`, `source_verification_hook.py`, `security.py`, `references.py`, `metadata.py`, `llm.py`, `linguistics.py`, `integrity.py`, `input_processing.py`, `hydration.py`, `dlq_guard.py`) | Unpacking loose dictionaries `state.global_context_vars.vars[...]` and naked `dict[str, Any]` payloads. | Access typed fields on `state.global_context_vars` via static dot notation (e.g. `language`, `profile_id`, `step_coach`). | Delete defensive `.get(key, default)` checks and fallback empty dictionaries. | Hook unit tests asserting typed attribute access and fail-fast validation. |
| 1-Hop Strategy & Worker Callers (`strategies/base.py`, `strategies/llm.py`, `strategies/logic.py`, `workers/synthesis_worker.py`) | Instantiating `GlobalContextVarsDTO(vars={...})` and unpacking `.vars` dictionary. | Pass keyword arguments for typed fields (`language=...`, `profile_id=...`) and update using `.model_copy(update=...)`. | Eradicate manual dictionary unpacking routines across strategies. | Integration tests across DAG executor and synthesis worker verifying typed context propagation. |
| Workers & Loggers (`execution_worker.py` #L135-155, `report_worker.py` #L245-260, `report_service.py` #L275-295, `llm_task_executor.py` #L258) | Silent exception swallowing `logger.warning` without DLQ classification, legacy Python 2 comma syntax `except OSError, ...`, generic `except Exception`, and log emojis. | Catch parenthesized exception tuples, log RFC 7807 structured errors, fail-fast with `AppException`, and remove emojis from log text. | Purge multi-layer exception catching that swallows critical infrastructure faults. | Unit tests asserting re-raised `AppException(ErrorCodes.INTERNAL_SERVER_ERROR)` on unrecoverable failures. |
| Unit Test Suites (`test_dlq_guard.py`, `test_metrics.py`, `test_references.py`, `test_dag_executor_prompt_blocks.py`, `test_llm_cost_tracking.py`, `test_synthesis_distiller_wiring.py`) | `object.__setattr__` monkeypatching, `hasattr` reflection, tuple mock returns `(..., {})`, and `result.state_delta["distilled_inputs"]` dict subscripting. | Construct immutable DTO instances using typed constructors, mock `ProjectedResultsDTO`, and access `state_delta.delta`. | Eradicate reflection helper functions and dynamic test monkeypatching. | Full test suite execution passing with >90% coverage and zero AST guardrail violations. |

**Target Files:**
- `[NEW]` @[backend_v2/models/dtos/global_context.py]
- `[NEW]` @[backend_v2/models/dtos/hook_delta.py]
- `[MODIFY]` @[backend_v2/models/dtos/hook_state.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/result_projector.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/normalization_hook.py]
- `[MODIFY]` @[backend_v2/services/execution/override_service.py]
- `[MODIFY]` @[backend_v2/hooks/validation.py]
- `[MODIFY]` @[backend_v2/hooks/source_verification_hook.py]
- `[MODIFY]` @[backend_v2/hooks/security.py]
- `[MODIFY]` @[backend_v2/hooks/references.py]
- `[MODIFY]` @[backend_v2/hooks/metadata.py]
- `[MODIFY]` @[backend_v2/hooks/llm.py]
- `[MODIFY]` @[backend_v2/hooks/linguistics.py]
- `[MODIFY]` @[backend_v2/hooks/integrity.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/hooks/hydration.py]
- `[MODIFY]` @[backend_v2/hooks/interaction_hook.py]
- `[MODIFY]` @[backend_v2/hooks/dlq_guard.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py]
- `[MODIFY]` @[backend_v2/workers/synthesis_worker.py]
- `[MODIFY]` @[backend_v2/services/llm_task_executor.py]
- `[MODIFY]` @[backend_v2/workers/execution_worker.py]
- `[MODIFY]` @[backend_v2/workers/report_worker.py]
- `[MODIFY]` @[backend_v2/services/report_service.py]
- `[NEW]` @[backend_v2/tests/unit/hooks/test_matrix_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_result_projector.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_validation.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_dlq_guard.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_metrics.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_references.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_archival.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metadata.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 3 established typed synthesis distillation contracts, EvaluatedAtomDTO stratification, and zero reflection in worker suites.</action>
    <action>Look forward: Verify that Phase 5 prompt compiler receives clean, typed context variables and state reducers without loose dictionaries.</action>
    <action>Note deferred contracts: [NEW] ContextVariablesDTO and [NEW] NodeExecutionUpdateDTO are explicitly scoped and deferred to Phase 5.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/04_placeholder_phase4.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>ResultProjector in @[backend_v2/services/orchestrator/result_projector.py] eliminates anonymous 2-tuples; ResultProjector.project returns frozen ProjectedResultsDTO(results=..., hydrated_references=...).</item>
    <item>ResultProjector.project_matrix_results in @[backend_v2/services/orchestrator/result_projector.py] extracts matrix-level aggregation from matrix_hook.py and returns frozen MatrixProjectionResultDTO(results=..., matrix_output=..., missing_context=...).</item>
    <item>TDAEngine callers in @[backend_v2/services/orchestrator/engines/tda_engine.py] consume ProjectedResultsDTO via static dot notation without tuple unpacking.</item>
    <item>GlobalContextVarsDTO is packaged in [NEW] @[backend_v2/models/dtos/global_context.py] with frozen strict immutability, replacing loose vars dictionary with explicit typed fields (language, target_locale, system_locale, profile_id, organization_id, initiator_id, step_coach, knowledge_base, hydration_results, step_linguistics, external_evidence).</item>
    <item>HookDeltaDTO is packaged in [NEW] @[backend_v2/models/dtos/hook_delta.py] with typed payload containers (MatrixHookResultDTO, MissingContextDTO, ProjectedResultsDTO, MatrixProjectionResultDTO), eliminating loose delta dictionary and __getitem__/__contains__ mapping methods.</item>
    <item>matrix_scoring_hook in @[backend_v2/hooks/scoring/matrix_hook.py] eradicates ev.model_dump(), TypeAdapter(dict[str, Any]), in-place payload mutations, dummy LightweightMatrixOutput(justification="[INITIALIZING]"), and all hardcoded emojis (specifically and exhaustively: \U0001f4cd, \U0001f4a1, \u26a0\ufe0f, \U0001f6e0\ufe0f) in favor of clean semantic identifiers and QuoteEvidenceDTO.</item>
    <item>recalculate in @[backend_v2/hooks/scoring/normalization_hook.py] eradicates in-place dictionary mutations and returns strongly typed ScoringResultDTO.</item>
    <item>All 11 hook consumers (@[backend_v2/hooks/validation.py], @[backend_v2/hooks/source_verification_hook.py], @[backend_v2/hooks/security.py], @[backend_v2/hooks/references.py], @[backend_v2/hooks/metadata.py], @[backend_v2/hooks/llm.py], @[backend_v2/hooks/linguistics.py], @[backend_v2/hooks/integrity.py], @[backend_v2/hooks/input_processing.py], @[backend_v2/hooks/hydration.py]) access state.global_context_vars via static dot notation without .vars subscripting.</item>
    <item>All 1-hop strategy and worker callers (@[backend_v2/services/orchestrator/strategies/base.py], @[backend_v2/services/orchestrator/strategies/llm.py], @[backend_v2/services/orchestrator/strategies/logic.py], @[backend_v2/workers/synthesis_worker.py]) construct GlobalContextVarsDTO using typed parameters without loose vars dicts.</item>
    <item>1-hop caller @[backend_v2/services/execution/override_service.py] assigns recalculate result back to record.context_variables.</item>
    <item>Unraised exception logging and old Python 2 comma syntax eradicated in @[backend_v2/workers/execution_worker.py], @[backend_v2/workers/report_worker.py], and @[backend_v2/services/report_service.py].</item>
    <item>Emoji eradicated in @[backend_v2/services/llm_task_executor.py], replaced with clean text "[QUALITY] LLM applied Contextual Override.".</item>
    <item>Unit test suite [NEW] @[backend_v2/tests/unit/hooks/test_matrix_hook.py] created with comprehensive ISTQB positive and negative boundary partitions.</item>
    <item>All hook unit test fixtures (@[backend_v2/tests/unit/hooks/test_dlq_guard.py], @[backend_v2/tests/unit/hooks/test_metrics.py], @[backend_v2/tests/unit/hooks/test_references.py], @[backend_v2/tests/unit/hooks/test_source_verification_hook.py], @[backend_v2/tests/unit/hooks/test_archival.py], @[backend_v2/tests/unit/test_metadata.py], @[backend_v2/tests/unit/hooks/test_validation.py], @[backend_v2/tests/unit/hooks/test_scoring.py], @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]) eradicate object.__setattr__ monkeypatching and reflection in favor of typed constructors.</item>
    <item>All 1-hop test mocks (@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py], @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]) updated to return ProjectedResultsDTO.</item>
    <item>Quality gates pass: uv run python scripts/backend_audit_loop.py on all touched modules with >90% coverage and zero fatal AST guardrail violations.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT modify prompt compilation logic or prompt_compiler.py in Phase 4 (reserved for Phase 5).</forbidden>
    <forbidden>Do NOT mutate SDUI presentation adapters or Flutter UI models in Phase 4 (reserved for Phase 6).</forbidden>
    <forbidden>Do NOT create parallel fallback access chains or re-introduce dict.get() lookups.</forbidden>
    <forbidden>Do NOT relocate hardcoded emojis to secondary modules; purge emojis entirely from backend execution payloads.</forbidden>
    <forbidden>Do NOT implement [NEW] ContextVariablesDTO or [NEW] NodeExecutionUpdateDTO in Phase 4 (strictly reserved and deferred to Phase 5).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/models/dtos/global_context.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/hook_delta.py]</backend>
    <backend>@[backend_v2/models/dtos/hook_state.py]</backend>
    <backend>@[backend_v2/services/orchestrator/result_projector.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/normalization_hook.py]</backend>
    <backend>@[backend_v2/services/execution/override_service.py]</backend>
    <backend>@[backend_v2/hooks/validation.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/hooks/security.py]</backend>
    <backend>@[backend_v2/hooks/references.py]</backend>
    <backend>@[backend_v2/hooks/metadata.py]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/hooks/linguistics.py]</backend>
    <backend>@[backend_v2/hooks/integrity.py]</backend>
    <backend>@[backend_v2/hooks/input_processing.py]</backend>
    <backend>@[backend_v2/hooks/hydration.py]</backend>
    <backend>@[backend_v2/hooks/interaction_hook.py]</backend>
    <backend>@[backend_v2/hooks/dlq_guard.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py]</backend>
    <backend>@[backend_v2/services/llm_task_executor.py]</backend>
    <backend>@[backend_v2/workers/execution_worker.py]</backend>
    <backend>@[backend_v2/workers/report_worker.py]</backend>
    <backend>@[backend_v2/services/report_service.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/hooks/test_matrix_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_result_projector.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_validation.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_scoring.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_dlq_guard.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_metrics.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_references.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_archival.py]</backend>
    <backend>@[backend_v2/tests/unit/test_metadata.py]</backend>
  </touched_artifacts>

  <pre_implementation_cleanups>
    <cleanup id="C1" target="@[backend_v2/services/orchestrator/result_projector.py]">
      <description>Eliminate anonymous 2-tuple return tuple[list[AtomResultDTO], dict[str, HydratedAtomDTO]] on Line 27 and Line 173.</description>
      <remedy>Define and return frozen ProjectedResultsDTO(results=..., hydrated_references=...). Implement project_matrix_results returning MatrixProjectionResultDTO (#L24-42, #L165-174).</remedy>
    </cleanup>
    <cleanup id="C2" target="@[backend_v2/models/dtos/hook_state.py]">
      <description>Eradicate loose vars: dict[str, Any] in GlobalContextVarsDTO and delta: dict[str, Any] / __getitem__ / __contains__ in HookDeltaDTO (#L44-76).</description>
      <remedy>Extract explicit typed fields into [NEW] global_context.py and [NEW] hook_delta.py, eliminating dictionary indexing and membership operations.</remedy>
    </cleanup>
    <cleanup id="C3" target="@[backend_v2/hooks/scoring/matrix_hook.py]">
      <description>Eradicate in-place mutation of untyped dictionary payload (Lines 475-499), dummy LightweightMatrixOutput(justification="[INITIALIZING]"), recalculate() in-place call (Line 501), and hardcoded emojis (Lines 432, 444, 446, 448).</description>
      <remedy>Delegate analytical aggregation to ResultProjector.project_matrix_results, purge all emojis in favor of clean semantic identifiers, and return MatrixHookResultDTO (#L410-519).</remedy>
    </cleanup>
    <cleanup id="C4" target="@[backend_v2/hooks/scoring/normalization_hook.py]">
      <description>Eradicate in-place mutation of payload: dict[str, Any] in recalculate (Lines 235-360).</description>
      <remedy>Enforce pure immutable transformation returning strongly typed ScoringResultDTO without mutating caller state.</remedy>
    </cleanup>
    <cleanup id="C5" target="@[backend_v2/hooks/validation.py]">
      <description>Eradicate inputs_dict = payload.root, .get("raw_inputs"), silent except ValidationError: pass, and state.global_context_vars.vars["language"] (Lines 180-205).</description>
      <remedy>Validate typed ExecutionInputsDTO directly, access state.global_context_vars.language via static dot notation, and fail-fast with AppException(ErrorCodes.VALIDATION_FAILED).</remedy>
    </cleanup>
    <cleanup id="C6" target="@[backend_v2/hooks/dlq_guard.py]">
      <description>Eradicate content_payload: dict[str, Any] = state.inputs.raw_inputs and evaluations = content_payload["evaluations"] (Lines 40-70).</description>
      <remedy>Validate evaluations container using strongly typed Pydantic model with strict validation.</remedy>
    </cleanup>
    <cleanup id="C7" target="@[backend_v2/services/llm_task_executor.py]">
      <description>Eradicate hardcoded emoji in logger.info("💡 [QUALITY] LLM applied Contextual Override.") on Line 258.</description>
      <remedy>Replace with clean structured log text: logger.info("[QUALITY] LLM applied Contextual Override.").</remedy>
    </cleanup>
    <cleanup id="C8" target="@[backend_v2/workers/execution_worker.py]">
      <description>Eradicate unraised logging in except (OSError, UnicodeDecodeError, ValidationError, ValueError, KeyError) as err: logger.warning(...) on Lines 142-143.</description>
      <remedy>Enforce RFC 7807 logging with explicit DLQ classification or raise AppException(ErrorCodes.INTERNAL_SERVER_ERROR).</remedy>
    </cleanup>
    <cleanup id="C9" target="@[backend_v2/workers/report_worker.py]">
      <description>Eradicate legacy Python 2 comma exception syntax except OSError, ValidationError, ValueError, KeyError: on Line 252.</description>
      <remedy>Catch using parenthesized tuple except (OSError, ValidationError, ValueError, KeyError): with structured logging (#L245-260).</remedy>
    </cleanup>
    <cleanup id="C10" target="@[backend_v2/services/report_service.py]">
      <description>Eradicate generic except Exception as err: logger.warning(...) on Line 285.</description>
      <remedy>Catch specific (StorageError, FileNotFoundError, OSError) and fail-fast with AppException(ErrorCodes.INTERNAL_SERVER_ERROR) on unexpected failures (#L275-295).</remedy>
    </cleanup>
    <cleanup id="C11" target="@[backend_v2/services/execution/override_service.py]">
      <description>Assign recalculate() return value back to record.context_variables instead of relying on legacy in-place mutation (Lines 190-211).</description>
      <remedy>Update caller to assign record.context_variables = await scoring.recalculate(...) and persist record.</remedy>
    </cleanup>
    <cleanup id="C12" target="@[backend_v2/services/orchestrator/strategies/base.py], @[backend_v2/services/orchestrator/strategies/llm.py], @[backend_v2/services/orchestrator/strategies/logic.py], @[backend_v2/workers/synthesis_worker.py]">
      <description>Eradicate instantiating GlobalContextVarsDTO(vars={...}) and unpacking .vars dictionary across 1-hop callers.</description>
      <remedy>Migrate instantiation to typed attributes and model_copy(update=...) across strategies and workers.</remedy>
    </cleanup>
    <cleanup id="C13" target="@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py], @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]">
      <description>Eradicate 2-tuple mock return values mock_project.return_value = (..., {}) on Line 199 and Line 96.</description>
      <remedy>Update test mock return values to ProjectedResultsDTO(results=..., hydrated_references=...).</remedy>
    </cleanup>
    <cleanup id="C14" target="@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]">
      <description>Eradicate dict-subscripting result.state_delta["distilled_inputs"] on Lines 414, 442, 491, 581 and hook test fixture reflection.</description>
      <remedy>Update test assertions to static dot notation result.state_delta.delta and construct valid immutable instances using typed constructors.</remedy>
    </cleanup>
  </pre_implementation_cleanups>

  <step id="4.1" name="Result Projector Segregation &amp; Two-Stage Separation Doctrine">
    <action>In @[backend_v2/services/orchestrator/result_projector.py] (#L24-42, #L165-174):
      1. Eliminate anonymous 2-tuple return tuple[list[AtomResultDTO], dict[str, HydratedAtomDTO]] in ResultProjector.project.
      2. Return defined frozen ProjectedResultsDTO(results=results, hydrated_references=hydrated_references).
      3. Implement ResultProjector.project_matrix_results(nodes, states, matrix_id, ...) returning defined frozen MatrixProjectionResultDTO(results=..., matrix_output=..., missing_context=...).
      4. Output clean domain data exclusively (zero emojis, zero markdown bullets, zero UI quote dicts).
    </action>
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py] (#L120-134, #L200-210):
      Update callers to consume projected = ResultProjector.project(...) and access projected.results and projected.hydrated_references via static dot notation.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_result_projector.py], @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py], @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py], @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py] (#L199), and @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py] (#L96):
      Update test assertions and mock return values to verify ProjectedResultsDTO and MatrixProjectionResultDTO with static dot notation.
    </action>
    <constraint invariant="ban_anonymous_state_tuples">Every multi-field return state must be encapsulated in an immutable Pydantic V2 DTO under ConfigDict(strict=True, extra="forbid", frozen=True).</constraint>
    <constraint invariant="pure_dot_notation_and_anti_reflection">Access attributes strictly via static dot notation without positional index unpacking.</constraint>
  </step>

  <step id="4.2" name="Global Context &amp; Hook Delta DTO Hardening">
    <action>Create [NEW] @[backend_v2/models/dtos/global_context.py]:
      Define GlobalContextVarsDTO(V2CoreBase) under ConfigDict(strict=True, extra="forbid", frozen=True) with explicit typed fields:
      - language: str | None = None
      - target_locale: str | None = None
      - system_locale: str | None = None
      - profile_id: str | None = None
      - organization_id: str | None = None
      - initiator_id: Annotated[str | None, Field(default=None, alias="_sys_initiator_id")] = None
      - step_coach: Annotated[dict[str, str | int | float | bool | list[str]] | None, Field(default=None)] = None
      - knowledge_base: Annotated[dict[str, str | int | float | bool | list[str]] | None, Field(default=None)] = None
      - hydration_results: Annotated[HydrationInputSourceDTO | None, Field(default=None)] = None
      - step_linguistics: Annotated[LinguisticsResultDTO | None, Field(default=None)] = None
      - external_evidence: Annotated[str | None, Field(default=None)] = None
    </action>
    <action>Create [NEW] @[backend_v2/models/dtos/hook_delta.py]:
      Define:
      - ProjectedResultsDTO(V2CoreBase): results: list[AtomResultDTO], hydrated_references: dict[str, HydratedAtomDTO]
      - MissingContextDTO(V2CoreBase): missing_atoms: list[str], missing_context_text: str | None = None
      - MatrixProjectionResultDTO(V2CoreBase): results: list[AtomResultDTO], matrix_output: LightweightMatrixOutput, missing_context: MissingContextDTO | None = None
      - MatrixHookResultDTO(V2CoreBase): matrix_outputs: dict[str, LightweightMatrixOutput], missing_contexts: dict[str, str], atom_quotes: dict[str, list[QuoteEvidenceDTO]]
      - HookDeltaDTO(V2CoreBase) under ConfigDict(strict=True, extra="forbid", frozen=True):
        - delta: Annotated[MatrixHookResultDTO | SynthesisDistillationDTO | StepOutputContentDTO | SanitizationResultDTO | BibliographyResultDTO | MetadataHookPayloadDTO | dict[str, Any] | None, Field(default=None)]
        - metadata_updates: Annotated[dict[str, Any] | None, Field(default=None)] = None
      Eliminate __getitem__ and __contains__ dictionary mapping methods.
    </action>
    <action>In @[backend_v2/models/dtos/hook_state.py] (#L44-76):
      Re-export GlobalContextVarsDTO and HookDeltaDTO from global_context.py and hook_delta.py per PEP 484 with redundant aliases.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py] (#L414, #L442, #L491, #L581):
      Update assertions from result.state_delta["distilled_inputs"] to static dot notation result.state_delta.delta.distilled_inputs.
    </action>
    <constraint invariant="zero_naked_dicts_and_permissive_typing">Enforce 100% typed transit using immutable Pydantic V2 DTOs configured with extra="forbid" and frozen=True.</constraint>
    <constraint invariant="explicit_reexport_mandate">All re-exported symbols in hook_state.py must use redundant aliases (from module import Symbol as Symbol) and __all__.</constraint>
  </step>

  <step id="4.3" name="Scoring Hooks Hardening, Result Projector Integration &amp; Universal Emoji Eradication">
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py] (#L410-519, #L254-290, #L320-370):
      1. Eradicate ev.model_dump(mode="json") and TypeAdapter(dict[str, Any]).validate_python(ev).
      2. Eradicate all emojis (specifically and exhaustively: \U0001f4cd, \U0001f4a1, \u26a0\ufe0f, \U0001f6e0\ufe0f on Lines 432, 444, 446, 448).
      3. Eradicate markdown bullets ("- {text}") and loose UI card dicts; use structured QuoteEvidenceDTO and pure semantic labels (COACHING, FALSIFICATION, OVERRIDE).
      4. Eradicate in-place mutation of untyped dictionary bags (new_payload = content_payload.copy(), payload[pb_id] = ...).
      5. Eliminate dummy LightweightMatrixOutput(justification="[INITIALIZING]") injection hacks.
      6. Delegate matrix projection and evaluation calculations to ResultProjector.project_matrix_results.
      7. Return strongly typed MatrixHookResultDTO wrapped in HookDeltaDTO.
      8. Access state.global_context_vars via static dot notation without .vars subscripting.
    </action>
    <action>In @[backend_v2/hooks/scoring/normalization_hook.py] (#L235-360):
      Eradicate in-place mutation in recalculate(payload: dict[str, Any]). Enforce pure immutable transformation returning strongly typed ScoringResultDTO.
    </action>
    <action>In @[backend_v2/services/execution/override_service.py] (#L190-211):
      Update callers of recalculate to assign record.context_variables = await scoring.recalculate(...) and persist updated state.
    </action>
    <constraint invariant="universal_emoji_eradication">Zero emojis allowed in analytical payloads, log statements, or hook outputs. UI headers bind to native Flutter Material icons.</constraint>
    <constraint invariant="the_duct_tape_ban">No in-place dictionary mutations, no dummy model initializations, and no empty dict fallbacks.</constraint>
  </step>

  <step id="4.4" name="Hook Consumers Global Context Dot-Notation Migration &amp; DLQ / Interaction Hook Hardening">
    <action>Migrate all hook consumers to direct dot notation on state.global_context_vars:
      - @[backend_v2/hooks/validation.py] (#L180-205): access state.global_context_vars.language directly. Eradicate inputs_dict = payload.root and .get("raw_inputs"), validate typed ExecutionInputsDTO directly, eradicate silent except ValidationError: pass.
      - @[backend_v2/hooks/source_verification_hook.py]: access state.global_context_vars.language directly.
      - @[backend_v2/hooks/security.py]: access state.global_context_vars.language directly.
      - @[backend_v2/hooks/references.py] (#L115-145): access state.global_context_vars.step_coach and state.global_context_vars.knowledge_base directly.
      - @[backend_v2/hooks/metadata.py] (#L50-85): access state.global_context_vars.profile_id, organization_id, initiator_id directly.
      - @[backend_v2/hooks/llm.py] (#L50-75): access state.global_context_vars.target_locale, system_locale, language directly.
      - @[backend_v2/hooks/linguistics.py]: access state.global_context_vars.language, target_locale directly.
      - @[backend_v2/hooks/integrity.py]: access state.global_context_vars.knowledge_base, step_coach directly.
      - @[backend_v2/hooks/input_processing.py]: access state.global_context_vars.language, target_locale, system_locale directly.
      - @[backend_v2/hooks/hydration.py]: access state.global_context_vars.hydration_results directly.
    </action>
    <action>In @[backend_v2/services/orchestrator/strategies/base.py] (#L260-285, #L340-385), @[backend_v2/services/orchestrator/strategies/llm.py] (#L805-930), @[backend_v2/services/orchestrator/strategies/logic.py] (#L130-175), and @[backend_v2/workers/synthesis_worker.py] (#L205-215):
      Migrate GlobalContextVarsDTO instantiations from vars={...} to explicit typed parameters and access attributes via static dot notation.
    </action>
    <action>In @[backend_v2/hooks/interaction_hook.py] and @[backend_v2/hooks/dlq_guard.py] (#L40-70):
      Remove naked dict[str, Any] parameter annotations and validate structured schemas with strict Pydantic models.
    </action>
    <constraint invariant="pure_dot_notation_and_anti_reflection">All hook consumers must access context attributes via static dot notation without dynamic dictionary indexing.</constraint>
    <constraint invariant="anti_lazy_fallback_mandate">Zero fallback operators (or [], or {}) to silently bypass missing context.</constraint>
  </step>

  <step id="4.5" name="Workers, Loggers &amp; Background Services Error Swallowing &amp; Emoji Eradication">
    <action>In @[backend_v2/services/llm_task_executor.py] (#L258):
      Replace logger.info("💡 [QUALITY] LLM applied Contextual Override.", ...) with logger.info("[QUALITY] LLM applied Contextual Override.", ...).
    </action>
    <action>In @[backend_v2/workers/execution_worker.py] (#L135-155):
      Eradicate unraised logging in except (OSError, UnicodeDecodeError, ValidationError, ValueError, KeyError) as err: logger.warning(...).
      Enforce RFC 7807 logging with explicit DLQ classification or raise AppException(ErrorCodes.INTERNAL_SERVER_ERROR).
    </action>
    <action>In @[backend_v2/workers/report_worker.py] (#L245-260):
      Eradicate legacy Python 2 comma syntax except OSError, ValidationError, ValueError, KeyError: on Line 252.
      Catch via parenthesized tuple except (OSError, ValidationError, ValueError, KeyError): and log structured error before re-raising.
    </action>
    <action>In @[backend_v2/services/report_service.py] (#L275-295):
      Eradicate generic except Exception as err: logger.warning(...). Target specific storage exceptions and fail-fast on unexpected errors.
    </action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every crash or failure must be preceded by structured logging containing the exact error code and contextual parameters.</constraint>
    <constraint invariant="the_duct_tape_ban">Fix root causes and fail-fast loudly; zero catch-all with silent unraised logging.</constraint>
  </step>

  <step id="4.6" name="Comprehensive Test Suites Modernization, Hook Fixture Reflection Eradication &amp; New Matrix Hook Suite">
    <action>Create [NEW] @[backend_v2/tests/unit/hooks/test_matrix_hook.py]:
      Add comprehensive positive and negative ISTQB test partitions:
      1. Happy path: matrix_scoring_hook computes matrix scores, returns MatrixHookResultDTO, zero emojis, zero in-place mutations.
      2. Missing context: missing mandatory blueprint_id or step raises AppException(ErrorCodes.VALIDATION_FAILED).
      3. Missing repository: missing deps.workflow_repo raises AppException(ErrorCodes.HOOK_EXECUTION_FAILED).
      4. DLQ atom handling: atoms in DLQ status mapped to ExecutionStatus.SYSTEM_ERROR without crashing.
      5. Contextual override quote extraction: verified without emoji prefix strings.
    </action>
    <action>In @[backend_v2/tests/unit/hooks/test_dlq_guard.py], @[backend_v2/tests/unit/hooks/test_metrics.py], @[backend_v2/tests/unit/hooks/test_references.py], @[backend_v2/tests/unit/hooks/test_source_verification_hook.py], @[backend_v2/tests/unit/hooks/test_archival.py], @[backend_v2/tests/unit/test_metadata.py], @[backend_v2/tests/unit/hooks/test_validation.py], and @[backend_v2/tests/unit/hooks/test_scoring.py]:
      Eradicate object.__setattr__ monkeypatching and hasattr reflection in favor of typed constructors with immutable models.
    </action>
    <action>Verify all target unit tests pass with >90% coverage and zero fatal AST guardrail violations.</action>
    <constraint invariant="mocking_mandate_for_llm">All tests must use mocked fixtures with zero live network calls.</constraint>
    <constraint invariant="anti_happy_path_mandate">Every positive test scenario must be accompanied by at least 2 negative test scenarios.</constraint>
  </step>

  <validation_gate>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/result_projector.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_matrix_hook.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/workers/execution_worker.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/workers/report_worker.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/execution/override_service.py --test</command>
  </validation_gate>
</execution_protocol>
```
