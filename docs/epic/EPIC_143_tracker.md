# EPIC 143 Tracker: Synthesis Matrix Explanation Timing Fix & Architecture Hardening

**Epic Document:** @[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]
**Task Directory:** @[docs/epic/tasks_EPIC_143/]

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[.agents/rules/05_llm_architecture.md]
- @[ki_god_code_prevention.md]
- @[ki_synthesis_payload_compression.md]
- @[ki_matrix_boolean_evaluation_strictness.md]
- @[ki_dual_axis_localization_architecture.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_sdui_matrix_synthesis.md]
- @[ki_sdui_adapter_pattern.md]
- @[ki_flat_polymorphic_pipeline.md]
- @[ki_global_config_sovereignty.md]
- @[ki_python_314_concurrency_strictness.md]
- @[ki_ai_testing_standards.md]
- @[ki_ast_guardrail_testing.md]
- @[ki_dag_engine_dto_projection_rules.md]
- @[ki_epic_lifecycle_workflow.md]
- @[ki_context_enriched_decompose_verify.md]
- @[ki_strict_sdui_serialization.md]
- @[ki_llm_extraction_architecture.md]
- @[ki_topological_engine.md]
- @[ki_execution_engine_protocol.md]
- @[ki_matrix_sensor_prompt_builder.md]
</required_context_rules>

## Phase Execution Status

### Phase 1: Foundation & SSOT Utilities
**Plan:** @[docs/epic/tasks_EPIC_143/01_phase1_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_143/01_phase1_plan.md] @[docs/epic/EPIC_143_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_143/01_phase1_plan.md] @[docs/epic/EPIC_143_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Centralized Settings SSOT Verification (VERIFIED_EXISTING)
  - [x] Step 2: Ranked Round-Robin SSOT Utility Implementation
  - [x] Step 3: Ranked Round-Robin Unit Tests
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_143/01_phase1_plan.md] @[docs/epic/EPIC_143_tracker.md]`


### Phase 2: Distiller Unfiltered Context Pipeline & Locale Hoisting
**Plan:** @[docs/epic/tasks_EPIC_143/02_phase2_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_143/02_phase2_plan.md] @[docs/epic/EPIC_143_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_143/02_phase2_plan.md] @[docs/epic/EPIC_143_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: AST Boundary Verification Pre-Step (God File Mandate) (VERIFIED_EXISTING / COMPLETED)
  - [x] Step 2: Synthesis Distiller Locale Hoisting & Legacy Key Purge
  - [x] Step 3: Synthesis Distiller Wiring Unit Tests
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_143/02_phase2_plan.md] @[docs/epic/EPIC_143_tracker.md]`

### Phase 3: Matrix Explanation Service Hardening & Dual Reporting
**Plan:** @[docs/epic/tasks_EPIC_143/03_phase3_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_143/03_phase3_plan.md] @[docs/epic/EPIC_143_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_143/03_phase3_plan.md] @[docs/epic/EPIC_143_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Matrix Explanation Service Hardening & Dual Reporting
  - [x] Step 2: Synthesis Payload Compressor SSOT Alignment
  - [x] Step 3: TypeAdapter Definition & Worker Direct Serialization (Double-Serialization Ban)
  - [x] Step 4: Knowledge Base Alignment
  - [x] Step 5: Matrix Explanation Service Unit & Contract Tests (Atomic Test Migration)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_143/03_phase3_plan.md] @[docs/epic/EPIC_143_tracker.md]`

### Phase 4: SDUI Presentation & XAI Highlights Fair Distribution
**Plan:** @[docs/epic/tasks_EPIC_143/04_phase4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_143/04_phase4_plan.md] @[docs/epic/EPIC_143_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_143/04_phase4_plan.md] @[docs/epic/EPIC_143_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: XAI Highlights SDUI Adapter Hardening & Round-Robin Fair Distribution
  - [ ] Step 2: XAI Highlights SDUI Adapter Unit Tests
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_143/04_phase4_plan.md] @[docs/epic/EPIC_143_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] Backend and Frontend full-stack integration test gates.

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend @[backend_v2/settings.py] @[backend_v2/utils/ranked_round_robin.py] @[backend_v2/tests/unit/utils/test_ranked_round_robin.py] @[backend_v2/services/orchestrator/synthesis_distiller.py] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py] @[backend_v2/models/dtos/synthesis.py] @[backend_v2/worker.py] @[backend_v2/services/orchestrator/matrix_explanation_service.py] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py] @[backend_v2/tests/unit/test_epic93_contract_verification.py] @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py] @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying created/modified `@-referenced` Flutter files. (N/A - no Flutter files created/modified).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** Epic Boundary Audit: Run `uv run python scripts/audit_markdown_boundaries.py --file @[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]` to verify all AST line boundaries in the Epic are still correct.
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- Atomic commits are MANDATORY per file or cohesively related block of logic.
- If seeding is necessary, use `uv run python backend_v2/seed/run_seed.py local`.
- ALWAYS use `@-reference` syntax when referring to files (e.g. `@[backend_v2/utils/ranked_round_robin.py]`).
- You MUST update the `/tier5-resume` or `/tier0-research-plan` (or `/tier0-create-plan` if the plan is missing) command at the bottom of this tracker before handing over the session.
- Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue.
- The mandatory workflow loop is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`.
- You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
- Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.
- Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

