<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# EPIC 161 Tracker: Topological Intelligence Preservation Across Distillation, Synthesis & SDUI Reporting

- **Epic:** @[docs/epic/EPIC_161_topological_synthesis_cohesion.md]
- **Task Directory:** @[docs/epic/tasks_EPIC_161/]

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation
**Plan:** @[docs/epic/tasks_EPIC_161/01_phase1_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_161/01_phase1_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md]`
  - [ ] Step 1.1: Scoped Boy Scout Technical Debt Cleanups & Toulmin Falsification Wiring
  - [ ] Step 1.2: DTO & Schema Enrichment (Full-Duplex Serialization Parity)
  - [ ] Step 1.3: Asymmetric Epistemic Distillation, Micro-CoT Tail Preservation & Topological Deficit Stratification
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md]`

### Phase 2: Orchestration, Frontier Contrastive Deficit Injection & Synthesis Convergence
**Plan:** @[docs/epic/tasks_EPIC_161/02_phase2_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_161/02_phase2_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_161/02_phase2_plan.md] @[docs/epic/EPIC_161_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/02_phase2_plan.md] @[docs/epic/EPIC_161_tracker.md]`
  - [ ] Step 2.1: Frontier Contrastive Deficit Injection & Transitive N_A Parent Hydration (MatrixExplanationService)
  - [ ] Step 2.2: Phase 1 In-DAG SynthesisEngine Convergence
  - [ ] Step 2.3: Phase 2 Unified CausalSynthesisBriefDTO Fan-Out
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_161/02_phase2_plan.md] @[docs/epic/EPIC_161_tracker.md]`

### Phase 3: Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization
**Plan:** @[docs/epic/tasks_EPIC_161/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_161/03_phase3_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_161/03_phase3_plan.md] @[docs/epic/EPIC_161_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/03_phase3_plan.md] @[docs/epic/EPIC_161_tracker.md]`
  - [ ] Step 3.1: Inline Topological & Short-Circuit Lineage in SDUI Blocks & Report DTOs
  - [ ] Step 3.2: Jinja2 PDF Template & PDF Generator Parity
  - [ ] Step 3.3: Flutter Freezed SDUI DTO & Widget Synchronization
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_161/03_phase3_plan.md] @[docs/epic/EPIC_161_tracker.md]`

