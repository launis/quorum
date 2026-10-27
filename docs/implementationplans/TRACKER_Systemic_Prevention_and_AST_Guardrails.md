# Tracker: Systemic Prevention, AST Guardrail QGR030 & Test Fixture Fortification

@[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md] @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`
  - [x] Step 1: Phase 1: Pre-Implementation Cleanups (Touched-Scope Technical Debt & Legacy Backend References)
  - [x] Step 2: Phase 2: Implement AST Guardrail QGR030 & Self-Verifying Exemption Lists (Improvements 1, 2, & 3)
  - [x] Step 3: Phase 3: First-Class Scripts Quality Gate & Zero-ORM Strictness Integration (Improvement 4)
  - [x] Step 4: Phase 4: Hermetic Test Fixtures & Pre-Flight Metatest Mapping Mandate (Improvements 1, 2, & 3)
  - [x] Step 5: Phase 5: Polyfactory SSOT & Hexadecimal ID Generation Expansion (Improvement 4)
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md] @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]" --gate backend --model gemini-4-argon-medium`.
  - [ ] @[backend_v2/database/driver.py]
  - [ ] @[backend_v2/database/factory.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter.py]
  - [ ] @[backend_v2/database/postgres/pool.py]
  - [ ] @[backend_v2/database/postgres/storage_driver.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/storage.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/reconcile_storage.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[backend_v2/tests/factories/model_factories.py]
  - [ ] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]" --gate frontend --model gemini-4-argon-medium`. (Zero frontend `.dart` production targets in this plan).
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_python_314_concurrency_strictness.md] @[ki_seed_vault_verification_and_sanitization.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the `QGR030` (`FATAL`) AST guardrail in `@[scripts/_ast_guardrails.py]` banning deprecated storage backend references (`LOCAL`, `FIRESTORE`) in function calls and attribute access alongside non-hexadecimal mock entity ID literals, the automated disk existence verification across all guardrail exemption sets (`BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, `RESIDUAL_FUTURE_PHASE_QGR028_FILES`) in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, the inclusion of operational and guardrail scripts in `@[scripts/backend_audit_loop.py]` and `@[scripts/audit_zero_orm_strictness.py]`, and the `preflight_metatest_and_exemption_mapping_mandate` in `@[.agents/workflows/tier0-research-plan.md]`.
     - `@[ki_zero_permissive_typing.md]`: Document the `ZORM001`–`ZORM006` Zero-ORM strictness enforcement extended to `@[scripts/reconcile_storage.py]` via `@[scripts/audit_zero_orm_strictness.py]`, the `QGR030` canonical hexadecimal Opaque Stripe ID regex enforcement (`^([a-z]{2,5})_[a-fA-F0-9]{16,32}$`) on mock ID string literals, and the Polyfactory SSOT expansion in `@[backend_v2/tests/factories/model_factories.py]` (`WorkflowFactory`, `SystemRulePromptBlockFactory`, `OutputProfileFactory`, `MatrixPromptBlockFactory`, `ExecutionStepFactory`, `ExecutionRecordFactory`, and `ReportArtifactFactory`) routing all IDs exclusively through `generate_opaque_id(EntityPrefix.<TYPE>)`.
     - `@[ki_python_314_concurrency_strictness.md]`: Document the `hermetic_test_fixtures_mandate` in `@[.agents/rules/01-python-backend.md]` and `zero_compromise_cutover_mandate` in `@[.agents/rules/00-antigravity-core.md]`, the removal of dead `StorageBackend.FIRESTORE` and `StorageBackend.LOCAL` branches in `Settings.is_cloud_storage` and `Settings.allow_mock_tokens` in `@[backend_v2/settings.py]`, and the hermetic `Settings()` instantiation across LLM provider unit tests without legacy storage backend overrides.
     - `@[ki_seed_vault_verification_and_sanitization.md]`: Document the alignment between authoritative PostgreSQL 19 seed entity prefixes (`EntityPrefix.WORKFLOW`, `EntityPrefix.OUTPUT_PROFILE`, `EntityPrefix.PROMPT_BLOCK`, `EntityPrefix.STEP`, `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.ORGANIZATION`), Polyfactory test fixtures in `@[backend_v2/tests/factories/model_factories.py]`, and static AST guardrail `QGR030` verification.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect `ReportArtifactFactory` in `backend_v2/tests/factories/model_factories.py`, `QGR030` enforcement in `scripts/_ast_guardrails.py`, and first-class operational script auditing in `scripts/backend_audit_loop.py` and `scripts/audit_zero_orm_strictness.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (specifically and exhaustively: `01_system_context_and_invariants.md`, `02_data_seeding_and_ontology.md`, and `05_resilience_and_observability.md`) describing the `QGR030` static AST guardrail, self-verifying boundary exemption sets, first-class operational script auditing, and hermetic Polyfactory ID authority in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md] @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors. (PASSED: 6,146 passed tests, 96.86% line coverage, 0 fatal or advisory AST violations).

## Instructions for the Execution Agent

1. **Execution Mode**:
   - **Step-by-Step Mode** (`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md] @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`): Execute a single unchecked step, run all step-level quality gates, update this tracker (`[x]`) and the `# Session Handover Context`, instruct the user to perform an atomic `git commit`, and STOP.
   - **Continuous Full-Auto Mode** (`/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md] @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`): Proceed autonomously across all steps in sequence as long as quality gates pass 100%, halting immediately if any quality gate fails or when `context_amnesia_prevention` handover thresholds are reached.
2. **Quality Gate Mandate**:
   - After modifying any `.py` file, run `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` and `uv run python scripts/audit_zero_orm_strictness.py`.
   - Before closing the final step, run the global completion gates: `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.
3. **Atomic Commit Mandate**:
   - Provide an atomic `git commit` instruction using strict Conventional Commits syntax (`<type>(<scope>): <imperative summary in lowercase, max 72 chars, no trailing period>`) with explicit `git add` file paths and a concise, factual bulleted list of physical changes.
4. **Workspace Path Normalization**:
   - Exclusively use workspace-relative `@[...]` paths across all documentation, trackers, and handover blocks.
5. **Post-Implementation Hardening Execution Options**:
   - Run interactive file-by-file hardening in chat via `/tier2-hardening-backend @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]`, OR
   - Run autonomous unattended CLI hardening via `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]" --gate backend --model gemini-4-argon-medium`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Remove dead comparisons to `StorageBackend.FIRESTORE` and `StorageBackend.LOCAL` in `@[backend_v2/settings.py#L803-L811]` (`is_cloud_storage`) and `@[backend_v2/settings.py#L983-L1000]` (`allow_mock_tokens`) so `is_cloud_storage` returns `bool(self.storage_bucket_name)` and `allow_mock_tokens` evaluates `self.active_backend != StorageBackend.POSTGRES`. | Step 1 | `[x]` |
