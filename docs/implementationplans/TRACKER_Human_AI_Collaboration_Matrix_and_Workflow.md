# Tracker: Human-AI Collaboration Matrix (HACM) Seed, Dedicated Workflow & Custom Output Profile

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

- [ ] **Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]`
  - [ ] Step 1: Pre-flight backup of `seed_data.json` and in-memory schema dry-run verification
  - [ ] Step 2: Define `PromptBlock` (MatrixModel `HACM`, `blk_7d8e9f0a1b2c3d4e`) in `backend_v2/seed/seed_data.json` with 25 TDA assertions (12 positive, 13 negative, `target_speaker: USER`) restoring the 5 user role archetypes (Matkustaja, Reaktiivinen viilaaja, Navigaattori, Kuljettaja, Arkkitehti)
  - [ ] Step 2b: Update Causal Analyst matrix (`blk_c5804a9143c34cb1`) in `backend_v2/seed/seed_data.json` with `is_evaluative: true`
  - [ ] Step 3: Define HACM specialist step blueprint (`sp_06c1d71000000001`) with HACM criteria and dynamic expected inputs
  - [ ] Step 3b: Define Dynamic Causal Discovery step blueprint (`sp_06b1d7100000ca06`) for proposition mining, directed dependencies, and fault chain attribution
  - [ ] Step 4: Define dedicated assessment workflow (`wf_06a1d71000000001`) with dynamic topology agnosticism and 7-step Tripartite Zone B DAG
  - [ ] Step 5: Define dedicated custom output profile (`prf_06b1d71000000001`) with enhanced synthesis directives (Executive Summary, Row Explanations, 2D/3D Radar, Variance, XAI max 4 items), radar groups, and SDUI hierarchy with causal action card; update all existing output profiles to configure `user_role_target_block` and `user_role_label`
  - [ ] Step 5b: Restore `RoleClassification` Enum SSOT resolution in `ExecutiveSummaryAdapter` (`executive_summary_adapter.py`) and expand unit tests (`test_executive_summary_adapter.py`) to guarantee deterministic role rendering across all output profiles
  - [ ] Step 6: Execute database atom audit (`audit_database_atoms.py`) and synchronize to local database (`run_seed.py local`)
  - [ ] Step 7: Execute end-to-end quality gate verification (`backend_audit_loop.py` and `audit_markdown_boundaries.py`)
- [ ] **Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]`

### Post-Implementation Gates
- [ ] **Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [ ] @[backend_v2/seed/seed_data.json]
  - [ ] @[backend_v2/services/sdui/adapters/executive_summary_adapter.py]
  - [ ] @[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]
- [ ] **Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **Database & Atom Integrity Audit**: Verify `uv run python scripts/audit_database_atoms.py --strict` passes with 0 findings.

### Documentation & Knowledge Item Update
- [ ] As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[ki_prompt_orchestration_and_matrix_evaluation.md] @[ki_workflow_context_governance.md]
  ```

### Final Plan Audit
- [ ] System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
1. Load all required context rules declared in `<required_context_rules>` block at top of file.
2. Execute each step sequentially via `/tier2-execute`.
3. Do not modify any source code files outside declarative seed assets in `@[backend_v2/seed/seed_data.json]`.
4. Ensure continuous atomic checkpoints after successful quality gate validation.
