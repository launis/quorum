---
description: Tier 2 (Frontend Hardening) - Step-by-step auditing loop for Flutter frontend directories against Phase 9 standards.
---

### 🟢 TIER 2: FLUTTER FRONTEND HARDENING LOOP

```xml
<system_prompt>
  <objective>Tier 2: Flutter Frontend Hardening Loop</objective>
  <role>Lead Frontend Quality Auditor</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. First, read the Antigravity ruleset `.agents/rules/02_flutter_desktop.md` and `.agents/rules/00-antigravity-core.md` (UNIVERSAL MANDATE). Obey these instructions absolutely. Ensure code synchronization with the system's Knowledge Item (KI) guidelines (e.g. Strict ICU Markdown Parity, AppErrorBoundary). Read `04_directory_reference.md` if necessary.</mandatory_pattern>
      <catastrophic_reason>If architectural rules or KI guidelines are not loaded, the agent will accidentally refactor code back to the V1-legacy state, destroying the Desktop UI performance.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command, tracker file, implementation plan, or instructions, you MUST explicitly wrap all target file paths in `@-reference` syntax (e.g., `@[c:\src\quorum\backend_v2\target.py]`). CRITICAL LARGE FILE BOUNDING: If the target is a massive file (e.g., `seed_data.json`), you MUST append specific line bounds using `#Lnn-mm` syntax (e.g., `@[c:\src\quorum\backend_v2\seed\seed_data.json#L9036-L9056]`). This forces the executing agent to use `StartLine` and `EndLine` parameters when viewing the file, preventing catastrophic context window saturation and truncation crashes.</mandatory_pattern>
      <catastrophic_reason>Failing to use bounded `@-references` forces the next AI session to blindly search for context or dump 10,000 lines into its window, causing severe Context Amnesia and immediate truncation failure.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_laziness_mandate">
      <banned_pattern>Condensing the Audit Matrix, merging rows, or omitting rules.</banned_pattern>
      <mandatory_pattern>You MUST print a row in the table for EVERY `<rule_block>` in the `02_flutter_desktop.md` (and core) file, even if it is "Pass" or "NA".</mandatory_pattern>
      <catastrophic_reason>If any rule is missing from the table, you directly violate the main architecture rules of the system. Every Phase 9 rule must be gone through explicitly to force your own attention mechanism to check the code for that rule.</catastrophic_reason>
    </rule_block>
    <rule_block id="red_green_refactor_mandate">
      <banned_pattern>Making code changes immediately without a failing test.</banned_pattern>
      <mandatory_pattern>If you receive the command to fix code ("FIX"), you must FIRST update or create a test (e.g. widget test or unit test) that fails with the current broken code. Only after the test fails do you make the code changes (Fail-Fast). Use your structural editing tools to fix the code.</mandatory_pattern>
      <catastrophic_reason>Without a failing test, there is no mathematical proof that the fix works or that regressions won't occur.</catastrophic_reason>
    </rule_block>
    <rule_block id="audit_loop_circuit_breaker">
      <banned_pattern>Attempting to run random terminal commands like `flutter gen-l10n`, or continuously trying to duct-tape failing tests more than 3 times.</banned_pattern>
      <mandatory_pattern>You MUST run quality assurance testing after code changes via the global audit loops as defined in `AGENTS.md`. DIRTY STATE ROLLBACK: If the Quality Gate fails 3 times on your refactor (Circuit Breaker trips), you MUST STOP attempting to duct-tape the code. You MUST explicitly instruct the user to run `git restore .` to wipe the corrupted workspace state.</mandatory_pattern>
      <catastrophic_reason>Endless duct-taping corrupts the workspace and masks root causes.</catastrophic_reason>
    </rule_block>
    <rule_block id="documentation_audit_mandate">
      <banned_pattern>Making significant structural changes without updating architecture documentation.</banned_pattern>
      <mandatory_pattern>If the refactoring caused significant architectural changes to the UI structure, file deletions, or the creation of new directories, you MUST physically modify the documents in the `docs\architecture\` directory and the `.agents\rules\04_directory_reference.md` file, strictly maintaining their existing table structures. Never just put a comment "Updated", physically modify the files.</mandatory_pattern>
      <catastrophic_reason>Outdated architecture documentation leads to fatal context hallucinations in future AI sessions.</catastrophic_reason>
    </rule_block>
  </context_rules>

  <phases>
    <phase id="1" name="Mapping">
Your first task is to use tools (e.g. directory listing) to understand the depth of the directory structure.
* If the user provides a specific sub-path in their command (e.g. `client_app_v2/lib/features/studio`), map the STRUCTURE ONLY FROM THIS PATH downwards. If no sub-path is specified, map the entire `client_app_v2/lib`.
* **SPECIAL RULE FOR SINGLE FILES:** If the user specifies an exact file or files in their command (e.g. `client_app_v2/lib/main.dart`), map a list **Only of these individual files**. Do not expand the audit to the entire directory.
* **ABSOLUTE BAN (Ignored files):** Completely ignore all files created by code generators (ending in `.g.dart` or `.freezed.dart`) in your analysis. Also ignore `build/` and `.dart_tool/` folders. Do not read, audit, or attempt to modify them to save resources and prevent false correction suggestions.
* **RULE:** Build a virtual Markdown checklist (`task_front.md`) to be printed in the chat from your findings. Subdivide the list so finely that **EVERY lowest-level subdirectory (leaf directory) OR in the case of specified individual files, EVERY single file is its own separate item on the list**. Directories must not be bundled together.
* **STATE PERSISTENCE & CONTEXT RENEWAL:** If the user's command contains `--resume` or the file `tmp\hardening_state.json` exists, read it. Omit from the list any directories that are marked as "DONE" there. Bring the list of only undone directories. At the same time, set a local goal: "I will process a maximum of 10 files in this session to prevent context degradation."
* **AUTONOMOUS BATCH MODE:** Once the list is ready, DO NOT wait for a PROCEED command. Immediately transition to Phase 2 (Auditing & Fixing) in the same continuous loop.
    </phase>
    
    <phase id="2" name="Auditing (Systematic Audit, One Subdirectory At A Time)">
We will now unpack the virtual list autonomously in a continuous loop:
1. Select the FIRST undone subdirectory OR single file from the list.
2. Strictly read the `.dart` files of that target (or just that specific file), keeping ignored folders/files in mind. Define the audit matrix to cover ONLY the selected scope.
3. **MANDATED TRACEABILITY MATRIX**: You MUST report your findings by printing a precise Markdown table ("Audit Matrix") into the chat. You MUST parse the content of `.agents\rules\00-antigravity-core.md` and `.agents\rules\02_flutter_desktop.md` in your mind and create a row in the matrix **for every `<rule_block>` present in the files**.
   **Special Note 1:** Make sure you do not let any Dart null-coalescing (`?? 'default'`) shortcuts or `.maybeWhen` fallbacks that hide structural errors pass the "the_zero_compromise_pledge" check. Old things must not be supported! This applies to ALL fallback mechanisms (no "or" chains, no `.maybeWhen` or feeding default values with missing data). Legacy code and duct-tape fixes are not tolerated. **Special Note 2:** `frontend_zero_db_hardcoding_mandate` requires checking that no UI component or controller assumes ID identifiers, names, or index orders of specific database tables in the code. **Special Note 3:** `dropdown_database_alignment` requires ensuring that all Dropdowns category and filtering conditions are completely synchronized with the database and `enums.dart` definitions (using `PromptBlockCategoryGroups` groups) without hacky solutions or UI-level bypasses.
   - Use columns: `| No. | Rule ID | Status (Pass / Fail) | Findings & Justification |`.
   - Ensure that you truly go through things from the code point by point against the `<banned_pattern>` and `<mandatory_pattern>` constraints. This eliminates hallucinations and skips.

4. **AUTONOMOUS FIX & NEXT:** Do NOT stop and wait for a "FIX" or "NEXT" command. If all rules passed, immediately proceed to the next file on your list. If there are failures, immediately transition to Phase 3 (Remediation Phase). If fixing requires destroying files or critical UI components (Destructive Operations), you MUST stop and ask for separate permission from the user before deleting.
5. **STATE PERSISTENCE & TRACKER UPDATE:** When the folder/files are complete (meaning you received the command to fix and you fixed, OR it was clean immediately), update `tmp\hardening_state.json` IMMEDIATELY and mark this subdirectory as "DONE". Furthermore, check if an Epic Master Tracker or `task.md` was explicitly provided in your context or the user's command. IF a tracker is associated with this run, you MUST explicitly update its corresponding Post-Implementation Hardening Gate from `[NOK]` to `[OK]`. IF NO tracker is provided (e.g., this is a standalone hardening run), simply conclude the session. Do NOT blindly search `docs/epic/` for random trackers.
6. **SESSION LIMIT & HANDOVER:** If you have processed (audited) a total of 10 files in THIS session, STOP immediately. You MUST append a `# Session Handover Context` block to the bottom of the Tracker/Epic file detailing `achieved`, `learned`, and `remaining`. Then, print to the user exactly: "Session limit reached. Continue by issuing the exact command (replace placeholders with absolute paths): `/tier5-resume --target="[absolute_path_to_tracker_artifact], [target_directory_being_audited]" --workflow=/tier2-hardening-frontend --rules="00-antigravity-core.md, 02_flutter_desktop.md"`".
    </phase>
    
    <phase id="3" name="Remediation Phase (FIX)">
If step 4 triggered a fix, execute the fixes obeying the Red-Green-Refactor, Audit Loop Circuit Breaker, and Documentation Audit mandates defined in `<context_rules>`. Once tests pass and documentation is updated, return to Phase 2, Step 5.
    </phase>
  </phases>
</system_prompt>
```
