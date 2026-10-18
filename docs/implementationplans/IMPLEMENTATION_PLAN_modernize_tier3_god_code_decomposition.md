<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Modernize Tier 3 God Code Decomposition Workflow

## Executive Summary
This implementation plan hardens and modernizes the Tier 3 God Code Decomposition Planner workflow (`@[.agents/workflows/tier3-god-code-decomposition.md]`) based on the exhaustive findings of the Tier 8 Red Team Security & Architecture Audit (`red_team_audit_tier3_god_code_decomposition.md`) and Tier 0 System 2 Research Deconstruction.

The refactoring eliminates seven critical vulnerabilities:
1. **Elimination of Text-Based Method Boundary Guessing**: Replaces naive `grep_search` with mandatory AST boundary extraction via `@[scripts/_ast_boundary_utils.py]`, preventing silent code cuts and syntax truncation.
2. **Resolution of Inter-Slice Circular Dependency Deadlocks**: Replaces generic type-splitting with strict **Bottom-Up Topological Leaf-First Order**, guaranteeing extracted modules never import unextracted logic from the God File.
3. **Protection of Shared In-Memory State and Concurrency Primitives**: Introduces mandatory shared concurrency state containers (`@dataclass(frozen=True)`) for `asyncio.Lock` (`_update_lock`), `asyncio.Semaphore`, and circuit breakers, eliminating Split-Brain state corruption during execution.
4. **Context Amnesia Prevention and Double-Migration Elimination**: Mandates in-flight module hardening prior to consumer migration and enforces strict batching of 1-hop consumer updates (maximum 5 files per batch) coupled with atomic commits and `/tier5-session-handover` intervals.
5. **Modern Python 3.14 & Quorum Modernity Sweep**: Expands the legacy 7-item checklist into an authoritative 10-item Tech Debt Inventory covering PEP 695 type aliases, PEP 750 template strings, PEP 742 `TypeIs`, Tuple Hell eradication, and strict Pydantic V2 configurations.
6. **Enforcement of Foundational Quality Gates & Facade Lockdown**: Integrates mandatory AST mutation testing (`@[scripts/audit_mutation_coverage.py]` with a 100% mutant kill rate on mathematical cores), SDUI/PDF semantic parity testing (`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`), post-deletion AST Guardrail `QGR017` lockdown, and canonical directory synchronization.
7. **Test Suite Preservation & Modular Test Decomposition Invariant**: Guarantees that existing monolithic tests continue passing without modification during extraction via the Strangler Fig proxy, and mandates that consumer migration explicitly rewires and decomposes monolithic test suites into modular test files mirroring the newly extracted domain modules.

---

## Scope & Target Boundaries

### Target Files (Read-Write)
- `[MODIFY] @[.agents/workflows/tier3-god-code-decomposition.md#L14-L85]` (Workflow Rules: core routing, DAG lock gate, leaf-first topological order, shared concurrency containers, security & DLP parity, test suite preservation)
- `[MODIFY] @[.agents/workflows/tier3-god-code-decomposition.md#L86-L147]` (Execution Protocol: AST boundary utilities, 10-item tech debt inventory, in-flight hardening, 5-file consumer batches, mutation & SDUI gates, modular test decomposition, QGR017 lockdown)

