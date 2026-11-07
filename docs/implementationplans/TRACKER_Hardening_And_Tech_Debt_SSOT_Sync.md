# Tracker: Unify Technical Debt & Hardening SSOT, Dynamic Tracker/Target Discovery, KI Resolution, `.agents/rules/` Invariants, and Micro/Macro Script Gates

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md] @[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md]`
  - [x] Step 1: Phase 1A: Unify AST Predicates and Dict .get() Exemption SSOT Between _ast_guardrails.py and audit_technical_debt.py
  - [x] Step 2: Phase 1B: Extend audit_skills_architecture.py (SKL003) to Enforce 4-Way Dynamic KI, Rule, and Script Coverage
  - [x] Step 3: Phase 1C: Harden backend_audit_loop.py, flutter_audit_loop.py, and auto_hardening_runner.py Companion Test SSOT, Dynamic Tracker/Target Discovery, and Micro/Macro Gates
  - [x] Step 4: Phase 2: Synchronize .agents/rules/00-antigravity-core.md, tier2-hardening-backend/SKILL.md, and tier2-hardening-frontend/SKILL.md
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md] @[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_skills_architecture.py]
  - [ ] @[scripts/audit_technical_debt.py]
  - [ ] @[scripts/auto_hardening_runner.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[scripts/flutter_audit_loop.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document `is_exempt_dict_get_call` SSOT unification between `@[scripts/_ast_guardrails.py]` and `@[scripts/audit_technical_debt.py]`, domain-scoped `TD_DICT_GET` enforcement, and `pytest.raises` negative validation exemptions for `TD_MODEL_FACTORY`.
     - `@[ki_deterministic_hardening_state.md]`: Document dynamic tracker discovery (`discover_tracker_files`, `discover_completed_trackers`), dynamic target and directory/glob expansion (`expand_dynamic_target_paths`, `discover_unhardened_targets`, `--discover`), companion unit test SSOT delegation (`discover_companion_test_targets`, `resolve_flutter_unit_test_files`), and 4-way `SKL003` verification in `@[scripts/audit_skills_architecture.py]`.
     - `@[ki_zero_permissive_typing.md]`: Document target-scoped `--micro` execution of `audit_dict_eradication.py` and `audit_technical_debt.py` inside `@[scripts/backend_audit_loop.py]` and `--fail-on-mismatch` DTO parity enforcement.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect updated responsibilities of `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_technical_debt.py]`, `@[scripts/audit_skills_architecture.py]`, `@[scripts/auto_hardening_runner.py]`, `@[scripts/backend_audit_loop.py]`, and `@[scripts/flutter_audit_loop.py]`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the unified AST/technical debt SSOT, 4-way skill/rule/KI/script verification gate, and dynamic hardening runner target resolution in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md] @[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/auto_hardening_runner.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Extract canonical `is_exempt_dict_get_call(node: ast.Call) -> bool` helper in `@[scripts/_ast_guardrails.py]`, export `_has_annotated_field`, `_is_annotated_subscript`, `_is_field_call`, and `is_exempt_dict_get_call` in `__all__`, and invoke `is_exempt_dict_get_call(node)` inside `QuorumGuardrailVisitor.visit_Call` (`QGR002`). | Step 1 | [x] Completed |
| REQ-002 | Delete duplicate AST helper definitions in `@[scripts/audit_technical_debt.py]`, import shared predicates from `scripts._ast_guardrails`, gate `TD_DICT_GET` to `self.is_domain_code` using `is_exempt_dict_get_call(node)`, and track `_in_pytest_raises` in `visit_With` / `visit_AsyncWith` to exempt intentional negative `model_validate({...})` tests from `TD_MODEL_FACTORY`. | Step 1 | [x] Completed |
| REQ-003 | Add ISTQB positive and negative unit tests in `@[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]` covering `is_exempt_dict_get_call`, `scripts/` non-domain `.get()` scoping, and `pytest.raises` exemptions for `TD_MODEL_FACTORY`. | Step 1 | [x] Completed |
| REQ-004 | Define `DEFAULT_CANONICAL_KI_ARTIFACTS`, `discover_canonical_ki_artifacts`, `CANONICAL_KI_ARTIFACTS`, and `PLACEHOLDER_KI_TOKENS` in `@[scripts/audit_skills_architecture.py]`, and extend `SkillsArchitectureAuditor` (`SKL003`) to fail-fast on phantom `ki_*.md` references, broken `scripts/*.py` references, or omitted canonical KIs and `.agents/rules/*.md` files across `tier2-hardening-backend` and `tier2-hardening-frontend`. | Step 2 | [x] Completed |
| REQ-005 | Add ISTQB positive and negative unit tests in `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]` verifying `discover_canonical_ki_artifacts`, valid KI/script references, and `SKL003` detection of phantom KIs, missing scripts, and omitted canonical KIs. | Step 2 | [x] Completed |
| REQ-006 | Extend `@[scripts/backend_audit_loop.py]` with `repo_root: Path \| None = None` support on `discover_companion_test_targets`, `f"test_{pkg_name}_init.py"` candidate resolution, `--fail-on-mismatch` on `audit_dto_parity.py`, `audit_skills_architecture.py` in Macro Stage 10/10, and target-scoped `audit_dict_eradication.py` + `audit_technical_debt.py` execution in `--micro` mode, verified via `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`. | Step 3 | [x] Completed |
| REQ-007 | Extend `resolve_flutter_unit_test_files` and `main` in `@[scripts/flutter_audit_loop.py]` to resolve and execute unit tests for `lib/` leaf directories in `--micro` mode, verified via positive and negative tests in `@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py]`. | Step 3 | [x] Completed |
| REQ-008 | Replace hardcoded `HISTORICAL_COMPLETED_TRACKERS` in `@[scripts/auto_hardening_runner.py]` with dynamic `discover_tracker_files` and `discover_completed_trackers`, add `expand_dynamic_target_paths`, `discover_unhardened_targets`, and `--discover` (`HardeningRunnerArgsDTO.discover`), delegate `resolve_target_unit_test_files` to `discover_companion_test_targets` and `resolve_flutter_unit_test_files`, and verify via `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]`. | Step 3 | [x] Completed |
| REQ-009 | Update `@[.agents/rules/00-antigravity-core.md]` line 17 to replace the deleted KI reference `@[ki_sdui_matrix_synthesis.md]` with `@[ki_god_code_prevention.md]`. | Step 4 | [x] Completed |
| REQ-010 | Synchronize `@[.agents/skills/tier2-hardening-backend/SKILL.md]` with conditional loading of `03_seed_vault.md` and `05_llm_architecture.md`, deterministic Domain-to-KI routing across all 8 canonical `ki_*.md` artifacts and pillar KIs, `QGR017` / `ZORM001`–`ZORM007` / `exclude_none=True` / `scoped_mock_and_fault_isolation_mandate` checklist items, and conditional/macro `scripts/` gates. | Step 4 | [x] Completed |
| REQ-011 | Synchronize `@[.agents/skills/tier2-hardening-frontend/SKILL.md]` with active Frontend KIs in `DOMAIN_KI_RESOLUTION_GATE`, `DGR011` (`context.mounted`), `DGR012` (`refreshListenable`), `LayoutBuilder` 1200/800 macro-breakpoints, `ExcludeSemantics` chart sandboxing, standardized `flutter_audit_loop.py ... --build --strict --micro` flags, and 4-gate `sdui-parity-sync` verification. | Step 4 | [x] Completed |
| REQ-012 | Pass `scripts/audit_skills_architecture.py` and `scripts/backend_audit_loop.py` with zero findings across all modified rules, skills, and scripts. | Step 4 | [x] Completed |

# Session Handover Context

## Achieved
- Executed Step 1 (Phase 1A — commit `8503ef65a`): Extracted canonical `is_exempt_dict_get_call` in `@[scripts/_ast_guardrails.py]`, unified AST helpers in `@[scripts/audit_technical_debt.py]`, scoped `TD_DICT_GET` to `self.is_domain_code`, and exempted `pytest.raises` blocks from `TD_MODEL_FACTORY`.
- Executed Step 2 (Phase 1B — commit `b0d6129e7`): Extended `@[scripts/audit_skills_architecture.py]` (`SKL003`) with `discover_canonical_ki_artifacts`, `CANONICAL_KI_ARTIFACTS`, `PLACEHOLDER_KI_TOKENS`, and 4-way KI/rule/script coverage enforcement across `.agents/skills/*/SKILL.md` and `.agents/rules/*.md`.
- Executed Step 3 (Phase 1C — commit `1a75d1c68`): Added `repo_root` and `f"test_{pkg_name}_init.py"` support to `discover_companion_test_targets`, wired `audit_dto_parity.py --fail-on-mismatch`, `audit_skills_architecture.py`, and `--micro` target-scoped `audit_dict_eradication.py` + `audit_technical_debt.py` in `@[scripts/backend_audit_loop.py]`; added `lib/` leaf directory `--micro` test resolution in `@[scripts/flutter_audit_loop.py]`; and replaced hardcoded `HISTORICAL_COMPLETED_TRACKERS` in `@[scripts/auto_hardening_runner.py]` with `discover_tracker_files`, `discover_completed_trackers`, `expand_dynamic_target_paths`, `discover_unhardened_targets` (`--discover`), and companion test SSOT delegation.
- Executed Step 4 (Phase 2 — commit `c972c978f`): Synchronized `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/skills/tier2-hardening-backend/SKILL.md]`, and `@[.agents/skills/tier2-hardening-frontend/SKILL.md]`, passing the 10-stage macro audit loop with `0` violations and >90% test coverage across all modified modules.
- Executed Tier 8 Plan Audit (`/tier8-audit-plan`): Verified 100% physical implementation across all 14 target files and 12 requirements (`REQ-001` through `REQ-012`), synchronized AST line bounds in `@[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md]`, and verified `0` technical debt findings, `0` DTO parity mismatches, `0` `SKL001`–`SKL005` violations, and `100%` plan-tracker parity.

## Learned
- Using `ast.parse(..., mode="eval").body` in AST unit test assertions avoids `ast.Expr` `.value` attribute narrowing issues without requiring `# type: ignore[attr-defined]`, preserving Census `T = 0` in `scripts/audit_warning_baseline.py`.
- `parse_tracker_unhardened_targets` in `scripts/auto_hardening_runner.py` must check `has_ext = "." in Path(clean_path).name` before filtering by `.py`/`.dart` so extensionless directory targets in tracker checklists flow into `expand_dynamic_target_paths`.
- `discover_canonical_ki_artifacts` must use `rglob("ki_*.md")` because Antigravity Knowledge Item artifacts reside in nested `knowledge/<ki_name>/artifacts/` subdirectories.

## Remaining
- Execute `Tier 2 Hardening (Backend)` via `scripts/auto_hardening_runner.py` across the 6 modified scripts (`scripts/_ast_guardrails.py`, `scripts/audit_skills_architecture.py`, `scripts/audit_technical_debt.py`, `scripts/auto_hardening_runner.py`, `scripts/backend_audit_loop.py`, `scripts/flutter_audit_loop.py`).
- Execute `/tier7-describe-architecture @[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_And_Tech_Debt_SSOT_Sync.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md] @[ki_zero_permissive_typing.md]`.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Hardening_And_Tech_Debt_SSOT_Sync.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
```