### Phase 4: Verification & E2E Integration Gate
**Plan:** @[docs/epic/tasks_EPIC_161/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_161/04_phase4_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_161/04_phase4_plan.md] @[docs/epic/EPIC_161_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/04_phase4_plan.md] @[docs/epic/EPIC_161_tracker.md]`
  - [ ] Step 4.1: Cross-Domain SDUI Semantic Parity & Heterogeneous Payload Verification
  - [ ] Step 4.2: AST Guardrail & Touched-Scope Technical Debt Verification
  - [ ] Step 4.3: Mandatory Live E2E REST API Verification Gate
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_161/04_phase4_plan.md] @[docs/epic/EPIC_161_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend Integration Suite**: Run `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py backend_v2/tests/unit/scripts/test_ast_guardrails.py`
- [ ] **[NOK] Frontend Compilation & Build Runner Gate**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify zero skipped (`@pytest.mark.skip`) or commented-out tests exist across modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Verify zero raw `if type(content) is dict:` checks in `blueprint.py` and zero bare claim-title deficit truncations remain across the codebase (`scripts/audit_epic_coverage.py --epic docs/epic/EPIC_161_topological_synthesis_cohesion.md`).
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_161_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"`
  - [ ] @[backend_v2/database/postgres/graph_adapter.py]
  - [ ] @[backend_v2/models/domain/proposition_graph.py]
  - [ ] @[backend_v2/models/domain/synthesis.py]
  - [ ] @[backend_v2/models/dtos/atom_evaluation.py]
  - [ ] @[backend_v2/models/dtos/causal_discovery.py]
  - [ ] @[backend_v2/models/dtos/lightweight_matrix.py]
  - [ ] @[backend_v2/models/dtos/report_data.py]
  - [ ] @[backend_v2/models/dtos/synthesis.py]
  - [ ] @[backend_v2/models/prompts/synthesis/synthesis_directives.py]
  - [ ] @[backend_v2/models/view/sdui.py]
  - [ ] @[backend_v2/services/blueprint.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]
  - [ ] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_explanation_service.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [ ] @[backend_v2/services/pdf_generator.py]
  - [ ] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]
  - [ ] @[backend_v2/services/sdui/sdui_mapper_service.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/workers/synthesis_tasks.py]
  - [ ] @[backend_v2/workers/synthesis_worker.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_161_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`
  - [ ] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/shared/models/sdui_block_dto.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify zero orphaned references to demolished patterns exist across the codebase.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for all modified orchestrator, synthesis worker, and SDUI service modules.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_161_tracker.md] @[docs/epic/EPIC_161_topological_synthesis_cohesion.md] @[ki_god_code_prevention.md] @[ki_sdui_matrix_synthesis.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_sdui_matrix_synthesis.md]`: Document the 5-Pillar Asymmetric Epistemic Distillation Architecture (`1500`-char `max_synthesis_reasoning_length` preserving `step_3_evaluate_anti_patterns` and `step_4_final_conclusion` of `ReasoningStepDTO`, zero-loss retention of `ExecutionStatus.FAILED`, `ExecutionStatus.N_A`, and `is_inverse_evidence` evaluations, topological deficit priority sorting by `(-int(is_inverse_evidence), -topological_out_degree, len(short_circuit_reason_tda_ids), atom_id)`, [NEW] `MatrixFailureDeficitDTO` defined in `@[backend_v2/models/dtos/synthesis.py]` with transitive parent-to-child `N_A` short-circuit hydration and developmental frontier $S+1$ `ContrastivePairDTO` injection capped at `MAX_CONTRASTIVE_DEFICITS_PER_ROW = 3`, Phase 1 `SynthesisEngine` injection of `matrix_reducer_output.reduced_atoms`, Phase 2 4-task fan-out of [NEW] `CausalSynthesisBriefDTO` defined in `@[backend_v2/models/dtos/synthesis.py]` combining `CausalRootCauseDiagnosisDTO` and `FalsifiedClaimMatch`, and inline SDUI rendering of `short_circuited_by_claims` and `falsified_warrant_claims`).
     - `@[ki_god_code_prevention.md]`: Document strict `StepOutputDTO` and `TypeAdapter` envelope projection in `blueprint.py` replacing raw `if type(content) is dict:` inspection.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` reflects `MatrixFailureDeficitDTO` and `CausalSynthesisBriefDTO` under `backend_v2/models/dtos/synthesis.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless architectural narratives in `docs/architecture/` describing asymmetric epistemic distillation, frontier contrastive anchoring, 3-way Toulmin falsification fan-out, and inline SDUI topological lineage in present tense with zero historical progressions or Epic IDs.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_161_topological_synthesis_cohesion.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
1. **Execution Protocol**: Execute sequentially through Phases 1 to 4. Each phase follows the mandatory workflow loop: `/tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
2. **Atomic Commits**: After completing each cohesive logical step and verifying tests with `uv run python scripts/backend_audit_loop.py` or `uv run python scripts/flutter_audit_loop.py`, commit changes using conventional commits format (`feat(synthesis): ...`, `fix(sdui): ...`).
3. **Execution Mode**: Supports both Step-by-Step and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto` or via `scripts/auto_phase_runner.py`). Progresses autonomously across steps while quality gates pass 100%, and triggers clean session handover when the context budget limit is reached (>8 turns, 3 atomic commits, or >5 modified files).
4. **Post-Implementation Gates**: Once all 4 Phases are complete, the loop MUST continue through the Post-Implementation Gates: `auto_hardening_runner.py --gate all` -> parameterized `/tier7-describe-architecture` -> `/tier8-audit-epic`.

## Requirements Traceability Matrix

