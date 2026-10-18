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

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups & Foundations
- **Plan:** @[docs/epic/tasks_EPIC_158/01_phase1_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 1.1: Verify duplicate Epic deletion and establish `coerce_source_quotes_tuple` SSOT in `core_base.py`
  - [ ] Step 1.2: Modernize `QuoteEvidenceDTO` and define strongly typed defined `GateMatchResultDTO` anti-tuple contract
  - [ ] Step 1.3: Remediate asymmetric quote extraction in `AnchorValidationService`
  - [ ] Step 1.4: Clean up mutating `truncate_source_quote_at_sentence` and unannotated linker collection factories
  - [ ] Step 1.5: Refine export formatter typing strictness and guard printable sources scalar access
  - [ ] Step 1.6: Remediate Flutter Theme Sovereignty and localization in touched widgets
  - [ ] Step 1.7: Implement and pass multi-segment foundation unit test suite
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 2: Domain Model, DTO, Client Freezed Contract & Test Fixture Multi-Segment Schema Refactoring (WP1)
- **Plan:** @[docs/epic/tasks_EPIC_158/02_phase2_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/02_phase2_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 2.1: Refactor backend domain models and DAG DTOs to `source_quotes: tuple[str, ...] | None`
  - [ ] Step 2.2: Refactor 1-hop caller orchestration, state reducer, and hook services
  - [ ] Step 2.3: Update atom extraction prompts, system instructions, and schema descriptions
  - [ ] Step 2.4: Synchronize Flutter Freezed DTO contracts and client citation widgets
  - [ ] Step 2.5: Synchronize test fixtures, factories, golden master files, and unit test suites
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/02_phase2_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)
- **Plan:** @[docs/epic/tasks_EPIC_158/03_phase3_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 3.1: Enhance coordinate normalization and strict matching for multi-segment tuples
  - [ ] Step 3.2: Implement forward-scan search, monotonic ordering, and single-document isolation in `AnchorValidationService`
  - [ ] Step 3.3: Update prompt extraction mandate in `matrix_evaluation.py` for 1–3 non-contiguous sentences
  - [ ] Step 3.4: Expand ISTQB boundary and negative test suite in `test_anchor_validation_service.py`
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)
- **Plan:** @[docs/epic/tasks_EPIC_158/04_phase4_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 4.1: Add `default_lexical_strictness_level` to `Workflow` domain model and Studio DTOs
  - [ ] Step 4.2: Update Studio workflow CRUD service to transit decoupled lexical strictness
  - [ ] Step 4.3: Synchronize database seed vault workflows and add localization strings
  - [ ] Step 4.4: Calibrate settings lexical threshold resolution function
  - [ ] Step 4.5: Transit decoupled lexical strictness in execution worker and DAG executor
  - [ ] Step 4.6: Expand worker and anchor validation test suites verifying morphological calibration
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)
- **Plan:** @[docs/epic/tasks_EPIC_158/05_phase5_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 5.1: Configure linker settings and budget capacity limits in `settings.py`
  - [ ] Step 5.2: Implement bounded deliverable root axiom header injection with dynamic quota allocation in `SlidingWindowLinker`
  - [ ] Step 5.3: Support multi-segment Toulmin warrants in causal edge records
  - [ ] Step 5.4: Implement Algorithm 1 dual fault attribution separating warrant grounding failures
  - [ ] Step 5.5: Expand causal linker and cohesion scoring test suites
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)
- **Plan:** @[docs/epic/tasks_EPIC_158/06_phase6_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 6.1: Synchronize tabular export streaming services for CSV and Excel formats
  - [ ] Step 6.2: Update SDUI highlights and printable sources adapters
  - [ ] Step 6.3: Remediate Jinja2 PDF template evidence quote emission
  - [ ] Step 6.4: Regenerate OpenAPI specification artifact reflecting schema updates
  - [ ] Step 6.5: Implement Studio continuous slider for lexical verification strictness
  - [ ] Step 6.6: Update client citation and causal inspector widgets
  - [ ] Step 6.7: Execute presentation and Flutter client audit gates
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)
- **Plan:** @[docs/epic/tasks_EPIC_158/07_phase7_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 7.1: Implement end-to-end multi-segment integration test suite
  - [ ] Step 7.2: Execute offline ablation benchmark ($N=220$) and verify zero chimera leaks
  - [ ] Step 7.3: Execute full audit gates and mandatory live E2E real LLM test
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Phase 8: As-Built Architectural Documentation & Scientific Manuscript Synchronization (`@[docs/tiede.md]`)
- **Plan:** @[docs/epic/tasks_EPIC_158/08_phase8_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_158/08_phase8_plan.md] @[docs/epic/EPIC_158_tracker.md]`
  - [ ] Step 8.1: Update directory reference rule with new integration tests and services
  - [ ] Step 8.2: Synchronize scientific manuscript `docs/tiede.md` with formal definitions, theorems, and benchmark results
  - [ ] Step 8.3: Execute parameterized Tier 7 as-built architecture audit
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/08_phase8_plan.md] @[docs/epic/EPIC_158_tracker.md]`

### Post-Implementation Gates

#### Backend Code Hardening Checklist (`.py`)
- [ ] `@[backend_v2/models/core_base.py]` hardened with `coerce_source_quotes_tuple` SSOT
- [ ] `@[backend_v2/models/dtos/quote_evidence.py]` hardened with defined `GateMatchResultDTO` anti-tuple contract
- [ ] `@[backend_v2/models/domain/blackboard.py]` hardened with `source_quotes: tuple[str, ...] | None`
- [ ] `@[backend_v2/models/dtos/dag_models.py]` hardened with `source_quotes: tuple[str, ...] | None`
- [ ] `@[backend_v2/models/dtos/causal_discovery.py]` hardened with `source_quotes: tuple[str, ...] | None`
- [ ] `@[backend_v2/models/dtos/atom_result.py]` hardened with `source_quotes: tuple[str, ...] | None`
- [ ] `@[backend_v2/models/dtos/matrix_scorecard.py]` hardened with `source_quotes: tuple[str, ...] | None`
- [ ] `@[backend_v2/models/domain/workflow.py]` hardened with decoupled `default_lexical_strictness_level`
- [ ] `@[backend_v2/models/dtos/studio.py]` hardened with `default_lexical_strictness_level`
- [ ] `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` hardened against mutating text truncation
- [ ] `@[backend_v2/services/orchestrator/anchor_validation_service.py]` hardened with symmetric index mapping and span ceiling
- [ ] `@[backend_v2/services/orchestrator/sliding_window_linker.py]` hardened with bounded root axiom injection
- [ ] `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` hardened with Algorithm 1 dual fault attribution
- [ ] `@[backend_v2/services/orchestrator/result_projector.py]` hardened with multi-segment tuple projection
- [ ] `@[backend_v2/services/orchestrator/matrix_reducer.py]` hardened with multi-segment quote transit
- [ ] `@[backend_v2/services/orchestrator/two_pass_atomizer.py]` hardened with multi-segment quote validation
- [ ] `@[backend_v2/services/orchestrator/topological_evaluator.py]` hardened with multi-segment tuple support
- [ ] `@[backend_v2/services/orchestrator/dag_executor.py]` hardened with decoupled lexical strictness propagation
- [ ] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]` hardened with multi-segment proposition support
- [ ] `@[backend_v2/services/studio/workflow_service.py]` hardened with lexical strictness validation
- [ ] `@[backend_v2/workers/execution_worker.py]` hardened with dual strictness extraction
- [ ] `@[backend_v2/hooks/scoring/matrix_hook.py]` hardened with multi-segment quote evidence transit
- [ ] `@[backend_v2/services/matrix_domain_parser.py]` hardened with multi-segment quote parsing
- [ ] `@[backend_v2/services/export_service.py]` hardened with standardized citation delimiter
- [ ] `@[backend_v2/services/export_evidence_formatter.py]` hardened with strict tuple type signature
- [ ] `@[backend_v2/services/report_service.py]` hardened with multi-segment quote row generation
- [ ] `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` hardened with multi-segment highlight citations
- [ ] `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` hardened against scalar quote attribute access
- [ ] `@[backend_v2/settings.py]` hardened with `linker_max_global_root_axioms` SSOT setting
- [ ] `@[backend_v2/models/prompts/execution/matrix_evaluation.py]` hardened with multi-segment extraction instructions
- [ ] `@[backend_v2/models/prompts/execution/field_prompts.py]` hardened with multi-segment schema descriptions
- [ ] `@[backend_v2/services/orchestrator/prompts/atom_extraction.py]` hardened with multi-segment citation instructions
- [ ] `@[backend_v2/scripts/generate_openapi.py]` hardened with schema synchronization
- [ ] `@[scripts/run_e2e_variance_test.py]` hardened with multi-segment offline benchmark validation

#### Frontend Code Hardening Checklist (`.dart`)
- [ ] `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]` hardened with `sourceQuotes` List contract
- [ ] `@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]` hardened with `sourceQuotes` List contract
- [ ] `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]` hardened with `sourceQuotes` List contract
- [ ] `@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]` hardened with `sourceQuotes` List contract
- [ ] `@[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]` hardened with `sourceQuotes` List contract
- [ ] `@[client_app_v2/lib/features/studio/models/workflow.dart]` hardened with `defaultLexicalStrictnessLevel`
- [ ] `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]` hardened with Theme Sovereignty and l10n tokens
- [ ] `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` hardened with multi-segment quote interpolation
- [ ] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]` hardened with null-safe multi-segment quote display
- [ ] `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]` hardened with Theme typography and tokens
- [ ] `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]` hardened with independent lexical strictness slider

