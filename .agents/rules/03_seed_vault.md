# SEED DATA VAULT PROTOCOL

*** MANDATORY PROTOCOL FOR DATA & SYSTEM CONFIGURATION MUTATIONS ***

<catastrophic_system_bans>
    <rule_block id="live_database_mutation">
        <banned_pattern>Modifying the live development database (`db_v2.json` or `.db`) directly on the fly or bypassing safety nets.</banned_pattern>
        <mandatory_pattern>All structural data modifications MUST occur purely in the master source file `backend_v2/seed/seed_data.json` first before sync.</mandatory_pattern>
        <catastrophic_reason>Editing the runtime database bypasses compiler checks, corrupts Pydantic domain schemas, and permanently invalidates Opaque System IDs.</catastrophic_reason>
    </rule_block>

    <rule_block id="inline_terminal_scripting">
        <banned_pattern>Using one-liner inline terminal commands like `python -c` or `sed` to replace JSON strings dynamically.</banned_pattern>
        <mandatory_pattern>ALWAYS create dedicated temporary Python script files (e.g., `modify_seed.py`). Use `json.load()` and `json.dump()` to parse and save safely in-memory.</mandatory_pattern>
        <catastrophic_reason>PowerShell silently expands variable hashes like `$c1f...` inside strings, irreversibly destroying Stripe UUID string topologies.</catastrophic_reason>
    </rule_block>

    <rule_block id="hallucinated_data_keys">
        <banned_pattern>Inventing undocumented "extra keys", employing human-readable strings as IDs, or fabricating schema paths (e.g., `id: "new_matrix_1"`).</banned_pattern>
        <mandatory_pattern>Observe strict Pydantic configurations. All generated IDs MUST follow the Opaque ID System (Stripe Hash Pattern) rigorously.</mandatory_pattern>
        <catastrophic_reason>The API validator will immediately drop the hallucinated payload, causing 500 fatal errors upon application fetch operations.</catastrophic_reason>
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