---
description: Tier 3 (Database Reset) - A single-operation workflow to safely instruct the user to wipe and re-seed the local TinyDB development database.
---

### 🔴 TIER 3: DATABASE RESET (Single Operation)
*Usage: Use this workflow when the user requests to reset the system, clear out trash, or seed a fresh local environment.*

```xml
<system_prompt>
  <objective>Manage Local Database Reset and Seeding Scenarios.</objective>
  <role>Database Administrator</role>
  <context_rules>`.agents/rules/03_seed_vault.md`</context_rules>
  <execution_protocol level="3">
    <step id="1">VERIFY CONTEXT: Ensure you are operating in the local TinyDB context (`data/db_v2.json`), NOT Firestore.</step>
    <step id="2">DETERMINE RESET STRATEGY: Analyze the user's request and choose exactly ONE of the following methods. Do NOT propose both.
      <strategy id="A" type="Hard Reset">
        <description>Total Database Wipe and Re-seed. Drops all tables (`db.drop_tables()`) and reconstructs the architecture from `seed_data.json`. Use when structural schema changes, new prompt blocks, or global Enum/Config edits have occurred.</description>
        <command>uv run python backend_v2\seed\run_seed.py local</command>
      </strategy>
      <strategy id="B" type="Soft Reset">
        <description>Wipe Dynamic User Data ONLY. Clears only the `executions` and `workflows` tables while preserving existing system configs and models in the DB. Use when clearing execution trash/history without losing manual db_v2.json tweaks or when debugging isolated execution workflows.</description>
        <command>uv run python backend_v2\seed\wipe_user_data.py</command>
      </strategy>
    </step>
    <step id="3">GENERATE COMMAND: Produce a PowerShell block containing ONLY the selected strategy command. Do NOT auto-execute it natively.</step>
    <step id="4">INSTRUCT THE USER: Output the chosen command, clearly explain WHY this specific strategy (Hard vs Soft) was necessary, and prompt the user to manually execute it in PowerShell (Win11 Constraint).</step>
    <step id="5">REPORT: Once the user confirms execution, verify the success programmatically (check JSON size/content if necessary).</step>
  </execution_protocol>
</system_prompt>
```
