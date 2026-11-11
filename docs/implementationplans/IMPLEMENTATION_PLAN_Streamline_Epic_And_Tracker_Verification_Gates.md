<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Streamline Epic and Tracker Verification Gates

## 1. Objective & Architectural Background

### Problem Statement & Root Cause Analysis
Empirical analysis of multi-phase Epic tracking workflows demonstrates that over 75% of tracker checklist items consist of redundant, non-automated verification overhead that duplicates deterministic quality gates and the post-implementation `Tier 2 Hardening` AI subagent pipeline (`@[scripts/auto_phase_runner.py]` and `@[scripts/auto_hardening_runner.py]`). Specifically and exhaustively, three structural root causes generate this redundancy:

1. **Standalone Verification-Only Phases in `epic_template.md` (`Phase 4: Verification & E2E Integration Gate`)**:
   - `@[.agents/skills/tier0-create-epic/resources/epic_template.md]` places `### Phase 4: Verification & E2E Integration Gate` inside `## 3. Phased Execution Plan (Implementation Strategy)` immediately above `## 4. Definition of Done (DoD) & Verification Plan`.
   - Consequently, `@[.agents/skills/tier0-create-epic/SKILL.md]` drafts a fourth phase that re-lists unit test files already authored and verified during Phases 1 through 3, and `@[.agents/skills/tier1-planner/SKILL.md]` compiles that section into a standalone `04_phase4_plan.md` with its own `/tier0-research-plan`, `/tier2-execute`, and `/tier8-audit-plan` cycle.
2. **Duplicate Per-Phase `/tier8-audit-plan` & `Test Coverage Assertions` Rows**:
   - `@[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]` and `@[scripts/audit_tracker_output.py]` (`TRK002`) force every phase in an Epic tracker (and `## Step Execution Status` in `@[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]`) to include `- [ ] **[NOK] Test Coverage Assertions:**` and `- [ ] **[NOK] Audit:** /tier8-audit-plan` in addition to `### Final Epic Audit` (`/tier8-audit-epic`) or `### Final Plan Audit` (`/tier8-audit-plan`).
   - During autonomous execution via `@[scripts/auto_phase_runner.py]`, each phase executes `/tier2-execute` followed by `run_phase_quality_gate` and hands off directly to `@[scripts/auto_hardening_runner.py]`, leaving per-phase `Test Coverage Assertions` and `Audit: /tier8-audit-plan` rows permanently unchecked.
3. **Redundant Manual Prose Checkboxes in `### Post-Implementation Gates`**:
   - `@[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]`, `@[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]`, and `@[scripts/audit_plan_tracker_parity.py]` (`TPR008`) require manual prose checkboxes (`Golden Master & Test Restoration Audit`, `Proxy Sunset & Consumer Migration`, `Pre-Delete Audit`, and `Semantic Coverage & Zero-Loss Audit`) that duplicate checks already enforced deterministically by `scripts/backend_audit_loop.py --test --ast-strict`, `scripts/flutter_audit_loop.py --build`, `scripts/auto_hardening_runner.py`, and `scripts/audit_epic_coverage.py`.

