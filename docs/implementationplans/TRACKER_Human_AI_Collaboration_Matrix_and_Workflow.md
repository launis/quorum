# Tracker: Human-AI Collaboration Matrix (HACM) Seed, Dedicated Workflow & Custom Output Profile

@[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]`
  - [ ] Step 1: Pre-flight backup of seed_data.json and in-memory schema dry-run verification
  - [ ] Step 2: Define PromptBlock (MatrixModel HACM, blk_7d8e9f0a1b2c3d4e) in backend_v2/seed/seed_data.json with 25 TDA assertions (12 positive, 13 negative, target_speaker: USER) restoring the 5 user role archetypes (Matkustaja, Reaktiivinen viilaaja, Navigaattori, Kuljettaja, Arkkitehti)
  - [ ] Step 2b: Update Causal Analyst matrix (blk_c5804a9143c34cb1) in backend_v2/seed/seed_data.json with is_evaluative: true
  - [ ] Step 3: Define HACM specialist step blueprint (sp_06c1d71000000001) with HACM criteria, engine_type: "tda", and dynamic expected inputs
  - [ ] Step 3b: Define Dynamic Causal Discovery step blueprint (sp_06b1d7100000ca06) for proposition mining, directed dependencies, and fault chain attribution
  - [ ] Step 4: Define dedicated assessment workflow (wf_06a1d71000000001) with dynamic topology agnosticism and 7-step Tripartite Zone B DAG
  - [ ] Step 5: Define dedicated custom output profile (prf_06b1d71000000001) with enhanced synthesis directives (Executive Summary, Row Explanations, 2D/3D Radar, Variance, XAI max 4 items), radar groups, and SDUI hierarchy with causal action card
  - [ ] Step 6: Execute database atom audit (audit_database_atoms.py) and synchronize to local database (run_seed.py local)
  - [ ] Step 7: Execute end-to-end quality gate verification (backend_audit_loop.py and audit_markdown_boundaries.py)
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend `.py` files. (No production .py files modified - pure declarative seed vault asset)
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter `.dart` files. (No production .dart files modified - pure declarative seed vault asset)
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.
- [ ] **[NOK] Database & Atom Integrity Audit**: Verify `uv run python scripts/audit_database_atoms.py --strict` passes with 0 findings.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[ki_prompt_orchestration_and_matrix_evaluation.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_zero_permissive_typing.md] @[ki_god_code_prevention.md] @[ki_workflow_context_governance.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_prompt_orchestration_and_matrix_evaluation.md]`: Document the Human-AI Collaboration Matrix (HACM, `blk_7d8e9f0a1b2c3d4e`) BARS scale architecture with exact 50/50 balance (12 positive capabilities, 13 negative error detectors), strict `TargetSpeaker.USER` evidentiary quarantine, and the 5 restored user role archetypes (Matkustaja, Reaktiivinen viilaaja, Navigaattori, Kuljettaja, Arkkitehti).
     - `@[ki_workflow_context_governance.md]`: Document dedicated assessment workflow `wf_06a1d71000000001` with dynamic document topology agnosticism, 7-step Tripartite Zone B DAG, and parallel peer specialist execution (HACM Evaluator, Evaluative Causal Analyst `blk_c5804a9143c34cb1`, and Dynamic Causal Discovery `sp_06b1d7100000ca06`).
     - `@[ki_unified_matrix_scoring_strictness.md]`: Document peer evaluative specialist matrix averaging in `apply_scoring_logic_hook` where both HACM and Causal Analyst matrices configure `is_evaluative: true` and average 50/50 into the unpenalized global score at continuous 50% strictness.
     - `@[ki_zero_permissive_typing.md]`: Document pure declarative data asset governance in `backend_v2/seed/seed_data.json` without ad-hoc dictionary passing or fallback shims, preserving `ExecutiveSummaryAdapter` native scale derivation without modifying code.
     - `@[ki_god_code_prevention.md]`: Document the quarantine of `ExecutiveSummaryAdapter` and avoidance of redundant helper abstractions by leveraging native `target_matrix.level_names[int_key]` mapping.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to verify that all new workflow, step, prompt block, and output profile entities are referenced and cataloged.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/01_system_context_and_invariants.md`, `docs/architecture/02_matrix_tda_pipeline.md`, and `docs/architecture/04_sdui_frontend_presentation.md` describing HACM human steering audit capabilities, peer evaluative specialist scoring, and native archetype badge derivation in present tense without historical language or plan IDs.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Strict Execution Mode**: Do not modify domain files without slash command invocation `/tier2-execute`.
- **Pure Seed Vault Scope**: All physical data mutations occur strictly in `@[backend_v2/seed/seed_data.json]`. Source code files (`.py`, `.dart`) are strictly read-only and quarantined.
- **Quality Gates**: After each logical step, run `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`.
- **Atomic Commits**: Run atomic git commits with Conventional Commits syntax following successful quality gate runs.
- **Double-Entry Bookkeeping**: Mark each completed step with `[x]` in this tracker and keep `# Session Handover Context` synchronized.

