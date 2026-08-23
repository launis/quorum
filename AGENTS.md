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

    <rule_block id="windows_powershell_syntax_mandate">
         <banned_pattern>Using Linux/bash syntax like `&&` to chain commands in PowerShell, or using Linux native commands like `ls`, `rm`, `cp`.</banned_pattern>
         <mandatory_pattern>You MUST exclusively use Windows PowerShell syntax. NEVER use `&&` (it fails in PowerShell 5.1). Use `;` to chain commands or execute them sequentially in separate tool calls. Remember the OS is Windows 11.</mandatory_pattern>
         <catastrophic_reason>Bash syntax like `&&` immediately throws ParserError in PowerShell, crashing the automated execution pipeline and breaking the IDE.</catastrophic_reason>
    </rule_block>

    <rule_block id="native_mcp_tooling">
         <banned_pattern>Instructing the user to run scripts manually, or attempting to use terminal commands like `cat`, `grep`, or `sed` inside PowerShell.</banned_pattern>
         <mandatory_pattern>ALWAYS prioritize native MCP tools. Use `view_file` to read, `grep_search` to find, and `multi_replace_file_content` to surgically edit files. NEVER use terminal text manipulation tools. If `multi_replace_file_content` fails due to matching errors, fallback to `view_file` to verify the exact code structure, OR use a full file overwrite (`write_to_file`) if necessary to avoid an infinite loop.</mandatory_pattern>
         <catastrophic_reason>Using terminal utilities like `sed` or `cat` on Windows PowerShell corrupts file encodings (UTF-16 vs UTF-8) and destroys the architectural audit trails.</catastrophic_reason>
    </rule_block>

    <rule_block id="prompt_preservation_mandate">
        <banned_pattern>Autonomously rewriting, simplifying, or "tightening" `system_prompt`, `ai_description`, or other natural-language text fields in `seed_data.json` to fix test failures or to enforce stricter JSON output schemas.</banned_pattern>
        <mandatory_pattern>The qualitative prompt texts in `seed_data.json` are the USER's intellectual property and represent deliberate coaching philosophy. If E2E parity tests or Pydantic validation fail due to LLM output shaped by these prompts, you MUST adjust the test assertions, the Pydantic schema tolerances, or the backend parsing logic. You MUST NEVER amputate the prompt text itself. You MUST request explicit "PERMISSION GRANTED to modify prompt text X" before touching any `system_prompt` or `ai_description` field.</mandatory_pattern>
        <catastrophic_reason>Repeated "Agentic Drift" has destroyed the Senior Executive Coach synthesis quality by roboticizing human-authored coaching prompts to satisfy automated test gates.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<agentic_control_center>
    <rule_block id="llm_psychological_biases">
        <banned_pattern>Falling into the "Path of Least Resistance" by hacking a solution (e.g. dict-parsing `execution_trace`) just to fix a crash quickly, prioritizing a green test suite over long-term architectural sovereignty.</banned_pattern>
        <mandatory_pattern>You MUST engage System 2 thinking when a test fails or the system crashes. 1. DO NOT prioritize acute firefighting over architectural rules. 2. RECOGNIZE context blindness (just because a trace is available doesn't mean it's the right CQRS layer to read). 3. REJECT the Anti-TDD trap (never write legacy dict-parsing just to make a test pass). 4. AVOID sidetracking the rules for convenience; if the right solution requires fixing state management or a database query, you MUST do it.</mandatory_pattern>
        <catastrophic_reason>Sacrificing architectural laws for immediate convenience accumulates catastrophic technical debt and guarantees brittle, unpredictable behavior (e.g., UI crashing because a nested dictionary structure changed).</catastrophic_reason>
    </rule_block>

    <rule_block id="knowledge_base_primacy">
        <banned_pattern>Starting complex coding tasks or diagnosing architecture bugs without reading provided Knowledge Item (KI) summaries or checking previous conversation Tracker contexts.</banned_pattern>
        <mandatory_pattern>BEFORE proposing architectural shifts, you MUST cross-reference the system-injected KI summaries. If continuing a previous session, you MUST prioritize reading the `# Session Handover Context` in the project Tracker file (e.g., `task.md` or `epic_tracker.md`) before falling back to `grep_search` on `.system_generated\logs\transcript.jsonl`.</mandatory_pattern>
        <catastrophic_reason>Ignoring the Knowledge Base leads to "Amnesia Programming". Scraping raw transcripts without checking Tracker handovers wastes context budget on truncated logs.</catastrophic_reason>
    </rule_block>

    <rule_block id="context_triggered_loading">
        <banned_pattern>Relying on context memory to assume the rules without physically reading them, or waiting until a task starts to read them.</banned_pattern>
        <mandatory_pattern>At the absolute beginning of EVERY new prompt or slash command, regardless of conversation history or previous context, you MUST treat it as a stateless reset. Your VERY FIRST tool call MUST be `view_file` to physically load the appropriate rule file into your current turn's active context window. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules.
        1. For **Global IDE & Orchestration**, you MUST read: `.agents/rules/00-antigravity-core.md`
        2. If working on **Backend/Python**, you MUST read: `.agents/rules/01-python-backend.md`
        3. If working on **Frontend/Flutter**, you MUST read: `.agents/rules/02_flutter_desktop.md`
        4. If working on **Data/Seed/JSON**, you MUST read: `.agents/rules/03_seed_vault.md`
        5. If working on **LLM or Prompts**, you MUST read: `.agents/rules/05_llm_architecture.md`
        6. If navigating or creating new files, you MUST read: `.agents/rules/04_directory_reference.md`
        
        **SELF-HYDRATING PLANS**: If the user provides a target tracker or plan file, you MUST load it concurrently on your first turn. On your second turn, extract its `<required_context_rules>` block and load all `@-referenced` files (`<rule>` for `.agents/rules/` and `<knowledge_item>` for Knowledge Items) before proceeding.
        </mandatory_pattern>
        <catastrophic_reason>The Single Source of Truth architecture requires language-specific constraints to be loaded on-demand. Without this absolute stateless reset, the LLM falls into "Context Bypass" mode and hallucinates old rules, causing system destruction.</catastrophic_reason>
    </rule_block>
