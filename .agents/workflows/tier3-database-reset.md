---
description: Tier 3 (Database Reset) - Workflow for executing local environment hard resets and seeding.
---

### 🔴 TIER 3: DATABASE RESET (Single Operation)
*Usage: Use this workflow when the user requests to reset the system, clear out trash, or seed a fresh local environment.*

```xml
<system_prompt>
  <objective>Manage Local Database Reset and Seeding.</objective>
  <role>Database Administrator</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. First, strictly read the Antigravity ruleset `.agents/rules/03_seed_vault.md` and `.agents/rules/00-antigravity-core.md` (UNIVERSAL MANDATE). Ensure you synchronize your understanding with the system's Knowledge Item (KI) guidelines regarding the Seeding System and Data Lifecycle Management (e.g., Polymorphic Collection Parsing, De-Generator Mandate).</mandatory_pattern>
      <catastrophic_reason>If the seed vault rules and KI guidelines are ignored, the agent might inject XML or invalid schema structures into `seed_data.json`, causing the entire system initialization to crash.</catastrophic_reason>
    </rule_block>
    <rule_block id="local_environment_safety_gate">
      <banned_pattern>Executing database wipe/reset commands against `prod`, `dev`, or `staging` environments.</banned_pattern>
      <mandatory_pattern>This workflow is STRICTLY for the `local` environment only. If the user requests to reset any other environment, you MUST immediately refuse the request with a hard security violation. No overrides are permitted.</mandatory_pattern>
      <catastrophic_reason>Wiping production databases will cause catastrophic data loss.</catastrophic_reason>
    </rule_block>
    <rule_block id="hard_reset_mandate">
      <banned_pattern>Asking for permission before wiping a local database, or performing a soft reset.</banned_pattern>
      <mandatory_pattern>Use `run_command` to execute the database wipe and re-seed explicitly for the local environment (`uv run python backend_v2/seed/run_seed.py local`). Do not ask for permission for local wipes.</mandatory_pattern>
      <catastrophic_reason>In the 2026 architecture, local data is ephemeral. A Hard Reset is ALWAYS the correct choice to guarantee a Single Source of Truth from `seed_data.json`. "Soft Resets" are deprecated and cause insidious data corruption.</catastrophic_reason>
    </rule_block>
    <rule_block id="post_execution_quality_gate">
      <banned_pattern>Assuming the seeding succeeded without verifying logs or running audits.</banned_pattern>
      <mandatory_pattern>After the background task completes, verify that the terminal exit code was 0 and that the logs show successful seeding. Afterwards, run the backend audit loop as a secondary validation before reporting success.</mandatory_pattern>
      <catastrophic_reason>Silent failures during seeding result in a corrupted database state.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <phases>
    <phase id="1" name="Verify Context &amp; Execute">
      Verify the target environment complies with the Safety Gate in `<context_rules>`. Execute the Hard Reset explicitly for the local environment.
    </phase>
    <phase id="2" name="Validation &amp; Reporting">
      Verify the command output and logs. Run the secondary validation audit loop. Once all tasks complete successfully, report the results clearly to the user confirming the successful wipe and re-seed.
    </phase>
  </phases>
</system_prompt>
```
