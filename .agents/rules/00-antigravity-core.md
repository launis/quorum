# 🚀 ANTIGRAVITY COMMAND CENTER

<domain_boundary>
    <role>GLOBAL SYSTEM & META-COGNITION</role>
    <instruction>These rules govern the overarching IDE environment, interaction formatting, global artifacts, and Git protocols. They apply universally across all contexts, but do NOT override language-specific constraints (Python/Flutter) or Database Seed operations.</instruction>
</domain_boundary>

<ide_orchestration_protocol>
    <rule_block id="permission_granted_workflow">
        <banned_pattern>Auto-executing the next steps in a plan, generating multiple files simultaneously, or rushing tasks without waiting.</banned_pattern>
        <mandatory_pattern>You MUST STOP after completing a single step in a plan. Do NOT proceed until the user explicitly says "PERMISSION GRANTED" or "PROCEED".</mandatory_pattern>
    </rule_block>
    <rule_block id="strict_execution_mode_mandate">
        <banned_pattern>Starting to execute an approved `implementation_plan.md` automatically or without switching to an explicit execution workflow setup.</banned_pattern>
        <mandatory_pattern>You MUST NEVER write domain code to execute an implementation plan without the user explicitly providing a slash command like `/tier2-execute` or `/tier2-hardening-backend`. Force the user to invoke the required execution workflow tier to bind safety constraints before execution starts.</mandatory_pattern>
    </rule_block>
    <rule_block id="slash_command_routing">
        <banned_pattern>Guessing the behavior of a slash command or answering a slash command with conversational filler.</banned_pattern>
        <mandatory_pattern>When a user inputs a slash command (e.g. `/tier2-execute`), your IMMEDIATE action must be to use the `view_file` tool on the corresponding workflow file in `.agents/workflows/` and strictly adopt its system prompt and execution protocol.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_apology">
        <banned_pattern>Outputting apologies, conversational filler, or subjective justifications after violating a rule (e.g., "I apologize for the oversight", "You are correct").</banned_pattern>
        <mandatory_pattern>When correcting a mistake based on user feedback, do not apologize or use conversational filler. You MUST first output your required `<thinking_process>` block detailing the root cause of the error, and then immediately output the corrected code. If the erroneous code was already committed, instruct the user to amend the commit.</mandatory_pattern>
        <catastrophic_reason>Conversational filler consumes tokens, dilutes the architectural context window, and slows down automated workflows.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_hallucination_read">
        <banned_pattern>Guessing the contents of a file.</banned_pattern>
        <mandatory_pattern>Actively use tools to read the current context before proposing modifications.</mandatory_pattern>
    </rule_block>
    <rule_block id="english_language_mandate">
        <banned_pattern>Writing code comments, docstrings, variable names, or git commit messages in Finnish or any language other than English.</banned_pattern>
        <mandatory_pattern>You MUST write ALL code-level artifacts (variables, functions, classes, docstrings, inline comments, and git commit messages) EXCLUSIVELY in English. Even if the user communicates in Finnish, the codebase MUST remain strictly English.</mandatory_pattern>
        <catastrophic_reason>Mixing languages in the codebase destroys readability for international developers, violates standard conventions, and breaks automated code analysis tools.</catastrophic_reason>
    </rule_block>
    <rule_block id="documentation_present_tense_mandate">
        <banned_pattern>Writing historical context, describing what was done in the past, or mentioning things like "Epic XX brought this..." in code comments or docstrings.</banned_pattern>
        <mandatory_pattern>When documenting code (docstrings, comments), always write in the present tense describing the CURRENT state and functionality. NEVER write about the history of the code or past iterations. A comment must only explain what the code does NOW.</mandatory_pattern>
    </rule_block>
    <rule_block id="ssot_reuse_mandate">
        <banned_pattern>Writing new components without analyzing reusability, building a new SSOT without migrating existing code, OR forcing "False Unifications" across decoupled domains.</banned_pattern>
        <mandatory_pattern>1. INVESTIGATE: Identify code that can be abstracted into an SSOT. 2. MIGRATE: Refactor legacy code to use the new SSOT immediately. 3. MITIGATE BIG-BANG: Legacy migration must be strictly timeboxed to "wiring the pipes"; do NOT rewrite the legacy internal business rules during migration. 4. MITIGATE FALSE UNIFICATION: Ensure unified code actually shares the same business domain, not just coincidental structural similarity.</mandatory_pattern>
        <catastrophic_reason>Failing to migrate old code creates parallel systems. Conversely, forcing "False Unifications" creates brittle dependencies, and uncontrolled "Big Bang" refactoring stalls business value delivery indefinitely.</catastrophic_reason>
    </rule_block>
    <rule_block id="explicit_scope_write">
        <banned_pattern>Modifying CONTEXT files.</banned_pattern>
        <mandatory_pattern>Only modify TARGET files. Treat CONTEXT files as Read-Only.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_duplication">
        <banned_pattern>Appending new versions of code to the end of a file while leaving the old broken ones intact.</banned_pattern>
        <mandatory_pattern>Explicitly DELETE or OVERWRITE the old version when modifying a file.</mandatory_pattern>
    </rule_block>
    <rule_block id="atomic_checkpoint_mandate">
        <banned_pattern>Modifying multiple architectural domains (e.g., UI and Backend) concurrently without a save state, proposing `git add .`, or writing git commit messages in a language other than English.</banned_pattern>
        <mandatory_pattern>After ANY successful run of the `universal_quality_gate` audit script that passes, you MUST explicitly instruct the user to perform an atomic `git commit` BEFORE proceeding to the next file or logic block. Exception: If a structural refactor mathematically requires modifying a coupled set of files (e.g., extracting shared interfaces to break circular imports) before the system can compile, you are authorized to modify that specific batch of files concurrently BEFORE running the quality gate and instructing the atomic commit. You MUST ALWAYS specify exact relative file paths (e.g., `git add client_app_v2/[tiedosto]`). Git commit messages MUST ALWAYS be written in English.</mandatory_pattern>
        <catastrophic_reason>Failure to enforce atomic commits per-file/per-domain results in massive, un-rollbackable Git histories and makes identifying regression bugs mathematically impossible.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
        <banned_pattern>Silently persisting in the same chat session after executing multiple massive file reads (e.g., 3+ directories in Tier 2 Hardening) or complex refactors.</banned_pattern>
        <mandatory_pattern>You MUST proactively suggest that the user executes the `/tier5-session-handover` workflow to start a new context window if the conversation exceeds 10 task iterations, or you have modified more than 5 complex files. This prevents 'Context Amnesia' and protects strict architectural rule adherence.</mandatory_pattern>
    </rule_block>
    <rule_block id="read_before_think_lock">
        <banned_pattern>Outputting a `<thinking_process>`, making assumptions, or generating code before reading the context-specific architecture rules.</banned_pattern>
        <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file (e.g. `00-antigravity-core.md`). You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules.</mandatory_pattern>
        <catastrophic_reason>AI models are prone to "lazy confidence". Guessing rules by their filename without reading the contents leads to hallucinated architecture constraints and code regression.</catastrophic_reason>
    </rule_block>
    <rule_block id="mandatory_chain_of_thought">
        <banned_pattern>Outputting code blocks or executing file-write tools immediately after receiving a user prompt.</banned_pattern>
        <mandatory_pattern>You MUST wrap your architectural thinking inside `<thinking_process>` XML tags BEFORE writing any code. State: 1) Rules applied, 2) Root cause, 3) Execution plan.</mandatory_pattern>
    </rule_block>
    <rule_block id="surgical_precision_edits">
        <banned_pattern>Using lazy placeholders like `// ... rest of the file ...` when outputting code.</banned_pattern>
        <mandatory_pattern>You MUST be surgical. Truncation is an act of data destruction. Provide the ENTIRE compilable structural block or use precise search-and-replace tools. If `multi_replace_file_content` fails due to matching errors, you MUST fallback to `view_file` to verify the exact structural state, OR use a full file overwrite (`write_to_file`) to break the retry loop.</mandatory_pattern>
    </rule_block>
    <rule_block id="temporary_workspace_sandbox">
        <banned_pattern>Creating scratch scripts, temporary data dumps, or one-off debugging programs in the repository root, core architectural directories (`backend_v2`, `client_app_v2`), or the legacy `tmp\` folder.</banned_pattern>
        <mandatory_pattern>All temporary files, debugging scripts, and ad-hoc execution programs MUST be written to and executed EXCLUSIVELY from the system-injected artifact scratch directory (`<appDataDir>\brain\<conversation-id>/scratch/`).</mandatory_pattern>
        <catastrophic_reason>Using a hardcoded `tmp\` directory conflicts with the native IDE artifact system, causing lost execution traces and polluting the workspace state.</catastrophic_reason>
    </rule_block>
    <rule_block id="logfire_delegation_mandate">
        <banned_pattern>Attempting to debug LLM token anomalies, performance latency bottlenecks, or "hallucination" issues purely by guessing or asking the user to manually dump text logs.</banned_pattern>
        <mandatory_pattern>If the user reports an anomaly related to performance (slow routing), LLM token explosion, or AI hallucination, you MUST proactively investigate it using the local execution traces. Because Logfire's SDK is write-only, you MUST use `grep_search` on `backend_debug.log` using the specific Execution ID to fetch the JSON log traces into your context. IF the issue is an LLM hallucination or PromptBlock assembly error, you MUST proactively ask for the Execution ID and use `view_file` to read the local `data/files/executions/<execution_id>/llm_debug_prompts.md` file. Instruct the user to check the visual Logfire Cloud dashboard ONLY if the local trace files are insufficient.</mandatory_pattern>
    </rule_block>
    <rule_block id="forensic_execution_artifacts">
        <banned_pattern>Ignoring execution artifacts when debugging a complex run or trying to read the massive `execution_trace.json` blindly top-to-bottom.</banned_pattern>
        <mandatory_pattern>When the user provides an execution folder (e.g., `data/files/executions/exe_...`), you MUST utilize its artifacts strategically: 1) Use `view_file` on `llm_debug_prompts.md` to inspect the exact prompts and raw LLM responses that caused hallucinations or schema errors. 2) Use `view_file` on `frozen_context.json` to see the exact snapshot of data provided to the engine. 3) Because `execution_trace.json` is usually multiple megabytes, DO NOT try to read the whole file at once. Instead, use `grep_search` with specific keywords or write a Python script in the `scratch/` directory to parse and analyze it programmatically. 4) If a `report.pdf` or `inputs/` exist, they represent the final generated output and user inputs.</mandatory_pattern>
    </rule_block>
</ide_orchestration_protocol>

<catastrophic_system_bans>
    <rule_block id="feature_sovereignty_mandate">
        <banned_pattern>Autonomously deleting, bypassing, or deprecating existing cognitive features (e.g., specific XAI output extensions, metrics, or matrix metadata) simply to optimize latency, resolve token explosion errors, or to "clean up" the schema without explicit USER consent.</banned_pattern>
        <mandatory_pattern>Performance optimizations MUST be structural (e.g., prompt refinement, architectural pipelining, synthesis delegation). If a performance issue requires dropping a functional feature or data field that the User expects in the UI or Database, you MUST STOP and explicitly ask for "PERMISSION GRANTED to deprecate feature X to solve Y".</mandatory_pattern>
        <catastrophic_reason>Agentic Drift. The AI risks prioritizing pure system stability over business value, silently amputating core platform capabilities under the guise of technical optimization.</catastrophic_reason>
    </rule_block>
    <rule_block id="the_zero_compromise_pledge">
        <banned_pattern>Implementing backwards compatibility, fallback chains ("if A is missing, try B"), shortcuts, language-level defaults (e.g., `v.get('field', '')`), or hardcoded patches. ANY use of `hasattr()`, `isinstance(data, dict)`, or recursive dictionary loops to guess missing data.</banned_pattern>
        <mandatory_pattern>You MUST enforce strict Pydantic V2/Freezed schemas. If an expected key is missing, you MUST raise an explicit `AppException` and CRASH. Zero Tolerance for silent bypasses.</mandatory_pattern>
        <catastrophic_reason>Masking data corruption with fallbacks destroys the deterministic Quorum engine and invalidates the forensic audit trail. (Rule enforced natively in English to prevent LLM attention dilution).</catastrophic_reason>
    </rule_block>
    <rule_block id="the_duct_tape_ban">
        <banned_pattern>Writing "duct-tape" code/logic, returning empty arrays `[]`, default dicts `{}`, or hiding UI elements `SizedBox.shrink()` when real data goes missing. Catching all errors with giant `try...except Exception:` blocks to prevent crashes.</banned_pattern>
        <mandatory_pattern>Fix the root cause instead of patching symptoms. If data is malformed, let the system CRASH loudly. Extract deep mutation loops into pure, isolated, testable functions.</mandatory_pattern>
        <catastrophic_reason>Silent fallbacks mask deeper architectural failures and corrupt state management.</catastrophic_reason>
    </rule_block>
    <rule_block id="zero_service_layer_fallbacks">
        <banned_pattern>Using Python `.get(key, default)`, `getattr(obj, key, default)`, or `if value is None: value = default` inside the Service or Controller layers to patch missing configuration.</banned_pattern>
        <mandatory_pattern>Domain definitions MUST be strictly typed utilizing Enum overrides and Pydantic `@model_validator`s. Services MUST crash Fail-Fast if the Domain Model does not provide a guaranteed value natively. NEVER use raw dictionaries for state transit (`no_naked_dicts_in_state`).</mandatory_pattern>
        <catastrophic_reason>Injecting "magic defaults" deeply in the controller/service logic bypasses the Pydantic/Dart structural audits, leading to untraceable shadow-states when the database or LLM behaves anomalously.</catastrophic_reason>
    </rule_block>
    <rule_block id="the_no_legacy_mandate">
        <banned_pattern>Writing code that maintains "backwards compatibility" with old V1 structures, deprecated APIs, or legacy databases. ANY form of fallback logic designed to catch missing or old data structures.</banned_pattern>
        <mandatory_pattern>Legacy support is STRICTLY PROHIBITED. If data is missing or malformed, the system MUST Fail-Fast. Obsolete code, fallback chains, and legacy test fixtures MUST be ruthlessly deleted.</mandatory_pattern>
        <catastrophic_reason>Preserving legacy fallbacks pollutes the V2 architecture with dead code pathways, bypasses strictness, and silently corrupts new data pipelines with deprecated logic.</catastrophic_reason>
    </rule_block>
    <rule_block id="database_schema_hallucination">
        <banned_pattern>Autonomously migrating relational SSOT arrays (like `output_profiles`) into embedded nested structures inside other objects (like `workflows`) within `seed_data.json` based on assumptions about Pydantic attributes.</banned_pattern>
        <mandatory_pattern>The SSOT structure in `seed_data.json` is immutable architectural law. Backend Pydantic models may define nested types (e.g., `EmbeddedOutputProfile`) for API responses or dynamic stitching (e.g., in `studio.py`), but you MUST NEVER physically alter the root persistence arrays in the `seed_data.json` SSOT to match these API shapes without an explicit roadmap mandate.</mandatory_pattern>
        <catastrophic_reason>Forcing dynamic API structures into static persistence layers breaks Single Source of Truth integrity, crashes Frontend UIs relying on global collections, and causes cascading data corruption across the system.</catastrophic_reason>
    </rule_block>
    <rule_block id="dependency_hallucination_firewall">
        <banned_pattern>Autonomously proposing new third-party packages to `pubspec.yaml` or `uv.lock`.</banned_pattern>
        <mandatory_pattern>Zero-Trust dependency environment. Solve problems using natively installed tools. If an external library is mathematically necessary, wait for "PERMISSION GRANTED".</mandatory_pattern>
    </rule_block>
    <rule_block id="windows_powershell_mandate">
        <banned_pattern>Using Unix/Linux terminal commands like `rm`, `ls`, `cat`, `grep`, or `sed` when executing terminal commands or providing command examples to the user.</banned_pattern>
        <mandatory_pattern>You MUST exclusively use native Windows 11 PowerShell commands (e.g., `Remove-Item` or `del` instead of `rm`, `Get-ChildItem` instead of `ls`). You are operating in a strict Windows PowerShell environment.</mandatory_pattern>
        <catastrophic_reason>Unix commands rely on unreliable PowerShell aliases that cause unpredictable behavior, or they fail entirely. Relying on Unix habits in a Windows ecosystem breaks automated scripts and corrupts file encodings.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="strict_variable_preservation">
        <banned_pattern>Arbitrarily renaming variables, DTO fields, or DB properties (e.g., changing `synthesis_md` to `synthesized_markdown`) without explicit user permission just to "clean things up".</banned_pattern>
        <mandatory_pattern>Respect and maintain the exact existing variable nomenclature across all boundaries unless an explicit schema refactoring is actively underway.</mandatory_pattern>
    </rule_block>
    <rule_block id="universal_fail_fast">
        <banned_pattern>Allowing invalid data to pass silently through the system boundaries, or fixing corrupted JSON visually in the UI.</banned_pattern>
        <mandatory_pattern>Enforce "Fail-Fast" at every boundary. If data does not precisely match the Pydantic V2 or Dart 3 Freezed schema, the system MUST crash audibly and visibly (`AppException` or `AppErrorBoundary`).</mandatory_pattern>
        <catastrophic_reason>If bad data is allowed to render, the user will eventually save it back to the database, permanently persisting the corrupted state into the SSOT.</catastrophic_reason>
    </rule_block>
    <rule_block id="rfc7807_dual_reporting_mandate">
        <banned_pattern>Crashing the system via `AppException` or `AppErrorBoundary` without simultaneously logging a deterministic, structured error trace.</banned_pattern>
        <mandatory_pattern>You MUST implement the Dual-Reporting pattern (RFC 7807). Every `AppException` thrown MUST be preceded by a structured `logger.error` containing the exact mathematical/logical reason for the failure and contextual parameters.</mandatory_pattern>
        <catastrophic_reason>Crashing without a structured trace creates opaque "black box" failures that cannot be audited in Logfire or forensic debugging sessions.</catastrophic_reason>
    </rule_block>
    <rule_block id="output_format_requirements">
        <banned_pattern>Writing prompt responses or code in language other than English, or explaining WHAT the code mechanically does in comments.</banned_pattern>
        <mandatory_pattern>Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish. Only comment WHY business logic exists using Imperative Mood.</mandatory_pattern>
    </rule_block>
    <rule_block id="mathematical_extrema_anchoring">
        <banned_pattern>Hardcoding min/max scale values (e.g., 1 to 5) or relying on assumed defaults when interpreting BARS or matrices.</banned_pattern>
        <mandatory_pattern>You MUST dynamically resolve absolute mathematical extrema by extracting the minimum and maximum `score` from the block's `scales` array. This MUST be implemented directly at the Domain Model layer (e.g., as `@property computed_min` and `computed_max` on the `PromptBlock` model) so that the exact same API payload seamlessly enforces absolute parity for both Frontend UI rendering and Backend LLM Context Mapping.</mandatory_pattern>
        <catastrophic_reason>Assuming static 1-5 scale bounds causes fatal LLM hallucinations ("pohjalukemissa" for 2.0/3) and logic blindness.</catastrophic_reason>
    </rule_block>
    <rule_block id="cross_language_mapping_mandate">
        <banned_pattern>Hardcoding "Finnish" as the only target language in system schemas, or writing LLM inference rules/prompts in the target language.</banned_pattern>
        <mandatory_pattern>LLM rules (Matrix scales, TDA Assertions, instructions) MUST ALWAYS be defined in English (the System Language). The LLM is then dynamically instructed to map these English rules against the Localized Target Language (e.g., Finnish) source documents. Always use generalized terms like "Localized Target Language" in schema descriptions instead of hardcoding a specific language.</mandatory_pattern>
    </rule_block>
    <rule_block id="sdui_contract_fracture_prevention">
        <banned_pattern>Modifying a Backend Python DTO (in `models/dtos/`) without synchronously updating the exact corresponding Frontend Dart/Freezed model (in `client_app_v2/.../models/`), or vice versa.</banned_pattern>
        <mandatory_pattern>Enforce Cross-Domain DTO Parity. The Backend and Frontend models are mathematically coupled via Server-Driven UI (SDUI). If you add, remove, or rename a field in a Python Pydantic model, you MUST immediately modify the corresponding Dart Freezed model in the Flutter codebase before declaring the task complete. Both MUST compile and pass their respective test gates (`backend_audit_loop.py` and `flutter_audit_loop.py`).</mandatory_pattern>
        <catastrophic_reason>Quorum enforces strict Fail-Fast parsing (`disallowUnrecognizedKeys` / `extra='forbid'`). Any mismatch between the API payload and the client parser instantly crashes the application with a "White Screen of Death" (Unrecognized Key error).</catastrophic_reason>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <rule_block id="quality_gate_delegation">
        <mandatory_pattern>Run the quality gate as defined in `AGENTS.md`.</mandatory_pattern>
    </rule_block>

    <rule_block id="zero_deprecation_mandate">
        <banned_pattern>Declaring a step complete when syntax errors or deprecation warnings (e.g., `deprecated_member_use`) exist.</banned_pattern>
        <mandatory_pattern>Proactively replace deprecated members. Resolve ALL syntax errors, typing errors, and warnings before completion.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="tdd_mandate">
        <banned_pattern>Fixing a bug or adding a feature without writing a test first.</banned_pattern>
        <mandatory_pattern>Write a failing test that reproduces the bug BEFORE fixing domain code. The code is not complete until a reliable test verifies the change.</mandatory_pattern>
    </rule_block>

    <rule_block id="anti_tdd_trap">
        <banned_pattern>Modifying Phase 9 modern domain code (e.g., reverting to dictionaries or removing strict types) just to make a failing legacy unit test pass.</banned_pattern>
        <mandatory_pattern>If a legacy test fails because it asserts outdated behavior (e.g., expecting a raw `dict` instead of a Pydantic V2 DTO, or relying on `asyncio.gather`), you MUST NOT patch the domain code to appease the test. Instead, you MUST ruthlessly rewrite or delete the legacy test to comply with the new Phase 9 architectural invariants.</mandatory_pattern>
        <catastrophic_reason>Prioritizing the survival of legacy tests over the enforcement of modern architecture creates a paradox where the AI intentionally corrupts the system to achieve "green tests".</catastrophic_reason>
    </rule_block>

    <rule_block id="mocking_mandate_for_llm">
        <banned_pattern>Executing direct HTTP calls to external LLM services or performing slow network requests during unit testing or CI/CD pipelines.</banned_pattern>
        <mandatory_pattern>Test Mandate Exception: When testing LLM interfaces or network operations, you MUST ABSOLUTELY use mocked JSON fixtures to mock the responses. You must utilize the global `backend_v2/llm/mock.py` and `mock_data.py` framework files when constructing Pytest fixtures. Live LLM calls during tests are strictly forbidden to prevent flaky, slow, and expensive test suites.</mandatory_pattern>
    </rule_block>

    <rule_block id="fragmented_quality_gates_prevention">
        <banned_pattern>Running ONLY localized test subsets (e.g., `pytest tests/unit/` or `flutter test test/feature/`) and immediately declaring the entire task a success ("Fake Green") without verifying the global integration state.</banned_pattern>
        <mandatory_pattern>You MUST enforce a Two-Stage Testing Pipeline to balance execution speed with global stability:
        1. **Development Stage**: When fixing a bug, run ONLY the specific isolated test (e.g., `uv run pytest path/to/test.py::test_name`) for speed and context efficiency.
        2. **Completion Gate Stage**: BEFORE declaring the task complete, you MUST run the GLOBAL audit loops (`backend_audit_loop.py` and `flutter_audit_loop.py`) or the ENTIRE test suite at least once.
        Testing only the directory you modified guarantees that cross-domain integrations will silently fail downstream.</mandatory_pattern>
        <catastrophic_reason>Running partial test suites hides regression failures in the CI/CD pipeline, leading to "Fake Green" commits that break the master branch. The Test Pyramid must be validated holistically.</catastrophic_reason>
    </rule_block>

    <rule_block id="circuit_breaker_protocol">
        <banned_pattern>Attempting to autonomously fix the exact same Pytest or Flutter error more than 3 times iteratively, or leaving the workspace in a broken state after failing.</banned_pattern>
        <mandatory_pattern>Implement the "Rule of Three". If failing 3 times, you MUST STOP. Output `<circuit_breaker_tripped>`, explicitly instruct the user to run `git restore .` to wipe the corrupted workspace state, explain the paradox, and WAIT for human guidance or handover.</mandatory_pattern>
    </rule_block>
    <rule_block id="deterministic_testing_delegation">
        <banned_pattern>Writing manual JSON dictionary mock data or claiming "Tests are complete" without passing Coverage.</banned_pattern>
        <mandatory_pattern>You are the worker, Python is the judge. 1) Use `polyfactory` for mock data. 2) The `conftest.py` blocks networks. 3) The `backend_audit_loop.py` enforces >90% coverage. Analyze the `Miss` column if it fails.</mandatory_pattern>
    </rule_block>
</universal_quality_gate>