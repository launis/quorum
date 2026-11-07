# Tracker: Schema Blast-Radius, Polyfactory SSOT Synchronization & Pairwise Rule/Guardrail Orthogonality Verification

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] (**Plan:** @[implementation_plan.md])

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] @[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]`
  - [x] Step 0: STRATEGIC ALIGNMENT CHECK
  - [x] Step 1: Phase 1, Step 1: Inject schema_blast_radius_and_factory_mandate & pairwise_rule_and_guardrail_orthogonality_mandate Across Planning and Red-Teaming Skills
  - [x] Step 2: Phase 1, Step 2: Synchronize Tier 2 Execution Skill & Modernity Replacement Matrix
  - [ ] Step 3: Phase 1, Step 3: Implement Automated Pairwise Rule Conflict & Static Checker Orthogonality Verifier in scripts/audit_skills_architecture.py and Unit Tests
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] @[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[scripts/audit_skills_architecture.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic and `@[scripts/audit_skills_architecture.py]`.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_deterministic_hardening_state.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document `schema_blast_radius_and_factory_mandate` and `pairwise_rule_and_guardrail_orthogonality_mandate` across all 6 planning, execution, and red-teaming skills (`PLANNING_AND_EXECUTION_FACTORY_SKILLS`), plus `RuleBlockSpecDTO`, `extract_rule_blocks_from_text`, `verify_candidate_rule_against_all`, and `verify_static_checker_orthogonality` in `@[scripts/audit_skills_architecture.py]`.
     - `@[ki_zero_permissive_typing.md]`: Document cross-checker AST witness orthogonality verification between `scan_source_code_for_guardrails` (`@[scripts/_ast_guardrails.py]`) and `DictEradicationVisitor` (`@[scripts/audit_dict_eradication.py]`) via `CANONICAL_RULE_SYNTAX_WITNESSES`.
     - `@[ki_deterministic_hardening_state.md]`: Document the automated pairwise $O(N^2)$ rule conflict and static checker orthogonality gate (`SKL003`) executed during Stage 10 of `@[scripts/backend_audit_loop.py]`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` under `<module path="scripts/">` to register pairwise rule conflict and static checker orthogonality verification (`RuleBlockSpecDTO`, `verify_candidate_rule_against_all`, `verify_static_checker_orthogonality`) on `audit_skills_architecture.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/01_system_context_and_invariants.md` and `docs/architecture/05_resilience_and_observability.md` describing the pairwise rule conflict detector, static checker syntax witness orthogonality gate, and Polyfactory schema blast-radius governance in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] @[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
  - Skills Architecture & Pairwise Orthogonality Gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/audit_skills_architecture.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Inject `<rule_block id="schema_blast_radius_and_factory_mandate">` and `<rule_block id="pairwise_rule_and_guardrail_orthogonality_mandate">` into `@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `@[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, and `@[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`. | Step 1 | [x] Completed |
| REQ-002 | Inject `pairwise_rule_and_guardrail_orthogonality_mandate` and `schema_blast_radius_and_factory_mandate` into `@[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]` and update Steps 2 and 3 to enforce pairwise one-by-one rule-vs-rule and static-checker orthogonality verification via `scripts/audit_skills_architecture.py`. | Step 1 | [x] Completed |
| REQ-003 | Inject `schema_blast_radius_and_factory_mandate` and `pairwise_rule_and_guardrail_orthogonality_mandate` into `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]` mandating synchronous `backend_v2/tests/factories/model_factories.py` updates, `ModelFactory.build(...)` usage in unit tests, explicit test/fake paths in `backend_audit_loop.py`, and pairwise rule/checker orthogonality verification. | Step 2 | [x] Completed |
| REQ-004 | Update `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]` to ban direct `DomainModel(...)` / `DTO(...)` constructor calls in unit tests in favor of `ModelFactory.build(...)` and mandate pairwise rule/guardrail orthogonality verification (`scripts/audit_skills_architecture.py`). | Step 2 | [x] Completed |
| REQ-005 | Define immutable `RuleBlockSpecDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) and implement `extract_rule_blocks_from_text(content: str, file_path: str) -> list[RuleBlockSpecDTO]` in `@[scripts/audit_skills_architecture.py#L203-L224]` and `@[scripts/audit_skills_architecture.py#L274-L293]`. | Step 3 | [ ] Pending |
| REQ-006 | Implement `verify_candidate_rule_against_all(candidate: RuleBlockSpecDTO, existing_rules: Sequence[RuleBlockSpecDTO]) -> list[SkillsAuditFindingDTO]` and `_check_pairwise_rule_orthogonality` (`C901 <= 10`) in `@[scripts/audit_skills_architecture.py#L772-L849]` to verify every rule block one-by-one against all other rule blocks across `AGENTS.md`, `.agents/rules/*.md`, and `.agents/skills/*/SKILL.md` (`SKL003`). | Step 3 | [ ] Pending |
| REQ-007 | Implement `verify_static_checker_orthogonality(witnesses: Mapping[str, str] = CANONICAL_RULE_SYNTAX_WITNESSES) -> list[SkillsAuditFindingDTO]` (`C901 <= 10`) in `@[scripts/audit_skills_architecture.py]` to validate canonical compliant Python syntax witnesses against both `scan_source_code_for_guardrails` (`scripts._ast_guardrails`) and `DictEradicationVisitor` (`scripts.audit_dict_eradication`). | Step 3 | [ ] Pending |
| REQ-008 | Extract `_check_hardening_skill_coverage` and `_check_planning_and_execution_skill_contracts` (`PLANNING_AND_EXECUTION_FACTORY_SKILLS`, `C901 <= 10`) in `@[scripts/audit_skills_architecture.py#L319-L403]` to enforce `schema_blast_radius_and_factory_mandate`, `pairwise_rule_and_guardrail_orthogonality_mandate`, and `model_factories.py` across all 6 planning/execution/red-teaming skills. | Step 3 | [ ] Pending |
| REQ-009 | Update `_populate_compliant_workspace` and add positive/negative unit tests (`test_scenario_8_negative_missing_schema_blast_radius_and_factory_mandate_skl003`, `test_scenario_9_negative_pairwise_rule_conflict_detection_skl003`, and `test_scenario_10_static_checker_orthogonality_witness_verification_skl003`) in `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L32-L106]` and `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L293-L337]`, passing `backend_audit_loop.py --test --ast-strict` with >90% coverage. | Step 3 | [ ] Pending |

# Session Handover Context

## Achieved
- Completed Tier 0 System 2 Research & Analysis (`/tier0-research-plan`) on the implementation plan with `CONVERGENCE ACHIEVED: 0 architectural defects found`.
- Persisted canonical workspace implementation plan at `@[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]`.
- Generated standardized standalone plan tracker at `@[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]`.

## Learned
- All 9 target files and `#L` line boundaries pass `scripts/audit_markdown_boundaries.py` with `0` findings, and `scripts/audit_technical_debt.py --include-one-hop` returns `0` findings.
- Decomposing `_check_skills_directory` and `_check_rule_budget` into `_check_hardening_skill_coverage`, `_check_planning_and_execution_skill_contracts`, `_check_pairwise_rule_orthogonality`, `verify_candidate_rule_against_all`, and `verify_static_checker_orthogonality` keeps McCabe cyclomatic complexity strictly at `C901 <= 10`.

## Remaining
- Execute Steps 0 through 3 via `/tier2-execute --full-auto`, followed by Post-Implementation Gates (`Tier 2 Hardening (Backend)`, `As-Built Architectural Sync`, and `System 2 Red-Team Audit`).

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md] @[docs/implementationplans/TRACKER_Schema_Blast_Radius_Polyfactory_SSOT_and_Pairwise_Rule_Orthogonality.md]
```

