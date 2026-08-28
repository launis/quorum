# SEED DATA VAULT PROTOCOL

*** MANDATORY PROTOCOL FOR DATA & SYSTEM CONFIGURATION MUTATIONS ***

<domain_boundary>
    <role>STATIC STATE & DATA ONLY</role>
    <instruction>These rules apply STRICTLY to static data mutation, primarily `seed_data.json`. You are operating on the Database Layer. Do NOT apply Python logic rules here. If a schema constraint fails, modify the DATA to fit the Pydantic model, NEVER modify the Pydantic model to fit the data.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="live_database_mutation">
        <mandate>NEVER modify the live development database (`db_v2.json` or `.db`) directly on the fly or bypass safety nets. All structural data modifications MUST occur purely in the master source file `backend_v2/seed/seed_data.json` first before sync.</mandate>
    </rule_block>

    <rule_block id="inline_terminal_scripting">
        <mandate>NEVER use one-liner terminal commands (`python -c`, `sed`), PowerShell variable expansion, or disposable python scripts to modify JSON data. ALWAYS use native MCP structural editing tools (`multi_replace_file_content`) to surgically alter JSON structures.</mandate>
    </rule_block>

    <rule_block id="hallucinated_data_keys">
        <mandate>NEVER invent extra JSON keys not strictly defined in Pydantic models, or use human-readable IDs (`id: "new_user_1"`). All generated IDs MUST strictly follow the Opaque Stripe ID pattern (e.g. `usr_x8f9a2b1`, `blk_a1b2c3d4`). No semantic string slugs allowed.</mandate>
    </rule_block>

    <rule_block id="relational_slug_ban">
        <mandate>NEVER use a `slug` as a foreign key or relational identifier in `seed_data.json` (e.g., `"row_explanations_block_id": "blk_row_explanation_rules"`). A `slug` is strictly an informative metadata field; ALL relational bindings MUST use the exact opaque ID (e.g., `"row_explanations_block_id": "blk_ad303690b26b413d"`).</mandate>
    </rule_block>

    <rule_block id="matrix_slug_identification_ban">
        <mandate>NEVER use a `slug` to identify, filter, or find a matrix block in `seed_data.json` during data mutation scripts or queries. A matrix MUST ONLY be identified if it is located inside `prompt_blocks` array AND has `"category_id": "matrix"`.</mandate>
    </rule_block>

    <rule_block id="local_data_ephemeral_nature">
         <mandate>NEVER hesitate to wipe `db_v2.json` or update `db_v2.json` manually on the fly. This is purely a local testing environment; always prioritize architectural purity and wipe/re-seed the local database via `uv run python backend_v2/seed/run_seed.py local` whenever corrupted states arise.</mandate>
    </rule_block>

    <rule_block id="ai_context_amnesia_guard">
         <mandate>NEVER use `grep_search` on `seed_data.json` or read the entire file using `view_file` without explicit line bounds (Windows CRLF silently breaks grep). To search, verify, or interrogate, write and execute deterministic Python audit scripts via `run_command` (e.g., `uv run python audit_seed.py` reading via `json.load`). Bounded reads (`StartLine`/`EndLine`) are permitted ONLY after verifying exact line numbers via Python.</mandate>
    </rule_block>
</catastrophic_system_bans>

<vault_mutation_protocol>
    <instruction>If requested to alter any data schemas, seed matrices, or internal configurations, you MUST run this sequential procedure:</instruction>
    
    <step id="1_propose">PROPOSE: Generate an `implementation_plan.md` artifact showing the intended JSON snippet delta and set `RequestFeedback: true`. PAUSE execution and wait for the user to click the Proceed button in the IDE UI.</step>
    <step id="2_backup">BACKUP: Store a precise timestamped backup copy inside `backend_v2/seed/backups/` (automatically created by `sanitize_seed_vault.py` or manual copy) BEFORE making any modifications.</step>
    <step id="3_modify">MODIFY: Perform structural edits using `multi_replace_file_content` or automate large-scale ontological sanitization via `uv run python scripts/sanitize_seed_vault.py --reseed --test`. Formatter uses strict Pydantic V2 re-serialization and atomic temporary file replacement.</step>
    <step id="3.5_syntax_check">JSON INTEGRITY CHECK: Immediately after modification, verify JSON syntax and referential integrity via `uv run python scripts/audit_database_atoms.py --strict`. CIRCUIT BREAKER: If any verification gate fails, immediately restore the backup from step `2_backup` and STOP.</step>
    <step id="4_verify">VERIFY (Critical Gate): Run full quality gates via `uv run python scripts/backend_audit_loop.py backend_v2 --test` and Flutter domain parity tests (`uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart`). If tests fail, YOU MUST revert.</step>
    <step id="5_report">REPORT: Describe specifically what paths aligned with expectations contextually.</step>
    <step id="6_reseed">RE-SEED: Once verified, autonomously execute the final seeding command via `run_command`: `uv run python backend_v2/seed/run_seed.py local` (or append `--reseed` to `sanitize_seed_vault.py`).</step>
</vault_mutation_protocol>