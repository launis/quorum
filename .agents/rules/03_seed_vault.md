---
trigger: always_on
description: Safe Database Seeding Protocol and Mutation Strategies
globs: backend_v2/seed/**/*.json, backend_v2/seed/**/*.py
---

# SEED DATA VAULT PROTOCOL

> [!CAUTION]
<architecture_bans>
  <rule>**VERY IMPORTANT RULE:** The live development database (TinyDB) must NEVER be modified directly or on-the-fly (`db_v2.json` or `.db`). Modifying `backend_v2/seed/seed_data.json` autonomously is STRICTLY BLOCKED without a safety net. Bypassing these instructions corrupts the system IDs permanently.</rule>
</architecture_bans>

## 1. THE 8-STEP SEED MUTATION WORKFLOW
To prevent catastrophic ID corruption, you MUST follow these exact steps when instructed to alter system configurations or workflows:

1. **PROPOSE:** Show the exact JSON snippet you intend to modify in the chat. Wait for the user to reply with "PERMISSION GRANTED".
2. **MODIFY:** Once permitted, make the structural change FIRST in the master source file: `backend_v2/seed/seed_data.json`.
3. **BACKUP:** Always take a backup of the current state and save it to the `backend_v2/seed/backups/` directory before proposing major changes.
4. **SCRIPTING RULES (Mandatory):** Create a dedicated Python script file (e.g., `modify_seed.py`) to systematically update the JSON. 
<architecture_bans>
   <rule>NEVER use inline terminal commands (like `python -c` or `sed`) because PowerShell/Bash will silently expand variables like `$c1f...` and destroy the Stripe UUIDs.</rule>
   <rule>NEVER use raw string replacement or regex on the JSON file directly.</rule>
   <rule>ALWAYS use proper parsing: use `json.load()` to parse the dict, mutate the Python dictionary intelligently in-memory, and use `json.dump()` to save it.</rule>
   <rule>NEVER add undocumented "extra keys" or hallucinated data structures. Strictly observe Pydantic domain schemas.</rule>
   <rule>All new IDs MUST strictly follow the Opaque ID (Stripe Pattern) rule (see `Arkkitehtuuristandardi_Tietokannan_Tunnisteet.md`). Do not invent human-readable words in IDs.</rule>
</architecture_bans>
5. **EXECUTE:** Ask the user to run your script locally via PowerShell.
6. **VERIFY:** Run tests (e.g., `uv run pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v`) to mathematically verify the change. If the test fails, your mutation corrupted the graph. Fix your script and retry.
7. **REPORT:** Confirm to the user that the data delta matches expectations and that all tests passed.
8. **RE-SEED (Siemennys):** Only after all previous steps are confirmed, instruct the user to execute the final local database update and sync: `uv run python backend_v2/seed/run_seed.py local`.