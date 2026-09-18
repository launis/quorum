# Tracker: ExecutionRecord Hardening & Technical Debt Resolution
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Execution_Record_Hardening_and_Tech_Debt.md]

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

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Execution_Record_Hardening_and_Tech_Debt.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Execution_Record_Hardening_and_Tech_Debt.md] @[docs/implementationplans/TRACKER_Execution_Record_Hardening_and_Tech_Debt.md]`
  - [ ] Step 1.0: ADD_SSE_FIELDS_TO_EXECUTION_STEP_MODELS
  - [ ] Step 1.1: REFACTOR_EXECUTION_TIMELINE_TO_TYPED_STEPS
  - [ ] Step 1.2: DECOUPLE_EXECUTION_VIEW_STEP_STATES_CONVERSION
  - [ ] Step 1.3: ERADICATE_DEAD_NOQA_SUPPRESSIONS
  - [ ] Step 1.4: DELETE_OBSOLETE_EXECUTION_INPUTS_MODEL
  - [ ] Step 1.5: DELETE_DEAD_EXECUTION_STATUS_CARD_WIDGET
  - [ ] Step 1.6: SYNCHRONIZE_DAG_EXECUTOR_AND_WORKER_STEP_PROGRESS_AND_WARNING
  - [ ] Step 2.1: OPTIMIZE_SSE_STREAM_STATUS_POLLING
  - [ ] Step 2.2: HARDEN_CHECK_RESUMABILITY_AND_FACTORY_TYPING
  - [ ] Step 2.3: ADD_SSE_SETTINGS_TO_SETTINGS_PY
  - [ ] Step 2.4: HARDEN_CONTEXT_VARIABLES_AND_MATH_UTILS_RESOLVER
  - [ ] Step 3.0: CONFIGURE_FLUTTER_ANALYSIS_OPTIONS
  - [ ] Step 3.1: CREATE_EXECUTION_SUMMARY_SNAPSHOT_DTO
  - [ ] Step 3.2: CREATE_WORKFLOW_INPUTS_DTO
  - [ ] Step 3.3: HARDEN_EXECUTION_STEP_AND_RECORD_MODELS
  - [ ] Step 3.4: ERADICATE_DE_GENERATOR_POLICY_AND_TYPIFY_EXECUTION_CLIENT
  - [ ] Step 3.5: CREATE_FROZEN_CONTEXT_SNAPSHOT_DTO
  - [ ] Step 4.1: RUN_BUILD_RUNNER_GENERATION
  - [ ] Step 4.2: SYNCHRONIZE_TEST_FIXTURES_AND_EXPAND_ISTQB
  - [ ] Step 5.1: RUN_QUALITY_GATES
  - [ ] Step 5.2: ATOMIC_GIT_COMMIT
  - [ ] Step 6.1: AUDIT_CODE_DIFFS_AND_CHANGE_REVIEW
  - [ ] Step 6.2: UPDATE_KNOWLEDGE_ITEMS
  - [ ] Step 6.3: EXECUTE_TIER7_ARCHITECTURE_SYNC
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Execution_Record_Hardening_and_Tech_Debt.md] @[docs/implementationplans/TRACKER_Execution_Record_Hardening_and_Tech_Debt.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files.
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/services/execution.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/utils/math_utils.py]
  - [ ] @[backend_v2/worker.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files.
  - [ ] @[client_app_v2/analysis_options.yaml]
  - [ ] @[client_app_v2/lib/core/api/execution_client.dart]
  - [ ] @[client_app_v2/lib/features/execution/controllers/execution_controller.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_record.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_step.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/workflow_inputs.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/execution_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/execution_timeline.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Execution_Record_Hardening_and_Tech_Debt.md] @[docs/implementationplans/TRACKER_Execution_Record_Hardening_and_Tech_Debt.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

1. **Strict Execution Invariant**:
   - Domain implementation code MUST NOT be written without an explicit `/tier2-execute` execution prompt from the user.
   - Stop and wait for user instruction before mutating source files.
2. **Quality Gate Loop**:
   - After each logical batch of edits to Python files, run `uv run python scripts/backend_audit_loop.py <target_path> --test`.
   - After each logical batch of edits to Dart files, run `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`.
3. **Atomic Commit Protocol**:
   - After any passing quality gate run, instruct the user to execute an atomic commit following Conventional Commits format (`<type>(<scope>): <summary>`).
   - Accompany the commit command with an objective list of physical changes made.
4. **Session Handover Protocol**:
   - Execute `/tier5-session-handover` if processing >8 prompts, completing 3 atomic commits, or modifying >5 complex files.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-SSE-STEP-PROGRESS-WARNING | Add `progress` (0-100) and `has_warning` (bool) fields to `ExecutionStep` in `v2_core.py` and `execution_step.dart` | Step 1.0 | PENDING |
| REQ-TIMELINE-TYPED-STEPS | Refactor `ExecutionTimeline` constructor to accept `List<ExecutionStep>`, consume typed fields, enforce Title Containment, and tokenize theme colors | Step 1.1 | PENDING |
| REQ-EXECUTION-VIEW-DECOUPLING | Decouple `execution_view.dart` from untyped `stepStates` map, eliminate unused `frozenContext` map, consume typed `versionId`, and pass `record.steps` directly | Step 1.2 | PENDING |
| REQ-NOQA-SUPPRESSIONS-CLEANUP | Verify eradication of dead `# noqa: E501` hanging suppressions across `test_execution.py` and `test_executions.py` | Step 1.3 | PENDING |
| REQ-DELETE-EXECUTION-INPUTS | Migrate test references in `execution_models_test.dart` to `WorkflowInputs` and delete obsolete `execution_inputs.dart` model | Step 1.4 | PENDING |
| REQ-DELETE-EXECUTION-STATUS-CARD | Verify zero callers and delete dead `execution_status_card.dart` widget | Step 1.5 | PENDING |
| REQ-SYNC-DAG-STEP-PROGRESS-PERSISTENCE | Synchronize real-time advancement percentages, warnings, and states in `dag_executor.py` across all transitions, add `steps` to `ExecutionCommitter.commit_trace()`, guard against partial commit null overwrites, synchronize resumability resets and RAG preflights, and preserve execution telemetry in `worker.py` | Step 1.6 | PENDING |
| REQ-SSE-STREAM-POLLING-OPTIMIZATION | Optimize `stream_status` in `services/execution.py` to poll with `hydrate=False` and `skip_resumability=True`, bind settings for polling interval and retries, and serialize with `exclude_none=True` | Step 2.1 | PENDING |
| REQ-RESUMABILITY-AND-FACTORY-TYPING | Eradicate duck-typing and `# noqa: QGR012` from `create_execution_record` using `TypeAdapter`, exclude `sys_*` virtual items from validation set parity, and enforce typed dot-notation in `check_resumability` | Step 2.2 | PENDING |
| REQ-SSE-SETTINGS-SSOT | Add `sse_max_transient_retries` and `sse_polling_interval_seconds` configuration to `settings.py` | Step 2.3 | PENDING |
| REQ-CONTEXT-VARS-AND-PATH-RESOLVER | Encapsulate context variables via EvaluatedMatrixContextDTO in override_atom and refactor resolve_dot_notation in math_utils.py to typed path resolver | Step 2.4 | PENDING |
| REQ-FLUTTER-ANALYSIS-OPTIONS | Create analysis_options.yaml in client_app_v2 configuring invalid_annotation_target ignore on Freezed models | Step 3.0 | PENDING |
| REQ-DTO-EXECUTION-SUMMARY | Create `ExecutionSummarySnapshot` Freezed model with strict `@JsonSerializable(disallowUnrecognizedKeys: true)` | Step 3.1 | PENDING |
| REQ-DTO-WORKFLOW-INPUTS | Create `WorkflowInputs` Freezed model matching backend schema with dynamic input encapsulation | Step 3.2 | PENDING |
| REQ-DTO-RECORD-AND-STEP-HARDENING | Update `ExecutionStep.scorecardAtoms` to `Map<String, ScorecardAtomDto>` and type `ExecutionRecord` fields (`executionSummary`, `rawInputs`, `modelsUsed`, `frozenContext`, `stepStates`) | Step 3.3 | PENDING |
| REQ-EXECUTION-CLIENT-DE-GENERATOR-REMOVAL | Overthrow De-Generator Policy in `ExecutionClient`, return `Future<ExecutionRecord>` across methods, and consume typed dot-notation in `ExecutionController` | Step 3.4 | PENDING |
| REQ-DTO-FROZEN-CONTEXT-SNAPSHOT | Create `FrozenContextSnapshot` Freezed model with multi-payload parity across REST and SSE delta streams | Step 3.5 | PENDING |
| REQ-BUILD-RUNNER-CODEGEN | Execute `build_runner` in `client_app_v2` to generate Freezed and JSON serialization files | Step 4.1 | PENDING |
| REQ-TEST-SYNCHRONIZATION-AND-ISTQB | Synchronize test fixtures in `execution_models_test.dart`, expand ISTQB boundary tests, create `execution_timeline_test.dart`, synchronize `test_execution.py` mock signatures, and update client test mocks | Step 4.2 | PENDING |
| REQ-UNIVERSAL-QUALITY-GATES | Execute backend and Flutter audit loops ensuring 100% pass rate | Step 5.1 | PENDING |
| REQ-ATOMIC-GIT-COMMIT | Instruct atomic conventional commit with explicit staged files | Step 5.2 | PENDING |
| REQ-AUDIT-DIFFS-CHANGE-REVIEW | Audit physical diffs across Python and Flutter to verify zero permissive typing and clean architectural boundaries | Step 6.1 | PENDING |
| REQ-UPDATE-KNOWLEDGE-ITEMS | Synchronize `ki_execution_record_ssot.md` and `ki_zero_permissive_typing.md` in the knowledge base | Step 6.2 | PENDING |
| REQ-TIER7-ARCHITECTURE-SYNC | Execute `/tier7-describe-architecture` for `01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, and `05_resilience_and_observability.md` | Step 6.3 | PENDING |

# Session Handover Context

## Achieved
- Formally generated standalone plan tracker `TRACKER_Execution_Record_Hardening_and_Tech_Debt.md` establishing durable double-entry bookkeeping.
- Extracted all 23 execution protocol steps (Steps 1.0 through 6.3) into 1:1 tracked child checkboxes.
- Populated granular file-level hardening checklists for 5 backend and 11 Flutter production targets.
- Established bidirectional Requirements Traceability Matrix mapping all 23 plan steps to granular requirement keys.
- Anchored canonical `<required_context_rules>` block referencing core ideological constraints and all 5 domain knowledge items.

## Learned
- The implementation plan has completed 21 exhaustive passes of Tier 0 Research Plan analysis, bringing all 61 architectural discoveries into immediate in-scope execution.
- Production files requiring hardening include 5 Python backend files (`v2_core.py`, `execution.py`, `dag_executor.py`, `settings.py`, `worker.py`) and 11 Flutter frontend files (`analysis_options.yaml`, `execution_client.dart`, `execution_controller.dart`, `execution_record.dart`, `execution_step.dart`, `execution_summary_snapshot.dart`, `frozen_context_snapshot.dart`, `workflow_inputs.dart`, `execution_view.dart`, `new_execution_view.dart`, `execution_timeline.dart`).
- All dead suppressions and ghost references are pre-verified, and test mock interfaces are specifically targeted with AST precision.

## Remaining
- Execution of all 23 protocol steps across Phases 1 through 6 via `/tier2-execute`.
- Execution of file-level hardening loops (`/tier2-hardening-backend` and `/tier2-hardening-frontend`).
- Final red-team audit via `/tier8-audit-plan`.

## Resume Command
`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Execution_Record_Hardening_and_Tech_Debt.md] @[docs/implementationplans/TRACKER_Execution_Record_Hardening_and_Tech_Debt.md]`
