---
description: System 2 Decomposition Planner for Legacy Refactoring
---

# Tier 3 Workflow: God Code Decomposition Planner

This workflow is designed for the systematic planning and decomposition of heavy "God Code" files according to Domain-Driven Design (DDD) and Single Responsibility Principles (SRP). Use this when a large file has grown beyond 500 lines and encapsulates too many decoupled responsibilities. This protocol utilizes the Strangler Fig Pattern to ensure safety. **This is a pure planning tier; it does NOT write domain code. It generates implementation plans and a tracker, delegating execution to Tier 2.**

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Target file specifically: "backend_v2/services/execution.py"]</objective>
  <role>Senior Staff Engineer & Python Systems Architect</role>
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool calls in a new task MUST be `view_file` to load the root rules. ALWAYS read `AGENTS.md` (for Universal Quality Gates) AND `.agents\rules\00-antigravity-core.md`. YOU MUST ALSO ALWAYS read `@[ki_god_code_prevention.md]`. Analyze your target: IF decomposing the Python backend, ADDITIONALLY read `01-python-backend.md`. IF decomposing Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. IF touching Database/Seed Data, ADDITIONALLY read `03_seed_vault.md`. IF touching file structures/routing, ADDITIONALLY read `04_directory_reference.md`. IF touching LLM/Prompts, ADDITIONALLY read `05_llm_architecture.md`.</mandatory_pattern>
      <catastrophic_reason>Refactoring massive files without the core architecture causes hallucinated boundaries that violate Phase 9 system integration.</catastrophic_reason>
    </rule_block>
    <rule_block id="strangler_fig_mandate">
      <mandatory_pattern>You MUST plan the decomposition incrementally using the Strangler Fig Pattern (extracting one cohesive slice at a time) rather than attempting a single massive rewrite. **Import Proxy Pattern (Delegation before Deletion & Explicit Re-Exports)**: If moving files into a subdirectory breaks hundreds of imports codebase-wide, the original methods in the God File MUST NOT be blindly deleted. They must be temporarily retained as proxy methods (delegating to the new extracted components) to keep the system compilable. ALL such proxy methods MUST be explicitly marked with `@deprecated` annotations (specifically via `warnings.warn` or `typing_extensions.deprecated`). **MyPy Strict Re-Export Enforcement**: In Python proxy files, all re-exported symbols (classes, functions, types) MUST be explicitly re-exported to satisfy PEP 484 and `mypy --strict`. Implicit re-exports (`from new_domain import ExtractedClass`) are STRICTLY BANNED because they trigger `implicit re-export` / `[attr-defined]` errors in CI/CD quality gates. You MUST mandate explicit re-exports using `__all__ = ["ExtractedClass", ...]` AND/OR redundant aliases (`from new_domain import ExtractedClass as ExtractedClass`). Do NOT plan massive dummy "Facade" files that live forever; preserve the immediate routing contract ONLY during the transition phase. You MUST explicitly plan the final deletion of this proxy file ONLY AFTER completing consumer migration, Tier 2 hardening, Zero-Reference static verification, and the pre-flight Global Integration & DI Boot Test. Premature deletion of the proxy file before the E2E and DI container boot tests pass is STRICTLY PROHIBITED.</mandatory_pattern>
      <catastrophic_reason>Refactoring massive files in one go leads to context truncation, severe LLM amnesia, and irreversible system corruption. Deleting the proxy file before passing the global E2E and DI boot test destroys the Strangler Fig safety net, causing unrecoverable compile errors. Using implicit imports without explicit re-exports (`__all__` / `as Symbol`) crashes MyPy Strict quality gates across the codebase during the transition phase. Conversely, failing to eventually delete the proxy methods leaves the God File as an eternal "Hollow Shell," confusing developers and permanently preserving technical debt.</catastrophic_reason>
    </rule_block>
    <rule_block id="test_coverage_prerequisite">
      <mandatory_pattern>Before any extraction plans are written, the target God File MUST have at least 75% test coverage. If coverage is below 75%, do NOT stop entirely. Instead, you MUST generate a "Phase 0: Coverage Bootstrap Plan". This plan will define black-box Characterization Tests (Golden Master tests) for the God file to lock in its current behavior. This Phase 0 plan must be added to the Tracker as a strict blocker that Tier 2 must execute and verify (reaching 75% coverage) before any actual code extraction begins.</mandatory_pattern>
      <catastrophic_reason>Decomposing a massive, untested file is blind surgery. Without 75% coverage, business logic will be silently destroyed. However, halting completely leaves the user stuck. Using Characterization Tests safely scaffolds the legacy code before surgery.</catastrophic_reason>
    </rule_block>
    <rule_block id="zero_behavioral_change_mandate">
      <mandatory_pattern>Decomposition is strictly a STRUCTURAL reorganization. You MUST NOT add new features, fix existing logical bugs, or "optimize" algorithms during decomposition. The ultimate goal of the Zero-Loss Parity Audit is to mathematically prove that the ORIGINAL FUNCTIONALITY remains exactly identical after the file has been reorganized. Test cases must be preserved, not just to keep the count high, but to guarantee zero behavioral change.</mandatory_pattern>
      <catastrophic_reason>Mixing functional changes (features/bugfixes) with structural changes (decomposition) destroys the ability to isolate regressions. If a test fails after refactoring, you won't know if the new logic is wrong or if the structural wire-up failed.</catastrophic_reason>
    </rule_block>
    <rule_block id="ssot_decomposition_mandate">
      <mandatory_pattern>Decomposition is a strict exercise in codebase-wide SSOT consolidation. Your sub-plans MUST mandate:
      1. REPLACE: Delete inline logic entirely if it can be replaced by existing global utilities.
      2. ELEVATE: Design the extracted core logic immediately as a reusable Single Source of Truth (SSOT) component.
      3. UNIFY (CRITICAL): Perform a Pre-Flight Fragmentation Audit. Actively search the directory and broader codebase for standalone files sharing the same domain name (specifically: if extracting 'PromptBlock', check if 'prompt_block.py' already exists). If found, you MUST mandate merging the extracted logic into the existing SSOT file rather than creating duplicates.
      4. DIRECTORY STRUCTURE: The generated plans MUST enforce that extracted domain files are placed into a cleanly named subdirectory (specifically: `repositories/components/matrix.py`) rather than cluttering the parent directory with prefix-hacked filenames.
      5. FUTURE REUSE: Always strive for SSOT solutions by examining current code. Reuse old implementations where applicable, or intentionally design the extracted logic as new shared modules that can be utilized in the future.</mandatory_pattern>
      <catastrophic_reason>Refactoring in isolation creates "micro-monoliths". Failing to unify fragmented logic preserves technical debt and limits future reusability.</catastrophic_reason>
    </rule_block>
    <rule_block id="decomposition_fidelity_mandate">
      <mandatory_pattern>Your execution plans MUST explicitly mandate the mathematical verification of security hooks, orphaned code, and Dependency Injection (DI) graphs:
      1. SECURITY PARITY: You MUST instruct the executing agent to mechanically verify that every authorization hook (specifically: `_enforce_tenant_isolation`) present in the original God Code survived the transplant into the decomposed files.
      2. ORPHANED FIXTURE CLEANUP: When splitting tests, explicitly mandate the removal of unused legacy fixtures or mocks, as orphaned fixtures drag down the mandatory 100% test coverage.
      3. DI RE-WIRING: Explicitly mandate updating the central Dependency Injection graph (specifically: `dependencies.py` or Flutter Providers) to point to the new domain `__init__.py` export boundaries.</mandatory_pattern>
      <catastrophic_reason>Copy-pasting logic during decomposition often drops critical tenant isolation security checks, silently opening the system to cross-tenant data leaks. Un-wired DI dependencies crash the system at runtime.</catastrophic_reason>
    </rule_block>
    <rule_block id="enum_and_literal_centralization">
      <mandatory_pattern>Before any domain extraction begins, the planner MUST evaluate the God file for hardcoded `Literal[...]` type annotations. If found, the planner MUST mandate a "Pre-Extraction Enum Centralization" phase. All closed-set `Literal` types MUST be converted to centralized Enum classes (specifically in `models/enums.py`) and updated in-place in the God file FIRST. This prevents circular dependency and type resolution nightmares during the physical file split.</mandatory_pattern>
      <catastrophic_reason>Extracting models with hardcoded inline literals scatters domain concepts. Trying to centralize them *during* extraction causes massive git conflicts and makes the Zero Behavioral Change audit impossible to isolate.</catastrophic_reason>
    </rule_block>
    <rule_block id="model_rebuild_and_deferred_import_handling">
      <mandatory_pattern>The planner MUST explicitly search for bottom-of-file `model_rebuild()` calls (Pydantic) or deferred imports used for circular dependency resolution inside the God file. The generated plans MUST explicitly dictate exactly where these `model_rebuild()` calls will be relocated (specifically to the bottom of the newly extracted files or a higher-level view module) and ensure the correct import order is preserved.</mandatory_pattern>
      <catastrophic_reason>Blindly moving Pydantic models without relocating their `model_rebuild()` calls leaves the extracted models permanently incomplete, instantly crashing FastAPI startup with `PydanticUndefinedAnnotation`.</catastrophic_reason>
    </rule_block>
    <rule_block id="circular_dependency_prevention">
      <mandatory_pattern>Before any business logic is moved, you MUST mandate a "Pre-Extraction" phase for shared types. All shared types, interfaces, DTO models, and constants must be extracted into explicitly named, domain-specific files strictly following the architecture (specifically: `models/domain/[domain]_types.py` or `models/dtos/[feature]_dto.py`). You MUST NOT create generic "garbage drawer" files named `types.py`, `models.py`, or `utils.py` in root directories. The newly extracted domain files MUST NEVER import the original God File. Instead, both the God File and the new domain files must import shared dependencies from these new domain-specific type files to prevent Circular Import crashes.</mandatory_pattern>
      <catastrophic_reason>If a newly extracted domain file imports a type from the God File, and the God File imports the domain file to proxy its logic (Strangler Fig), a strict Python circular import is created, crashing the application instantly. However, extracting them into a generic `types.py` creates a Garbage Drawer anti-pattern, spawning a new type monolith.</catastrophic_reason>
    </rule_block>
    <rule_block id="state_and_transaction_audit">
      <mandatory_pattern>The planner MUST explicitly map database session lifecycles and any shared runtime state within the God file. The generated implementation plans MUST specify exactly how session objects (or database connections) are injected (Dependency Injection) into the newly extracted modules. If the God File executed operations under a single atomic transaction, the extracted domain logic MUST accept the existing session as a parameter rather than creating new independent sessions.</mandatory_pattern>
      <catastrophic_reason>Splintering a single God File transaction into multiple independent domain transactions destroys database atomicity. If one domain succeeds and the next fails, partial commits will irreparably corrupt the system data state.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_abstraction_mandate">
      <banned_pattern>Abstracting, summarizing, or generalizing explicit details from the original God Code file using lazy placeholders.</banned_pattern>
      <mandatory_pattern>You MUST NOT act as a lossy compression algorithm. You MUST extract and VERBATIM preserve exact variable names, method signatures, ErrorCodes, and numbered algorithmic steps from the original God Code file directly into the generated XML extraction plans.</mandatory_pattern>
      <catastrophic_reason>Abstracting details forces the executing agent to guess or hallucinate during extraction, breaking structural parity.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command (`/tier5-resume`), a tracker file (`task.md`), an implementation plan, or instructions for the user, you MUST explicitly wrap all target file paths in `@-reference` syntax (specifically: `@[backend_v2\target.py]`). ORIGINAL BOUNDARY PRESERVATION: If you are extracting a specific block from the God Code, you MUST append specific line bounds using `#Lnn-mm` syntax (specifically: `@[file.py#L830-L841]`) to precisely target the extraction zone. DYNAMIC RULES INJECTION: You MUST explicitly list the global core rule (`@[.agents\rules\00-antigravity-core.md]`), ANY relevant Knowledge Items (KIs), PLUS the domain-specific rule file for the phase inside a `<required_context_rules>` block in EVERY generated plan and tracker.</mandatory_pattern>
      <catastrophic_reason>Failing to use `@-references` with precise line bounds forces the next AI session to blindly search for context, wasting tokens, and causing severe Context Amnesia or incorrect logic extraction.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_item_preflight">
      <banned_pattern>Creating multiple structurally identical extracted files without first establishing a canonical reference template in the Knowledge Base.</banned_pattern>
      <mandatory_pattern>During Step 2 (Pre-flight), the planner MUST evaluate whether the decomposition produces a REPEATING STRUCTURAL PATTERN (3+ extracted files sharing identical structure). If so, the planner MUST search existing KIs and either reference an existing KI or CREATE a new KI with a canonical reference template, locked terminology, and anti-patterns list BEFORE generating extraction plans.</mandatory_pattern>
      <catastrophic_reason>Without a pre-execution canonical KI, each extraction phase's executing agent independently interprets structural requirements, causing terminology drift and inconsistent file structures across the decomposed modules.</catastrophic_reason>
    </rule_block>
    <rule_block id="test_contract_specification">
      <banned_pattern>Writing vague test instructions like "write unit tests" or "ensure coverage" in generated extraction plans without specifying exact test names, inputs, and expected outputs.</banned_pattern>
      <mandatory_pattern>Every generated extraction plan MUST include a `<test_contracts>` XML block containing concrete, named test specifications. Each test contract MUST define: 1) test name following `test_{method}_{scenario}_{expected}` convention, 2) input fixture, 3) expected output or exception, 4) category (positive/negative/boundary/error_path). For every positive test, at least 2 negative/boundary tests MUST be specified. Since God Code decomposition requires zero behavioral change, test contracts MUST include `regression` category tests that lock the EXACT current output of each extracted method.</mandatory_pattern>
      <catastrophic_reason>God Code decomposition without explicit test contracts makes it impossible to verify zero behavioral change. The executing agent writes superficial tests that pass but fail to detect subtle logic drift introduced during extraction.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
  </context_rules>
  <execution_protocol level="3">
    <step id="1" name="GREETING &amp; INSTRUCTIONS">
      <action>Your VERY FIRST response to the user must print a brief summary of the Tier 3 God Code Planner instructions to the screen.</action>
      <action>Explain that you are acting purely as a Planner, generating Tracker and implementation plans using the Strangler Fig approach, and delegating execution to Tier 2.</action>
    </step>
    
    <step id="2" name="PHASE 1 (Pre-flight &amp; Baseline Validation)">
      <action name="CONTEXT AMNESIA PREVENTION">Do NOT read the massive target file entirely in one go. You MUST use `grep_search` with regex (specifically: `^(class|def|async def) `) to extract structural outlines, or use `view_file` with strict `StartLine` and `EndLine` constraints to read the file in small, safe chunks (max 300 lines at a time).</action>
      <action>If invoked to plan later phases, you MUST actively search for and read the existing Tracker file to understand which phases are completed and which remain.</action>
      <gate name="TEST BASELINE">You MUST first find the corresponding test file for the target domain file. Then, run the tests using explicit native commands (specifically: `uv run pytest <path_to_test_file> --cov=<path_to_domain_file>` for Python, or `uv run python scripts/flutter_audit_loop.py <target_path> --test` for Flutter) to establish a baseline. Do NOT use naked `pytest`, `python -m unittest`, or run `pytest` directly against the domain file. If the baseline fails, STOP. Record the exact number of passing tests and coverage percentage in the Tracker file as a `[BASELINE]` metric.</gate>
      <fallback trigger="coverage is below 75%">Immediately plan a `phase0_coverage_bootstrap.md` task focused on Characterization Tests.</fallback>
      <action>Document the target DDD bounded contexts and generate an Exhaustive Symbol Inventory artifact saved to `docs\epic\tasks_[filename]\symbol_migration_map.md` (mapping every class/function to its future location).</action>
      <action name="BLAST RADIUS &amp; 1-HOP DEPENDENCY MAPPING">Identify all external dependencies, consumers, and 1-hop callers of the God Class (via `grep_search`) to map the blast radius and establish the full touched scope.</action>
      <action name="TOUCHED SCOPE TECH DEBT INVENTORY">While analyzing the target God File AND its immediate 1-hop callers, actively inspect both the target and 1-hop dependencies against the complete 7-item technical debt checklist:
        1. Python Backend (Duck Typing &amp; Reflection): Search for `getattr()`, `hasattr()`, and `isinstance(x, dict)`.
        2. Python Backend (Fallbacks &amp; Dicts): Search for `.get("key", default)`, `or "default"`, and raw dictionary parsing instead of strict Pydantic V2 DTOs.
        3. Python Backend (Error Handling): Search for bare or silent `except Exception:` blocks missing `AppException` re-raises or RFC 7807 structured dual-logging.
        4. Python Backend (Immutability &amp; Validation): Search for unvalidated `model_copy(update=...)`, missing `@model_validator` decorators, and hardcoded `Literal[...]` types (must be centralized in `enums.py`).
        5. Python Backend (Configuration &amp; Concurrency): Search for hardcoded magic numbers, timeouts, or model strings (must reside in `settings.py`), and `asyncio.gather` (must use `asyncio.TaskGroup`).
        6. Flutter Frontend (UI &amp; Localization): Search for hardcoded strings (missing `.arb` localization), hardcoded hex colors (`Color(0x...)`), manual string clippings (`substring(...)`), and missing `AppErrorBoundary` or `AsyncValue` guards.
        7. ISTQB Testing (Partitions &amp; Fixtures): Search for missing negative ISTQB partitions (boundary values, error paths) and legacy dictionary test fixtures (must use `polyfactory`).
        Do NOT plan to fix these during the initial structural extraction phases (to preserve Zero Behavioral Change). Instead, compile them into an itemized Tech Debt Inventory for resolution during the Tier 2 Hardening phase.</action>
    </step>
    
    <step id="3" name="PHASE 2 (Micro-Chunking &amp; Lazy Plan Generation)">
      <action>Break the decomposition down into multiple `phaseX_[domain]_extraction.md` plans inside a new `docs\epic\tasks_[filename]\` directory. Create ONE plan per domain. This transforms the extraction into a continuous execution loop.</action>
      <constraint name="CRITICAL LIMIT">To prevent LLM cognitive overload, if there are more than 3 extraction phases, you MUST ONLY generate detailed plans for Phase 1 and Phase 2. For Phase 3 and beyond, just create empty placeholder files or title headers in the tracker.</constraint>
      <constraint name="HYBRID_XML_SANDWICH_MANDATE">You MUST require that generated `phaseX_extraction.md` files wrap their step-by-step instructions in `<execution_protocol>` XML blocks inside fenced ```xml ``` codeblocks, exactly matching the format produced by `tier0-create-plan`.</constraint>
      <action>Add an explicit `[NOK]` task in the tracker after Phase 2 instructing the executing agent: "Invoke the Tier 3 Planner again to generate detailed plans for the remaining phases based on the updated codebase state."</action>
      <action>Ensure the Strangler Fig mapping (including test mock updates and DI shadow fixes) is detailed in the generated plans.</action>
      <action>You MUST inject a `<required_context_rules>` XML block into every generated plan containing the `@-references` to the core rules and domain-specific rules required to execute it.</action>
      <action name="EXTRACTED_FILE_TRACKER_REGISTRATION">ALL planned extracted target files MUST be explicitly registered as indented file-level child checkboxes under the `Tier 2 Hardening` task in the master decomposition tracker (specifically: `  - [ ] @[relative/path.py]`). The Tier 3 Planner MUST NOT write to `tmp/hardening_state.json`; the runtime JSON state file is initialized and managed exclusively during the Tier 2 Hardening execution phase.</action>
      <action name="TEST CONTRACT GENERATION">For every generated extraction plan, you MUST include a `<test_contracts>` XML block specifying exact regression tests that lock the current output of each extracted method. These contracts ensure the executing agent can mathematically prove zero behavioral change after extraction.</action>
      <action name="KI PREFLIGHT CHECK">If the decomposition produces 3+ structurally identical files, you MUST create or reference a canonical KI template BEFORE generating the extraction plans. Inject a `<constraint invariant="knowledge_item_preflight">` tag into every extraction plan that creates a file following this pattern.</action>
      <action name="SELF HEALING BOUNDARY AUDIT">After creating the `phaseX_extraction.md` plans, you MUST physically run the boundaries audit script on each generated plan: `uv run python scripts/audit_markdown_boundaries.py --file <path_to_plan>`. If it fails, you MUST correct the plan and re-run. CIRCUIT BREAKER: If the script still fails after 3 repair attempts, STOP immediately and ask the user for manual intervention. Do NOT loop indefinitely.</action>
    </step>
    
    <step id="4" name="PHASE 3 (Tracker Generation)">
      <action>Create a master tracker file at `docs\epic\[filename]_decomposition_tracker.md`. You MUST inject a `<required_context_rules>` XML block at the top of this tracker. If a Phase 0 coverage plan was created, list it as the VERY FIRST `[NOK]` task and explicitly state it is a strict blocker.</action>
      <action>List every generated extraction sub-plan as a `[NOK]` task.</action>
      <action>You MUST save the 'Exhaustive Symbol Inventory' into a dedicated `docs\epic\tasks_[filename]\symbol_migration_map.md` artifact rather than embedding it into the tracker. Then, append a specific `[NOK]` task called "Proxy Sunset & Consumer Migration" which explicitly @-references this separate migration map file (`@[docs\epic\tasks_[filename]\symbol_migration_map.md]`) so the Tier 2 agent loads it on-demand without saturating the tracker's context window.</action>
      <action name="DECOMPOSITION PIPELINE">After 'Proxy Sunset &amp; Consumer Migration', you MUST add a mandatory `[NOK]` task named 'Tier 2 Hardening' to the Tracker file. You MUST explicitly list every item from your Tech Debt Inventory (covering both the target God File and all touched 1-hop callers) as sub-tasks, AND list all newly planned extracted files along with all touched 1-hop caller files as indented child checkboxes (specifically: `  - [ ] @[relative/path.py]`) under this Hardening task in accordance with `ki_deterministic_hardening_state.md`. This ensures the executing agent has an exhaustive, deterministic list of files to harden once extraction is complete.</action>
      <gate name="PRE_DELETE_ZERO_REFERENCE_AND_SEMANTIC_COVERAGE">After 'Tier 2 Hardening', append a `[NOK]` task for 'Pre-Delete Zero-Reference &amp; Semantic Coverage Audit'. This task MUST instruct the agent to: 1) Run `grep_search` across the entire codebase (excluding the proxy file itself) to mathematically prove 0 remaining imports of the legacy God Code file, and 2) Verify line coverage of the *surviving business logic* remains >90%, and all old fallback tests have been cleanly replaced by strict Pydantic V2 boundary tests.</gate>
      <gate name="PRE_FLIGHT_GLOBAL_INTEGRATION_AND_DI_AUDIT">Append a mandatory `[NOK]` task for 'Pre-Flight Global Integration &amp; DI Boot Test'. This task MUST be executed WHILE THE PROXY FILE IS STILL INTACT on disk. Instruct the executing agent to run the global `backend_audit_loop.py` or `flutter_audit_loop.py` (with `--test`) to ensure the entire application compiles, all Dependency Injection containers (specifically: FastAPI `dependencies.py` or Flutter providers) wire correctly, and integration tests pass 100% green without mock interference. If the application fails to boot, the agent MUST resolve the broken export boundaries or DI bindings before proceeding.</gate>
      <action name="SAFE_PHYSICAL_PROXY_DELETION">ONLY AFTER both the Zero-Reference check and Pre-Flight Global Integration &amp; DI Boot Test have passed 100% green, append a `[NOK]` task for 'Physical Proxy Deletion' (completely DELETING the original God Code proxy file from disk). It is STRICTLY FORBIDDEN to leave the temporary proxy file alive permanently.</action>
      <gate name="POST_DELETE_REGRESSION_GATE">Append a final `[NOK]` task for 'Post-Delete Regression Smoke Test'. This task MUST instruct the executing agent to run an immediate fast audit and boot check (`uv run python backend_v2/seed/run_seed.py local` and `uv run python scripts/backend_audit_loop.py <target_path> --test`) to mathematically prove that the physical absence of the proxy file caused zero runtime regressions or hidden import failures.</gate>
    </step>
    
    <step id="5" name="PHASE 4 (Embedded Handover Context)">
      <action>Append a `# Session Handover Context` section at the VERY END of the tracker file itself. Write out exhaustive summaries for: Achieved, Learned, and Remaining.</action>
      <constraint>Do NOT pass these as long CLI parameters.</constraint>
      <action>Provide a concise `/tier5-resume` command for the next session. The command MUST explicitly delegate execution to the Tier 2 workflow (`--workflow=/tier2-execute`). You MUST ONLY target the tracker file (`--target="docs\epic\[filename]_decomposition_tracker.md"`). Do NOT include the massive `[original_god_code_file]` in the target parameter. The Tier 2 agent will load the file safely via the line-bounded `@-references` contained within the extraction plans. Do NOT include a `--rules` parameter; rules are now self-hydrating directly from the `<required_context_rules>` blocks in the plans and tracker.</action>
      <action>You MUST explicitly wrap all target file paths in `@-reference` syntax.</action>
      <constraint name="MANDATORY_STOP">Ensure the instructions strictly reinforce that the agent MUST stop and instruct the user to execute the plans in a fresh context window using the `/tier5-resume --workflow=/tier2-execute` command.</constraint>
    </step>
    
    <step id="6" name="PHASE 5 (Stop &amp; Present)">
      <action>Present the generated plans and tracker to the user.</action>
      <action>Inform the user that planning is complete and they MUST STOP and instruct the user to execute the plans in a fresh context window using the `/tier5-resume --workflow=/tier2-execute` command.</action>
      <constraint>Do NOT implement any domain code yourself in this session.</constraint>
    </step>
  </execution_protocol>
</system_prompt>
```
