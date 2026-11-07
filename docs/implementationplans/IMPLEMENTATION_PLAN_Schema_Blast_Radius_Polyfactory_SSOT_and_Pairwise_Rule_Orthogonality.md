<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Schema Blast-Radius, Polyfactory SSOT Synchronization & Pairwise Rule/Guardrail Orthogonality Verification (`schema_blast_radius_and_factory_mandate` & `pairwise_rule_and_guardrail_orthogonality_mandate`)

## 1. Objective & Architectural Background

### Problem Statement & Root Cause Analysis
Currently, `deterministic_testing_delegation` (`@[.agents/rules/00-antigravity-core.md#L82]`) and `hermetic_test_fixtures_mandate` (`@[.agents/rules/01-python-backend.md#L43-L45]`) prohibit raw JSON dictionary mock data (`dict`) in unit tests, instructing agents to use `polyfactory`. However, the planning, execution, and red-teaming playbooks (`@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `@[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, `@[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`, `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]`, and `@[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]`) lack two critical safeguards:

1. **Direct Constructor Blast Radius under `pydantic.mypy` (`--strict`):** When a Pydantic V2 model in `backend_v2/models/` is modified (specifically and exhaustively: adding a required field, removing a silent scalar default under `QGR020` Check 20C, or converting `Field(default_factory=...)` to PEP 593 `Annotated[list[T] | dict[K, V], Field(default_factory=...)]` without an RHS assignment under `QGR020` Check 20B), `pydantic.mypy` treats those fields as mandatory keyword arguments on direct `Model(...)` constructor calls, breaking every test and fake that calls `Model(...)` directly instead of `ModelFactory.build(...)` from `@[backend_v2/tests/factories/model_factories.py]`.
2. **Omitted Factory & Fake Targets in Implementation Plans (`MBD008` / `explicit_scope_write`):** Planning agents modify schemas in `backend_v2/models/` without running `grep_search` for direct `ModelName(` constructor calls across `backend_v2/`, `backend_v2/tests/fakes/`, and `scripts/`, leaving `@[backend_v2/tests/factories/model_factories.py]` and `@[backend_v2/tests/fakes/in_memory_repositories.py]` out of the plan's `[MODIFY]` target table, and omitting modified test/fake file paths from `<validation_gate>` `backend_audit_loop.py` invocations (where `@[pyproject.toml]` otherwise excludes `backend_v2/tests/` from global `mypy` runs).
3. **Syntax Deadlocks Between Mutually Conflicting Rules or Static Checkers:** Two static checkers or architectural rules can demand mutually incompatible syntax when evaluated in isolation (for instance, in Phase 2 `QGR020` Check 20B in `@[scripts/_ast_guardrails.py]` required `Annotated[list[str], Field(default_factory=list)]`, while `DictEradicationVisitor` in `@[scripts/audit_dict_eradication.py]` prohibited `= []` and `= Field(...)`, causing `mypy --strict` / `pydantic.mypy` to treat the field as a required constructor argument on direct `Model(...)` calls). Currently, there is no pairwise $O(N^2)$ rule-vs-rule verification or automated check that tests every new or existing rule one-by-one against all other rules and static AST checkers (`_ast_guardrails.py` and `audit_dict_eradication.py`).

### Target Architecture
1. **Planning, Execution & Red-Teaming Skill Synchronization (`.agents/skills/`):**
   - Inject `<rule_block id="schema_blast_radius_and_factory_mandate">` and `<rule_block id="pairwise_rule_and_guardrail_orthogonality_mandate">` into `@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `@[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, `@[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`, `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]`, and `@[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]`, and update `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]`.
   - Mandate that whenever any rule (`<rule_block>`) or static checker (`QGR*`, `DGR*`, `ZORM*`, `SKL*`, `TD_*`, `DictEradicationVisitor`) is added or modified, it MUST be verified **individually one-by-one against every other rule and static checker** (`_ast_guardrails.py`, `audit_dict_eradication.py`, `audit_technical_debt.py`, `ruff`, and `mypy --strict`).
2. **Automated Pairwise Rule Conflict & Static Checker Orthogonality Engine (`@[scripts/audit_skills_architecture.py#L210-L223]`, `@[scripts/audit_skills_architecture.py#L263-L284]`, `@[scripts/audit_skills_architecture.py#L347-L374]`, & `@[scripts/audit_skills_architecture.py#L772-L849]`):**
   - Create `RuleBlockSpecDTO`, `extract_rule_blocks_from_text`, `verify_candidate_rule_against_all`, `verify_static_checker_orthogonality`, and `_check_pairwise_rule_orthogonality` (each with McCabe complexity `C901 <= 10`) in `@[scripts/audit_skills_architecture.py]`:
     - **All-Pairs Rule Verification ($O(N^2)$ One-by-One):** Extracts every `<rule_block id="...">` across `AGENTS.md`, `.agents/rules/*.md`, and `.agents/skills/*/SKILL.md` and checks each rule $R_i$ individually against every other rule $R_j$ ($j \neq i$) via `verify_candidate_rule_against_all(candidate_rule, existing_rules)` to detect any mandate-vs-ban polarity contradiction (`(R_i.mandatory_constructs & R_j.banned_constructs) | (R_i.banned_constructs & R_j.mandatory_constructs)` within shared domain scopes).
     - **Automated New-Rule Gate & Canonical AST Witness Orthogonality (`verify_static_checker_orthogonality`):** Whenever a new rule or guardrail is added, `SkillsArchitectureAuditor.run_audit()` (which runs automatically in Stage 10 of `@[scripts/backend_audit_loop.py]`) executes `verify_candidate_rule_against_all` on all discovered rules AND validates `CANONICAL_RULE_SYNTAX_WITNESSES` (canonical compliant Python syntax snippets for `QGR020` scalar defaults, `QGR020` `Annotated` `default_factory` via `ModelFactory.build(...)`, and `QGR018` strict `ConfigDict`) against both `scan_source_code_for_guardrails` (`@[scripts/_ast_guardrails.py]`) and `DictEradicationVisitor` (`@[scripts/audit_dict_eradication.py]`), failing fast with `SKL003` if any two checkers demand mutually contradictory syntax.

```python
class RuleBlockSpecDTO(BaseModel):
    """Immutable DTO representing a parsed <rule_block> specification for pairwise conflict auditing."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_id: Annotated[str, Field(min_length=1, description="Rule block identifier")]
    file_path: Annotated[str, Field(min_length=1, description="Workspace-relative file path")]
    banned_constructs: Annotated[
        frozenset[str],
        Field(description="Normalized backticked constructs explicitly banned by this rule"),
    ]
    mandatory_constructs: Annotated[
        frozenset[str],
        Field(description="Normalized backticked constructs explicitly mandated by this rule"),
    ]
```

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/01-python-backend.md]`
- `@[.agents/rules/04_directory_reference.md]`
- `@[scripts/_ast_guardrails.py]`
- `@[scripts/audit_dict_eradication.py]`
- `@[backend_v2/tests/factories/model_factories.py]`
- `@[backend_v2/tests/fakes/in_memory_repositories.py]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY] @[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `[MODIFY] @[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `[MODIFY] @[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, `[MODIFY] @[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`, `[MODIFY] @[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]` | Planning schema mutations without `grep_search` blast-radius mapping or introducing/auditing rules and static guardrails without checking each rule one-by-one against all other rules and static checkers (`_ast_guardrails.py`, `audit_dict_eradication.py`, `mypy --strict`). | Add `<rule_block id="schema_blast_radius_and_factory_mandate">` and `<rule_block id="pairwise_rule_and_guardrail_orthogonality_mandate">` requiring: 1) `grep_search` blast-radius discovery for `ModelName(`, 2) synchronous `[MODIFY]` inclusion of `@[backend_v2/tests/factories/model_factories.py]` and `@[backend_v2/tests/fakes/in_memory_repositories.py]`, 3) `ModelFactory.build(...)` in tests and `<test_contracts>`, 4) explicit test/fake paths in `<validation_gate>`, and 5) pairwise one-by-one verification of every rule/guardrail against all other rules and static checkers. | Zero redundant prose duplication; concise rule blocks enforced across planning and red-teaming skills. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY] @[.agents/skills/tier2-execute/SKILL.md#L22-L60]`, `[MODIFY] @[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]` | Writing brittle direct `DomainModel(...)` or `DTO(...)` constructor calls in unit tests or adding AST guardrails during `/tier2-execute` without verifying pairwise compatibility against `audit_dict_eradication.py` and `mypy --strict`. | Add `<rule_block id="schema_blast_radius_and_factory_mandate">` and `<rule_block id="pairwise_rule_and_guardrail_orthogonality_mandate">` to `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]` and update `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]` to mandate `ModelFactory.build(...)` (`@[backend_v2/tests/factories/model_factories.py]`) and pairwise guardrail orthogonality verification. | Zero changes to `always_on` rule byte budget (`44,741 / 72,000` bytes). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |
| `[MODIFY] @[scripts/audit_skills_architecture.py#L306-L327]`, `[MODIFY] @[scripts/audit_skills_architecture.py#L306-L327]`, `[MODIFY] @[scripts/audit_skills_architecture.py#L306-L327]`, `[MODIFY] @[scripts/audit_skills_architecture.py#L772-L849]`, `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L38-L123]`, `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L292-L307]` | Lack of an automated pairwise rule conflict detector or static checker orthogonality verifier when new rules (`<rule_block>`) or AST guardrails are attached to the repository. | Implement `RuleBlockSpecDTO`, `extract_rule_blocks_from_text`, `verify_candidate_rule_against_all` (checking a new/candidate rule one-by-one against every existing rule), `verify_static_checker_orthogonality` (testing canonical syntax witnesses across `scan_source_code_for_guardrails` and `DictEradicationVisitor`), `_check_pairwise_rule_orthogonality`, and `_check_planning_and_execution_skill_contracts` in `@[scripts/audit_skills_architecture.py]`, with full positive/negative unit test coverage in `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`. | Keep every function and method in `@[scripts/audit_skills_architecture.py]` strictly at McCabe cyclomatic complexity `C901 <= 10`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_skills_architecture.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Pre-flight execution of `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/audit_skills_architecture.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --include-one-hop` returned **0 findings (`PASSED (Clean)`)**. In Step 3, `_check_skills_directory` and `_check_rule_budget` in `@[scripts/audit_skills_architecture.py#L561-L602]` and `@[scripts/audit_skills_architecture.py#L772-L849]` are decomposed into focused helper methods (`_check_hardening_skill_coverage`, `_check_planning_and_execution_skill_contracts`, `_check_pairwise_rule_orthogonality`, `verify_candidate_rule_against_all`, and `verify_static_checker_orthogonality`) so that every function remains strictly at McCabe complexity `C901 <= 10`.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Run `git log --oneline -n 10` and inspect `@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[scripts/audit_skills_architecture.py#L347-L374]`, and `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L38-L123]` to verify current codebase state before applying changes.</action>
  </step>

  <dod_checklist>
    <item>`@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `@[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, `@[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`, and `@[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]` contain `schema_blast_radius_and_factory_mandate` and `pairwise_rule_and_guardrail_orthogonality_mandate` rule blocks.</item>
    <item>`@[.agents/skills/tier2-execute/SKILL.md#L22-L60]` and `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]` enforce `schema_blast_radius_and_factory_mandate` and `pairwise_rule_and_guardrail_orthogonality_mandate`.</item>
    <item>`@[scripts/audit_skills_architecture.py#L306-L327]`, `@[scripts/audit_skills_architecture.py#L306-L327]`, `@[scripts/audit_skills_architecture.py#L306-L327]`, and `@[scripts/audit_skills_architecture.py#L772-L849]` implement `RuleBlockSpecDTO`, `extract_rule_blocks_from_text`, `verify_candidate_rule_against_all`, `verify_static_checker_orthogonality`, `_check_pairwise_rule_orthogonality`, and `_check_planning_and_execution_skill_contracts` (`C901 &lt;= 10`), and `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L38-L123]` and `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L292-L307]` pass with &gt;90% coverage.</item>
  </dod_checklist>

  <anti_targets>
    <file>@[backend_v2/seed/seed_data.json]</file>
    <file>@[pyproject.toml]</file>
    <file>@[.agents/rules/00-antigravity-core.md]</file>
  </anti_targets>

  <touched_artifacts>
    <file>@[.agents/skills/tier0-create-plan/SKILL.md]</file>
    <file>@[.agents/skills/tier0-create-epic/SKILL.md]</file>
    <file>@[.agents/skills/tier1-planner/SKILL.md]</file>
    <file>@[.agents/skills/tier0-research-plan/SKILL.md]</file>
    <file>@[.agents/skills/tier8-red-teaming-audit/SKILL.md]</file>
    <file>@[.agents/skills/tier2-execute/SKILL.md]</file>
    <file>@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]</file>
    <file>@[scripts/audit_skills_architecture.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]</file>
  </touched_artifacts>

  <step id="1" name="Phase 1, Step 1: Inject schema_blast_radius_and_factory_mandate &amp; pairwise_rule_and_guardrail_orthogonality_mandate Across Planning and Red-Teaming Skills">
    <context>
      `@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `@[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, `@[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`, and `@[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]` govern Epic, Plan, and Red-Teaming authoring, but do not currently require `grep_search` blast-radius discovery for direct `ModelName(` constructor calls, `ModelFactory.build(...)` usage in test contracts, or pairwise one-by-one rule-vs-rule and static-checker orthogonality verification.
    </context>
    <demolish>
      Eliminate the planning and auditing blind spots where: (1) schema modifications in `backend_v2/models/` omit `@[backend_v2/tests/factories/model_factories.py]` and `@[backend_v2/tests/fakes/in_memory_repositories.py]` from `[MODIFY]` targets, and (2) rules or static checkers are planned or audited in isolation without checking each rule one-by-one against every other rule and static checker (`_ast_guardrails.py`, `audit_dict_eradication.py`, `mypy --strict`).
    </demolish>
    <constraint invariant="deterministic_testing_delegation">All planned unit tests and test contracts must instantiate domain models and DTOs via centralized `ModelFactory[T]` classes in `backend_v2/tests/factories/model_factories.py` or `.model_validate()` boundary hydration rather than direct `Model(...)` constructors.</constraint>
    <constraint invariant="ast_guardrail_mandate">Every new or modified rule or static guardrail (`QGR*`, `DGR*`, `ZORM*`, `SKL*`, `TD_*`, `DictEradicationVisitor`) must be checked individually one-by-one against all other existing rules and static checkers to prove mutual syntax satisfiability.</constraint>
    <action>
      1. `[MODIFY]` `@[.agents/skills/tier0-create-plan/SKILL.md#L66-L115]`, `@[.agents/skills/tier0-create-epic/SKILL.md#L65-L117]`, `@[.agents/skills/tier1-planner/SKILL.md#L49-L89]`, and `@[.agents/skills/tier0-research-plan/SKILL.md#L50-L95]`: Add `schema_blast_radius_and_factory_mandate` (requiring `grep_search` constructor blast-radius mapping, synchronous `[MODIFY]` inclusion of `backend_v2/tests/factories/model_factories.py` and `backend_v2/tests/fakes/in_memory_repositories.py`, `ModelFactory.build(...)` in tests and test contracts, and explicit test/fake paths in validation gates) and `pairwise_rule_and_guardrail_orthogonality_mandate` (requiring that whenever a plan or epic introduces or modifies a rule or static checker, each rule MUST be verified one-by-one against every other rule and static checker via `scripts/audit_skills_architecture.py` and canonical syntax probes across `_ast_guardrails.py`, `audit_dict_eradication.py`, and `mypy --strict`).
      2. `[MODIFY]` `@[.agents/skills/tier8-red-teaming-audit/SKILL.md#L63-L79]`: Add `pairwise_rule_and_guardrail_orthogonality_mandate` and `schema_blast_radius_and_factory_mandate`, and update Steps 2 and 3 so Red-Team audits of `.agents/rules/*.md` or `.agents/skills/*/SKILL.md` compare every rule block individually one-by-one against all other rules and static checkers (`_ast_guardrails.py`, `audit_dict_eradication.py`, `mypy --strict`) and execute `uv run python scripts/audit_skills_architecture.py`.
    </action>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py`
    </validation_gate>
  </step>

  <step id="2" name="Phase 1, Step 2: Synchronize Tier 2 Execution Skill &amp; Modernity Replacement Matrix">
    <context>
      `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]` and `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]` govern code, guardrail, and test authoring during `/tier2-execute`.
    </context>
    <demolish>
      Replace permissive test instantiation guidance in `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]` and `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]` that allowed direct multi-field `DomainModel(...)` / `DTO(...)` constructor calls in unit tests or unverified single-checker AST guardrail additions.
    </demolish>
    <constraint invariant="hermetic_test_fixtures_mandate">Unit tests must instantiate domain models and DTOs via `ModelFactory[T]` in `backend_v2/tests/factories/model_factories.py` or `.model_validate()` boundary hydration.</constraint>
    <action>
      1. `[MODIFY]` `@[.agents/skills/tier2-execute/SKILL.md#L22-L60]`: Add `schema_blast_radius_and_factory_mandate` and `pairwise_rule_and_guardrail_orthogonality_mandate` rule blocks mandating synchronous updates to `backend_v2/tests/factories/model_factories.py`, `ModelFactory.build(...)` usage in unit tests, explicit test/fake file paths in `backend_audit_loop.py`, and automatic pairwise rule/checker orthogonality verification via `scripts/audit_skills_architecture.py` whenever rules or AST guardrails are added or modified.
      2. `[MODIFY]` `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md#L35-L44]`: Add a row to `## 1. Quorum 2026 Modernity Replacement Matrix` banning direct `DomainModel(...)` / `DTO(...)` constructor calls in unit tests in favor of `ModelFactory.build(...)` from `backend_v2/tests/factories/model_factories.py`, and update `## 2. Scoped Boy Scout Technical Debt Checklist` to require pairwise rule/guardrail orthogonality verification (`scripts/audit_skills_architecture.py`) and passing modified test/fake files to `scripts/backend_audit_loop.py`.
    </action>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py`
    </validation_gate>
  </step>

  <step id="3" name="Phase 1, Step 3: Implement Automated Pairwise Rule Conflict &amp; Static Checker Orthogonality Verifier in scripts/audit_skills_architecture.py and Unit Tests">
    <context>
      `@[scripts/audit_skills_architecture.py#L393-L432]`, `@[scripts/audit_skills_architecture.py#L393-L432]`, `@[scripts/audit_skills_architecture.py#L393-L432]`, and `@[scripts/audit_skills_architecture.py#L772-L849]` run automatically in Stage 10 of `@[scripts/backend_audit_loop.py]`. Adding an automated pairwise rule conflict verifier (`verify_candidate_rule_against_all` and `_check_pairwise_rule_orthogonality`) plus an executable static checker witness verifier (`verify_static_checker_orthogonality`) guarantees that every existing and newly attached rule is checked one-by-one against all other rules and static checkers (`_ast_guardrails.py` and `audit_dict_eradication.py`).
    </context>
    <demolish>
      Decompose inline checks in `_check_skills_directory` (`@[scripts/audit_skills_architecture.py#L561-L602]`) and `_check_rule_budget` (`@[scripts/audit_skills_architecture.py#L772-L849]`) into dedicated low-complexity helper methods (`C901 &lt;= 10`) and eliminate unverified rule/checker additions.
    </demolish>
    <constraint invariant="ast_guardrail_mandate">Enforce pairwise rule-vs-rule polarity checks and AST guardrail witness orthogonality statically in `scripts/audit_skills_architecture.py` with McCabe cyclomatic complexity `C901 &lt;= 10` per function.</constraint>
    <constraint invariant="anti_happy_path_mandate">Include positive, negative, and boundary unit test assertions in `backend_v2/tests/unit/scripts/test_audit_skills_architecture.py` covering pairwise rule block contradictions, static checker witness conflicts, and missing skill contracts.</constraint>
    <action>
      1. `[MODIFY]` `@[scripts/audit_skills_architecture.py#L210-L223]`, `@[scripts/audit_skills_architecture.py#L263-L284]`, `@[scripts/audit_skills_architecture.py#L347-L374]`, and `@[scripts/audit_skills_architecture.py#L772-L849]`:
         - Define `RuleBlockSpecDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) encapsulating `rule_id`, `file_path`, `banned_constructs: frozenset[str]`, and `mandatory_constructs: frozenset[str]`.
         - Implement `extract_rule_blocks_from_text(content: str, file_path: str) -&gt; list[RuleBlockSpecDTO]` to extract rule block definitions and parse backticked constructs from banned pattern / `NEVER (use|call|invoke|import|write|allow|combine)` clauses vs. mandatory pattern / `(ALWAYS|MUST) (exclusively )?(use|call|invoke|import|enforce)` clauses.
         - Implement `verify_candidate_rule_against_all(candidate: RuleBlockSpecDTO, existing_rules: Sequence[RuleBlockSpecDTO]) -&gt; list[SkillsAuditFindingDTO]` to compare a candidate or newly attached rule individually one-by-one against every rule in `existing_rules` within shared domain scopes, emitting `SKL003` whenever `(candidate.mandatory_constructs &amp; other.banned_constructs) | (candidate.banned_constructs &amp; other.mandatory_constructs)` is non-empty.
         - Implement `verify_static_checker_orthogonality(witnesses: Mapping[str, str] = CANONICAL_RULE_SYNTAX_WITNESSES) -&gt; list[SkillsAuditFindingDTO]` to run `scan_source_code_for_guardrails` (`scripts._ast_guardrails`) and `DictEradicationVisitor` (`scripts.audit_dict_eradication`) against canonical compliant Python syntax witnesses (specifically covering `QGR020` `Annotated` scalar defaults, `QGR020` `Annotated[list[str], Field(default_factory=list)]` without `= []` or `= Field(...)`, and `QGR018` `ConfigDict(strict=True, extra="forbid", frozen=True)`), emitting `SKL003` if any static checker rejects another rule's mandated compliant syntax.
         - Wire `_check_pairwise_rule_orthogonality` into `SkillsArchitectureAuditor.run_audit()` so every rule block across `AGENTS.md`, `.agents/rules/*.md`, and `.agents/skills/*/SKILL.md` is verified pairwise against all other rules and `verify_static_checker_orthogonality()` is executed on every audit run.
         - Extract `_check_hardening_skill_coverage` and `_check_planning_and_execution_skill_contracts` (`PLANNING_AND_EXECUTION_FACTORY_SKILLS = ("tier0-create-epic", "tier0-create-plan", "tier0-research-plan", "tier1-planner", "tier2-execute", "tier8-red-teaming-audit")`) to verify `schema_blast_radius_and_factory_mandate`, `pairwise_rule_and_guardrail_orthogonality_mandate`, and `model_factories.py` across all 6 skills.
      2. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L38-L123]` and `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py#L292-L307]`:
         - Update `_populate_compliant_workspace` to include `schema_blast_radius_and_factory_mandate`, `pairwise_rule_and_guardrail_orthogonality_mandate`, and `model_factories.py` in generated planning/execution/red-teaming `SKILL.md` fixtures.
         - Add unit tests verifying: (a) `test_scenario_8_negative_missing_schema_blast_radius_and_factory_mandate_skl003`, (b) `test_scenario_9_negative_pairwise_rule_conflict_detection_skl003` (verifying both `verify_candidate_rule_against_all` when attaching a conflicting new rule block and full all-pairs detection in `SkillsArchitectureAuditor.run_audit()`), and (c) `test_scenario_10_static_checker_orthogonality_witness_verification_skl003` (verifying that `verify_static_checker_orthogonality()` passes on canonical witnesses and emits `SKL003` when a witness violates `_ast_guardrails.py` or `DictEradicationVisitor`).
    </action>
    <test_contracts>
      <contract name="test_scenario_1_happy_path_valid_skills_and_rule_budget" category="positive">
        <input>Compliant workspace containing all 29 skills where `tier0-create-epic`, `tier0-create-plan`, `tier0-research-plan`, `tier1-planner`, `tier2-execute`, and `tier8-red-teaming-audit` declare `schema_blast_radius_and_factory_mandate`, `pairwise_rule_and_guardrail_orthogonality_mandate`, and `model_factories.py`, and all rule block definitions and `CANONICAL_RULE_SYNTAX_WITNESSES` are mutually orthogonal.</input>
        <expected>`SkillsArchitectureAuditor(repo_root=tmp_path).run_audit()` returns 0 findings and `main(["--repo-root", str(tmp_path)]) == 0`.</expected>
      </contract>
      <contract name="test_scenario_9_negative_pairwise_rule_conflict_detection_skl003" category="negative">
        <input>Rule A in `.agents/rules/00-antigravity-core.md` bans `legacy_helper()` while newly attached Rule B in `.agents/rules/01-python-backend.md` mandates `legacy_helper()`.</input>
        <expected>`verify_candidate_rule_against_all` and `SkillsArchitectureAuditor(repo_root=tmp_path).run_audit()` emit a `SKL003` pairwise rule conflict finding identifying `legacy_helper()` and both conflicting rule IDs.</expected>
      </contract>
      <contract name="test_scenario_10_static_checker_orthogonality_witness_verification_skl003" category="negative">
        <input>`verify_static_checker_orthogonality` invoked with a synthetic witness containing a duplicate `= Field(...)` assignment on an `Annotated[list[str], Field(default_factory=list)]` field (`items: Annotated[list[str], Field(default_factory=list)] = Field(default_factory=list)`).</input>
        <expected>`verify_static_checker_orthogonality` detects the cross-checker violation from `DictEradicationVisitor` / `scan_source_code_for_guardrails` and returns a `SKL003` finding.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_skills_architecture.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict`
    </validation_gate>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — `test_scenario_1_happy_path_valid_skills_and_rule_budget`):** Compliant `.agents/skills/` and `.agents/rules/` workspace with zero pairwise `<rule_block>` conflicts and 100% orthogonal `CANONICAL_RULE_SYNTAX_WITNESSES` -> `SkillsArchitectureAuditor.run_audit()` returns `findings == []` and CLI returns exit code `0`.
- **Scenario 2 (Negative Path 1 — `test_scenario_8_negative_missing_schema_blast_radius_and_factory_mandate_skl003`):** `.agents/skills/tier0-create-plan/SKILL.md` missing `schema_blast_radius_and_factory_mandate` or `pairwise_rule_and_guardrail_orthogonality_mandate` and `.agents/skills/tier2-execute/SKILL.md` missing `model_factories.py` -> `SkillsArchitectureAuditor.run_audit()` emits `SKL003` violations and CLI returns exit code `1`.
- **Scenario 3 (Negative Path 2 — `test_scenario_9_negative_pairwise_rule_conflict_detection_skl003`):** Attaching a new `<rule_block>` whose `<mandatory_pattern>` (`ALWAYS use \`legacy_helper()\``) contradicts an existing rule's `<banned_pattern>` (`NEVER use \`legacy_helper()\``) -> `verify_candidate_rule_against_all` and `SkillsArchitectureAuditor.run_audit()` emit `SKL003` identifying the exact conflicting pair.
- **Scenario 4 (Negative Path 3 / Cross-Checker Orthogonality — `test_scenario_10_static_checker_orthogonality_witness_verification_skl003`):** Passing a syntax witness that violates `DictEradicationVisitor` (`duplicate_field_assignments` or `mutable_defaults`) or `scan_source_code_for_guardrails` (`QGR020`) to `verify_static_checker_orthogonality()` -> emits `SKL003` fail-fast.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Localized & Skills Architecture Audit Gate:**
  `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_skills_architecture.py backend_v2/tests/unit/scripts/test_audit_skills_architecture.py --test --ast-strict`
- **Global Backend Audit Loop:**
  `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:**
  `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

