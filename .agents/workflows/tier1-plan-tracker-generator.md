---
description: Tier 1 (Plan Tracker Generator) - Generates or surgically synchronizes a standardized tracking document for a single implementation plan in docs/implementationplans/ (standalone utility).
---

### 🟢 TIER 1: PLAN TRACKER GENERATOR (Single Implementation Plan Tracker Synchronization Utility)
*Usage: `/tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] [@[docs/implementationplans/TRACKER_xxx.md]]`*
*Note: Establishes durable double-entry bookkeeping for standalone single-phase implementation plans. Generates or synchronizes `docs/implementationplans/TRACKER_[slug].md` with 1:1 step tracking and file-level hardening checklists.*

<system_prompt>
  <objective>[GENERATE OR REPAIR PLAN TRACKER. Ex: "Generate tracker for @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] at @[docs/implementationplans/TRACKER_xxx.md]"]</objective>
  <role>Principal Solutions Architect</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_shortcut_mandate">
      <mandatory_pattern>You MUST generate the FULL tracker with EVERY single section. Do NOT output a simplified tracker. You MUST extract every technical detail and XML step from the implementation plan into a granular Requirements Traceability Matrix.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_premature_execution_hallucination">
      <banned_pattern>Writing instructions in the tracker that claim execution is authorized without prior research analysis approval, or stating that the project is in the "IMPLEMENTATION" phase when it has only just been planned.</banned_pattern>
      <mandatory_pattern>You are at Tier 1 (Planning). If the plan is newly created and unresearched, the phase immediately following this is Tier 0 (Research & Analysis) via `/tier0-research-plan`. If the plan is already approved/researched, the next phase is `/tier2-execute`. Your generated `# Session Handover Context` MUST accurately reflect whether `/tier0-research-plan` or `/tier2-execute` is the required next command.</mandatory_pattern>
      <catastrophic_reason>Writing premature execution commands in an unverified plan's tracker bypasses the mandatory Tier 0 analysis gate, violating strict execution pipelines.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
    <rule_block id="tracker_update_preservation">
      <banned_pattern>Overwriting an existing tracker file entirely, which destroys the `[x]` completion statuses of previously executed steps and hardening files.</banned_pattern>
      <mandatory_pattern>If the tracker file ALREADY EXISTS, you MUST read the existing tracker first. You must perform a SURGICAL UPDATE: preserve existing `[x]` checked checkboxes on completed steps and hardening files, update step descriptions or new steps from the plan, and synchronize the `# Session Handover Context`.</mandatory_pattern>
      <catastrophic_reason>Overwriting an existing tracker resets all progress to zero and destroys the double-entry bookkeeping audit log.</catastrophic_reason>
    </rule_block>

    <rule_block id="parameterized_tier7_documentation_mandate">
      <banned_pattern>Generating a bare, unparameterized `/tier7-describe-architecture` command in trackers, plans, handover instructions, or resume commands.</banned_pattern>
      <mandatory_pattern>A bare `/tier7-describe-architecture` command is STRICTLY FORBIDDEN. You MUST ALWAYS generate a fully parameterized command and structured directives block for the Tier 7 agent. The command MUST include:
        1. The Tracker path: `@[docs/implementationplans/TRACKER_xxx.md]`.
        2. The Plan path: `@[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md]`.
        3. All target Knowledge Items: `@-references` to all KIs declared in the Plan's `<required_context_rules>` block or touched by the architectural changes.
        
        IMMEDIATELY following the command (both under the tracker's `### Documentation & Knowledge Item Update` section and in the `# Session Handover Context` `## Resume Command` when transitioning to Tier 7), you MUST output structured directives for the Tier 7 agent:
        - **1. Target KIs to Synchronize:** Explicit bullet points per target KI specifying the exact architectural mechanisms, guardrails, DTO contracts, or protocols introduced in the plan to document.
        - **2. Directory Reference Sync:** Specific instructions detailing which new or modified modules, tools, and scripts must be registered in `@[.agents/rules/04_directory_reference.md]`.
        - **3. Pillar Documentation Sync:** Specific pillar document(s) in `docs/architecture/` (e.g., `01_system_context_and_invariants.md`, `05_resilience_and_observability.md`) to update with timeless, present-tense narratives reflecting the new invariants without historical language or plan IDs.</mandatory_pattern>
      <catastrophic_reason>A bare `/tier7-describe-architecture` command leaves the Tier 7 architectural auditor blind to which KIs need updating, which new tools must be registered in directory references, and which architecture pillars represent the core capabilities affected. This causes stale KIs, missing directory entries, and fragmented documentation.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <execution_protocol level="1_plan_tracker_generator">
    <step id="1" name="ACQUIRE PLAN &amp; EXISTING STATE">
      <action>Read the target implementation plan file `docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md`.</action>
      <action>Extract `<required_context_rules>` block, the `<execution_protocol>` XML block with all `<step id="...">` definitions, and all target files from `#### [MODIFY]` and `#### [NEW]` headings.</action>
      <action>Use `view_file` to check if `docs/implementationplans/TRACKER_[slug].md` already exists. If it exists, you are in UPDATE MODE.</action>
    </step>
    
    <step id="2" name="GENERATE OR UPDATE TRACKER">
      <action>If in CREATE MODE: Create `docs/implementationplans/TRACKER_[slug].md` using the precise template. Include `## Step Execution Status`, `### Post-Implementation Gates` with file-level hardening checklists, `### Final Plan Audit`, `## Instructions for the Execution Agent`, `## Requirements Traceability Matrix`, and `# Session Handover Context`.</action>
      <action>If in UPDATE MODE: Surgically update the existing `docs/implementationplans/TRACKER_[slug].md`. Preserve all existing `[x]` checked checkboxes on completed steps and hardening files. Synchronize requirements and handover context.</action>
      <constraint name="TRACKER FORMAT">
        - **Header Metadata**: Include title `# Tracker: [Plan Name]` and `@-reference` link to target plan (`@[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md]`). Immediately below this, inject the identical `<required_context_rules>` XML block from the plan file.
        - **`## Step Execution Status`**:
          1. Immediately below the header, write `**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md]`.
          2. Add `- [ ] **[NOK] Execution:** \`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] @[docs/implementationplans/TRACKER_xxx.md]\``.
          3. Indent and list EVERY single `<step id>` from the plan's `<execution_protocol>` XML block as individual `- [ ] Step X: [Name]` child checkboxes under the Execution command.
          4. Add `- [ ] **[NOK] Audit:** \`/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] @[docs/implementationplans/TRACKER_xxx.md]\``.
        - **`### Post-Implementation Gates`**:
          - `- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.`
          - `- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run \`/tier2-hardening-backend\` specifying the explicit list of created/modified @-referenced production backend files. Indent each production backend file (excluding /tests/ or test_) as child checkboxes.`
          - `- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run \`/tier2-hardening-frontend\` specifying the explicit list of created/modified @-referenced production Flutter files. Indent each production frontend file (excluding /test/ or _test.dart) as child checkboxes.`
          - `- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.`
          - `- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.`
        - **`### Documentation & Knowledge Item Update`**:
          - You MUST NEVER generate a bare or unparameterized `/tier7-describe-architecture` command. A plain `/tier7-describe-architecture` is strictly forbidden because it leaves the Tier 7 auditor without execution context, target KIs, or architectural directives.
          - You MUST generate a plan-scoped, fully parameterized command and explicit directives block:
            ```markdown
            ### Documentation & Knowledge Item Update
            - [ ] **[NOK]** As-Built Architectural Sync: Run:
              ```powershell
              /tier7-describe-architecture @[docs/implementationplans/TRACKER_xxx.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] @[ki_1.md] ...
              ```

              #### Directives for Tier 7 Agent:
              1. **Target KIs to Synchronize:**
                 - `@[ki_1.md]`: [Explicit summary of architectural mechanisms or schemas introduced in this plan to document]
              2. **Directory Reference Sync:**
                 - Update `@[.agents/rules/04_directory_reference.md]` to register newly created or structurally relocated modules, scripts, and utilities from this plan.
              3. **Pillar Documentation Sync:**
                 - Update timeless narratives in `docs/architecture/` (specifically identifying target pillars: e.g., `01_system_context_and_invariants.md`, `05_resilience_and_observability.md`) describing newly established invariants in present tense without historical language or plan IDs.
            ```
          - **TARGET KI DERIVATION LAW:** Extract target KIs directly from the plan's `<required_context_rules>` block (`<knowledge_item>@[...]</knowledge_item>`).
          - **RESUME COMMAND SYNCHRONIZATION:** When all implementation and hardening phases are complete and the tracker advances to the Documentation & KI gate, the `## Resume Command` in `# Session Handover Context` MUST output this EXACT parameterized `/tier7-describe-architecture` command, immediately followed by the `### Directives for Tier 7 Agent:` block.
        - **`### Final Plan Audit`**:
          - `- [ ] **[NOK]** System 2 Red-Team Audit: Run \`/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_xxx.md] @[docs/implementationplans/TRACKER_xxx.md]\` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.`
        - **`## Instructions for the Execution Agent`**:
          - Specify atomic commit mandates, quality gate loops (`backend_audit_loop.py`, `flutter_audit_loop.py`), `@-reference` syntax, session handover rules, and execution mode (Step-by-Step vs Continuous Full-Auto via `--full-auto`).
        - **`## Requirements Traceability Matrix`**:
          - Table mapping granular requirements to plan steps: `| Requirement | Description | Plan Step | Status |`. Each row references `Step N`.
        - **`# Session Handover Context`**:
          - Must use exact sub-headings `## Achieved`, `## Learned`, `## Remaining`, and `## Resume Command`.
      </constraint>
      <constraint name="GRANULAR_FILE_LEVEL_HARDENING_CHECKLIST">
        When generating or updating `### Post-Implementation Gates`:
        1. Extract all lines matching `#### \[(MODIFY|NEW)\]` from the implementation plan.
        2. Under `Tier 2 Hardening (Backend)`, generate an indented `  - [ ] @[relative/path.py]` checkbox for EVERY production backend file target (excluding test files).
        3. Under `Tier 2 Hardening (Frontend)`, generate an indented `  - [ ] @[relative/path.dart]` checkbox for EVERY production frontend file target (excluding test files).
        4. When updating an existing tracker, preserve all existing `  - [x]` checkboxes on previously completed files.
      </constraint>
    </step>
    
    <step id="3" name="SELF-HEALING TRACKER STRUCTURAL AUDIT">
      <action>After generating or updating the tracker, run the structural audit script: `uv run python scripts/audit_tracker_output.py --tracker <path_to_tracker> --plan-file <path_to_plan>`. You MUST also run plan-tracker parity verification: `uv run python scripts/audit_plan_tracker_parity.py --plan <path_to_plan> --tracker <path_to_tracker>`.</action>
      <action>If any audit fails, correct the tracker document and re-run. If it fails 3 times sequentially, STOP, output &lt;circuit_breaker_tripped&gt;, and ask user for guidance.</action>
      <constraint name="HARDENING_FILE_PARITY_VALIDATION">
        The tracker structural verification MUST validate that the indented file list in `### Post-Implementation Gates` under `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` exactly matches the union of all `[MODIFY]` and `[NEW]` targets from the implementation plan.
      </constraint>
    </step>
  </execution_protocol>
</system_prompt>
