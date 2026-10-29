<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Antigravity Skills Architecture Migration & Rule Budget Sovereignty

## 1. Objective & Architectural Background

Migrate the Quorum agentic orchestration layer from deprecated `.agents/workflows/*.md` files to the modern Antigravity Skills architecture (`.agents/skills/<name>/SKILL.md`), establish Progressive Disclosure subdirectories (`resources/` and `references/`) as Single Sources of Truth (SSOT) for templates and audit checklists, introduce three domain-specific auto-triggered Quorum skills (`sdui-parity-sync`, `trace-forensics`, `seed-vault-ops`), resolve the 20,000-token `defaultRulesBudget` overflow that currently demotes `@[.agents/rules/00-antigravity-core.md]` from inline startup injection, and enforce these invariants programmatically via `[NEW] @[scripts/audit_skills_architecture.py]` and `[NEW] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`.

### Root Causes Addressed
1. **Deprecated Workflow Topology:** All 24 Tier 0 through Tier 8 operational playbooks reside in `.agents/workflows/*.md`, which is deprecated in Antigravity in favor of `.agents/skills/<name>/SKILL.md`.
2. **20,000-Token `defaultRulesBudget` Overflow:** Antigravity enforces a strict 20,000-token aggregate budget (`defaultRulesBudget`) and a 24,000-byte per-file cap on `always_on` rules. Currently, `@[AGENTS.md]`, `@[GEMINI.md]`, `@[.agents/rules/05_llm_architecture.md]`, and `@[.agents/rules/00-antigravity-core.md]` exceed 20,000 tokens combined, causing `@[.agents/rules/00-antigravity-core.md]` to be excluded from inline context injection at session startup.
3. **Duplicated Checklists & Templates Across Playbooks:** Legacy workflow files duplicate the 2026 modernity checklist, technical debt sweep directives, and markdown/XML templates instead of isolating them in on-demand `resources/` and `references/` files inside skill directories.
4. **Missing Auto-Triggered Domain Runbooks:** High-risk cross-cutting workflows (specifically SDUI + PDF semantic parity verification, OpenTelemetry local execution trace forensics, and Seed Vault sanitization) lack dedicated auto-discovered skills.

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[GEMINI.md]`
- `@[scripts/auto_phase_runner.py]`
- `@[scripts/auto_hardening_runner.py]`
- `@[scripts/audit_markdown_boundaries.py]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[NEW] @[scripts/audit_skills_architecture.py]` | Ban untyped dicts, missing `argparse` CLI flags, or unvalidated skill frontmatter | Strict Pydantic V2 `SkillsAuditFindingDTO` & `SkillsAuditSummaryDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) and `argparse.ArgumentParser` CLI entrypoint | Pure stdlib string/regex frontmatter parsing without external YAML parser bloat | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_skills_architecture.py --test --ast-strict` |
| `[NEW] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]` | Ban happy-path-only testing or tautological mocks | ISTQB unit test suite (1 positive + 3 negative boundary and validation failure cases `SKL001`–`SKL004`) | Use `tmp_path` filesystem fixtures directly with zero mock classes | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict` |
| `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L57-L63]` | Ban stale hardcoded script count assertions (`31`) after adding `audit_skills_architecture.py` | Register `"audit_skills_architecture.py"` in `ALL_SCRIPTS` and update `test_script_count_is_exhaustive` assertion to `32` | Reuse existing parametrized `--help`, `-h`, latency, and unknown-flag test harness | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py` |
| `[NEW] @[.agents/skills/tier0-create-epic/SKILL.md]` | Ban legacy `.agents/workflows/` location and missing YAML frontmatter | Migrate Tier 0 Epic creation playbook to skill format with `name` and `description` frontmatter | Delegate Epic Markdown template to `resources/epic_template.md` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier0-create-epic/resources/epic_template.md]` | Ban inline template duplication inside `SKILL.md` | Extract canonical Quorum Epic template into Progressive Disclosure resource | Single static Markdown template resource | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier0-create-plan/SKILL.md]` | Ban legacy `.agents/workflows/` location and missing YAML frontmatter | Migrate Tier 0 Plan creation playbook to skill format with `name` and `description` frontmatter | Delegate Plan template to `resources/plan_template.md` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier0-create-plan/resources/plan_template.md]` | Ban inline template duplication inside `SKILL.md` | Extract canonical Hybrid XML Sandwich plan template into Progressive Disclosure resource | Single static Markdown template resource | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier0-research-epic/SKILL.md]` | Ban legacy `.agents/workflows/` location and missing YAML frontmatter | Migrate Tier 0 Epic research and red-teaming playbook to skill format | Keep single-file skill without unnecessary sub-folders | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier0-research-plan/SKILL.md]` | Ban legacy `.agents/workflows/` location and missing YAML frontmatter | Migrate Tier 0 Plan research playbook to skill format | Keep single-file skill without unnecessary sub-folders | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier1-planner/SKILL.md]` | Ban legacy `.agents/workflows/` location and missing YAML frontmatter | Migrate Tier 1 Epic phase planner playbook to skill format | Keep single-file skill without unnecessary sub-folders | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier1-tracker-generator/SKILL.md]` | Ban legacy `.agents/workflows/` location and bare `uv run` commands | Migrate Tier 1 Epic tracker generator playbook to skill format with offline `uv run` mandate | Delegate tracker template to `resources/epic_tracker_template.md` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]` | Ban inline tracker template duplication | Extract canonical Epic tracker markdown template into Progressive Disclosure resource | Single static Markdown template resource | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier1-plan-tracker-generator/SKILL.md]` | Ban legacy `.agents/workflows/` location and bare `uv run` commands | Migrate Tier 1 standalone plan tracker generator playbook to skill format with offline `uv run` mandate | Delegate tracker template to `resources/plan_tracker_template.md` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]` | Ban inline tracker template duplication | Extract canonical standalone plan tracker template into Progressive Disclosure resource | Single static Markdown template resource | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier2-execute/SKILL.md]` | Ban legacy `.agents/workflows/` location and duplicated modernity tables | Migrate Tier 2 systematic execution playbook to skill format | Reference shared `references/modernity_and_tech_debt_checklist.md` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` | Ban copy-pasting modernity tables across playbooks | Centralize Quorum 2026 modernity replacements and Scoped Boy Scout checklist | Single shared Markdown reference | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier2-hardening-backend/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 2 Python backend hardening playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier2-hardening-frontend/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 2 Flutter frontend hardening playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier3-database-reset/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 3 database reset and re-seeding playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier3-feature-refactor/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 3 feature refactor playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier3-god-code-decomposition/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 3 AST-assisted decomposition playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier3-minify-customization/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 3 rule and skill compression playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier4-bug-hunting/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 4 root cause analysis and TDD bug resolution playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier5-session-handover/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 5 session handover export playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier5-resume/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 5 session resume and zero-shortcut audit playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier6-execution-monitor/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 6 background log auditing and Auto-RCA monitor to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier7-describe-architecture/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 7 as-built architecture documentation synchronizer to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier8-red-teaming-audit/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 8 rule and skill red-teaming audit playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier8-audit-feature/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 8 first-principles feature audit playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier8-audit-plan/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 8 completed plan audit playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier8-audit-epic/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 8 reverse verification epic audit playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/tier8-test-coverage-expansion/SKILL.md]` | Ban legacy `.agents/workflows/` location | Migrate Tier 8 ISTQB negative and boundary test expansion playbook to skill format | Keep single-file skill | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/sdui-parity-sync/SKILL.md]` | Ban manual unverified SDUI edits across Python/PDF/Flutter | Create auto-triggered domain skill for SDUI Python/PDF/Flutter semantic parity | Direct CLI invocation of existing parity scripts | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/trace-forensics/SKILL.md]` | Ban unstructured log scraping or full-file `execution_trace.json` reads | Create auto-triggered domain skill for OpenTelemetry trace snapshot and FinOps inspection | Direct delegation to existing trace & FinOps utilities | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[NEW] @[.agents/skills/seed-vault-ops/SKILL.md]` | Ban manual `seed_data.json` prompt edits or unverified reseeding | Create auto-triggered domain skill for Seed Vault sanitization and database reseeding | Direct delegation to `sanitize_seed_vault.py` and `run_seed.py` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier0-create-epic.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier0-create-plan.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier0-research-epic.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier0-research-plan.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier1-planner.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier1-tracker-generator.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier1-plan-tracker-generator.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier2-execute.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier2-hardening-backend.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier2-hardening-frontend.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier3-database-reset.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier3-feature-refactor.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier3-god-code-decomposition.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier3-minify-customization.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier4-bug-hunting.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier5-session-handover.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier5-resume.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier6-execution-monitor.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier7-describe-architecture.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier8-red-teaming-audit.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier8-audit-feature.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier8-audit-plan.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier8-audit-epic.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[DELETE] @[.agents/workflows/tier8-test-coverage-expansion.md]` | Ban dual-directory `.agents/workflows/` coexistence or `.bak` files | Delete deprecated legacy workflow file after skill cutover | Complete physical removal | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `@[AGENTS.md]` | Ban `defaultRulesBudget` overflow that demotes `00-antigravity-core.md` | Update `<workflow_routing>` to reference `.agents/skills/<name>/SKILL.md` and keep `always_on` rules under 72,000 bytes | Rely on native `<skills>` discovery instead of duplicating skill descriptions | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `@[.agents/rules/00-antigravity-core.md]` | Ban stale `.agents/workflows/` routing references | Update `slash_command_routing` to reference `.agents/skills/` and verify inline token budget fit | Zero duplicate workflow routing tables | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `@[.agents/rules/05_llm_architecture.md]` | Ban unconditional `always_on` injection of domain-specific LLM rules on non-LLM turns | Change YAML frontmatter to `trigger: model_decision` with explicit `description` | Load on demand via `context_triggered_loading` and `model_decision` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `@[.agents/rules/04_directory_reference.md]` | Ban stale `.agents/workflows/` module entry or unregistered script/test files | Replace `.agents/workflows/` module entry with `.agents/skills/` and register `audit_skills_architecture.py` and `test_audit_skills_architecture.py` | Maintain single canonical directory index | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

