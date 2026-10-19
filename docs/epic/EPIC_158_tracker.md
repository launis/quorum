<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
</required_context_rules>

# EPIC 158 Tracker: Multi-Segment Evidence Extraction, Morphological Decoupling & Causal Horizon Expansion

- **Epic:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]
- **Task Directory:** @[docs/epic/tasks_EPIC_158/]

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups & Foundations
- **Plan:** @[docs/epic/tasks_EPIC_158/01_phase1_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Baseline Verification
  - [x] Step 1: Verify duplicate Epic deletion and establish `coerce_source_quotes_tuple` SSOT in `core_base.py`
  - [x] Step 2: Modernize `QuoteEvidenceDTO` and define strongly typed `GateMatchResultDTO` anti-tuple contract
  - [x] Step 3: Remediate asymmetric quote extraction in `AnchorValidationService`
  - [x] Step 4: Clean up mutating `truncate_source_quote_at_sentence` and unannotated linker collection factories
  - [x] Step 5: Refine export formatter typing strictness and guard printable sources scalar access
  - [x] Step 6: Remediate Flutter Theme Sovereignty and localization in touched widgets
  - [x] Step 7: Implement and pass multi-segment foundation unit test suite
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 2: Domain Model, DTO, Client Freezed Contract & Test Fixture Multi-Segment Schema Refactoring (WP1)
- **Plan:** @[docs/epic/tasks_EPIC_158/02_phase2_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/02_phase2_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/02_phase2_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [x] Step 2.0: Look backward and forward to verify actual codebase state and contracts before refactoring
  - [x] Step 2.1: Refactor backend domain models and DAG DTOs to `source_quotes: tuple[str, ...] | None`
  - [x] Step 2.2: Refactor 1-hop caller orchestration, state reducer, and hook services
  - [x] Step 2.3: Update atom extraction prompts, system instructions, and schema descriptions
  - [x] Step 2.4: Synchronize Flutter Freezed DTO contracts and client citation widgets
  - [x] Step 2.5: Synchronize test fixtures, factories, golden master files, and unit test suites
- [x] **[OK] Test Coverage Assertions:** Strict 90% TDD gate passed with 96.15% line coverage (810 passed, 0 failures), 0 fatal AST guardrails, 0 residual debt ceiling violations, clean imports, and 100% Freezed build parity.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/02_phase2_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)
- **Plan:** @[docs/epic/tasks_EPIC_158/03_phase3_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [x] Step 3.0: Strategic alignment check and pre-implementation technical debt cleanups
  - [x] Step 3.1: Enhance coordinate normalization and strict matching for multi-segment tuples
  - [x] Step 3.2: Implement forward-scan search, monotonic ordering, and single-document buffer isolation in `AnchorValidationService`
  - [x] Step 3.3: Enforce single-document buffer isolation in atom processing
  - [x] Step 3.4: Update prompt extraction mandate in `matrix_evaluation.py` for 1–3 non-contiguous sentences
  - [x] Step 3.5: Expand ISTQB boundary and negative test suite in `test_anchor_validation_service.py`
- [x] **[OK] Test Coverage Assertions:** Strict 90% TDD gate passed with 93% line coverage on `anchor_validation_service.py` (49 passed, 0 failures) and 100% on `matrix_evaluation.py` (4 passed, 0 failures), 0 fatal AST guardrails, 0 residual debt ceiling violations, clean imports, and clean DTO parity.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)
- **Plan:** @[docs/epic/tasks_EPIC_158/04_phase4_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [x] Step 4.0: Strategic alignment check and baseline verification
  - [x] Step 4.1: Add `default_lexical_strictness_level` to `Workflow` domain model and Studio DTOs
  - [x] Step 4.2: Update Studio workflow CRUD service to transit decoupled lexical strictness
  - [x] Step 4.3: Synchronize database seed vault workflows and add localization strings
  - [x] Step 4.4: Calibrate settings lexical threshold resolution function
  - [x] Step 4.5: Transit decoupled lexical strictness in execution worker and DAG executor
  - [x] Step 4.6: Expand worker and anchor validation test suites verifying morphological calibration
- [x] **[OK] Test Coverage Assertions:** Strict 90% TDD gate passed with 93% line coverage on `anchor_validation_service.py` (53 passed, 0 failures), 100% on `workflow_service.py` and `execution_worker.py` (18 passed, 0 failures), dry-run seed validation 100% clean, 0 fatal AST guardrails, 0 residual debt ceiling violations, clean imports, and 100% DTO parity.
- [x] **[OK] Audit:** Completed Tier 8 Post-Implementation Red-Team Audit (`red_team_audit_phase4_plan.md`): 100% of requirements REQ-158-020 through REQ-158-025 verified on disk, 0 orphan requirements, 0 fatal AST violations, 0 supply chain violations, clean DTO parity, and global backend completion gate passed.

### Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)
- **Plan:** @[docs/epic/tasks_EPIC_158/05_phase5_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [x] Step 5.0: Strategic alignment check and baseline verification
  - [x] Step 5.1: Configure linker settings and budget capacity limits in `settings.py`
  - [x] Step 5.2: Implement bounded deliverable root axiom header injection with dynamic quota allocation in `SlidingWindowLinker`
  - [x] Step 5.3: Support multi-segment Toulmin warrants in causal edge records
  - [x] Step 5.4: Implement Algorithm 1 dual fault attribution separating warrant grounding failures
  - [x] Step 5.5: Expand causal linker and cohesion scoring test suites
- [x] **[OK] Test Coverage Assertions:** Universal Quality Gate passed with 100% clean check across all 10 gates. 53 unit tests passing across sliding window linker, causal cohesion scoring, and causal discovery engine. Strict 90% TDD line coverage achieved across all targets (sliding_window_linker.py 90%, causal_cohesion_evaluator.py 90%, settings.py 90%, dag_models.py 90%, causal_discovery.py 90%, causal_discovery_engine.py 90%). 0 fatal AST guardrail violations (QGR016, QGR023 resolved), 0 residual debt ceiling violations, 365 clean imports, and 100% full-duplex DTO parity (52/52 models aligned between Python and Flutter Freezed code).
- [x] **[OK] Audit:** Completed Tier 8 Post-Implementation Red-Team Audit (`red_team_audit_phase5_plan.md`): 100% of requirements REQ-158-026 through REQ-158-030 verified on disk, 0 orphan requirements, 0 fatal AST violations, 0 supply chain violations, clean DTO parity, 54 unit tests passing, and global backend completion gate passed.

### Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)
- **Plan:** @[docs/epic/tasks_EPIC_158/06_phase6_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [x] Step 6.0: Strategic alignment check and baseline verification
  - [x] Step 6.1: Synchronize tabular export streaming services for CSV and Excel formats
  - [x] Step 6.2: Update SDUI highlights and printable sources adapters
  - [x] Step 6.3: Remediate Jinja2 PDF template evidence quote emission
  - [x] Step 6.4: Regenerate OpenAPI specification artifact reflecting schema updates
  - [x] Step 6.5: Implement Studio continuous slider for lexical verification strictness
  - [x] Step 6.6: Update client citation and causal inspector widgets
  - [x] Step 6.7: Execute presentation and Flutter client audit gates
- [x] **[OK] Test Coverage Assertions:** Universal Quality Gate passed with 100% clean check across all 10 backend quality gates (`backend_audit_loop.py`). All 97 backend unit tests passing across export formatter, export service, printable sources adapter, PDF generator, and report headers l10n parity. Flutter audit loop passed 4/4 stages with 0 errors (`flutter_audit_loop.py client_app_v2/ --build`). Full Flutter test suite passing 590/590 tests with 0 failures (`flutter test`). 0 fatal AST guardrail violations, 0 residual debt violations, 100% Theme Sovereignty with 0 raw TextStyle instantiations.
- [x] **[OK] Audit:** Completed Tier 8 Post-Implementation Red-Team Audit (`red_team_audit_phase6_plan.md`): 100% of requirements REQ-158-031 through REQ-158-037 verified on disk, 0 orphan requirements, 0 fatal AST violations, 0 supply chain violations, clean DTO parity, 97 backend unit tests passing, Flutter audit loop passing 4/4 stages, and global backend completion gate passed with 5,635 tests (97.77% coverage).

### Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)
- **Plan:** @[docs/epic/tasks_EPIC_158/07_phase7_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 7.0: Strategic alignment check and baseline verification
  - [ ] Step 7.1: Implement end-to-end multi-segment integration test suite
  - [ ] Step 7.2: Execute offline ablation benchmark ($N=220$) and verify zero chimera leaks
  - [ ] Step 7.3: Execute full audit gates and mandatory live E2E real LLM test
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 8: As-Built Architectural Documentation & Scientific Manuscript Synchronization (`@[docs/tiede.md]`)
- **Plan:** @[docs/epic/tasks_EPIC_158/08_phase8_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/08_phase8_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/08_phase8_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 8.0: Strategic alignment check and baseline verification
  - [ ] Step 8.1: Update directory reference rule with new integration tests and services
  - [ ] Step 8.2: Synchronize scientific manuscript `docs/tiede.md` with formal definitions, theorems, and benchmark results
  - [ ] Step 8.3: Execute parameterized Tier 7 as-built architecture audit
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/08_phase8_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend Integration Suite**: Run `uv run pytest backend_v2/tests/integration/test_multi_segment_causal_e2e.py`
- [ ] **[NOK] Frontend Compilation & Build Runner Gate**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/models/dtos/quote_evidence.py]
  - [ ] @[backend_v2/models/domain/blackboard.py]
  - [ ] @[backend_v2/models/dtos/dag_models.py]
  - [ ] @[backend_v2/models/dtos/causal_discovery.py]
  - [ ] @[backend_v2/models/dtos/atom_result.py]
  - [ ] @[backend_v2/models/dtos/atom_evaluation.py]
  - [ ] @[backend_v2/models/dtos/matrix_scorecard.py]
  - [ ] @[backend_v2/models/dtos/report_artifact.py]
  - [ ] @[backend_v2/models/domain/workflow.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/services/orchestrator/extractive_sensor_service.py]
  - [ ] @[backend_v2/services/orchestrator/anchor_validation_service.py]
  - [ ] @[backend_v2/services/orchestrator/sliding_window_linker.py]
  - [ ] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]
  - [ ] @[backend_v2/services/orchestrator/result_projector.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/two_pass_atomizer.py]
  - [ ] @[backend_v2/services/orchestrator/topological_evaluator.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/workers/execution_worker.py]
  - [ ] @[backend_v2/hooks/scoring/matrix_hook.py]
  - [ ] @[backend_v2/services/matrix_domain_parser.py]
  - [ ] @[backend_v2/services/export_service.py]
  - [ ] @[backend_v2/services/export_evidence_formatter.py]
  - [ ] @[backend_v2/services/report_service.py]
  - [ ] @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/models/prompts/execution/matrix_evaluation.py]
  - [ ] @[backend_v2/models/prompts/execution/field_prompts.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/atom_extraction.py]
  - [ ] @[backend_v2/scripts/generate_openapi.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
  - [ ] @[backend_v2/services/sdui/sdui_mapper_service.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_distiller.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_explanation_service.py]
  - [ ] @[backend_v2/services/orchestrator/state_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/engines/tda_engine.py]
  - [ ] @[backend_v2/services/studio/simulation_service.py]
  - [ ] @[backend_v2/llm/mock_data.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
  - [ ] @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_158_tracker.md] @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[ki_structured_forensic_quotes.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_structured_forensic_quotes.md]`: Multi-segment coordinate normalization, forward-scan search, monotonic ordering ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$), single-document buffer boundary isolation, and immutable `source_quotes: tuple[str, ...] | None` DTO contract.
     - `@[ki_topological_engine.md]`: Bounded deliverable root axiom injection ($K_{axiom}^{max} = 8$ axioms where $InDegree(v)=0$), dynamic quota allocation ($W_{min} = 12, M_{win} \le 20$), and Algorithm 1 dual fault attribution separating warrant grounding failures.
     - `@[ki_unified_matrix_scoring_strictness.md]`: Decoupled lexical strictness SSOT (`Workflow.default_lexical_strictness_level`), continuous Studio slider, and Gate 5 Snowball morphological calibration.
     - `@[ki_prompt_orchestration_and_matrix_evaluation.md]`: Evidence extraction prompt directives for ordered 1–3 non-contiguous sentence tuples with strict anti-chimera validation.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register new integration test suite `backend_v2/tests/integration/test_multi_segment_causal_e2e.py` and modernized DTOs.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (`01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, `04_server_driven_ui_and_presentation.md`) describing multi-segment evidence and decoupled lexical strictness in present tense without historical language or Epic IDs.
  4. **Scientific Manuscript Sync:**
     - Synchronize `@[docs/tiede.md]` with formal definitions, theorems, proofs, and empirical ablation tables ($N=220, \text{Specificity}_{lex} = 1.000$).

### Final Epic Audit
- [ ] Verification audit executed: `/tier8-audit-epic @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] All 100 target files confirmed verified on physical disk.
- [ ] All 7 line bounds confirmed respected without lossy compression.
- [ ] Zero AST warnings or typing errors reported by quality gate audit scripts.

## Instructions for the Execution Agent
1. **Stateless Reset**: Begin every phase by physically reading `@[.agents/rules/00-antigravity-core.md]` and domain rule files before any execution logic.
2. **Mandatory Workflow Loop**: The mandatory workflow loop is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
3. **Sequential Phase Gates**: Execute phases in strict numerical order (Phase 1 through Phase 8). Never start Phase N+1 until Phase N has passed its audit gate.
4. **Execution Mode**: Supports both Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto` or explicit continuous mandate; progresses autonomously across steps as long as quality gates pass 100%, and triggers clean session handover when the context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified files).
5. **Session Handover Update**: You MUST update the `/tier5-resume` or `/tier0-research-plan` (or `/tier8-audit-plan` if audit pending) command at the bottom of this tracker before handing over the session. Whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue.
6. **Post-Implementation Progression**: Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> parameterized `/tier7-describe-architecture` (with target KIs and directives) -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.
7. **Atomic Commits & Fail-Fast**: After completing each cohesive logical step or passing audit gates, instruct atomic `git commit` with English conventional commit messages. If any test fails or validation crashes, halt immediately and diagnose root cause without duct-tape bypasses.
8. **Preserve Prompts**: Never modify qualitative natural-language prompt texts or persona instructions in `seed_data.json` without explicit authorization.

## Requirements Traceability Matrix

| Requirement ID | Description | Implementation Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-158-001** | Eliminate duplicate Epic file to maintain single SSOT | Phase 1, Step 1 | IMPLEMENTED |
| **REQ-158-002** | Establish canonical `coerce_source_quotes_tuple` SSOT pre-validator | Phase 1, Step 1 | IMPLEMENTED |
| **REQ-158-003** | Eradicate anonymous 3-tuples via `GateMatchResultDTO` contract | Phase 1, Step 2 | IMPLEMENTED |
| **REQ-158-004** | Remediate asymmetric quote extraction in `AnchorValidationService` | Phase 1, Step 3 | IMPLEMENTED |
| **REQ-158-005** | Eliminate mutating text truncation in `ExtractiveSensorService` | Phase 1, Step 4 | IMPLEMENTED |
| **REQ-158-006** | Replace unannotated lambda dictionary factories in `SlidingWindowLinker` | Phase 1, Step 4 | IMPLEMENTED |
| **REQ-158-007** | Lock export evidence formatter signature to strict immutable tuple | Phase 1, Step 5 | IMPLEMENTED |
| **REQ-158-008** | Remediate scalar quote access in `PrintableSourcesAdapter` | Phase 1, Step 5 | IMPLEMENTED |
| **REQ-158-009** | Enforce Flutter Theme Sovereignty in override dialog and modals | Phase 1, Step 6 | IMPLEMENTED |
| **REQ-158-010** | Implement multi-segment foundation unit test suite | Phase 1, Step 7 | IMPLEMENTED |
| **REQ-158-011** | Modernize Pydantic V2 domain models and DTOs to multi-segment tuple schema | Phase 2, Step 1 | IMPLEMENTED |
| **REQ-158-012** | Refactor 1-hop caller orchestration, state reducer, and hook services | Phase 2, Step 2 | IMPLEMENTED |
| **REQ-158-013** | Update atom extraction prompts, system instructions, and schema descriptions | Phase 2, Step 3 | IMPLEMENTED |
| **REQ-158-014** | Synchronize Flutter Freezed DTO contracts and client citation widgets | Phase 2, Step 4 | IMPLEMENTED |
| **REQ-158-015** | Synchronize test fixtures, factories, golden master files, and unit tests | Phase 2, Step 5 | IMPLEMENTED |
| **REQ-158-016** | Enhance coordinate normalization and strict matching for multi-segment tuples | Phase 3, Step 1 | IMPLEMENTED |
| **REQ-158-017** | Implement forward-scan search, monotonic ordering, and single-document buffer isolation | Phase 3, Step 2 | IMPLEMENTED |
| **REQ-158-018** | Update prompt extraction mandate in `matrix_evaluation.py` for 1–3 non-contiguous sentences | Phase 3, Step 3 | IMPLEMENTED |
| **REQ-158-019** | Expand ISTQB boundary and negative test suite in `test_anchor_validation_service.py` | Phase 3, Step 4 | IMPLEMENTED |
| **REQ-158-020** | Add `default_lexical_strictness_level` to `Workflow` model and Studio DTOs | Phase 4, Step 1 | IMPLEMENTED |
| **REQ-158-021** | Update Studio workflow CRUD service to transit decoupled lexical strictness | Phase 4, Step 2 | IMPLEMENTED |
| **REQ-158-022** | Synchronize database seed vault workflows and add localization strings | Phase 4, Step 3 | IMPLEMENTED |
| **REQ-158-023** | Calibrate settings lexical threshold resolution function | Phase 4, Step 4 | IMPLEMENTED |
| **REQ-158-024** | Transit decoupled lexical strictness in execution worker and DAG executor | Phase 4, Step 5 | IMPLEMENTED |
| **REQ-158-025** | Expand worker and anchor validation test suites verifying morphological calibration | Phase 4, Step 6 | IMPLEMENTED |
| **REQ-158-026** | Configure linker settings and budget capacity limits in `settings.py` | Phase 5, Step 1 | IMPLEMENTED |
| **REQ-158-027** | Implement bounded deliverable root axiom header injection with dynamic quota allocation | Phase 5, Step 2 | IMPLEMENTED |
| **REQ-158-028** | Support multi-segment Toulmin warrants in causal edge records | Phase 5, Step 3 | IMPLEMENTED |
| **REQ-158-029** | Implement Algorithm 1 dual fault attribution separating warrant grounding failures | Phase 5, Step 4 | IMPLEMENTED |
| **REQ-158-030** | Expand causal linker and cohesion scoring test suites | Phase 5, Step 5 | IMPLEMENTED |
| **REQ-158-031** | Synchronize tabular export streaming services for CSV and Excel formats | Phase 6, Step 1 | IMPLEMENTED |
| **REQ-158-032** | Update SDUI highlights and printable sources adapters | Phase 6, Step 2 | IMPLEMENTED |
| **REQ-158-033** | Remediate Jinja2 PDF template evidence quote emission | Phase 6, Step 3 | IMPLEMENTED |
| **REQ-158-034** | Regenerate OpenAPI specification artifact reflecting schema updates | Phase 6, Step 4 | IMPLEMENTED |
| **REQ-158-035** | Implement Studio continuous slider for lexical verification strictness | Phase 6, Step 5 | IMPLEMENTED |
| **REQ-158-036** | Update client citation and causal inspector widgets | Phase 6, Step 6 | IMPLEMENTED |
| **REQ-158-037** | Execute presentation and Flutter client audit gates | Phase 6, Step 7 | IMPLEMENTED |
| **REQ-158-038** | Implement end-to-end multi-segment integration test suite | Phase 7, Step 1 | PENDING |
| **REQ-158-039** | Execute offline ablation benchmark ($N=220$) and verify zero chimera leaks | Phase 7, Step 2 | PENDING |
| **REQ-158-040** | Execute full audit gates and mandatory live E2E real LLM test | Phase 7, Step 3 | PENDING |
| **REQ-158-041** | Update directory reference rule with new integration tests and services | Phase 8, Step 1 | PENDING |
| **REQ-158-042** | Synchronize scientific manuscript `docs/tiede.md` with formal definitions and theorems | Phase 8, Step 2 | PENDING |
| **REQ-158-043** | Execute parameterized Tier 7 as-built architecture audit | Phase 8, Step 3 | PENDING |

# Session Handover Context

## Achieved
- Completed Phase 1 Pre-Implementation Technical Debt Cleanups & Foundations across backend and frontend targets.
- Established canonical `coerce_source_quotes_tuple` SSOT in `backend_v2/models/core_base.py`.
- Modernized `QuoteEvidenceDTO` and implemented `GateMatchResultDTO` anti-tuple contract.
- Remediated asymmetric quote extraction and multi-block span matching in `AnchorValidationService`.
- Eliminated mutating text truncation in `ExtractiveSensorService` and unannotated collection factories in `SlidingWindowLinker`.
- Enforced strict tuple type signatures in `ExportEvidenceFormatter`, safe iteration in `PrintableSourcesAdapter`, and Flutter Theme Sovereignty with l10n in touched widgets.
- Implemented and passed all 16 multi-segment foundation tests in `test_multi_segment_quote_foundation.py`.
- Completed Phase 2 Multi-Segment Schema Refactoring across all backend domain models and DAG DTOs (`BooleanEvaluationResult`, `PreFlightResult`, `DraftExtractedAtom`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, `AtomResultDTO`, `HydratedAtomDTO`, `EvaluatedAtomDTO`, `ReducedAtomDTO`, `QuoteEvidenceDTO`, `ScorecardAtomDTO`).
- Synchronized all 1-hop caller orchestration, state reducer, and hook services (`sdui_mapper_service.py`, `causal_cohesion_evaluator.py`, `topological_evaluator.py`, `dag_executor.py`, `causal_discovery_engine.py`, `matrix_hook.py`, `matrix_domain_parser.py`, `report_service.py`, `synthesis_payload_compressor.py`, `matrix_explanation_service.py`, `result_projector.py`, `matrix_reducer.py`, `two_pass_atomizer.py`, `tda_engine.py`, `simulation_service.py`, `export_service.py`, `sliding_window_linker.py`, `anchor_validation_service.py`, `enriched_dag_executor.py`, `llm.py`).
- Synchronized atom extraction prompts and descriptions (`field_prompts.py`, `atom_extraction.py`).
- Synchronized Flutter Freezed contracts (`QuoteEvidenceDto`, `AtomResultDTO`, `CausalNodeDto`, `HydratedAtomDto`, `Workflow`) and citation widgets (`human_override_dialog.dart`, `atom_matrix_table_widget.dart`).
- Synchronized test factories, golden master fixtures, and unit test suites across 20+ test modules with 100% pass rate.
- Passed full strict backend audit loop (`backend_audit_loop.py backend_v2/models/ --test --ast-strict`): 10/10 quality gates passed, 810 unit tests passed, 96.15% TDD line coverage, 0 fatal AST guardrail violations, 0 residual debt ceiling violations, and clean DTO parity.
- Passed full Flutter audit loop (`flutter_audit_loop.py client_app_v2/ --build`) with 0 errors.
- Completed Tier 8 Red-Team Audit for Phase 2 (`red_team_audit_phase2_plan.md`): 100% of requirements REQ-158-011 through REQ-158-015 verified, 0 orphan requirements, 0 fatal AST violations, 0 supply chain violations, and clean full-duplex DTO parity.
- Completed Tier 0 Research & Red-Team analysis for Phase 3 (`03_phase3_plan.md`): hardened plan with 5-column directives table, Pre-Implementation Technical Debt Cleanups (parameter typing, immutable tuple return, explicit magic number constants), candidate $s_1$ anchor iteration, single-document buffer boundary isolation, and comprehensive ISTQB test contracts.
- Completed Phase 3 Lexical Firewall Multi-Segment & Distance Verification implementation across `AnchorValidationService` and `matrix_evaluation.py`:
  - Modernized parameter and return signatures to strict sequences/tuples, eliminating magic numbers with SSOT constants `MAX_CITATION_SPAN_CHARS = 1000`, `MIN_MULTI_SEGMENT_FLOOR_CHARS = 30`, `MIN_ENTROPY_GATE_CHARS = 10`.
  - Implemented candidate $s_1$ anchor iteration and monotonic forward-scan search ($s_k < e_k < s_{k+1}$) in `strict_match`, `_is_lexically_valid`, and `validate_evidence`, enforcing individual segment floor $\ge 30$ chars when $m > 1$ and bounding span $(e_m - s_1) \le 1\,000$ chars.
  - Symmetrically extracted physical source text quotes via `pdf_map` using typed `GateMatchResultDTO` segments, eradicating anonymous primitive tuples per `ban_anonymous_state_tuples` and QGR023.
  - Enforced single-document buffer boundary isolation across `<ai_context_directive>`, `SourceDocumentContext`, and `mcp_source_texts` in `validate_evidence` and `process_atom_evaluation`, eradicating cross-document chimera quotes while preserving immutable quote integrity.
  - Updated `<evidence_extraction_mandate>` in `matrix_evaluation.py` instructing foundational models on 1–3 non-contiguous sentence segments in `source_quotes` with unbroken character substrings, single-document boundaries, and zero banned ambiguities.
  - Expanded ISTQB boundary and negative test suite in `test_anchor_validation_service.py` to 49 test cases covering monotonic order, inverted order failure, distance bounding failure, cross-document chimeras, multi-segment floor, candidate $s_1$ iteration, MCP texts, and branch fallbacks.
  - Passed Universal Quality Gate with strict AST mode (`backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py backend_v2/models/prompts/execution/matrix_evaluation.py --test --ast-strict`): 10/10 quality gates clean, 49 unit tests passed with 93% line coverage on `anchor_validation_service.py` and 100% on `matrix_evaluation.py`, 0 fatal AST guardrail violations, and 0 residual debt ceiling violations.
- Completed Tier 8 Red-Team Audit for Phase 3 (`red_team_audit_phase3_plan.md`): 100% of requirements REQ-158-016 through REQ-158-019 verified on disk, 0 orphan requirements, 0 fatal AST violations, 0 supply chain violations, clean DTO parity, and global backend completion gate passed with 5,616 tests and 97.78% coverage.
- Completed Tier 0 Research & Red-Team analysis for Phase 4 (`04_phase4_plan.md`):
  - Synthesized and injected 5-Column Architectural Directives Table across all 9 target scopes and boundaries into `04_phase4_plan.md`.
  - Audited and locked exact AST line bounds spanning complete `ClassDef` and `FunctionDef` nodes (`workflow.py#L25-L208`, `studio.py#L89-L138`, `studio.py#L579-L608`, `workflow_service.py#L40-L672`, `settings.py#L985-L1006`, `execution_worker.py#L75-L538`, `dag_executor.py#L597-L1794`, `extractive_sensor_service.py#L175-L728`, `anchor_validation_service.py#L25-L836`, and `seed_data.json#L20538-L21331`).
  - Added Step 0 Pre-Implementation Cleanups targeting discovered technical debt: eliminating inline ternary fallback expressions per QGR016, parameterizing hardcoded strictness constants into SSOT thresholds in `settings.py`, and updating Studio DTOs (`WorkflowCreateDTO`, `WorkflowUpdateDTO`) to transit `default_lexical_strictness_level` without loss.
  - Resolved seed vault target discrepancy: verified exactly 3 active workflows in `seed_data.json#L20538-L21331` (`wf_9d68c573802341db`, `wf_a8f1d71000000001`, `wf_b9e2d71000000002`) and targeted them with zero prompt text mutation.
  - Enforced full bidirectional parity (MBD008) ensuring every Column 1 target has a matching action tag in the execution protocol.
  - Added ISTQB boundary value analysis and negative test contracts ($s < 0, s > 100$) and threshold scaling tests in `test_settings_lexical_thresholds.py`, `test_execution_worker.py`, and `test_anchor_validation_service.py`.
  - Passed both `audit_markdown_boundaries.py` and `audit_planner_output.py` with 100% compliance.
- Completed Phase 4 Strictness Decoupling SSOT & Gate 5 Morphological Calibration implementation across domain models, Studio DTOs, Studio services, Seed Vault, settings, execution worker, DAG executor, extractive sensor, and anchor validation:
  - Preserved `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100)] = 50` on `Workflow` domain model and mirrored it across `WorkflowCreateDTO` (`default=50`) and `WorkflowUpdateDTO` (`default=None`) in `studio.py`.
  - Updated Studio `workflow_service.py` to transit `default_lexical_strictness_level` across creation, draft instantiation, cloning, and retrieval pipelines.
  - Synchronized all 3 seeded workflows in `seed_data.json` (`wf_9d68c573802341db`, `wf_a8f1d71000000001`, `wf_b9e2d71000000002`) with `"default_lexical_strictness_level": 50`, strictly respecting the Prompt Preservation Mandate (zero prompt or description changes).
  - Added bilingual localization metadata `"metadata_lexical_strictness"` to both `fi.json` ("Leksikaalinen tiukkuus") and `en.json` ("Lexical Strictness").
  - Calibrated `get_lexical_fuzz_threshold(locale, lexical_strictness_level)` in `settings.py` to compute dynamic calibrated thresholds with tier multipliers (<30: x0.80, >=30: x0.90, >=50: x1.0, >=85: x1.02, >=100: 100.0).
  - Decoupled `AnchorValidationService` in `anchor_validation_service.py` by accepting `lexical_strictness_level: int = 50` in `_is_lexically_valid`, `validate_evidence`, and `process_atom_evaluation`, pruning caller-side duplicate multiplier logic in favor of `get_lexical_fuzz_threshold` and gating Stage 3 Snowball morphological stemming strictly on `lexical_strictness_level < 100`.
  - Transited `lexical_strictness_level` through `execution_worker.py`, `dag_executor.py` (`execute_workflow`, `node_executor.execute`), `StrategyContext`, and `extractive_sensor_service.py` (`_fuzzy_match`, `pre_evaluate`, `_batch_fuzzy_match`, `batch_pre_evaluate`).
  - Added unit tests: `test_execution_worker_transits_decoupled_strictness_parameters` in `test_execution_worker.py`; and `test_strictness_decoupling_high_scoring_allows_morphology`, `test_strictness_decoupling_absolute_lexical_rejects_morphology`, `test_lexical_strictness_bounds_validation_negative`, and `test_get_lexical_fuzz_threshold_strictness_tiers` in `test_anchor_validation_service.py`.
  - Passed Universal Quality Gate (`backend_audit_loop.py` with `--test --ast-strict`) across all touched targets: 10/10 quality gates clean, 53 anchor validation tests passed (93% line coverage), 18 worker tests passed, dry-run seed validation 100% clean, 0 fatal AST guardrails, 0 residual debt ceiling violations, and clean DTO parity.
- Completed Tier 8 Red-Team Audit for Phase 4 (`red_team_audit_phase4_plan.md`):
  - Verified 100% of requirements REQ-158-020 through REQ-158-025 on physical disk with line bounds.
  - Zero orphan requirements, zero AST violations, zero supply chain violations.
  - Clean full-duplex DTO parity (52/52 models).
  - Executed Five-Axis System 2 Adversarial As-Built Evaluation and 5-Column Architectural Verification Table.
- Completed Tier 0 Research & Red-Team analysis for Phase 5 (`05_phase5_plan.md`):
  - Synthesized and injected 5-Column Architectural Directives Table across all 9 target scopes and boundaries into `05_phase5_plan.md`.
  - Audited and verified exact AST line bounds spanning complete `ClassDef` and `FunctionDef` nodes (`settings.py#L54-L972`, `dag_models.py#L30-L69`, `causal_discovery.py#L59-L66`, `sliding_window_linker.py#L48-L61`, `sliding_window_linker.py#L120-L365`, `causal_cohesion_evaluator.py#L79-L290`, `causal_cohesion_evaluator.py#L94-L149`, and `causal_discovery_engine.py#L42-L370`).
  - Added Step 0 Pre-Implementation Cleanups targeting discovered technical debt: eliminating mutable collection default arguments in helper methods, parameterizing hardcoded window limits into SSOT settings (`max_causal_window_atoms: int = 20`, `min_current_window_reserve_atoms: int = 12`, `max_root_axiom_header_atoms: int = 8`), and updating `LinkerEdgeDTO` to support multi-segment warrants without loss.
  - Specified dynamic allocation equation $K_{eff} = \min(K_{max}, \max(0, M_{win} - W_{current}))$ guaranteeing reservation floor $W_{min} = 12$ while capping global window size at $M_{win} \le 20$.
  - Specified candidate root axiom selection: filtered by candidate deliverable document keys, zero in-degree within the deliverable document ($InDegree_{deliv}(v) = 0$), and sorted deterministically by $(-OutDegree(v), atom.source_sequence_index)$.
  - Standardized multi-segment Toulmin warrant transit via immutable `warrant_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple` across `CausalEdge`, `CausalEdgeDTO`, and `LinkerEdgeDTO`.
  - Defined Algorithm 1 dual fault attribution separating intrinsic premise flaws (`NODE_FAILURE`) from inferential warrant flaws (`WARRANT_GROUNDING_FAILURE`).
  - Added comprehensive ISTQB test contracts covering positive, boundary, and negative partitions.
  - Verified `05_phase5_plan.md` passes `audit_markdown_boundaries.py` with 0 errors and all 8 plans pass `audit_planner_output.py` with 116/116 AST bounds verified.
- Completed Phase 5 Execution (`05_phase5_plan.md`):
  - Configured SSOT linker capacity limits in `backend_v2/settings.py` (`linker_max_global_root_axioms: int = 8`, `linker_min_window_atoms_quota: int = 12`).
  - Standardized multi-segment Toulmin inferential warrant transit via typed `warrant_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple` across `CausalEdge`, `CausalEdgeDTO`, and `LinkerEdgeDTO`.
  - Synchronized Flutter Freezed `CausalEdgeDto` with `warrant_quotes` and regenerated Freezed/g.dart models, achieving 100% full-duplex DTO parity (52/52 models).
  - Implemented deliverable root axiom candidate selection and dynamic budget allocation ($W_{min}=12, K_{eff} = \min(8, \max(0, 20 - W_{current}))$) in `SlidingWindowLinker._select_root_axioms` with `RootAxiomRankDTO` deterministic sorting by $(-OutDegree(v), atom.source_sequence_index)$ and $M_{win} \le 20$ hard guard.
  - Implemented `--- GLOBAL CONTEXT ANCHORS (ROOT AXIOMS) ---` header injection and alias registration in `SlidingWindowLinker`.
  - Transited `warrant_quotes=edge.warrant_quotes` and deliverable input keys scoping in `CausalDiscoveryEngine`.
  - Implemented Algorithm 1 dual fault attribution in `CausalCohesionEvaluator.diagnose_root_causes`, distinguishing `WARRANT_GROUNDING_FAILURE` from `NODE_FAILURE` and formatting warrant quote details into diagnostic explanations.
  - Implemented all 7 ISTQB test contracts across `test_sliding_window_linker.py` and `test_causal_cohesion_scoring.py`, and added coverage tests to `test_causal_discovery_engine.py`, achieving 100% pass across 53 unit tests.
  - Passed Universal Quality Gate (`backend_audit_loop.py` with `--test --ast-strict`): 10/10 quality gates clean, strict 90% TDD line coverage across all 6 target modules, 0 fatal AST guardrails, 0 residual debt ceiling violations, and clean imports.
- Completed Tier 8 Red-Team Audit for Phase 5 (`red_team_audit_phase5_plan.md`):
  - Verified 100% of requirements REQ-158-026 through REQ-158-030 on physical disk with exact AST bounds.
  - Zero orphan requirements, zero AST violations, zero supply chain violations.
  - Clean full-duplex DTO parity (52/52 models).
  - Executed Five-Axis System 2 Adversarial As-Built Evaluation and 5-Column Architectural Verification Table.
- Completed Phase 6 Tier 0 Research & Red-Team Audit (`06_phase6_plan.md`):
  - Formulated 5-Column Architectural Directives Table across 14 target scopes and boundaries.
  - Identified 4 pre-implementation technical debt items: raw `TextStyle` instantiation in `sdui_matrix_table_widget.dart#L566`, citation truncation in `printable_sources_adapter.py#L99-L341`, tabular cell shifting delimiter debt in `export_evidence_formatter.py#L46-L77`, and stale test assertions in `test_export_evidence_formatter.py#L69-L78`.
  - Injected Step 0 Pre-Implementation Technical Debt Cleanups and explicit `<action>` tags satisfying MBD008 Table-Protocol Bidirectional Parity.
  - Verified 159 Python AST line bounds against physical codebase, including decorated async functions (`test_pdf_generator.py#L231-L317`).
  - Verified `06_phase6_plan.md` passes `audit_markdown_boundaries.py` with 0 errors and all 8 plans pass `audit_planner_output.py` with 159/159 AST bounds verified.
- Completed Phase 6 Execution: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3):
  - Formatted multi-segment quotes with standardized `" [...] ".join(source_quotes)` in `backend_v2/services/export_evidence_formatter.py` and `backend_v2/services/export_service.py`, preserving rectangular CSV/Excel geometry.
  - Remediated single-segment quote truncation in `backend_v2/services/sdui/adapters/printable_sources_adapter.py` by formatting full multi-segment provenance context using `" [...] ".join(eq.source_quotes)`.
  - Remediated Jinja2 PDF report template (`report_template.jinja2`) at line 478 to render `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, eliminating empty citation omissions.
  - Regenerated `docs/swagger/openapi.json` from authoritative Pydantic V2 schemas via `generate_openapi.py`.
  - Implemented independent continuous slider for lexical verification strictness [0, 100], 4 discrete preset chips (Flexible, Calibrated, Strict, Absolute), and dynamic semantic consequence card in `WorkflowStrictnessTab` with 100% Theme Sovereignty and 1:1 cross-language ARB localization (`app_fi.arb`, `app_en.arb`, `metaLexicalStrictness`).
  - Eradicated raw `TextStyle(...)` instantiation in `sdui_matrix_table_widget.dart` via `Theme.of(context).textTheme.bodySmall?.copyWith(...)`.
  - Synchronized `causal_inspector_modal.dart` and `sdui_matrix_table_widget.dart` to interpolate `node.sourceQuotes?.join(' [...] ')`.
  - Resolved `AppExceptionBoundary` multi-instance `ErrorWidget.builder` race condition using static reference counting.
  - Passed Universal Quality Gate (`backend_audit_loop.py` with `--test --ast-strict`): 10/10 quality gates passed, 97 backend unit tests passed.
  - Passed Flutter audit loop (`flutter_audit_loop.py client_app_v2/ --build`) and 590/590 Flutter tests (`flutter test`).
  - Completed Tier 8 Post-Implementation Red-Team Audit for Phase 6 (`red_team_audit_phase6_plan.md`): 100% of requirements REQ-158-031 through REQ-158-037 verified on physical disk, 0 orphan requirements, 0 fatal AST violations, 0 supply chain violations, clean full-duplex DTO parity, and global backend completion gate passed with 5,635 tests (97.77% coverage).

## Learned
- In `blackboard.py`, `two_pass_atomizer.py`, `report_service.py`, and `sdui_mapper_service.py`, inline ternary expressions (specifically: `' [...] '.join(atom.source_quotes) if atom.source_quotes else ''`) trigger AST Guardrail `QGR016` (banned ternary lazy fallback). Replacing them with explicit `if/elif/else` blocks satisfies `QGR016` deterministically.
- `audit_dto_parity.py` compares `WorkflowResponseDTO` with `Workflow` in `workflow.dart`. When `default_lexical_strictness_level` is present on Flutter's `Workflow`, backend `Workflow` must define `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100)] = 50` to maintain full-duplex DTO parity.
- In `ExtractedAtom`, `validate_logical_deduction_and_quote` requires that `source_quotes` is mandatory unless `is_logical_deduction` or `is_inverse` is True. Unit tests verifying early exit for empty quotes must set `is_logical_deduction=True` when `source_quotes=None`.
- In `AnchorValidationService`, when $q_1$ repeats earlier in a document preamble, greedy single-pass forward-scan causes false rejection of valid evidence downstream. Implementing candidate $s_1$ anchor iteration ensures that subsequent occurrences of $q_1$ are evaluated within the $[s_1, s_1 + 1\,000]$ window.
- In `AnchorValidationService.process_atom_evaluation`, independent per-segment document matching creates cross-document chimera vulnerabilities where segment 1 matches document A and segment 2 matches document B. Multi-segment citations must be validated cohesively against each candidate document context, requiring all segments to resolve monotonically within the same single source document buffer.
- `audit_markdown_boundaries.py` enforces AST bound matching via `ast.walk()` exclusively for `FunctionDef`, `AsyncFunctionDef`, and `ClassDef` nodes. For decorated functions (e.g. `@pytest.mark.asyncio`), the AST span start line is the first decorator line (`min(d.lineno for d in node.decorator_list)`), not the `def` keyword line.
- In `scripts/_ast_guardrails.py`, `QGR023` flags any `tuple[int, int]` type annotation as an anonymous state tuple. Encapsulating segment boundaries inside `GateMatchResultDTO` replaces primitive coordinates with named properties (`start_idx`, `end_idx`), fulfilling `ban_anonymous_state_tuples` and passing `QGR023`.
- `audit_warning_baseline.py` enforces a monotonic ratchet of 0 for Census T (`type-ignore` annotations in `backend_v2/tests`). Writing `# type: ignore` in test files causes Gate 9 failure; tests must use typed signatures without inline suppressions.
- Natural-language prompt constants in `backend_v2/models/prompts/` (specifically: `matrix_evaluation.py`) can exceed 120 characters per line. Adding these modules to `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml` ensures alignment between isolated docstring checks and global lint passes.
- In `seed_data.json`, lines 20538-21331 contain exactly 3 active workflow objects (`wf_9d68c573802341db`, `wf_a8f1d71000000001`, `wf_b9e2d71000000002`). Updating seed documentation to reference these 3 explicit IDs instead of an ambiguous "8 workflows" eliminates domain guessing while respecting the Prompt Preservation Mandate.
- In `backend_v2/settings.py`, `get_lexical_fuzz_threshold(locale, lexical_strictness_level)` is the sole mathematical SSOT for lexical verification thresholds (Free 70%, Normal 82%, Strict 88%, Zero-Trust 95%). Gate 5 Snowball stemming enablement is strictly controlled by `lexical_strictness_level < 85`, fully decoupled from scoring dampening exponent $\zeta_{score}$.
- `WorkflowCreateDTO` and `WorkflowUpdateDTO` in `backend_v2/models/dtos/studio.py` lacked `default_lexical_strictness_level`, which would cause Studio workflow updates to drop the setting on roundtrip. Extending both DTOs with `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100)] = 50` guarantees full-duplex CRUD parity.
- Conflating scoring dampening exponent $\zeta_{score}$ with lexical matching threshold $\zeta_{lex}$ artificially blocked Snowball morphological stemming when scoring strictness was high ($\zeta_{score} = 85$). Decoupling `lexical_strictness_level` allows high cognitive dampening while still permitting authentic Finnish grammatical case inflections at normal lexical strictness ($\zeta_{lex} = 50$).
- Without root axiom pinning, extended documents ($N \in [141, 252]$) suffer from sliding-window horizon truncation where introductory axioms lack local descendants within their initial window ($M_{win} \le 20$), inflating isolated claim ratios $r_{\text{iso}}$. Prepended Global Context Anchor headers bounded by $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$ eliminate this truncation while guaranteeing current window reservations ($W_{min} = 12$).
- `CausalEdge` in `dag_models.py` and `CausalEdgeDTO` in `causal_discovery.py` enforce `ConfigDict(extra="forbid", strict=True, frozen=True)`. Attempting to instantiate them with `warrant_quotes` without first updating their schema triggers immediate validation failure. They must be updated synchronously in Step 2.
- In Algorithm 1, when an upstream premise evaluates cleanly (`status == PASSED`) but the dependent child fails, the fault is attributed to `CausalRootCauseType.WARRANT_GROUNDING_FAILURE` rather than `NODE_FAILURE`, preventing unfair double-penalization of authors for valid premise assertions.
- In `sliding_window_linker.py`, AST guardrail `QGR023` (anonymous primitive tuple ban) flags `sort_key: tuple[int, int]`. Encapsulating ranking coordinates into an immutable `RootAxiomRankDTO` with `__lt__` comparison eliminates anonymous tuples while enforcing strict Pydantic V2 contracts.
- In `causal_cohesion_evaluator.py` and `causal_discovery_engine.py`, inline ternary expressions on dictionary lookups and argument passing trigger AST Guardrail `QGR016`. Replacing them with procedural `if/else` assignments guarantees fail-safe compliance.
- When extending `CausalEdgeDTO` in `causal_discovery.py`, `audit_dto_parity.py` validates 1:1 alignment with Flutter's `CausalEdgeDto`. Synchronously adding `@JsonKey(name: 'warrant_quotes') List<String>? warrantQuotes` to `causal_discovery_dto.dart` and running `flutter_audit_loop.py --build` satisfies Full-Duplex Serialization Parity.
- In `test_sliding_window_linker.py`, `ExtractedAtom.tda_id` enforces regex pattern `^tda_[a-fA-F0-9]{8,32}$`. Test fixture identifiers must use hexadecimal encoding (`f"tda_{i:08x}"`) rather than arbitrary string suffixes.
- `StrategyContext` enforces `ConfigDict(frozen=True)`. Tests configuring `expected_inputs` must inject them during construction via `create_engine_request` rather than mutating `request.context` post-instantiation.
- In `client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L566`, a raw `TextStyle(...)` instantiation violates `flutter_theme_sovereignty_mandate`. It must be refactored to `Theme.of(context).textTheme.bodySmall?.copyWith(...)`.
- In `backend_v2/services/export_evidence_formatter.py#L46-L77`, formatting multiple quotes with numbered newlines (`[1] ...\n[2] ...`) deforms rectangular Excel/CSV cells and causes column shifting. Standardizing to `" [...] ".join(cleaned_items)` preserves clean rectangular grid geometry.
- In `backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341`, taking `matched_quotes[0]` causes citation truncation for multi-segment quotes. Formatting multi-segment citations using `" [...] ".join(eq.source_quotes)` preserves complete forensic provenance.
- In `AppExceptionBoundary`, mounting multiple instances simultaneously in `SduiBlocksRenderer` causes an `ErrorWidget.builder` LIFO/FIFO inversion race condition on widget teardown. Adding static reference counting (`_boundaryCount`) ensures only the outermost root boundary captures and restores `_rootOriginalErrorBuilder`, preventing framework teardown assertions from failing.

## Remaining
- Research and execute Phase 7: Empirical Offline Benchmark & Regression Gate (WP4) via `/tier0-research-plan @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`.
- Research and execute Phase 8: As-Built Architectural Documentation & Scientific Manuscript Synchronization (`@[docs/tiede.md]`).

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]
```