| **REQ-002** | Remove deprecated `storage_backend="LOCAL"` keyword arguments from `Settings(...)` instantiations across `@[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L108-L150]`, `@[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L153-L246]`, `@[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L291-L358]`, `@[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L83-L126]`, `@[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L267-L362]`, `@[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L19-L49]`, `@[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L52-L182]`, `@[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L185-L280]`, `@[backend_v2/tests/unit/test_epic66_multi_provider.py#L23-L37]`, and `@[backend_v2/tests/unit/test_epic66_multi_provider.py#L40-L54]`. | Step 1 | `[x]` |
| **REQ-003** | Replace non-hexadecimal test directory identifiers `"exe_test1234567890"` and `"exe_sdui1234567890"` in `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L292-L312]` and `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L315-L337]` with canonical 16-character hexadecimal IDs `"exe_1111222233334444"` and `"exe_5555666677778888"`, and ensure ISTQB negative test partitions (`test_*_invalid`, `test_*_error`) are present in both `test_reconcile_storage.py` and `test_epic66_multi_provider.py`. | Step 1 | `[x]` |
| **REQ-004** | Implement `QGR030` (`FATAL`) in `QuorumGuardrailVisitor` (`visit_Call` and `visit_Attribute`, exempting `self.is_guardrail_self`) inside `@[scripts/_ast_guardrails.py#L528-L2646]` to ban `storage_backend="LOCAL"`, `storage_backend="FIRESTORE"`, `StorageBackend.LOCAL`, and `StorageBackend.FIRESTORE` outside `backend_v2/models/enums.py`. | Step 2 | `[x]` |
| **REQ-005** | Expand `QGR030` (`FATAL`) in `QuorumGuardrailVisitor.visit_Constant` inside `@[scripts/_ast_guardrails.py#L528-L2646]` to flag string literals matching `^([a-z]{2,5})_[a-zA-Z0-9]{14,32}$` for canonical entity prefixes (`exe`, `rep`, `tda`, `wf`, `stp`, `prf`, `blk`, `sys`, `usr`, `org`, `nod`, `edg`) where the 14-to-32 character suffix mixes digits (`[0-9]`) with non-hexadecimal letters (`[g-zG-Z]`). | Step 2 | `[x]` |
| **REQ-006** | Add deterministic self-verification tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1924-L1934]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]` iterating `BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` to assert physical disk existence, alongside unit tests for `QGR030` covering >=2 positive violation detections and >=2 negative boundary cases. | Step 2 | `[x]` |
| **REQ-007** | Update `@[scripts/backend_audit_loop.py#L85-L379]` and `@[scripts/backend_audit_loop.py#L382-L628]` so the macro completion gate (`backend_audit_loop.py backend_v2/ --test`) audits authoritative operational and guardrail scripts in `scripts/` (specifically and exhaustively: `scripts/reconcile_storage.py`, `scripts/_ast_guardrails.py`, `scripts/audit_zero_orm_strictness.py`, `scripts/backend_audit_loop.py`, `scripts/audit_markdown_boundaries.py`, `scripts/audit_dict_eradication.py`, `scripts/audit_technical_debt.py`, and `scripts/_ast_boundary_utils.py`) across Ruff, MyPy `--strict`, and AST Guardrail checks, and invokes `scripts/audit_zero_orm_strictness.py`. | Step 3 | `[x]` |
| **REQ-008** | Update `run_zero_orm_audit` in `@[scripts/audit_zero_orm_strictness.py#L582-L636]` to include `_WORKSPACE_ROOT / "scripts" / "reconcile_storage.py"` in default `resolved_targets` so `ZORM001`–`ZORM006` are enforced on `scripts/reconcile_storage.py`. | Step 3 | `[x]` |
| **REQ-009** | Codify `hermetic_test_fixtures_mandate` in `@[.agents/rules/01-python-backend.md#L10-L60]`, `zero_compromise_cutover_mandate` in `@[.agents/rules/00-antigravity-core.md#L87-L105]`, and `preflight_metatest_and_exemption_mapping_mandate` in `@[.agents/workflows/tier0-research-plan.md#L50-L53]`. | Step 4 | `[x]` |
| **REQ-010** | Update `@[backend_v2/tests/factories/model_factories.py#L84-L133]` (`WorkflowFactory`), `@[backend_v2/tests/factories/model_factories.py#L136-L177]` (`SystemRulePromptBlockFactory`), `@[backend_v2/tests/factories/model_factories.py#L180-L246]` (`OutputProfileFactory`), `@[backend_v2/tests/factories/model_factories.py#L249-L313]` (`MatrixPromptBlockFactory`), `@[backend_v2/tests/factories/model_factories.py#L316-L340]` (`ExecutionStepFactory`), and `@[backend_v2/tests/factories/model_factories.py#L343-L426]` (`ExecutionRecordFactory`), and add `ReportArtifactFactory` (`ReportArtifact`) so all factories generate canonical hexadecimal Opaque Stripe IDs via `generate_opaque_id(EntityPrefix.<TYPE>)`. | Step 5 | `[x]` |
| **REQ-011** | Update `@[backend_v2/tests/factories/test_model_factories.py#L46-L59]` to register `ReportArtifactFactory` in `ALL_FACTORIES`, assert `OPAQUE_STRIPE_ID_REGEX` compliance across all generated IDs, and add >=2 ISTQB negative validation boundary tests (`test_polyfactory_invalid_id_error`, `test_polyfactory_invalid_extra_field_error`). | Step 5 | `[x]` |

# Session Handover Context

## Achieved
- Completed and committed all 5 execution steps (`REQ-001` through `REQ-011`) of `@[docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md]`:
  - Step 1 (`d6dced55c`): Removed dead `StorageBackend.FIRESTORE` and `StorageBackend.LOCAL` branches in `@[backend_v2/settings.py]`, removed `storage_backend="LOCAL"` overrides across LLM provider unit tests, and enforced canonical 16-char hexadecimal IDs in `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py]`.
  - Step 2 (`b76ef43b4`): Implemented `QGR030` (`FATAL`) in `@[scripts/_ast_guardrails.py]` (`QuorumGuardrailVisitor.visit_Call`, `visit_Attribute`, and `visit_Constant`) and added disk-existence self-verification across all 4 exemption sets in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`.
  - Step 3 (`458163ca4`): Expanded `@[scripts/backend_audit_loop.py]` macro completion gate to audit authoritative operational and guardrail scripts and invoke `@[scripts/audit_zero_orm_strictness.py]`, and added `@[scripts/reconcile_storage.py]` to default `run_zero_orm_audit` targets.
  - Step 4 (`335d0c28a`): Codified `hermetic_test_fixtures_mandate` in `@[.agents/rules/01-python-backend.md]`, `zero_compromise_cutover_mandate` in `@[.agents/rules/00-antigravity-core.md]`, and `preflight_metatest_and_exemption_mapping_mandate` in `@[.agents/workflows/tier0-research-plan.md]`.
  - Step 5 (`84fb17755`): Updated Polyfactory models in `@[backend_v2/tests/factories/model_factories.py]` (`WorkflowFactory`, `SystemRulePromptBlockFactory`, `OutputProfileFactory`, `MatrixPromptBlockFactory`, `ExecutionStepFactory`, `ExecutionRecordFactory`), added `ReportArtifactFactory`, and verified `OPAQUE_STRIPE_ID_REGEX` compliance and ISTQB negative boundary cases in `@[backend_v2/tests/factories/test_model_factories.py]`.
- Updated `@[.agents/rules/04_directory_reference.md]` and synchronized AST line boundaries across both the implementation plan and this tracker.
- Completed `/tier8-audit-plan` (`PASSED` with 0 findings: 6,146 passed tests, 96.86% total line coverage, 0 `QGR001`–`QGR030` violations, 0 `ZORM001`–`ZORM006` violations, 0 technical debt findings across 17 targets and 65 1-hop callers).

## Learned
- `CausalGraphPayloadDTOFactory` requires deterministic empty defaults for `partition_node_ids` and `edge_root_causes` so `CausalGraphPayloadDTO.validate_referential_integrity` succeeds on default `.build()` calls.
- Resolving sibling `test_<filename>` modules in `@[scripts/backend_audit_loop.py]` (`run_tests_with_strict_coverage`) enables direct coverage verification when targeting non-test modules under `backend_v2/tests/factories/`.

## Remaining
- Execute `### Post-Implementation Gates` (`Tier 2 Hardening (Backend)`).
- Execute `### Documentation & Knowledge Item Update` (`/tier7-describe-architecture`).

## Resume Command
```powershell
/tier5-resume --target="@[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]" --workflow=/tier2-hardening-backend
```
