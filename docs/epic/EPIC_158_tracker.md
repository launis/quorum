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
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 3.0: Strategic alignment check and baseline verification
  - [ ] Step 3.1: Enhance coordinate normalization and strict matching for multi-segment tuples
  - [ ] Step 3.2: Implement forward-scan search, monotonic ordering, and single-document buffer isolation in `AnchorValidationService`
  - [ ] Step 3.3: Update prompt extraction mandate in `matrix_evaluation.py` for 1–3 non-contiguous sentences
  - [ ] Step 3.4: Expand ISTQB boundary and negative test suite in `test_anchor_validation_service.py`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)
- **Plan:** @[docs/epic/tasks_EPIC_158/04_phase4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 4.0: Strategic alignment check and baseline verification
  - [ ] Step 4.1: Add `default_lexical_strictness_level` to `Workflow` domain model and Studio DTOs
  - [ ] Step 4.2: Update Studio workflow CRUD service to transit decoupled lexical strictness
  - [ ] Step 4.3: Synchronize database seed vault workflows and add localization strings
  - [ ] Step 4.4: Calibrate settings lexical threshold resolution function
  - [ ] Step 4.5: Transit decoupled lexical strictness in execution worker and DAG executor
  - [ ] Step 4.6: Expand worker and anchor validation test suites verifying morphological calibration
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)
- **Plan:** @[docs/epic/tasks_EPIC_158/05_phase5_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 5.0: Strategic alignment check and baseline verification
  - [ ] Step 5.1: Configure linker settings and budget capacity limits in `settings.py`
  - [ ] Step 5.2: Implement bounded deliverable root axiom header injection with dynamic quota allocation in `SlidingWindowLinker`
  - [ ] Step 5.3: Support multi-segment Toulmin warrants in causal edge records
  - [ ] Step 5.4: Implement Algorithm 1 dual fault attribution separating warrant grounding failures
  - [ ] Step 5.5: Expand causal linker and cohesion scoring test suites
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)
- **Plan:** @[docs/epic/tasks_EPIC_158/06_phase6_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 6.0: Strategic alignment check and baseline verification
  - [ ] Step 6.1: Synchronize tabular export streaming services for CSV and Excel formats
  - [ ] Step 6.2: Update SDUI highlights and printable sources adapters
  - [ ] Step 6.3: Remediate Jinja2 PDF template evidence quote emission
  - [ ] Step 6.4: Regenerate OpenAPI specification artifact reflecting schema updates
  - [ ] Step 6.5: Implement Studio continuous slider for lexical verification strictness
  - [ ] Step 6.6: Update client citation and causal inspector widgets
  - [ ] Step 6.7: Execute presentation and Flutter client audit gates
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`

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
| **REQ-158-016** | Enhance coordinate normalization and strict matching for multi-segment tuples | Phase 3, Step 1 | PENDING |
| **REQ-158-017** | Implement forward-scan search, monotonic ordering, and single-document buffer isolation | Phase 3, Step 2 | PENDING |
| **REQ-158-018** | Update prompt extraction mandate in `matrix_evaluation.py` for 1–3 non-contiguous sentences | Phase 3, Step 3 | PENDING |
| **REQ-158-019** | Expand ISTQB boundary and negative test suite in `test_anchor_validation_service.py` | Phase 3, Step 4 | PENDING |
| **REQ-158-020** | Add `default_lexical_strictness_level` to `Workflow` model and Studio DTOs | Phase 4, Step 1 | PENDING |
| **REQ-158-021** | Update Studio workflow CRUD service to transit decoupled lexical strictness | Phase 4, Step 2 | PENDING |
| **REQ-158-022** | Synchronize database seed vault workflows and add localization strings | Phase 4, Step 3 | PENDING |
| **REQ-158-023** | Calibrate settings lexical threshold resolution function | Phase 4, Step 4 | PENDING |
| **REQ-158-024** | Transit decoupled lexical strictness in execution worker and DAG executor | Phase 4, Step 5 | PENDING |
| **REQ-158-025** | Expand worker and anchor validation test suites verifying morphological calibration | Phase 4, Step 6 | PENDING |
| **REQ-158-026** | Configure linker settings and budget capacity limits in `settings.py` | Phase 5, Step 1 | PENDING |
| **REQ-158-027** | Implement bounded deliverable root axiom header injection with dynamic quota allocation | Phase 5, Step 2 | PENDING |
| **REQ-158-028** | Support multi-segment Toulmin warrants in causal edge records | Phase 5, Step 3 | PENDING |
| **REQ-158-029** | Implement Algorithm 1 dual fault attribution separating warrant grounding failures | Phase 5, Step 4 | PENDING |
| **REQ-158-030** | Expand causal linker and cohesion scoring test suites | Phase 5, Step 5 | PENDING |
| **REQ-158-031** | Synchronize tabular export streaming services for CSV and Excel formats | Phase 6, Step 1 | PENDING |
| **REQ-158-032** | Update SDUI highlights and printable sources adapters | Phase 6, Step 2 | PENDING |
| **REQ-158-033** | Remediate Jinja2 PDF template evidence quote emission | Phase 6, Step 3 | PENDING |
| **REQ-158-034** | Regenerate OpenAPI specification artifact reflecting schema updates | Phase 6, Step 4 | PENDING |
| **REQ-158-035** | Implement Studio continuous slider for lexical verification strictness | Phase 6, Step 5 | PENDING |
| **REQ-158-036** | Update client citation and causal inspector widgets | Phase 6, Step 6 | PENDING |
| **REQ-158-037** | Execute presentation and Flutter client audit gates | Phase 6, Step 7 | PENDING |
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

## Learned
- In `blackboard.py`, `two_pass_atomizer.py`, `report_service.py`, and `sdui_mapper_service.py`, inline ternary expressions like `' [...] '.join(atom.source_quotes) if atom.source_quotes else ''` trigger AST Guardrail `QGR016` (banned ternary lazy fallback). Replacing them with explicit `if/elif/else` blocks satisfies `QGR016` deterministically.
- `audit_dto_parity.py` compares `WorkflowResponseDTO` with `Workflow` in `workflow.dart`. When `default_lexical_strictness_level` is present on Flutter's `Workflow`, backend `Workflow` must define `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100)] = 50` to maintain full-duplex DTO parity.
- In `ExtractedAtom`, `validate_logical_deduction_and_quote` requires that `source_quotes` is mandatory unless `is_logical_deduction` or `is_inverse` is True. Unit tests verifying early exit for empty quotes must set `is_logical_deduction=True` when `source_quotes=None`.

## Remaining
- Proceed through Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2).

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]
```
