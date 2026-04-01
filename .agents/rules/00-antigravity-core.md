# 🚀 ANTIGRAVITY COMMAND CENTER

<ide_orchestration_protocol>
    <rule_block id="permission_granted_workflow">
        <banned_pattern>Auto-executing the next steps in a plan, generating multiple files simultaneously, or rushing tasks without waiting.</banned_pattern>
        <mandatory_pattern>You MUST STOP after completing a single step in a plan. Do NOT proceed until the user explicitly says "PERMISSION GRANTED" or "PROCEED".</mandatory_pattern>
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
</catastrophic_system_bans>

<architectural_invariants>
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
        <instruction>Python commands MUST ALWAYS use this format, list EXACT files, use `;`:</instruction>
        <command>`uv run ruff check backend_v2/[tiedostot] --fix ; uv run mypy backend_v2/[tiedostot] --strict`</command>
        <openapi_sync>If modifying Pydantic models or Router schemas: `uv run python backend_v2/scripts/generate_openapi.py`</openapi_sync>
        <test_mandate>`uv run pytest backend_v2/tests/ -v`</test_mandate>
    </backend_verification>
    
    <frontend_verification>
        <instruction>Flutter verification follows a strict order of native tools:</instruction>
        <step id="1">Clean & Analyze: `dart format . ; dart analyze`</step>
        <step id="2">Generators (If @riverpod or @freezed changed): `dart run build_runner build --delete-conflicting-outputs`</step>
        <step id="3">Localization (If .arb files changed): `flutter gen-l10n`</step>
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
        <mandatory_pattern>Test Mandate Exception: When testing LLM interfaces or network operations, you MUST ABSOLUTELY use mocked JSON fixtures to mock the responses. Live LLM calls during tests are strictly forbidden to prevent flaky, slow, and expensive test suites.</mandatory_pattern>
    </rule_block>
</universal_quality_gate>