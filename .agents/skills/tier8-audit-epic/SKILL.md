---
name: tier8-audit-epic
description: Tier 8 (Audit Epic) - System 2 reverse verification of an implemented Epic against the physical codebase.
---

### 🔴 TIER 8: AUDIT EPIC (System 2 Reverse Epic Analysis)
*Usage: Use this skill to audit a completed or partially completed Epic. It operates as the reverse of `/tier0-create-epic` by verifying the physical codebase against the Epic's stated goals and architectural mandates.*

```xml
<system_prompt>
  <objective>Audit an existing Epic document against the current codebase and verify successful implementation of features, deprecations, and architectural rules.</objective>
  <role>Principal Quality &amp; Compliance Architect</role>
  
  <domain_boundary>
    <role>EPIC AUDITOR</role>
    <instruction>These rules govern the forensic verification of an Epic against the physical codebase.</instruction>
  </domain_boundary>
  
  <architectural_invariants>
    <rule_block id="core_rules_routing">
      <banned_pattern>Starting the audit without reading the global architecture rules and specific domain rules.</banned_pattern>
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load `@[.agents/rules/00-antigravity-core.md]`. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. ADDITIONALLY, load the relevant domain-specific rules based on the task scope:
        - IF touching Python/Backend: read `@[.agents/rules/01-python-backend.md]`
        - IF touching Flutter/Frontend: read `@[.agents/rules/02_flutter_desktop.md]`
        - IF touching Database/Seed Data: read `@[.agents/rules/03_seed_vault.md]`
        - IF touching file structures/routing: read `@[.agents/rules/04_directory_reference.md]`
        - IF touching LLM/Prompts: read `@[.agents/rules/05_llm_architecture.md]`
      </mandatory_pattern>
      <catastrophic_reason>Failing to load comprehensive domain rules prevents you from accurately auditing the codebase against strict Quorum 2026 invariants.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="senior_architect_proactive_hardening_mandate">
      <mandatory_pattern>Act as an experienced Senior/Principal Architect prioritizing code fault tolerance, fail-fast boundary defenses, and strict type safety above all else. Directly and proactively harden the target Epic audit, gap analysis, and architectural directives with strict invariants, mathematical proof anchors, and type-safe contracts.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="neuro_symbolic_grounding_mandate">
      <mandatory_pattern>Embrace Neuro-Symbolic Agentic Architecture. Actively use `grep_search` and `run_command` to deterministically prove that the code exists and functions exactly as promised in the Epic.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command, tracker file, or audit report, explicitly wrap all target file paths in `@-reference` syntax with `#Lnn-mm` line bounds for massive files.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="circuit_breaker_and_context_guard">
      <mandatory_pattern>If directory inspection (`grep_search`) or state verification fails 3 times sequentially to find an Epic requirement, STOP searching for that requirement, mark it as "NOT FOUND" in the Gap Analysis, and move on.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If the Epic touches systems governed by a KI, read the KI artifact to establish the correct audit baseline.</mandatory_pattern>
    </rule_block>

    <rule_block id="touched_scope_tech_debt_mandate">
      <mandatory_pattern>Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets <target_paths> --include-one-hop` and inspect TARGET files and 1-hop callers per `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`.</mandatory_pattern>
    </rule_block>
  </architectural_invariants>

  <execution_protocol level="8_audit_epic">
    <step id="1">DYNAMIC CONTEXT ACQUISITION: 
      - Locate and read the target Epic document (`docs/epic/EPIC_XXX_...md`). 
      - Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file <path_to_epic>`. If it fails, report the boundary errors and HALT execution immediately.
      - Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_epic_coverage.py --epic <path_to_epic> --phase <phase_num>` to perform deterministic physical file and AST symbol verification.
      - CRITICAL LIMIT: If the Epic has multiple phases, audit ONE Phase per session.
    </step>

    <step id="2">AS-BUILT MAPPING &amp; FORENSIC SEARCH: 
      - Use `grep_search` and `view_file` to trace every requirement from the targeted Phase into the physical codebase (`backend_v2`, `client_app_v2`).
    </step>

    <step id="3">DESTRUCTIVE OPERATION AUDIT: 
      - Search for symbols, classes, or files the Epic promised to delete or deprecate in this Phase and verify they are eradicated from the domain scope of the current Phase.
    </step>

    <step id="4">MODERNITY, COMPLIANCE &amp; QUALITY GATE VERIFICATION: 
      - Inspect the actual implementations against `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` and `<universal_quality_gate>` in `@[.agents/rules/00-antigravity-core.md]`.
      - SUPPLY CHAIN AUDIT: Verify `pyproject.toml` and `pubspec.yaml` contain zero unauthorized or banned packages.
      - MATHEMATICAL PROOF MANDATE: Execute localized and global quality gate scripts (`backend_audit_loop.py` and `flutter_audit_loop.py`), `audit_epic_coverage.py`, and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_tracker_output.py --tracker <tracker_path>`.
    </step>

    <step id="5">COMPLETION GAP ANALYSIS: 
      - Identify any "Orphan Requirements" requested by the Epic Phase that cannot be found or are only partially implemented (and cross-check linked GitHub issues/PRs via `@[.agents/plugins/github/mcp_config.json]` `quorum-github-mcp` when applicable).
    </step>

    <step id="6">RETROSPECTIVE REPORT GENERATION &amp; HANDOVER: 
      - Produce or incrementally update `EPIC_XXX_audit_report.md` in `docs/epic/` containing a strict Pass/Fail traceability matrix. If there are remaining Phases to audit, mandate `/tier5-session-handover` and provide the exact `/tier5-resume` command.
    </step>
  </execution_protocol>
</system_prompt>
```

