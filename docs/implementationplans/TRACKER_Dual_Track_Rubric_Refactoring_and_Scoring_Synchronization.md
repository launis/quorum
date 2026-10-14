# Tracker: Dual-Track Rubric Refactoring & Scoring Architecture Synchronization

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]`
  - [x] Step 1: Seed Vault Backup and Preflight Verification
  - [x] Step 2: Seed Vault Dual-Track Rubric Refactoring
  - [x] Step 3: Scoring Unit and Property Test Expansion
  - [ ] Step 4: Knowledge Items Synchronization
  - [x] Step 4: Knowledge Items Synchronization
  - [x] Step 5: Architecture Compendium Update (08_matrix_explanations.md)
  - [x] Step 6: Architecture Pillars Documentation Synchronization
  - [x] Step 7: Seed Vault In-Memory Audit and Atomic Reseed
  - [x] Step 8: Universal Quality Gates and Boundary Audit
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files (No production backend code files modified in target scope; seed vault and tests only).
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files (No frontend files modified).
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic (Achieved 97.75%).

### Documentation & Knowledge Item Update
- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_unified_matrix_scoring_strictness.md]`: Document Section 5 'Dual-Track Rubric Architecture: Progressive Novice vs Malus Error Radar', detailing hit ratios, Guttman cumulative progression, Inverted Rubric Paradox prohibition, and multi-matrix global score aggregation.
     - `@[ki_prompt_orchestration_and_matrix_evaluation.md]`: Document the mandatory dichotomy between positive evidence extraction for Developmental TDA atoms and inverse error radar falsification for Diagnostic TDA atoms.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any seed scripts, hooks, or test utilities are structurally updated or added.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/08_matrix_explanations.md`, `docs/architecture/03_cognitive_orchestration_engine.md`, `docs/architecture/02_data_seeding_and_ontology.md`, `docs/architecture/04_server_driven_ui_and_presentation.md`, and `docs/architecture/06_enriched_atom_graph_engine.md` describing newly established Dual-Track Rubric invariants, Dumb Painter presentation parity, and machine-readable 22-column CSV streaming in present tense without historical language or plan IDs.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Strict Execution Mode**: Do not modify domain files without slash command invocation `/tier2-execute`.
- **Quality Gates**: After each logical step, run `uv run python scripts/backend_audit_loop.py <target_path> --test` for Python files and markdown boundary validation for documentation.
- **Atomic Commits**: Run atomic git commits with Conventional Commits syntax following successful quality gate runs.
- **Double-Entry Bookkeeping**: Mark each completed step with `[x]` in this tracker and keep `# Session Handover Context` synchronized.
- **Execution Mode**: Continuous Full-Auto Mode authorized via `/tier2-execute --full-auto`.

## Requirements Traceability Matrix
| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Seed Vault Backup and Preflight Baseline Verification | Step 1 | Completed |
| REQ-002 | Refactor 6 Developmental Matrices to Positive Novice Baseline (Track A) | Step 2 | Completed |
| REQ-003 | Refactor 8 Diagnostic Matrices to Two-Factor Orthogonal Malus (Track B) | Step 2 | Completed |
| REQ-004 | Scoring Unit and Property Test Expansion for Dual-Track Dynamics | Step 3 | Completed |
| REQ-005 | Knowledge Items Synchronization (Unified Scoring & Prompt Orchestration) | Step 4 | Completed |
| REQ-006 | Architecture Compendium Update (08_matrix_explanations.md) and Orphan Cleanup | Step 5 | Completed |
| REQ-007 | Cognitive Orchestration Engine Documentation Synchronization (03) | Step 6 | Completed |
| REQ-008 | Data Seeding & Ontology Documentation Synchronization (02) | Step 6 | Completed |
| REQ-009 | SDUI and Presentation Documentation Synchronization (04) | Step 6 | Completed |
| REQ-010 | Enriched Atom Graph Documentation Synchronization (06) | Step 6 | Completed |
| REQ-011 | Seed Vault In-Memory Audit and Atomic Reseed Synchronization | Step 7 | Completed |
| REQ-012 | Universal Quality Gates and Architectural Markdown Boundary Verification | Step 8 | Completed |

