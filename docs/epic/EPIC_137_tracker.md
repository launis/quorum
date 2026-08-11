# EPIC 137 Tracker: Qualitative Depth Restoration & TDA Extraction Fix

@[c:\src\quorum\docs\epic\EPIC_137_Qualitative_Depth_Restoration.md]
@[c:\src\quorum\docs\epic\EPIC_137_plans/]

<required_context_rules>
- @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
- @[c:\src\quorum\.agents\rules\01-python-backend.md]
- @[c:\src\quorum\.agents\rules\03_seed_vault.md]
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[c:\src\quorum\.agents\rules\05_llm_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\execution_engine_protocol\artifacts\ki_execution_engine_protocol.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\domain_model_prompt_separation\artifacts\ki_domain_model_prompt_separation.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\context_enriched_pipeline\artifacts\ki_context_enriched_decompose_verify.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\de_generator_execution_paradigm\artifacts\ki_de_generator_execution_paradigm.md]
</required_context_rules>

## Phase Execution Status

### Phase 1: Database Snapshot & Seed Hygiene
**Plan:** @[c:\src\quorum\docs\epic\EPIC_137_plans\01_phase1_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\01_phase1_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_137_plans\01_phase1_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
  - [ ] Step 1: Backup `seed_data.json` to `backend_v2/seed/backups/seed_data_pre_epic137.json`.
  - [ ] Step 2: Audit and list block IDs and line boundaries.
  - [ ] Step 3: Update `tone_instruction` for `prf_5d6e7f8091a2b3c4`.
  - [ ] Step 4: Standardize all `theory_grounding.citation_reference` to APA.
  - [ ] Step 5: Clean up `ai_description` rules.
  - [ ] Step 6: Validate JSON structure correctness using Python `json.load`.
  - [ ] Step 7: Flush Context with Session Handover.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\01_phase1_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`

### Phase 2: Dead Code Eradication
**Plan:** @[c:\src\quorum\docs\epic\EPIC_137_plans\02_phase2_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\02_phase2_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_137_plans\02_phase2_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
  - [ ] Step 1: Resume session.
  - [ ] Step 2: Delete `compile_xml_rubrics()` from localization & prompt compiler.
  - [ ] Step 3: Delete `compile_chunk_prompt()` from adapter.
  - [ ] Step 4: Delete matching dead unit tests from 4 test files.
  - [ ] Step 5: Run `--test` to verify code removal safety.
  - [ ] Step 6: Flush Context with Session Handover.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\02_phase2_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`

### Phase 3: DTO Strictness & Engine Metadata Wiring
**Plan:** @[c:\src\quorum\docs\epic\EPIC_137_plans\03_phase3_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\03_phase3_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_137_plans\03_phase3_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
  - [ ] Step 1: Resume session.
  - [ ] Step 2: Define strict `MatrixEvaluationContext` using exact native schema fields.
  - [ ] Step 3: Append `matrix_context` field to `EngineExecutionRequest`.
  - [ ] Step 4: Flush Context with Session Handover.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\03_phase3_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`

### Phase 4: TDA Pipeline Rewiring
**Plan:** @[c:\src\quorum\docs\epic\EPIC_137_plans\04_phase4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\04_phase4_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_137_plans\04_phase4_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
  - [ ] Step 1: Resume session.
  - [ ] Step 2: Mutate `llm.py` to inject Context and fix `getattr` rule violation.
  - [ ] Step 3: Mutate `tda_engine.py` to passthrough Context.
  - [ ] Step 4: Update `execute_graph()` inside DAG Executor for Context parameter.
  - [ ] Step 5: Flush Context with Session Handover.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\04_phase4_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`

### Phase 5: Sensor Prompt Re-Architecture
**Plan:** @[c:\src\quorum\docs\epic\EPIC_137_plans\05_phase5_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\05_phase5_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_137_plans\05_phase5_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
  - [ ] Step 1: Resume session.
  - [ ] Step 2: Establish `MatrixSensorPromptBuilder`.
  - [ ] Step 3: Construct static/dynamic string caching boundaries.
  - [ ] Step 4: Inject builder into `ExtractiveSensorService`.
  - [ ] Step 5: Synchronize builder inside DAG callback for caching parity.
  - [ ] Step 6: Flush Context with Session Handover.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\05_phase5_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`

### Phase 6: Negative Testing & Mocks & Final Audit
**Plan:** @[c:\src\quorum\docs\epic\EPIC_137_plans\06_phase6_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\06_phase6_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_137_plans\06_phase6_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
  - [ ] Step 1: Resume session.
  - [ ] Step 2: Refactor all `AsyncMock` references globally for Sensor Service.
  - [ ] Step 3: Engineer Negative Tests for Missing Theory Grounding / Bypass Blocks.
  - [ ] Step 4: Perform Global Python Audit.
  - [ ] Step 5: Commit changes to seed DB.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\06_phase6_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`


### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend Integration Verification**
- [ ] **[NOK] Frontend Rendering Integration**

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_137_Qualitative_Depth_Restoration.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
You MUST update the `/tier5-resume` or `/tier0-research-plan` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands (specifically: `/tier0-research-plan`, `/tier2-execute`, `/tier8-audit-plan`). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating. All seed modifications MUST be atomic `multi_replace_file_content` calls, verified by `uv run python backend_v2/seed/run_seed.py local`. Use strict `@-reference` syntax for all file targets.

## Requirements Traceability Matrix
| Requirement ID | Description | Phase & Step |
|----------------|-------------|--------------|
| R1 | Upgrade Tone Instruction to Senior Executive Coach in `prf_5d6e7f8091a2b3c4` | Phase 1, Step 3 |
| R2 | Formalize `theory_grounding.citation_reference` to APA via web search | Phase 1, Step 4 |
| R3 | Strip `RULES:` blocks from `ai_description` across all seed matrices | Phase 1, Step 5 |
| R4 | Ensure `seed_data.json` mutational syntax validity (No Python scripts) | Phase 1, Step 2, 6 |
| R5 | Eliminate `compile_xml_rubrics` from Prompt & Localization Compilers | Phase 2, Step 2 |
| R6 | Eliminate `compile_chunk_prompt` from Prompt Compiler Adapter | Phase 2, Step 3 |
| R7 | Destroy dead code tests tied to deleted compiler methods | Phase 2, Step 4 |
| R8 | Construct `MatrixEvaluationContext` DTO natively structurally before execution payload | Phase 3, Step 2 |
| R9 | Append `matrix_context` to `EngineExecutionRequest` | Phase 3, Step 3 |
| R10 | Safely fix `getattr(b, "category_id")` violation inside `llm.py` | Phase 4, Step 2 |
| R11 | TDAEngine natively delegates Context payload downstream | Phase 4, Step 3 |
| R12 | `enriched_dag_executor.py` processes Context as an optional pass-through | Phase 4, Step 4 |
| R13 | Create completely decoupled `MatrixSensorPromptBuilder` class | Phase 5, Step 2 |
| R14 | Assemble static caching boundaries and dynamic context logic independently | Phase 5, Step 3 |
| R15 | Refactor Sensor Service and DAG Callback to harness the new Builder | Phase 5, Step 4, 5 |
| R16 | Guarantee negative validation of `AsyncMock` and API integrations | Phase 6, Step 2, 3 |

# Session Handover Context
## Achieved
- Formally compiled the comprehensive Tier 1 Implementation Plans (Phases 1-6) into the strict architectural tracker.
- Mapped all Epic 137 requirements into the Traceability Matrix.

## Learned
- **Baseline State Snapshot**: `seed_data.json` currently uses raw `"RULES:"` prefixes inside `ai_description` and non-APA localized citations. `ExtractiveSensorService.evaluate_atom_boolean_batch()` uses an overly generic prompt that lacks `<theory_grounding>`. The `prompt_compiler.py` and `localization_compiler.py` files contain dead code methods (`compile_xml_rubrics`) that have zero production callers. `llm.py` contains a `getattr(b, "category_id", None)` which violates the strict fail-fast property access rule.

## Remaining
- Immediate execution of Phase 1: Database Snapshot & Seed Hygiene.

## Resume Command
`/tier0-research-plan @[c:\src\quorum\docs\epic\EPIC_137_plans\01_phase1_plan.md] @[c:\src\quorum\docs\epic\EPIC_137_tracker.md]`
