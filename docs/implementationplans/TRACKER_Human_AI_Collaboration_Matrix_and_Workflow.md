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
  - [ ] Step 2: Define `PromptBlock` (MatrixModel `HACM`, `blk_7d8e9f0a1b2c3d4e`) in `backend_v2/seed/seed_data.json` with 25 TDA assertions (12 positive, 13 negative, `target_speaker: USER`)
  - [ ] Step 3: Define specialist step blueprint (`sp_06c1d71000000001`) with HACM criteria and dynamic expected inputs
  - [ ] Step 4: Define dedicated assessment workflow (`wf_06a1d71000000001`) with dynamic topology agnosticism and 3-Zone step DAG
  - [ ] Step 5: Define dedicated custom output profile (`prf_06b1d71000000001`) with tailored preface, radar groups, and SDUI hierarchy
  - [ ] Step 6: Execute database atom audit (`audit_database_atoms.py`) and synchronize to local database (`run_seed.py local`)
  - [ ] Step 7: Execute end-to-end quality gate verification (`backend_audit_loop.py` and `audit_markdown_boundaries.py`)
- [ ] **Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md] @[docs/implementationplans/TRACKER_Human_AI_Collaboration_Matrix_and_Workflow.md]`

### Post-Implementation Gates
- [ ] **Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [ ] @[backend_v2/seed/seed_data.json]
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
