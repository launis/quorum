# Tracker: AST & Quality Gate Extensions (`QGR031` Query Filter Guard, Dynamic `scripts/*.py` Discovery & `QGR032` Polyfactory Invariant Guard)

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`
  - [ ] Step 1: Phase 1: AST Guardrail QGR031 (Static Query Filter Validation)
  - [ ] Step 2: Phase 2: Dynamic scripts/*.py Auto-Discovery in backend_audit_loop.py
  - [ ] Step 3: Phase 3: AST Guardrail QGR032 (Polyfactory 32-Hex UUIDv7 Invariant Guard & Meta-Tests)
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure`.
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/backend_audit_loop.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_python_314_concurrency_strictness.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document AST guardrails `QGR031` (static query filter validation) and `QGR032` (Polyfactory 32-hex `UUIDv7` invariant guard) as well as dynamic `scripts/*.py` scanning in `scripts/backend_audit_loop.py`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` so `_ast_guardrails.py` documents `QGR001-QGR032` and `backend_audit_loop.py` documents dynamic `scripts/*.py` discovery.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing `QGR031`, `QGR032`, and dynamic `scripts/*.py` quality gate scanning in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

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
| REQ-001 | Implement AST rule `QGR031` (`GuardrailSeverity.FATAL`) in `@[scripts/_ast_guardrails.py#L874-L1440]` validating `Filter(...)` and `QueryCondition(...)` calls for non-empty `field`, valid operator literals or `FilterOperator` enum attributes, and non-string collection targets on `"in"` filters. | Step 1 | [ ] Pending |
| REQ-002 | Add positive and negative unit tests for `QGR031` in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]`. | Step 1 | [ ] Pending |
| REQ-003 | Replace the static `_MACRO_AUTHORITATIVE_SCRIPTS` tuple in `@[scripts/backend_audit_loop.py#L430-L690]` with `discover_authoritative_scripts()` using `Path("scripts").glob("*.py")`. | Step 2 | [ ] Pending |
| REQ-004 | Verify that 100% of dynamically discovered `scripts/*.py` files pass Ruff, `mypy --strict`, and `scripts/_ast_guardrails.py` with zero errors. | Step 2 | [ ] Pending |
| REQ-005 | Implement AST rule `QGR032` (`GuardrailSeverity.FATAL`) in `@[scripts/_ast_guardrails.py#L1566-L1708]` enforcing that every `ModelFactory` subclass routes `id` and `*_id` fields via `Use(generate_opaque_id, EntityPrefix.<TYPE>)`. | Step 3 | [ ] Pending |
| REQ-006 | Audit `@[backend_v2/tests/factories/model_factories.py#L107-L188]` through `@[backend_v2/tests/factories/model_factories.py#L812-L897]` and expand `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]` to assert 100% `ModelFactory` registry completeness in `ALL_FACTORIES` and 32-hex `OPAQUE_STRIPE_ID_REGEX` compliance across all `id` and `*_id` fields, plus `QGR032` unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]`. | Step 3 | [ ] Pending |

# Session Handover Context

## Achieved
- Created `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` and `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`.
- Verified AST symbol boundaries and executed `scripts/audit_technical_debt.py` across all targets (`Status: PASSED`).

## Learned
- Replacing `_MACRO_AUTHORITATIVE_SCRIPTS` in `scripts/backend_audit_loop.py` with `discover_authoritative_scripts()` closes the shadow-script loophole across `scripts/*.py`.
- Combining static `QGR032` AST verification on `ModelFactory` class definitions with dynamic `ALL_FACTORIES` completeness assertions in `test_model_factories.py` guarantees 100% 32-hex `PrefixedUUID7` fixture parity.

## Remaining
- Execute Steps 1 through 3 via `/tier2-execute`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]
```
