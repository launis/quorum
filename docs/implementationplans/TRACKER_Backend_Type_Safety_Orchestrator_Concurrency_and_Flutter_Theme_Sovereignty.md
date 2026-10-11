# Tracker: Backend Type Safety, Orchestrator Concurrency, State Reduction, LLM Caching, SDUI Dumb Painter, Flutter UI/Theme Hardening & Test Fixture AST Guardrails

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]

- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md] @[docs/implementationplans/TRACKER_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]`
  - [x] Step 1: Harden SynthesisMetadataDTO and TranslationResponseDTO Typing
  - [x] Step 2: Add Invariant Validation to StepPanelDTO
  - [x] Step 3: Unify FlattenedAtom Base Hierarchy
  - [x] Step 5: Type-Harden GlobalContextVarsDTO and Refactor state_reducer.py (Zero Dict Wrappers)
  - [ ] Step 6: Implement Wave-Based TaskGroup Step Execution and DLQ Handlers in dag_executor.py
  - [ ] Step 7: Harden TopologicalEvaluator Wave Crash Recovery
  - [ ] Step 8: Seal XML Sandwich and CDATA Shielding in prompt_compiler.py
  - [ ] Step 9: Eradicate Regex Prompt Scraping in prompt_compiler_adapter.py
  - [ ] Step 10: Enforce Fail-Fast Purity Scanning in caching_service.py
  - [ ] Step 11: Relocate Output Profile Directives to Dynamic User Tail in strategies/llm.py
  - [ ] Step 12: Harden SDUI Adapters, Dumb Painter Boundaries and Relocate SduiMapperService
  - [ ] Step 13: Enforce Theme Sovereignty, Strict Boundary Validation, and Flutter UI Hardening
  - [ ] Step 14: Implement Targeted QGR029 AST Guardrail, Polyfactory Suite Expansion and Test Fixture Hardening
  - [ ] Step 15: Implement ISTQB Unit Tests and Verify Quality Gates
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md] @[docs/implementationplans/TRACKER_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` on modified production backend files.
  - [ ] @[backend_v2/llm/caching_service.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/models/domain/matrix.py]
  - [ ] @[backend_v2/models/domain/scoring.py]
  - [ ] @[backend_v2/models/domain/synthesis.py]
  - [ ] @[backend_v2/models/dtos/global_context.py]
  - [ ] @[backend_v2/models/dtos/state.py]
  - [ ] @[backend_v2/models/view/sdui.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/prompt_compiler.py]
  - [ ] @[backend_v2/services/orchestrator/prompt_compiler_adapter.py]
  - [ ] @[backend_v2/services/orchestrator/state_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/services/orchestrator/topological_evaluator.py]
  - [ ] @[backend_v2/services/sdui/adapters/__init__.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/penalties_adapter.py]
  - [ ] @[backend_v2/services/sdui/sdui_mapper_service.py]
  - [ ] @[backend_v2/services/sdui_mapper_service.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_flutter_theme_sovereignty.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` on modified production frontend files.
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]
  - [ ] @[client_app_v2/lib/l10n/app_en.arb]
  - [ ] @[client_app_v2/lib/l10n/app_fi.arb]
  - [ ] @[client_app_v2/lib/shared/widgets/result_dashboard.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/specialist_section.dart]
  - [ ] @[client_app_v2/lib/theme/app_colors.dart]
  - [ ] @[client_app_v2/lib/theme/app_theme.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md] @[ki_zero_permissive_typing.md] @[ki_god_code_prevention.md] @[ki_python_314_concurrency_strictness.md] @[ki_topological_engine.md] @[ki_dag_engine_dto_projection_rules.md] @[ki_prompt_orchestration_and_matrix_evaluation.md] @[ki_opentelemetry_logfire_observability.md] @[ki_dumb_painter_sdui.md] @[ki_dual_axis_localization_architecture.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_zero_permissive_typing.md]`: Document AST guardrail rule QGR029 banning untyped dictionary fixture returns in tests, Polyfactory test fixture patterns, and elimination of residual `dict[str, JsonValue]` in `SynthesisMetadataDTO` and `TranslationResponseDTO`.
     - `@[ki_god_code_prevention.md]`: Document relocation of `SduiMapperService` to canonical `backend_v2/services/sdui/sdui_mapper_service.py` and eradication of monolithic root mapper with zero backward compatibility.
     - `@[ki_python_314_concurrency_strictness.md]`: Document Kahn's wave-based topological `TaskGroup` execution in `dag_executor.py` with PEP 758 `except*` handlers, DLQ task cancellation recording, and `ExecutionRecord.transition_step` atomic state synchronization with `_update_lock`.
     - `@[ki_topological_engine.md]`: Document `TopologicalEvaluator` wave crash recovery capturing `BaseException` and transitioning all unreached downstream nodes to `BLOCKED` or `SYSTEM_ERROR`.
     - `@[ki_dag_engine_dto_projection_rules.md]`: Document elimination of `_EvaluativeMatricesWrapperDTO` and dict wrappers in `state_reducer.py` in favor of direct Pydantic DTO fields on `GlobalContextVarsDTO`.
     - `@[ki_prompt_orchestration_and_matrix_evaluation.md]`: Document complete XML sandwich chat history containment, CDATA prompt breakout shielding in `prompt_compiler.py`, eradication of regex prompt scraping in `prompt_compiler_adapter.py`, and relocation of dynamic output profile directives to Layer 4 dynamic user tail in `strategies/llm.py`.
     - `@[ki_opentelemetry_logfire_observability.md]`: Document Fail-Fast purity scanning in `caching_service.py` raising `AppException(ErrorCodes.VALIDATION_FAILED)` upon detecting timestamps or UUIDs in static prompt prefix.
     - `@[ki_dumb_painter_sdui.md]`: Document deterministic matrix graph emission by `view_type`, clean alert block emission in `penalties_adapter.py`, schema-driven column visibility in `matrix_summary_table_adapter.py`, and `AppErrorBoundary` wrapping in `sdui_blocks_renderer.dart`.
     - `@[ki_dual_axis_localization_architecture.md]`: Document Flutter Theme Sovereignty architecture (total ban on direct `Color` and naked `TextStyle`, `AppSemanticColors` ThemeExtension, FlexColorScheme integration, and automated verification via `scripts/audit_flutter_theme_sovereignty.py`) and 1:1 `.arb` extraction.
  2. **Directory Reference Sync:**
     - Register `backend_v2/services/sdui/sdui_mapper_service.py` under SDUI services and remove legacy root reference.
     - Register `scripts/audit_flutter_theme_sovereignty.py` under Static Guardrails and Audits.
     - Register `backend_v2/tests/factories/model_factories.py` and `backend_v2/tests/factories/test_model_factories.py` under Test Infrastructure.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/01_system_context_and_invariants.md` describing Theme Sovereignty (zero direct styling in Flutter widgets), direct Pydantic DTO state transit, and QGR029 fixture AST rules in present tense.
     - Update `docs/architecture/03_execution_runtime_and_engine.md` describing wave-based topological `TaskGroup` execution, atomic step transitions, and crash recovery.
     - Update `docs/architecture/05_resilience_and_observability.md` describing fail-fast caching purity scanning, DLQ task cancellation recording, and SDUI composite block error boundaries.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md] @[docs/implementationplans/TRACKER_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

1. **Step-by-Step Execution**: By default, execute ONE step at a time. Run localized tests via `backend_audit_loop.py` or `flutter_audit_loop.py` after each step, then stop and report status to the user.
2. **Continuous Full-Auto Mode**: If the user provides `--full-auto` or grants explicit continuous permission, proceed autonomously across steps as long as quality gates pass 100%. Halt immediately on failure or when triggering `context_amnesia_prevention` handover.
3. **Atomic Commit Mandate**: After each step's quality gate passes, instruct the user to execute an atomic `git commit` formatted according to Conventional Commits before proceeding.
4. **Zero Permissive Typing & SSOT Compliance**: Enforce strict Pydantic V2/Freezed schemas and 100% typed domain transit. Never create runtime dictionaries (`d = {}`, `d[k] = v`, `_EvaluativeMatricesWrapperDTO`) in state reduction or service layers.
5. **Theme Sovereignty Compliance**: In Flutter widgets, never instantiate raw `Color(...)`, `Colors.*`, or naked `TextStyle(...)`. Derive all colors from `Theme.of(context).colorScheme` or `AppSemanticColors`, and all text styles from `Theme.of(context).textTheme`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Remove residual open-JSON `dict[str, JsonValue]` in `SynthesisMetadataDTO` and `TranslationResponseDTO` | Step 1 | [x] Completed |
| REQ-002 | Add `@model_validator(mode="after")` to `StepPanelDTO` verifying non-empty analysis payloads | Step 2 | [x] Completed |
| REQ-003 | Clean up base class divergence on `FlattenedAtom` in `matrix.py` to inherit from `V2CoreBase` | Step 3 | [x] Completed |
| REQ-004 | Implement atomic `ExecutionRecord.transition_step` synchronizing `steps` list and `step_states` dict | Step 4 | [x] Completed |
| REQ-005 | Add strongly typed fields to `GlobalContextVarsDTO` for cognitive deltas and delete `_EvaluativeMatricesWrapperDTO` | Step 5 | [x] Completed |
| REQ-006 | Refactor `state_reducer.py` to execute pure Pydantic DTO updates (zero dict wrappers, zero `d[k]=v`) | Step 5 | [x] Completed |
| REQ-007 | Compute Kahn's topological waves and execute steps via wave-based `asyncio.TaskGroup` in `dag_executor.py` | Step 6 | [ ] Pending |
| REQ-008 | Wrap wave execution with PEP 758 `except*` handlers and commit unreached steps to DLQ | Step 6 | [ ] Pending |
| REQ-009 | Delegate all 11 state mutations in `dag_executor.py` to `exec_record.transition_step(...)` with `_update_lock` | Step 6 | [ ] Pending |
| REQ-010 | Harden `TopologicalEvaluator` callback handling to catch `BaseException` and fail fast without orphan nodes | Step 7 | [ ] Pending |
| REQ-011 | Seal unwrapped string branches for `is_chat_history` inside `<chat_history>` in `prompt_compiler.py` | Step 8 | [ ] Pending |
| REQ-012 | Eradicate fallback for unknown `$source_path` inputs in `prompt_compiler.py` (fail fast on unmapped prefixes) | Step 8 | [ ] Pending |
| REQ-013 | Eradicate regex prompt scraping (`<execution_parameters>`) in `prompt_compiler_adapter.py` | Step 9 | [ ] Pending |
| REQ-014 | Remove silent message-popping shims (`last_msg = static_msgs.pop()`) in `prompt_compiler_adapter.py` | Step 9 | [ ] Pending |
| REQ-015 | Upgrade passive purity logging to Fail-Fast `AppException` in `caching_service.py` | Step 10 | [ ] Pending |
| REQ-016 | Purge dynamic output profile injection from `base_system_prompt` and move to `user_payload` in `strategies/llm.py` | Step 11 | [ ] Pending |
| REQ-017 | Eradicate heuristic axis count guessing fallbacks and ad-hoc `MarkdownBlock` headers in `matrix_graphs_adapter.py` | Step 12 | [ ] Pending |
| REQ-018 | Eradicate manual string concatenations and punctuation surgery in `penalties_adapter.py` | Step 12 | [ ] Pending |
| REQ-019 | Eliminate `or STANDARD_COLUMNS` lazy code fallback in `matrix_summary_table_adapter.py` | Step 12 | [ ] Pending |
| REQ-020 | Explicitly re-export `VarianceAdapter` in `services/sdui/adapters/__init__.py` | Step 12 | [ ] Pending |
| REQ-021 | Relocate `sdui_mapper_service.py` to canonical `backend_v2/services/sdui/sdui_mapper_service.py` and delete root file | Step 12 | [ ] Pending |
| REQ-022 | Enforce strict non-empty string check on persona capitalization and ban `safeSubstring` in `result_dashboard.dart` | Step 13 | [ ] Pending |
| REQ-023 | Register `AppSemanticColors` as `ThemeExtension` in `app_theme.dart` (light and dark) and refactor `app_colors.dart` | Step 13 | [ ] Pending |
| REQ-024 | Eradicate naked `TextStyle` and static colors in `bars_matrix_builder.dart`, `atom_matrix_table_widget.dart`, `specialist_section.dart`, and `result_dashboard.dart` | Step 13 | [ ] Pending |
| REQ-025 | Extract hardcoded UI chrome strings into `.arb` localization files with 1:1 English/Finnish parity | Step 13 | [ ] Pending |
| REQ-026 | Wrap autonomous composite SDUI blocks with `AppErrorBoundary` in `sdui_blocks_renderer.dart` | Step 13 | [ ] Pending |
| REQ-027 | Implement static audit CLI `scripts/audit_flutter_theme_sovereignty.py` | Step 13 | [ ] Pending |
| REQ-028 | Implement AST guardrail `QGR029`, Polyfactory suite expansion, static test snapshot DTO deserialization, and repository persistence refactor | Step 14 | [ ] Pending |
| REQ-029 | Implement comprehensive ISTQB unit tests, verification suites, and pass all automated quality gates | Step 15 | [ ] Pending |

# Session Handover Context

## Achieved
- Formulated and verified Implementation Plan at `@[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]`.
- Successfully generated standalone implementation tracker at `@[docs/implementationplans/TRACKER_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]` with 15 granular execution steps, 22 backend and 9 frontend production hardening targets, 29 traceability matrix rows, and parameterized Tier 7 directives.
- Verified 100% structural compliance and plan-tracker parity against `scripts/audit_tracker_output.py` and `scripts/audit_plan_tracker_parity.py`.
- Completed Tier 0 Research and System 2 adversarial audit (`/tier0-research-plan`), verifying zero backward compatibility, zero permissive dicts, Kahn's wave concurrency, Theme Sovereignty, and QGR029 AST guardrails.

## Learned
- In `IMPLEMENTATION_PLAN_...md`, explicit `[MODIFY]`, `[NEW]`, and `[DELETE]` tags on all architectural directives ensure deterministic target discovery by `audit_plan_tracker_parity.py`.
- Theme Sovereignty mandates zero direct `Color(...)`, `Colors.*`, or naked `TextStyle(...)` instantiations in Flutter widgets, deriving all styling purely from `Theme.of(context)` tokens and `ThemeExtension<AppSemanticColors>`.
- Concurrency hardening requires Kahn's wave-based topological `asyncio.TaskGroup` step execution with PEP 758 `except*` handlers, DLQ failure recording, and atomic `transition_step` mutations guarded by `_update_lock`.
- Mathematical AST line bounds must align precisely with `ast.ClassDef.end_lineno` (specifically: `SynthesisMetadataDTO` spanning lines 225–262).

## Remaining
- Execute Step 1 through Step 15 via `/tier2-execute`.
- Complete Post-Implementation Gates (Golden Master audit, Tier 2 Hardening Backend/Frontend, Pre-Delete audit, Semantic Coverage).
- Execute As-Built Architectural Sync via parameterized `/tier7-describe-architecture`.
- Execute Final Plan Audit via `/tier8-audit-plan`.

## Resume Command
```powershell
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md] @[docs/implementationplans/TRACKER_Backend_Type_Safety_Orchestrator_Concurrency_and_Flutter_Theme_Sovereignty.md]
```