### Context Files (Read-Only)
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/01-python-backend.md]`
- `@[.agents/rules/04_directory_reference.md]`
- `@[.agents/workflows/tier0-create-plan.md]`
- `@[scripts/_ast_boundary_utils.py]`
- `@[scripts/_ast_guardrails.py]`
- `@[scripts/audit_markdown_boundaries.py]`
- `@[scripts/backend_audit_loop.py]`
- `@[scripts/audit_mutation_coverage.py]`
- `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Rule Block: `core_rules_routing` & Orchestrator Gate) | Banned lazy context assumptions, unverified workflow invocations, and unauthorized execution planning on fragile DAG orchestrator files. | Mandatory physical loading of `AGENTS.md`, `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/workflows/tier0-create-plan.md]`, `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`, and `@[ki_zero_permissive_typing.md]` on turn 1. Explicit Fail-Fast authorization gate for `backend_v2/services/orchestrator/` targets. Normalize all path references to forward slashes. | Pruned redundant generic rule prompts; centralized core orchestration constraints in SSOT rule references. | Mathematical verification via `scripts/audit_markdown_boundaries.py` and planner clearance gate. |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Rule Block: `topological_leaf_first_extraction_mandate`) | Banned naive type splitting, circular import bypasses via inline method-level imports, and newly extracted modules importing the original God File. | Mandatory internal call-graph DAG construction using `@[scripts/_ast_boundary_utils.py]`. Strict Phase 1A Pre-Extraction of leaf types, shared domain models, DTOs, constants, and shared leaf helpers (depth 0) before bounded contexts. | Pruned speculative multi-layer type wrapper hierarchies; enforce direct extraction into domain SSOT modules. | Static AST import cycle detection via `scripts/audit_clean_imports.py` and `scripts/_ast_guardrails.py`. |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Rule Block: `shared_state_and_transaction_audit`) | Banned Split-Brain concurrency primitive instantiations, independent splintered DB transactions, and mutable in-place state modifications across coroutines. | Mandatory encapsulation of shared concurrency primitives (`asyncio.Lock`, `asyncio.Semaphore`, circuit breakers) into an immutable `@dataclass(frozen=True)` dependency container. Execution state transits strictly via frozen Pydantic V2 DTOs updated via `.model_copy(update=...)` under shared lock. | Pruned dynamic reflection-based state proxies; state transitions are pure, typed, and localized. | `asyncio.Lock` isolation assertions and AST verification under `01-python-backend.md`. |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Rule Block: `decomposition_fidelity_mandate` & Test Invariance) | Banned dropping authorization checks (`_enforce_tenant_isolation`), silent exceptions missing RFC 7807 dual-logging, breaking existing monolithic tests during extraction, and leaving orphaned monolithic test suites after proxy deletion. | Existing monolithic tests must pass 100% green without modification throughout Phase 1 & 2 via the Hollow Shell proxy. During Consumer Migration (Phase 3), the monolithic test file is treated as a 1-hop consumer: all tests must be rewired to new domain modules and decomposed into focused test files mirroring the new architecture. Mechanically verify security hook survival and RFC 7807 dual-logging. | Pruned ad-hoc logging wrapper abstractions; test re-wiring is direct and maps 1:1 to decomposed modules. | Zero-leakage DLP audit, AST guardrail `QGR005`, and 100% test pass on existing test suites. |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Workflow Step 2: Pre-flight & Tech Debt Sweep) | Banned text-based regex line-guessing (`grep_search`), loose line bounds, and ignoring modern Python 3.14 tech debt in touched scopes. | Mandatory execution of `uv run python scripts/_ast_boundary_utils.py --file <file> --extract-symbols` to extract mathematical AST line boundaries including decorators. Authoritative 10-item Tech Debt Inventory covering PEP 695 type aliases, PEP 742 `TypeIs`, PEP 750 template strings, and strict Pydantic V2 per `@[ki_zero_permissive_typing.md]`. | Pruned manual line estimation and unstructured audit notes; boundaries are deterministic and machine-verifiable. | AST node line validation via `_ast_boundary_utils.py --validate-bound` and `scripts/audit_markdown_boundaries.py`. |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Workflow Steps 3, 4 & 5: Pipeline, Batch Migration & Handover) | Banned big-bang consumer migration, legacy `tmp/` scratch files, unhardened module consumption (Double-Migration trap), leaving eternal hollow shell facades, and deprecated resume commands. | Extracted domain modules must pass Tier 2 Hardening BEFORE external 1-hop consumers are migrated. Batch consumer migrations (including test files) into <=5 files per batch with atomic commits and `/tier5-session-handover`. Mandate 100% mutant kill rate on mathematical cores (`@[scripts/audit_mutation_coverage.py]`), SDUI parity (`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`), and AST Guardrail `QGR017` facade lockdown. Modernize Phase 4 session handover command syntax to `/tier2-execute --full-auto plan_path tracker_path`. | Pruned complex multi-file simultaneous migration spirals; bounded 5-file batches prevent LLM context amnesia. | 100% mutation kill rate verification, SDUI integration test pass, and `_ast_guardrails.py` QGR017 enforcement. |
| **@[.agents/workflows/tier3-god-code-decomposition.md]**<br>(Workflow Step 7: Boundary Audit Self-Healing) | Banned unverified workflow documentation releases, unescaped XML tags, ambiguous words, and broken relative file paths. | Mandatory execution of `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md` with 0 fatal findings and 0 warnings before sign-off. | Pruned manual markdown formatting checklists; audit script provides deterministic automated proof. | Clean exit code 0 from `scripts/audit_markdown_boundaries.py`. |

