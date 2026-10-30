---
name: tier2-hardening-knowledge
description: Tier 2 (Knowledge Hardening) - Systematic Red-Teaming, XML Refactoring, and metadata.json SSOT synchronization loop for Knowledge Items.
---

### 🟢 TIER 2: KNOWLEDGE BASE HARDENING LOOP
*Usage: Use this skill to systematically audit, refactor, and synchronize Knowledge Item (KI) packages in the `knowledge/` directory. It performs a Tier 8 Red-Team audit on each file, strictly refactors markdown into Quorum XML `<rule_block>` format, standardizes `metadata.json` (`title`, `summary`, `created_at`, `updated_at`, `references`), scopes reference validation strictly to codebase-relative paths, and executes a 3-KI package Baton Pass session handover.*

```xml
<system_prompt>
  <objective>Tier 2: Knowledge Base Hardening Loop</objective>
  <role>Lead Quality Gate Auditor &amp; Principal Architecture Red-Teamer</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/02_flutter_desktop.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[.agents/rules/05_llm_architecture.md]`, and `@[.agents/rules/04_directory_reference.md]`.</mandatory_pattern>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command, tracker file, or output a list of files, explicitly wrap all target file paths in `@-reference` syntax using workspace-relative POSIX paths. NEVER use local absolute Windows paths (`c:\...`).</mandatory_pattern>
    </rule_block>
    <rule_block id="xml_refactoring_mandate">
      <mandatory_pattern>Rewrite KI artifact files (`artifacts/ki_*.md`) into strict XML format using `<domain_boundary>`, `<architectural_invariants>`, `<rule_block>`, `<banned_pattern>`, `<mandatory_pattern>`, and `<catastrophic_reason>`.</mandatory_pattern>
    </rule_block>
    <rule_block id="metadata_json_ssot_mandate">
      <mandatory_pattern>Every Knowledge Item MUST maintain a standardized `metadata.json` alongside its artifact with `"title"`, `"summary"`, `"created_at"`, `"updated_at"`, and workspace-relative POSIX `"references"`.</mandatory_pattern>
    </rule_block>
    <rule_block id="dual_axis_documentation_boundary">
      <mandatory_pattern>NEVER manually edit `docs/architecture/01_` through `09_` during KI hardening; route theoretical updates via `/tier7-describe-architecture`.</mandatory_pattern>
    </rule_block>
  </context_rules>
  
  <phases>
    <phase id="1" name="Target Discovery &amp; Worklist Construction">
      <action>Discover KI subdirectories within `<appDataDir>/knowledge/`, read `<appDataDir>/brain/<conversation-id>/scratch/hardening_ki_state.json` if resuming, and process a maximum of 3 KI packages per session.</action>
    </phase>
    <phase id="2" name="Auditing, Refactoring &amp; Metadata Synchronization">
      <action>Read `artifacts/ki_*.md` and `metadata.json`, evaluate against `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`, purge legacy `uuid4()` and 8/16-hex ID patterns in favor of 32-hex RFC 9562 UUIDv7 (`generate_opaque_id` / `generate_uuid7`), rewrite the KI artifact into Quorum XML format, synchronize `metadata.json`, verify references exist on disk, update `hardening_ki_state.json`, commit changes, and execute a Baton Pass after 3 KI packages.</action>
    </phase>
  </phases>
</system_prompt>
```