1. **Inline Rule Budget Exhaustion (`@[AGENTS.md]`, `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/rules/05_llm_architecture.md]`):**
   - `@[.agents/rules/05_llm_architecture.md]` currently uses `trigger: always_on` and is unconditionally injected alongside `@[AGENTS.md]` and `@[GEMINI.md]`, pushing `@[.agents/rules/00-antigravity-core.md]` over the 20,000-token `defaultRulesBudget`. Changing `@[.agents/rules/05_llm_architecture.md]` to `trigger: model_decision` with an explicit description and trimming the redundant `<execution_tiers>` table in `@[AGENTS.md]` restores 100% inline injection for `@[.agents/rules/00-antigravity-core.md]`.
2. **Deprecated `.agents/workflows/` Directory & Duplicated Playbook Blocks:**
   - All 24 `.agents/workflows/*.md` files lack standard Skill YAML frontmatter (`name` + `description`) and duplicate 40+ lines of identical rule blocks across files. Migrating to `.agents/skills/<name>/SKILL.md` and extracting shared checklists/templates into `references/` and `resources/` eliminates this duplication.
3. **Metatest Script Inventory Synchronization (`@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L57-L63]`):**
   - `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L57-L63]` asserts an exact 31-script inventory in `scripts/`. Adding `[NEW] @[scripts/audit_skills_architecture.py]` requires synchronously registering `"audit_skills_architecture.py"` in `ALL_SCRIPTS`, updating `test_script_count_is_exhaustive` to assert `len(ALL_SCRIPTS) == 32`, and implementing `argparse.ArgumentParser` CLI semantics (`--help`, `-h`, exit code `2` on invalid flags).

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Create Deterministic Skills &amp; Rule Budget Auditor and ISTQB Unit Tests">
    <constraint invariant="strict_pydantic_v2_rust">Create and define `SkillsAuditFindingDTO` and `SkillsAuditSummaryDTO` in `[NEW] @[scripts/audit_skills_architecture.py]` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` field definitions.</constraint>
    <constraint invariant="anti_happy_path_mandate">Write unit tests in `[NEW] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]` covering 1 positive scenario and 3 negative ISTQB scenarios (missing YAML frontmatter, leftover `.agents/workflows/*.md` file, and `always_on` rule budget overflow).</constraint>
    <action>Create `[NEW] @[scripts/audit_skills_architecture.py]` implementing `SkillsAuditFindingDTO`, `SkillsAuditSummaryDTO`, `SkillsArchitectureAuditor`, and `main(argv: list[str] | None = None) -> int` using `argparse.ArgumentParser` (with `RawDescriptionHelpFormatter` and `--repo-root` option) to statically verify: (1) zero `.md` or `.md.bak` files remain inside `.agents/workflows/`, (2) all 27 required Quorum skills exist under `.agents/skills/<name>/SKILL.md` with valid YAML frontmatter containing `name` equal to `<name>` and a non-empty `description`, (3) all relative Markdown links (`./resources/...`, `./references/...`) and `@[...]` paths inside `.agents/skills/` resolve to existing files on disk, and (4) the combined byte and estimated token size of `AGENTS.md`, `GEMINI.md`, and all `.agents/rules/*.md` files with `trigger: always_on` (or without `trigger: model_decision`) is strictly below `MAX_ALWAYS_ON_BYTES = 72000` (18,000 tokens at 4 bytes/token) and each individual `always_on` file is strictly below `MAX_SINGLE_RULE_FILE_BYTES = 24000`.</action>
    <action>Update `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L57-L63]` and `ALL_SCRIPTS` to include `"audit_skills_architecture.py"` and assert `len(ALL_SCRIPTS) == 32`.</action>
    <action>Create `[NEW] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]` testing `SkillsArchitectureAuditor` across 4 deterministic partitions: (1) valid skills directory and compliant `always_on` rule budget returning zero findings, (2) legacy `.agents/workflows/legacy.md` file triggering fatal `SKL001`, (3) malformed `SKILL.md` missing `name` or `description` triggering fatal `SKL002`, and (4) `always_on` rule file exceeding `MAX_SINGLE_RULE_FILE_BYTES` or aggregate `MAX_ALWAYS_ON_BYTES` triggering fatal `SKL004`.</action>
    <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_skills_architecture.py --test --ast-strict`, `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict`, and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py` to verify 100% quality gate compliance.</action>
  </step>

  <step id="2" name="Phase 2A: Migrate Tier 0 and Tier 1 Planning &amp; Tracking Workflows to Skills with Progressive Disclosure Resources">
    <constraint invariant="ssot_reuse_mandate">Extract canonical Markdown/XML document templates into `resources/` subdirectories inside the corresponding Tier 0 and Tier 1 skill folders so that `SKILL.md` files remain concise and load templates on demand.</constraint>
    <action>Create `[NEW] @[.agents/skills/tier0-create-epic/resources/epic_template.md]` containing the canonical Quorum Epic Markdown structure and `<required_context_rules>` header block.</action>
    <action>Create `[NEW] @[.agents/skills/tier0-create-epic/SKILL.md]` with YAML frontmatter (`name: tier0-create-epic`, `description`) and full `<system_prompt>` execution protocol referencing `[epic_template.md](./resources/epic_template.md)`.</action>
    <action>Create `[NEW] @[.agents/skills/tier0-create-plan/resources/plan_template.md]` containing the canonical Hybrid XML Sandwich implementation plan structure and 5-Column Directives Table header.</action>
    <action>Create `[NEW] @[.agents/skills/tier0-create-plan/SKILL.md]` with YAML frontmatter (`name: tier0-create-plan`, `description`) and full `<system_prompt>` execution protocol referencing `[plan_template.md](./resources/plan_template.md)`.</action>
    <action>Create `[NEW] @[.agents/skills/tier0-research-epic/SKILL.md]` and `[NEW] @[.agents/skills/tier0-research-plan/SKILL.md]` with YAML frontmatter (`name`, `description`) and complete Five-Axis System 2 deconstruction protocols.</action>
    <action>Create `[NEW] @[.agents/skills/tier1-planner/SKILL.md]` with YAML frontmatter (`name: tier1-planner`, `description`) and full Epic phase planning protocol.</action>
    <action>Create `[NEW] @[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]` and `[NEW] @[.agents/skills/tier1-tracker-generator/SKILL.md]` with YAML frontmatter (`name: tier1-tracker-generator`, `description`).</action>
    <action>Create `[NEW] @[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]` and `[NEW] @[.agents/skills/tier1-plan-tracker-generator/SKILL.md]` with YAML frontmatter (`name: tier1-plan-tracker-generator`, `description`).</action>
  </step>

  <step id="3" name="Phase 2B: Migrate Tier 2 through Tier 8 Execution, Refactoring, Handover, and Audit Workflows to Skills">
    <constraint invariant="anti_duplication">Centralize the Quorum 2026 modernity replacement matrix and Scoped Boy Scout technical debt checklist in `[NEW] @[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` and reference it from execution and auditing skills.</constraint>
    <action>Create `[NEW] @[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` and `[NEW] @[.agents/skills/tier2-execute/SKILL.md]` with YAML frontmatter (`name: tier2-execute`, `description`).</action>
    <action>Create `[NEW] @[.agents/skills/tier2-hardening-backend/SKILL.md]` and `[NEW] @[.agents/skills/tier2-hardening-frontend/SKILL.md]` with YAML frontmatter and full hardening protocols.</action>
    <action>Create `[NEW] @[.agents/skills/tier3-database-reset/SKILL.md]`, `[NEW] @[.agents/skills/tier3-feature-refactor/SKILL.md]`, `[NEW] @[.agents/skills/tier3-god-code-decomposition/SKILL.md]`, and `[NEW] @[.agents/skills/tier3-minify-customization/SKILL.md]` with YAML frontmatter and full Tier 3 protocols.</action>
    <action>Create `[NEW] @[.agents/skills/tier4-bug-hunting/SKILL.md]`, `[NEW] @[.agents/skills/tier5-session-handover/SKILL.md]`, `[NEW] @[.agents/skills/tier5-resume/SKILL.md]`, `[NEW] @[.agents/skills/tier6-execution-monitor/SKILL.md]`, and `[NEW] @[.agents/skills/tier7-describe-architecture/SKILL.md]` with YAML frontmatter and full Tier 4 through Tier 7 protocols.</action>
    <action>Create `[NEW] @[.agents/skills/tier8-red-teaming-audit/SKILL.md]`, `[NEW] @[.agents/skills/tier8-audit-feature/SKILL.md]`, `[NEW] @[.agents/skills/tier8-audit-plan/SKILL.md]`, `[NEW] @[.agents/skills/tier8-audit-epic/SKILL.md]`, and `[NEW] @[.agents/skills/tier8-test-coverage-expansion/SKILL.md]` with YAML frontmatter and full Tier 8 audit protocols.</action>
  </step>

  <step id="4" name="Phase 2C: Purge Deprecated .agents/workflows/ Directory">
    <constraint invariant="the_no_legacy_mandate">Delete all 24 legacy `.agents/workflows/*.md` files cleanly without leaving `.bak` files in version control.</constraint>
    <action>Delete `[DELETE] @[.agents/workflows/tier0-create-epic.md]`, `[DELETE] @[.agents/workflows/tier0-create-plan.md]`, `[DELETE] @[.agents/workflows/tier0-research-epic.md]`, `[DELETE] @[.agents/workflows/tier0-research-plan.md]`, `[DELETE] @[.agents/workflows/tier1-planner.md]`, `[DELETE] @[.agents/workflows/tier1-tracker-generator.md]`, and `[DELETE] @[.agents/workflows/tier1-plan-tracker-generator.md]`.</action>
    <action>Delete `[DELETE] @[.agents/workflows/tier2-execute.md]`, `[DELETE] @[.agents/workflows/tier2-hardening-backend.md]`, `[DELETE] @[.agents/workflows/tier2-hardening-frontend.md]`, `[DELETE] @[.agents/workflows/tier3-database-reset.md]`, `[DELETE] @[.agents/workflows/tier3-feature-refactor.md]`, `[DELETE] @[.agents/workflows/tier3-god-code-decomposition.md]`, and `[DELETE] @[.agents/workflows/tier3-minify-customization.md]`.</action>
    <action>Delete `[DELETE] @[.agents/workflows/tier4-bug-hunting.md]`, `[DELETE] @[.agents/workflows/tier5-session-handover.md]`, `[DELETE] @[.agents/workflows/tier5-resume.md]`, `[DELETE] @[.agents/workflows/tier6-execution-monitor.md]`, `[DELETE] @[.agents/workflows/tier7-describe-architecture.md]`, `[DELETE] @[.agents/workflows/tier8-red-teaming-audit.md]`, `[DELETE] @[.agents/workflows/tier8-audit-feature.md]`, `[DELETE] @[.agents/workflows/tier8-audit-plan.md]`, `[DELETE] @[.agents/workflows/tier8-audit-epic.md]`, and `[DELETE] @[.agents/workflows/tier8-test-coverage-expansion.md]`.</action>
  </step>

  <step id="5" name="Phase 3: Create Domain-Specific Auto-Triggered Quorum Skills">
    <constraint invariant="sdui_contract_fracture_prevention">Ensure `sdui-parity-sync` enforces running `audit_dto_parity.py`, `test_sdui_semantic_parity.py`, `backend_audit_loop.py`, and `flutter_audit_loop.py --build` synchronously whenever SDUI blocks, adapters, PDF templates, or Flutter SDUI models change.</constraint>
    <action>Create `[NEW] @[.agents/skills/sdui-parity-sync/SKILL.md]` with YAML frontmatter (`name: sdui-parity-sync`, `description: Enforce 1:1 Cross-Domain DTO, Jinja PDF, and Flutter Freezed SDUI semantic parity whenever modifying SDUI models, adapters, PDF templates, or Flutter SDUI widgets.`) and deterministic step-by-step verification commands.</action>
    <action>Create `[NEW] @[.agents/skills/trace-forensics/SKILL.md]` with YAML frontmatter (`name: trace-forensics`, `description: Diagnose LLM token usage, context caching hits, execution latency, and span errors using local OpenTelemetry trace snapshots, bounded frozen_context.json inspection, and FinOps trace analysis.`) and deterministic forensic procedures.</action>
    <action>Create `[NEW] @[.agents/skills/seed-vault-ops/SKILL.md]` with YAML frontmatter (`name: seed-vault-ops`, `description: Safely inspect, validate, sanitize, and re-seed seed_data.json and local PostgreSQL 19 / JSON databases while enforcing prompt preservation and Opaque Stripe ID invariants.`) and deterministic seed verification commands.</action>
  </step>

  <step id="6" name="Phase 4: Optimize Rule Token Budget and Synchronize Root Governance Files">
    <constraint invariant="universal_ssot_and_normalization_mandate">Ensure `@[AGENTS.md]` and `@[.agents/rules/00-antigravity-core.md]` fit 100% within the 20,000-token `defaultRulesBudget` so `@[.agents/rules/00-antigravity-core.md]` is always injected inline without truncation or demotion.</constraint>
    <action>Modify `@[.agents/rules/05_llm_architecture.md]` to prepend YAML frontmatter (`trigger: model_decision` and `description: Apply when working inside backend_v2/llm/, prompts, or services involving AI execution, prompt compilation, or structured LLM outputs.`) so it loads on-demand rather than consuming the global `always_on` budget on non-LLM turns.</action>
    <action>Modify `@[AGENTS.md]` to update `<workflow_routing>` to reference `.agents/skills/<name>/SKILL.md` and streamline the `<execution_tiers>` summary to rely on native Antigravity `<skills>` discovery.</action>
    <action>Modify `@[.agents/rules/00-antigravity-core.md]` to update `<rule_block id="slash_command_routing">` to load `.agents/skills/<command>/SKILL.md` instead of `.agents/workflows/`.</action>
    <action>Modify `@[.agents/rules/04_directory_reference.md]` to replace the `<module path=".agents/workflows/">` entry with `<module path=".agents/skills/">` and register `audit_skills_architecture.py` in `<module path="scripts/">` and `test_audit_skills_architecture.py` in `<rule_block id="test_directory_isolation">`.</action>
    <action>Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict` to verify 0 findings across all skills and rule budgets.</action>
  </step>
</execution_protocol>
```

---

## 5. Reference Implementation Specification (`[NEW] @[scripts/audit_skills_architecture.py]`)

```python
"""Deterministic Auditor for Antigravity Skills Architecture & Rule Budget Sovereignty.

Verifies that all workspace playbooks reside in .agents/skills/<name>/SKILL.md
with valid YAML frontmatter, that no legacy .agents/workflows/*.md files exist,
that all relative skill resource/reference links resolve on disk, and that the
always_on rules token/byte budget stays within Antigravity inline limits.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field

MAX_SINGLE_RULE_FILE_BYTES: Final[int] = 24_000
MAX_ALWAYS_ON_BYTES: Final[int] = 72_000


class SkillsAuditFindingDTO(BaseModel):
    """Immutable DTO representing a single skills or rule-budget violation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[str, Field(pattern=r"^SKL\d{3}$", description="Violation code SKL001-SKL004")]
    file_path: Annotated[str, Field(min_length=1, description="Workspace-relative file path")]
    message: Annotated[str, Field(min_length=1, description="Human-readable violation description")]
    remediation: Annotated[str, Field(min_length=1, description="Deterministic remediation instruction")]


class SkillsAuditSummaryDTO(BaseModel):
    """Immutable DTO summarizing the full skills and rule-budget audit result."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    verified_skills_count: Annotated[int, Field(ge=0, description="Number of valid SKILL.md files verified")]
    always_on_total_bytes: Annotated[int, Field(ge=0, description="Total UTF-8 byte count of always_on rules")]
    findings: Annotated[list[SkillsAuditFindingDTO], Field(description="Accumulated audit findings")]
```

---

## 6. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
1. **Localized Audit & Unit Test Execution:**
   ```powershell
   $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_skills_architecture.py --test --ast-strict
   $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict
   $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py
   $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py
   ```
2. **ISTQB Equivalence Partitioning & Boundary Value Scenarios (`[NEW] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`):**
   - **Scenario 1 (Happy Path - Valid Skills & Rule Budget):** Temp repo root containing valid `.agents/skills/<name>/SKILL.md` with YAML `name` and `description`, existing `./resources/template.md` link, empty `.agents/workflows/`, and `always_on` rule files totaling `< 72,000` bytes (`< 24,000` bytes each) returns `SkillsAuditSummaryDTO` with `findings == []`.
   - **Scenario 2 (Negative Path 1 - Legacy Workflow Remnant `SKL001`):** Temp repo root containing `.agents/workflows/tier2-execute.md` returns a `SkillsAuditFindingDTO` with `rule_code == "SKL001"`.
   - **Scenario 3 (Negative Path 2 - Missing or Mismatched Frontmatter / Broken Resource Link `SKL002` & `SKL003`):** Temp repo root containing `.agents/skills/my-skill/SKILL.md` without `description:` or referencing a non-existent `./resources/missing.md` returns findings with `rule_code == "SKL002"` and `rule_code == "SKL003"`.
   - **Scenario 4 (Negative Path 3 - Rule Budget Boundary Violation `SKL004`):** Temp repo root containing an `always_on` rule file of `24,001` bytes (`MAX_SINGLE_RULE_FILE_BYTES + 1`) or aggregate `always_on` rules of `72,001` bytes (`MAX_ALWAYS_ON_BYTES + 1`) returns a finding with `rule_code == "SKL004"`.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Global Backend Audit Loop:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/ --test
  ```
- **Global Flutter Audit Loop:**
  ```powershell
  uv run python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell:
    ```powershell
    $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
    ```
  - Unix / Bash:
    ```bash
    RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
    ```