#### Documentation & Knowledge Item Update
- [ ] Parameterized `/tier7-describe-architecture` command executed:
  `/tier7-describe-architecture @[docs/epic/EPIC_158_tracker.md] @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[ki_structured_forensic_quotes.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]`
- [ ] Directives verified:
  1. Target KIs to Synchronize: `@[ki_structured_forensic_quotes.md]`, `@[ki_topological_engine.md]`, `@[ki_unified_matrix_scoring_strictness.md]`, `@[ki_prompt_orchestration_and_matrix_evaluation.md]`.
  2. Directory Reference Sync: `@[.agents/rules/04_directory_reference.md]`.
  3. Pillar Documentation Sync: `@[docs/architecture/01_system_context_and_invariants.md]`, `@[docs/architecture/03_cognitive_orchestration_engine.md]`, `@[docs/architecture/04_server_driven_ui_and_presentation.md]`.
  4. Scientific Manuscript Proof & Synthesis (`@[docs/tiede.md]`): Formalize mathematical definitions, theorems, proofs, and empirical ablation tables.

### Final Epic Audit
- [ ] Verification audit executed: `/tier8-audit-epic @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[docs/epic/EPIC_158_tracker.md]`
- [ ] All 100 target files confirmed verified on physical disk.
- [ ] All 7 line bounds confirmed respected without lossy compression.
- [ ] Zero AST warnings or typing errors reported by quality gate audit scripts.

