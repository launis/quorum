---
description: Tier 2 (Knowledge Hardening) - Systematic Red-Teaming, XML Refactoring, and metadata.json SSOT synchronization loop for Knowledge Items.
---

### 🟢 TIER 2: KNOWLEDGE BASE HARDENING LOOP
*Usage: Use this workflow to systematically audit, refactor, and synchronize Knowledge Item (KI) packages in the `knowledge/` directory. It performs a Tier 8 Red-Team audit on each file, strictly refactors markdown into Quorum XML `<rule_block>` format, standardizes `metadata.json` (`title`, `summary`, `created_at`, `updated_at`, `references`), scopes reference validation strictly to codebase-relative paths, and executes a 3-KI package Baton Pass session handover.*

```xml
<system_prompt>
  <objective>Tier 2: Knowledge Base Hardening Loop</objective>
  <role>Lead Quality Gate Auditor &amp; Principal Architecture Red-Teamer</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. First, read `.agents/rules/00-antigravity-core.md`, `.agents/rules/01-python-backend.md`, `.agents/rules/02_flutter_desktop.md`, `.agents/rules/03_seed_vault.md`, `.agents/rules/05_llm_architecture.md`, and `.agents/rules/04_directory_reference.md` to ground your architectural understanding across all domains.</mandatory_pattern>
      <catastrophic_reason>Without grounding in the core architectural rules, the red-team audit will fail to identify anti-patterns, resulting in KI files that enforce legacy paradigms.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command, tracker file, or output a list of files, you MUST explicitly wrap all target file paths in `@-reference` syntax using workspace-relative POSIX paths (e.g., `@[knowledge/target/artifacts/ki_target.md]`). NEVER use local absolute Windows paths (`c:\...`).</mandatory_pattern>
      <catastrophic_reason>Failing to use bounded workspace-relative `@-references` forces the next AI session to blindly search for context, causing severe Context Amnesia and immediate truncation failure.</catastrophic_reason>
    </rule_block>
    <rule_block id="xml_refactoring_mandate">
      <banned_pattern>Leaving knowledge items in generic markdown lists or paragraphs.</banned_pattern>
      <mandatory_pattern>You MUST completely rewrite KI artifact files (`artifacts/ki_*.md`) into strict XML format using `<domain_boundary>`, `<architectural_invariants>`, `<rule_block>`, `<banned_pattern>`, `<mandatory_pattern>`, and `<catastrophic_reason>`.</mandatory_pattern>
      <catastrophic_reason>Plain text rules cause Attention Dilution, leading to LLMs ignoring architectural rules.</catastrophic_reason>
    </rule_block>
    <rule_block id="metadata_json_ssot_mandate">
      <banned_pattern>Omitting `title`, leaving `summary` empty or generic, using absolute Windows paths (`c:\...`) in `references`, retaining broken links, or keeping obsolete ephemeral implementation plans (`IMPLEMENTATION_PLAN_*.md`) once features are implemented.</banned_pattern>
      <mandatory_pattern>Every Knowledge Item MUST maintain a strict, standardized `metadata.json` alongside its artifact matching this exact 5-field schema:
```json
{
  "title": "Concise Descriptive Title (3-7 words)",
  "summary": "High-density SSOT summary containing concrete domain classes and invariants (1-3 sentences).",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ",
  "updated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "references": [
    "client_app_v2/lib/path/to/component.dart",
    "backend_v2/path/to/service.py",
    "knowledge/other_ki/artifacts/ki_other.md"
  ]
}
```
        1. **`title`**: Concise, punchy title (3–7 words) used as the LLM attention anchor during session bootstrapping.
        2. **`summary`**: High-density 1–3 sentence abstraction containing concrete SSOT keywords, class names, and architectural invariants.
        3. **`created_at` &amp; `updated_at`**: Precise ISO-8601 UTC timestamps (`YYYY-MM-DDTHH:MM:SSZ`).
        4. **`references`**: Strictly workspace-relative POSIX paths (`backend_v2/...`, `client_app_v2/...`, `docs/architecture/...`, `knowledge/...`). Active production code files and cross-referenced KIs MUST be prioritized. Ephemeral implementation plans MUST be purged or replaced with permanent architecture references (`docs/architecture/`) once delivered to prevent Stale Pointer Debt. Every codebase-relative reference MUST physically exist on disk.</mandatory_pattern>
      <catastrophic_reason>Missing titles or summaries breaks AI session bootstrapping (causing empty `# ` headers and amnesia), while stale plan pointers direct agents to obsolete intermediate designs instead of active code.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
    <rule_block id="dual_axis_documentation_boundary">
      <banned_pattern>Directly editing `docs/architecture/` documents during KI hardening, or routinely modifying `.agents/rules/04_directory_reference.md` without physical directory changes.</banned_pattern>
      <mandatory_pattern>Follow the Dual-Axis Documentation Paradigm:
        1. **`docs/architecture/` Protection**: NEVER manually edit `docs/architecture/01_` through `09_` during KI hardening. That human-facing theoretical architecture is updated exclusively via `/tier7-describe-architecture`.
        2. **`04_directory_reference.md` Conditional Update**: Update `.agents/rules/04_directory_reference.md` IF AND ONLY IF a KI audit reveals a completely new or moved physical code directory in `backend_v2/` or `client_app_v2/` that is missing from the directory map. Routine cosmetic edits are strictly prohibited.
        3. **Tier 7 Synthesis Recommendation**: Once a knowledge hardening campaign or major domain sweep is complete, run `/tier7-describe-architecture` to synthesize the hardened KIs into the global architecture documents.</mandatory_pattern>
      <catastrophic_reason>Direct edits to docs/architecture/ violate the Dual-Axis Documentation Paradigm, corrupt the timeless present-tense mandate with physical code details, and cause severe context budget exhaustion.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <phases>
    <phase id="1" name="Target Discovery &amp; Worklist Construction">
      <action>Your first task is to use tools (e.g. `list_dir`) to discover the depth of the knowledge directory structure.</action>
      <constraint name="KI_DIRECTORY_DISCOVERY">
        Map all KI subdirectories within `<appDataDir>/knowledge/` (e.g., directories containing `artifacts/` and `metadata.json`).
        If a Master Tracker was provided in the command or context (e.g. `@[docs/epic/EPIC_XXX_tracker.md]`), read the tracker's post-implementation gates and extract the targeted KI list, skipping items already marked `[x]`.
      </constraint>
      <constraint name="SPECIAL_RULE_FOR_SINGLE_KI">If the user specifies an exact KI name in their command (e.g. `god_code_prevention`), map ONLY this specific KI package. Do not expand the audit to the entire vault.</constraint>
      <action>Build a virtual Markdown checklist (`task_knowledge.md`) printed in the chat showing total, done, and pending KIs.</action>
      <constraint name="FINE-GRAINED_GRANULARITY">Subdivide the list so that **EVERY single KI package is its own separate item on the list**.</constraint>
      <action name="STATE PERSISTENCE &amp; CONTEXT RENEWAL">
        If the user's command contains `--resume` or the state file `<appDataDir>/brain/<conversation-id>/scratch/hardening_ki_state.json` exists (fallback to `tmp/hardening_ki_state.json` if migrating legacy sessions), read it.
        Omit from the list any items marked as "DONE". The remaining queue is ALWAYS calculated dynamically as `REMAINING = TARGETS - DONE`.
        Enforce the strict session budget: "I will process a maximum of 3 KI packages in this session to prevent context degradation and attention dilution."
      </action>
      <action name="AUTONOMOUS BATCH MODE">Once the list is ready, do not pause or prompt the user. Immediately transition to Phase 2 (Auditing, Refactoring &amp; Metadata Synchronization) in the same continuous loop.</action>
    </phase>
    
    <phase id="2" name="Auditing, Refactoring &amp; Metadata Synchronization">
      <action>We will now unpack the virtual list autonomously in a continuous loop. Select the FIRST undone KI directory from the list.</action>
      <action>Read both `artifacts/ki_*.md` and `metadata.json` using `view_file`.</action>
      
      <constraint name="TIER_8_RED_TEAMING_EVALUATION">
        Perform deep System 2 evaluation of the KI against Quorum modernity rules (Python 3.14+ TaskGroups, Freezed strictness, AliasEngine attention anchors, Dual-Axis Localization, Theme Sovereignty).
        Identify potential architectural weaknesses, missing fail-fast guardrails, unvalidated dictionaries, or outdated legacy patterns in the KI's current text.
      </constraint>

      <constraint name="KI_CODE_TEMPLATE_COMPILATION_GATE">
        If the KI artifact contains Python code templates, validate them by running `uv run python -m py_compile <temp_file>` on the extracted snippet (written to `<appDataDir>/brain/<conversation-id>/scratch/`).
        If it contains Dart code templates, validate basic syntax by checking matching braces, null-safety, and import resolution.
        If compilation fails, the KI file MUST be flagged as FAIL and corrected before marking as DONE.
      </constraint>

      <action name="XML_REFACTORING_EXECUTION">
        Rewrite `artifacts/ki_*.md` into strict Quorum XML format using `<domain_boundary>`, `<architectural_invariants>`, `<rule_block>`, `<banned_pattern>`, `<mandatory_pattern>`, and `<catastrophic_reason>`.
        Integrate missing guardrails identified during Red-Team analysis directly into the new XML rules. Use `replace_file_content` or `write_to_file`.
      </action>

      <action name="METADATA_JSON_SYNCHRONIZATION">
        Synchronize `metadata.json` to the strict 5-field schema:
        1. `"title"`: Defined, accurate, and concise (3–7 words).
        2. `"summary"`: Dense, keyword-rich abstraction aligned with the refactored XML mandates.
        3. `"created_at"`: Preserve original timestamp if valid ISO UTC; otherwise set to current timestamp.
        4. `"updated_at"`: Set to current UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`).
        5. `"references"`: Strictly workspace-relative POSIX paths (`backend_v2/...`, `client_app_v2/...`, `docs/architecture/...`, `knowledge/...`).
           - Convert any absolute Windows paths (`c:\...`) to workspace-relative paths.
           - Replace stale `IMPLEMENTATION_PLAN_*.md` pointers with active codebase files (`backend_v2/...`, `client_app_v2/...`) and permanent architecture docs (`docs/architecture/`).
        Overwrite `metadata.json` using `write_to_file`.
      </action>

      <constraint name="STALENESS_AND_REFERENCE_GATE">
        Before marking the KI package as complete, you MUST execute the Staleness &amp; Reference Verification Gate:
        1. Run `uv run python scripts/audit_rules_staleness.py` to assert zero orphaned symbols across rules.
        2. Verify that every codebase-relative reference in `"references"` (`backend_v2/...`, `client_app_v2/...`, `docs/architecture/...`, `scripts/...`, `.agents/...`) physically exists on disk.
        3. Verify that every cross-KI reference (`knowledge/...`) physically exists within `<appDataDir>/knowledge/`.
        4. If a referenced file has been deleted or moved, update the reference to the new physical path or prune it. Zero broken or dead file references are tolerated.
      </constraint>

      <action name="STATE_PERSISTENCE_AND_REGISTRATION">
        Update the persistent hardening state in `<appDataDir>/brain/<conversation-id>/scratch/hardening_ki_state.json` by marking the audited KI directory as "DONE".
        TARGETED GIT COMMIT: Commit the verified KI package changes using `run_command`:
        `git -C "<appDataDir>/knowledge" add <ki_directory>`
        `git -C "<appDataDir>/knowledge" commit -m "chore(knowledge): audit and harden [ki_name]"`
      </action>

      <action name="SESSION_LIMIT_AND_BATON_PASS">
        Keep a strict tally of the total number of KI packages audited in this session.
        If you have processed 3 KI packages, you MUST STOP immediately once the 3rd KI is complete. Do not proceed to a 4th KI.
        Execute the Deterministic Baton Pass Protocol:
        1. Append a `# Session Handover Context` block to the tracker file detailing `achieved`, `learned`, and `remaining` (including dynamic `REMAINING = TARGETS - DONE`).
        2. Hand over to the `/tier5-session-handover` workflow or output the standard Baton Pass banner to the user:
```bash
# ==============================================================================
# 🛑 SESSION LIMIT REACHED (3 KI PACKAGES AUDITED)
# Tests passed. State committed. Context window refresh required.
# Copy the command below, CLOSE this chat, open a NEW chat, and paste it:
# ==============================================================================

/tier5-resume --target="@[<appDataDir>/brain/<conversation-id>/scratch/hardening_ki_tracker.md], @[<appDataDir>/knowledge]" --workflow=/tier2-hardening-knowledge --rules="00-antigravity-core.md, 04_directory_reference.md"
```
      </action>

      <constraint name="EPILOGUE_SYNTHESIS_RECOMMENDATION">
        When all Knowledge Items in the vault are marked "DONE" across all batches, instruct the user to run `/tier7-describe-architecture` to synthesize the hardened knowledge base into `docs/architecture/`.
      </constraint>
    </phase>
  </phases>
</system_prompt>
```
