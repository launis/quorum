# ANTIGRAVITY AGENT CONFIGURATION & DIRECTIVES (V6.2)

<system_context>
    <os>Windows 11 (PowerShell)</os>
    <architecture>Quorum (Python Backend V2 + Flutter Client V2)</architecture>
</system_context>

<catastrophic_system_bans>
    <rule_block id="win11_run_command_crash_exceptions">
        <banned_pattern>Calling the `run_command` tool natively for arbitrary Linux commands, `&&` chains, or heavy build tools (like `flutter gen-l10n`).</banned_pattern>
        <mandatory_pattern>DELEGATE EXECUTION for arbitrary commands on Windows 11. EXCEPTION: You MUST use the `run_command` tool natively to run automated testing via the Universal Quality Gates (see below).</mandatory_pattern>
        <catastrophic_reason>General sandboxing and bash scripts fail on Windows 11 natively.</catastrophic_reason>
    </rule_block>

    <rule_block id="naked_python_execution_ban">
        <banned_pattern>Instructing the user to run `python`, `pytest`, or `pip install` nakedly (without `uv run`).</banned_pattern>
        <mandatory_pattern>ALWAYS prefix python tooling with `uv run ` (e.g. `uv run pytest`, `uv run python scripts/...`).</mandatory_pattern>
        <catastrophic_reason>Naked python execution targets the global Windows environment, missing local `.venv` dependencies and causing cascade module errors.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<agentic_control_center>
    <rule_block id="native_mcp_tooling">
         <banned_pattern>Instructing the user to run Python or shell scripts manually just to dump text or retrieve logs.</banned_pattern>
         <mandatory_pattern>ALWAYS use your built-in internal MCP tools (`view_file`, `grep_search`, `list_dir`, `replace_file_content`) to actively scan `backend_debug.log` and `client_debug.log` before proposing fixes.</mandatory_pattern>
    </rule_block>

    <rule_block id="context_triggered_loading">
        <banned_pattern>Writing domain-specific code (Python, Flutter, or Seed Data) without reading the strict architecture laws first.</banned_pattern>
        <mandatory_pattern>BEFORE writing backend or frontend code, you MUST dynamically read the relevant architecture laws using the `view_file` tool:
        1. If working on **Backend/Python**, you MUST read: `c:\src\quorum\.agents\rules\01-python-backend.md`
        2. If working on **Frontend/Flutter**, you MUST read: `c:\src\quorum\.agents\rules\02_flutter_desktop.md`
        3. If working on **Data/Seed/JSON**, you MUST read: `c:\src\quorum\.agents\rules\03_seed_vault.md`
        </mandatory_pattern>
        <catastrophic_reason>The Single Source of Truth architecture requires language-specific constraints to be loaded on-demand to preserve context and ensure extreme accuracy.</catastrophic_reason>
    </rule_block>
</agentic_control_center>

<universal_quality_gates>
    <instruction>You MUST strictly enforce automated audit testing via `run_command` after EVERY significant code mutation. Do NOT bypass these loops.</instruction>
    
    <gate id="backend_audit_loop">
        <trigger>Any modification to `.py` files in `backend_v2/`.</trigger>
        <command>uv run python scripts/backend_audit_loop.py <target_path> --test</command>
        <description>Runs Ruff formatting, MyPy strict typing, and Pytest coverage recursively.</description>
    </gate>
    
    <gate id="flutter_audit_loop">
        <trigger>Any modification to `.dart` files in `client_app_v2/`.</trigger>
        <command>uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> [--build]</command>
        <description>Runs Dart formatter and analyzer. Add `--build` ONLY if Freezed models or JSON structures were modified to regenerate `.g.dart` files.</description>
    </gate>
</universal_quality_gates>

<workflow_routing>
    <instruction>You MUST follow strict operation tiers relying on natively supported workflows in `c:\src\quorum\.agents\workflows\`. If a user uses a slash command, refer to the corresponding workflow file:</instruction>
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