---

## Phase 1: Pre-Implementation Cleanups & Technical Debt Remediation
Target file `@[.agents/workflows/tier3-god-code-decomposition.md]` currently contains pre-existing markdown syntax defects flagged by `@[scripts/audit_markdown_boundaries.py]`:
1. **Windows Path Separators**: Legacy Windows backslashes (`\`) are present in path references (`.agents\rules\00-antigravity-core.md`, `docs\epic\tasks_[filename]\symbol_migration_map.md`, `docs\epic\tasks_[filename]\`, `docs\epic\[filename]_decomposition_tracker.md`). These must be normalized to POSIX forward slashes (`/`).
2. **Ambiguous Documentation Terminology**: Occurrences of non-deterministic words (specifically: line 77) must be replaced with deterministic language per `anti_ambiguity_mandate`.
3. **Unescaped XML Tags in Descriptions**: Bare text occurrences of the execution protocol tag inside descriptive constraints (specifically line 113) cause XML tag nesting mismatches and must be escaped (`&lt;execution_protocol&gt;`).
4. **Invalid Dummy File References**: Non-existent placeholder paths inside `@-reference` syntax trigger `MBD003` fatal errors. These must be replaced with valid real-world reference paths (`@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]`, `@[backend_v2/services/execution/lifecycle_service.py#L23-L248]`, `@[backend_v2/services/execution/ingress_service.py#L48-L133]`) or descriptive format specifications without raw `@-reference` triggers on fictitious filenames.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PRE_FLIGHT_TECH_DEBT_AND_CORE_RULES_ROUTING_OVERHAUL">
    <action>Modify `@[.agents/workflows/tier3-god-code-decomposition.md]` to update the `core_rules_routing` rule block.</action>
    <action>Require explicit physical loading of `AGENTS.md`, `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/workflows/tier0-create-plan.md]`, `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`, and `@[ki_zero_permissive_typing.md]` before any planning actions begin.</action>
    <action>Inject the DAG Orchestrator &amp; Architecture Lock Gate: If the target file resides within `backend_v2/services/orchestrator/` (specifically and exhaustively: `atomizer.py`, `dag_executor.py`, `topological_evaluator.py`, `matrix_reducer.py`, `causal_cohesion_evaluator.py`), the planner MUST STOP and explicitly request `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"`. Furthermore, blocks marked with `ARCHITECTURE LOCK` must remain untouched.</action>
    <action>Normalize all legacy Windows backslashes (`\`) across path references in `@[.agents/workflows/tier3-god-code-decomposition.md]` (specifically lines 15, 68, 97, 111, 124, 126, 137) to POSIX forward slashes (`/`).</action>
    <action>Replace ambiguous non-deterministic phrasing on line 77 (specifically replacing non-deterministic patterns with `(specifically: "write unit tests" or "ensure coverage")`) with deterministic SSOT terminology per `anti_ambiguity_mandate`.</action>
    <action>Escape bare execution protocol tag syntax on line 113 to `&lt;execution_protocol&gt;` to resolve MBD002 XML tag nesting mismatches.</action>
    <action>Replace fictitious placeholder path references on lines 68, 117, 126, and 127 with valid real-world workspace paths (`@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]`, `@[backend_v2/services/execution/lifecycle_service.py#L23-L248]`, `@[backend_v2/services/execution/ingress_service.py#L48-L133]`) or descriptive format specifications without `@-reference` triggers on fictitious filenames to eliminate MBD003 fatal errors.</action>
    <constraint invariant="orchestrator_god_object_fragility">
      Prevent unauthorized planning or decomposition on core DAG orchestrator components without full blast-radius authorization.
    </constraint>
    <constraint invariant="absolute_path_context_amnesia_ban">
      Ensure all file references across the workflow use normalized relative paths with forward slashes.
    </constraint>
  </step>

  <step id="2" name="TOPOLOGICAL_LEAF_FIRST_EXTRACTION_MANDATE">
    <action>In `@[.agents/workflows/tier3-god-code-decomposition.md]`, replace the rule block `circular_dependency_prevention` with `topological_leaf_first_extraction_mandate`.</action>
    <action>Mandate internal call-graph and type-graph DAG construction prior to phase definition using `@[scripts/_ast_boundary_utils.py]`.</action>
    <action>Enforce Phase 1A Pre-Extraction of leaf types, shared domain models, DTOs, constants, and shared leaf helper methods (depth 0 in the call graph, including `_enforce_tenant_isolation`) into dedicated SSOT modules before extracting higher-level bounded contexts.</action>
    <action>Enforce that newly extracted domain files NEVER import the original God File and NEVER use inline function-level imports, mathematically eliminating circular dependency deadlocks.</action>
    <constraint invariant="topological_leaf_first_extraction_mandate">
      Extracted modules must only depend on previously extracted lower-depth modules or established external SSOTs.
    </constraint>
    <constraint invariant="inline_imports_ban">
      Inline method-level imports are strictly prohibited as a mechanism to bypass circular dependencies.
    </constraint>
  </step>

  <step id="3" name="SHARED_CONCURRENCY_STATE_AND_TRANSACTION_AUDIT">
    <action>In `@[.agents/workflows/tier3-god-code-decomposition.md]`, replace the rule block `state_and_transaction_audit` with `shared_state_and_transaction_audit`.</action>
    <action>Expand the audit mandate across three distinct axes: 1) Database Session &amp; Transaction Atomicity, 2) Shared Concurrency &amp; Synchronization Primitives (`asyncio.Lock`, `asyncio.Semaphore`, Circuit Breakers), and 3) Stateless Sub-Service Invariant.</action>
    <action>Require that shared concurrency primitives be encapsulated into an immutable `@dataclass(frozen=True)` dependency container instantiated by the facade and injected into each sub-service constructor.</action>
    <action>Require that execution-scoped mutable state transit strictly through immutable Pydantic V2 Context Envelopes (`ConfigDict(strict=True, extra="forbid", frozen=True)`) updated exclusively via `.model_copy(update=...)` inside the shared lock.</action>
    <constraint invariant="async_io_lock_isolation_mandate">
      Protect against Split-Brain lock instantiation across decomposed services.
    </constraint>
    <constraint invariant="frozen_state_mutability">
      Enforce immutable model state copies inside concurrency synchronization locks.
    </constraint>
  </step>

  <step id="4" name="SECURITY_DLP_TELEMETRY_AND_RFC7807_PARITY">
    <action>In `@[.agents/workflows/tier3-god-code-decomposition.md]`, update the rule block `decomposition_fidelity_mandate`.</action>
    <action>Mandate verification that authorization hooks (`_enforce_tenant_isolation`, `is_system_core`) survive extraction into new domain boundaries.</action>
    <action>Mandate verification of RFC 7807 Dual-Reporting: Every `AppException` must preserve its structured `logger.error` preceding call with Opaque Stripe IDs (`blk_...`, `stp_...`, `wor_...`).</action>
    <action>Mandate verification of Data Leak Prevention (DLP): OpenTelemetry and Logfire spans must never leak raw HTTP payloads, user prompts (PII), or credentials into span attributes during inter-service dispatch.</action>
    <action>Mandate verification of Test Suite Invariance &amp; Modular Decomposition: Explicitly codify that existing unit tests testing the original God File MUST run 100% green without modification throughout the extraction phases via the Hollow Shell proxy. During Consumer Migration, the monolithic test file must be treated as a 1-hop consumer: all test imports must be rewired to the new domain modules, and the monolithic test file must be cleanly decomposed into focused unit test files mirroring the newly extracted modules.</action>
    <action>Mandate cleanup of orphaned test fixtures and updating of central Dependency Injection containers (`dependencies.py` or Flutter providers) using typed containers.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">
      Guarantee RFC 7807 structured error logging preceding all exception raises.
    </constraint>
    <constraint invariant="data_leak_logging">
      Enforce strict Data Leak Prevention across all decomposed telemetry spans.
    </constraint>
    <constraint invariant="test_suite_invariance_and_decomposition">
      Guarantee existing tests pass without modification during extraction and are cleanly decomposed alongside domain modules.
    </constraint>
  </step>

  <step id="5" name="AST_BOUNDARY_CALCULATION_AND_PYTHON_314_TECH_DEBT_INVENTORY">
    <action>In `@[.agents/workflows/tier3-god-code-decomposition.md]`, update Step 2 (`step id="2"`, PHASE 1: Pre-flight &amp; Baseline Validation).</action>
    <action>Replace naive `grep_search` line-guessing with mandatory execution of `uv run python scripts/_ast_boundary_utils.py --file <path_to_domain_file> --extract-symbols` to extract mathematical `lineno` and `end_lineno` spans including decorators.</action>
    <action>Expand the 7-item technical debt sweep into an authoritative 10-item Tech Debt Inventory covering:
      1. Duck Typing &amp; Reflection (`getattr`, `hasattr`, `isinstance(x, dict)`).
      2. Fallbacks &amp; Raw Dicts (`.get("key", default)`, unannotated dict accumulators, missing `ConfigDict(strict=True, extra="forbid")`).
      3. Tuple Hell &amp; Anonymous State Tuples (multi-value tuples of 3+ items or 2+ identical primitives).
      4. Error Handling &amp; DLP (bare `except Exception:`, missing RFC 7807 structured dual-logging, PII logging).
      5. Pydantic V2 Strictness &amp; Annotations (unvalidated `model_copy`, missing PEP 593 `Annotated`, `RootModel` usage).
      6. Python 3.14 Modern Syntax (PEP 695 `class C[T]:` and `type Alias = ...`, PEP 673 `Self`, PEP 742 `TypeIs`, PEP 750 template strings, `pathlib.Path`, PEP 734 `interpreters`, `asyncio.TaskGroup` with `except*`).
      7. Branching &amp; Configuration (hardcoded timeouts/URLs outside `settings.py`, unbounded I/O, >2 branch routing missing Strategy + Registry).
      8. Docstrings &amp; Hygiene (missing PEP 257 docstrings, `Raises: None`, unannotated `# type: ignore`).
      9. Flutter Frontend (hardcoded strings, hex colors, manual string clippings, missing `AppErrorBoundary`).
      10. ISTQB Testing &amp; Polyfactory (missing negative partitions, legacy dictionary fixtures, tautological mocks).
    </action>
    <constraint invariant="ast_boundary_verification_mandate">
      Forbid simple regex searching for method boundaries in Python files exceeding 300 lines.
    </constraint>
    <constraint invariant="python_314_modern_syntax">
      Enforce PEP 695 type parameters, PEP 742 TypeIs, and PEP 750 template strings across all modernized code.
    </constraint>
  </step>

  <step id="6" name="EXTRACTION_PIPELINE_BATCH_MIGRATION_AND_QUALITY_GATES">
    <action>In `@[.agents/workflows/tier3-god-code-decomposition.md]`, update Step 3 (`step id="3"`), Step 4 (`step id="4"`), and Step 5 (`step id="5"`).</action>
    <action>Remove all references to legacy `tmp/` directories (`tmp/hardening_state.json`), enforcing that temporary scratch data resides exclusively in `<appDataDir>/brain/<conversation-id>/scratch/`.</action>
    <action>Mandate injection of the canonical `<required_context_rules>` block (using `rule` and `knowledge_item` tags) in all generated plans and trackers.</action>
    <action>Reorder the decomposition pipeline: Extracted domain modules MUST undergo Tier 2 Hardening BEFORE external 1-hop consumers are migrated, ensuring target interfaces are finalized and preventing the Double-Migration trap.</action>
    <action>Partition "Proxy Sunset &amp; Consumer Migration" into discrete batches of at most 5 files per batch. Each batch requires: import rewiring, 1-hop tech debt resolution, `backend_audit_loop.py` execution, atomic `git commit`, and `/tier5-session-handover` between batches. Explicitly include monolithic test suites in this consumer migration, decomposing them into focused test files mirroring the newly extracted modules.</action>
    <action>Enforce Conditional Mathematical Core Gate: Foundational scoring and DAG evaluation modules MUST achieve a 100% mutant kill rate under `uv run python scripts/audit_mutation_coverage.py`.</action>
    <action>Enforce Conditional SDUI/PDF Semantic Parity Gate: Extracted view models, SDUI blocks, or templates MUST pass `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Enforce AST Guardrail QGR017 Lockdown: Following physical proxy deletion, register the retired facade path in `@[scripts/_ast_guardrails.py]` (rule `QGR017`, FATAL severity), update `@[.agents/rules/04_directory_reference.md]`, and issue parameterized `/tier7-describe-architecture` synchronization directives.</action>
    <action>Modernize Step 5 (Phase 4 Embedded Handover Context) to replace legacy parameter flags with standardized continuous execution syntax `/tier2-execute --full-auto plan_path tracker_path` using POSIX forward slashes.</action>
    <constraint invariant="remedial_strangler_fig_proxy">
      Enforce maximum 5 files per consumer migration batch and permanent facade deletion backed by QGR017.
    </constraint>
    <constraint invariant="mathematical_core_mutation_testing_invariance">
      Enforce 100% mutant kill rate on mathematical scoring engines.
    </constraint>
    <constraint invariant="sdui_contract_fracture_prevention">
      Enforce 1:1 Flutter UI and PDF semantic parity verification.
    </constraint>
  </step>

  <step id="7" name="MARKDOWN_BOUNDARY_VERIFICATION_AND_SELF_HEALING">
    <action>Execute `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md`.</action>
    <action>Verify 0 fatal findings, 0 ambiguity warnings, 0 XML nesting errors, and 0 missing file references.</action>
    <action>If any boundary violations emerge, perform surgical in-place remediation and re-run the verification gate.</action>
    <constraint invariant="universal_quality_gate">
      Mathematical verification of markdown boundaries must pass cleanly before task sign-off.
    </constraint>
  </step>
</execution_protocol>
```