## Instructions for the Execution Agent
1. **Stateless Reset**: Begin every phase by physically reading `@[.agents/rules/00-antigravity-core.md]` and domain rule files before any execution logic.
2. **Sequential Phase Gates**: Execute phases in strict numerical order (Phase 1 through Phase 8). Never start Phase N+1 until Phase N has passed its audit gate.
3. **Fail-Fast Invariant**: If any test fails or validation crashes, halt immediately and diagnose root cause. Never suppress errors or write duct-tape bypasses.
4. **Preserve Prompts**: Never modify qualitative natural-language prompt texts or persona instructions in `seed_data.json` without explicit authorization.

## Requirements Traceability Matrix

| Requirement ID | Description | Implementation Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-158-001** | Eliminate duplicate Epic file to maintain single SSOT | Phase 1, Step 1 | PENDING |
| **REQ-158-002** | Establish canonical `coerce_source_quotes_tuple` SSOT pre-validator | Phase 1, Step 1 | PENDING |
| **REQ-158-003** | Eradicate anonymous 3-tuples via `GateMatchResultDTO` contract | Phase 1, Step 2 | PENDING |
| **REQ-158-004** | Remediate asymmetric quote extraction in `AnchorValidationService` | Phase 1, Step 3 | PENDING |
| **REQ-158-005** | Eliminate mutating text truncation in `ExtractiveSensorService` | Phase 1, Step 4 | PENDING |
| **REQ-158-006** | Replace unannotated lambda dictionary factories in `SlidingWindowLinker` | Phase 1, Step 4 | PENDING |
| **REQ-158-007** | Lock export evidence formatter signature to strict immutable tuple | Phase 1, Step 5 | PENDING |
| **REQ-158-008** | Remediate scalar quote access in `PrintableSourcesAdapter` | Phase 1, Step 5 | PENDING |
| **REQ-158-009** | Enforce Flutter Theme Sovereignty in override dialog and modals | Phase 1, Step 6 | PENDING |
| **REQ-158-010** | Implement multi-segment foundation unit test suite | Phase 1, Step 7 | PENDING |
| **REQ-158-011** | Modernize Pydantic V2 domain models and DTOs to multi-segment tuple schema | Phase 2, Step 1 | PENDING |
| **REQ-158-012** | Refactor 1-hop caller orchestration, state reducer, and hook services | Phase 2, Step 2 | PENDING |
| **REQ-158-013** | Update atom extraction prompts, system instructions, and schema descriptions | Phase 2, Step 3 | PENDING |
| **REQ-158-014** | Synchronize Flutter Freezed DTO contracts and client citation widgets | Phase 2, Step 4 | PENDING |
| **REQ-158-015** | Synchronize test fixtures, factories, golden master files, and unit tests | Phase 2, Step 5 | PENDING |
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
- Decomposed EPIC 158 into 8 comprehensive phased implementation plans in `docs/epic/tasks_EPIC_158/`.
- Preserved all 100 target files, 7 exact line bounds, and 19 Knowledge Item references verbatim from the parent Epic without lossy compression.
- Created `docs/epic/EPIC_158_tracker.md` with full phase execution statuses, file-granular hardening checklists, parameterized documentation directives, and a bidirectional Requirements Traceability Matrix mapping all 40 plan steps.
- Executed Tier 0 Research & Analysis on `docs/epic/tasks_EPIC_158/01_phase1_plan.md`, producing a hardened 5-Column Architectural Directives Table with zero permissive typing, zero unannotated collections, and zero `hasattr`/`getattr` reflection.
- Validated planner output and markdown boundaries with 100% pass rates across `scripts/audit_planner_output.py` and `scripts/audit_markdown_boundaries.py`.

