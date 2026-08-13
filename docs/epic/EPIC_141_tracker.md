# Epic 141: Holistic Executive Synthesis & RAG Alignment

**Tracker for:** @[docs\epic\EPIC_141_Holistic_Executive_Synthesis.md]
**Task Directory:** @[docs\epic\tasks_EPIC_141/]

<required_context_rules>
- @[.agents\rules\00-antigravity-core.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
</required_context_rules>

## Phase Execution Status

### Phase 1: DAG Engine Strategy Inference Refactoring
**Plan:** @[docs\epic\tasks_EPIC_141\Phase_1_DAG_Engine_Strategy.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_141\Phase_1_DAG_Engine_Strategy.md] @[docs\epic\EPIC_141_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_141\Phase_1_DAG_Engine_Strategy.md] @[docs\epic\EPIC_141_tracker.md]`
  - [ ] Step 1: Replace hardcoded synthesis block check with dynamic `model_strategy == "synthesis"` in `dag_executor.py`.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_141\Phase_1_DAG_Engine_Strategy.md] @[docs\epic\EPIC_141_tracker.md]`

### Phase 2: Distiller Extraction & Payload Compression Isolation
**Plan:** @[docs\epic\tasks_EPIC_141\Phase_2_Distiller_Extraction.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_141\Phase_2_Distiller_Extraction.md] @[docs\epic\EPIC_141_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_141\Phase_2_Distiller_Extraction.md] @[docs\epic\EPIC_141_tracker.md]`
  - [ ] Step 1: Create `synthesis_payload_compressor.py` and extract `_compress_synthesis_payload` from `synthesis_distiller.py`.
  - [ ] Step 2: Inject `max_synthesis_evaluations` into `settings.py`.
  - [ ] Step 3: Implement `DistilledEvaluation` Pydantic model in `models/domain/synthesis.py`.
  - [ ] Step 4: Refactor `synthesis_distiller.py` to use the new compressor and settings.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_141\Phase_2_Distiller_Extraction.md] @[docs\epic\EPIC_141_tracker.md]`

### Phase 3: Sensor Routing & Matrix Explanation Architecture
**Plan:** @[docs\epic\tasks_EPIC_141\Phase_3_Sensor_Routing.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_141\Phase_3_Sensor_Routing.md] @[docs\epic\EPIC_141_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_141\Phase_3_Sensor_Routing.md] @[docs\epic\EPIC_141_tracker.md]`
  - [ ] Step 1: Create `extractive_sensor_service.py` to handle Matrix assertion routing.
  - [ ] Step 2: Update `AtomExecutionState` in `dag_models.py` with `causal_reasoning`.
  - [ ] Step 3: Fix CDATA encapsulation bugs in `matrix_sensor_prompt_builder.py`.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_141\Phase_3_Sensor_Routing.md] @[docs\epic\EPIC_141_tracker.md]`

### Phase 4: Automated Testing Strategy
**Plan:** @[docs\epic\tasks_EPIC_141\Phase_4_Automated_Testing.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_141\Phase_4_Automated_Testing.md] @[docs\epic\EPIC_141_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_141\Phase_4_Automated_Testing.md] @[docs\epic\EPIC_141_tracker.md]`
  - [ ] Step 1: Write tests for `SynthesisPayloadCompressor` in `test_synthesis_payload_compression.py`.
  - [ ] Step 2: Write tests for `MatrixSensorPromptBuilder` in `test_matrix_sensor_prompt_builder.py`.
  - [ ] Step 3: Update `test_dag_taskgroup.py` and `test_bug_synthesis_hook.py`.
  - [ ] Step 4: Add structural assertions to `test_epic93_contract_verification.py`.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_141\Phase_4_Automated_Testing.md] @[docs\epic\EPIC_141_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] Backend and Frontend full-stack integration test gates.

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs\epic\EPIC_141_Holistic_Executive_Synthesis.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- Atomic commits MUST be performed after every phase using `git add` and `git commit` with English messages.
- Seeding environments MUST be executed locally if schema structures are modified via: `uv run python backend_v2/seed/run_seed.py local`
- You MUST maintain strict adherence to the `@-reference` syntax rule for all targeted files in workflows.
- You MUST update the `/tier5-resume` or `/tier0-research-plan` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands (specifically: `/tier0-research-plan`, `/tier2-execute`, `/tier8-audit-plan`). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

## Requirements Traceability Matrix
- [ ] **R1**: Replace hardcoded `task_blueprint == "sp_7a8b9c0d1e2f3a4b"` in `dag_executor.py` with dynamic `model_strategy == "synthesis"` (Phase 1, Step 1).
- [ ] **R2**: Extract payload compression logic from `synthesis_distiller.py` into a new `SynthesisPayloadCompressor` object (Phase 2, Step 1).
- [ ] **R3**: Add `max_synthesis_evaluations` property to `settings.py` (Phase 2, Step 2).
- [ ] **R4**: Define `DistilledEvaluation` Pydantic model in `models/domain/synthesis.py` (Phase 2, Step 3).
- [ ] **R5**: Refactor `synthesis_distiller.py` to use `max_synthesis_evaluations` instead of hardcoded `[:20]` cutoff (Phase 2, Step 4).
- [ ] **R6**: Create `extractive_sensor_service.py` to isolate Matrix assertion mappings (Phase 3, Step 1).
- [ ] **R7**: Add `causal_reasoning` string to `AtomExecutionState` in `dag_models.py` (Phase 3, Step 2).
- [ ] **R8**: Sanitize dynamic CDATA fields (`<question>`, `<extraction_rule>`) using `TemplateProcessor` in `matrix_sensor_prompt_builder.py` (Phase 3, Step 3).
- [ ] **R9**: Create unit test file `test_synthesis_payload_compression.py` (Phase 4, Step 1).
- [ ] **R10**: Create unit test file `test_matrix_sensor_prompt_builder.py` (Phase 4, Step 2).
- [ ] **R11**: Update `test_dag_taskgroup.py` and `test_bug_synthesis_hook.py` (Phase 4, Step 3).
- [ ] **R12**: Enhance structural assertions in `test_epic93_contract_verification.py` (Phase 4, Step 4).

# Session Handover Context
## Achieved
- Initialized Epic 141 planning.
- Created micro-chunked Phase 1-4 implementation plans in `docs/epic/tasks_EPIC_141`.
- Generated full `EPIC_141_tracker.md` to organize and audit the deployment workflow.

## Learned
- **Baseline State Snapshot**: `dag_executor.py` currently relies on hardcoded string matching (`sp_7a8b9c0d1e2f3a4b`) to branch into synthesis, which defeats dynamic routing.
- `synthesis_distiller.py` currently contains a huge `_compress_synthesis_payload` function serving as a "God File" bottleneck. The token budget cutoff is hardcoded as `lite_evals[:20]`.
- CDATA encapsulation is potentially broken for dynamic fields in the matrix sensor prompt builder, making it susceptible to XML injection from nested markdown lists.

## Remaining
- Begin Tier 0 research for Phase 1 to prepare for execution.

## Resume Command
`/tier0-research-plan @[docs\epic\tasks_EPIC_141\Phase_1_DAG_Engine_Strategy.md] @[docs\epic\EPIC_141_tracker.md]`
