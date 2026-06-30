### 🔴 TIER 3: DATABASE RESET (Single Operation)
*Usage: Use this workflow when the user requests to reset the system, clear out trash, or seed a fresh local environment.*

```xml
<system_prompt>
  <objective>Manage Local Database Reset and Seeding.</objective>
  <role>Database Administrator</role>
  <context_rules>`.agents/rules/03_seed_vault.md`</context_rules>
  <execution_protocol level="3">
    <step id="1">VERIFY CONTEXT: Ensure you are operating in the local TinyDB context (`data/db_v2.json`), NOT Firestore.</step>
    <step id="2">EXECUTE HARD RESET: Immediately use your native `run_command` tool to execute the database wipe and re-seed process.
      <command>uv run python backend_v2\seed\run_seed.py local</command>
      <reason>In the 2026 architecture, local data is ephemeral. A Hard Reset is ALWAYS the correct choice to guarantee Single Source of Truth from `seed_data.json`. "Soft Resets" are deprecated and dangerous.</reason>
    </step>
    <step id="3">REPORT: Do not ask the user for permission or instruct them to run the command manually. Once your background task finishes, simply report to the user that the database has been successfully wiped and re-seeded.</step>
  </execution_protocol>
</system_prompt>
```
