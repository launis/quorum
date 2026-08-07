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
  </context_rules>
  
  <execution_protocol level="1_tracker_generator">
    <step id="1" name="ACQUIRE PLANS">
      <action>Read the original Epic document. Read all generated implementation plans from the `docs/epic/tasks_EPIC_XXX/` directory.</action>
    </step>
    <step id="2" name="GENERATE TRACKER">
      <action>Create `docs/epic/EPIC_XXX_tracker.md` using the precise template.
      Include `## Phase Execution Status`, `### Post-Implementation Gates` (Proxy Sunset, Tier 2 Hardening, Semantic Coverage, E2E Gate), `### Final Epic Audit`, and `## Instructions for the Execution Agent`.</action>
      <action>Generate a granular `## Requirements Traceability Matrix` mapped to the XML `<step id>` tags from the plans.</action>
      <action>Generate `# Session Handover Context` at the bottom with `## Achieved`, `## Learned`, `## Remaining`, and `## Resume Command`.</action>
      <constraint name="TRACKER FORMAT">
        - **Header Metadata**: Include `@-reference` links to original Epic (`@[c:\src\quorum\docs\epic\EPIC_XXX.md]`) and Task Directory (`@[c:\src\quorum\docs\epic\tasks_EPIC_XXX/]`). Immediately below this, you MUST inject a `<required_context_rules>` XML block listing the global core rule (`@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`) and ANY Epic-specific Knowledge Items (KIs) relevant to the overall Epic architecture.
        - **`## Phase Execution Status`**: For EACH Phase, you MUST follow this EXACT format:
          1. Immediately below the Phase header, write `**Plan:** @[path_to_plan.md]`.
          2. Add `- [ ] **[NOK] Red-Teaming:** \`/tier0-research-plan ...\``.
          3. Add `- [ ] **[NOK] Execution:** \`/tier2-execute ...\``.
          4. **CRITICAL:** You MUST indent and list every single `<step id>` from your XML plan as individual `- [ ] Step X:` checkboxes UNDER the Execution command to allow micro-tracking of partial execution failures. Include the step name and a short description.
          5. Add `- [ ] **[NOK] Audit:** \`/tier8-audit-plan ...\``.
        - **`### Integration Checkpoint: Full-Stack Validation`**: Backend and Frontend full-stack integration test gates.
        - **`### Post-Implementation Gates`**:
          - `[ ] **[NOK] Golden Master & Test Restoration Audit**`: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
          - `[ ] **[NOK] Proxy Sunset & Consumer Migration**`: Codebase-wide search/replace of old import paths & delete deprecated proxies.
          - `[ ] **[NOK] Tier 2 Hardening (Backend)**`: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
          - `[ ] **[NOK] Tier 2 Hardening (Frontend)**`: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
          - `[ ] **[NOK] Pre-Delete Audit**`: Verify no orphaned dependencies remain.
          - `[ ] **[NOK] Semantic Coverage & Zero-Loss Audit**`: Mathematically verify line coverage >90% for surviving business logic.
          - `[ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.
        - **`### Documentation & Knowledge Item Update`**:
          - `- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.`
          - `- [ ] **[NOK]** As-Built Architectural Sync: Run \`/tier7-describe-architecture\` to automatically scan the codebase, anchor the physical implementation map in \`docs/architecture/\`, and update \`.agents/rules/04_directory_reference.md\`.`
        - **`### Final Epic Audit`**:
          - `- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run \`/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_XXX.md]\` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.`
        - **`## Instructions for the Execution Agent`**: You MUST include this section and specify: Atomic commit mandates, seeding environment commands (`uv run python backend_v2/seed/run_seed.py local`), `@-reference` syntax rule. You MUST add an instruction here: "You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating."
        - **`## Requirements Traceability Matrix`**: You MUST break down the Epic into highly granular, micro-level logical requirements (e.g., R1 through R15+). Do not summarize them into 5 or 6 broad phases. You MUST extract every single technical detail from the Epic into a separate row. Map each granular requirement to the specific `<step id>` in the XML plan. This serves as the human-readable Double-Entry Bookkeeping audit log.
        - **`# Session Handover Context`**: You MUST include this EXACT detailed section at the absolute bottom of the tracker. It must use the precise sub-headings `## Achieved`, `## Learned`, `## Remaining`, and `## Resume Command`. Do NOT use generic terms like "Current State" or "Next Steps". This section MUST ONLY exist in the tracker file. Format it EXACTLY like this:
          ```markdown
          # Session Handover Context
          ## Achieved
          - Bullet points of what was actually completed in this session.
          
          ## Learned
          - You MUST include a detailed Baseline State Snapshot. Document exactly how the current codebase behaves before modification (e.g. existing function signatures, problematic lines) so the execution agent has immediate diagnostic context.
          
          ## Remaining
          - Specific tasks left for the next session.
          
          ## Resume Command
          `/tier5-resume --workflow=/tier0-research-plan --target="@[c:\src\quorum\docs\epic\EPIC_XXX_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_XXX\01_plan.md]"`
          ```
          The `## Resume Command` MUST be an exact copy-pasteable slash command for the user to execute next, properly injecting the `@-referenced` target files. Do NOT include a `--rules` parameter; rules are now self-hydrated directly from the `<required_context_rules>` blocks in the plans and tracker.
      </constraint>
    </step>
  </execution_protocol>
</system_prompt>