## Requirements Traceability Matrix
| Requirement ID | Description | Mapped Step (Phase & Step ID) |
|---|---|---|
| REQ-143-01 | Verify centralized settings SSOT in `Settings` (`max_synthesis_quote_length: int = 300`, `max_synthesis_quotes_per_matrix: int = 5`, `max_synthesis_unmet_criteria_per_matrix: int = 5`) per `global_config_sovereignty`. | Phase 1, Step 1 |
| REQ-143-02 | Implement pure generic `ranked_round_robin_select[T]` utility using PEP 695 generics in `backend_v2/utils/ranked_round_robin.py` as SSOT for group interleaving. | Phase 1, Step 2 |
| REQ-143-03 | Guarantee $O(N \log N + K)$ algorithmic performance in `ranked_round_robin_select` via internal inverted sorting and native $O(1)$ tail `.pop()` extraction. | Phase 1, Step 2 |
| REQ-143-04 | Implement strict dictionary key deletion `del groups[eg]` in `ranked_round_robin_select` without `.pop(eg, None)` fallbacks per `anti_lazy_fallback_mandate`. | Phase 1, Step 2 |
| REQ-143-05 | Create unit test suite for Ranked Round-Robin utility in `test_ranked_round_robin.py` covering empty inputs, single group, multi-group interleaving, budget capping, unequal groups, and $O(1)$ tail pop performance scaling (< 25ms for $10^4$ items). | Phase 1, Step 3 |
| REQ-143-06 | Execute AST boundary verification pre-step for `synthesis_distiller.py` (324 lines > 300 God File threshold) extracting exact method line bounds. | Phase 2, Step 1 |
| REQ-143-07 | Hoist and unify `target_locale` validation at start of `synthesis_distiller_hook` with strict Fail-Fast validation (`AppException(VALIDATION_FAILED)` on missing or whitespace strings). | Phase 2, Step 2 |
| REQ-143-08 | Verify complete elimination of `target_blocks` filter loop in `synthesis_distiller.py`, preserving complete cognitive sensor findings in `<source>` prompt blocks. | Phase 2, Step 2 |
| REQ-143-09 | Pass unfiltered `available_dtos` directly to alias registration, `<source>` prompt distillation, and `MatrixExplanationService.assemble_matrices_to_explain`. | Phase 2, Step 2 |
| REQ-143-10 | Rename parameter from `language` to `target_locale` in `_build_title_map` function in `synthesis_distiller.py`. | Phase 2, Step 2 |
| REQ-143-11 | Purge deprecated `"language": target_locale` key from `HookResult.state_delta` in `synthesis_distiller.py` (exporting ONLY `"target_locale"`) to enforce Zero Backwards Compatibility per `the_no_legacy_mandate`. | Phase 2, Step 2 |
| REQ-143-12 | Create synthesis distiller wiring unit tests in `test_synthesis_distiller_wiring.py` (unfiltered DTOs, missing/whitespace `target_locale`, cognitive sensor preservation, legacy key purge). | Phase 2, Step 3 |
| REQ-143-13 | Update `MatrixExplanationService.assemble_matrices_to_explain` signature to require mandatory `target_locale: str` without optional defaults. | Phase 3, Step 1 |
| REQ-143-14 | Hoist global settings at start of `assemble_matrices_to_explain` (`max_synthesis_quote_length`, `max_synthesis_quotes_per_matrix`, `max_synthesis_unmet_criteria_per_matrix`) eliminating $O(N)$ lookup overhead. | Phase 3, Step 1 |
| REQ-143-15 | Eliminate 12 legacy anti-patterns (`isinstance`, `hasattr`, `getattr`, `.get()`, raw `+` concatenation, unhandled validation errors) in `MatrixExplanationService`. | Phase 3, Step 1 |
| REQ-143-16 | Implement strict `None`-guard on nullable `AtomResultDTO.source_quote` and filter low-substance quote fragments (< 15 characters) from `SUPPORTING EVIDENCE`. | Phase 3, Step 1 |
| REQ-143-17 | Wrap `LightweightMatrixOutput.model_validate` and `LevelStatsDTO.model_validate` in `try...except (ValidationError, ValueError)` probe boundaries with diagnostic warning logging (`ErrorCodes.INVALID_OUTPUT_SCHEMA`). | Phase 3, Step 1 |
| REQ-143-18 | Implement explicit `if lw_matrix.level_breakdown:` guard in `MatrixExplanationService` preventing `AttributeError` on non-hierarchical matrices. | Phase 3, Step 1 |
| REQ-143-19 | Resolve claim labels dynamically using `claim.label.resolve(target_locale)` supporting multilingual localization without hardcoded English. | Phase 3, Step 1 |
| REQ-143-20 | Implement Status-Aware Dual Reporting in `MatrixExplanationService` (segregating `SUPPORTING EVIDENCE:` for `PASSED` atoms and `UNMET CRITERIA / DEFICITS:` for `FAILED` atoms), eliminating Positivity Bias. | Phase 3, Step 1 |
| REQ-143-21 | Implement Ranked Round-Robin claim diversity in `MatrixExplanationService` with per-matrix pre-deduplication hash set (`seen_matrix_quotes`), eliminating Single-Claim Starvation and Deduplication Starvation. | Phase 3, Step 1 |
| REQ-143-22 | Implement deterministic unmet criteria curation sorted in ascending scale score order (Level 1 critical deficits first, alphabetical tie-break), eliminating Priority Inversion. | Phase 3, Step 1 |
| REQ-143-23 | Replace hardcoded `[:300]` quote slice in `SynthesisPayloadCompressor` with `settings_obj.max_synthesis_quote_length`. | Phase 3, Step 2 |
| REQ-143-24 | Update `ki_synthesis_payload_compression.md` to replace references to `ExtractiveSensorService` with `MatrixExplanationService` and document centralized quote limits and round-robin curation. | Phase 3, Step 3 |
| REQ-143-25 | Execute atomic test migration updating 5 existing test cases in `test_matrix_explanation_service.py` to pass `target_locale="en"` and assert updated Status-Aware justification headers. | Phase 3, Step 4 |
| REQ-143-26 | Add 6 new unit tests in `test_matrix_explanation_service.py` (round-robin diversity, deduplication starvation prevention, severity order sorting, short quote filtering, multilingual resolution, corrupt level stats handling). | Phase 3, Step 4 |
| REQ-143-27 | Update call-site in `test_epic93_contract_verification.py` to pass mandatory `target_locale="en"` in `test_matrices_to_explain_assembly`. | Phase 3, Step 4 |
| REQ-143-28 | Integrate `ranked_round_robin_select` into `XaiHighlightsAdapter.build` to interleave highlights across active extension types ranked by content length/informativeness, eliminating Primacy Bias and Category Starvation. | Phase 4, Step 1 |
| REQ-143-29 | Implement strict graceful UI degradation in `XaiHighlightsAdapter` (returning `[]` immediately when `visible_block_extensions` is empty/None or `max_extension_items` is zero/None). | Phase 4, Step 1 |
| REQ-143-30 | Eliminate duck-typing in `XaiHighlightsAdapter` (`isinstance(item, dict)`, `.get()`, `getattr()`) with strict `XaiHighlightItem.model_validate` probe boundary and warning logging. | Phase 4, Step 1 |
| REQ-143-31 | Preserve SDUI presentation schema invariance (keeping `SduiMatrixTableBlock` and Flutter Freezed DTOs 100% structurally compatible without client-side modifications). | Phase 4, Step 1 |
| REQ-143-32 | Expand unit test suite in `test_xai_highlights_adapter.py` (graceful degradation, round-robin distribution across categories, malformed item skipping). | Phase 4, Step 2 |

