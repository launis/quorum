---
description: Tier 2 (Matrix & Atom Hardening) - Step-by-step auditing, balancing, and expansion loop for Quorum Evaluation Matrices in seed_data.json.
---

### 🟢 TIER 2: MATRIX & ATOM HARDENING LOOP
*Usage: Use this workflow to systematically audit, balance, and expand evaluation matrices in `backend_v2/seed/seed_data.json` to eliminate fragile cliff risks (< 3 atoms per level), balance inverse evidence, and guarantee realistic score dispersion.*

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Ex: "Run Tier 2 Matrix Hardening Loop for blk_440a5fef9331451b" or "Run Tier 2 Matrix Hardening Loop for all 13 matrices"]</objective>
  <role>Lead Evaluation Matrix Auditor & Ontological Seed Architect</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`, `.agents/rules/03_seed_vault.md`, and `.agents/rules/05_llm_architecture.md`. You MUST NOT output any `<thinking_process>` or mutate code before reading these rules.</mandatory_pattern>
      <catastrophic_reason>Modifying evaluation matrices without seed vault and prompt compilation rules corrupts the SSOT database schema and crashes test pipelines.</catastrophic_reason>
    </rule_block>

    <rule_block id="prompt_preservation_mandate">
      <mandatory_pattern>Qualitative texts, coaching descriptions, and matrix theories in `seed_data.json` represent deliberate coaching philosophy. Never amputate prompt semantics. Expand and refine extraction rules with ISTQB precision.</mandatory_pattern>
      <catastrophic_reason>Agentic drift destroys human-authored synthesis quality when reducing complex cognitive dimensions into naive binary checks.</catastrophic_reason>
    </rule_block>

    <rule_block id="streamlined_execution_mandate">
      <mandatory_pattern>Do NOT generate an `implementation_plan.md` artifact or pause for approval during `/tier2-hardening-matrix`. Per user mandate, proceed directly with surgical structural updates to `seed_data.json`, verify against automated quality gates (`audit_database_atoms.py --strict`, `run_seed.py local --dry-run`), re-seed the local DB, and generate the Opponent Card report.</mandatory_pattern>
      <catastrophic_reason>Pausing for interactive plans on each matrix stalls the high-throughput 13-matrix ontological hardening pipeline.</catastrophic_reason>
    </rule_block>

    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever referencing a matrix block, wrap it in `@-reference` syntax with exact line bounds if viewed: `@[backend_v2/seed/seed_data.json#Lnn-mm]`.</mandatory_pattern>
      <catastrophic_reason>Dumping 10,000 lines of seed data without line bounds crashes context windows.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <phases>
    <phase id="1" name="Mapping & Status Inspection">
      <action>Execute the deterministic audit engine: `uv run python scripts/matrix_hardening_loop.py --status`.</action>
      <action>If a specific matrix ID was given in the command (e.g. `blk_440a5fef9331451b`), select ONLY that matrix. Otherwise, select the first matrix marked `[TODO]`.</action>
      <action>Run deep inspection for the active target: `uv run python scripts/matrix_hardening_loop.py --inspect <target_matrix_id>`.</action>
    </phase>
    
    <phase id="2" name="Level-by-Level Audit & Hardening">
      <action>For the selected matrix, review each scale level against the 3 Golden Rules:
        1. ATOM DENSITY: Every level MUST have $\ge 3$ atoms (ideally 3–5) to eliminate brittle 0%/50% binary cliff failures.
        2. TRI-AXIS BALANCE: Each level should combine Structural form, Substantive cognitive depth, and Error-detection (`inverse_evidence=True`).
        3. EXTRACTION PRECISION: Ensure `extraction_rule` is unambiguous with explicit ACCEPTABLE / UNACCEPTABLE contrastive examples.
      </action>
      <action>Perform surgical structural updates to `backend_v2/seed/seed_data.json` using native MCP editing tools (`replace_file_content` / `multi_replace_file_content`).</action>
      <constraint name="VALIDATION_GATE">
        Immediately after editing `seed_data.json`, you MUST execute the two deterministic verification gates:
        1. `uv run python scripts/audit_database_atoms.py --strict`
        2. `uv run python backend_v2/seed/run_seed.py local --dry-run`
        If any gate fails, revert immediately.
      </constraint>
      <action>Once validated, mark the matrix as completed: `uv run python scripts/matrix_hardening_loop.py --done <target_matrix_id>`.</action>
      <action>Re-seed the local testing database: `uv run python backend_v2/seed/run_seed.py local`.</action>
      <action name="RED_TEAM_PROMPT_GENERATION">
        For EVERY completed matrix, you MUST output a dedicated, self-contained Markdown Review & Opponent Card containing:
        1. MATRIX THEORY GROUNDING: Full academic theory, philosophy, and scale level logic.
        2. COMPLETE ATOM LIST: All level-by-level assertions, extraction rules, and contrastive examples.
        3. EXTERNAL AI OPPONENT PROMPT (/tier8-audit-feature style): A pre-formatted, copy-pasteable prompt for another AI (ChatGPT, Claude, Gemini) to aggressively red-team, stress-test, and find edge-case loopholes or biases in this matrix definition.
      </action>
      <action>SESSION LIMIT: Audit a maximum of 2–3 matrices per session to maintain fresh reasoning and prevent context fatigue.</action>
    </phase>
  </phases>
</system_prompt>
```