---

## Architectural Safeguards & Verification Plan

### Test & Validation Commands
1. **Automated Markdown Boundary Audit**:
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md
   ```
2. **AST Guardrail Validation**:
   ```powershell
   uv run python scripts/_ast_guardrails.py
   ```
3. **Targeted Unit Test Verification**:
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -k "qgr017"
   ```

### Anti-Happy-Path Test Scenarios

#### Scenario 1: Unauthorized DAG Orchestrator Target (Negative Path)
- **Input**: User attempts to invoke Tier 3 decomposition on `backend_v2/services/orchestrator/dag_executor.py` without prior blast-radius clearance.
- **Expected Outcome**: The planner halts immediately at Step 1, refusing to generate decomposition plans until explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` authorization is recorded.

#### Scenario 2: Legacy Coverage Under-Threshold Block (Negative Path)
- **Input**: God Code target file exhibiting 58% baseline unit test line coverage.
- **Expected Outcome**: The planner halts structural extraction planning and mandates a blocking `Phase 0: Coverage Bootstrap Plan` containing Characterization Golden Master tests that must achieve 75% verified coverage before Phase 1 extraction begins.

#### Scenario 3: Mathematical Core Mutation Survival (Negative Path)
- **Input**: Decomposed mathematical scoring module (`UnifiedScoringEngine`) achieving 94% line coverage but failing to kill 2 relational operator mutants (`>` mutated to `>=`).
- **Expected Outcome**: Pre-delete quality gate rejects the decomposition, halting proxy deletion until unit test assertions are strengthened to achieve a 100% mutant kill rate.

#### Scenario 4: Post-Deletion Resurrected Facade Import (Negative Path)
- **Input**: Downstream consumer imports a symbol from the deleted God Code facade file.
- **Expected Outcome**: AST Guardrail `QGR017` in `@[scripts/_ast_guardrails.py]` flags the import with FATAL severity during Stage 4 of `backend_audit_loop.py`, blocking CI/CD merging.

#### Scenario 5: Monolithic Test Suite Migration Regression (Negative Path)
- **Input**: A monolithic test file (`test_monolith.py`) is left importing from the deleted God Code facade file after proxy deletion.
- **Expected Outcome**: Pre-Delete Zero-Reference check and `backend_audit_loop.py` catch the residual import with FATAL error, halting proxy deletion until all tests are rewired and decomposed into dedicated test modules mirroring the new domain architecture.

#### Scenario 6: Successful Compliant Decomposition (Positive Path)
- **Input**: Monolithic service file (>500 lines) evaluated under modernized Tier 3 workflow.
- **Expected Outcome**: AST boundaries extracted via `@[scripts/_ast_boundary_utils.py]`, domain slices sorted bottom-up in leaf-first topological order, shared concurrency primitives isolated in a frozen dependency container, consumer and test migrations structured into <=5 file batches, 100% green quality gates passed, and proxy safely deleted with AST guardrail lockdown.

### Non-Destructive End-to-End Dry-Run Verification Protocol

To empirically prove that the modernized Tier 3 Planner functions end-to-end on real monolithic codebases without modifying production source code, execute the following dry-run verification suite:

#### Target 1: Real-World Monolith Decomposition Planning (Positive Path)
- **Target File**: `@[backend_v2/services/auth.py]` (993 lines, 30 AST symbol definitions spanning `OrganizationRepository`, `UserRepository`, and `AuthService`).
- **Pre-Flight Test Baseline**: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth` (Verifies 30 passing unit tests and 93% line coverage, exceeding the 75% threshold).
- **Execution Command**:
  ```powershell
  /tier3-god-code-decomposition --target="backend_v2/services/auth.py"
  ```
