# Phase 3: Domain & Service Layer Duct-Tape Eradication & Mutation Invariance (QGR020, QGR012, QGR016, QGR002, QGR019, QGR001, QGR003, QGR010)

**Overview:** Systematically eliminate all 913 active advisory AST warning violations across domain models, service layers, LLM adapters, and test fixtures (specifically: 108 QGR020 mutable defaults and duplicate Field assignments, 118 QGR012 duck-typing cascades, 193 QGR016 ternary lazy fallbacks, 341 QGR002 chained dictionary .get calls, 95 QGR001 dynamic reflections, 40 QGR019 in-place dict.pop mutations, 16 QGR003 exception swallowings, and 2 QGR010 naive datetimes), promote each visitor rule to FATAL severity in `@[scripts/_ast_guardrails.py]`, implement the automated AST mutation testing engine in [NEW] `@[scripts/audit_mutation_coverage.py]`, and verify a 100% mutant kill rate on mathematical cores (`UnifiedScoringEngine` and `TopologicalEvaluator`).

**Source:** `@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md#L287-L314]`

**Target Files:**
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[MODIFY]` `@[scripts/audit_warning_baseline.py]`
- `[NEW]` `@[scripts/audit_mutation_coverage.py]`
- `[NEW]` `@[backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`
- `[MODIFY]` `@[backend_v2/utils/scoring/unified_engine.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/topological_evaluator.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py]`
- `[MODIFY]` `@[backend_v2/services/report_service.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/studio.py]`
- `[MODIFY]` `@[backend_v2/models/view/sdui.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/synthesis.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/dag_models.py]`
- `[MODIFY]` `@[backend_v2/models/domain/xai.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/atom_result.py]`
- `[MODIFY]` `@[backend_v2/models/domain/report_artifact.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/finops.py]`
- `[MODIFY]` `@[backend_v2/models/llm.py]`
- `[MODIFY]` `@[backend_v2/models/domain/analyst.py]`
- `[MODIFY]` `@[backend_v2/models/domain/validation.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/sdui_rules.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/base.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]`
- `[MODIFY]` `@[backend_v2/services/blueprint.py]`
- `[MODIFY]` `@[backend_v2/llm/provider.py]`
- `[MODIFY]` `@[backend_v2/utils/static_charts.py]`
- `[MODIFY]` `@[backend_v2/services/document_extraction.py]`
- `[MODIFY]` `@[backend_v2/llm/ingress_pipeline.py]`
- `[MODIFY]` `@[backend_v2/llm/client.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/openai_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/base_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/vertex_adapter.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/audit.py]`
- `[MODIFY]` `@[backend_v2/seed/wipe_user_data.py]`
- `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_matrix_data_integrity.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]` | Permissive `WARNING` severity assignments for QGR020, QGR012, QGR016, QGR002, QGR001, QGR019, QGR003, and QGR010 allowing debt accumulation across runs. | Assign unconditional FATAL severity across all visitor methods for QGR020, QGR012, QGR016, QGR002, QGR001, QGR019, QGR003, and QGR010. | Pruned dynamic severity toggles; visitor methods instantiate `GuardrailViolation` with invariant fatal severity. | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| `@[scripts/audit_warning_baseline.py]` | Permissive warning ceiling (`CURRENT_WARNING_CEILING = 934`) permitting active warnings to survive Phase 3. | Set `CURRENT_WARNING_CEILING = 0`; assert 0 fatal violations and 0 advisory warnings across all 896 modules in `backend_v2`. | Pruned multi-tier warning tolerance calculations; enforce binary zero-defect validation. | `uv run python scripts/audit_warning_baseline.py --verify-zero` |
| `[NEW] @[scripts/audit_mutation_coverage.py]` | Coverage blindness on mathematical cores where executed lines do not prove arithmetic assertion sensitivity. | Implement automated AST mutation testing engine using Python stdlib `ast`: systematically mutates relational operators, arithmetic operators, and conditional branches in `UnifiedScoringEngine` and `TopologicalEvaluator`; runs localized test suites asserting 100% mutant kill rate. | Pruned external heavyweight mutation frameworks (`mutmut`, `cosmic-ray`); lightweight pure AST mutator executing directly in pytest sub-processes. | `uv run python scripts/audit_mutation_coverage.py` |
| `[NEW] @[backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py]` | Untested mutation testing tool infrastructure; unverified mutant generation or detection logic. | Implement dedicated unit test harness asserting operator mutation coverage, mutant survival detection, and report DTO generation. | Pruned redundant mock servers; test AST visitor and mutator directly on synthetic code snippets. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py` |
| Step 3.1: QGR020 Models (`@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/models/view/sdui.py]`, `@[backend_v2/models/dtos/synthesis.py]`, `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/models/domain/xai.py]`, `@[backend_v2/models/dtos/atom_result.py]`) | 108 instances of redundant `= Field(...)` assignments on Annotated fields and class-level mutable defaults (`= []` or `= {}`). | Enforce PEP 593 Annotated typing with `Field(default_factory=list)` or `Field(default_factory=dict)`; strip redundant `= Field(...)` right-hand assignments per `pydantic_annotated_fields_mandate`. | Pruned custom default factory wrappers; use native Pydantic V2 `Field(default_factory=...)`. | `uv run python scripts/_ast_guardrails.py backend_v2/models/ --strict` |
| Step 3.2: QGR012 Services (`@[backend_v2/services/orchestrator/strategies/llm.py]`, `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`, `@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]`, `@[backend_v2/services/blueprint.py]`) | 118 instances of duck-typing `isinstance(..., (dict, Mapping))` cascades and bifurcated dictionary branches. | Enforce single-type method signatures accepting strictly validated Pydantic V2 DTOs; validate incoming raw payloads at ingress via `TypeAdapter` per `no_naked_dicts_in_state`. | Pruned branching fallback adapters; enforce single deterministic execution pipeline per `single_pipeline_invariant_mandate`. | `uv run python scripts/_ast_guardrails.py backend_v2/services/ --strict` |
| Step 3.3: QGR016 Providers & Repositories (`@[backend_v2/llm/provider.py]`, `@[backend_v2/utils/static_charts.py]`, `@[backend_v2/services/document_extraction.py]`, `@[backend_v2/database/repositories/execution.py]`, `@[backend_v2/database/repositories/audit.py]`) | 193 instances of ternary lazy fallbacks (`val or {}`, `val or ""`, `val or []`, `val if val else default`). | Replace loose ternary and binary `or` fallbacks with schema-level defaults or explicit `if val is not None:` null checks per `the_duct_tape_ban`. | Pruned defensive coalescing chains; crash Fail-Fast on missing required parameters. | `uv run python scripts/_ast_guardrails.py backend_v2/llm/provider.py backend_v2/database/repositories/ --strict` |
| Step 3.4: QGR002 Test Suites & Repositories (`@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`, `@[backend_v2/tests/unit/test_matrix_data_integrity.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py]`) | 341 instances of chained `.get()` dictionary calls across test fixtures and domain code. | In tests and domain code, replace `.get(key, default)` with static dot notation on typed DTOs or positive membership indexing `d[k]` guarded by `if k in d:` per `strict_attribute_integrity`. | Pruned dictionary probing; validate payloads into concrete Pydantic schemas before assertion. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/unit/ --strict` |
| Step 3.5: Residual Rules (`@[backend_v2/llm/provider.py]`, `@[backend_v2/llm/client.py]`, `@[backend_v2/database/repositories/audit.py]`, `@[backend_v2/seed/wipe_user_data.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`) | 95 QGR001 dynamic reflection calls, 40 QGR019 in-place `dict.pop()` calls, 16 QGR003 silent exception swallowings, and 2 QGR010 naive datetimes. | Replace `getattr`/`hasattr`/`vars()` with typed attribute access; replace `dict.pop()` with pure dictionary projection; replace exception swallowing with structured logging and re-raise; replace naive datetime with `datetime.now(timezone.utc)`. | Pruned reflection shims; enforce static typing and timezone-aware ISO datetimes. | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |

## Phase 3: Pre-Implementation Cleanups

All technical debt identified across touched files and 1-hop callers is quarantined and queued for pre-implementation resolution:
1. **Model Duplicate Field Cleanups (`backend_v2/models/`)**: 108 instances of redundant `= Field(...)` right-hand assignments on fields with `Annotated[T, Field(...)]` annotations across DTOs and domain entities. Cleaned in Step 3.1.
2. **Duck-Typing Cascade Elimination (`backend_v2/services/orchestrator/`)**: 118 instances of `isinstance(..., Mapping)` in context builder, execution time resolver, and strategy handlers. Cleaned in Step 3.2.
3. **Ternary Fallback Purge (`backend_v2/llm/provider.py`, `backend_v2/database/repositories/`)**: 193 instances of `val or {}`, `val or ""`, and `val or []` masking uninitialized state. Cleaned in Step 3.3.
4. **Test Fixture `.get()` Purge (`backend_v2/tests/unit/`)**: 341 instances of dictionary `.get()` lookups across unit test assertions and data integrity tests. Cleaned in Step 3.4.
5. **Reflection and Mutable Mutation Purge (`backend_v2/llm/`, `backend_v2/tests/fakes/`)**: 95 reflection instances (`getattr`/`hasattr`/`vars`), 40 in-place `dict.pop()` calls, 16 silent exception swallowings, and 2 naive datetimes. Cleaned in Step 3.5.
6. **AST Mutation Testing Infrastructure (`[NEW] @[scripts/audit_mutation_coverage.py]`)**: Build pure Python AST mutation engine verifying 100% mutant kill rate on mathematical cores. Cleaned in Step 3.6.
7. **Warning Baseline Zero Lock (`scripts/audit_warning_baseline.py`)**: Update `CURRENT_WARNING_CEILING` from 934 down to 0, asserting 0 advisory warnings and 0 fatal errors. Cleaned in Step 3.7.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established QGR024, QGR025, clean imports, and the 8-stage audit loop, and Phase 2 eliminated all 319 deceptive mocks, reducing warnings to 913 with 0 FATAL errors in domain code.</action>
    <action>Look forward: Verify that systematically cleaning QGR020, QGR012, QGR016, QGR002, QGR001, QGR019, QGR003, and QGR010 will eliminate all 913 active warnings across all 896 modules before locking each rule to FATAL severity.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/03_phase3_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Clean all 108 QGR020 instances (duplicate Field assignments and mutable class defaults) and promote QGR020 to FATAL severity in scripts/_ast_guardrails.py.</item>
    <item>Clean all 118 QGR012 instances (isinstance Mapping duck-typing cascades) and promote QGR012 to FATAL severity in scripts/_ast_guardrails.py.</item>
    <item>Clean all 193 QGR016 instances (ternary lazy fallbacks and falsy or chains) and promote QGR016 to FATAL severity in scripts/_ast_guardrails.py.</item>
    <item>Clean all 341 QGR002 instances (chained .get lookups in tests and domain code) and promote QGR002 to FATAL severity in scripts/_ast_guardrails.py.</item>
    <item>Clean all residual rules: 95 QGR001 (reflection), 40 QGR019 (dict.pop), 16 QGR003 (exception swallowing), 2 QGR010 (naive datetime) and promote them to FATAL severity.</item>
    <item>Implement automated AST mutation testing script scripts/audit_mutation_coverage.py asserting 100% mutant kill rate on UnifiedScoringEngine and TopologicalEvaluator.</item>
    <item>Implement comprehensive unit test suite in backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py passing 100%.</item>
    <item>Lock CURRENT_WARNING_CEILING = 0 in scripts/audit_warning_baseline.py and update test_audit_warning_baseline.py.</item>
    <item>Mathematically verify 0 FATAL violations and 0 WARNINGS across backend_v2 using uv run python scripts/_ast_guardrails.py backend_v2 --strict.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Inverting default audit loop strictness flag (quarantined for Phase 4).</anti_target>
    <anti_target>Third-party mutation testing frameworks (mutmut, cosmic-ray) - banned per Axis 4.</anti_target>
    <anti_target>Blanket comment suppressions (# noqa: QGR*) in domain code - strictly prohibited per QGR000.</anti_target>
    <anti_target>Deleting test assertions to silence .get() violations - tests must assert against typed models.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/audit_warning_baseline.py]</backend>
    <backend>[NEW] @[scripts/audit_mutation_coverage.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py]</backend>
    <backend>@[backend_v2/utils/scoring/unified_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/topological_evaluator.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/services/report_service.py]</backend>
  </touched_artifacts>

  <step id="3.1" name="Clean and Lock QGR020 (Mutable Class Defaults &amp; Duplicate Field())">
    <action>Audit all 108 QGR020 occurrences across `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/models/view/sdui.py]`, `@[backend_v2/models/dtos/synthesis.py]`, `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/models/domain/xai.py]`, `@[backend_v2/models/dtos/atom_result.py]`, `@[backend_v2/models/domain/report_artifact.py]`, `@[backend_v2/models/dtos/finops.py]`, `@[backend_v2/models/llm.py]`, and related domain files.</action>
    <action>Refactor class attributes: replace redundant `= Field(...)` right-hand assignments on fields with `Annotated[T, Field(...)]` with factory defaults or remove the right-hand assignment; replace class-level mutable defaults (`= []` or `= {}`) with `Field(default_factory=list)` or `Field(default_factory=dict)`.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, update QGR020 severity classification to assign unconditional FATAL severity.</action>
    <action>Verify 0 QGR020 violations remain using `uv run python scripts/_ast_guardrails.py backend_v2/models --strict`.</action>
    <constraint invariant="pydantic_annotated_fields_mandate">All Pydantic models must enforce PEP 593 Annotated fields with zero redundant right-hand Field() calls.</constraint>
  </step>

  <step id="3.2" name="Clean and Lock QGR012 (Duck-Typing isinstance(..., Mapping) Cascades)">
    <action>Audit all 118 QGR012 occurrences across `@[backend_v2/services/orchestrator/strategies/llm.py]`, `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`, `@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]`, `@[backend_v2/services/blueprint.py]`, `@[backend_v2/services/orchestrator/dag_executor.py]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py]`, `@[backend_v2/hooks/scoring/falsifier_hook.py]`, and test files.</action>
    <action>Eliminate bifurcated `if isinstance(val, (dict, Mapping)): ... elif isinstance(val, BaseModel): ...` cascades and `match/case dict` patterns; enforce single-type method signatures accepting strictly validated Pydantic V2 DTOs; validate incoming raw payloads at ingress boundaries via `TypeAdapter`.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, update QGR012 severity classification to assign unconditional FATAL severity.</action>
    <action>Verify 0 QGR012 violations remain using `uv run python scripts/_ast_guardrails.py backend_v2/services --strict`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All execution paths must flow through exactly one sovereign pipeline with zero bifurcated duck-typing branches.</constraint>
  </step>

  <step id="3.3" name="Clean and Lock QGR016 (Ternary Lazy Fallbacks &amp; Falsy or Chains)">
    <action>Audit all 193 QGR016 occurrences across `@[backend_v2/llm/provider.py]`, `@[backend_v2/utils/static_charts.py]`, `@[backend_v2/services/document_extraction.py]`, `@[backend_v2/llm/ingress_pipeline.py]`, `@[backend_v2/database/repositories/execution.py]`, `@[backend_v2/models/dtos/quote_evidence.py]`, `@[backend_v2/services/blueprint.py]`, `@[backend_v2/database/repositories/audit.py]`, and `@[backend_v2/seed/run_seed.py]`.</action>
    <action>Replace `val or {}`, `val or ""`, `val or []`, and `val if val else default` with schema-level defaults or explicit `if val is not None:` null checks per `the_duct_tape_ban`.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, update QGR016 severity classification to assign unconditional FATAL severity.</action>
    <action>Verify 0 QGR016 violations remain using `uv run python scripts/_ast_guardrails.py backend_v2/llm backend_v2/database/repositories --strict`.</action>
    <constraint invariant="the_duct_tape_ban">Never use lazy fallback operators or chain multi-variable fallbacks; fail fast on missing required state.</constraint>
  </step>

  <step id="3.4" name="Clean and Lock QGR002 (Chained Dictionary .get() Lookups in Tests and Domain Code)">
    <action>Audit all 341 QGR002 occurrences across test suites (specifically and exhaustively: `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`, `@[backend_v2/tests/unit/test_matrix_data_integrity.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py]`, `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]`, `@[backend_v2/tests/unit/models/dtos/test_schema_bounds.py]`, `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`) and boundary files (`@[backend_v2/llm/provider.py]`).</action>
    <action>In tests and domain code, replace `.get(key, default)` with static dot notation on typed DTOs or positive membership indexing `d[k]` guarded by `if k in d:` per `strict_attribute_integrity`.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, update QGR002 severity classification to assign unconditional FATAL severity across all file categories.</action>
    <action>Verify 0 QGR002 violations remain using `uv run python scripts/_ast_guardrails.py backend_v2/tests --strict`.</action>
    <constraint invariant="strict_attribute_integrity">Never convert strict dot-notation into dynamic getattr or dictionary .get fallbacks; access attributes directly.</constraint>
  </step>

  <step id="3.5" name="Clean and Lock Residual Rules (QGR001, QGR019, QGR003, QGR010)">
    <action>Audit and eliminate 95 QGR001 instances: replace `getattr`/`hasattr`/`vars()` with typed attribute access across `@[backend_v2/llm/provider.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`, and test files.</action>
    <action>Audit and eliminate 40 QGR019 instances: replace in-place `dict.pop()` calls with pure dictionary projections or immutable model copies across `@[backend_v2/llm/client.py]`, `@[backend_v2/llm/adapters/openai_adapter.py]`, `@[backend_v2/llm/adapters/base_adapter.py]`, and `@[backend_v2/services/orchestrator/strategies/llm.py]`.</action>
    <action>Audit and eliminate 16 QGR003 instances: replace silent exception swallowing with structured logging and explicit `raise` across test suites and `@[backend_v2/llm/provider.py]`.</action>
    <action>Audit and eliminate 2 QGR010 instances: replace naive `datetime.now()` with `datetime.now(timezone.utc)` in `@[backend_v2/database/repositories/audit.py]` and `@[backend_v2/seed/wipe_user_data.py]`.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, update severity classifications for QGR001, QGR019, QGR003, and QGR010 to assign unconditional FATAL severity.</action>
    <action>Verify 0 violations remain across these residual rules using `uv run python scripts/_ast_guardrails.py backend_v2 --strict`.</action>
    <constraint invariant="universal_fail_fast">Every boundary must enforce fail-fast validation with zero silent bypasses or untyped reflection.</constraint>
  </step>

  <step id="3.6" name="Implement Mutation Invariance Verification Engine">
    <action>Create [NEW] `@[scripts/audit_mutation_coverage.py]` implementing a pure Python stdlib AST mutation testing engine.</action>
    <action>The mutation engine must target mathematical cores: `UnifiedScoringEngine` (`@[backend_v2/utils/scoring/unified_engine.py]`) and `TopologicalEvaluator` (`@[backend_v2/services/orchestrator/topological_evaluator.py]`).</action>
    <action>Mutate operators: relational operators (`<` to `<=`, `>` to `>=`, `==` to `!=`), arithmetic operators (`+` to `-`, `*` to `/`), and conditional branches (`if x` to `if not x`).</action>
    <action>Execute localized pytest test suites (`test_unified_engine.py` and `test_topological_evaluator.py`) against each mutated AST; assert 100% mutant kill rate.</action>
    <action>Create [NEW] `@[backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py]` to test the mutation engine itself with positive, boundary, and error partition coverage.</action>
    <constraint invariant="ast_guardrail_mandate">Mathematical engines must prove algorithmic mutation sensitivity without external heavy frameworks.</constraint>
  </step>

  <step id="3.7" name="Synchronize Warning Baseline Ledger to Zero Ceiling &amp; Execute Phase 3 Completion Gate">
    <action>In `@[scripts/audit_warning_baseline.py]`, update `CURRENT_WARNING_CEILING` from 934 down to 0.</action>
    <action>In `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`, update test fixtures and assertions to validate the zero ceiling.</action>
    <action>Run `uv run python scripts/audit_warning_baseline.py --verify-zero` to verify 0 fatal violations and 0 advisory warnings across all 896 modules.</action>
    <action>Execute full repository strict AST audit: `uv run python scripts/_ast_guardrails.py backend_v2 --strict`.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_audit_warning_baseline.py backend_v2/tests/unit/scripts/test_audit_mutation_coverage.py`.</action>
    <action>Execute full 8-stage global completion gate: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
    <constraint invariant="universal_quality_gate">Phase 3 closure requires 100% green status across all 8 stages with zero warnings and zero fatals.</constraint>
  </step>

  <test_contracts>
    <test name="test_mutation_coverage_kills_all_arithmetic_mutants" category="positive">
      <input>scripts/audit_mutation_coverage.py run against UnifiedScoringEngine</input>
      <expected>100% mutant kill rate achieved across arithmetic and boundary mutations</expected>
    </test>
    <test name="test_mutation_coverage_kills_all_topological_mutants" category="positive">
      <input>scripts/audit_mutation_coverage.py run against TopologicalEvaluator</input>
      <expected>100% mutant kill rate achieved across DAG topological mutations</expected>
    </test>
    <test name="test_warning_baseline_ledger_asserts_zero_ceiling" category="positive">
      <input>scripts/audit_warning_baseline.py --verify-zero run against backend_v2</input>
      <expected>Exit code 0, fatal_count == 0, warning_count == 0</expected>
    </test>
    <test name="test_ast_guardrails_strict_asserts_zero_violations" category="positive">
      <input>scripts/_ast_guardrails.py backend_v2 --strict</input>
      <expected>Exit code 0, 0 fatal violations, 0 warnings across all 896 files</expected>
    </test>
    <test name="test_mutation_engine_detects_surviving_mutant" category="negative">
      <input>scripts/audit_mutation_coverage.py run with dummy non-asserting test suite</input>
      <expected>Exit code 1, reports surviving mutants, triggers Fail-Fast</expected>
    </test>
    <test name="test_warning_baseline_fails_on_nonzero_warning_count" category="negative">
      <input>scripts/audit_warning_baseline.py --verify-zero run with simulated warning</input>
      <expected>Exit code 1, is_under_ceiling == False, triggers Fail-Fast</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute AST guardrails check across backend_v2 in strict mode: `uv run python scripts/_ast_guardrails.py backend_v2 --strict`</action>
    <action>Execute mutation testing: `uv run python scripts/audit_mutation_coverage.py`</action>
    <action>Execute warning baseline verification: `uv run python scripts/audit_warning_baseline.py --verify-zero`</action>
    <action>Execute full 8-stage audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
  </validation_gate>
</execution_protocol>
```
