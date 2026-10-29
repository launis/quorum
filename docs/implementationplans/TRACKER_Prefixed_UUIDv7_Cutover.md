# Tracker: Universal PrefixedUUID7 Cutover (Model A), Studio Default Anchor Eradication & Topological Graph Mathematics Synchronization

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md] @[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]`
  - [ ] Step 1: Phase 1: Pre-Implementation Technical Debt Cleanups & Core PrefixedUUID7 SSOT Lock
  - [ ] Step 2: Phase 2: Deterministic seed_data.json 32-Hex UUIDv7 Cutover & sanitize_seed_vault.py Auto-ID Generator
  - [ ] Step 3: Phase 3: PostgreSQL 19 12-Table Native UUIDv7 DDL & Symmetric Adapter Bridge
  - [ ] Step 4: Phase 4: Studio Draft Anchor Eradication & Direct Causal Cohesion Matrix Binding
  - [ ] Step 5: Phase 5: Topological Graph Mathematics Synchronization, Counterfactual Simulation & Full-Duplex Parity
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md] @[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure`.
  - [ ] @[backend_v2/database/postgres/entity_adapter.py]
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/models/domain/step.py]
  - [ ] @[backend_v2/models/domain/workflow.py]
  - [ ] @[backend_v2/models/dtos/causal_discovery.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/sanitize_seed_vault.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure`.
  - [ ] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_python_314_concurrency_strictness.md] @[ki_seed_vault_verification_and_sanitization.md] @[ki_sdui_matrix_synthesis.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_seed_vault_verification_and_sanitization.md]`: Document the universal 32-hex RFC 9562 `PrefixedUUID7` (`{prefix}_{32_hex}`) standard across all 12 PostgreSQL 19 tables, `EntityPrefix.SCALE` (`sc_`), and the automatic missing-ID generator in `scripts/sanitize_seed_vault.py`.
     - `@[ki_sdui_matrix_synthesis.md]`: Document the direct binding of the BARS causal cohesion matrix to `Step.criteria_block_ids` on `StepType.CAUSAL_DISCOVERY`, the 0-token topological metrics ($r_{\text{LCC}}$, $r_{\text{conv}}$, $\kappa_{\text{steer}}$) in `AntiFluffAuditDTO`, and `simulate_counterfactual_retraction` in `CausalCohesionEvaluator`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect `CounterfactualSimulationResultDTO` in `backend_v2/models/dtos/causal_discovery.py` and the unified 12-table `UUIDv7` schema in `001_pg19_uuidv7_schema.sql`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the 12-table native PostgreSQL 19 `UUIDv7` schema and topological graph mathematics in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md] @[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/settings.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Eliminate `TD_DICT_GET` permissive `.get()` calls on lines 467, 473, and 593 of `@[scripts/sanitize_seed_vault.py#L445-L548]` and `@[scripts/sanitize_seed_vault.py#L577-L606]`. | Step 1 | [ ] Pending |
| REQ-002 | Add `SCALE = "sc"` to `EntityPrefix` in `@[backend_v2/models/enums.py#L228-L244]` and update `SystemConfigID.MCP_GATEWAYS` to a 32-hex RFC 9562 `UUIDv7` in `@[backend_v2/models/enums.py#L283-L286]`. | Step 1 | [ ] Pending |
| REQ-003 | Lock `OPAQUE_STRIPE_ID_REGEX = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"` and route `generate_opaque_id(prefix)` unconditionally to `generate_uuid7_opaque_id(prefix)` in `@[backend_v2/models/core_base.py#L199-L229]`. | Step 1 | [ ] Pending |
| REQ-004 | Deterministically migrate all entity IDs and relational foreign keys in `@[backend_v2/seed/seed_data.json#L1-L22793]` to 32-hex RFC 9562 `UUIDv7` (`{prefix}_{32_hex}`) and normalize `wor_` workflow prefixes to `wf_`. | Step 2 | [ ] Pending |
| REQ-005 | Extend `@[scripts/sanitize_seed_vault.py#L445-L548]` and `@[scripts/sanitize_seed_vault.py#L635-L692]` to auto-generate canonical 32-hex `UUIDv7` IDs via `generate_uuid7_opaque_id()` for any new row, scale, or `TDAAssertion` missing a valid ID and persist it atomically to `@[backend_v2/seed/seed_data.json#L1-L22793]`. | Step 2 | [ ] Pending |
| REQ-006 | Upgrade tables 1–7 (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) and all cross-table foreign keys in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L308]` to native PostgreSQL 19 `UUID` columns with `DEFAULT uuidv7()`, `VIRTUAL` timestamp extraction, and `CHECK (uuid_extract_version(...) = 7)`. | Step 3 | [ ] Pending |
| REQ-007 | Standardize `@[backend_v2/database/postgres/entity_adapter.py#L828-L2366]` to apply symmetric `parse_prefixed_uuid7()` and `format_prefixed_uuid7()` conversion across all 12 tables and enforce via `@[scripts/audit_zero_orm_strictness.py#L550-L579]`. | Step 3 | [ ] Pending |
| REQ-008 | Replace hardcoded `"blk_440a5fef9331451b"` and `"prf_0000000000000000"` in `@[backend_v2/services/studio/workflow_service.py#L348-L390]` and `@[backend_v2/services/studio/workflow_service.py#L677-L729]` and `"sys_8172bda70c8641c5"` in `@[backend_v2/models/domain/workflow.py#L25-L217]` with dynamic repository lookups and `None` defaults. | Step 4 | [ ] Pending |
| REQ-009 | Bind the BARS causal cohesion matrix directly to `Step.criteria_block_ids` on `StepType.CAUSAL_DISCOVERY` in `@[backend_v2/models/domain/step.py#L125-L185]`, remove `causal_cohesion_block_id` from `@[backend_v2/models/domain/workflow.py#L194-L217]`, and read the step's hydrated matrix in `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L79-L123]`. | Step 4 | [ ] Pending |
| REQ-010 | Delete `causal_cohesion_matrix_block_id` from `@[backend_v2/settings.py#L47-L1087]` and remove `CAUSAL_COHESION_TDA_IDS` and `CAUSAL_COHESION_CLAIMS` from `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L80-L302]`. | Step 5 | [ ] Pending |
| REQ-011 | Add `largest_component_ratio`, `branch_convergence_ratio`, `steering_coupling_ratio`, and `[NEW]` `CounterfactualSimulationResultDTO` / `CounterfactualSimulationResultDto` to `@[backend_v2/models/dtos/causal_discovery.py#L208-L228]`, `@[backend_v2/models/dtos/causal_discovery.py#L305-L332]`, and `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart#L61-L78]`. | Step 5 | [ ] Pending |
| REQ-012 | Compute $r_{\text{LCC}}$, $r_{\text{conv}}$, and $\kappa_{\text{steer}}$ in `compute_causal_tda_fusion_result` (`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L64-L238]`). | Step 5 | [ ] Pending |
| REQ-013 | Configure Equation (13) Guttman tier thresholds (`causal_cohesion_l2_min_nodes` through `causal_cohesion_l4_convergence_min`) in `@[backend_v2/settings.py#L47-L1087]` and enforce them in `CausalCohesionEvaluator.evaluate_causal_cohesion` (`@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]`). | Step 5 | [ ] Pending |
| REQ-014 | Implement `simulate_counterfactual_retraction(graph, retracted_node_id, conjunctive)` per Algorithm 1 in `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L163-L302]`. | Step 5 | [ ] Pending |
| REQ-015 | Tighten `QGR030` in `@[scripts/_ast_guardrails.py#L2670-L2714]` to enforce 32-hex `{prefix}_{32_hex}` IDs across all test fixtures. | Step 5 | [ ] Pending |

# Session Handover Context

## Achieved
- Created `@[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md]` and `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]`.
- Verified AST symbol boundaries and executed `scripts/audit_technical_debt.py` across all Python targets (`Status: PASSED`).

## Learned
- All 14 entity prefixes (`org`, `usr`, `sys`, `blk`, `stp`, `sr`, `wf`, `prf`, `exe`, `rep`, `nod`, `edg`, `tda`, `sc`) are governed by `EntityPrefix` in `backend_v2/models/enums.py`.
- Binding the causal cohesion BARS matrix directly to `Step.criteria_block_ids` on `StepType.CAUSAL_DISCOVERY` eliminates the `causal_cohesion_matrix_block_id` setting and `CAUSAL_COHESION_TDA_IDS` / `CAUSAL_COHESION_CLAIMS` tuples completely.

## Remaining
- Execute Steps 1 through 5 via `/tier2-execute`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Prefixed_UUIDv7_Cutover.md] @[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]
```
