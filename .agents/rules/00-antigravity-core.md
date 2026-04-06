# 🚀 ANTIGRAVITY COMMAND CENTER

<ide_orchestration_protocol>
    <rule_block id="permission_granted_workflow">
        <banned_pattern>Auto-executing the next steps in a plan, generating multiple files simultaneously, or rushing tasks without waiting.</banned_pattern>
        <mandatory_pattern>You MUST STOP after completing a single step in a plan. Do NOT proceed until the user explicitly says "PERMISSION GRANTED" or "PROCEED".</mandatory_pattern>
    </rule_block>
    <rule_block id="strict_execution_mode_mandate">
        <banned_pattern>Starting to execute an approved `implementation_plan.md` automatically or without switching to an explicit execution workflow setup.</banned_pattern>
        <mandatory_pattern>You MUST NEVER write domain code to execute an implementation plan without the user explicitly providing a slash command like `/tier2-execute` or `/tier2-hardening-backend`. Force the user to invoke the required execution workflow tier to bind safety constraints before execution starts.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_apology">
        <banned_pattern>Apologizing if you violate a rule.</banned_pattern>
        <mandatory_pattern>Acknowledge the error briefly and output the fixed code immediately.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_hallucination_read">
        <banned_pattern>Guessing the contents of a file.</banned_pattern>
        <mandatory_pattern>Actively use tools to read the current context before proposing modifications.</mandatory_pattern>
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
        <banned_pattern>Proceeding to the next architectural milestone without ensuring a save state, proposing `git add .` which captures unwanted state, or writing git commit messages in a language other than English.</banned_pattern>
        <mandatory_pattern>After a successful step, test, or `FIX` phase, you MUST explicitly instruct the user to perform an atomic `git commit` as a save point BEFORE asking for the `PROCEED` command. IMPORTANT: You MUST ALWAYS specify exact relative file paths starting from the workspace root (e.g., `git add client_app_v2/[tiedosto]`). NEVER output `git add .`. Git commit messages MUST ALWAYS be written in English (e.g., `git commit -m "feat: updated text payload"`).</mandatory_pattern>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
        <banned_pattern>Silently persisting in the same chat session after executing multiple massive file reads (e.g., 3+ directories in Tier 2 Hardening) or complex refactors.</banned_pattern>
        <mandatory_pattern>You MUST proactively suggest that the user starts a new context window to prevent 'Context Amnesia' and protect strict architectural rule adherence whenever the session gets uncomfortably heavy.</mandatory_pattern>
    </rule_block>
    <rule_block id="mandatory_chain_of_thought">
        <banned_pattern>Outputting code blocks or executing file-write tools immediately after receiving a user prompt.</banned_pattern>
        <mandatory_pattern>You MUST wrap your architectural thinking inside `<thinking_process>` XML tags BEFORE writing any code. State: 1) Rules applied, 2) Root cause, 3) Execution plan.</mandatory_pattern>
    </rule_block>
    <rule_block id="surgical_precision_edits">
        <banned_pattern>Using lazy placeholders like `// ... rest of the file ...` when outputting code.</banned_pattern>
        <mandatory_pattern>You MUST be surgical. Truncation is an act of data destruction. Provide the ENTIRE compilable structural block or use precise search-and-replace tools.</mandatory_pattern>
    </rule_block>
    <rule_block id="temporary_workspace_sandbox">
        <banned_pattern>Creating scratch scripts, temporary data dumps, or one-off debugging programs in the repository root or inside core architectural directories (`backend_v2`, `client_app_v2`).</banned_pattern>
        <mandatory_pattern>All temporary files, debugging scripts, and ad-hoc execution programs MUST be written to and executed from `c:\src\quorum\tmp\`. Treat `tmp\` as your exclusive scratchpad.</mandatory_pattern>
    </rule_block>
</ide_orchestration_protocol>

<catastrophic_system_bans>
    <rule_block id="the_duct_tape_ban">
        <banned_pattern>Writing "duct-tape" code (purkkakoodi), returning empty arrays `[]`, default dicts `{}`, or hiding UI elements `SizedBox.shrink()` when real data goes missing.</banned_pattern>
        <mandatory_pattern>Fix the root cause instead of patching symptoms.</mandatory_pattern>
        <catastrophic_reason>Silent fallbacks mask deeper architectural failures and corrupt state management.</catastrophic_reason>
    </rule_block>
    <rule_block id="the_no_legacy_mandate">
        <banned_pattern>Writing code that maintains "backwards compatibility" with old V1 structures, deprecated APIs, or legacy databases.</banned_pattern>
        <mandatory_pattern>Obsolete code must be ruthlessly deleted and replaced with modern V2 Architecture.</mandatory_pattern>
    </rule_block>
    <rule_block id="dependency_hallucination_firewall">
        <banned_pattern>Autonomously proposing new third-party packages to `pubspec.yaml` or `uv.lock`.</banned_pattern>
        <mandatory_pattern>Zero-Trust dependency environment. Solve problems using natively installed tools. If an external library is mathematically necessary, wait for "PERMISSION GRANTED".</mandatory_pattern>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="strict_variable_preservation">
        <banned_pattern>Arbitrarily renaming variables, DTO fields, or DB properties (e.g., changing `synthesis_md` to `synthesized_markdown`) without explicit user permission just to "clean things up".</banned_pattern>
        <mandatory_pattern>Respect and maintain the exact existing variable nomenclature across all boundaries unless an explicit schema refactoring is actively underway.</mandatory_pattern>
    </rule_block>
    <rule_block id="universal_fail_fast">
        <banned_pattern>Allowing invalid data to pass silently through the system boundaries.</banned_pattern>
        <mandatory_pattern>Enforce "Fail-Fast" at every boundary. If data does not precisely match the Pydantic V2 or Dart 3 Freezed schema, the system MUST crash audibly and visibly (`AppException` or `AppErrorBoundary`).</mandatory_pattern>
    </rule_block>
    <rule_block id="output_format_requirements">
        <banned_pattern>Writing prompt responses or code in language other than English, or explaining WHAT the code mechanically does in comments.</banned_pattern>
        <mandatory_pattern>Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish. Only comment WHY business logic exists using Imperative Mood.</mandatory_pattern>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <backend_verification>
        <instruction>Backend verification MUST utilize the unified audit loop script for safety and consistency.</instruction>
        <command>Execution: `uv run python scripts/backend_audit_loop.py backend_v2/[tiedostot]`</command>
        <command>Execution (If Pydantic or Routers changed): `uv run python scripts/backend_audit_loop.py backend_v2/[tiedostot] --openapi`</command>
        <test_mandate>Included directly: `uv run python scripts/backend_audit_loop.py backend_v2/[tiedostot] --test`</test_mandate>
    </backend_verification>
    
    <frontend_verification>
        <instruction>Flutter verification MUST follow a strict order of native tools natively mapped inside the core workspace. You must use the unified audit loop script for this process.</instruction>
        <command>Execution: `uv run python scripts/flutter_audit_loop.py client_app_v2`</command>
        <command>Execution (If @riverpod or @freezed changed): `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</command>
        <test_mandate>`flutter test`</test_mandate>
    </frontend_verification>

    <rule_block id="zero_deprecation_mandate">
        <banned_pattern>Declaring a step complete when syntax errors or deprecation warnings (e.g., `deprecated_member_use`) exist.</banned_pattern>
        <mandatory_pattern>Proactively replace deprecated members. Resolve ALL syntax errors, typing errors, and warnings before completion.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="tdd_mandate">
        <banned_pattern>Fixing a bug or adding a feature without writing a test first.</banned_pattern>
        <mandatory_pattern>Write a failing test that reproduces the bug BEFORE fixing domain code. The code is not complete until a reliable test verifies the change.</mandatory_pattern>
    </rule_block>

    <rule_block id="mocking_mandate_for_llm">
        <banned_pattern>Executing direct HTTP calls to external LLM services or performing slow network requests during unit testing or CI/CD pipelines.</banned_pattern>
        <mandatory_pattern>Test Mandate Exception: When testing LLM interfaces or network operations, you MUST ABSOLUTELY use mocked JSON fixtures to mock the responses. You must utilize the global `backend_v2/llm/mock.py` and `mock_data.py` framework files when constructing Pytest fixtures. Live LLM calls during tests are strictly forbidden to prevent flaky, slow, and expensive test suites.</mandatory_pattern>
    </rule_block>
    <rule_block id="circuit_breaker_protocol">
        <banned_pattern>Attempting to autonomously fix the exact same Pytest or Flutter error more than 3 times iteratively.</banned_pattern>
        <mandatory_pattern>Implement the "Rule of Three". If failing 3 times, you MUST STOP. Output `<circuit_breaker_tripped>`, explain the paradox, and WAIT for human guidance.</mandatory_pattern>
    </rule_block>
    <rule_block id="deterministic_testing_delegation">
        <banned_pattern>Writing manual JSON dictionary mock data or claiming "Tests are complete" without passing Coverage.</banned_pattern>
        <mandatory_pattern>You are the worker, Python is the judge. 1) Use `polyfactory` for mock data. 2) The `conftest.py` blocks networks. 3) The `backend_audit_loop.py` enforces >90% coverage. Analyze the `Miss` column if it fails.</mandatory_pattern>
    </rule_block>
</universal_quality_gate>