# Session Handover Context
## Achieved
- Step 1: Preflight backup created (`backend_v2/seed/backups/seed_data_backup_dual_track.json`), dry-run seeder verified (0 errors), and strict atom linter verified (14 matrices, 345 TDA atoms).
- Step 2: Refactored `backend_v2/seed/seed_data.json` via sanitized script with `TrackAConfig` and `ClaimUpdateConfig` typed models. Track A (6 matrices) Level 1 renamed to Novice with positive baseline capabilities (`inverse_evidence: false`). Track B (8 diagnostic matrices) Levels 1-2 locked to pure error radars (`inverse_evidence: true`, `aggregation_mode: EXISTS`). Preserved all 345 TDA atoms across the 14-matrix ontology without destructive pruning.
- Step 3: Expanded scoring unit and property tests. Added `test_dreyfus_cumulative_novice_scoring` and `test_dreyfus_expert_satisfies_novice_invariant` in `test_unified_engine.py`. Added `test_toulmin_error_radar_clean_baseline` and `test_toulmin_fatal_flaw_penalty_deduction` in `test_scoring.py`. Universal Quality Gate passed 100% with 98.13% coverage. Atomic commit `43d3f4045`.
- Step 4: Synchronized SSOT Knowledge Items:
  - `ki_unified_matrix_scoring_strictness.md`: Section 5 added with mathematical hit ratios, Guttman cumulative progression, Inverted Rubric Paradox prohibition, and global score aggregation formula.
  - `ki_prompt_orchestration_and_matrix_evaluation.md`: Added `dual_track_rubric_polarity_mandate` and Parameter 12 dichotomy.
- Step 5: Updated architecture compendium `docs/architecture/08_matrix_explanations.md`:
  - Section 2: Added `Rubric Track` column and incorporated `matrix_hacm` across all 14 matrices.
  - Sections 3.2, 3.4, 3.6, 3.7, 3.8: Updated BARS Level 1 descriptions to match refactored seed vault definitions.
  - Section 3.14: Added Human-AI Collaboration Matrix (HACM).
  - Section 8.4: Expanded mathematical bottom-up scoring documentation (weighted ratios, piecewise exponent curve, per-matrix normalization, multi-matrix global score aggregation).
  - Excised orphaned duplicate Toulmin snippet.
- Step 6: Synchronized architecture pillars:
  - `docs/architecture/03_cognitive_orchestration_engine.md`: Updated Sections 2.19, 2.20 and added Section 2.22 ('Commensurate Multi-Matrix Global Score Aggregation').
  - `docs/architecture/02_data_seeding_and_ontology.md`: Documented 14 canonical matrices and added Section 2.14 ('Dual-Track Matrix Schema & TDA Assertion Polarity Standards').
  - `docs/architecture/04_server_driven_ui_and_presentation.md`: Added Section 2.13 ('Cross-Surface Presentation Parity & Machine-Readability Standard') covering Tab 1, Tab 2, Excel Tab 1, and 22-column rectangular CSV streaming. Fixed ambiguous language tokens and client DTO definitions.
  - `docs/architecture/06_enriched_atom_graph_engine.md`: Added Section 2.14 ('Decoupling of Evaluative Matrix TDA Atoms and Dynamic Causal Graph Propositions'). Fixed ambiguous language tokens.
- Step 7: Completed two-phase seed vault pre-flight in-memory validation and atomic reseed:
  - `backend_v2/seed/run_seed.py local --dry-run` passed cleanly.
  - `scripts/audit_database_atoms.py --strict` passed cleanly (14 matrices, 345 atoms, 0 errors).
  - `backend_v2/seed/run_seed.py local` executed and reseeded local database (`data/db_v2.json`) cleanly.
- Step 8: Universal Quality Gates executed:
  - `scripts/backend_audit_loop.py backend_v2 --test --ast-strict`: 5,322 passed, 0 failed, 97.75% coverage, all 10 AST and typing gates passed cleanly.
  - `scripts/audit_markdown_boundaries.py`: 100% pass (EXIT CODE 0) across all 5 modified architecture documents.

## Learned
- Inverted Rubric Paradox is permanently solved: Track A developmental matrices measure presence of capability from Level 1 up, while Track B diagnostic matrices act as error radars on Levels 1-2 without awarding positive baseline capability points.
- The Monotonic Ratchet ledger (`audit_warning_baseline.py`) and AST Dict Eradication Auditor strictly enforce typed Pydantic models (specifically `I18nText`) over nested primitive dictionaries (`dict[str, dict[str, str]]`) even in seed migration scripts.
- Preserving non-pruning claim mutations ensures all 345 atoms across the 14-matrix ontology maintain referential integrity with upstream workflow provenance and telemetry assertions.

## Remaining
- Step 9: Final Plan Audit (`/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]`).

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]
```