- **Expected Verification Criteria**:
  1. **Automated Baseline Recording**: Tier 3 records `[BASELINE] 30 passed, 93% coverage` without triggering Phase 0 bootstrap blocker.
  2. **Deterministic AST Boundary Extraction**: Executes `uv run python scripts/_ast_boundary_utils.py --file backend_v2/services/auth.py --extract-symbols`, extracting exact symbol line spans without regex approximation.
  3. **Topological Leaf-First Extraction Order**: Deconstructs call graph into Phase 1A leaf models/repositories (`OrganizationRepository`, `UserRepository`) before higher-level `AuthService` slices.
  4. **Contract-Compliant Artifact Generation**: Generates `docs/epic/tasks_auth/symbol_migration_map.md`, `phase1_repositories_extraction.md`, and master tracker `docs/epic/auth_decomposition_tracker.md`.
  5. **Deterministic Markdown Audit Clearance**: Passes `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/auth_decomposition_tracker.md` with 0 fatal errors and 0 warnings.
  6. **Zero-Production-Mutation Invariant**: `git status` verifies zero modifications to `.py` production files.

#### Target 2: DAG Orchestrator Lock Gate Clearance (Negative Path)
- **Target File**: `@[backend_v2/services/orchestrator/dag_executor.py]` (1,632 lines).
- **Execution Command**:
  ```powershell
  /tier3-god-code-decomposition --target="backend_v2/services/orchestrator/dag_executor.py"
  ```
- **Expected Verification Criteria**:
  1. **Immediate Fail-Fast Halt**: Step 1 halts immediately, refusing to create plans until explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` authorization is recorded.

