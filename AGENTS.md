# ANTIGRAVITY AGENT CONFIGURATION & DIRECTIVES (V6.3)

<system_context>
    <os>Windows 11 (PowerShell)</os>
    <architecture>Quorum (Python Backend V2 + Flutter Client V2)</architecture>
</system_context>

<domain_boundary>
    <role>SUPREME SYSTEM ROOT</role>
    <instruction>This is the root configuration. These rules possess supreme authority over all other files and workflows. You MUST obey these catastrophic bans before any other logic.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="async_background_execution_mandate">
        <banned_pattern>Refusing to run heavy build tools (like `flutter build` or `npm run`) out of fear of timeout, or waiting endlessly for a synchronous terminal response.</banned_pattern>
        <mandatory_pattern>You MUST leverage Antigravity 2.1.1's background task management for heavy commands. Set `WaitMsBeforeAsync` appropriately in `run_command` and use `manage_task` to check statuses. Remember that the OS is purely Windows 11 PowerShell; bash commands are PROHIBITED.</mandatory_pattern>
        <catastrophic_reason>Refusing to build or compile leaves the codebase unverified. Relying on bash (`&&`) or sync-blocking the LLM execution pipeline crashes the IDE workspace.</catastrophic_reason>
    </rule_block>

    <rule_block id="naked_python_execution_ban">
        <banned_pattern>Instructing the user to run `python`, `pytest`, or `pip install` nakedly (without `uv run`).</banned_pattern>
        <mandatory_pattern>ALWAYS prefix python tooling with `uv run ` (e.g. `uv run pytest`, `uv run python scripts/...`).</mandatory_pattern>
        <catastrophic_reason>Naked python execution targets the global Windows environment, missing local `.venv` dependencies and causing cascade module errors.</catastrophic_reason>
    </rule_block>

    <rule_block id="native_mcp_tooling">
         <banned_pattern>Instructing the user to run scripts manually, or attempting to use terminal commands like `cat`, `grep`, or `sed` inside PowerShell.</banned_pattern>
         <mandatory_pattern>ALWAYS prioritize native MCP tools. Use `view_file` to read, `grep_search` to find, and `multi_replace_file_content` to surgically edit files. NEVER use terminal text manipulation tools.</mandatory_pattern>
         <catastrophic_reason>Using terminal utilities like `sed` or `cat` on Windows PowerShell corrupts file encodings (UTF-16 vs UTF-8) and destroys the architectural audit trails.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<agentic_control_center>
    <rule_block id="knowledge_base_primacy">
        <banned_pattern>Starting complex coding tasks or diagnosing architecture bugs without reading provided Knowledge Item (KI) summaries or checking previous conversation transcripts.</banned_pattern>
        <mandatory_pattern>BEFORE proposing architectural shifts, you MUST cross-reference the system-injected KI summaries. If continuing a previous session, use `grep_search` on `.system_generated\logs\transcript.jsonl` to establish context.</mandatory_pattern>
        <catastrophic_reason>Ignoring the Knowledge Base leads to "Amnesia Programming", where the LLM repeats fixed bugs, overrides established patterns, and destroys multi-session Epic continuity.</catastrophic_reason>
    </rule_block>

    <rule_block id="context_triggered_loading">
        <banned_pattern>Writing domain-specific code (Python, Flutter, or Seed Data) without reading the strict architecture laws first.</banned_pattern>
        <mandatory_pattern>BEFORE writing any code or executing plans, you MUST dynamically read the relevant architecture laws using the `view_file` tool:
        1. For **Global IDE & Orchestration**, you MUST read: `c:\src\quorum\.agents\rules\00-antigravity-core.md`
        2. If working on **Backend/Python**, you MUST read: `c:\src\quorum\.agents\rules\01-python-backend.md`
        3. If working on **Frontend/Flutter**, you MUST read: `c:\src\quorum\.agents\rules\02_flutter_desktop.md`
        4. If working on **Data/Seed/JSON**, you MUST read: `c:\src\quorum\.agents\rules\03_seed_vault.md`
        5. If working on **LLM or Prompts**, you MUST read: `c:\src\quorum\.agents\rules\05_llm_architecture.md`
        6. If navigating or creating new files, you MUST read: `c:\src\quorum\.agents\rules\04_directory_reference.md`
        </mandatory_pattern>
        <catastrophic_reason>The Single Source of Truth architecture requires language-specific constraints to be loaded on-demand to preserve context and ensure extreme accuracy.</catastrophic_reason>
    </rule_block>
</agentic_control_center>

<universal_quality_gates>
    <rule_block id="zero_tolerance_audit_loop">
        <banned_pattern>Skipping automated testing because a code change was "minor", "just a typo", or not "significant".</banned_pattern>
        <mandatory_pattern>You MUST strictly enforce automated audit testing via `run_command` after EVERY SINGLE code mutation, no matter how small. Do NOT bypass these loops.</mandatory_pattern>
        <catastrophic_reason>Assuming a change is "too small to test" is the leading cause of massive cascading system outages. Fail-Fast requires mathematical proof, not assumptions.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="backend_audit_execution">
        <banned_pattern>Running generic pytest without the global audit script.</banned_pattern>
        <mandatory_pattern>If you modify `.py` files, you MUST run: `uv run python scripts/backend_audit_loop.py <target_path> --test`</mandatory_pattern>
        <catastrophic_reason>The audit loop enforces Ruff formatting and MyPy strict typing simultaneously with Pytest.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="flutter_audit_execution">
        <banned_pattern>Running basic flutter test without the audit script.</banned_pattern>
        <mandatory_pattern>If you modify `.dart` files, you MUST run: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> [--build]`</mandatory_pattern>
        <catastrophic_reason>The flutter audit script handles the build runner for Freezed models automatically if `--build` is appended.</catastrophic_reason>
    </rule_block>
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