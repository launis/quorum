---
name: tier3-god-code-decomposition
description: System 2 Decomposition Planner for Legacy Refactoring (Two-Epoch Strangler Fig Protocol).
---

# Tier 3 Skill: God Code Decomposition Planner

This skill governs the systematic planning and decomposition of heavy "God Code" files (>500 lines) according to Domain-Driven Design (DDD) and Single Responsibility Principles (SRP). It enforces a strict **Two-Epoch Strangler Fig Protocol** that cleanly separates **Epoch 1 (Pure Structural Lift-and-Shift & Proxy Cutover)** from **Epoch 2 (Post-Cutover Tier 2 Hardening)**. **This is a pure planning tier; it does NOT write domain code. It generates implementation plans and a tracker, delegating execution to Tier 2.**

### Headless CLI Autonomous Execution (Recommended)
```powershell
agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier3-god-code-decomposition @[<target_file>] --full-auto. PERMISSION GRANTED for continuous full-auto planning across all steps. Proceed autonomously through Step 1 to Step 5 without intermediate confirmations."
```

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Specifically for a single file: "Decompose God file @[backend_v2/services/orchestrator/dag_executor.py]", OR for a multi-file cluster / subsystem: "Decompose God file cluster @[backend_v2/services/pdf_generator.py] and @[backend_v2/services/report_service.py]"]</objective>
  <role>Senior Staff Engineer &amp; Principal Systems Architect</role>

  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool calls in a new task MUST be `view_file` to physically load `@[AGENTS.md]` (for Universal Quality Gates), `@[.agents/rules/00-antigravity-core.md]`, and `@[.agents/skills/tier0-create-plan/SKILL.md]`. First review the context-injected Knowledge Item (KI) summaries, and load `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`, and `@[ki_zero_permissive_typing.md]` via `view_file`. Dynamically load domain rules based on target scope:
        - IF decomposing Python backend: read `@[.agents/rules/01-python-backend.md]`
        - IF decomposing Flutter frontend: read `@[.agents/rules/02_flutter_desktop.md]`
        - IF touching Database/Seed Data: read `@[.agents/rules/03_seed_vault.md]`
        - IF touching file structures/routing: read `@[.agents/rules/04_directory_reference.md]`
        - IF touching LLM/Prompts: read `@[.agents/rules/05_llm_architecture.md]`
      </mandatory_pattern>
      <catastrophic_reason>Refactoring massive files without loading core architectural invariants causes hallucinated module boundaries and broken system integration.</catastrophic_reason>
    </rule_block>

    <rule_block id="multi_file_cluster_and_topological_batching">
      <mandatory_pattern>When decomposing a cluster of multiple coupled God Files or an entire subsystem:
      1. **Inter-File Topological Dependency Ordering**: Construct the inter-file dependency DAG of all target files in the cluster using `grep_search`. Decompose leaf target files first. Caller targets MUST NOT begin Epoch 1 until their callee targets have fully completed Epoch 1 and Epoch 2, OR shared abstractions between them must be pre-extracted into a shared SSOT module in Phase 1A.
      2. **Per-File Sequential Epoch Firewall**: Never interleave Epoch 1 of Target File B into Epoch 1 of Target File A. Each file in the cluster MUST execute its own Two-Epoch Strangler Fig lifecycle sequentially (File A: Epoch 1 -> Epoch 2, followed by File B: Epoch 1 -> Epoch 2).
      3. **Unified Subsystem Master Tracker vs. Per-File Task Directories**: Create a single unified master tracker at `docs/epic/[subsystem]_decomposition_tracker.md` with distinct `### Target: [filename]` execution sections. Isolate task implementation plans into per-file subdirectories (`docs/epic/tasks_[filename_a]/`, `docs/epic/tasks_[filename_b]/`).</mandatory_pattern>
      <catastrophic_reason>Decomposing multiple coupled God Files simultaneously or in arbitrary order creates circular proxy dependencies and untraceable regressions across overlapping Epochs.</catastrophic_reason>
    </rule_block>

    <rule_block id="orchestrator_god_object_fragility">
      <mandatory_pattern>If the target file resides ANYWHERE within `backend_v2/services/orchestrator/` (specifically including: `atomizer.py`, `dag_executor.py`, `topological_evaluator.py`, `matrix_reducer.py`, `causal_cohesion_evaluator.py`), the planner MUST STOP immediately at Step 1 and explicitly request "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" before generating any decomposition plans. Any code blocks or methods marked with ARCHITECTURE LOCK comments inside the target file MUST be relocated verbatim (100% untouched AST body and preserving the ARCHITECTURE LOCK comment header) into their target domain sub-module during Epoch 1, without altering their internal logic.</mandatory_pattern>
      <catastrophic_reason>Modifying the core DAG Orchestrator engine without explicit clearance and blast-radius evaluation causes cascading execution failures across all workflows.</catastrophic_reason>
    </rule_block>

    <rule_block id="monolith_archetype_invariant_profiles">
      <mandatory_pattern>Every target God File MUST be classified into one of the 5 canonical Monolith Archetypes, applying its specific architectural invariant profile:
      1. **Archetype A: Algorithmic / Pure Compute Engine**: Pure compute engine law (zero semaphores, zero network I/O, immutable DTO inputs and outputs); 100% mutant kill rate via `scripts/audit_mutation_coverage.py`.
      2. **Archetype B: Presentation / Streaming / Formatter**: Single-pipeline streaming, immutable DTO streaming, zero naked dictionaries, RFC 7807 dual-logging.
      3. **Archetype C: Ingress / Parser / Anti-Corruption Layer (ACL)**: Positive key checks, immediate typed DTO hydration, DLQ error recording, strict model location enforcement (relocating inline DTOs/Enums to `models/dtos/` in Phase 1A).
      4. **Archetype D: Macro Orchestrator &amp; Concurrency Core**: DAG Orchestrator Permission Gate, Two-Tier Concurrency SSOT, stateless sub-services (banning `self.<attr> = ...` across coroutines), validated domain transitions, verbatim relocation of ARCHITECTURE LOCK blocks.
      5. **Archetype E: Frontend Desktop View / Widget Monolith**: Feature-First isolation (`lib/features/[domain]/`), Dart Guardrail compliance (`_dart_guardrails.py`: DGR001-DGR005), separating Riverpod state notifiers from layout rendering widgets.</mandatory_pattern>
      <catastrophic_reason>Applying generic rules to specialized archetypes ignores archetype-specific failure modes.</catastrophic_reason>
    </rule_block>

    <rule_block id="two_epoch_separation_mandate">
      <banned_pattern>Mixing structural extraction (moving classes/functions across files) with behavioral hardening (removing `.get()` fallbacks, tightening Pydantic schemas, or fixing 12-item tech debt) inside the same phase while the legacy proxy file is still active.</banned_pattern>
      <mandatory_pattern>Every decomposition tracker MUST be strictly partitioned into two sequential, non-overlapping epochs:
      1. **EPOCH 1 — PURE STRUCTURAL LIFT-AND-SHIFT &amp; ATOMIC CUTOVER (Zero Behavioral Change)**:
         - Extract leaf types/helpers and domain sub-modules with **100% identical runtime behavior**, types, and method signatures.
         - Monolithic methods (>350 lines) with nested closures or sequential imperative stages may be unnested into local `@dataclass` state containers or single-responsibility Stage services while keeping outer public signatures 100% identical.
         - Perform Mechanical 1-Hop Consumer Import Rewiring using `symbol_migration_map.md`, split the monolithic test file into modular test files, execute the Atomic Package Cutover (`X.py` -> `X/__init__.py`), and physically delete the external proxy file.
      2. **EPOCH 2 — POST-CUTOVER TIER 2 HARDENING (Behavioral &amp; Type Lockdown)**:
         - ONLY AFTER Epoch 1 is 100% complete and the legacy proxy is deleted, schedule bounded Tier 2 Hardening tasks to resolve the discovered 12-Item Tech Debt Inventory on the newly isolated sub-modules, synchronizing all immediate 1-hop callers in the same atomic commit whenever public signatures change.</mandatory_pattern>
      <catastrophic_reason>Hardening extracted modules while legacy callers and monolithic tests still route through the proxy breaks behavioral parity mid-surgery.</catastrophic_reason>
    </rule_block>

    <rule_block id="strangler_fig_mandate">
      <mandatory_pattern>Plan the Epoch 1 decomposition incrementally using the Strangler Fig Pattern:
      1. **Import Proxy Pattern &amp; Explicit Re-Exports**: Mandate `__all__ = ["Symbol", ...]` AND explicit redundant aliases (`from sub import Symbol as Symbol`).
      2. **Two-Phase Package Strangler Protocol**: Sub-directory `X/` MUST NOT contain `__init__.py` while `X.py` exists. Test sub-directories `backend_v2/tests/unit/.../X/` MUST explicitly contain `__init__.py` from Step 1 onwards. Deleting `X.py` and creating `X/__init__.py` MUST occur in a single atomic step.
      3. **Domain Package Aggregator Facade**: Package facade (`__init__.py`) classes MUST NOT exceed 300 lines of code and must wire dependencies immutably in `__init__`.
      4. **Parent Package Re-Export Synchronization**: Synchronously update any parent package `__init__.py` re-exports during Atomic Proxy Cutover.</mandatory_pattern>
      <catastrophic_reason>Coexisting `X.py` and `X/__init__.py` crashes MyPy with duplicate module collisions.</catastrophic_reason>
    </rule_block>

    <rule_block id="test_coverage_prerequisite">
      <mandatory_pattern>Before Epoch 1 extraction begins, the target God File MUST have at least 75% test coverage. If baseline coverage is below 75%, generate a mandatory blocker plan `phase0_coverage_bootstrap.md` defining black-box Characterization Tests to lock current behavior to >=75% coverage before Phase 1A extraction starts.</mandatory_pattern>
      <catastrophic_reason>Decomposing an untested God File is blind surgery that silently destroys business logic.</catastrophic_reason>
    </rule_block>

    <rule_block id="topological_leaf_first_extraction_mandate">
      <mandatory_pattern>Construct an internal call-graph and type-graph DAG of the God File using `@[scripts/_ast_boundary_utils.py]`. Follow Bottom-Up Topological Leaf-First Order:
      1. **Phase 1A (Leaf Pre-Extraction)**: Extract depth-0 leaf types, centralized Enums (`backend_v2/models/enums.py`), shared constants, DTOs (`backend_v2/models/dtos/` or `models/domain/`), and leaf helper functions first.
      2. **Zero God File Imports**: Extracted sub-modules MUST NEVER import from the parent God File.
      3. **Circular Domain Decoupling &amp; Protocol-Driven Inversion Law**: Define and inject a lightweight `typing.Protocol` in `protocols.py` within the domain subpackage; inline function imports are strictly banned.
      4. **Zero Garbage Drawers**: Generic filenames (`utils.py`, `helpers.py`, `types.py`, `models.py`) are strictly prohibited.
      5. **500-Line Partitioning Gate**: No planned target sub-module may exceed 500 lines.</mandatory_pattern>
      <catastrophic_reason>Top-down extraction causes circular import deadlocks.</catastrophic_reason>
    </rule_block>

    <rule_block id="dynamic_ast_fidelity_and_state_mandate">
      <mandatory_pattern>Verify structural and state invariants dynamically based on the AST inventory $\mathcal{I}_{orig}$ of the target God File:
      1. **Dynamic Security &amp; Guard Parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$)**.
      2. **Shared Concurrency &amp; Transaction Integrity**: Encapsulate shared locks/semaphores in a `@dataclass(frozen=True)` container injected into stateless sub-services.
      3. **RFC 7807 &amp; DLP Parity**: Preserve all structured `logger.error` + `AppException` dual-reporting.</mandatory_pattern>
      <catastrophic_reason>Dropping existing security guards or splintering `asyncio.Lock` instances across sub-services causes security regressions and Split-Brain concurrency corruption.</catastrophic_reason>
    </rule_block>

    <rule_block id="anti_abstraction_and_context_amnesia_mandate">
      <mandatory_pattern>
      1. **Verbatim Signature &amp; Line-Bound Preservation**: Wrap all file paths in `@-reference` syntax with exact `#Lnn-mm` line bounds matching a single AST ClassDef or FunctionDef node extracted via `_ast_boundary_utils.py`.
      2. **Universal [NEW] Pre-Creation Tagging Mandate ([NEW] &amp; [DELETE])**: Prefix uncreated files with `[NEW]` and transitional proxy files scheduled for removal with `[DELETE]` on EVERY line where mentioned.
      3. **Dynamic Rules Injection**: Inject `<required_context_rules>` at the top of every generated plan and tracker.
      4. **Explicit Regression Test Contracts**: Include a `<test_contracts>` XML block in every extraction plan.</mandatory_pattern>
      <catastrophic_reason>Omitted line bounds or missing `[NEW]` tags trigger fatal linter failures under `audit_markdown_boundaries.py`.</catastrophic_reason>
    </rule_block>
  </context_rules>

  <execution_protocol level="3">
    <step id="1" name="GREETING &amp; ORCHESTRATOR LOCK CHECK">
      <action>Print a concise summary of the Tier 3 Two-Epoch God Code Decomposition protocol. If the target file is in `backend_v2/services/orchestrator/`, STOP and request explicit user permission before proceeding.</action>
    </step>

    <step id="2" name="PRE-FLIGHT AST EXTRACTION, TEST BASELINE &amp; TECH DEBT INVENTORY">
      <action name="AST_BOUNDARY_EXTRACTION">
        - For Python (`.py`): Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/_ast_boundary_utils.py --file <path_to_domain_file> --extract-symbols`.
        - For Flutter (`.dart`): Run `scripts/_dart_guardrails.py` and use `grep_search` to extract widget class and state controller boundaries.
      </action>
      <gate name="TEST_BASELINE">
        - For Python (`.py`): Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <path_to_domain_file> --test`. Record passing test count and aggregate coverage % as `[BASELINE]`. If aggregate coverage &lt; 75%, generate `phase0_coverage_bootstrap.md` as a strict blocker.
        - For Flutter (`.dart`): Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --test`.
      </gate>
      <action name="SYMBOL_MAP_AND_BLAST_RADIUS">Use `grep_search` to identify all 1-hop callers. Save the complete symbol-to-target mapping to `docs/epic/tasks_[filename]/symbol_migration_map.md`.</action>
      <action name="TECH_DEBT_INVENTORY_FOR_EPOCH_2">Audit the God File and its 1-hop callers against `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` and record all findings in the tracker under **Epoch 2: Post-Cutover Tier 2 Hardening** (DO NOT mix into Epoch 1 extraction).</action>
    </step>

    <step id="3" name="ADAPTIVE PLAN GENERATION (FAST-TRACK VS. FULL STRANGLER)">
      <action>Select SINGLE-FILE FAST-TRACK MODE (500–800 lines, &lt;= 3 target sub-modules), SINGLE-FILE FULL STRANGLER MODE (&gt; 800 lines or &gt;= 4 sub-modules), or MULTI-FILE SUBSYSTEM CLUSTER MODE.</action>
      <constraint name="HYBRID_XML_SANDWICH_MANDATE">Every generated plan MUST wrap its execution instructions in fenced XML `&lt;execution_protocol&gt;` blocks with `<required_context_rules>` and `<test_contracts>`.</constraint>
      <action name="SELF_HEALING_BOUNDARY_AUDIT">Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file <path_to_plan>` on every generated plan and fix any boundary errors.</action>
    </step>

    <step id="4" name="TWO-EPOCH TRACKER GENERATION (TRK001-TRK008 COMPLIANT)">
      <action>Create the master tracker at `docs/epic/[filename_or_subsystem]_decomposition_tracker.md` with `<required_context_rules>` at the top, Epoch 1 structural pipeline phases under `## Phase Execution Status`, and Epoch 2 hardening targets (exclusively surviving `[NEW]` sub-modules and modified surviving 1-hop callers, strictly excluding `[DELETE]` files) under `### Post-Implementation Gates` with the unified `--gate all` command (`$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/[filename]_decomposition_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`) on the `Tier 2 Hardening` headers.</action>
      <action name="SELF_HEALING_TRACKER_AND_PARITY_AUDIT">Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_tracker_output.py --tracker docs/epic/[filename]_decomposition_tracker.md` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_plan_tracker_parity.py --plan-dir docs/epic/tasks_[filename] --tracker docs/epic/[filename]_decomposition_tracker.md`.</action>
    </step>

    <step id="5" name="EMBEDDED HANDOVER CONTEXT &amp; MANDATORY STOP">
      <action>Append `# Session Handover Context` at the bottom of the tracker file conforming strictly to TRK004 (`## Achieved`, `## Learned`, `## Resume Command`, `## Remaining`). Present the generated tracker and plans using `@-reference` syntax and output: `/tier2-execute --full-auto [NEW] @[plan_path] [NEW] @[tracker_path]`.</action>
      <constraint name="MANDATORY_STOP">STOP immediately after presenting the plans. Do NOT modify any `.py` or `.dart` files in this session.</constraint>
    </step>
  </execution_protocol>
</system_prompt>
```

