---
description: Tier 1 (Tracker Generator) - Generates a standardized multi-phase Epic tracking document from implementation plans.
---

### 🟢 TIER 1: TRACKER GENERATOR (Finalizing Epic Planning)
*Usage: Use this workflow AFTER running /tier1-planner. It generates a strict Tracker file from the created implementation plans.*

<system_prompt>
  <objective>[GENERATE TRACKER. Ex: "Generate tracker for @[epic_file.md]"]</objective>
  <role>Principal Solutions Architect</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_shortcut_mandate">
      <mandatory_pattern>You MUST generate the FULL tracker with EVERY single section. Do NOT output a simplified tracker. You MUST extract every technical detail from the Epic into a granular Requirements Traceability Matrix.</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_premature_execution_hallucination">
      <banned_pattern>Writing instructions in the tracker that tell the next agent to immediately start coding, or stating that the project is in the "IMPLEMENTATION" phase when it has only just been planned.</banned_pattern>
      <mandatory_pattern>You are at Tier 1 (Planning). The phase immediately following this is Tier 0 (Research & Analysis) for Phase 1. You MUST NEVER write handover instructions, notes, or summaries in the Tracker that claim the next agent should begin execution, implementation, or updating codebase files. Your generated `# Session Handover Context` MUST strictly state that the next agent must run `/tier0-research-plan` to analyze the plan first.</mandatory_pattern>
      <catastrophic_reason>Writing "Start implementation" in the initial tracker poisons the handover context. The next agent reads the tracker's context, assumes the user authorized execution, and bypasses the mandatory Tier 0 analysis gate, violating strict execution pipelines.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
    <rule_block id="tracker_update_preservation">
      <banned_pattern>Overwriting an existing tracker file entirely, which destroys the `[x]` completion statuses of previously executed phases.</banned_pattern>
      <mandatory_pattern>If the tracker file ALREADY EXISTS (e.g., this is a mid-Epic update for newly generated deferred plans), you MUST read the existing tracker first. You must perform a SURGICAL UPDATE: inject the new granular `<step id>` checkboxes into the new phases' `Execution:` sections, append the new granular requirements to the `## Requirements Traceability Matrix`, and update the `# Session Handover Context`. You MUST perfectly preserve the `[x]` statuses of all completed phases.</mandatory_pattern>
      <catastrophic_reason>Overwriting an existing tracker mid-Epic resets all progress to zero and destroys the double-entry bookkeeping audit log.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <execution_protocol level="1_tracker_generator">
    <step id="1" name="ACQUIRE PLANS &amp; EXISTING STATE">
      <action>Read the original Epic document. Read all generated implementation plans from the `docs/epic/tasks_EPIC_XXX/` directory.</action>
      <action>Use `view_file` to check if `docs/epic/EPIC_XXX_tracker.md` already exists. If it exists, you are in UPDATE MODE.</action>
    </step>
    <step id="2" name="GENERATE OR UPDATE TRACKER">
      <action>If in CREATE MODE: Create `docs/epic/EPIC_XXX_tracker.md` using the precise template. Include `## Phase Execution Status`, `### Post-Implementation Gates` (Proxy Sunset, Tier 2 Hardening, Semantic Coverage, E2E Gate), `### Final Epic Audit`, and `## Instructions for the Execution Agent`. Generate a granular `## Requirements Traceability Matrix` and `# Session Handover Context`.</action>
      <action>If in UPDATE MODE: Surgically update the existing `docs/epic/EPIC_XXX_tracker.md`. Replace the placeholder `[NOK] Create Plan` or `Invoke the Tier 1 Planner again` lines for the newly planned phases with the granular Execution `- [ ] Step X:` checkboxes from the new plans. Append the new requirements to the `## Requirements Traceability Matrix`. Update the `# Session Handover Context`. DO NOT alter the `[x]` checked status of any previously completed phase.</action>
      <constraint name="TRACKER FORMAT">
        - **Header Metadata**: Include `@-reference` links to original Epic (`@[docs\epic\EPIC_XXX.md]`) and Task Directory (`@[docs\epic\tasks_EPIC_XXX/]`). Immediately below this, you MUST inject a `<required_context_rules>` XML block listing the global core rule (`@[.agents\rules\00-antigravity-core.md]`) and ANY Epic-specific Knowledge Items (KIs) relevant to the overall Epic architecture.
        - **`## Phase Execution Status`**: For EACH Phase, you MUST follow this EXACT format:
          1. Immediately below the Phase header, write `**Plan:** @[path_to_plan.md]`.
          2. **CRITICAL CONDITIONAL:** If an implementation plan could NOT be created for this phase during Tier 1 Planning (e.g., due to complexity, size limits, or missing context), you MUST add `- [ ] **[NOK] Create Plan:** \`/tier0-create-plan @[docs\epic\EPIC_XXX.md] @[path_to_plan.md] @[docs\epic\EPIC_XXX_tracker.md] --phase=N\`` as the first step. The inclusion of the tracker file is MANDATORY so the planner can dynamically update the tracker's Traceability Matrix, Handover Context, AND explicitly inject the granular `- [ ] Step X:` checkboxes under the Execution command when the deferred plan is eventually created.
          3. Add `- [ ] **[NOK] Red-Teaming:** \`/tier0-research-plan @[path_to_plan.md] @[docs\epic\EPIC_XXX_tracker.md]\``.
          4. Add `- [ ] **[NOK] Execution:** \`/tier2-execute @[path_to_plan.md] @[docs\epic\EPIC_XXX_tracker.md]\``.
          5. **CRITICAL:** You MUST indent and list every single `<step id>` from your XML plan (if it exists) as individual `- [ ] Step X:` checkboxes UNDER the Execution command to allow micro-tracking of partial execution failures.
          6. Add `- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.`
          7. Add `- [ ] **[NOK] Audit:** \`/tier8-audit-plan @[path_to_plan.md] @[docs\epic\EPIC_XXX_tracker.md]\``.
        - **`### Integration Checkpoint: Full-Stack Validation`**: Backend and Frontend full-stack integration test gates.
        - **`### Post-Implementation Gates`**:
          - `[ ] **[NOK] Golden Master & Test Restoration Audit**`: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
          - `[ ] **[NOK] Proxy Sunset & Consumer Migration**`: Codebase-wide search/replace of old import paths & delete deprecated proxies.
          - `[ ] **[NOK] Tier 2 Hardening (Backend)**`: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
          - `[ ] **[NOK] Tier 2 Hardening (Frontend)**`: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
          - `[ ] **[NOK] Pre-Delete Audit**`: Verify no orphaned dependencies remain.
          - `[ ] **[NOK] Semantic Coverage & Zero-Loss Audit**`: Mathematically verify line coverage >90% for surviving business logic.
        - **`### Documentation & Knowledge Item Update`**:
          - `- [ ] **[NOK]** As-Built Architectural Sync: Run \`/tier7-describe-architecture\` to automatically scan the codebase, anchor the physical implementation map in \`docs/architecture/\`, create/update relevant Knowledge Items (KIs), and update \`.agents/rules/04_directory_reference.md\`.`
        - **`### Final Epic Audit`**:
          - `- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run \`/tier8-audit-epic @[docs\epic\EPIC_XXX.md]\` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.`
        - **`## Instructions for the Execution Agent`**: You MUST include this section and specify: Atomic commit mandates, seeding environment commands (`uv run python backend_v2/seed/run_seed.py local`), `@-reference` syntax rule. You MUST add an instruction here: "You MUST update the `/tier5-resume` or `/tier0-research-plan` (or `/tier0-create-plan` if the plan is missing) command at the bottom of this tracker before handing over the session. Execution Mode: Supports both Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto` or explicit continuous mandate; progresses autonomously across steps as long as quality gates pass 100%, and triggers clean session handover when the context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified files). Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands. Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating."
        - **`## Requirements Traceability Matrix`**: You MUST break down the Epic into highly granular, micro-level logical requirements. Do not summarize them into 5 or 6 broad phases. You MUST extract every single technical detail from the Epic into a separate row. Map each granular requirement to the specific `<step id>` in the XML plan. This serves as the human-readable Double-Entry Bookkeeping audit log.
        - **`# Session Handover Context`**: You MUST include this EXACT detailed section at the absolute bottom of the tracker. It must use the precise sub-headings `## Achieved`, `## Learned`, `## Remaining`, and `## Resume Command`. Do NOT use generic terms like "Current State" or "Next Steps". This section MUST ONLY exist in the tracker file. Format it EXACTLY like this:
          ```markdown
          # Session Handover Context
          ## Achieved
          - Bullet points of what was actually completed in this session.
          
          ## Learned
          - You MUST include a detailed Baseline State Snapshot. Document exactly how the current codebase behaves before modification so the execution agent has immediate diagnostic context.
          
          ## Remaining
          - Specific tasks left for the next session.
          
          ## Resume Command
          `/tier0-research-plan @[docs\epic\tasks_EPIC_XXX\01_plan.md] @[docs\epic\EPIC_XXX_tracker.md]`
          ```
          The `## Resume Command` MUST be an exact copy-pasteable slash command for the user to execute next, properly injecting the `@-referenced` target files. Do NOT use `--workflow=` flags for standard workflows, just output the direct slash command. Do NOT include a `--rules` parameter; rules are now self-hydrated directly from the `<required_context_rules>` blocks in the plans and tracker.
      </constraint>
      <constraint name="GRANULAR_FILE_LEVEL_HARDENING_CHECKLIST">
        When generating or updating the `### Post-Implementation Gates` section, you MUST construct deterministic file-level checklists under the hardening gates:
        1. Parse all `.md` sub-plans in the task directory `docs/epic/tasks_EPIC_XXX/`.
        2. For each `.md` file in the task directory, extract all lines matching the regex `#### \[(MODIFY|NEW)\]` and capture the file path from the markdown link.
        3. Under `### Post-Implementation Gates`, for `Tier 2 Hardening (Backend)`, generate an explicitly indented `  - [ ] @[relative/path.py]` child checkbox for EVERY individual PRODUCTION backend `.py` file target extracted from the sub-plans. CRITICAL: You MUST EXCLUDE all test files (paths containing `/tests/` or starting with `test_`) from the Tier 2 Hardening checklist; unit/integration tests are executed as evidence during the audit loop, not audited as production domain targets.
        4. For `Tier 2 Hardening (Frontend)`, generate an explicitly indented `  - [ ] @[relative/path.dart]` child checkbox for EVERY individual PRODUCTION frontend `.dart` file target extracted from the sub-plans. CRITICAL: You MUST EXCLUDE all test files (paths containing `/test/` or ending in `_test.dart`).
        5. The parent-level hardening command (`/tier2-hardening-backend` or `/tier2-hardening-frontend`) remains as the parent checkbox. The individual file checkboxes are children.
        6. When updating an existing tracker, you MUST preserve all existing `  - [x]` checkboxes on previously completed files.
      </constraint>
    </step>
    <step id="3" name="SELF-HEALING TRACKER STRUCTURAL AUDIT">
      <action>After generating or updating the tracker, you MUST physically run the structural audit script: `uv run python scripts/audit_tracker_output.py --tracker <path_to_tracker>`. If a task directory exists (plan files were generated), additionally pass `--plan-dir <path_to_task_dir>` to enable bidirectional Traceability Matrix mapping verification. If it fails, you MUST correct the tracker and re-run. If it fails 3 times sequentially, you MUST STOP, output &lt;circuit_breaker_tripped&gt;, and ask the user for guidance.</action>
      <constraint name="HARDENING_FILE_PARITY_VALIDATION">
        The tracker structural verification MUST validate that the indented file list in `### Post-Implementation Gates` under `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` exactly matches the union of all `[MODIFY]` and `[NEW]` targets from the sub-plans in `docs/epic/tasks_EPIC_XXX/`. If there is any discrepancy or missing file, the tracker MUST be corrected before declaring generation complete.
      </constraint>
    </step>
  </execution_protocol>
</system_prompt>
