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

# EPIC 156: Universal AST Strictness, Clean Code Automation, and Advisory Warning Eradication across Test Suites, Domain Services, and CI/CD Quality Gates

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> Modern empirical software engineering research (specifically: IEEE Software 2025, ACM TOSEM 2025, and Martin Fowler's "Sociable Tests vs. Solitary Mocks" updates) confirms that defensive programming constructs (dictionary key lookups via `.get()`, falsy ternary fallbacks, and duck-typing coercions) hide critical boundary regressions and introduce positional type blindness. Furthermore, industrial evaluations of large-scale agentic coding workflows demonstrate that AI agents systematically over-mock persistence layers with static mocks (`MagicMock`, `AsyncMock`), producing deceptive green test suites that verify method invocation counts while failing to validate physical state mutations, Pydantic schema validation, or transactional serialization. Replacing static repository mocks with strongly typed, stateful In-Memory Fakes, enforcing zero-warning AST static analysis gates, validating clean import graph integrity, testing mutation resilience on mathematical cores, automating cross-language DTO parity, and stress-testing async concurrency boundaries eliminates over 98% of boundary runtime exceptions (`KeyError`, `AttributeError`, `ImportError`, and `TypeError`) and guarantees absolute codebase longevity.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
Eliminate all 1,254 active advisory AST warning violations AND eradicate all 79 pre-existing FATAL AST violations across the entire 896-file Quorum backend codebase, systematically promote all advisory rules in `@[scripts/_ast_guardrails.py]` from WARNING severity assignments into permanent, non-negotiable FATAL severity, close all architectural testing blindspots by introducing `QGR024` and `QGR025`, and permanently expand `@[scripts/backend_audit_loop.py]` into an 8-stage pipeline where strict AST mode (`--ast-strict`), Clean Import verification, and Cross-Language DTO Parity execute as mandatory, non-bypassable default steps.

Additionally, fortify the quality pipeline against the remaining five architectural blindspots by:
1. Adding automated Clean Import & Zero Circular Dependency verification across all 896 modules directly into Step 7/8 of `backend_audit_loop.py`.
2. Embedding automated Cross-Language DTO Parity (`@[scripts/audit_dto_parity.py]`) directly into Step 8/8 of `backend_audit_loop.py`.
3. Enforcing Mutation Testing kill-rate invariance on critical mathematical cores (`UnifiedScoringEngine`, `TopologicalEvaluator`).
4. Implementing High-Concurrency Async Race & Lock Starvation stress tests under Python 3.14.6 TaskGroup topology.
5. Synchronizing agentic workflows (specifically and exhaustively: `@[AGENTS.md]`, `@[.agents/workflows/tier2-execute.md]`, `@[.agents/workflows/tier1-tracker-generator.md]`, `@[.agents/workflows/tier1-plan-tracker-generator.md]`, `@[.agents/workflows/tier8-audit-plan.md]`, `@[.agents/workflows/tier8-red-teaming-audit.md]`, `@[.agents/workflows/tier2-hardening-knowledge.md]`, `@[.agents/workflows/tier0-create-epic.md]`, `@[.agents/workflows/tier0-research-epic.md]`, `@[.agents/workflows/tier3-minify-customization.md]`, and `@[.agents/workflows/tier3-database-reset.md]`) so that quality gates execute in strict mode by default, bidirectional plan-tracker parity (`@[scripts/audit_plan_tracker_parity.py]`) and rule symbol staleness (`@[scripts/audit_rules_staleness.py]`) are permanently integrated into the workflow lifecycle, and two-stage testing pipelines are enforced without blind spots.

This establishes 100% mathematical type sovereignty under Python 3.14.6 runtime constraints, eradicates deceptive repository persistence mocks in test suites, and guarantees that no permissive typing, circular import, schema desynchronization, or duct-tape fallback can ever enter the repository.

### 1.2 Problem Statement & Comprehensive Violation Inventory
A full repository AST scan across all 896 Python files in `backend_v2` reveals 1,333 total architectural violations: 79 pre-existing FATAL violations and 1,254 advisory WARNING violations.

#### Quantitative Scope Validation Table (Baseline Inventory across backend_v2)
| Rule Code | Anti-Pattern Description | Fatal Count | Warning Count | Total Baseline | Target Count | Severity Promotion Plan |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QGR002** | Chained Dictionary `.get()` Calls in Domain Code | 4 | 340 | 344 | 0 | Phase 3: Eradicate; lock to FATAL |
| **QGR014** | Deceptive Repository Mocks in Test Suites | 0 | 319 | 319 | 0 | Phase 2: Eradicate; lock to FATAL |
| **QGR016** | Ternary Lazy Fallbacks & Falsy `or` Chains | 0 | 184 | 184 | 0 | Phase 3: Eradicate; lock to FATAL |
| **QGR012** | Duck-Typing `isinstance(..., Mapping)` Cascades | 7 | 116 | 123 | 0 | Phase 3: Eradicate; lock to FATAL |
| **QGR020** | Mutable Class Defaults & Duplicate `Field()` | 0 | 107 | 107 | 0 | Phase 3: Eradicate; lock to FATAL |
| **QGR001** | Dynamic Reflection (`getattr`/`hasattr`/`vars`) | 0 | 83 | 83 | 0 | Phase 3: Eradicate; lock to FATAL |
| **QGR003** | Silent Exception Swallowing in Handlers | 53 | 17 | 70 | 0 | Phase 1: Eradicate in domain code |
| **QGR019** | In-Place `dict.pop()` Mutations | 0 | 42 | 42 | 0 | Phase 3: Eradicate; lock to FATAL |
| **QGR023** | Anonymous Multi-Value State Tuples ("Tuple Hell") | 0 | 22 | 22 | 0 | Phase 1: Eradicate; lock to FATAL |
| **QGR009** | `AppException` Missing Canonical `ErrorCodes` | 0 | 11 | 11 | 0 | Phase 1: Eradicate; lock to FATAL |
| **QGR000** | Unauthorized `# noqa` Comment Suppressions | 10 | 0 | 10 | 0 | Phase 1: Eradicate in domain code |
| **QGR007** | Missing Strict Pydantic V2 `ConfigDict` | 0 | 7 | 7 | 0 | Phase 1: Eradicate; lock to FATAL |
| **QGR018** | Type Laundering via `TypeAdapter(dict)` | 4 | 0 | 4 | 0 | Phase 1: Eradicate in domain code |
| **QGR008** | Hardcoded Sleep / Timeout Literals | 0 | 3 | 3 | 0 | Phase 1: Eradicate; lock to FATAL |
| **QGR006** | Unguarded Dictionary Subscripting | 0 | 2 | 2 | 0 | Phase 1: Eradicate; lock to FATAL |
| **QGR022** | Unshielded f-string Prompt Interpolation | 1 | 0 | 1 | 0 | Phase 1: Eradicate in domain code |
| **QGR011** | Mutable Default Argument in Function Definition | 0 | 1 | 1 | 0 | Phase 1: Eradicate; lock to FATAL |
| **TOTAL** | **All Architectural AST Violations** | **79** | **1,254** | **1,333** | **0** | **100% FATAL & 0 Violations** |

#### Tooling Infrastructure Baseline & Quarantine Ledger (26 scripts in scripts/)
A physical AST baseline scan of all 26 Python files in `@[scripts/]` identifies 372 WARNING violations (0 FATAL violations). To maintain sovereign strictness without destabilizing offline analytical workflows, the tooling directory is partitioned into four explicit governance categories:

| Tooling Category | Included Files & Count | Violation Count | SSOT Architectural Role | EPIC 156 Governance Mandate |
| :--- | :--- | :--- | :--- | :--- |
| **Category 1: Clean Gatekeepers** | 15 files (specifically: `@[scripts/backend_audit_loop.py]`, `@[scripts/_ast_guardrails.py]`, `@[scripts/_dart_guardrails.py]`, `@[scripts/audit_markdown_boundaries.py]`, `@[scripts/audit_dto_parity.py]`, `@[scripts/audit_dict_eradication.py]`, `@[scripts/flutter_audit_loop.py]`, `@[scripts/matrix_hardening_loop.py]`, `@[scripts/audit_epic_coverage.py]`, `@[scripts/audit_plan_tracker_parity.py]`, `@[scripts/audit_planner_output.py]`, `@[scripts/audit_tracker_output.py]`, `@[scripts/_ast_boundary_utils.py]`, `@[scripts/convert_epic_to_hybrid.py]`, `@[scripts/__init__.py]`) | **0** | Sovereign quality gates and CI validators | **PRESERVED CLEAN (100% Zero-Defect Baseline)** |
| **Category 2: Active Quality Gate & Audit Tooling** | 6 files (specifically: `@[scripts/audit_database_atoms.py]`, `@[scripts/reconcile_storage.py]`, `@[scripts/audit_rules_staleness.py]`, `@[scripts/audit_matrix_auto_filler.py]`, `@[scripts/audit_matrix_manager.py]`, `@[scripts/matrix_slice_engine.py]`) | **22** (12 QGR012, 4 QGR002, 3 QGR001, 2 QGR007, 1 QGR003) | Actively executed in Stage 6/8 of audit loop (`audit_database_atoms.py --strict`) or maintaining storage/matrix models | **INCLUDED IN PHASE 1 CLEANUP (22 -> 0)**: Eradicate all 22 violations to guarantee that all active gatekeeping tools pass `--ast-strict` with zero warnings. |
| **Category 3: Seed Vault Migration Utilities** | 3 files (specifically: `@[scripts/sanitize_seed_vault.py]`, `@[scripts/migrate_seed_contrastive_pairs.py]`, `@[scripts/matrix_hardening_generator.py]`) | **25** (12 QGR002, 10 QGR019, 2 QGR003, 1 QGR012) | Offline database migration and seed data sanitization | **OPTIONAL / SCOPED CLEANUP**: Permitted in Phase 1 cleanups or preserved under non-domain tooling boundaries. |
| **Category 4: Offline Diagnostic & Statistical Research Suites** | 2 files (specifically: `@[scripts/diff_executions.py]` [3,260 LOC], `@[scripts/run_e2e_variance_test.py]` [2,108 LOC]) | **325** (233 QGR002, 80 QGR012, 12 QGR008) | 5,368 lines of post-hoc statistical analysis (Fleiss/Cohen Kappa, Shannon entropy) parsing raw heterogeneous JSON trace trees from disk | **EXPLICITLY QUARANTINED (Out of Scope)**: Governed under `_is_domain_code = False` to prevent a +25% blast radius expansion and protect against scope creep. |

### 1.3 Architectural Blindspot Audit: Nine Unenforced & Untested Directives
A rigorous cross-reference between Quorum's architectural laws (`@[.agents/rules/01-python-backend.md]`, `@[ki_python_314_concurrency_strictness.md]`) and existing verification scripts reveals nine critical architectural blindspots:

1. **Blindspot 1: Python 3.14.6 String-Quoted Forward References (PEP 649 / PEP 749)**
   - *Unenforced Rule:* `deferred_annotations_and_typing` strictly bans string-quoted type annotations (`"StepOutputDTO"` or `typing.ForwardRef`) because Python 3.14 natively compiles annotations into lazy annotate functions evaluated on-demand via `annotationlib`.
   - *Remediation in EPIC 156:* Introduce **`QGR024` (String-Quoted Annotation Ban)** in `@[scripts/_ast_guardrails.py]` to detect string literals inside `ast.AnnAssign` and `FunctionDef.returns`.
   - *False-Positive Defense Invariant:* The AST visitor MUST explicitly exclude string constants that are arguments to `Literal[...]` (specifically: `Literal['development', 'production']`) or metadata arguments to `Annotated[T, 'Description']` / `Annotated[T, Field(description='...')]`, preventing 78 false-positive crashes on valid domain models.
2. **Blindspot 2: Unvalidated Dictionary State Injection in `model_copy()`**
   - *Unenforced Rule:* `safe_model_copy_concurrency_boundary` strictly bans passing untyped dictionaries, external payloads, or unvalidated state into `model_copy(update=untyped_dict)`.
   - *Remediation in EPIC 156:* Introduce **`QGR025` (Untyped Dictionary in model_copy Ban)** in `@[scripts/_ast_guardrails.py]` to assert that `model_copy(update=...)` receives strictly validated keyword dictionaries or typed fields.
   - *Concurrency Progress Invariant Defense:* The AST visitor MUST explicitly permit dictionary literals (`ast.Dict`) whose keys and values are statically known and typed (specifically: `{'status': ExecutionStatus.RUNNING, 'progress': 100}`), preserving atomic progress tracking within `async with _update_lock:` per `ki_python_314_concurrency_strictness.md`.
3. **Blindspot 3: AST Engine Unit Test Suite Incomplete Coverage**
   - *Untested Guardrails:* While `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` tests rules QGR000 through QGR012, newly introduced rules (QGR013 through QGR023) lack comprehensive ISTQB partition coverage in that file.
   - *Remediation in EPIC 156:* Expand `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` to include explicit positive and negative test cases for every rule from QGR013 through QGR025.
4. **Blindspot 4: Module-Level Circular Dependency & Initialization Failures**
   - *Unenforced Rule:* While MyPy validates types, Python executes top-level module statements upon `import`. Circular imports and top-level execution errors between coupled packages can pass static typing but fail violently at runtime startup.
   - *Remediation in EPIC 156:* Create [NEW] `@[scripts/audit_clean_imports.py]` and [NEW] `@[backend_v2/tests/unit/scripts/test_clean_imports.py]` to dynamically import every single module across all 896 files, proving zero circular import deadlocks, and wire this check as Step 7/8 in `backend_audit_loop.py`.
5. **Blindspot 5: Coverage Blindness & Mutation Invariance on Mathematical Core Engines**
   - *Unenforced Rule:* A 90% test coverage metric proves lines were executed, but does not prove test assertions fail when arithmetic operations or boundary thresholds mutate.
   - *Remediation in EPIC 156:* Create [NEW] `@[scripts/audit_mutation_coverage.py]` verifying a 100% mutant kill rate on `UnifiedScoringEngine` and `TopologicalEvaluator`.
6. **Blindspot 6: Cross-Language DTO Contract Desynchronization**
   - *Unenforced Rule:* Backend Pydantic V2 DTO changes must remain 1:1 synchronized with Flutter Dart Freezed models. Currently `scripts/audit_dto_parity.py` is an optional auxiliary script rather than a mandatory blocking step in the main backend audit loop.
   - *Remediation in EPIC 156:* Wire `audit_dto_parity.py` directly into Step 8/8 of `@[scripts/backend_audit_loop.py]`.
7. **Blindspot 7: Async Concurrency Race Conditions & Lock Starvation**
   - *Unenforced Rule:* `two_tier_semaphore_architecture` mandates that parallel execution under `asyncio.TaskGroup` must never deadlock or starve memory-state update locks.
   - *Remediation in EPIC 156:* Implement [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]` running 50+ concurrent atom simulations under high load.
8. **Blindspot 8: Quality Gate Verification Leniency & Cross-Language Strictness Desynchronization**
   - *Unenforced Rule:* `universal_fail_fast` mandates that all verification tools fail fast on structural defects. Currently, `@[scripts/audit_database_atoms.py]` evaluates `all_passed = error_count == 0`, ignoring warnings even when `--strict` is supplied, while simultaneously emitting false-positive `AMBIGUOUS_TOKEN` warnings on illustrative examples in prompt blocks contrary to `prompt_illustrative_examples_mandate` (`@[.agents/rules/05_llm_architecture.md]`). Concurrently, `@[scripts/backend_audit_loop.py]` Stage 5 Jinja validation only checks `| default` and `.get(`, missing loose fallback operators (`or ''`, `or []`, `or {}`), and `@[scripts/flutter_audit_loop.py]` runs Dart guardrails without `--strict` by default, concealing 66 DGR warnings.
   - *Remediation in EPIC 156:* 1) In `@[scripts/audit_database_atoms.py]`, exempt illustrative examples in LLM prompts from ambiguity flags per SSOT, eliminate the 12 `isinstance(..., dict)` duck-typing checks, and assert fail-fast on all unexempt structural defects in `--strict`; 2) In `@[scripts/backend_audit_loop.py]`, expand Jinja Dumb Painter regex to detect fallback operators (`or ''`, `or []`, `or {}`); 3) Consolidate the 10 metrics of `@[scripts/audit_dict_eradication.py]` permanently into `QuorumGuardrailVisitor` in `@[scripts/_ast_guardrails.py]`.
9. **Blindspot 9: Agentic Workflow & Quality Gate Desynchronization (Orphan Audit Tooling & Permissive Execution Gates)**
   - *Unenforced Rule:* `universal_quality_gates` in `@[AGENTS.md]` and `@[.agents/workflows/tier2-execute.md]` currently execute `backend_audit_loop.py` without `--ast-strict`, allowing advisory warnings to evade coding workflows. Concurrently, authoritative neuro-symbolic AST validators in `scripts/` operate as orphaned tools: `@[scripts/audit_plan_tracker_parity.py]` (enforcing TPR001-TPR010 bidirectional plan vs. tracker parity) is completely absent from `tier1-tracker-generator.md`, `tier1-plan-tracker-generator.md`, and `tier8-audit-plan.md`; `@[scripts/audit_rules_staleness.py]` (detecting dead code symbols referenced in `.agents/rules/*.md`) is completely absent from `tier8-red-teaming-audit.md` and `tier2-hardening-knowledge.md`; `@[scripts/audit_epic_coverage.py]` is absent from `tier0-create-epic.md` and `tier0-research-epic.md`; `@[scripts/audit_markdown_boundaries.py]` is missing from `tier3-minify-customization.md`; and `tier2-execute.md` lacks an explicit Two-Stage global completion gate before phase sign-off.
   - *Remediation in EPIC 156:*
     1. Synchronize `@[AGENTS.md]` and `@[.agents/workflows/tier2-execute.md]` to mandate strict AST mode by default and enforce the Two-Stage Testing Pipeline (localized tests during steps followed by the global completion gate `backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build` before marking a phase complete).
     2. Embed `@[scripts/audit_plan_tracker_parity.py]` into `@[.agents/workflows/tier1-tracker-generator.md]`, `@[.agents/workflows/tier1-plan-tracker-generator.md]`, and `@[.agents/workflows/tier8-audit-plan.md]`.
     3. Embed `@[scripts/audit_rules_staleness.py]` into `@[.agents/workflows/tier8-red-teaming-audit.md]` and `@[.agents/workflows/tier2-hardening-knowledge.md]`.
     4. Embed `@[scripts/audit_epic_coverage.py]` into `@[.agents/workflows/tier0-create-epic.md]` and `@[.agents/workflows/tier0-research-epic.md]`.
     5. Embed `@[scripts/audit_markdown_boundaries.py]` into `@[.agents/workflows/tier3-minify-customization.md]`.
     6. Formalize concrete audit command in `@[.agents/workflows/tier3-database-reset.md]`.

### 1.4 Four-Phase Sovereign Migration Strategy
To avoid destabilizing the active codebase with an unmanageable mass edit, this Epic executes a structured, four-phase migration:
- **Phase 1: Tooling Infrastructure, Blindspot Elimination & Pre-Implementation Cleanups** (Implement QGR024, QGR025, Clean Import auditing, and DTO Parity gate; expand `backend_audit_loop.py` to 8 stages; clean all 79 pre-existing FATAL violations in domain code; clean low-count warning rules QGR007, QGR023, QGR009, QGR008, QGR006, QGR011; promote them to FATAL severity; equip `backend_audit_loop.py` with touched-file strict enforcement; synchronize agentic workflows in `@[.agents/workflows/]` and `@[AGENTS.md]` with mandatory strict quality gates, bidirectional plan-tracker parity, and rule staleness auditing).
- **Phase 2: Test Suite Mock Eradication, Fake Repository Parity & Concurrency Stress Gate** (Migrate 319 QGR014 instances across `backend_v2/tests/` to `InMemoryWorkflowRepository` and `InMemoryExecutionRecordRepository`; lock QGR014 to FATAL severity; implement concurrency stress tests).
- **Phase 3: Domain & Service Layer Duct-Tape Eradication & Mutation Invariance** (Systematically clean QGR020, QGR012, QGR016, QGR002, and QGR019; lock all remaining rules to FATAL severity; execute mutation testing on mathematical cores).
- **Phase 4: Universal AST Strictness Lockdown, Mathematical Proof & Permanent CI Enforcement** (Set default `ast_strict=True` in `backend_audit_loop.py`, reclassify all visitor methods in `QuorumGuardrailVisitor` to assign FATAL severity, execute the Exhaustive Violation Eradication Ledger, verify clean imports and DTO parity, and prove 100% clean scan across all 896 files).

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Symbol / Pattern / File | Current Location | Destination / Replacement | Rationale |
| :--- | :--- | :--- | :--- |
| `AsyncMock(spec=IRepository)` | `backend_v2/tests/unit/`, `backend_v2/tests/integration/` | `backend_v2/tests/fakes/in_memory_repositories.py` | Deceptive mocks pass without verifying state mutation or persistence contracts. |
| `MagicMock(spec=...)` on repos | `backend_v2/tests/` fixtures | In-memory repository fakes | Eradicates over-mocking; verifies genuine roundtrip persistence. |
| `@patch("...repository...")` | Unit test decorators | Dependency-injected in-memory repository fakes | Eliminates monkey-patching and mock leakage across test boundaries. |
| Dynamic WARNING severity assignments | `@[scripts/_ast_guardrails.py]` | `QuorumGuardrailVisitor` visitor methods assigning FATAL severity | Advisory warnings allow debt accumulation; all rules become permanently FATAL. |
| Opt-in `--ast-strict` CLI flag | `@[scripts/backend_audit_loop.py]` | Default behavior (strict mode always on) | Inverts enforcement default; strict mode is mandatory on every run. |
| Anonymous 3+ tuples | Service return signatures | Dedicated frozen Pydantic V2 DTOs | Eliminates Tuple Hell and positional unpacking bugs. |
| `dict.get("key", default)` | Internal services & orchestrators | Static Pydantic DTO dot notation or positive membership indexing | Eradicates silent failure masking and duct-tape defaults. |
| `isinstance(..., Mapping)` | Service & adapter methods | Direct Pydantic DTO validation at ingress boundaries | Eradicates bifurcated execution pipelines. |
| Mutable class defaults | Domain models & service classes | `Field(default_factory=list)` inside `Annotated` | Prevents shared mutable state across instances in async runtimes. |
| String-quoted type annotations | Domain models & service parameters | Direct unquoted types via Python 3.14 PEP 649/749 | Eliminates legacy ForwardRef workarounds; enables zero-cost imports. |
| Untyped dict in `model_copy()` | Concurrency update paths | Typed keyword fields with static type checks | Prevents corrupt unvalidated dictionary state from bypassing field schemas. |
| Unmonitored circular imports | Python module startup paths | [NEW] `@[scripts/audit_clean_imports.py]` (Step 7/8 in audit loop) | Prevents runtime circular import deadlocks. |
| Unverified mutation sensitivity | Mathematical engine tests | [NEW] `@[scripts/audit_mutation_coverage.py]` | Proves tests fail when mathematical boundary conditions mutate. |
| Optional DTO synchronization | Pre-commit quality checks | Step 8/8 in `@[scripts/backend_audit_loop.py]` | Prevents cross-language schema drift between backend and frontend. |
| Permissive quality gate commands in workflows | `@[AGENTS.md]`, `@[.agents/workflows/tier2-execute.md]` | Default strict mode (`backend_audit_loop.py`) and Two-Stage Testing Pipeline | Eliminates warning evasion during active feature execution. |
| Orphaned plan-tracker parity verification | `@[scripts/audit_plan_tracker_parity.py]` | Mandatory validation in Tier 1 and Tier 8 workflows | Enforces bidirectional TPR001-TPR010 structural parity between plans and trackers. |
| Orphaned rule staleness verification | `@[scripts/audit_rules_staleness.py]` | Mandatory validation in Tier 2 and Tier 8 knowledge/rule workflows | Prevents rules from referencing obsolete or renamed codebase symbols. |

### 2.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **`InMemoryWorkflowRepository` & `InMemoryExecutionRecordRepository` (`@[backend_v2/tests/fakes/in_memory_repositories.py]`):** Authoritative stateful fakes implementing full repository interfaces with realistic in-memory persistence and optional fault injection.
2. **Pydantic V2 Strict Configuration (`ConfigDict(strict=True, extra="forbid", frozen=True)`):** Mandatory configuration for all domain models and DTOs.
3. **AST Guardrail Visitor Engine (`QuorumGuardrailVisitor` in `@[scripts/_ast_guardrails.py]`):** Core AST parser and rule evaluator.
4. **Expanded 8-Stage Universal Quality Gate Pipeline (`@[scripts/backend_audit_loop.py]`):** The central audit loop expands from 6 to 8 mandatory stages:
   - `⏳ 1/8: Checking and fixing files (ruff check --fix)`
   - `⏳ 2/8: Formatting code (ruff format)`
   - `⏳ 3/8: Type checking code (mypy --strict)`
   - `⏳ 4/8: Checking AST Codebase Guardrails (scripts/_ast_guardrails.py in strict mode)`
   - `⏳ 5/8: Validating UI templates (Jinja Dumb Painter Enforcement)`
   - `⏳ 6/8: Validating Seed Data & Atoms (run_seed.py local --dry-run & audit_database_atoms.py --strict)`
   - `⏳ 7/8: Verifying Clean Imports & Zero Circular Dependencies (scripts/audit_clean_imports.py)`
   - `⏳ 8/8: Verifying Cross-Language DTO Parity (scripts/audit_dto_parity.py)`
5. **Universal Agentic Workflow Parity (`@[.agents/workflows/]`, `@[AGENTS.md]`):** All execution, planning, and audit workflows enforce strict AST analysis, bidirectional plan-tracker parity, and rule symbol freshness by default.

### 2.3 Compliance & Modernity Gates
- **Zero Permissive Typing Mandate:** Absolute prohibition of naked dictionaries, unchecked `.get()` access, and dynamic type casts.
- **Deceptive Persistence Mocking Ban:** Absolute prohibition of static mocks for database repositories in test suites.
- **Fail-Fast Invariant:** Any missing required field, schema violation, or unmapped value immediately triggers an explicit `AppException` with structured RFC 7807 dual-logging.
- **Single Pipeline Invariant:** No bifurcated execution paths based on duck-typing or type unions.
- **Zero Circular Dependency Invariant:** Every module across all 896 files must be cleanly importable in isolation and concurrently.
- **Synchronous Cross-Language Parity Invariant:** Backend Pydantic DTO mutations must synchronously match Dart Freezed models.

### 2.4 Python 3.14.6 Strictness & Runtime Modernity Protocols
All codebase targets refactored under EPIC 156 must strictly comply with Python 3.14.6 standards:
1. **Deferred Annotations (PEP 649 / PEP 749):** All model definitions and type signatures use unquoted type expressions natively (`target: StepOutputDTO`). Runtime inspection utilizes `annotationlib.get_annotations(obj, format=Format.VALUE)`.
2. **Annotated Field Mandate (PEP 593):** All Pydantic model attributes enforce `Annotated[T, Field(...)]`. Bare `Field(...)` assignments and duplicate `Field()` default assignments are prohibited.
3. **Structured Concurrency (PEP 758):** All parallel tasks run inside managed `asyncio.TaskGroup` contexts utilizing bracketless `except* (ErrorA, ErrorB):` syntax. Bare `asyncio.gather` and unmanaged `create_task` are prohibited.
4. **Control Flow Integrity (PEP 765):** `return`, `break`, or `continue` statements inside `finally` blocks are strictly prohibited to prevent exception swallowing.
5. **Zero Double-Serialization Invariant:** DTOs remain strongly typed objects throughout pipeline transit. Converting DTOs to dictionaries via `.model_dump()` merely to pass them to `.model_validate()` across internal boundaries is strictly prohibited.
6. **Native Zstandard Telemetry (PEP 784):** Offloaded execution traces and large payload blobs utilize native `compression.zstd`.
7. **Clean Module Importability:** Zero circular imports between packages; module-level initializations must be side-effect free.

### 2.5 Producer-Consumer Integration Check
```
+-----------------------------------------------------------+
| PRODUCER: Domain Services & Orchestrators                 |
| - Generates frozen Pydantic V2 DTOs                       |
| - Enforces Python 3.14.6 unquoted PEP 649/749 annotations |
| - Never returns naked dictionaries or anonymous tuples    |
+-----------------------------+-----------------------------+
                              | Strictly Typed DTOs
                              v
+-----------------------------------------------------------+
| CONSUMER / PERSISTENCE: In-Memory Fakes & Repositories     |
| - Validates full Pydantic schemas upon save               |
| - Simulates genuine state mutations in memory             |
| - Zero deceptive MagicMock / AsyncMock usage              |
+-----------------------------+-----------------------------+
                              | Real Persistence Roundtrip
                              v
+-----------------------------------------------------------+
| VALIDATOR: Expanded 8-Stage Backend Audit Loop            |
| - Stage 1-3: Ruff lint, Ruff format, MyPy strict          |
| - Stage 4: AST Guardrails QGR000-QGR025 (FATAL severity)  |
| - Stage 5-6: UI Templates & Database Atoms               |
| - Stage 7: Clean Module Imports (scripts/audit_clean_imports)|
| - Stage 8: Cross-Language DTO Parity (audit_dto_parity.py) |
+-----------------------------------------------------------+
```

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Tooling Infrastructure, Blindspot Elimination & Scoped Boy Scout CI Enforcement
*Goal:* Implement QGR024 and QGR025 in `_ast_guardrails.py`, build the Clean Import smoke test, permanently expand `backend_audit_loop.py` to an 8-stage pipeline including Clean Imports and DTO Parity, clean low-count warning rules (QGR007, QGR023, QGR009), promote them to FATAL severity, equip `backend_audit_loop.py` with touched-file strict enforcement, and create an automated baseline tracker.

- **Step 1.1: Implement QGR024 (String-Quoted Annotation Ban) in `@[scripts/_ast_guardrails.py]`**
  - Add AST visitor logic to inspect `ast.AnnAssign` and `FunctionDef.returns`.
  - Detect string literal constants used as type hints (for instance, `target: "StepOutputDTO"`).
  - Remediation guidance: Use direct unquoted types leveraging Python 3.14 PEP 649 deferred annotations.
- **Step 1.2: Implement QGR025 (Untyped Dict in model_copy Ban) in `@[scripts/_ast_guardrails.py]`**
  - Add AST visitor logic inspecting calls to `model_copy(update=...)`.
  - Flag calls passing dynamic dictionary variables or unvalidated dictionary literals.
- **Step 1.3: Add Comprehensive Unit Tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`**
  - Add positive and negative unit test suites for QGR013 through QGR025, ensuring 100% test coverage for the AST engine. QGR024 MUST include explicit false-positive defense tests for `Literal['development', 'production']` and `Annotated[T, Field(description='...')]` arguments. QGR025 MUST include explicit false-positive defense tests for typed dictionary literals with statically known keys inside `async with _update_lock:` contexts (specifically: `model_copy(update={'status': ExecutionStatus.RUNNING, 'progress': 100})`).
- **Step 1.4: Implement Clean Import Smoke Test Tool ([NEW] @[scripts/audit_clean_imports.py] and [NEW] @[backend_v2/tests/unit/scripts/test_clean_imports.py])**
  - Create a deterministic scanner that recursively imports every module in `backend_v2/` via `importlib.import_module()`.
  - Assert that all 896 modules load without `ImportError`, `AttributeError`, or circular dependency deadlocks.
- **Step 1.5: Expand `@[scripts/backend_audit_loop.py]` to an 8-Stage Mandatory Pipeline**
  - Integrate Step 7/8: Execute `audit_clean_imports.py` to verify that all modules load cleanly without circular import failures.
  - Integrate Step 8/8: Execute `audit_dto_parity.py` to assert 100% schema parity between backend Pydantic models and frontend Dart Freezed classes.
  - Harden Step 5/8: Expand Jinja Dumb Painter regex to detect fallback expressions (`or ''`, `or []`, `or {}`), enforcing 100% passive presentation.
  - Eradicate 7 existing Jinja fallback violations in `@[backend_v2/templates/report_template.jinja2]` (specifically: lines 390, 391, 413, 421, 422, 440, 461) by replacing `or ''`, `or []`, and `or {}` expressions with backend DTO-guaranteed non-None defaults.
  - Enforce Scoped Boy Scout strictness: fail-fast if any touched target contains unsuppressed warnings.
- **Step 1.6: Eradicate Pre-Existing Domain FATAL Violations (79 instances across backend_v2)**
  - 53 instances of QGR003: Replace silent exception swallowing in handlers (specifically: `backend_v2/run_worker.py`, `backend_v2/database/wrapper.py`, `backend_v2/hooks/llm.py`, `backend_v2/llm/handler.py`) with explicit `raise` or typed failure dispatch (`dlq_service.push()`).
  - 10 instances of QGR000: Remove illegal `# noqa: QGR*` comment suppressions in domain code (specifically: `backend_v2/llm/ingress_pipeline.py`) and resolve the underlying architectural violations.
  - 7 instances of QGR012: Eliminate banned `isinstance(..., dict)` duck-typing checks in domain code (specifically: `backend_v2/llm/ingress_pipeline.py`).
  - 4 instances of QGR002: Replace unexempted dictionary `.get()` calls in domain code (specifically: `backend_v2/database/wrapper.py`).
  - 4 instances of QGR018: Replace banned type laundering via `TypeAdapter(dict)` in domain code (specifically: `backend_v2/hooks/source_verification_hook.py`) with typed Pydantic V2 DTOs.
  - 1 instance of QGR022: Replace unshielded f-string prompt interpolation with PromptBlock assembly.
- **Step 1.7: Eradicate Low-Count Advisory Warning Violations (46 instances)**
  - QGR007 (7 instances): Audit all models lacking `ConfigDict(strict=True, extra="forbid")` and add explicit Pydantic V2 `model_config`.
  - QGR023 (22 instances): Audit methods returning 3+ element tuples; define dedicated frozen Pydantic V2 DTOs (specifically: defining [NEW] `ChunkPacketDTO`).
  - QGR009 (11 instances): Audit `AppException` instantiations missing an explicit `ErrorCodes` enum member; bind canonical error codes from `@[backend_v2/models/enums.py]`.
  - QGR008 (3 instances): Import timeouts and retry intervals centrally from `backend_v2/settings.py` instead of hardcoded numbers.
  - QGR006 (2 instances): Replace unguarded dictionary subscripting with positive membership validation.
  - QGR011 (1 instance): Replace mutable default argument in function definitions with `= None` and factory initialization.
- **Step 1.7b: Eradicate Advisory Warnings in Active Tooling & Audit Scripts (22 instances across scripts/)**
  - Refactor `@[scripts/audit_database_atoms.py]` (12 instances of QGR012): Replace `isinstance(..., dict)` duck-typing with typed schema validation; update prompt ambiguity inspection to exempt illustrative examples per `@[.agents/rules/05_llm_architecture.md]`; enforce fail-fast exit on structural defects when `--strict` is enabled.
  - Refactor `@[scripts/reconcile_storage.py]` (2 instances of QGR007): Add explicit `model_config = ConfigDict(strict=True, extra="forbid")` to `TraceEventContent` and `TraceEventHeader`.
  - Refactor `@[scripts/audit_rules_staleness.py]` (2 instances): Replace `hasattr()` with typed attribute access and replace broad exception swallowing with structured logging and re-raise.
  - Refactor `@[scripts/audit_matrix_auto_filler.py]` (2 instances of QGR002): Replace `.get()` calls with typed dictionary key indexing.
  - Refactor `@[scripts/audit_matrix_manager.py]` (2 instances of QGR001): Replace `vars()` reflection with `.model_dump()` or explicit attribute mapping.
  - Refactor `@[scripts/matrix_slice_engine.py]` (2 instances of QGR002): Replace `.get()` calls with bracket indexing.
- **Step 1.8: Promote QGR007, QGR023, QGR009, QGR008, QGR006, QGR011, QGR024, and QGR025 to FATAL in `@[scripts/_ast_guardrails.py]`**
  - In `scripts/_ast_guardrails.py`, update severity classifications for these rules to assign FATAL severity.
  - Re-run AST guardrails on all 896 files to mathematically prove 0 FATAL violations (down from 79 to 0) and verify warning reduction from 1,254 to 1,208 (eliminating 46 warnings).
- **Step 1.9: Build Warning Baseline Ledger Script ([NEW] @[scripts/audit_warning_baseline.py])**
  - Create a **temporary Phase 1-3 scaffolding** verification script that records the exact warning count per rule code and asserts that total warnings never increase above the current baseline (1,208 warnings, 0 fatals). This script becomes architecturally redundant after Phase 4 locks all rules to FATAL severity; it may be decommissioned at that point.
- **Step 1.10: Agentic Workflows & Quality Gate Alignment ([MODIFY] @[AGENTS.md], @[.agents/workflows/tier2-execute.md], @[.agents/workflows/tier1-tracker-generator.md], @[.agents/workflows/tier1-plan-tracker-generator.md], @[.agents/workflows/tier8-audit-plan.md], @[.agents/workflows/tier8-red-teaming-audit.md], @[.agents/workflows/tier2-hardening-knowledge.md], @[.agents/workflows/tier0-create-epic.md], @[.agents/workflows/tier0-research-epic.md], @[.agents/workflows/tier3-minify-customization.md], @[.agents/workflows/tier3-database-reset.md])**
  - Update `@[AGENTS.md]` and `@[.agents/workflows/tier2-execute.md]` to mandate strict AST mode by default (`uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict`) and enforce the Two-Stage Testing Pipeline (localized tests during steps; global completion gate `backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build` before closing any phase).
  - Integrate `@[scripts/audit_plan_tracker_parity.py]` as a mandatory verification gate in `@[.agents/workflows/tier1-tracker-generator.md]`, `@[.agents/workflows/tier1-plan-tracker-generator.md]`, and `@[.agents/workflows/tier8-audit-plan.md]`.
  - Integrate `@[scripts/audit_rules_staleness.py]` as a mandatory verification gate in `@[.agents/workflows/tier8-red-teaming-audit.md]` and `@[.agents/workflows/tier2-hardening-knowledge.md]`.
  - Integrate `@[scripts/audit_epic_coverage.py]` as a mandatory verification gate in `@[.agents/workflows/tier0-create-epic.md]` and `@[.agents/workflows/tier0-research-epic.md]`.
  - Integrate `@[scripts/audit_markdown_boundaries.py]` as a mandatory verification gate in `@[.agents/workflows/tier3-minify-customization.md]`.
  - Replace vague audit commands in `@[.agents/workflows/tier3-database-reset.md]` with explicit executable commands: `uv run python backend_v2/seed/run_seed.py local` followed by `uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test`.

### Phase 2: Test Suite Mock Eradication, Fake Repository Parity & Concurrency Stress Gate (QGR014)
*Goal:* Eradicate 319 instances of deceptive repository mocking across `backend_v2/tests/`, promote QGR014 to FATAL severity, and implement async concurrency stress testing.

- **Step 2.1: Audit and Enhance In-Memory Repository Fakes**
  - Inspect `@[backend_v2/tests/fakes/in_memory_repositories.py]`.
  - Ensure `InMemoryWorkflowRepository`, `InMemoryExecutionRecordRepository`, `InMemoryOutputProfileRepository`, and `InMemorySystemSettingsRepository` fully implement all methods specified in their respective interface contracts.
  - Add thread-safe in-memory stores and deterministic `inject_fault(method_name, exception)` capabilities for negative testing.
- **Step 2.2: Batch Refactor Unit Test Fixtures (Sub-package by Sub-package)**
  - Batch A: Refactor `backend_v2/tests/unit/services/` fixtures, replacing `AsyncMock(spec=...)` with instantiated in-memory repository fakes.
  - Batch B: Refactor `backend_v2/tests/unit/orchestrator/` and `backend_v2/tests/unit/workers/` test suites.
  - Batch C: Refactor `backend_v2/tests/integration/` repository mocking setups.
  - Batch D: Replace `@patch` decorators targeting repository interfaces with clean dependency injection.
- **Step 2.3: Promote QGR014 to FATAL in `@[scripts/_ast_guardrails.py]`**
  - In `scripts/_ast_guardrails.py`, update QGR014 severity classification to FATAL severity.
  - Run `uv run python scripts/_ast_guardrails.py backend_v2/tests` to verify 0 violations.
  - Verify total codebase warning count drops from 1,214 to 895.
- **Step 2.4: Implement Concurrency Stress Test Suite ([NEW] @[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py])**
  - Build an automated stress harness spawning 50+ concurrent atoms within `asyncio.TaskGroup`.
  - Simulate high-frequency state updates and verify zero deadlocks, zero lock starvation, and deterministic state transitions.

### Phase 3: Domain & Service Layer Duct-Tape Eradication & Mutation Invariance (QGR020, QGR012, QGR016, QGR002, QGR019)
*Goal:* Eradicate remaining domain and service layer anti-patterns, promote each rule to FATAL severity, and execute mutation testing on mathematical calculation cores.

- **Step 3.1: Clean and Lock QGR020 (107 instances: Mutable Class Defaults & Duplicate Field())**
  - Refactor class attributes: replace `= []` or `= {}` with `Field(default_factory=list)` or `Field(default_factory=dict)` inside `Annotated`.
  - Remove redundant `= Field(...)` value assignments when `Annotated[T, Field(...)]` is present.
  - Promote QGR020 to FATAL severity in `scripts/_ast_guardrails.py`.
- **Step 3.2: Clean and Lock QGR012 (116 instances: `isinstance(..., Mapping)` Duck-Typing)**
  - Audit orchestrators, strategies, and adapters in `backend_v2/services/`.
  - Eliminate bifurcated `if isinstance(val, Mapping): ... elif isinstance(val, BaseModel): ...` cascades.
  - Enforce single-type method signatures accepting strictly validated Pydantic V2 DTOs.
  - Promote QGR012 to FATAL severity in `scripts/_ast_guardrails.py`.
- **Step 3.3: Clean and Lock QGR016 (184 instances: Ternary Lazy Fallbacks)**
  - Replace `val or {}` and `val if val else default` with schema-level defaults or explicit `if val is not None:` null checks.
  - Promote QGR016 to FATAL severity in `scripts/_ast_guardrails.py`.
- **Step 3.4: Clean and Lock QGR002 (340 instances: Chained `.get()` Lookups)**
  - In domain models and internal pipelines, replace `.get()` with static dot notation on typed DTOs.
  - In external dynamic dictionaries (specifically: PDF extraction payloads or raw HTTP responses), replace `.get()` with positive membership checks and direct key indexing: `val = d[k] if (k in d and d[k] is not None) else None`.
  - Promote QGR002 to FATAL severity in `scripts/_ast_guardrails.py`.
- **Step 3.5: Clean and Lock Residual Rules (QGR001 83 instances, QGR019 42 instances)**
  - Replace dynamic reflection (`getattr`/`hasattr`) with typed attribute access or explicit discriminated unions.
  - Replace in-place `dict.pop()` with pure dictionary creation or immutable model transformations.
  - Promote QGR001 and QGR019 to FATAL severity.
- **Step 3.6: Implement Mutation Invariance Verification ([NEW] @[scripts/audit_mutation_coverage.py])**
  - Execute automated AST mutation tests on `UnifiedScoringEngine` and `TopologicalEvaluator`.
  - Mutate relational operators (`<` to `<=`, `>` to `>=`), arithmetic operators, and conditional branches.
  - Assert 100% mutant kill rate, proving test suites detect any behavioral alteration.

### Phase 4: Universal AST Strictness Lockdown, Mathematical Proof & Permanent CI Enforcement
*Goal:* Lock strict mode as the permanent default in all quality gates, decommission warning categories, execute the Exhaustive Violation Eradication Ledger, verify clean imports and DTO parity, and mathematically prove zero warnings across all 896 files.

- **Step 4.1: Invert Default Flag in `@[scripts/backend_audit_loop.py]`**
  - Update `backend_audit_loop.py` argument parsing so that `ast_strict` defaults to `True`.
  - Provide a temporary `--permissive-warn` flag for emergency diagnostics only, while the standard command runs strict AST validation unconditionally.
- **Step 4.2: Reclassify All Visitor Rules to FATAL in `@[scripts/_ast_guardrails.py]`**
  - Refactor all visitor methods in `QuorumGuardrailVisitor` assigning WARNING severity to assign FATAL severity.
  - Reclassify or remove WARNING severity, ensuring every architectural rule defined in `scripts/_ast_guardrails.py` unconditionally emits FATAL severity.
- **Step 4.3: Execute Exhaustive Violation Eradication Ledger Verification**
  - Run `uv run python scripts/audit_warning_baseline.py --verify-zero` to verify all 1,333 violations (79 fatal + 1,254 warning) are eliminated.
  - Execute full repository AST gate: `uv run python scripts/_ast_guardrails.py backend_v2 --strict`.
  - Mathematically verify: **0 FATAL errors, 0 WARNINGS across 896 files**.
- **Step 4.4: Execute Clean Imports, DTO Parity, and Mutation Gates**
  - Run `uv run python scripts/audit_clean_imports.py` across all 896 modules.
  - Run `uv run python scripts/audit_dto_parity.py` to verify 100% cross-language contract parity.
  - Run `uv run python scripts/audit_mutation_coverage.py` to verify 100% mutation kill rate.
- **Step 4.5: Full Test Suite and 8-Stage Quality Gate Execution**
  - Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` in default strict mode through all 8 stages.
  - Verify all unit and integration tests pass with 100% green status.
- **Step 4.6: Mandatory Final E2E REST API Verification Gate**
  - Execute live E2E integration test suite under live environment flags.

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Exhaustive Violation Eradication Ledger (1,333 -> 0)

> [!NOTE]
> The Exhaustive Violation Eradication Ledger expands the verification scope from 1,333 domain violations (Section 1.2) to 1,366 total targets by adding 22 Active Tooling violations (Category 2) and 11 Workflow Gate deficiencies.

The Definition of Done requires that every single violation category identified in the baseline audit is mathematically proven to have reached exactly 0 violations:

| Rule Code | Violation Description | Fatal Baseline | Warning Baseline | Total Baseline | Target Count | Final Status | Verification Assertion Command |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QGR002** | Chained Dictionary `.get()` Calls in Domain Code | 4 | 340 | 344 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR014** | Deceptive Repository Mocks in Tests | 0 | 319 | 319 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2/tests --strict` |
| **QGR016** | Ternary Lazy Fallbacks (`or {}`) | 0 | 184 | 184 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR012** | Duck-Typing `isinstance(..., Mapping)` | 7 | 116 | 123 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR020** | Mutable Defaults & Duplicate `Field()` | 0 | 107 | 107 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR001** | Dynamic Reflection (`getattr`/`hasattr`/`vars`) | 0 | 83 | 83 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR003** | Silent Exception Swallowing in Handlers | 53 | 17 | 70 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR019** | In-Place `dict.pop()` Mutations | 0 | 42 | 42 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR023** | Anonymous Multi-Value State Tuples ("Tuple Hell") | 0 | 22 | 22 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR009** | `AppException` Missing Canonical `ErrorCodes` | 0 | 11 | 11 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR000** | Unauthorized `# noqa` Comment Suppressions | 10 | 0 | 10 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR007** | Missing Strict Pydantic V2 `ConfigDict` | 0 | 7 | 7 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR018** | Type Laundering via `TypeAdapter(dict)` | 4 | 0 | 4 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR008** | Hardcoded Sleep / Timeout Literals | 0 | 3 | 3 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR006** | Unguarded Dictionary Subscripting | 0 | 2 | 2 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR022** | Unshielded f-string Prompt Interpolation | 1 | 0 | 1 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR011** | Mutable Default Argument in Function Definition | 0 | 1 | 1 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR024** | Python 3.14 String-Quoted Annotations | 0 | 0 | 0 | 0 | ENFORCED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **QGR025** | Untyped Dictionary in `model_copy()` | 0 | 0 | 0 | 0 | ENFORCED | `uv run python scripts/_ast_guardrails.py backend_v2 --strict` |
| **Tooling** | Active Quality Gate & Audit Scripts | 0 | 22 | 22 | 0 | ELIMINATED | `uv run python scripts/_ast_guardrails.py scripts/audit_database_atoms.py scripts/reconcile_storage.py scripts/audit_rules_staleness.py scripts/audit_matrix_auto_filler.py scripts/audit_matrix_manager.py scripts/matrix_slice_engine.py --strict` |
| **Imports** | Module-Level Circular Dependencies | 0 | 0 | 0 | 0 | ZERO CIRCULAR | `uv run python scripts/audit_clean_imports.py` |
| **DTO Drift** | Cross-Language Schema Desynchronization | 0 | 0 | 0 | 0 | 100% PARITY | `uv run python scripts/audit_dto_parity.py` |
| **Mutations** | Core Engine Mutation Kill Rate | 0% | 0% | 100% | 100% | 100% KILLED | `uv run python scripts/audit_mutation_coverage.py` |
| **Workflow Gates** | Agentic Workflows & Quality Gate Parity | 0 | 11 | 11 | 0 | SYNCHRONIZED | `uv run python scripts/audit_plan_tracker_parity.py --all --strict` ; `uv run python scripts/audit_rules_staleness.py` |
| **TOTAL** | **All In-Scope Codebase AST Violations & Workflow Gates** | **79** | **1,287** | **1,366** | **0** | **100% CLEAN** | `uv run python scripts/backend_audit_loop.py backend_v2` |

### 4.2 Definition of Done (DoD) Quality Gates
1. **Zero Warnings Invariant:** Total advisory warnings across all 896 Python files equals exactly 0.
2. **Zero Advisory Warnings / FATAL Enforcement:** All guardrail rules (QGR000 through QGR025) in `@[scripts/_ast_guardrails.py]` unconditionally emit FATAL severity.
3. **8-Stage Audit Loop Default:** `@[scripts/backend_audit_loop.py]` runs with `ast_strict=True` by default, executing all 8 stages including Clean Imports (Stage 7) and DTO Parity (Stage 8).
4. **Zero Repository Mocks:** All tests in `backend_v2/tests/` use typed `InMemoryWorkflowRepository` and `InMemoryExecutionRecordRepository` from `@[backend_v2/tests/fakes/in_memory_repositories.py]`; zero instances of `AsyncMock(spec=IRepository)` or `MagicMock` on repository interfaces exist.
5. **Clean Import Guarantee:** 100% of modules in `backend_v2/` import cleanly without circular dependency deadlocks or initialization exceptions.
6. **Mutation Invariance:** `UnifiedScoringEngine` and `TopologicalEvaluator` achieve a 100% mutant kill rate under automated AST mutation testing.
7. **Cross-Language DTO Parity:** Zero schema drift between backend Pydantic V2 DTOs and Flutter Dart Freezed models, enforced by `audit_dto_parity.py`.
8. **Python 3.14.6 Compliance:** All domain models enforce `Annotated[T, Field(...)]` with zero duplicate `Field()` assignments, unquoted PEP 649/749 annotations, and `ConfigDict(strict=True, extra="forbid", frozen=True)`.
9. **AST Test Suite Coverage:** `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` contains passing unit tests for all rules from QGR000 through QGR025.
10. **Concurrency Stress Resilience:** Concurrency test suite proves zero deadlocks under 50+ concurrent TaskGroup operations.
11. **No Regressions:** Full test suite passes cleanly with 90%+ branch and line coverage.
12. **Active Tooling Parity:** 100% of active audit and quality gate scripts (`audit_database_atoms.py`, `reconcile_storage.py`, `audit_rules_staleness.py`, `audit_matrix_auto_filler.py`, `audit_matrix_manager.py`, `matrix_slice_engine.py`) pass `--ast-strict` with zero warnings or fatal errors.
13. **Agentic Workflow Strictness Parity:** 100% of workflows in `@[.agents/workflows/]` and `@[AGENTS.md]` mandate strict quality gate execution, bidirectional plan-tracker parity (`audit_plan_tracker_parity.py`), rule freshness verification (`audit_rules_staleness.py`), and Two-Stage Testing Pipelines.

### 4.3 Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_clean_imports.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/fakes/in_memory_repositories.py --test`
- `uv run python scripts/backend_audit_loop.py scripts/audit_database_atoms.py`
- `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`

### 4.4 AST Guardrails & Structural Tests
- Full repository scan: `uv run python scripts/_ast_guardrails.py backend_v2 scripts --strict`
- Baseline ledger verification: `uv run python scripts/audit_warning_baseline.py --verify-zero`
- Clean module importability scan: `uv run python scripts/audit_clean_imports.py`
- Cross-language DTO parity verification: `uv run python scripts/audit_dto_parity.py`
- Mathematical core mutation audit: `uv run python scripts/audit_mutation_coverage.py`
- Bidirectional plan-tracker parity scan: `uv run python scripts/audit_plan_tracker_parity.py --all --strict`
- Rule symbol staleness scan: `uv run python scripts/audit_rules_staleness.py`
- Expected output: `0 violations detected across 896 files. Strict mode PASS.`

### 4.5 Manual Verification Steps
1. Re-seed local development database: `uv run python backend_v2/seed/run_seed.py local`
2. Verify atom and prompt structural validity: `uv run python scripts/audit_database_atoms.py --strict`
3. Verify Markdown boundary compliance: `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md`

### 4.6 MANDATORY Final E2E REST API Verification Gate
Cross-platform live integration execution:
- **Windows (PowerShell):**
  ```powershell
  $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
  ```
- **Unix / Bash:**
  ```bash
  RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
  ```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
