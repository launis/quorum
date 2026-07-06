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

    <rule_block id="local_data_ephemeral_nature">
         <banned_pattern>Hesitating to wipe `db_v2.json` or running `run_seed.py` out of fear of losing customer data. Also, attempting to update `db_v2.json` manually on the fly.</banned_pattern>
         <mandatory_pattern>This is purely a local testing environment with zero real customer data. Always prioritize architectural purity and wipe/re-seed the local database via `uv run python backend_v2/seed/run_seed.py local` whenever corrupted states arise. NEVER update `db_v2.json` directly.</mandatory_pattern>
         <catastrophic_reason>Editing the runtime `db_v2.json` creates a fork between local state and the schema. The next `run_seed.py` execution will ruthlessly overwrite it anyway, causing lost work.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<vault_mutation_protocol>
    <instruction>If requested to alter any data schemas, seed matrices, or internal configurations, you MUST run this sequential procedure:</instruction>
    
    <step id="1_propose">PROPOSE: Render the intended JSON snippet delta in the chat and PAUSE. Wait for the explicit order "PERMISSION GRANTED".</step>
    <step id="2_modify">MODIFY: Commit structural edits safely into the file `backend_v2/seed/seed_data.json` using your structural editing tools (replace_file_content). Do NOT create standalone python scripts for this.</step>
    <step id="2.5_syntax_check">JSON INTEGRITY CHECK: Immediately after executing `replace_file_content`, you MUST verify the JSON syntax by invoking a dry-run read of the file, ensuring no trailing commas or broken braces were introduced.</step>
    <step id="3_backup">BACKUP: Store a precise timestamped backup copy inside `backend_v2/seed/backups/` using a native IDE tool (e.g., executing a safe OS copy command via `run_command` using PowerShell `Copy-Item`).</step>
    <step id="4_verify">VERIFY (Critical Gate): Trigger the native `<universal_quality_gates>` backend command via `run_command` tool to mathematically verify blueprint integrity. If tests fail, YOU MUST revert.</step>
    <step id="5_report">REPORT: Describe specifically what paths aligned with expectations contextually.</step>
    <step id="6_reseed">RE-SEED: Once verified, command the ultimate final step to the user: `uv run python backend_v2/seed/run_seed.py local`.</step>
</vault_mutation_protocol>