| Requirement ID | Technical Requirement Description | Implementation Phase & Step | Verification & Acceptance Gate |
| :--- | :--- | :--- | :--- |
| **REQ-161-001** | Eradicate raw `if type(content) is dict:` loop in `blueprint.py#L127-L698` in favor of strict `StepOutputDTO` / `TypeAdapter` validation, and wire `CteReasoningStrategy.find_falsified_claims` (`graph_adapter.py#L347-L431`) returning `list[FalsifiedClaimMatch]` (`proposition_graph.py#L343-L391`) into `causal_tda_fusion.py#L392-L465` and `step_execution_stage.py#L211-L363`. | Phase 1, Step 1.1 | `backend_audit_loop.py` on `blueprint.py` and `causal_tda_fusion.py` passes with 0 AST or test violations. |
| **REQ-161-002** | Enrich `DistilledEvaluation` (`synthesis.py#L131-L155`), `ReducedAtomDTO` (`atom_evaluation.py#L43-L67`), `CausalRootCauseDiagnosisDTO`, and `CausalTdaFusionResultDTO` (`causal_discovery.py`) with topological lineage, human-readable claim texts, warrant relations, and `falsified_claims` under `ConfigDict(strict=True, extra="forbid", frozen=True)`. | Phase 1, Step 1.2 | `test_causal_tda_fusion_unit.py` and `test_causal_tda_fusion.py` pass with 100% Full-Duplex Serialization Parity. |
| **REQ-161-003** | Raise `max_synthesis_reasoning_length` from `300` to `1500` in `settings.py`, retain all `FAILED`, `N_A`, and `is_inverse_evidence` evaluations in `_clean_and_distill_payload` (`synthesis_payload_compressor.py#L182-L393`), and sort `deficits` by `(-int(item.is_inverse_evidence), -item.topological_out_degree, len(item.short_circuit_reason_tda_ids), atom_id)` at `synthesis_payload_compressor.py#L135-L140`. | Phase 1, Step 1.3 | `test_synthesis_payload_compressor.py` passes ISTQB BVA and topological priority sorting assertions. |
| **REQ-161-004** | Define [NEW] `MatrixFailureDeficitDTO` in `models/dtos/synthesis.py` and upgrade `MatrixExplanationService.assemble_matrices_to_explain` (`matrix_explanation_service.py#L56-L311`) with transitive parent-to-child `N_A` blocker reasoning hydration and frontier $S+1$ `ContrastivePairDTO` injection (`MAX_CONTRASTIVE_DEFICITS_PER_ROW = 3`). | Phase 2, Step 2.1 | `test_matrix_explanation_service.py` passes frontier $S+1$ and transitive `N_A` hydration unit tests. |
| **REQ-161-005** | Inject `matrix_reducer_output.reduced_atoms` (aliased via `AliasEngine`) into `SynthesisEngine.execute()` (`synthesis_engine.py#L58-L301`) alongside `raw_extensions` and `global_atom_blackboard`. | Phase 2, Step 2.2 | `test_synthesis_engine.py` asserts aliased `reduced_atoms` failure reasoning in compiled prompt payload. |
| **REQ-161-006** | Define [NEW] `CausalSynthesisBriefDTO` in `models/dtos/synthesis.py`, add `<causal_tda_diagnosis_mandate>` and `<contrastive_frontier_mandate>` in `synthesis_directives.py`, and fan out `CausalSynthesisBriefDTO` across all four tasks in `synthesis_worker.py#L92-L664` and `synthesis_tasks.py`. | Phase 2, Step 2.3 | `test_synthesis_worker.py` verifies all 4 synthesis tasks receive `CausalSynthesisBriefDTO` in their tail user payload. |
| **REQ-161-007** | Bind `short_circuited_by_claims` and `falsified_warrant_claims` onto matrix rows and causal graph nodes in `report_data.py`, `models/view/sdui.py`, `matrix_summary_table_adapter.py`, `causal_graph_adapter.py#L32-L185`, and `sdui_mapper_service.py#L91-L167`. | Phase 3, Step 3.1 | `test_sdui_mapper_service.py` asserts inline topological lineage without bottom-of-report `SduiNACard` orphans. |
| **REQ-161-008** | Render inline `short_circuited_by_claims` blocker badges and `falsified_warrant_claims` Toulmin rebuttal links in `report_template.jinja2` and `pdf_generator.py`. | Phase 3, Step 3.2 | `backend_audit_loop.py` on `pdf_generator.py` passes. |
| **REQ-161-009** | Synchronize Freezed models (`sdui_block_dto.dart`, `causal_discovery_dto.dart`) and SDUI widgets (`sdui_matrix_table_widget.dart`, `sdui_causal_graph_widget.dart`) with 1:1 Backend DTO parity and Theme Sovereignty compliance. | Phase 3, Step 3.3 | `flutter_audit_loop.py client_app_v2/ --build` and `audit_flutter_theme_sovereignty.py` pass with 0 violations. |
| **REQ-161-010** | Verify 1:1 Cross-Domain SDUI Semantic Parity across Python SDUI DTOs, Jinja2 PDF templates, and Dart Freezed models in `test_sdui_semantic_parity.py`. | Phase 4, Step 4.1 | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` passes 100%. |
| **REQ-161-011** | Verify AST guardrail enforcement in `test_ast_guardrails.py` and 0 technical debt findings across touched scope and 1-hop callers via `audit_technical_debt.py`. | Phase 4, Step 4.2 | `test_ast_guardrails.py` and `audit_technical_debt.py --include-one-hop` pass with 0 findings. |
| **REQ-161-012** | Execute global backend and Flutter audit loops and mandatory live E2E REST API verification gate in `test_integration_real_llm.py`. | Phase 4, Step 4.3 | `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` passes 100%. |

# Session Handover Context

## Achieved
- Completed Tier 1 Epic Planning (`/tier1-planner @[docs/epic/EPIC_161_topological_synthesis_cohesion.md]`):
  - Ingested `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]` and `@[docs/epic/EPIC_161_audit_report.md]`.
  - Verified AST symbol line spans across all target Python files and confirmed zero pre-implemented Epic 161 changes in the codebase.
  - Generated four micro-chunked phased implementation plans in `@[docs/epic/tasks_EPIC_161/]`:
    - `@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]` (Phase 1: Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation)
    - `@[docs/epic/tasks_EPIC_161/02_phase2_plan.md]` (Phase 2: Orchestration, Frontier Contrastive Deficit Injection & Synthesis Convergence)
    - `@[docs/epic/tasks_EPIC_161/03_phase3_plan.md]` (Phase 3: Frontend Flutter UI, Jinja PDF & Freezed SDUI DTO Synchronization)
    - `@[docs/epic/tasks_EPIC_161/04_phase4_plan.md]` (Phase 4: Verification & E2E Integration Gate)
  - Created and synchronized `@[docs/epic/EPIC_161_tracker.md]` with 1:1 Requirement Traceability (`REQ-161-001` through `REQ-161-012`), unified `--gate all` hardening commands, and parameterized `/tier7-describe-architecture` directives.

## Learned
- All 32 exact `#Lnn-Lmm` AST boundaries from `@[docs/epic/EPIC_161_topological_synthesis_cohesion.md]` and the 5-Pillar Asymmetric Epistemic Distillation Architecture (`1500`-char Micro-CoT reasoning ceiling, zero-loss retention of `FAILED`/`N_A`/`is_inverse_evidence` evaluations, topological deficit sorting, transitive parent-to-child `N_A` hydration, frontier $S+1$ contrastive injection capped at `3` per row, and 4-task `CausalSynthesisBriefDTO` fan-out) are locked across Phases 1–4.

## Remaining
- Execute Tier 0 Research & Red-Teaming on Phase 1 (`@[docs/epic/tasks_EPIC_161/01_phase1_plan.md]`), followed by sequential execution of Phases 1 through 4 and Post-Implementation Gates. The next agent must run `/tier0-research-plan` to analyze the Phase 1 plan first before any code execution.

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md]
```
