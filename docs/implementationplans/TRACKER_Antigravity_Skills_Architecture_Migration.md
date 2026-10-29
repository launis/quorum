# Tracker: Antigravity Skills Architecture Migration & Rule Budget Sovereignty

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md] @[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]`
  - [x] Step 1: Phase 1: Create Deterministic Skills & Rule Budget Auditor and ISTQB Unit Tests
  - [x] Step 2: Phase 2A: Migrate Tier 0 and Tier 1 Planning & Tracking Workflows to Skills with Progressive Disclosure Resources
  - [x] Step 3: Phase 2B: Migrate Tier 2 through Tier 8 Execution, Refactoring, Handover, and Audit Workflows to Skills
  - [x] Step 4: Phase 2C: Purge Deprecated .agents/workflows/ Directory
  - [x] Step 5: Phase 3: Create Domain-Specific Auto-Triggered Quorum Skills
  - [x] Step 6: Phase 4: Optimize Rule Token Budget and Synchronize Root Governance Files
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md] @[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[scripts/audit_skills_architecture.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain after deleting all 24 `.agents/workflows/*.md` files.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic and `scripts/audit_skills_architecture.py`.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the Antigravity Skills Architecture (`.agents/skills/<name>/SKILL.md`), Progressive Disclosure `resources/` and `references/` subdirectories (`epic_template.md`, `plan_template.md`, `epic_tracker_template.md`, `plan_tracker_template.md`, `modernity_and_tech_debt_checklist.md`), and the static auditor `scripts/audit_skills_architecture.py` (`SKL001`–`SKL004`) with `SkillsAuditFindingDTO` and `SkillsAuditSummaryDTO`.
     - `@[ki_deterministic_hardening_state.md]`: Document `always_on` rule token budget sovereignty (`MAX_SINGLE_RULE_FILE_BYTES = 24000`, `MAX_ALWAYS_ON_BYTES = 72000`), `trigger: model_decision` configuration on `.agents/rules/05_llm_architecture.md`, and the auto-triggered domain skills (`sdui-parity-sync`, `trace-forensics`, `seed-vault-ops`).
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to replace `<module path=".agents/workflows/">` with `<module path=".agents/skills/">`, register `audit_skills_architecture.py` under `<module path="scripts/">`, and register `scripts/test_audit_skills_architecture.py` under `<rule_block id="test_directory_isolation">`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/01_system_context_and_invariants.md` and `docs/architecture/05_resilience_and_observability.md` describing the `.agents/skills/` orchestration topology and deterministic `audit_skills_architecture.py` quality gate in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md] @[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, instruct or execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`), explicitly staging only the touched files.
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
  - Skills Architecture & Rule Budget Gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py`
  - CLI Inventory Metatest Gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/audit_skills_architecture.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex Python/Dart modules.
- **Execution Mode**: Supports Step-by-Step mode (default pause after each step) and Continuous Full-Auto Mode invoked via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Antigravity_Skills_Architecture_Migration.md] @[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]`.
- **Post-Implementation Hardening Execution Options**:
  - Interactive Chat Mode: `/tier2-hardening-backend @[scripts/audit_skills_architecture.py]`
  - Autonomous Unattended CLI Runner: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Define immutable Pydantic V2 DTOs `SkillsAuditFindingDTO` and `SkillsAuditSummaryDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields in `[NEW] @[scripts/audit_skills_architecture.py]`. | Step 1 | [x] Completed |
| REQ-002 | Implement `SkillsArchitectureAuditor` and `main(argv: list[str] \| None = None) -> int` in `[NEW] @[scripts/audit_skills_architecture.py]` using `argparse.ArgumentParser` (`RawDescriptionHelpFormatter` and `--repo-root`) to enforce `SKL001` (zero `.agents/workflows/*.md` or `.bak` files), `SKL002` (all 27 required `.agents/skills/<name>/SKILL.md` files exist with matching `name` and non-empty `description`), `SKL003` (all relative `./resources/...`, `./references/...`, and `@[...]` links resolve on disk), and `SKL004` (`MAX_SINGLE_RULE_FILE_BYTES = 24000` and `MAX_ALWAYS_ON_BYTES = 72000`). | Step 1 | [x] Completed |
| REQ-003 | Synchronize `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L57-L63]` by registering `"audit_skills_architecture.py"` in `ALL_SCRIPTS` and updating `test_script_count_is_exhaustive` to assert `len(ALL_SCRIPTS) == 32`. | Step 1 | [x] Completed |
| REQ-004 | Create ISTQB unit test suite `[NEW] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]` covering 1 positive scenario and 3 negative boundary scenarios (`SKL001`, `SKL002`/`SKL003`, `SKL004`) using `tmp_path` fixtures, and pass `backend_audit_loop.py --test --ast-strict`. | Step 1 | [x] Completed |
| REQ-005 | Extract canonical Quorum Epic template into `[NEW] @[.agents/skills/tier0-create-epic/resources/epic_template.md]` and migrate `[NEW] @[.agents/skills/tier0-create-epic/SKILL.md]` with YAML frontmatter (`name: tier0-create-epic`, `description`). | Step 2 | [x] Completed |
| REQ-006 | Extract canonical Hybrid XML Sandwich plan template into `[NEW] @[.agents/skills/tier0-create-plan/resources/plan_template.md]` and migrate `[NEW] @[.agents/skills/tier0-create-plan/SKILL.md]` with YAML frontmatter (`name: tier0-create-plan`, `description`). | Step 2 | [x] Completed |
| REQ-007 | Migrate `[NEW] @[.agents/skills/tier0-research-epic/SKILL.md]`, `[NEW] @[.agents/skills/tier0-research-plan/SKILL.md]`, and `[NEW] @[.agents/skills/tier1-planner/SKILL.md]` with YAML frontmatter and full System 2 deconstruction and planning protocols. | Step 2 | [x] Completed |
| REQ-008 | Extract canonical tracker templates into `[NEW] @[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]` and `[NEW] @[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]`, and migrate `[NEW] @[.agents/skills/tier1-tracker-generator/SKILL.md]` and `[NEW] @[.agents/skills/tier1-plan-tracker-generator/SKILL.md]` with offline `uv run` mandates. | Step 2 | [x] Completed |
| REQ-009 | Centralize Quorum 2026 modernity replacement matrix and Scoped Boy Scout technical debt checklist in `[NEW] @[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` and migrate `[NEW] @[.agents/skills/tier2-execute/SKILL.md]`, `[NEW] @[.agents/skills/tier2-hardening-backend/SKILL.md]`, and `[NEW] @[.agents/skills/tier2-hardening-frontend/SKILL.md]`. | Step 3 | [x] Completed |
| REQ-010 | Migrate Tier 3 skills (`[NEW] @[.agents/skills/tier3-database-reset/SKILL.md]`, `[NEW] @[.agents/skills/tier3-feature-refactor/SKILL.md]`, `[NEW] @[.agents/skills/tier3-god-code-decomposition/SKILL.md]`, `[NEW] @[.agents/skills/tier3-minify-customization/SKILL.md]`). | Step 3 | [x] Completed |
| REQ-011 | Migrate Tier 4 through Tier 7 skills (`[NEW] @[.agents/skills/tier4-bug-hunting/SKILL.md]`, `[NEW] @[.agents/skills/tier5-session-handover/SKILL.md]`, `[NEW] @[.agents/skills/tier5-resume/SKILL.md]`, `[NEW] @[.agents/skills/tier6-execution-monitor/SKILL.md]`, `[NEW] @[.agents/skills/tier7-describe-architecture/SKILL.md]`). | Step 3 | [x] Completed |
| REQ-012 | Migrate Tier 8 audit skills (`[NEW] @[.agents/skills/tier8-red-teaming-audit/SKILL.md]`, `[NEW] @[.agents/skills/tier8-audit-feature/SKILL.md]`, `[NEW] @[.agents/skills/tier8-audit-plan/SKILL.md]`, `[NEW] @[.agents/skills/tier8-audit-epic/SKILL.md]`, `[NEW] @[.agents/skills/tier8-test-coverage-expansion/SKILL.md]`). | Step 3 | [x] Completed |
| REQ-013 | Physically delete all 24 legacy `.agents/workflows/*.md` files (`tier0-create-epic.md` through `tier8-test-coverage-expansion.md`) without leaving `.bak` artifacts. | Step 4 | [x] Completed |
| REQ-014 | Create domain-specific auto-triggered skill `[NEW] @[.agents/skills/sdui-parity-sync/SKILL.md]` enforcing synchronous execution of `audit_dto_parity.py`, `test_sdui_semantic_parity.py`, `backend_audit_loop.py`, and `flutter_audit_loop.py --build`. | Step 5 | [x] Completed |
| REQ-015 | Create domain-specific auto-triggered skills `[NEW] @[.agents/skills/trace-forensics/SKILL.md]` (OpenTelemetry trace snapshot and bounded `frozen_context.json` forensics) and `[NEW] @[.agents/skills/seed-vault-ops/SKILL.md]` (`sanitize_seed_vault.py` and `run_seed.py` verification). | Step 5 | [x] Completed |
| REQ-016 | Prepend `trigger: model_decision` and explicit `description` YAML frontmatter to `@[.agents/rules/05_llm_architecture.md]` so it loads on-demand and frees inline `defaultRulesBudget` capacity for `@[.agents/rules/00-antigravity-core.md]`. | Step 6 | [x] Completed |
| REQ-017 | Update `<workflow_routing>` in `@[AGENTS.md]` and `<rule_block id="slash_command_routing">` in `@[.agents/rules/00-antigravity-core.md]` to route slash commands through `.agents/skills/<name>/SKILL.md` while keeping combined `always_on` rules under `MAX_ALWAYS_ON_BYTES = 72000`. | Step 6 | [x] Completed |
| REQ-018 | Synchronize `@[.agents/rules/04_directory_reference.md]` by replacing `<module path=".agents/workflows/">` with `<module path=".agents/skills/">`, registering `audit_skills_architecture.py` in `<module path="scripts/">`, registering `scripts/test_audit_skills_architecture.py` in `<rule_block id="test_directory_isolation">`, and verifying 0 findings via `scripts/audit_skills_architecture.py`. | Step 6 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Step 1 (Phase 1): Implemented deterministic static auditor `@[scripts/audit_skills_architecture.py]` (`SkillsAuditFindingDTO`, `SkillsAuditSummaryDTO`, `SkillsArchitectureAuditor`, `main()`), ISTQB unit test suite `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`, and synchronized `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]` (`ALL_SCRIPTS` count `31 -> 32`).
- Completed Step 2 (Phase 2A): Migrated Tier 0 and Tier 1 planning and tracking playbooks to `.agents/skills/<name>/SKILL.md` with Progressive Disclosure `resources/` templates (`epic_template.md`, `plan_template.md`, `epic_tracker_template.md`, `plan_tracker_template.md`).
- Completed Step 3 (Phase 2B): Migrated Tier 2 through Tier 8 playbooks (including `tier2-hardening-knowledge` and `tier2-hardening-matrix`) to `.agents/skills/<name>/SKILL.md` and centralized the 2026 modernity checklist in `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`.
- Completed Step 4 (Phase 2C): Physically deleted all 26 legacy `.agents/workflows/*.md` files with zero `.bak` files remaining.
- Completed Step 5 (Phase 3): Created auto-triggered domain skills `@[.agents/skills/sdui-parity-sync/SKILL.md]`, `@[.agents/skills/trace-forensics/SKILL.md]`, and `@[.agents/skills/seed-vault-ops/SKILL.md]`.
- Completed Step 6 (Phase 4): Updated `@[.agents/rules/05_llm_architecture.md]` to `trigger: model_decision`, updated `@[AGENTS.md]` and `@[.agents/rules/00-antigravity-core.md]` (`23,987` bytes `< 24,000` single-file cap; total `always_on` budget `44,769 / 72,000` bytes), and synchronized `@[.agents/rules/04_directory_reference.md]`.

## Learned
- `.agents/rules/00-antigravity-core.md` was previously `37,515` bytes (`> 24,000` single-file byte cap), which in combination with `05_llm_architecture.md` caused Antigravity to exclude `00-antigravity-core.md` from inline context injection. Compressing `00-antigravity-core.md` to `23,987` bytes while preserving all 59 `<rule_block id="...">` blocks and converting `05_llm_architecture.md` to `trigger: model_decision` brought total `always_on` rules to `44,769 / 72,000` bytes (~11,192 tokens).
- Two additional legacy workflow files (`tier2-hardening-knowledge.md` and `tier2-hardening-matrix.md`) were present in `.agents/workflows/` and were migrated to `.agents/skills/tier2-hardening-knowledge/SKILL.md` and `.agents/skills/tier2-hardening-matrix/SKILL.md` so all 29 skills pass `audit_skills_architecture.py`.

## Remaining
- Execute Tier 2 Hardening (Backend) on `@[scripts/audit_skills_architecture.py]` and As-Built Architectural Sync (`/tier7-describe-architecture`).

## Resume Command
```powershell
/tier5-resume --target="@[docs/implementationplans/TRACKER_Antigravity_Skills_Architecture_Migration.md]" --workflow=/tier2-hardening-backend
```