# Session Handover Context
## Achieved
- **[Epic 143 Planning & Architecture Finalized]**: All 4 implementation plans (`01_phase1_plan.md` through `04_phase4_plan.md`) generated, fully verified, and aligned with `@[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]`.
- **[Epic 143 Tracker Created]**: Authored `@[docs/epic/EPIC_143_tracker.md]` with granular execution status checkboxes, post-implementation quality gates, instructions for execution agent, and a 32-item Requirements Traceability Matrix covering RCA-1 through RCA-14 and Anti-Happy-Path scenarios A through X.
- **[Phase 1 Red-Teaming, Execution & Audit Complete]**:
  - Centralized settings SSOT verified in `@[backend_v2/settings.py#L136-L138]`.
  - Implemented `ranked_round_robin_select[T]` in `@[backend_v2/utils/ranked_round_robin.py]` with inverted sort and $O(1)$ tail pop.
  - Implemented and passed all 13 unit test contracts in `@[backend_v2/tests/unit/utils/test_ranked_round_robin.py]`.
  - Tier 8 audit passed cleanly with 100% test coverage.
- **[Phase 2 Red-Teaming, Execution & Audit Complete]**:
  - AST boundaries verified for `@[backend_v2/services/orchestrator/synthesis_distiller.py]`: `_build_title_map` (L111-L156), `synthesis_distiller_hook` (L160-L323).
  - Purged deprecated `"language": target_locale` key from `HookResult.state_delta` in `@[backend_v2/services/orchestrator/synthesis_distiller.py#L309-L322]` (exporting ONLY `"target_locale"`), enforcing Zero Backwards Compatibility per `the_no_legacy_mandate`.
  - Created and passed 12 comprehensive unit test contracts in `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`.
  - Re-exported wiring tests in `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]` and passed the Universal Quality Gate with 64% coverage (> 30% gate requirement).
  - Completed Tier 8 Audit (`/tier8-audit-plan @[docs/epic/tasks_EPIC_143/02_phase2_plan.md] @[docs/epic/EPIC_143_tracker.md]`) with PASSED verdict documented in `@[docs/epic/tasks_EPIC_143/red_team_audit_02_phase2_plan.md]`.
