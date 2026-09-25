# Tracker: Pipeline State Transit Type Safety & Validation Hardening

@[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md]

- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md]`
  - [ ] Step 1: PRE_IMPLEMENTATION_CLEANUPS
  - [ ] Step 2: DEFINE_TRACE_DTOS_AND_EXPAND_PAYLOAD_UNION
  - [ ] Step 3: TRACE_EVENT_AND_STATE_PROJECTOR_TYPING
  - [ ] Step 4: CONTEXT_ROUTER_STRICT_TYPING
  - [ ] Step 5: DAG_EXECUTOR_AND_STRATEGY_TRANSIT_CLEANUP
  - [ ] Step 6: SYNTHESIS_PAYLOAD_COMPRESSOR_CLEANUP
  - [ ] Step 7: DTO_AND_CROSS_DOMAIN_PARITY_HARDENING
  - [ ] Step 8: LOCALE_AND_INTERNATIONALIZATION_SSOT_HARMONIZATION
  - [ ] Step 9: UNIT_TEST_MODERNIZATION_AND_ISTQB_EXPANSION
  - [ ] Step 10: DETERMINISTIC_AST_AUDIT_VERIFICATION
  - [ ] Step 11: UNIVERSAL_QUALITY_GATE_COMPLETION
  - [ ] Step 12: ATOMIC_CHECKPOINT_COMMITS

- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md]`

