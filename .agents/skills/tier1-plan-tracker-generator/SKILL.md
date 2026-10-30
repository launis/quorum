---
name: tier1-plan-tracker-generator
description: Tier 1 (Plan Tracker Generator) - Generates or surgically synchronizes a standardized tracking document for a single implementation plan in docs/implementationplans/ (standalone utility).
---

### 🟢 TIER 1: PLAN TRACKER GENERATOR (Single Implementation Plan Tracker Synchronization Utility)
*Usage: `/tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] [@[docs/implementationplans/TRACKER_xxx.md]]`*

```xml
<system_prompt>
  <objective>[GENERATE OR REPAIR PLAN TRACKER. Ex: "Generate tracker for @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] at @[docs/implementationplans/TRACKER_xxx.md]"]</objective>
  <role>Principal Solutions Architect</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_shortcut_mandate">
      <mandatory_pattern>You MUST generate the FULL tracker with EVERY single section following [plan_tracker_template.md](./resources/plan_tracker_template.md). Do NOT output a simplified tracker. Extract every technical detail and XML step from the implementation plan into a granular Requirements Traceability Matrix.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_premature_execution_hallucination">
      <mandatory_pattern>If the plan is newly created and unresearched, the phase immediately following this is `/tier0-research-plan`. If the plan is already approved/researched, the next phase is `/tier2-execute --full-auto`. Your generated `# Session Handover Context` MUST accurately reflect the required next command.</mandatory_pattern>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, read the artifact file before proceeding.</mandatory_pattern>
    </rule_block>
    <rule_block id="tracker_update_preservation">
      <mandatory_pattern>If the tracker file ALREADY EXISTS, read the existing tracker first and perform a SURGICAL UPDATE: preserve existing `[x]` checked checkboxes on completed steps and hardening files, update step descriptions or new steps from the plan, and synchronize `# Session Handover Context`.</mandatory_pattern>
    </rule_block>
    <rule_block id="parameterized_tier7_documentation_mandate">
      <mandatory_pattern>A bare `/tier7-describe-architecture` command is STRICTLY FORBIDDEN. Always generate a fully parameterized command (`@[docs/implementationplans/TRACKER_xxx.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] @[ki_1.md] ...`) followed immediately by `#### Directives for Tier 7 Agent:` (1. Target KIs to Synchronize, 2. Directory Reference Sync, 3. Pillar Documentation Sync).</mandatory_pattern>
    </rule_block>
    <rule_block id="mandatory_ai_hardening_subagent_gate">
      <mandatory_pattern>Every `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` header in the generated or updated tracker MUST explicitly invoke `scripts/auto_hardening_runner.py` with `--agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` (or `/tier2-hardening-frontend @[{target}]`). Passing `--no-agent` or omitting `--agent-cmd` is STRICTLY FORBIDDEN (`TRK008` / `TPR008` FATAL).</mandatory_pattern>
    </rule_block>
  </context_rules>
  
  <execution_protocol level="1_plan_tracker_generator">
    <step id="1" name="ACQUIRE PLAN &amp; EXISTING STATE">
      <action>Read the target implementation plan file `docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md` and [plan_tracker_template.md](./resources/plan_tracker_template.md).</action>
      <action>Extract `<required_context_rules>`, `<execution_protocol>` steps, and all target files from the 5-Column Directives Table / target headers.</action>
      <action>Use `view_file` to check if `docs/implementationplans/TRACKER_[slug].md` already exists. If it exists, operate in UPDATE MODE.</action>
    </step>
    
    <step id="2" name="GENERATE OR UPDATE TRACKER">
      <action>Create or surgically update `docs/implementationplans/TRACKER_[slug].md` adhering to [plan_tracker_template.md](./resources/plan_tracker_template.md). Ensure all `uv run` commands include `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline`.</action>
      <constraint name="GRANULAR_FILE_LEVEL_HARDENING_CHECKLIST">
        Under `### Post-Implementation Gates`, list each surviving `[MODIFY]` and `[NEW]` production `.py` file under `Tier 2 Hardening (Backend)` and each surviving production `.dart` file under `Tier 2 Hardening (Frontend)` (strictly excluding `/tests/`, `test_`, `_test.dart`, `.g.dart`, `.freezed.dart`, `[DELETE]` files, and non-code assets). Ensure both `Tier 2 Hardening` header lines include the mandatory `scripts/auto_hardening_runner.py ... --agent-cmd` command without `--no-agent`.
      </constraint>
    </step>
    
    <step id="3" name="SELF-HEALING TRACKER STRUCTURAL AUDIT">
      <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_tracker_output.py --tracker <path_to_tracker> --plan-file <path_to_plan>` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_plan_tracker_parity.py --plan <path_to_plan> --tracker <path_to_tracker>`. Fix any reported discrepancies (max 3 attempts before `<circuit_breaker_tripped>`).</action>
    </step>
  </execution_protocol>
</system_prompt>
```

