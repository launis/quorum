# SEED DATA VAULT PROTOCOL

*** MANDATORY PROTOCOL FOR DATA & SYSTEM CONFIGURATION MUTATIONS ***

<domain_boundary>
    <role>STATIC STATE & DATA ONLY</role>
    <instruction>These rules apply STRICTLY to static data mutation, primarily `seed_data.json`. You are operating on the Database Layer. Do NOT apply Python logic rules here. If a schema constraint fails, modify the DATA to fit the Pydantic model, NEVER modify the Pydantic model to fit the data.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="live_database_mutation">
        <banned_pattern>Modifying the live development database (`db_v2.json` or `.db`) directly on the fly or bypassing safety nets.</banned_pattern>
        <mandatory_pattern>All structural data modifications MUST occur purely in the master source file `backend_v2/seed/seed_data.json` first before sync.</mandatory_pattern>
        <catastrophic_reason>Editing the runtime database bypasses compiler checks, corrupts Pydantic domain schemas, and permanently invalidates Opaque System IDs.</catastrophic_reason>
    </rule_block>

    <rule_block id="inline_terminal_scripting">
        <banned_pattern>Using one-liner terminal commands (`python -c`, `sed`), PowerShell variable expansion, or writing disposable python scripts to modify JSON data.</banned_pattern>
        <mandatory_pattern>ALWAYS use your native MCP structural editing tools (`multi_replace_file_content`) to surgically alter JSON structures. Procedural data patching scripts are STRICTLY PROHIBITED.</mandatory_pattern>
        <catastrophic_reason>Ad-hoc terminal scripts bypass structural IDE logging, creating untraceable "ghost mutations" in the database that ruin the forensic audit trail.</catastrophic_reason>
    </rule_block>

    <rule_block id="hallucinated_data_keys">
        <banned_pattern>Inventing extra JSON keys not strictly defined in Pydantic models, or using human-readable IDs like `id: "new_user_1"`.</banned_pattern>
        <mandatory_pattern>All generated IDs MUST strictly follow the Opaque Stripe ID pattern (e.g. `usr_x8f9a2b1`, `blk_a1b2c3d4`). No semantic string slugs allowed.</mandatory_pattern>
        <catastrophic_reason>Human-readable slugs (like "admin") create ID collisions and break the Polymorphic Routing engine which mathematically depends on the exact 3-letter opaque prefix.</catastrophic_reason>
        <code_example>
            <anti_pattern>{ "id": "admin_user", "email": "test@test.com" } # FATAL: Invalid ID</anti_pattern>
            <pro_pattern>{ "id": "usr_x8f9a2b1", "email": "test@test.com" } # STRICT ALIGNMENT</pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="relational_slug_ban">
        <banned_pattern>Using a `slug` (e.g., `"slug": "blk_row_explanation_rules"`) as a foreign key or relational identifier in `seed_data.json` (e.g., `"row_explanations_block_id": "blk_row_explanation_rules"`).</banned_pattern>
        <mandatory_pattern>A `slug` is strictly an informative, human-readable metadata field and MUST NEVER be used as a relation. ALL relational bindings must use the exact opaque ID (e.g., `"row_explanations_block_id": "blk_ad303690b26b413d"`).</mandatory_pattern>
        <catastrophic_reason>Database queries strictly fetch by opaque ID. Using a slug as an ID causes silent `None` returns, severing critical logic paths and causing silent application failures.</catastrophic_reason>
    </rule_block>

    <rule_block id="local_data_ephemeral_nature">
         <banned_pattern>Hesitating to wipe `db_v2.json` or running `run_seed.py` out of fear of losing customer data. Also, attempting to update `db_v2.json` manually on the fly.</banned_pattern>
         <mandatory_pattern>This is purely a local testing environment with zero real customer data. Always prioritize architectural purity and wipe/re-seed the local database via `uv run python backend_v2/seed/run_seed.py local` whenever corrupted states arise. NEVER update `db_v2.json` directly.</mandatory_pattern>
         <catastrophic_reason>Editing the runtime `db_v2.json` creates a fork between local state and the schema. The next `run_seed.py` execution will ruthlessly overwrite it anyway, causing lost work.</catastrophic_reason>
    </rule_block>

    <rule_block id="ai_context_amnesia_guard">
         <banned_pattern>Reading the entire `seed_data.json` file using `view_file` without explicit line bounds.</banned_pattern>
         <mandatory_pattern>The `seed_data.json` is a massive file. You MUST use bounded reads (`StartLine`/`EndLine`) or run python search scripts (like `uv run python check_seed_data.py` or `uv run python backend_v2/seed/run_seed.py local --dry-run`) to interrogate the file without blowing out the context window.</mandatory_pattern>
         <catastrophic_reason>Reading a massive JSON file in a single operation overflows the LLM context window, causing immediate "Context Amnesia" and preventing coherent code generation in this session.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<vault_mutation_protocol>
    <instruction>If requested to alter any data schemas, seed matrices, or internal configurations, you MUST run this sequential procedure:</instruction>
    
    <step id="1_propose">PROPOSE: Generate an `implementation_plan.md` artifact showing the intended JSON snippet delta and set `RequestFeedback: true`. PAUSE execution and wait for the user to click the Proceed button in the IDE UI.</step>
    <step id="2_backup">BACKUP: Store a precise timestamped backup copy of the original file inside `backend_v2/seed/backups/` using `run_command` with PowerShell. You MUST ensure the backup directory exists first (e.g., `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_<timestamp>.json`). You MUST do this BEFORE making any modifications.</step>
    <step id="3_modify">MODIFY: Commit structural edits safely into the file `backend_v2/seed/seed_data.json` using your structural editing tools (`multi_replace_file_content`). You MUST use exact bounded line ranges. NEVER attempt to rewrite the entire file at once, as this causes catastrophic file truncation. Do NOT create standalone python scripts for this.</step>
    <step id="3.5_syntax_check">JSON INTEGRITY CHECK: Immediately after executing `multi_replace_file_content`, you MUST verify the JSON syntax by invoking a dry-run read of the file, ensuring no trailing commas or broken braces were introduced. CIRCUIT BREAKER: If the JSON syntax is broken, you MUST NOT attempt to fix it iteratively. You MUST immediately restore the backup from step `2_backup` and STOP.</step>
    <step id="4_verify">VERIFY (Critical Gate): Trigger the native backend audit script via `run_command` tool (`uv run python scripts/backend_audit_loop.py backend_v2 --test`) to mathematically verify blueprint integrity. If tests fail, YOU MUST revert.</step>
    <step id="5_report">REPORT: Describe specifically what paths aligned with expectations contextually.</step>
    <step id="6_reseed">RE-SEED: Once verified, you MUST autonomously execute the final seeding command via `run_command`: `uv run python backend_v2/seed/run_seed.py local`. NEVER ask the user to run this for you.</step>
</vault_mutation_protocol>