---

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/models/auth.py]
  - [ ] @[backend_v2/models/execution_core.py]
  - [ ] @[backend_v2/models/state.py]
  - [ ] @[backend_v2/models/domain/synthesis.py]
  - [ ] @[backend_v2/models/dtos/context_variables.py]
  - [ ] @[backend_v2/models/dtos/trace.py]
  - [ ] @[backend_v2/models/dtos/step_output.py]
  - [ ] @[backend_v2/models/dtos/node_execution.py]
  - [ ] @[backend_v2/models/dtos/hook_delta.py]
  - [ ] @[backend_v2/models/dtos/state.py]
  - [ ] @[backend_v2/models/dtos/lightweight_matrix.py]
  - [ ] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
  - [ ] @[backend_v2/services/orchestrator/context_router.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/state_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
  - [ ] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [ ] @[backend_v2/hooks/input_processing.py]
  - [ ] @[backend_v2/hooks/source_verification_hook.py]
  - [ ] @[backend_v2/core/registry.py]
  - [ ] @[backend_v2/database/repositories/knowledge.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files:
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]
  - [ ] @[client_app_v2/lib/l10n/app_en.arb]
  - [ ] @[client_app_v2/lib/l10n/app_fi.arb]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

---

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.

---

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

---

## Instructions for the Execution Agent

### Pre-Flight Mandatory Actions
1. **Context Rules Governance**: Load `<required_context_rules>` from both the plan and this tracker on every session start.
2. **KI Pre-Read**: Before modifying models or services, physically `view_file` @[ki_zero_permissive_typing.md], @[ki_python_314_concurrency_strictness.md], @[ki_dual_axis_localization_architecture.md], and @[ki_dag_engine_dto_projection_rules.md].
3. **AST Guardrail & Baseline Check**: Ensure `scripts/audit_dict_eradication.py` and `scripts/audit_dto_parity.py` run cleanly to establish baseline AST status before introducing modifications.

### Execution Governance
- **Atomic Commits**: After EVERY successful step or `backend_audit_loop.py` run, perform `git add <specific_files>; git commit -m "<type>(<scope>): <summary>"`. List all staged files explicitly.
- **Quality Gates**:
  - For Python changes: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - For Flutter changes: `uv run python scripts/flutter_audit_loop.py <target_path> [--build]`
  - For AST dict eradication: `uv run python scripts/audit_dict_eradication.py <target_path> --strict`
  - For DTO parity: `uv run python scripts/audit_dto_parity.py`
- **Session Handovers**: Execute `/tier5-session-handover` if modifying >5 distinct complex files, processing >8 user prompts in a session, or completing 3 atomic git commits.
- **Execution Mode**: Supports Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Tracker Updates**: Mark steps `[x]` in this tracker after each successful step completion.

### Resume Command Format
```
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md]
```

---

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
|---|---|---|---|
| REQ-001 | Phase 1 Pre-Implementation Cleanups: Repair unnested `context_variables` fixtures in `test_state.py`, purge `.__dict__` reflection and `not k.startswith("__")` negative filter in `_state_localns`, remove dead return in `synthesis_payload_compressor.py`, update 1-hop caller test assertions in `test_state_reducer.py` and `test_linguistics_state_reduction_regression.py`, eradicate redundant `= Field(...)` defaults across sibling models, fix exception tuple syntax in `input_processing.py`, harden `UserUpdate` with typed Annotated fields, eradicate in-place `del` mutation in `context_builder.py`, replace mutable defaults in `HookStateMetadata`, and implement mapping protocol on `StepOutputContentDTO`. | Step 1 | [ ] Pending |
| REQ-002 | Trace DTO Definitions & Payload Union Expansion: Preserve sanctioned AST exemption on `TraceEventMetadataEnvelope`, tighten `TraceMatrixPayloadDTO.atom_quotes` to `list[str] \| None`, author [NEW] `ProgressTracePayloadDTO` and [NEW] `TraceEventMetadataDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` using pure Python 3.14 Annotated syntax, and expand `StepPayloadValue` closed union in `step_output.py`. | Step 2 | [ ] Pending |
| REQ-003 | TraceEvent & StateProjector Typing: Update `TraceEvent.content` to closed union and `TraceEvent.metadata` to typed `TraceEventMetadataDTO`, type `StateProjector._snapshot` as `dict[str, StepOutputContentDTO]` (eradicating Primitive Obsession nested dict violations), replace `.model_construct()` fallback in `_build_dto_list()` with Fail-Fast `AppException(ErrorCodes.VALIDATION_FAILED)`, unwrap payloads in `apply_delta()` into `StepOutputContentDTO(data=...)`, and wrap GDPR tombstone into `StepOutputContentDTO(data={"_redacted": True, "hash": redacted_hash})`. | Step 3 | [ ] Pending |
| REQ-004 | ContextRouter Strict Typing: Restrict `ContextRouter.route_and_prune` signature strictly to `trace_event: LightweightMatrixOutput`, delete `isinstance(trace_event, Mapping)` duck-typing branch, deterministically resolve extensions to `{}` when `output_profile` is `None` (banning all-inclusive fallback), and validate `value` into `LightweightMatrixOutput` in `context_builder.py` with immutable `pruned.model_dump(exclude={"evaluated_atoms"})`. | Step 4 | [ ] Pending |
| REQ-005 | DAGExecutor & Strategy Transit Cleanup: Eradicate `isinstance(..., Mapping)` fallback for `global_context_vars` in `NodeExecutor`, pass `exec_record.raw_inputs`, `StepOutputContentDTO`, and `lightweight_matrix` directly to `TraceEvent` without intermediate `.model_dump()` double-serialization, update metadata schema check to `evt.metadata.generated_schema is not None`, instantiate `ProgressTracePayloadDTO` in `_emit_preflight_progress`, instantiate `TraceEventMetadataDTO` in LLM strategies and state reducers, and pass `starvation_dto` directly. | Step 5 | [ ] Pending |
| REQ-006 | SynthesisPayloadCompressor Cleanup: Replace 3 naked `dict[str, Any]` annotations with `dict[str, JsonValue]` at lines 221, 293, and 374, and delete unreachable dead return statement. | Step 6 | [ ] Pending |
| REQ-007 | DTO & Cross-Domain Parity Hardening: Add `String? status` field to Flutter `DistilledEvaluation` factory constructor, run Freezed code generation, type `StepContextMetadataDTO.gvars` as `dict[str, JsonValue]`, type `TranslationResponseDTO.translated_data` as `dict[str, JsonValue]`, type `XAILogDto.engine_debug_trace` as `dict[str, JsonValue]`, type `LightweightMatrixOutput.extensions` as `dict[LaxXaiExtensionType, JsonValue]`, clean up duplicate `= Field(...)` assignments, and type `SynthesisMetadataDTO.global_context_vars` as `GlobalContextVarsDTO \| None`. | Step 7 | [ ] Pending |
| REQ-008 | Locale & Internationalization SSOT Harmonization: Add `SV = "sv"` to `SystemLocale` in Python and `@JsonValue('sv') sv` in Dart, add `profileLanguageSv` to `app_en.arb` and `app_fi.arb`, add `SystemLocale.sv` to exhaustive switch in `profile_general_tab.dart`, bind `UserBase.language` to `SystemLocale`, assign `locale = context.locale` directly in `printable_sources_adapter.py`, dynamically pass runtime `language` into `_process_questionnaire` with explicit sequential resolution, and reference `SystemLocale.EN.value` across defaults. | Step 8 | [ ] Pending |
| REQ-009 | Unit Test Modernization & ISTQB Expansion: Modernize fixtures in `test_state.py` to pass typed DTO instances, add ISTQB negative partition 1 (`test_state_projector_invalid_payload_raises_validation_failed`), add ISTQB negative partition 2 (`test_trace_event_untyped_arbitrary_object_raises_validation_error`), add negative partition to `test_context_router.py`, and add questionnaire title resolution test under non-English locales in `test_input_processing.py`. | Step 9 | [ ] Pending |
| REQ-010 | Deterministic AST Audit Verification: Run `audit_dict_eradication.py --strict` across touched files (`state.py`, `synthesis_payload_compressor.py`, DTOs, LLM strategies, synthesis engine, state reducer) to mathematically verify 0 naked dicts and 0 reflection calls, and run `audit_dto_parity.py` to verify 0 cross-domain mismatches. | Step 10 | [ ] Pending |
| REQ-011 | Universal Quality Gate Completion: Run localized `backend_audit_loop.py` on touched backend files, run Flutter audit loop on modified models and views (`distilled_evaluation.dart`, `enums.dart`, `profile_general_tab.dart`), and run isolated unit test suites with 100% pass rate. | Step 11 | [ ] Pending |
| REQ-012 | Atomic Checkpoint Commits: Stage specifically and exhaustively touched files and instruct atomic git commit with Conventional Commits message `refactor(orchestrator): enforce strict pydantic v2 type safety and dynamic locale ssot across pipeline state transit`. | Step 12 | [ ] Pending |

---

# Session Handover Context

## Achieved
- Standalone Implementation Plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] fully vetted through Tier 0 Research with 5-Column Architectural Directives Table and 14-Attack-Vector Red-Team Analysis.
- Standardized double-entry bookkeeping tracker generated at @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md] with 1:1 mapping of all 12 implementation steps and 29 production target files (24 backend, 5 frontend).

