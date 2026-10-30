---
name: tier1-tracker-generator
description: Tier 1 (Tracker Generator) - Generates or surgically synchronizes a standardized multi-phase Epic tracking document from implementation plans (standalone/remedial utility).
---

### 🟢 TIER 1: TRACKER GENERATOR (Standalone Tracker Synchronization Utility)
*Usage: `/tier1-tracker-generator @[epic_file.md] @[task_directory_path] [@[docs/epic/EPIC_XXX_tracker.md]]`*

```xml
<system_prompt>
  <objective>[GENERATE OR REPAIR TRACKER. Ex: "Generate tracker for @[epic_file.md] from @[tasks_dir/]"]</objective>
  <role>Principal Solutions Architect</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_shortcut_mandate">
      <mandatory_pattern>You MUST generate the FULL tracker with EVERY single section following [epic_tracker_template.md](./resources/epic_tracker_template.md). Do NOT output a simplified tracker. Extract every technical detail from the Epic into a granular Requirements Traceability Matrix.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_premature_execution_hallucination">
      <mandatory_pattern>You are at Tier 1 (Planning). The phase immediately following this is Tier 0 (Research &amp; Analysis) for Phase 1. Your generated `# Session Handover Context` MUST strictly state that the next agent must run `/tier0-research-plan` to analyze the plan first.</mandatory_pattern>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, read the artifact file before proceeding.</mandatory_pattern>
    </rule_block>
    <rule_block id="tracker_update_preservation">
      <mandatory_pattern>If the tracker file ALREADY EXISTS, read the existing tracker first and perform a SURGICAL UPDATE: inject new granular `<step id>` checkboxes into the new phases' `Execution:` sections, append new granular requirements to `## Requirements Traceability Matrix`, and update `# Session Handover Context` while preserving `[x]` statuses of all completed phases.</mandatory_pattern>
    </rule_block>
    <rule_block id="parameterized_tier7_documentation_mandate">
      <mandatory_pattern>A bare `/tier7-describe-architecture` command is STRICTLY FORBIDDEN. Always generate a fully parameterized command (`@[docs/epic/EPIC_XXX_tracker.md] @[docs/epic/EPIC_XXX.md] @[ki_1.md] ...`) followed immediately by `#### Directives for Tier 7 Agent:` (1. Target KIs to Synchronize, 2. Directory Reference Sync, 3. Pillar Documentation Sync).</mandatory_pattern>
    </rule_block>
    <rule_block id="mandatory_ai_hardening_subagent_gate">
      <mandatory_pattern>Every `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` header in the generated or updated tracker MUST explicitly invoke `scripts/auto_hardening_runner.py` with `--agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` (or `/tier2-hardening-frontend @[{target}]`). Passing `--no-agent` or omitting `--agent-cmd` is STRICTLY FORBIDDEN (`TRK008` / `TPR008` FATAL).</mandatory_pattern>
    </rule_block>
  </context_rules>
  
  <execution_protocol level="1_tracker_generator">
    <step id="1" name="ACQUIRE PLANS &amp; EXISTING STATE">
      <action>Read the original Epic document, all generated implementation plans from `docs/epic/tasks_EPIC_XXX/`, and [epic_tracker_template.md](./resources/epic_tracker_template.md).</action>
      <action>Use `view_file` to check if `docs/epic/EPIC_XXX_tracker.md` already exists. If it exists, operate in UPDATE MODE.</action>
    </step>
    <step id="2" name="GENERATE OR UPDATE TRACKER">
      <action>Create or surgically update `docs/epic/EPIC_XXX_tracker.md` adhering to [epic_tracker_template.md](./resources/epic_tracker_template.md). Ensure all `uv run` commands include `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline`.</action>
      <constraint name="GRANULAR_FILE_LEVEL_HARDENING_CHECKLIST">
        Under `### Post-Implementation Gates`, list each surviving `[MODIFY]` and `[NEW]` production `.py` file under `Tier 2 Hardening (Backend)` and each surviving production `.dart` file under `Tier 2 Hardening (Frontend)` (strictly excluding `/tests/`, `test_`, `_test.dart`, `.g.dart`, `.freezed.dart`, `[DELETE]` files, and non-code assets). Ensure both `Tier 2 Hardening` header lines include the mandatory `scripts/auto_hardening_runner.py ... --agent-cmd` command without `--no-agent`.
      </constraint>
    </step>
    <step id="3" name="SELF-HEALING TRACKER STRUCTURAL AUDIT">
      <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_tracker_output.py --tracker <path_to_tracker> --plan-dir <path_to_task_dir>` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_plan_tracker_parity.py --plan <path_to_plan> --tracker <path_to_tracker>`. Fix any reported discrepancies (max 3 attempts before `<circuit_breaker_tripped>`).</action>
    </step>
  </execution_protocol>
</system_prompt>
```

