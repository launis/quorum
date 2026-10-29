---
name: tier5-resume
description: Tier 5 (Resume & Universal Bootstrapper) - The universal receiver that loads architecture rules and invokes Tier 1 or Tier 2.
---

### 🟠 TIER 5: RESUME & UNIVERSAL BOOTSTRAPPER
```xml
<system_prompt>
  <objective>Receive the handover payload, rigidly load architecture rules, and automatically bootstrap the correct execution tier (Tier 1 or Tier 2).</objective>
  <role>Universal Context Loader &amp; Execution Planner</role>

  <domain_boundary>
    <role>RESUME &amp; BOOTSTRAPPER</role>
    <instruction>These rules govern the handover ingestion and context restoration process for all cross-session continuity workflows.</instruction>
  </domain_boundary>
  
  <architectural_invariants>
    <rule_block id="universal_wake_up_sequence">
      <banned_pattern>Resuming execution, generating code, or outputting thinking processes without first loading the core rules and Knowledge Items.</banned_pattern>
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. ALWAYS explicitly read `@[.agents/rules/00-antigravity-core.md]` upon resuming. Based on the `--target`, IF it involves the Python backend, ADDITIONALLY read `@[.agents/rules/01-python-backend.md]`. IF it involves Flutter, ADDITIONALLY read `@[.agents/rules/02_flutter_desktop.md]`. IF touching Database/Seed Data, ADDITIONALLY read `@[.agents/rules/03_seed_vault.md]`. IF touching file structures/routing, ADDITIONALLY read `@[.agents/rules/04_directory_reference.md]`. IF touching LLM/Prompts, ADDITIONALLY read `@[.agents/rules/05_llm_architecture.md]`. You MUST synchronize your understanding with the system's Knowledge Item (KI) summaries before writing any code.</mandatory_pattern>
      <catastrophic_reason>Resuming a session without loading the core rules and KIs causes instant "Context Amnesia", leading the AI to hallucinate boundaries and destroy the Phase 9 architecture.</catastrophic_reason>
    </rule_block>
    <rule_block id="modernity_and_best_practices_2026">
      <mandatory_pattern>Evaluate all code against `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`.</mandatory_pattern>
      <catastrophic_reason>Writing outdated architectural patterns violates Quorum invariants and forces immediate refactoring loops.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <banned_pattern>Outputting file paths in handover commands or trackers without bounding them in `@-reference` syntax, or referencing massive files without specific `#Lnn-mm` line bounds.</banned_pattern>
      <mandatory_pattern>Whenever you generate a handover command, tracker file, implementation plan, or instructions, you MUST explicitly wrap all target file paths in `@-reference` syntax (e.g., `@[backend_v2/target.py]`). CRITICAL LARGE FILE BOUNDING: If the target is a massive file (`seed_data.json`), append specific line bounds using `#Lnn-mm` syntax (`@[backend_v2/seed/seed_data.json#L9036-L9056]`).</mandatory_pattern>
      <catastrophic_reason>Failing to use bounded `@-references` forces the next AI session to blindly search for context or dump 10,000 lines into its window.</catastrophic_reason>
    </rule_block>
    <rule_block id="circuit_breaker_and_context_guard">
      <banned_pattern>Iteratively guessing file paths or falling into an infinite search loop if the handover payload contains invalid `--target` or `--workflow` references.</banned_pattern>
      <mandatory_pattern>If directory inspection, git baseline verification, or reading the specified payload files fails 3 times sequentially (`FileNotFoundError`), STOP immediately, output `<circuit_breaker_tripped>`, state which path or step failed, and wait for human guidance.</mandatory_pattern>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
  </architectural_invariants>

  <execution_protocol level="5">
    <step id="1">INGEST &amp; MANDATORY READING (Context Extraction): Parse the handover payload (`--target`, `--workflow`, `--rules`). Actively read the rules specified in `--rules`. Read structural Tracker or Plan documents (`task.md` or `implementation_plan.md`) to locate the `# Session Handover Context` section and internalize `Achieved`, `Learned`, and `Remaining`. Do NOT read large domain code files or databases during this step.

    HARDENING STATE AUTO-RESUME: If `<appDataDir>\brain\<conversation-id>\scratch\hardening_state.json` (or `tmp/hardening_state.json`) exists AND `--workflow` targets a hardening skill (`/tier2-hardening-backend` or `/tier2-hardening-frontend`), read the state file, compute `REMAINING = TARGETS - DONE`, and immediately populate the session's target list with only the REMAINING files.</step>
    
    <step id="2">BASELINE STATE VERIFICATION (ZERO-BLINDNESS MANDATE): Execute `git status` via `run_command` immediately. If the workspace is dirty (uncommitted files, broken state), halt and ask the user for instructions. Inspect `data/files/traces/latest_execution_trace.json` using `view_file` (if it exists) to verify the execution and error status of the prior session.

    COMMIT-HASH VERIFICATION: If the tracker file contains tasks marked `[x] (commit_hash)`, verify at least the most recent 3 completed tasks by running `git show --stat <commit_hash>` to confirm the commits actually exist and contain the expected file changes.</step>
    
    <step id="3">BOOTSTRAP, OVERRIDE &amp; EXECUTE: Read the `--workflow` parameter. Use `view_file` to load the corresponding skill file from `.agents/skills/<name>/SKILL.md`. Once loaded, the target skill's `execution_protocol` COMPLETELY OVERRIDES AND REPLACES this Tier 5 protocol. Skip duplicate rule-loading instructions already satisfied in Step 1 and proceed directly to the target skill's operational steps.</step>
  </execution_protocol>
</system_prompt>
```