### Preserved High-Value Verification Architecture
To maintain 100% defect-detection power without bureaucratic duplication, the streamlined pipeline retains the four orthogonal verification layers:
1. **Per-Phase Implementation & Micro-Audit (`/tier2-execute`)**: Every implementation phase delivers production code paired with its companion unit/widget tests in the same phase, verified by `backend_audit_loop.py <target> --test --ast-strict` and `flutter_audit_loop.py <target> --build`.
2. **Per-File Isolated `Tier 2 Hardening` AI Subagent Passes (`--agent-cmd`)**: `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` via `@[scripts/auto_hardening_runner.py]` with `--agent-cmd` (`/tier2-hardening-backend` and `/tier2-hardening-frontend` per target file) and content-addressed SHA-256 caching (`data/hardening_cache.json`) remain 100% mandatory (`TRK008` and `TPR008`) to provide zero-author-bias semantic bug hunting per surviving modified file.
3. **Integration, Seed & Live E2E Checkpoint**: Full-repository macro quality gates, database seed verification, and Live E2E (`test_integration_real_llm.py`).
4. **Final Architectural Audit (`/tier8-audit-epic` or `/tier8-audit-plan`)**: Single final audit at the end of the tracker (`### Final Epic Audit` or `### Final Plan Audit`).

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/01-python-backend.md]`
- `@[.agents/rules/04_directory_reference.md]`
- `@[scripts/auto_phase_runner.py]`
- `@[scripts/auto_hardening_runner.py]`
- `@[scripts/audit_skills_architecture.py]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY]` @[.agents/skills/tier0-create-epic/resources/epic_template.md] | Hardcoded `### Phase 4: Verification & E2E Integration Gate` inside `## 3. Phased Execution Plan` causing standalone test-only phase plans | Restrict `## 3. Phased Execution Plan` to implementation phases with paired unit tests; keep global verification exclusively in `## 4. Definition of Done (DoD) & Verification Plan` | Eliminate duplicate `Phase 4` verification phase generation | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier0-create-epic/SKILL.md] | Unconstrained phase breakdown allowing verification-only phases in `## 3. Phased Execution Plan` | Add `<rule_block id="ban_verification_only_phases">` mandating vertical code + unit test pairing per phase while preserving `REQUIRED_FACTORY_SKILL_TOKENS` | Zero standalone test-only phases | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier1-planner/SKILL.md] | Generating `04_phase4_plan.md` for verification-only phases and lacking streamlined `### Phase N` directives in `tracker_auto_synchronization_mandate` and Step 4 (`MANDATORY TRACKER AUTO-UPDATE`) | Enforce `<rule_block id="ban_verification_only_phases">` and explicitly codify streamlined `### Phase N` blocks (`Red-Teaming` + `Execution` with indented steps, zero per-phase `Audit:` or `Test Coverage Assertions`) in `tracker_auto_synchronization_mandate` and Step 4 while preserving `REQUIRED_FACTORY_SKILL_TOKENS` and `Tier 2 Hardening` `--agent-cmd` | Remove verification-only phase plans and per-phase audit rows | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md] | Per-phase `Test Coverage Assertions` and `Audit: /tier8-audit-plan` rows, 4 redundant manual prose checkboxes in `### Post-Implementation Gates`, and `-> /tier8-audit-plan ->` in `- **Workflow Loop**:` (line 59) | Streamline `### Phase 1` to `Plan`, `Red-Teaming`, and `Execution`; preserve dedicated `### Integration Checkpoint: Full-Stack Validation` section header; restrict `### Post-Implementation Gates` to `Tier 2 Hardening (Backend & Frontend)` (`--agent-cmd`); remove `-> /tier8-audit-plan ->` from `- **Workflow Loop**:`; retain `Documentation & Knowledge Item Update` and `Final Epic Audit` | Cut 12+ redundant manual tracker checkboxes per Epic and align workflow loop instructions | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier1-tracker-generator/SKILL.md] | Implicit template delegation without explicit UPDATE MODE ban on legacy per-phase `/tier8-audit-plan`, `Test Coverage Assertions`, or removed prose checkboxes | Synchronize `tracker_update_preservation` and Step 2 (`GENERATE OR UPDATE TRACKER`) with streamlined `epic_tracker_template.md`, stripping obsolete per-phase `Audit:` and prose checkboxes on tracker updates while strictly retaining `mandatory_ai_hardening_subagent_gate` | Single final `/tier8-audit-epic` gate per Epic tracker across CREATE and UPDATE modes | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md] | Duplicate `/tier8-audit-plan` row under `## Step Execution Status` and 3 redundant manual prose checkboxes under `### Post-Implementation Gates` | Retain `Execution:` + indented steps under `## Step Execution Status`, `Tier 2 Hardening (Backend & Frontend)` (`--agent-cmd`) under `### Post-Implementation Gates`, `Documentation & Knowledge Item Update`, and single `### Final Plan Audit` (`/tier8-audit-plan`) | Eliminate duplicate `/tier8-audit-plan` and prose checkboxes in standalone trackers | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier1-plan-tracker-generator/SKILL.md] | Implicit template delegation without explicit UPDATE MODE ban on duplicate `Audit:` rows or removed prose checkboxes in standalone trackers | Synchronize `tracker_update_preservation` and Step 2 (`GENERATE OR UPDATE TRACKER`) with streamlined `plan_tracker_template.md`, stripping obsolete duplicate `Audit:` and prose checkboxes on tracker updates while preserving `mandatory_ai_hardening_subagent_gate` | Unified clean structure across Epic and Plan trackers across CREATE and UPDATE modes | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[.agents/skills/tier2-execute/SKILL.md] | Unconditional `<gate>` in Step 8 (`PLAN WRAP-UP & AUDIT ROUTING`) instructing the user to run `/tier8-audit-plan` after every executed `implementation_plan.md`, re-introducing per-phase `/tier8-audit-plan` in Epics and bypassing `Post-Implementation Gates` | Route Step 8 deterministically while preserving `REQUIRED_FACTORY_SKILL_TOKENS`: advance intermediate Epic phases directly to next phase `/tier0-research-plan`, and upon completing all implementation phases/steps route through `Post-Implementation Gates` (`auto_hardening_runner.py ... --agent-cmd`) -> `/tier7-describe-architecture` -> single final `/tier8-audit-epic` (Epic) or `/tier8-audit-plan` (Standalone Plan) | Eliminate contradictory post-phase `/tier8-audit-plan` routing in `tier2-execute` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY]` @[scripts/audit_tracker_output.py#L99-L171] | `TRK002` failing when per-phase `Audit: /tier8-audit-plan` is omitted from `### Phase N` | Validate `**Plan:** @[...]`, `Execution:`, and indented `Step` checkboxes (or deferred `Create Plan`) in `check_phase_format` while `TRK001` enforces `### Final Epic Audit` | Zero false-positive `TRK002` failures on streamlined Epic trackers | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py --test --ast-strict` |
| `[MODIFY]` @[scripts/audit_tracker_output.py#L174-L253] | `TRK002` requiring a duplicate `Audit:` line inside `## Step Execution Status` in addition to `### Final Plan Audit` | Validate `**Plan:** @[...]`, `Execution:`, and indented `Step` checkboxes in `check_step_format` while `TRK001` enforces `### Final Plan Audit` | Eliminate duplicate audit requirement in `PLAN` mode | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py --test --ast-strict` |
| `[MODIFY]` @[scripts/audit_plan_tracker_parity.py#L128-L155] | Requiring `has_golden_master_gate`, `has_pre_delete_gate`, and `has_semantic_coverage_gate` boolean fields on `TrackerDocumentAST` | Retain `has_doc_sync_gate`, `has_final_audit_gate`, `has_session_handover`, `has_resume_command`, `has_backend_hardening_agent_cmd`, and `has_frontend_hardening_agent_cmd` on `TrackerDocumentAST` | Prune 3 obsolete prose-gate booleans from `TrackerDocumentAST` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --test --ast-strict` |
| `[MODIFY]` @[scripts/audit_plan_tracker_parity.py#L294-L455] | Regex-scanning for `Golden Master & Test Restoration Audit`, `Pre-Delete Audit`, and `Semantic Coverage & Zero-Loss Audit` | Parse `has_doc_sync_gate`, `has_final_audit_gate`, `has_session_handover`, `has_resume_command`, `has_backend_hardening_agent_cmd`, and `has_frontend_hardening_agent_cmd` | Deterministic AST extraction of active quality gates | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --test --ast-strict` |
| `[MODIFY]` @[scripts/audit_plan_tracker_parity.py#L458-L840] | Raising fatal `TPR008` on missing prose checkboxes (`has_golden_master_gate`, `has_pre_delete_gate`, `has_semantic_coverage_gate`) | Enforce fatal `TPR008` strictly on `has_backend_hardening_agent_cmd`, `has_frontend_hardening_agent_cmd`, `has_doc_sync_gate`, `has_final_audit_gate`, `has_session_handover`, and `has_resume_command` | Keep 100% enforcement of AI subagent hardening, Tier 7 doc sync, final audit, and handover | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --test --ast-strict` |
| `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L65-L207] | Asserting `TRK002` failure when per-phase `Audit:` line is omitted in `check_phase_format` | Assert `check_phase_format` passes both with and without optional `Audit:` lines and fails fast (`TRK002`) when `**Plan:**`, `Execution:`, or indented `Step` checkboxes are missing | 100% unit test alignment with streamlined phase format | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py --test --ast-strict` |
| `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L599-L610] | Including redundant `Audit:` line in baseline `check_step_format` fixture | Verify `check_step_format` passes cleanly with `**Plan:**`, `Execution:`, and indented `Step` checkboxes | Match streamlined `plan_tracker_template.md` | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py --test --ast-strict` |
| `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L613-L649] | Expecting `TRK002` failure on `no_audit` in `check_step_format` | Verify `no_plan`, `no_exec`, and `no_steps` trigger `TRK002` while `no_audit` passes `check_step_format` (since `### Final Plan Audit` is validated by `check_mandatory_sections`) | Accurate negative boundary test coverage | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py --test --ast-strict` |
| `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py] | Out-of-bounds module-level `SAMPLE_TRACKER` causing weak `assert exc_info.value.code in (0, 1)` assertions, 6 test fixtures embedding removed prose gate strings (`Golden Master`, `Pre-Delete`, `Semantic Coverage`), and missing negative `TPR008` tests for `has_doc_sync_gate` / `has_final_audit_gate` | Upgrade `SAMPLE_TRACKER` to a valid streamlined tracker so `test_parse_and_parity_clean`, `test_main_cli_success`, and `test_main_cli_auto_infer_plan` assert `report.passed is True` and `exc_info.value.code == 0`; remove obsolete prose gate lines across all 6 test fixtures while preserving `b_pattern` `- [ ]` lookahead coverage in `test_backend_only_hardening_checklist_without_frontend_gate`; add negative `TPR008` assertions for missing `As-Built Architectural Sync` and `System 2 Red-Team Audit` | Complete whole-file ISTQB positive, negative, and regex-boundary test coverage with zero theater assertions | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --test --ast-strict` |
| `[MODIFY]` @[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md] | Self-hosting standalone tracker retaining transitional duplicate `Audit:` row and 3 legacy prose checkboxes needed prior to Step 3 auditor updates | Streamline `TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md` in Step 3 immediately after updating `audit_tracker_output.py` and `audit_plan_tracker_parity.py`, verifying `0` findings across both CLI auditors | Live self-hosting dogfood verification on active standalone tracker | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_plan_tracker_parity.py --plan docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md --tracker docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Pre-flight execution of `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/audit_tracker_output.py scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --include-one-hop` returned **0 findings (`PASSED Clean`)**. No pre-existing technical debt exists in the touched Python targets.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Step 1: Streamline Epic Template, Tier 0 Create Epic Skill, and Tier 1 Planner Skill">
    <constraint invariant="anti_ambiguity_mandate">Never use forbidden ambiguity markers in skill definitions or templates; use explicit closed lists ("specifically and exhaustively:").</constraint>
    <constraint invariant="pairwise_rule_and_guardrail_orthogonality_mandate">Preserve all required factory and orthogonality tokens (`schema_blast_radius_and_factory_mandate`, `pairwise_rule_and_guardrail_orthogonality_mandate`, `model_factories.py`) in `tier0-create-epic/SKILL.md` and `tier1-planner/SKILL.md` (`SKL003`).</constraint>
    <touched_artifacts>
      <artifact action="MODIFY">@.agents/skills/tier0-create-epic/resources/epic_template.md</artifact>
      <artifact action="MODIFY">@.agents/skills/tier0-create-epic/SKILL.md</artifact>
      <artifact action="MODIFY">@.agents/skills/tier1-planner/SKILL.md</artifact>
    </touched_artifacts>
    <action>
      1. In `@[.agents/skills/tier0-create-epic/resources/epic_template.md]`:
         - Remove `### Phase 4: Verification &amp; E2E Integration Gate` and its bullet `- [Unit, integration, and live E2E verification.]` from `## 3. Phased Execution Plan (Implementation Strategy)`.
         - Update `### Phase 2` and `### Phase 3` bullets in `## 3. Phased Execution Plan (Implementation Strategy)` to explicitly state that each phase includes its companion unit and widget tests alongside production code changes, while global full-suite audit loops, database seed verification, and Live E2E reside exclusively in `## 4. Definition of Done (DoD) &amp; Verification Plan`.
      2. In `@[.agents/skills/tier0-create-epic/SKILL.md]`:
         - Add `<rule_block id="ban_verification_only_phases">` inside `<context_rules>` using `<banned_pattern>` and `<mandatory_pattern>` tags (avoiding `NEVER use/call/invoke` phrasings on shared audit script names so `verify_candidate_rule_against_all` in `SKL003` remains 100% conflict-free): ban creating standalone verification-only, test-only, or E2E gate phases (specifically `### Phase 4: Verification &amp; E2E Integration Gate` or `04_phase4_plan.md`) in `## 3. Phased Execution Plan`. Mandate that every phase in `## 3. Phased Execution Plan` delivers production code paired with its companion unit/widget tests in the same phase, while full-repository audit loops (`scripts/backend_audit_loop.py`, `scripts/flutter_audit_loop.py`), `backend_v2/seed/run_seed.py local` (using full path `backend_v2/seed/run_seed.py`, never `scripts/run_seed.py`), and Live E2E (`backend_v2/tests/integration/test_integration_real_llm.py`) belong exclusively in `## 4. Definition of Done (DoD) &amp; Verification Plan`.
      3. In `@[.agents/skills/tier1-planner/SKILL.md]`:
         - Add `<rule_block id="ban_verification_only_phases">` inside `<context_rules>` prohibiting the generation of standalone verification-only phase plans (`04_phase4_plan.md`); instruct the planner to fold any unit/widget test targets into their corresponding implementation phase plans and place global seed/E2E verification exclusively in the tracker's `### Integration Checkpoint: Full-Stack Validation`.
         - Update `<rule_block id="tracker_auto_synchronization_mandate">` and Step 4 (`SELF-HEALING FIDELITY AUDIT &amp; TRACKER SYNCHRONIZATION` -> `<action name="MANDATORY TRACKER AUTO-UPDATE">`) to emit streamlined `### Phase N` blocks (`Red-Teaming` + `Execution` with indented step checkboxes, omitting per-phase `Test Coverage Assertions` and per-phase `Audit: /tier8-audit-plan` lines) while strictly preserving `mandatory_ai_hardening_subagent_gate` (`Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` with `--agent-cmd`).
    </action>
    <validation_gate>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py</validation_gate>
  </step>

  <step id="2" name="Step 2: Streamline Epic and Standalone Plan Tracker Templates, Generator Skills, and Tier 2 Execute Routing">
    <constraint invariant="mandatory_ai_subagent_hardening_tracker_gates">Strictly preserve `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` headers invoking `scripts/auto_hardening_runner.py` with `--agent-cmd` and child `- [ ]` target file items (`TRK008` and `TPR008`).</constraint>
    <constraint invariant="pairwise_rule_and_guardrail_orthogonality_mandate">Preserve all required factory and orthogonality tokens (`schema_blast_radius_and_factory_mandate`, `pairwise_rule_and_guardrail_orthogonality_mandate`, `model_factories.py`) in `tier2-execute/SKILL.md` (`SKL003`).</constraint>
    <constraint invariant="dual_axis_documentation_mandate">Strictly preserve the parameterized `/tier7-describe-architecture` command and `#### Directives for Tier 7 Agent:` under `### Documentation &amp; Knowledge Item Update`.</constraint>
    <touched_artifacts>
      <artifact action="MODIFY">@.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md</artifact>
      <artifact action="MODIFY">@.agents/skills/tier1-tracker-generator/SKILL.md</artifact>
      <artifact action="MODIFY">@.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md</artifact>
      <artifact action="MODIFY">@.agents/skills/tier1-plan-tracker-generator/SKILL.md</artifact>
      <artifact action="MODIFY">@.agents/skills/tier2-execute/SKILL.md</artifact>
    </touched_artifacts>
    <action>
      1. In `@[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]`:
         - Under `### Phase 1: [Phase Name]`, keep the `**Plan:**` reference line, `- [ ] **[NOK] Red-Teaming:** /tier0-research-plan ...`, and `- [ ] **[NOK] Execution:** /tier2-execute --full-auto ...` with `  - [ ] Step 1: [Step Title]`. Delete the two redundant lines `- [ ] **[NOK] Test Coverage Assertions:** ...` and `- [ ] **[NOK] Audit:** /tier8-audit-plan ...`.
         - Retain `### Integration Checkpoint: Full-Stack Validation` (`- [ ] **[NOK] Backend &amp; Frontend Full-Stack Integration Gate**`) as its dedicated `###` section header immediately above `### Post-Implementation Gates` so `check_phase_format` lookahead boundaries in `scripts/audit_tracker_output.py` remain intact.
         - Under `### Post-Implementation Gates`, retain `Tier 2 Hardening (Backend)` (`scripts/auto_hardening_runner.py ... --agent-cmd`) and `Tier 2 Hardening (Frontend)` (`scripts/auto_hardening_runner.py ... --agent-cmd`). Delete the 4 redundant prose checkboxes (`Golden Master &amp; Test Restoration Audit`, `Proxy Sunset &amp; Consumer Migration`, `Pre-Delete Audit`, and `Semantic Coverage &amp; Zero-Loss Audit`).
         - Under `## Instructions for the Execution Agent`, update `- **Workflow Loop**:` (line 59) to remove `-> /tier8-audit-plan ->`, producing: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute --full-auto -> Integration Checkpoint &amp; Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`.
         - Retain `### Documentation &amp; Knowledge Item Update` (`/tier7-describe-architecture`) and `### Final Epic Audit` (`/tier8-audit-epic`) unchanged.
      2. In `@[.agents/skills/tier1-tracker-generator/SKILL.md]`:
         - Update `tracker_update_preservation` and Step 2 (`GENERATE OR UPDATE TRACKER`) to match the streamlined `epic_tracker_template.md` (two lifecycle rows per Phase: `Red-Teaming` and `Execution` with indented step checkboxes; dedicated `### Integration Checkpoint: Full-Stack Validation`; `Tier 2 Hardening (Backend &amp; Frontend)` with `--agent-cmd` under `### Post-Implementation Gates`; `Documentation &amp; Knowledge Item Update`; and `Final Epic Audit`), and explicitly instruct UPDATE MODE to strip legacy per-phase `Test Coverage Assertions`, per-phase `Audit: /tier8-audit-plan`, and the 4 removed prose checkboxes when updating existing trackers.
      3. In `@[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]`:
         - Under `## Step Execution Status`, retain the `**Plan:**` reference line, `- [ ] **[NOK] Execution:** /tier2-execute --full-auto ...`, and `  - [ ] Step 1: [Step Title]`. Delete the duplicate `- [ ] **[NOK] Audit:** /tier8-audit-plan ...` line (as `### Final Plan Audit` already runs `/tier8-audit-plan`).
         - Under `### Post-Implementation Gates`, retain `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` with `scripts/auto_hardening_runner.py ... --gate all ... --agent-cmd`. Delete the 3 redundant prose checkboxes (`Golden Master &amp; Test Restoration Audit`, `Pre-Delete Audit`, and `Semantic Coverage &amp; Zero-Loss Audit`).
         - Retain `### Documentation &amp; Knowledge Item Update` and `### Final Plan Audit` unchanged.
      4. In `@[.agents/skills/tier1-plan-tracker-generator/SKILL.md]`:
         - Update `tracker_update_preservation` and Step 2 (`GENERATE OR UPDATE TRACKER`) to align 1:1 with the streamlined `plan_tracker_template.md` and instruct UPDATE MODE to strip duplicate `Audit:` rows under `## Step Execution Status` and the 3 removed prose checkboxes under `### Post-Implementation Gates` when synchronizing existing trackers.
      5. In `@[.agents/skills/tier2-execute/SKILL.md]`:
         - Update the `PLAN WRAP-UP &amp; AUDIT ROUTING` section (`DUAL_MODE_WRAPUP_SYNC`, lines 149-156) so completed `implementation_plan.md` runs route deterministically without per-phase `/tier8-audit-plan`: in Epic Tracker mode when subsequent phases remain `[ ]`, set `Resume Command` to `/tier0-research-plan` targeting the next unexecuted phase plan and Epic tracker; when all implementation phases or standalone plan steps are `[x]`, route sequentially through `### Post-Implementation Gates` (`scripts/auto_hardening_runner.py ... --agent-cmd`), `### Documentation &amp; Knowledge Item Update` (`/tier7-describe-architecture`), and finally `### Final Epic Audit` (`/tier8-audit-epic`) for Epics or `### Final Plan Audit` (`/tier8-audit-plan`) for standalone Plans.
    </action>
    <validation_gate>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py</validation_gate>
  </step>

  <step id="3" name="Step 3: Update Tracker Structural &amp; Parity Auditors, Unit Test Suites, and Self-Hosting Tracker">
    <constraint invariant="strict_pydantic_v2_rust">Enforce `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` on `TrackerDocumentAST` in `scripts/audit_plan_tracker_parity.py`.</constraint>
    <constraint invariant="anti_happy_path_mandate">Maintain positive and negative unit tests covering missing `**Plan:**`, missing `Execution:`, missing indented `Step` items (`TRK002`), missing `### Final Epic Audit` / `### Final Plan Audit` (`TRK001`), and missing `--agent-cmd`, `As-Built Architectural Sync`, or `System 2 Red-Team Audit` (`TPR008`).</constraint>
    <touched_artifacts>
      <artifact action="MODIFY">@scripts/audit_tracker_output.py#L99-L171</artifact>
      <artifact action="MODIFY">@scripts/audit_tracker_output.py#L174-L253</artifact>
      <artifact action="MODIFY">@scripts/audit_plan_tracker_parity.py#L128-L155</artifact>
      <artifact action="MODIFY">@scripts/audit_plan_tracker_parity.py#L294-L455</artifact>
      <artifact action="MODIFY">@scripts/audit_plan_tracker_parity.py#L458-L840</artifact>
      <artifact action="MODIFY">@backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L65-L207</artifact>
      <artifact action="MODIFY">@backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L599-L610</artifact>
      <artifact action="MODIFY">@backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L613-L649</artifact>
      <artifact action="MODIFY">@backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py</artifact>
      <artifact action="MODIFY">@docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md</artifact>
    </touched_artifacts>
    <action>
      1. In `@[scripts/audit_tracker_output.py#L99-L171]` and `@[scripts/audit_tracker_output.py#L174-L253]`:
         - Remove the mandatory `has_audit` check (`TRK002` on missing `- [ ] **[NOK] Audit:**`) from both `check_phase_format` and `check_step_format`, because final audit presence is authoritatively enforced by `check_mandatory_sections` (`### Final Epic Audit` in `TrackerMode.EPIC` and `### Final Plan Audit` in `TrackerMode.PLAN`).
         - Keep `**Plan:** @[...]`, `Execution:`, and indented `Step` checkbox (or deferred `Create Plan`) checks in `TRK002`.
      2. In `@[scripts/audit_plan_tracker_parity.py#L128-L155]`, `@[scripts/audit_plan_tracker_parity.py#L294-L455]`, and `@[scripts/audit_plan_tracker_parity.py#L458-L840]`:
         - Remove `has_golden_master_gate`, `has_pre_delete_gate`, and `has_semantic_coverage_gate` from `TrackerDocumentAST`, `parse_tracker_document`, and `audit_plan_tracker_parity`.
         - Preserve `has_doc_sync_gate`, `has_final_audit_gate`, `has_session_handover`, `has_resume_command`, `has_backend_hardening_agent_cmd`, and `has_frontend_hardening_agent_cmd` (`TPR008` `GuardrailSeverity.FATAL`).
      3. In `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L65-L207]`, `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L599-L610]`, and `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L613-L649]`:
         - Update `test_tracker_audit_direct_helper_functions` so `missing_audit_phase` (streamlined phase without per-phase `Audit:` line) asserts `check_phase_format(missing_audit_phase) == []`, while adding/retaining negative assertions for missing `Execution:` and missing `**Plan:**`.
         - Update `test_plan_mode_step_format_valid` and `test_plan_mode_step_format_missing_components` to verify streamlined `## Step Execution Status` blocks without duplicate `Audit:` lines pass `check_step_format`, while missing `**Plan:**`, missing `Execution:`, or missing indented `Step` lines trigger `TRK002`.
      4. In `@[backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py]`:
         - Update module-level `SAMPLE_TRACKER` (`#L39-L78`) to a valid streamlined tracker containing `Tier 2 Hardening (Backend)` with `--agent-cmd` + child target item `scripts/tool.py`, `As-Built Architectural Sync`, `System 2 Red-Team Audit`, and a `&gt;=10`-character RTM description, and tighten `test_parse_and_parity_clean`, `test_main_cli_success`, and `test_main_cli_auto_infer_plan` to assert `report.passed is True` and `exc_info.value.code == 0` (eradicating `in (0, 1)`).
         - Remove obsolete `Golden Master &amp; Test Restoration Audit`, `Pre-Delete Audit`, and `Semantic Coverage &amp; Zero-Loss Audit` lines across all 6 test functions (`test_non_code_targets_excluded_from_hardening_check`, `test_invalid_extension_and_test_file_in_hardening_checklist`, `test_backend_only_hardening_checklist_without_frontend_gate`, `test_missing_hardening_agent_cmd_triggers_fatal_tpr008`, `test_deleted_targets_excluded_from_required_hardening_checklist`, and `test_deleted_target_included_in_hardening_checklist_triggers_fatal_tpr004`); in `test_backend_only_hardening_checklist_without_frontend_gate`, retain a non-backend top-level `- [ ]` checkbox referencing synthetic `scripts/old_tool.py` immediately after `  - [ ] @[scripts/audit_skills_architecture.py]` so `b_pattern`'s `^-\s+\[[ x]\]\s+` lookahead boundary remains covered.
         - Add explicit negative `TPR008` `FATAL` assertions for missing `As-Built Architectural Sync` (`has_doc_sync_gate`) and missing `System 2 Red-Team Audit` (`has_final_audit_gate`) alongside missing `--agent-cmd` / `--no-agent`.
      5. In `@[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]`:
         - Remove the transitional duplicate `- [ ] **[NOK] Audit:** /tier8-audit-plan ...` line under `## Step Execution Status` and the 3 legacy prose checkboxes (`Golden Master &amp; Test Restoration Audit`, `Pre-Delete Audit`, and `Semantic Coverage &amp; Zero-Loss Audit`) under `### Post-Implementation Gates`, then run both `audit_tracker_output.py --mode plan` and `audit_plan_tracker_parity.py` to dogfood-verify 0 findings on the streamlined self-hosting tracker.
    </action>
    <validation_gate>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --test --ast-strict; uv run --no-sync --offline python scripts/audit_tracker_output.py --tracker docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md --mode plan --plan-file docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md; uv run --no-sync --offline python scripts/audit_plan_tracker_parity.py --plan docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md --tracker docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md</validation_gate>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — Streamlined Epic & Standalone Trackers Pass Structural and Parity Audits):**
  - *Input*: A multi-phase Epic tracker containing `### Phase 1` with `**Plan:**`, `Red-Teaming:`, `Execution:`, and indented `Step 1.1` items (without per-phase `Test Coverage Assertions` or `Audit: /tier8-audit-plan`), `Integration Checkpoint`, `Tier 2 Hardening (Backend & Frontend)` with `scripts/auto_hardening_runner.py ... --agent-cmd` (without `Golden Master`, `Pre-Delete`, or `Semantic Coverage` prose checkboxes), `### Documentation & Knowledge Item Update`, and `### Final Epic Audit`.
  - *Expected Output*: `check_phase_format`, `check_mandatory_sections`, `check_hardening_targets`, and `audit_plan_tracker_parity` return `0` fatal findings (`passed=True`).
- **Scenario 2 (Negative Path 1 — Missing Mandatory Execution or Plan Reference in Phase/Step Block):**
  - *Input*: A tracker phase or step block omitting `**Plan:** @[...]`, `- [ ] **[NOK] Execution:**`, or indented `- [ ] Step` checkboxes.
  - *Expected Output*: `check_phase_format` / `check_step_format` returns `GuardrailSeverity.FATAL` findings with `rule_code == "TRK002"`.
- **Scenario 3 (Negative Path 2 — Missing AI Subagent Hardening `--agent-cmd` or Presence of `--no-agent`):**
  - *Input*: A tracker where `Tier 2 Hardening (Backend)` or `Tier 2 Hardening (Frontend)` omits `--agent-cmd` or passes `--no-agent`.
  - *Expected Output*: `check_hardening_targets` raises `TRK008` (`GuardrailSeverity.FATAL`) and `audit_plan_tracker_parity` raises `TPR008` (`GuardrailSeverity.FATAL`).
- **Scenario 4 (Negative Path 3 — Missing Final Epic/Plan Audit or Tier 7 Doc Sync Gate):**
  - *Input*: A tracker omitting `### Final Epic Audit` / `### Final Plan Audit` (`System 2 Red-Team Audit`) or `As-Built Architectural Sync`.
  - *Expected Output*: `check_mandatory_sections` raises `TRK001` (`GuardrailSeverity.FATAL`) and `audit_plan_tracker_parity` raises `TPR008` (`GuardrailSeverity.FATAL`).

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Skills Architecture & Orthogonality Audit:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py`
- **Targeted Backend Audit Loop:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_tracker_output.py scripts/audit_plan_tracker_parity.py backend_v2/tests/unit/scripts/test_audit_tracker_output.py backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py --test --ast-strict`
- **Global Backend Audit Loop:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