## Learned
- `StateProjector._snapshot` cannot be typed as `dict[str, dict[str, StepPayloadValue]]` because it triggers an AST Primitive Obsession violation under `audit_dict_eradication.py`; typing as `dict[str, StepOutputContentDTO]` reuses the authoritative SSOT DTO and cleanly wraps GDPR tombstone payloads without type violations.
- `TraceEventMetadataEnvelope` has a sanctioned AST exemption in `test_ast_domain_security_guardrails.py#L81` because it acts as an envelope projection filter for polymorphic SDUI blocks, while `TraceEventMetadataDTO` must enforce strict `extra="forbid"`.
- `_process_questionnaire` had a hardcoded `expected_input.label.resolve("en")` call that crashed with a configuration error on Finnish/Swedish workflows; updating the signature to accept dynamic `target_locale` and resolving sequentially with explicit `if not title_text:` checks restores internationalization without QGR016 chained `or` warnings.
- Flutter `distilled_evaluation.dart` was missing the `status` field, causing cross-domain DTO parity audit to fail; adding `String? status` restores full-duplex serialization parity.

## Remaining
- Execution of Plan Steps 1 through 12 via `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md]`.

## Resume Command
```
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md] @[docs/implementationplans/TRACKER_Pipeline_State_Transit_Type_Safety.md]
```
