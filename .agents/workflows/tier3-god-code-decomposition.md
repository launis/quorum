---
description: System 2 Decomposition Planner for Legacy Refactoring (Two-Epoch Strangler Fig Protocol)
---

# Tier 3 Workflow: God Code Decomposition Planner

This workflow governs the systematic planning and decomposition of heavy "God Code" files (>500 lines) according to Domain-Driven Design (DDD) and Single Responsibility Principles (SRP). It enforces a strict **Two-Epoch Strangler Fig Protocol** that cleanly separates **Epoch 1 (Pure Structural Lift-and-Shift & Proxy Cutover)** from **Epoch 2 (Post-Cutover Tier 2 Hardening)**. **This is a pure planning tier; it does NOT write domain code. It generates implementation plans and a tracker, delegating execution to Tier 2.**

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Specifically: "Decompose God file @[backend_v2/services/orchestrator/dag_executor.py]"]</objective>
  <role>Senior Staff Engineer &amp; Principal Systems Architect</role>

  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool calls in a new task MUST be `view_file` to physically load `AGENTS.md` (for Universal Quality Gates), `@[.agents/rules/00-antigravity-core.md]`, and `@[.agents/workflows/tier0-create-plan.md]`. First review the context-injected Knowledge Item (KI) summaries, and load `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`, and `@[ki_zero_permissive_typing.md]` via `view_file`. Dynamically load domain rules based on target scope:
        - IF decomposing Python backend: read `@[.agents/rules/01-python-backend.md]`
        - IF decomposing Flutter frontend: read `@[.agents/rules/02_flutter_desktop.md]`
        - IF touching Database/Seed Data: read `@[.agents/rules/03_seed_vault.md]`
        - IF touching file structures/routing: read `@[.agents/rules/04_directory_reference.md]`
        - IF touching LLM/Prompts: read `@[.agents/rules/05_llm_architecture.md]`
      </mandatory_pattern>
      <catastrophic_reason>Refactoring massive files without loading core architectural invariants causes hallucinated module boundaries and broken system integration.</catastrophic_reason>
    </rule_block>

    <rule_block id="orchestrator_god_object_fragility">
      <mandatory_pattern>If the target file resides ANYWHERE within `backend_v2/services/orchestrator/` (specifically including: `atomizer.py`, `dag_executor.py`, `topological_evaluator.py`, `matrix_reducer.py`, `causal_cohesion_evaluator.py`), the planner MUST STOP immediately at Step 1 and explicitly request "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" before generating any decomposition plans. Any code blocks or methods marked with ARCHITECTURE LOCK comments inside the target file MUST be relocated verbatim (100% untouched AST body and preserving the ARCHITECTURE LOCK comment header) into their target domain sub-module during Epoch 1, without altering their internal logic.</mandatory_pattern>
      <catastrophic_reason>Modifying the core DAG Orchestrator engine without explicit clearance and blast-radius evaluation causes cascading execution failures across all workflows.</catastrophic_reason>
    </rule_block>

    <rule_block id="two_epoch_separation_mandate">
      <banned_pattern>Mixing structural extraction (moving classes/functions across files) with behavioral hardening (removing `.get()` fallbacks, tightening Pydantic schemas, or fixing 12-item tech debt) inside the same phase while the legacy proxy file is still active.</banned_pattern>
      <mandatory_pattern>Every decomposition tracker MUST be strictly partitioned into two sequential, non-overlapping epochs:
      1. **EPOCH 1 — PURE STRUCTURAL LIFT-AND-SHIFT &amp; ATOMIC CUTOVER (Zero Behavioral Change)**:
         - Extract leaf types/helpers and domain sub-modules with **100% identical runtime behavior**, types, and method signatures.
         - MONOLITHIC METHOD CLOSURE UNNESTING: If a single AST `FunctionDef` or `AsyncFunctionDef` node exceeds 350 lines and contains nested `def` / `async def` closures mutating `nonlocal` state or sharing local `asyncio.Lock` primitives, Epoch 1 is explicitly permitted to encapsulate the method's local mutable state and concurrency locks into a private `@dataclass` execution state container scoped strictly to the local method invocation stack frame, and hoist the nested closures into private helper methods or dedicated sub-module functions accepting that state container (ensuring no sub-module exceeds the 500-line gate). The outer method's public signature, parameter types, return type, and observable runtime behavior MUST remain 100% identical during Epoch 1, with all plan references pointing to complete AST node bounds or `[NEW]` target files to satisfy MBD004.
         - Existing unit tests MUST run 100% green against the temporary proxy (`X.py`) throughout extraction.
         - Perform Mechanical 1-Hop Consumer Import Rewiring using `symbol_migration_map.md`, split the monolithic test file into modular test files, execute the Atomic Package Cutover (`X.py` -> `X/__init__.py`), and physically delete the external proxy file.
      2. **EPOCH 2 — POST-CUTOVER TIER 2 HARDENING (Behavioral &amp; Type Lockdown)**:
         - ONLY AFTER Epoch 1 is 100% complete and the legacy proxy is deleted, schedule bounded Tier 2 Hardening tasks to resolve the discovered 12-Item Tech Debt Inventory (eradicating `.get()`, `getattr()`, loose dicts, and legacy test fixtures) on the newly isolated sub-modules.
         - CALLER CONTRACT SYNCHRONIZATION: Whenever a sub-module's public function signature, parameter type, or return schema is tightened during Epoch 2, all immediate 1-hop callers of that symbol MUST be updated and verified in the exact same atomic commit.</mandatory_pattern>
      <catastrophic_reason>Hardening extracted modules while legacy callers and monolithic tests still route through the proxy breaks behavioral parity mid-surgery, causing un-isolatable test failures that trap executing agents in rollback loops. Failing to synchronize callers when signatures change in Epoch 2 breaks downstream consumers.</catastrophic_reason>
    </rule_block>

    <rule_block id="strangler_fig_mandate">
      <mandatory_pattern>Plan the Epoch 1 decomposition incrementally using the Strangler Fig Pattern:
      1. **Import Proxy Pattern &amp; Explicit Re-Exports**: While extracting slices, retain re-exports or `@deprecated` proxy delegations in `X.py` so the codebase remains 100% compilable. Implicit re-exports (`from sub import Symbol`) are STRICTLY BANNED by `mypy --strict`. Always mandate `__all__ = ["Symbol", ...]` AND explicit redundant aliases (`from sub import Symbol as Symbol`).
      2. **Two-Phase Package Strangler Protocol (File-to-Package Transition)**: Python and MyPy forbid `X.py` and `X/__init__.py` from coexisting simultaneously (`Duplicate module named X`).
         - *Intermediate Extraction Phases*: Sub-directory `X/` MUST NOT contain `__init__.py` while `X.py` exists. Extracted sub-modules in `X/` are re-exported from `X.py`.
         - *Atomic Proxy Cutover Step*: Deleting `X.py` and creating `X/__init__.py` (with identical `__all__` facade exports) MUST occur in a single atomic step, immediately verified via `uv run mypy --strict`.
      3. **Domain Package Aggregator Facade vs. Banned Hollow Shell**:
         - *Banned Hollow Shell*: Any transitional proxy file living *outside* the package (`X.py`) MUST be deleted at the end of Epoch 1 and locked via AST Guardrail `QGR017`.
         - *Approved Package Facade*: The canonical package root `X/__init__.py` is the permanent, typed entrypoint for package `X/`, wiring sub-services via dependency injection with pure 1-line delegations.</mandatory_pattern>
      <catastrophic_reason>Coexisting `X.py` and `X/__init__.py` crashes MyPy with duplicate module collisions. Leaving external proxy files alive permanently preserves technical debt.</catastrophic_reason>
    </rule_block>

    <rule_block id="test_coverage_prerequisite">
      <mandatory_pattern>Before Epoch 1 extraction begins, the target God File MUST have at least 75% test coverage. If baseline coverage is below 75%, generate a mandatory blocker plan `phase0_coverage_bootstrap.md` defining black-box Characterization Tests (Golden Master tests) to lock current behavior to >=75% coverage before Phase 1A extraction starts.</mandatory_pattern>
      <catastrophic_reason>Decomposing an untested God File is blind surgery that silently destroys business logic.</catastrophic_reason>
    </rule_block>

    <rule_block id="topological_leaf_first_extraction_mandate">
      <mandatory_pattern>Construct an internal call-graph and type-graph DAG of the God File using `@[scripts/_ast_boundary_utils.py]`. Decompositions MUST follow **Bottom-Up Topological Leaf-First Order**:
      1. **Phase 1A (Leaf Pre-Extraction)**: Extract depth-0 leaf types, centralized Enums (converting any inline `Literal[...]` definitions into `backend_v2/models/enums.py`), shared constants, DTOs, and leaf helper functions first. Relocate any bottom-of-file Pydantic `model_rebuild()` calls deterministically.
      2. **Zero God File Imports**: Extracted sub-modules MUST NEVER import from the parent God File.
      3. **Circular Domain Decoupling**: If Sub-Module A and Sub-Module B exhibit mutual execution dependencies, inline function imports (`from ... import` inside methods) are STRICTLY BANNED. Use a typed `typing.Protocol` or `Callable` injected by the parent facade (`X/__init__.py`).
      4. **Zero Garbage Drawers**: Generic filenames (`utils.py`, `helpers.py`, `types.py`, `models.py`) are strictly prohibited.
      5. **Monolithic Method Closure Unnesting**: When unnesting methods exceeding 350 lines with `nonlocal` closures, encapsulate local mutable state and concurrency locks in a private `@dataclass` container scoped to the invocation stack frame. Hoist closures to private helpers or sub-module functions taking that state container, keeping outer public signatures 100% identical and satisfying the 500-line gate.</mandatory_pattern>
      <catastrophic_reason>Top-down extraction causes circular import deadlocks, and moving Pydantic models without their `model_rebuild()` calls crashes FastAPI startup with `PydanticUndefinedAnnotation`.</catastrophic_reason>
    </rule_block>

    <rule_block id="ssot_decomposition_mandate">
      <mandatory_pattern>Enforce codebase-wide SSOT consolidation during planning:
      1. **UNIFY (Pre-Flight Fragmentation Audit)**: Search the codebase for existing files sharing the target domain name. Merge extracted logic into existing SSOT modules rather than creating duplicate files.
      2. **SUBDIRECTORY STRUCTURE**: Place extracted sub-modules into a cleanly named domain package directory (`backend_v2/services/[domain]/`) rather than cluttering parent directories with prefix-hacked files.
      3. **500-Line Partitioning Gate**: No planned target sub-module may exceed 500 lines (or 400 lines of pure business logic). Slice large bounded contexts into cohesive sub-modules before generating plans.</mandatory_pattern>
      <catastrophic_reason>Extracting "mini-god" files (>500 lines) or duplicating existing domain modules preserves architectural fragmentation.</catastrophic_reason>
    </rule_block>

    <rule_block id="dynamic_ast_fidelity_and_state_mandate">
      <mandatory_pattern>Verify structural and state invariants dynamically based on the AST inventory $\mathcal{I}_{orig}$ of the target God File (do NOT force domain-irrelevant checks onto unrelated files):
      1. **Dynamic Security &amp; Guard Parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$)**: Every authorization check, tenant isolation guard, or validation decorator present in the original God File AST MUST be mathematically accounted for in the extracted sub-modules.
      2. **Shared Concurrency &amp; Transaction Integrity**:
         - *Database Sessions*: If the God File executes multi-step operations within a shared DB session/transaction, pass the session explicitly into sub-services.
         - *Concurrency Primitives*: If the God File contains `asyncio.Lock`, `asyncio.Semaphore`, or circuit breakers, encapsulate them in a shared `@dataclass(frozen=True)` container instantiated by the parent facade and injected into sub-services. Sub-services MUST NEVER instantiate independent locks.
         - *Stateless Sub-Services &amp; Ban on Stateful Attribute Mutation*: Sub-services and injected collaborators MUST NEVER store or mutate execution-scoped attributes (`self.<attr> = ...`) on `self` across coroutines (distinguishing immutable dependency injection bindings in `__init__` from banned execution-scoped mutable state). All execution-scoped identifiers and locks MUST be passed as explicit method parameters or inside an execution-scoped `@dataclass(frozen=True)` context.
         - *Validated State Transitions*: State transitions execute strictly inside `async with shared_locks.update_lock:` using validated domain transition methods or validated DTO builder methods during Epoch 2 hardening, rather than unvalidated `.model_copy(update=...)` calls.
      3. **RFC 7807 &amp; DLP Parity**: Preserve all structured `logger.error` + `AppException` dual-reporting and ensure OpenTelemetry/Logfire spans never serialize raw PII, prompts, or credentials.</mandatory_pattern>
      <catastrophic_reason>Dropping existing security guards or splintering `asyncio.Lock` instances across sub-services causes security regressions and Split-Brain concurrency corruption.</catastrophic_reason>
    </rule_block>

    <rule_block id="anti_abstraction_and_context_amnesia_mandate">
      <mandatory_pattern>
      1. **Verbatim Signature & Line-Bound Preservation**: Never use lazy placeholders (`# ... existing logic ...`). Wrap all file paths in `@-reference` syntax with exact `#Lnn-mm` line bounds matching a single AST ClassDef or FunctionDef node extracted via `_ast_boundary_utils.py` (specifically: `@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]`). Multi-method spanning bounds are strictly prohibited by MBD004.
      2. **Pre-Creation Reference Tagging ([NEW] & [DELETE])**: When referencing target sub-modules that do not yet exist on disk, ALWAYS prefix the link with `[NEW]` (specifically: `[NEW] @[backend_v2/services/report/lifecycle_service.py]`) to satisfy MBD003. When referencing transitional proxy files scheduled for removal, prefix with `[DELETE]`.
      3. **Dynamic Rules Injection**: Inject `<required_context_rules>` at the top of every generated plan and tracker.
      4. **Explicit Regression Test Contracts**: Every extraction plan MUST include a `<test_contracts>` XML block defining named `regression`, `positive`, and `negative` tests (`test_{method}_{scenario}_{expected}`) locking exact pre-extraction outputs.</mandatory_pattern>
      <catastrophic_reason>Omitted line bounds or vague test instructions cause Context Amnesia and silent logic drift during Tier 2 execution. Omitting [NEW] triggers fatal linter failures for missing files.</catastrophic_reason>
    </rule_block>
  </context_rules>

  <execution_protocol level="3">
    <step id="1" name="GREETING &amp; ORCHESTRATOR LOCK CHECK">
      <action>Print a concise summary of the Tier 3 Two-Epoch God Code Decomposition protocol.</action>
      <action>Enforce the DAG Orchestrator Gate: If the target file is in `backend_v2/services/orchestrator/`, STOP and request explicit user permission before proceeding.</action>
    </step>

    <step id="2" name="PRE-FLIGHT AST EXTRACTION, TEST BASELINE &amp; TECH DEBT INVENTORY">
      <action name="AST_BOUNDARY_EXTRACTION">Run `uv run python scripts/_ast_boundary_utils.py --file <path_to_domain_file> --extract-symbols` to extract defined symbols, classes, functions, and exact line boundaries. Manually inspect the target file to inventory all security hooks, decorators, and concurrency locks as invariant set $\mathcal{I}_{orig}$.</action>
      <gate name="TEST_BASELINE">Use `grep_search` to discover ALL unit and integration test files importing the target God File (specifically `test_[filename]*.py` in `backend_v2/tests/unit/` and `backend_v2/tests/integration/`) and run coverage across the entire matching test suite (`uv run pytest <all_matching_test_files> --cov=<path_to_domain_file>` or `uv run python scripts/flutter_audit_loop.py <target_path> --test`). Record passing test count and aggregate coverage % as `[BASELINE]`. If aggregate coverage &lt; 75%, generate `phase0_coverage_bootstrap.md` as a strict blocker.</gate>
      <action name="SYMBOL_MAP_AND_BLAST_RADIUS">Use `grep_search` to identify all 1-hop callers. Save the complete symbol-to-target mapping to `docs/epic/tasks_[filename]/symbol_migration_map.md`.</action>
      <action name="TECH_DEBT_INVENTORY_FOR_EPOCH_2">Audit the God File and its 1-hop callers against the 12-Item Tech Debt Checklist (1. `getattr`/`hasattr`/`isinstance(dict)`/`type(x) is dict`/`Any` annotations, 2. `.get()`/raw dicts/missing `strict=True`/explicit `strict=False` overrides, 3. anonymous 3+ tuples, 4. silent `except Exception:`/DLP, 5. unvalidated `model_copy`, 6. Python 3.14 PEP 695/673/742/`TaskGroup`, 7. magic numbers outside `settings.py`, 8. missing docstrings/`# type: ignore`, 9. Flutter hardcoded strings/colors, 10. missing negative ISTQB partitions, 11. stateful service mutations via `self.<attr> =`, 12. non-deterministic execution state via unordered set iterations or `uuid.uuid4()`). Record all findings in the tracker under **Epoch 2: Post-Cutover Tier 2 Hardening** (DO NOT mix into Epoch 1 extraction).</action>
      <action name="KI_PREFLIGHT_CHECK">If decomposition produces 3+ structurally identical sub-modules, reference or create a canonical KI template before generating plans.</action>
    </step>

    <step id="3" name="ADAPTIVE PLAN GENERATION (FAST-TRACK VS. FULL STRANGLER)">
      <action>Select the planning mode based on the Step 2 AST metrics:
        - **FAST-TRACK MODE (500–800 lines, &lt;= 3 target sub-modules, non-orchestrator)**: Generate ALL `phaseX_[domain]_extraction.md` plans in `docs/epic/tasks_[filename]/` in a single pass. No placeholder files or mid-flight Tier 3 re-invocations required.
        - **FULL STRANGLER MODE (&gt; 800 lines, &gt;= 4 target sub-modules, or orchestrator core)**: Generate detailed XML plans ONLY for Phase 1 and Phase 2 to prevent context saturation. Create header placeholders for Phase 3+ and insert a tracker gate to re-invoke `/tier3-god-code-decomposition` after Phase 2 completes.</action>
      <constraint name="HYBRID_XML_SANDWICH_MANDATE">Every generated plan MUST wrap its execution instructions in fenced XML `&lt;execution_protocol&gt;` blocks with `<required_context_rules>` and `<test_contracts>`.</constraint>
      <action name="SELF_HEALING_BOUNDARY_AUDIT">Run `uv run python scripts/audit_markdown_boundaries.py --file <path_to_plan>` on every generated plan. Fix any boundary errors (Circuit Breaker: stop after 3 consecutive failures).</action>
    </step>

    <step id="4" name="TWO-EPOCH TRACKER GENERATION (TRK001-TRK006 COMPLIANT)">
      <action>Create the master tracker at `docs/epic/[filename]_decomposition_tracker.md` with `<required_context_rules>` at the top. The tracker MUST strictly conform to `scripts/audit_tracker_output.py` formatting standards (TRK001-TRK006) containing `## Phase Execution Status`, `### Post-Implementation Gates`, `### Final Epic Audit`, `## Instructions for the Execution Agent`, `## Requirements Traceability Matrix`, and `# Session Handover Context`.</action>
      <action name="EPOCH_1_STRUCTURAL_PIPELINE">
        Under `## Phase Execution Status`, generate sequential `### Phase N: <Title>` sections for **Epoch 1 (Pure Structural Lift-and-Shift &amp; Atomic Cutover)**:
        1. `Phase 0: Coverage Bootstrap` (if baseline &lt; 75%).
        2. `Phase 1A: Leaf Types, Enums &amp; Helpers Extraction` (Bottom-Up Leaf-First).
        3. `Phase 1B..N: Cohesive Domain Sub-Module Extractions` (with explicit re-exports in `X.py`; existing unit tests 100% green).
        4. `Phase Cutover - Step 1: Mechanical Consumer Import Rewiring &amp; Test Suite Modularization`: Rewire all 1-hop consumer imports deterministically per `[NEW] @[docs/epic/tasks_filename/symbol_migration_map.md]`. If the test suite is already split across multiple `test_[filename]_*.py` files, rewire their imports to the new sub-modules and add missing per-submodule unit test suites rather than assuming a single monolithic test file (zero behavioral changes).
        5. `Phase Cutover - Step 2: Atomic Package Cutover &amp; Pre-Flight DI Boot Audit`: Atomically replace external proxy `X.py` with package facade `X/__init__.py`, update DI bindings (`dependencies.py` / providers), and verify 0 remaining legacy imports plus 100% green `backend_audit_loop.py` / `flutter_audit_loop.py --test`.
        6. `Phase Cutover - Step 3: Post-Delete AST Guardrail QGR017 Lockdown &amp; Smoke Test`: Register retired God File path in `@[scripts/_ast_guardrails.py]` (`QGR017`), update `@[.agents/rules/04_directory_reference.md]`, and run `run_seed.py local` + modular test suite.
      </action>
      <action name="EPOCH_2_HARDENING_PIPELINE">
        Under `### Post-Implementation Gates`, define the sequential gates for **Epoch 2 (Post-Cutover Tier 2 Hardening)**:
        1. `#### Tier 2 Hardening (Backend)`: Register every newly extracted sub-module as an explicit indented child checkbox (`  - [ ] [NEW] @[path/to/submodule.py]`). Mandate that each sub-module resolution resolves the Step 2 12-Item Tech Debt Inventory, audits OpenTelemetry / Logfire `set_attribute` calls in all extracted sub-modules to guarantee zero raw user prompt, input payload, or PII serialization, adds negative ISTQB boundary tests, AND synchronizes all immediate 1-hop callers if method signatures are tightened.
        2. `#### Conditional Mutation / SDUI Parity Gates`: Add `audit_mutation_coverage.py` (if mathematical/scoring core) or `test_sdui_semantic_parity.py` (if SDUI/PDF).
        3. `#### Architectural Documentation Synchronization`: Parameterized `/tier7-describe-architecture` command.
      </action>
      <action name="SELF_HEALING_TRACKER_AND_PARITY_AUDIT">Run `uv run python scripts/audit_tracker_output.py --file docs/epic/[filename]_decomposition_tracker.md` and `uv run python scripts/audit_plan_tracker_parity.py --plan-dir docs/epic/tasks_[filename] --tracker docs/epic/[filename]_decomposition_tracker.md`. Fix any formatting, parity, or TRK001-TRK006 errors before proceeding to Step 5 (Circuit Breaker: stop after 3 consecutive failures).</action>
    </step>

    <step id="5" name="EMBEDDED HANDOVER CONTEXT &amp; MANDATORY STOP">
      <action>Append `# Session Handover Context` at the bottom of the tracker file conforming strictly to TRK004 (mandating `## Achieved`, `## Learned`, `## Resume Command`, and `## Remaining`). Set `## Resume Command` to `/tier2-execute [NEW] @[plan_path] [NEW] @[tracker_path]`.</action>
      <action>Present the generated tracker and plans using `@-reference` syntax and output the exact next-step command: `/tier2-execute --full-auto [NEW] @[plan_path] [NEW] @[tracker_path]`.</action>
      <constraint name="MANDATORY_STOP">STOP immediately after presenting the plans. Do NOT modify any `.py` or `.dart` files in this session.</constraint>
    </step>
  </execution_protocol>
</system_prompt>
```
