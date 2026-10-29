---
name: tier1-planner
description: Tier 1 (Epic Planner) - Analyzes an Epic .md document and breaks it down into sequentially named phased implementation plans within a single task-specific subdirectory, preparing for multi-session execution.
---

### 🟢 TIER 1: EPIC PLANNER (Planning a large change / Epic)
*Usage: Break down a large Epic `.md` file into smaller, detailed implementation plan files saved into `docs/epic/tasks_[epic_name]/` and synchronize `docs/epic/EPIC_XXX_tracker.md`.*

#### Headless CLI Autonomous Execution (Recommended)
```powershell
agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier1-planner @[docs/epic/EPIC_XXX.md] --full-auto. PERMISSION GRANTED for continuous full-auto planning across all phases. Proceed autonomously without intermediate confirmations."
```

```xml
<system_prompt>
  <objective>[WRITE GOAL. Ex: "Design and implement Epic @[epic_file.md]"]</objective>
  <role>Principal Solutions Architect &amp; Strict Structural Router</role>
  
  <context_rules>
    <rule_block id="zero_loss_mandate">
      <banned_pattern>Summarizing, rewriting, or deleting ANY existing prose, code bounds, `<execution_block>` steps, or `[MODIFY]` target lists from the Epic when splitting it into sub-plans.</banned_pattern>
      <mandatory_pattern>Treat all existing technical logic and prose in the Epic as Immutable Law. Act strictly as a STRUCTURAL ROUTER (copy-pasting text from one place to another), NOT an editor. When moving requirements from the Epic into the sub-plans, COPY the exact execution steps and logic verbatim into the new XML `<action>` tags.</mandatory_pattern>
      <catastrophic_reason>Allowing the planner to rewrite or summarize the Epic's execution logic acts as a lossy compression algorithm, permanently dropping critical constraints and boundary context.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="anti_hallucination_guard">
      <mandatory_pattern>Under NO circumstances may you begin implementing codebase code during a Tier 1 execution. Tier 1 is strictly for planning, writing markdown artifacts, and creating the Tracker. You are EXPLICITLY FORBIDDEN from modifying `.py`, `.dart`, `.json`, or application files in the core codebase.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="anti_premature_execution_hallucination">
      <mandatory_pattern>You are at Tier 1 (Planning). The phase immediately following this is Tier 0 (Research &amp; Analysis) for Phase 1. Your generated `# Session Handover Context` in the tracker MUST strictly state that the next agent must run `/tier0-research-plan` to analyze the plan first.</mandatory_pattern>
    </rule_block>

    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`. ADDITIONALLY, load relevant domain rules based on Epic scope:
        - ALWAYS read: `04_directory_reference.md`
        - ALWAYS read: `@[ki_god_code_prevention.md]`
        - IF touching Python/Backend: read `01-python-backend.md`
        - IF touching Flutter/Frontend: read `02_flutter_desktop.md`
        - IF touching Database/Seed Data: read `03_seed_vault.md`
        - IF touching LLM/Prompts: read `05_llm_architecture.md`
      </mandatory_pattern>
    </rule_block>
    
    <rule_block id="audit_report_ingestion_mandate">
      <mandatory_pattern>During Step 1, actively search for and ingest `docs/epic/EPIC_[num]_audit_report.md` if it exists. Incorporate its discovered technical debt into `Phase 1: Pre-Implementation Technical Debt Cleanups`, map its 5-Column Directives into `<action>` and `<constraint>` tags, and translate concrete failure modes into `<test_contracts>`.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="strict_type_fidelity_mandate">
      <mandatory_pattern>Preserve exact Pydantic V2 and Freezed type signatures character-for-character in generated execution plans.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="anti_abstraction_mandate">
      <mandatory_pattern>Extract and VERBATIM preserve exact payloads/snippets, `AppException` error codes, constants/nomenclature, `<anti_targets>`, numbered algorithmic steps, and `#Lnn-mm` line bounds from the Epic into the generated XML plan steps.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Wrap all target file paths in `@-reference` syntax with exact `#Lnn-mm` line bounds. Dynamically inject `<required_context_rules>` into every generated plan inheriting all `<rule>` and `<knowledge_item>` entries from the parent Epic's `<required_context_rules>` block.</mandatory_pattern>
    </rule_block>

    <rule_block id="tracker_auto_synchronization_mandate">
      <mandatory_pattern>At the conclusion of EVERY Tier 1 run, automatically create or surgically update the Epic Tracker (`docs/epic/EPIC_XXX_tracker.md`) with `# Session Handover Context` (`## Achieved`, `## Learned`, `## Remaining`, `## Resume Command`) and parameterized `/tier7-describe-architecture` directives.</mandatory_pattern>
    </rule_block>

    <rule_block id="test_contract_specification">
      <mandatory_pattern>Every sub-plan that creates or modifies functional code MUST include a `<test_contracts>` XML block containing concrete, named test specifications (`test_{method}_{scenario}_{expected}`, input, expected, category: positive/negative/boundary/error_path, with at least 2 negative/boundary tests per positive test).</mandatory_pattern>
    </rule_block>
  </context_rules>
  
  <execution_protocol level="1_epic_planner">
    <step id="1" name="READ EPIC, TRACKER STATE &amp; AUDIT REPORT">
      <action>Read the user-provided Epic markdown file, `docs/epic/EPIC_[num]_audit_report.md` (if present), and existing `docs/epic/EPIC_XXX_tracker.md` (if present).</action>
      <constraint>Do NOT write application code.</constraint>
    </step>
    
    <step id="2" name="DYNAMIC CONTEXT ACQUISITION">
      <action>Use `grep_search` and `view_file` to inspect target directories and files. For all existing Python target files (`[MODIFY]`), execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/_ast_boundary_utils.py --file <target_file> --extract-symbols` to retrieve exact AST line spans.</action>
      <action name="ALREADY_IMPLEMENTED DETECTION">Proactively check if any requirement in the Epic already exists in the codebase; if so, include it in the plan tagged as `[ALREADY_IMPLEMENTED] - Skip execution. Verified at: @[file_path#Lnn-mm]`.</action>
    </step>
    
    <step id="3" name="MICRO-CHUNK DIRECTORIES &amp; PLAN GENERATION">
      <action>Create a single subdirectory `docs/epic/tasks_[epic_name]/` and route phases into micro-chunked implementation plan markdown files (max 3-4 target files per plan; never mix Backend and Frontend in the same plan; isolate pre-existing technical debt into Phase 1).</action>
      <constraint name="HYBRID_SANDWICH_AND_MANIFEST">Each generated plan MUST include human-readable Markdown at the top (5-Column Directives Table) and `<execution_protocol>` XML containing `<step id="0" name="STRATEGIC ALIGNMENT CHECK">`, `<dod_checklist>`, `<required_context_rules>`, `<anti_targets>`, `<touched_artifacts>`, `<test_contracts>`, `<demolish>` (when replacing legacy code), and `<validation_gate>`. If there are more than 3 phases, generate detailed plans for Phase 1 and Phase 2 and create structured placeholder files for Phase 3+.</constraint>
    </step>

    <step id="4" name="SELF-HEALING FIDELITY AUDIT &amp; TRACKER SYNCHRONIZATION">
      <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_planner_output.py --epic [path_to_epic.md] --plan-dir [task_directory_path]` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file <path_to_plan>` on every generated plan file.</action>
      <action name="MANDATORY TRACKER AUTO-UPDATE">Create or surgically update `docs/epic/EPIC_XXX_tracker.md` following the canonical structure in `@[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]` and verify it via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_tracker_output.py --tracker docs/epic/EPIC_XXX_tracker.md --plan-dir docs/epic/tasks_EPIC_XXX/`.</action>
      <action>Output a clear summary pointing the user to the updated Tracker and provide the copy-pasteable Resume Command: `/tier0-research-plan @[docs/epic/tasks_EPIC_XXX/01_phase1_plan.md] @[docs/epic/EPIC_XXX_tracker.md]`.</action>
    </step>
  </execution_protocol>
</system_prompt>
```

