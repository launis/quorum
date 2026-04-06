---
description: Tier 3 (Database Reset) - A single-operation workflow to safely instruct the user to wipe and re-seed the local TinyDB development database.
---

### 🔴 TIER 3: DATABASE RESET (Single Operation)
*Usage: Use this workflow when the user requests to reset the system, clear out trash, or seed a fresh local environment.*

```xml
<system_prompt>
  <objective>Reset the Local Data Environment.</objective>
  <role>Database Administrator</role>
  <context_rules>`.agents/rules/03_seed_vault.md`</context_rules>
  <execution_protocol level="3">
    <step id="1">VERIFY CONTEXT: Ensure you are operating in the local TinyDB context (`data/db_v2.json`), NOT Firestore.</step>
    <step id="2">DATABASE WIPE: Generate a PowerShell block containing the command to wipe the database. Do NOT auto-execute.
   Command format: `uv run python backend_v2\seed\wipe_user_data.py`</step>
    <step id="3">DATABASE SEED: Generate a PowerShell block containing the command to re-seed the database. Do NOT auto-execute.
   Command format: `uv run python backend_v2\seed\run_seed.py local`</step>
    <step id="4">INSTRUCT THE USER: Output the commands and explicitly ask the user to run them in their PowerShell instance, fulfilling the CRITICAL WIN11 CONSTRAINTS.</step>
    <step id="5">REPORT: Once the user confirms execution, verify the success programmatically (check JSON size/content).</step>
  </execution_protocol>
</system_prompt>
```
