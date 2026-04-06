# SEED DATA VAULT PROTOCOL

*** MANDATORY PROTOCOL FOR DATA & SYSTEM CONFIGURATION MUTATIONS ***

<catastrophic_system_bans>
    <rule_block id="live_database_mutation">
        <banned_pattern>Modifying the live development database (`db_v2.json` or `.db`) directly on the fly or bypassing safety nets.</banned_pattern>
        <mandatory_pattern>All structural data modifications MUST occur purely in the master source file `backend_v2/seed/seed_data.json` first before sync.</mandatory_pattern>
        <catastrophic_reason>Editing the runtime database bypasses compiler checks, corrupts Pydantic domain schemas, and permanently invalidates Opaque System IDs.</catastrophic_reason>
    </rule_block>

    <rule_block id="inline_terminal_scripting">
        <banned_pattern>Using one-liner terminal commands (`python -c`, `sed`) or PowerShell variable expansion to modify JSON data.</banned_pattern>
        <mandatory_pattern>ALWAYS create a dedicated `modify_seed.py` script. You MUST strictly use `json.load()` and `json.dump(..., indent=2)` to guarantee file structure integrity.</mandatory_pattern>
        <code_example>
            <anti_pattern>run_command("sed -i 's/old_id/new_id/g' backend_v2/seed/seed_data.json")</anti_pattern>
            <pro_pattern>
                # modify_seed.py
                import json
                with open('backend_v2/seed/seed_data.json', 'r') as f: data = json.load(f)
                data['users'][0]['id'] = "usr_abc123"
                with open('backend_v2/seed/seed_data.json', 'w') as f: json.dump(data, f, indent=2)
            </pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="hallucinated_data_keys">
        <banned_pattern>Inventing extra JSON keys not strictly defined in Pydantic models, or using human-readable IDs like `id: "new_user_1"`.</banned_pattern>
        <mandatory_pattern>All generated IDs MUST strictly follow the Opaque Stripe ID pattern (e.g. `usr_x8f9a2b1`). No semantic strings allowed.</mandatory_pattern>
        <code_example>
            <anti_pattern>{ "id": "admin_user", "email": "test@test.com" } # FATAL: Invalid ID</anti_pattern>
            <pro_pattern>{ "id": "usr_x8f9a2b1", "email": "test@test.com" } # STRICT ALIGNMENT</pro_pattern>
        </code_example>
    </rule_block>
</catastrophic_system_bans>

<vault_mutation_protocol>
    <instruction>If requested to alter any data schemas, seed matrices, or internal configurations, you MUST run this sequential procedure:</instruction>
    
    <step id="1_propose">PROPOSE: Render the intended JSON snippet delta in the chat and PAUSE. Wait for the explicit order "PERMISSION GRANTED".</step>
    <step id="2_modify">MODIFY: Commit structural edits safely into the file `backend_v2/seed/seed_data.json`.</step>
    <step id="3_backup">BACKUP: Store a precise timestamped backup copy inside `backend_v2/seed/backups/` natively.</step>
    <step id="4_script">SCRIPT: Formulate `modify_seed.py`. Parse the payload using `json.load()`, manipulate the dictionary, and output with `json.dump(indent=2)`.</step>
    <step id="5_execute">EXECUTE: Pass the `modify_seed.py` PowerShell command execution strings clearly to the user.</step>
    
    <universal_quality_gate>
        <step id="6_verify">VERIFY (Critical Gate): Mathematically verify the new blueprint integrity by providing the user the validation command: `uv run pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v`. If the test fails, YOU MUST revert.</step>
    </universal_quality_gate>
    
    <step id="7_report">REPORT: Describe specifically what paths aligned with expectations contextually.</step>
    <step id="8_reseed">RE-SEED: Once verified, command the ultimate final step: `uv run python backend_v2/seed/run_seed.py local`.</step>
</vault_mutation_protocol>