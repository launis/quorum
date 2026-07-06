---
description: Tier 2 (Frontend Hardening) - Step-by-step auditing loop for Flutter frontend directories against Phase 9 standards.
---

### 🟢 TIER 2: FLUTTER FRONTEND HARDENING LOOP

```xml
<system_prompt>
  <objective>Tier 2: Flutter Frontend Hardening Loop</objective>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>First, read the Antigravity ruleset `.agents/rules/02_flutter_desktop.md` and `.agents/rules/00-antigravity-core.md` (UNIVERSAL MANDATE). Obey these instructions absolutely. Ensure code synchronization with the system's Knowledge Item (KI) guidelines (e.g. Strict ICU Markdown Parity, AppErrorBoundary). Read `04_directory_reference.md` if necessary.</mandatory_pattern>
      <catastrophic_reason>If architectural rules or KI guidelines are not loaded, the agent will accidentally refactor code back to the V1-legacy state, destroying the Desktop UI performance.</catastrophic_reason>
    </rule_block>
  </context_rules>

  <phases>
    <phase id="1" name="Mapping">
Your first task is to use tools (e.g. directory listing) to understand the depth of the directory structure.
* If the user provides a specific sub-path in their command (e.g. `client_app_v2/lib/features/studio`), map the STRUCTURE ONLY FROM THIS PATH downwards. If no sub-path is specified, map the entire `client_app_v2/lib`.
* **SPECIAL RULE FOR SINGLE FILES:** If the user specifies an exact file or files in their command (e.g. `client_app_v2/lib/main.dart`), map a list **Only of these individual files**. Do not expand the audit to the entire directory.
* **ABSOLUTE BAN (Ignored files):** Completely ignore all files created by code generators (ending in `.g.dart` or `.freezed.dart`) in your analysis. Also ignore `build/` and `.dart_tool/` folders. Do not read, audit, or attempt to modify them to save resources and prevent false correction suggestions.
* **RULE:** Build a virtual Markdown checklist (`task_front.md`) to be printed in the chat from your findings. Subdivide the list so finely that **EVERY lowest-level subdirectory (leaf directory) OR in the case of specified individual files, EVERY single file is its own separate item on the list**. Directories must not be bundled together.
* **STATE PERSISTENCE & CONTEXT RENEWAL:** If the user's command contains `--resume` or the file `c:\src\quorum\tmp\hardening_state.json` exists, read it. Omit from the list any directories that are marked as "DONE" there. Bring the list of only undone directories. At the same time, set a local goal: "I will process a maximum of 10 files in this session to prevent context degradation."
* **BAN:** DO NOT make code changes at this stage. Always end your response with the words: *"List ready. Awaiting PROCEED command."*
    </phase>
    
    <phase id="2" name="Auditing (Systematic Audit, One Subdirectory At A Time)">
When I give permission to proceed ("PROCEED"), we will begin unpacking the virtual list:
1. Select the FIRST undone subdirectory OR single file from the list.
2. Strictly read the `.dart` files of that target (or just that specific file), keeping ignored folders/files in mind. Define the audit matrix to cover ONLY the selected scope.
3. **MANDATED TRACEABILITY MATRIX**: You MUST report your findings by printing a precise Markdown table ("Audit Matrix") into the chat. You MUST parse the content of `c:\src\quorum\.agents\rules\00-antigravity-core.md` and `c:\src\quorum\.agents\rules\02_flutter_desktop.md` in your mind and create a row in the matrix **for every `<rule_block>` present in the files**.
   **Special Note 1:** Make sure you do not let any Dart null-coalescing (`?? 'default'`) shortcuts or `.maybeWhen` fallbacks that hide structural errors pass the "the_zero_compromise_pledge" check. Old things must not be supported! This applies to ALL fallback mechanisms (no "or" chains, no `.maybeWhen` or feeding default values with missing data). Legacy code and duct-tape fixes are not tolerated. **Special Note 2:** `frontend_zero_db_hardcoding_mandate` requires checking that no UI component or controller assumes ID identifiers, names, or index orders of specific database tables in the code. **Special Note 3:** `dropdown_database_alignment` requires ensuring that all Dropdowns category and filtering conditions are completely synchronized with the database and `enums.dart` definitions (using `PromptBlockCategoryGroups` groups) without hacky solutions or UI-level bypasses.
   - Use columns: `| No. | Rule ID | Status (Pass / Fail) | Findings & Justification |`.
   - Ensure that you truly go through things from the code point by point against the &lt;banned_pattern&gt; and &lt;mandatory_pattern&gt; constraints. This eliminates hallucinations and skips.

    <critical_anti_laziness_mandate>
      BAN: Condensing the Audit Matrix, merging rows, or omitting rules is STRICTLY FORBIDDEN (Anti-Laziness Mandate). 
      You MUST print a row in the table for EVERY `<rule_block>` in the `02_flutter_desktop.md` (and core) file, even if it is "Pass" or "NA". 
      If any rule is missing from the table, you directly violate the main architecture rules of the system. Every Phase 9 rule must be gone through explicitly to force your own attention mechanism to check the code for that rule.
    </critical_anti_laziness_mandate>

4. Stop after printing the table. I expect to see it. Wait for the command "FIX" (if things need to be fixed) or the command "NEXT" (if all rules were purely Pass). If "FIX" requires destroying files or critical UI components (Destructive Operations), you MUST ask for separate permission from the user before deleting.
5. **STATE PERSISTENCE:** When the folder is complete (meaning you received the command to fix and you fixed, OR it was clean immediately), update `c:\src\quorum\tmp\hardening_state.json` IMMEDIATELY and mark this subdirectory as "DONE".
6. **SESSION LIMIT & HANDOVER:** If you have processed (audited) a total of 10 files in THIS session, STOP immediately. Print to the user: "Session limit reached. Continue by issuing the command: `/tier2-hardening-frontend --resume`" and ensure that the master task document (e.g. `task.md`) is updated before closing.
    </phase>
    
    <critical_remediation_protocol name="STEP 3 - FIX (Remediation Phase)">
      <step id="1">RED-GREEN-REFACTOR MANDATE: If you received the command to fix code ("FIX"), you must FIRST update or create a test (e.g. widget test or unit test) that fails with the current broken code. Only after the test fails do you make the code changes (Fail-Fast). Use your structural editing tools to fix the code.</step>
      <step id="2">AUDIT LOOP EXECUTION: NEVER attempt to run random commands yourself with the `run_command` tool (e.g. `flutter gen-l10n` is forbidden in the sandbox). You MUST run quality assurance testing after code changes: `uv run python scripts/flutter_audit_loop.py client_app_v2/[path]`. Use the `--build` flag only if `@riverpod` or `@freezed` models were modified.</step>
      <step id="3">DOCUMENTATION AUDIT MANDATE: If the refactoring caused significant architectural changes to the UI structure, file deletions, or the creation of new directories, you MUST physically modify the documents in the `c:\src\quorum\docs\architecture\` directory and the `c:\src\quorum\.agents\rules\04_directory_reference.md` file, strictly maintaining their existing table structures. Never just put a comment "Updated", physically modify the files.</step>
    </critical_remediation_protocol>
  </phases>
</system_prompt>
```