- **[Phase 3 Red-Teaming, Execution & Tests Complete]**:
  - `MatrixExplanationService.assemble_matrices_to_explain` hardened with Status-Aware Dual Reporting (`SUPPORTING EVIDENCE:` and `UNMET CRITERIA / DEFICITS:`), Ranked Round-Robin quote selection, ascending scale score severity-first unmet criteria curation, and mandatory `target_locale: str` without fallback defaults.
  - Eliminated legacy anti-patterns (`isinstance`, `hasattr`, `getattr`, `.get()`, raw `+` concatenation, unhandled validation errors) and added probe boundaries with `INVALID_OUTPUT_SCHEMA` warning logs.
  - `MatrixExplanationContextList = TypeAdapter(list[MatrixExplanationContextDTO])` defined in `@[backend_v2/models/dtos/synthesis.py]`.
  - Double-Serialization in `@[backend_v2/worker.py]` eliminated using direct `MatrixExplanationContextList.dump_json(...)`.
  - Quote length in `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]` centralized to `settings.max_synthesis_quote_length`.
  - Updated `@[ki_synthesis_payload_compression.md]` with SSOT settings and TypeAdapter direct dump.
  - Implemented 11 unit tests in `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]` and updated contract test in `@[backend_v2/tests/unit/test_epic93_contract_verification.py]`.
  - Universal Quality Gate passed with 93% line coverage on `MatrixExplanationService` and 79% overall on `backend_v2/services/orchestrator/`.

## Learned
### Baseline State Snapshot & Execution Lessons
- **Ranked Round-Robin Utility (`backend_v2/utils/ranked_round_robin.py`)**:
  - Generic SSOT utility for interleaved selection with $O(1)$ tail pop extraction and strict dictionary key deletion `del groups[k]`.
- **Synthesis Distiller Hook (`backend_v2/services/orchestrator/synthesis_distiller.py`)**:
  - Confirmed `target_blocks` pruning loop is completely deleted, allowing full cognitive findings to flow into `<source>` tags and matrix explanation.
  - `target_locale` is strictly validated at hook entry with Fail-Fast (`AppException(VALIDATION_FAILED)`) on missing or whitespace values.
  - `HookResult.state_delta` exports strictly `"target_locale"`, eliminating legacy `"language"` duplication.
  - Passes all 29 unit tests in `test_synthesis_distiller_wiring.py` and `test_synthesis_distiller.py` with 64% coverage.
- **Matrix Explanation Service Hardening (`backend_v2/services/orchestrator/matrix_explanation_service.py`)**:
  - Status-Aware Dual Reporting (`SUPPORTING EVIDENCE:` for `PASSED` atoms and `UNMET CRITERIA / DEFICITS:` for `FAILED` atoms) cleanly eliminates Positivity Bias.
  - Pre-deduplication with `seen_matrix_quotes: set[str]` before `ranked_round_robin_select` prevents post-selection quota collapse.
  - Severity-first ascending scale order sorting for unmet criteria eliminates Priority Inversion.
  - `TypeAdapter(list[MatrixExplanationContextDTO])` direct dump in `worker.py` eliminates double-serialization overhead and intermediate Python dict allocations.
  - Mandatory `target_locale: str` across all production and test call-sites without fallback defaults.

## Remaining
- **Phase 3 Audit**: Run `/tier8-audit-plan @[docs/epic/tasks_EPIC_143/03_phase3_plan.md] @[docs/epic/EPIC_143_tracker.md]`.
- **Phase 4 Planning, Execution & Audit**: Harden `XaiHighlightsAdapter` with Ranked Round-Robin highlight curation, graceful degradation, and expanded unit tests.
- **Post-Implementation & Final Audits**: Tier 2 Hardening (Backend), Golden Master audit, E2E gate, documentation sync, and Tier 8 Reverse Epic Analysis.

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_EPIC_143/03_phase3_plan.md] @[docs/epic/EPIC_143_tracker.md]`