## Requirements Traceability Matrix
| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Pre-flight backup of seed_data.json and in-memory schema dry-run validation | Step 1 | Pending |
| REQ-002 | Define PromptBlock (MatrixModel HACM, blk_7d8e9f0a1b2c3d4e) in seed_data.json with 25 TDA assertions | Step 2 | Pending |
| REQ-003 | Update Causal Analyst matrix (blk_c5804a9143c34cb1) in seed_data.json with is_evaluative: true | Step 2b | Pending |
| REQ-004 | Define HACM specialist task blueprint (sp_06c1d71000000001) with engine_type: "tda" | Step 3 | Pending |
| REQ-005 | Define Dynamic Causal Discovery task blueprint (sp_06b1d7100000ca06) for proposition and dependency mining | Step 3b | Pending |
| REQ-006 | Define dedicated assessment workflow (wf_06a1d71000000001) with 7-stage Tripartite Zone B DAG | Step 4 | Pending |
| REQ-007 | Define dedicated custom output profile (prf_06b1d71000000001) with enhanced synthesis directives | Step 5 | Pending |
| REQ-008 | Execute database atom audit (audit_database_atoms.py) and sync to local database (run_seed.py local) | Step 6 | Pending |
| REQ-009 | Execute end-to-end quality gate verification (backend_audit_loop.py and audit_markdown_boundaries.py) | Step 7 | Pending |

# Session Handover Context
## Achieved
- Completed Tier 0 deep System 2 research, red-teaming, and architectural hardening of `@[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md]`.
- Verified that `ExecutiveSummaryAdapter.build` natively derives user role archetype badges via `target_matrix.level_names[int_key]`, completely eliminating the need for Python code modifications or fallback shims.
- Pruned unauthorized mutations of output profiles 4 and 5 to prevent orphan references to unmapped matrices.
- Hardened step blueprint `sp_06c1d71000000001` to declare `engine_type: "tda"`.
- Synchronized standalone execution tracker for full-duplex step tracking and double-entry bookkeeping.

## Learned
- Dynamic Causal Discovery steps in Zone B DAGs must declare `expected_sdui_type: null` and `is_synthesis_source: false`, while downstream synthesis steps bind `causal_source_step_id: "sr_06s1000000000004"` to satisfy `validate_step_rule_consistency()`.
- Production output profiles legitimately omit the user role badge when their workflows do not evaluate human steering agency; hardcoding disconnected block IDs onto unrelated profiles violates domain sovereignty.

## Remaining
- Step 1: Pre-flight backup of `seed_data.json` and in-memory dry-run validation.
- Step 2: Define `blk_7d8e9f0a1b2c3d4e` (HACM PromptBlock with 25 TDA assertions) in `seed_data.json`.
- Step 2b: Update `blk_c5804a9143c34cb1` (Causal Analyst) with `is_evaluative: true` in `seed_data.json`.
- Step 3: Define `sp_06c1d71000000001` (HACM Evaluator Step Blueprint) with `engine_type: "tda"`.
- Step 3b: Define `sp_06b1d7100000ca06` (Dynamic Causal Discovery Step Blueprint).
- Step 4: Define `wf_06a1d71000000001` (Dedicated Assessment Workflow).
- Step 5: Define `prf_06b1d71000000001` (Dedicated Custom Output Profile).
- Step 6: Execute atom structural audit and database synchronization via `run_seed.py local`.
- Step 7: Execute full backend audit loop and markdown boundary checks.

## Resume Command
```bash
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]
```
