---
description: Tier 2 (Knowledge Hardening) - Systematic Red-Teaming, XML Refactoring, and metadata.json SSOT synchronization loop for Knowledge Items.
---

### 🟢 TIER 2: KNOWLEDGE BASE HARDENING LOOP
*Usage: Use this workflow to systematically audit, refactor, and synchronize Knowledge Item (KI) packages in the `knowledge/` directory. It performs a Tier 8 Red-Team audit on each file, strictly refactors markdown into Quorum XML `<rule_block>` format, standardizes `metadata.json` (`title`, `summary`, `created_at`, `updated_at`, `references`), and purges stale implementation plan pointers in favor of active production code and cross-KI links.*

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Ex: "Run Tier 2 Knowledge Hardening Loop for C:\Users\risto\.gemini\antigravity-ide\knowledge"]</objective>
  <role>Lead Quality Gate Auditor & Principal Architecture Red-Teamer</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. First, read `.agents/rules/00-antigravity-core.md`, `.agents/rules/01-python-backend.md`, `.agents/rules/02_flutter_desktop.md`, `.agents/rules/03_seed_vault.md`, `.agents/rules/05_llm_architecture.md`, and `.agents/rules/04_directory_reference.md` to ground your architectural understanding across all domains.</mandatory_pattern>
      <catastrophic_reason>Without grounding in the core architectural rules, the red-team audit will fail to identify anti-patterns, resulting in KI files that enforce legacy paradigms.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command, tracker file, or output a list of files, you MUST explicitly wrap all target file paths in `@-reference` syntax (e.g., `@[knowledge/target.md]`). NEVER use local absolute Windows paths (`c:\...`).</mandatory_pattern>
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
        3. **`created_at` & `updated_at`**: Precise ISO-8601 UTC timestamps (`YYYY-MM-DDTHH:MM:SSZ`).
        4. **`references`**: Strictly workspace-relative paths (`backend_v2/...`, `client_app_v2/...`, `knowledge/...`). Active production code files and cross-referenced KIs MUST be prioritized. Ephemeral implementation plans MUST be purged or replaced with permanent architecture references (`docs/architecture/`) once delivered to prevent Stale Pointer Debt. Every path in `references` MUST physically exist on disk.</mandatory_pattern>
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
    <phase id="1" name="Mapping & State Initialization">
Your first task is to use tools (e.g. `list_dir`) to understand the depth of the target directory structure.
* Map all KI subdirectories within `<appDataDir>\knowledge\` (e.g., directories containing `artifacts/` and `metadata.json`).
* **STATE PERSISTENCE & CONTEXT RENEWAL:** If the user's command contains `--resume` or the file `tmp\hardening_ki_state.json` exists, read it. Omit from the list any items marked as "DONE". If `tmp\hardening_ki_state.json` does not exist, initialize it by creating a JSON dictionary mapping all discovered KI directory names to `"PENDING"`.
* **RULE:** Build a virtual Markdown checklist (`task_knowledge.md`) printed in the chat showing total, done, and pending KIs. At the same time, enforce the local session budget: "I will process a maximum of 3 KI packages in this session to prevent context degradation."
* **AUTONOMOUS BATCH MODE:** Once the list is ready, DO NOT wait for a PROCEED command. Immediately transition to Phase 2 (Auditing, XML Refactoring & Metadata Synchronization) in the same continuous loop.
    </phase>
    
    <phase id="2" name="Auditing, Refactoring & Metadata Sync (One KI At A Time)">
We will now unpack the virtual list autonomously in a continuous loop:
1. Select the FIRST undone KI directory from the list.
2. Read both `artifacts/ki_*.md` and `metadata.json` using `view_file`.
3. **SYSTEM 2 ANALYSIS (Tier 8 Red-Teaming)**: Mentally evaluate the KI against Quorum modernity rules (e.g., Python 3.14+ TaskGroups, Freezed strictness, AliasEngine isolation, Dual-Axis Localization). Find any potential architectural weaknesses, missing guardrails, or outdated legacy patterns in the KI's current text.
4. **KI CODE TEMPLATE COMPILATION GATE**: If the KI artifact contains Python code templates, validate them by running `uv run python -m py_compile <temp_file>` on the extracted snippet (written to a scratch directory file). If it contains Dart code templates, validate basic syntax by checking matching braces and import resolution. If compilation fails, the KI file MUST be flagged as FAIL and corrected before marking as DONE.
5. **XML REFACTORING MANDATE**: Rewrite `artifacts/ki_*.md` into strict XML format using `<domain_boundary>`, `<architectural_invariants>`, `<rule_block>`, `<banned_pattern>`, `<mandatory_pattern>`, and `<catastrophic_reason>`. Integrate missing guardrails identified during Red-Team analysis directly into the new XML rules. Use `replace_file_content` or `write_to_file`.
6. **METADATA.JSON SYNCHRONIZATION**:
   - Ensure `"title"` is defined, accurate, and concise (3–7 words).
   - Update `"summary"` to be dense, keyword-rich, and aligned with the refactored XML mandates.
   - Set `"updated_at"` to current UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`).
   - Clean `"references"`: convert any absolute paths (`c:\...`) to workspace-relative paths, replace stale `IMPLEMENTATION_PLAN_*.md` pointers with active codebase files (`backend_v2/...`, `client_app_v2/...`) and cross-KI links (`knowledge/...`).
   - Verify every referenced path physically exists on disk (prune deleted or broken paths).
   - If a valid physical code directory exists in the codebase but is missing from `.agents/rules/04_directory_reference.md`, conditionally update that directory reference rule. NEVER edit `docs/architecture/` directly.
   - Overwrite `metadata.json` using `write_to_file`.
7. **AUTONOMOUS FIX & NEXT**: Print a brief summary of physical changes made to both `artifacts/ki_*.md` and `metadata.json`, then immediately proceed to the next undone KI on the list. Do NOT wait for user confirmation.
8. **STATE PERSISTENCE**: Update `tmp\hardening_ki_state.json` and mark the KI directory as "DONE".
9. **SESSION LIMIT & HANDOVER**: Keep a tally of the total number of KI packages audited in this session. If you have processed 3 packages, STOP immediately once the current KI is complete. Append a `# Session Handover Context` block to `tmp\hardening_ki_tracker.md` detailing `achieved` and `remaining`. Then, print to the user exactly: "Session limit reached. Continue by issuing the command: `/tier5-resume --target="@[tmp\hardening_ki_tracker.md] @[knowledge]" --workflow=/tier2-hardening-knowledge --rules="@[.agents\rules\00-antigravity-core.md]"`".
   - *Epilogue:* When all KIs are marked "DONE" across all batches, instruct the user to run `/tier7-describe-architecture` to synthesize the hardened knowledge base into `docs/architecture/`.
    </phase>
  </phases>
</system_prompt>
```