</agentic_control_center>

<universal_quality_gates>
    <rule_block id="zero_tolerance_audit_loop">
        <banned_pattern>Skipping automated testing because a code change was "minor", "just a typo", or not "significant".</banned_pattern>
        <mandatory_pattern>You MUST strictly enforce automated audit testing via `run_command` after completing a cohesive logical step (e.g., finishing a complete function, file update, or task step). You are authorized to batch multiple related edits together before running the audit, but you MUST NEVER bypass the audit loop entirely once the logical step is done.</mandatory_pattern>
        <catastrophic_reason>Assuming a change is "too small to test" is the leading cause of massive cascading system outages. Fail-Fast requires mathematical proof, not assumptions.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="backend_audit_execution">
        <banned_pattern>Running generic pytest without the global audit script.</banned_pattern>
        <mandatory_pattern>If you modify `.py` files, you MUST run: `uv run python scripts/backend_audit_loop.py <target_path> --test`</mandatory_pattern>
        <catastrophic_reason>The audit loop enforces Ruff formatting and MyPy strict typing simultaneously with Pytest.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="flutter_audit_execution">
        <banned_pattern>Running basic flutter test without the audit script.</banned_pattern>
        <mandatory_pattern>If you modify `.dart` files, you MUST run: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build` (append --build when Freezed models need generation).</mandatory_pattern>
        <catastrophic_reason>The flutter audit script handles the build runner for Freezed models automatically if `--build` is appended.</catastrophic_reason>
    </rule_block>
</universal_quality_gates>

<workflow_routing>
    <instruction>You MUST follow strict operation tiers relying on natively supported workflows in `.agents/workflows/`. When a user inputs a slash command (e.g. `/tier0-create-plan`), this triggers a HARD CONTEXT RESET. Your absolute first tool calls MUST use `view_file` to physically load `.agents/rules/00-antigravity-core.md`, the requested `.agents/workflows/` file, AND any relevant domain-specific rule files (e.g., `.agents/rules/01-python-backend.md`). You are STRICTLY FORBIDDEN from calling any destructive tools (e.g., `replace_file_content`, `run_command`) in the same turn before these files are physically read and evaluated. Do not guess the workflow logic.</instruction>
    <execution_tiers>
        <tier id="0_create_epic" path="/tier0-create-epic">Generates a standardized multi-phase Epic document (docs/epic/EPIC_XXX.md).</tier>
        <tier id="0_plan" path="/tier0-create-plan">Generates architectural implementation plan.</tier>
        <tier id="0_epic" path="/tier0-research-epic">Deep System 2 analysis of Epic documents.</tier>
        <tier id="0_research" path="/tier0-research-plan">System 2 analysis of implementation plans.</tier>
        <tier id="1" path="/tier1-planner">Epic Planner for generating `implementation_plan.md`.</tier>
        <tier id="2" path="/tier2-execute">Systematic step-by-step implementation of an approved plan.</tier>
        <tier id="2_backend" path="/tier2-hardening-backend">Step-by-step auditing loop for Python architecture.</tier>
        <tier id="2_frontend" path="/tier2-hardening-frontend">Step-by-step auditing loop for Flutter architecture.</tier>
        <tier id="3_db" path="/tier3-database-reset">Database wipes and re-seeding tweaks.</tier>
        <tier id="3_refactor" path="/tier3-feature-refactor">Single feature implementation or existing file cleanup.</tier>
        <tier id="3_god" path="/tier3-god-code-decomposition">System 2 Decomposition Planner for Legacy Refactoring.</tier>
        <tier id="4" path="/tier4-bug-hunting">Deep root cause analysis and bug resolution.</tier>
        <tier id="5_handover" path="/tier5-session-handover">Session Handover Export for context transition.</tier>
        <tier id="5_resume" path="/tier5-resume">Resume & Zero-Shortcut Audit for new sessions.</tier>
        <tier id="6" path="/tier6-execution-monitor">Execution Monitor for real-time background log auditing.</tier>
        <tier id="7" path="/tier7-describe-architecture">As-Built architectural documentation from current codebase.</tier>
        <tier id="8_audit" path="/tier8-red-teaming-audit">System 2 deep-dive evaluation and red-teaming of rules and workflows.</tier>
        <tier id="8_audit_feature" path="/tier8-audit-feature">System 2 First Principles analysis, Panel of Experts audit, and red-teaming of proposed features.</tier>
        <tier id="8_audit_plan" path="/tier8-audit-plan">System 2 deep-dive evaluation and audit of a completed implementation plan.</tier>
        <tier id="8_audit_epic" path="/tier8-audit-epic">System 2 reverse verification of an Epic against the physical codebase.</tier>
        <tier id="8_test_expansion" path="/tier8-test-coverage-expansion">ISTQB-based iterative test coverage expansion for negative and edge-case tests.</tier>
    </execution_tiers>
</workflow_routing>