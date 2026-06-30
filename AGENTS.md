# ANTIGRAVITY AGENT CONFIGURATION & DIRECTIVES (V6.1)

<system_context>
    <os>Windows 11 (PowerShell)</os>
    <architecture>Quorum (Python Backend V2 + Flutter Client V2)</architecture>
</system_context>

<catastrophic_system_bans>
    <rule_block id="win11_run_command_crash_exceptions">
        <banned_pattern>Calling the `run_command` tool natively for arbitrary Linux commands, `&&` chains, or heavy build tools (like `flutter gen-l10n`).</banned_pattern>
        <mandatory_pattern>DELEGATE EXECUTION for arbitrary commands. EXCEPTION: You MUST use the `run_command` tool natively to run automated testing via `uv run python scripts/backend_audit_loop.py . --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2` after every significant change.</mandatory_pattern>
        <catastrophic_reason>While general sandboxing might fail on Windows 11, the automated Python audit loops MUST be run by the AI to guarantee Tier 2 constraints and Universal Quality Gates are met.</catastrophic_reason>
    </rule_block>

    <rule_block id="direct_database_mutation">
        <banned_pattern>Modifying the live `data\db_v2.json` database directly on the fly.</banned_pattern>
        <mandatory_pattern>If data must be altered, mutate `backend_v2\seed\seed_data.json` instead, verify locally, ask for USER CONFIRMATION, and use `backend_v2\seed\run_seed.py local`.</mandatory_pattern>
        <catastrophic_reason>Editing the runtime database bypasses the Pydantic fail-fast pipeline and corrupts Opaque Stripe ID relations permanently.</catastrophic_reason>
    </rule_block>

    <rule_block id="deprecated_commands_ban">
        <banned_pattern>Calling or proposing `flutter pub run`.</banned_pattern>
        <mandatory_pattern>ALWAYS use `dart run` instead.</mandatory_pattern>
        <catastrophic_reason>Deprecated tooling breaks the modern Flutter 3 pipeline and Quality Gate logic.</catastrophic_reason>
    </rule_block>

    <rule_block id="naked_python_execution_ban">
        <banned_pattern>Instructing the user to run `python`, `pytest`, or `pip install` nakedly (without `uv run`).</banned_pattern>
        <mandatory_pattern>ALWAYS prefix python tooling with `uv run ` (e.g. `uv run pytest`, `uv run python scripts/...`).</mandatory_pattern>
        <catastrophic_reason>Naked python execution targets the global Windows environment, missing local `.venv` dependencies and causing cascade module errors.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="core_architecture_parity">
         <banned_pattern>Implementing fallback logic, returning empty dicts `{}`, or hardcoding arbitrary UUIDs/UI strings.</banned_pattern>
         <mandatory_pattern>Enforce Fail-Fast Pydantic V2 definitions, Serverless Event Sourcing, and the Opaque Stripe ID Pattern. JSON Parsing done exclusively via Dart `Isolate.run()`.</mandatory_pattern>
    </rule_block>

    <rule_block id="native_mcp_tooling">
         <banned_pattern>Instructing the user to run Python or shell scripts manually just to dump text or retrieve logs.</banned_pattern>
         <mandatory_pattern>ALWAYS use your built-in internal MCP tools (`view_file`, `grep_search`, `list_dir`, `replace_file_content`) to actively scan `backend_debug.log` and `client_debug.log` before proposing fixes.</mandatory_pattern>
    </rule_block>
</architectural_invariants>

<agentic_control_center>
    <directive>Before writing backend or frontend code, you MUST dynamically read the relevant architecture laws from `c:\src\quorum\.agents\rules\` using your MCP tools.</directive>
    <required_scanners>
        <file id="06">c:\src\quorum\GEMINI.MD</file>
        <file id="00">c:\src\quorum\.agents\rules\00-antigravity-core.md</file>
        <file id="01">c:\src\quorum\.agents\rules\01-python-backend.md</file>
        <file id="02">c:\src\quorum\.agents\rules\02_flutter_desktop.md</file>
        <file id="03">c:\src\quorum\.agents\rules\03_seed_vault.md</file>
        <file id="04">c:\src\quorum\.agents\rules\04_directory_reference.md</file>
        <file id="05">c:\src\quorum\.agents\rules\05_llm_architecture.md</file>
    </required_scanners>
</agentic_control_center>

<workflow_routing>
    <instruction>You MUST follow strict operation tiers relying on natively supported workflows in `c:\src\quorum\.agents\workflows\`:</instruction>
    <execution_tiers>
        <tier id="1" path="/tier1-planner">Epic Planner for generating `implementation_plan.md`.</tier>
        <tier id="2" path="/tier2-execute">Systematic step-by-step implementation of an approved plan.</tier>
        <tier id="2_backend" path="/tier2-hardening-backend">Step-by-step auditing loop for Python architecture.</tier>
        <tier id="2_frontend" path="/tier2-hardening-frontend">Step-by-step auditing loop for Flutter architecture.</tier>
        <tier id="3_db" path="/tier3-database-reset">Database wipes and re-seeding tweaks.</tier>
        <tier id="3_refactor" path="/tier3-feature-refactor">Single feature implementation or existing file cleanup.</tier>
        <tier id="4" path="/tier4-bug-hunting">Deep root cause analysis and bug resolution.</tier>
        <tier id="5_handover" path="/handover">Session Handover Export for context transition.</tier>
        <tier id="5_resume" path="/tier5-resume">Resume & Zero-Shortcut Audit for new sessions.</tier>
        <tier id="6" path="/tier6-execution-monitor">Execution Monitor for real-time background log auditing.</tier>
        <tier id="7" path="/tier7-describe-architecture">As-Built architectural documentation from current codebase.</tier>
    </execution_tiers>
</workflow_routing>