## Learned
- Multi-segment evidence extraction requires preserving physical coordinate mappings and forward monotonic order ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$) with single-document buffer boundary isolation to maintain $\text{Specificity}_{lex} = 1.000$.
- Decoupling lexical tolerance ($\zeta_{lex}$) from power-curve score dampening ($\zeta_{score}$) enables valid Finnish inflection recognition via Gate 5 Snowball stemming without artificially penalizing strict scoring evaluations.
- Deliverable root axiom anchoring ($K_{axiom}^{max} = 8$ axioms where $InDegree(v)=0$) in `SlidingWindowLinker` resolves document length-dependent causal horizon truncation while dynamically guarding the prompt budget ($M_{win} \le 20$).
- Forward compatibility without QGR reflection violations: in Phase 1, `QuoteEvidenceDTO` must provide a strongly typed `get_quotes()` accessor returning `tuple[str, ...]`, allowing callers (specifically: `PrintableSourcesAdapter`) to iterate safely without breaking duck-typing bans (`hasattr`, `getattr`).
- `SlidingWindowLinker` settings injection: `get_settings()` should be injected via constructor `settings: Settings | None = None` and stored on `self.max_atoms_per_window`, eliminating repeated fetches in loops without breaking existing imports.
- Flutter localization parity: Touched widgets require adding `humanOverrideDefaultBadge`, `causalInspectorCitationEvidenceHeader`, and `causalInspectorLocationPrefix` to both `app_en.arb` and `app_fi.arb` before running code generation.

## Remaining
- Execute Phase 1 implementation via `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`.
- Execute Phase 1 audit via `/tier8-audit-plan @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`.
- Proceed sequentially to Phase 2 through Phase 8.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]
```
