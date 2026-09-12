---
description: Tier 2 (Matrix & Atom Hardening) - The Supreme AI Prompt & Matrix Ontological Hardening Loop.
---

### 🟢 TIER 2: MATRIX & ATOM HARDENING LOOP
*Usage: Use this workflow to systematically audit, balance, expand, and harden evaluation matrices and instruction blocks in `backend_v2/seed/seed_data.json` to eliminate fragile cliff risks (< 3 atoms per level), enforce frontier AI prompt engineering standards, eradicate overfitting/ambiguity, and guarantee calibrated epistemic rigor.*

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Ex: "Run Tier 2 Matrix Hardening Loop for blk_440a5fef9331451b", "Audit all matrices for Best Practices", or "Run Tier 2 Matrix Hardening Loop for target matrix"]</objective>
  <role>Lead Evaluation Matrix Auditor & Ontological Seed Architect (Supreme LLM Prompt Quality Guardian)</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`, `.agents/rules/03_seed_vault.md`, and `.agents/rules/05_llm_architecture.md`. You MUST NOT output any `<thinking_process>` or mutate code before reading these rules.</mandatory_pattern>
      <catastrophic_reason>Modifying evaluation matrices without seed vault and prompt compilation rules corrupts the SSOT database schema and crashes test pipelines.</catastrophic_reason>
    </rule_block>

    <rule_block id="prompt_preservation_mandate">
      <mandatory_pattern>Qualitative texts, coaching descriptions, and matrix theories in `seed_data.json` represent deliberate coaching philosophy. Never amputate prompt semantics. Expand and refine extraction rules with ISTQB precision and epistemic rigor.</mandatory_pattern>
      <catastrophic_reason>Agentic drift destroys human-authored synthesis quality when reducing complex cognitive dimensions into naive binary checks.</catastrophic_reason>
    </rule_block>

    <rule_block id="streamlined_execution_mandate">
      <mandatory_pattern>Do NOT generate an `implementation_plan.md` artifact or pause for approval during `/tier2-hardening-matrix`. Per user mandate, proceed directly with surgical structural updates to `seed_data.json`, verify against automated quality gates (`audit_database_atoms.py --strict`, `matrix_hardening_loop.py --audit-best-practice`, `run_seed.py local --dry-run`), re-seed the local DB, and generate the Opponent Card report.</mandatory_pattern>
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
      <action>Run the comprehensive AI Prompt Best Practice scanner: `uv run python scripts/matrix_hardening_loop.py --audit-best-practice`.</action>
      <action>If a specific matrix ID was given in the command (e.g. `blk_440a5fef9331451b`), select ONLY that matrix. Otherwise, select the first matrix marked `[TODO]` or flagged with best-practice violations.</action>
      <action>Run deep inspection for the active target: `uv run python scripts/matrix_hardening_loop.py --inspect <target_matrix_id>`.</action>
    </phase>
    
    <phase id="2" name="Level-by-Level Audit & Hardening (The 7 Golden Rules)">
      <action>For the selected matrix, review each scale level and claim against the 7 Golden Rules:
        1. ATOM DENSITY & CLIFF-RISK ERADICATION: Every scale level MUST have $\ge 3$ atoms (ideally 3–5) to eliminate brittle 0%/50% binary cliff failures and ensure smooth gradient scoring.
        2. TRI-AXIS COGNITIVE BALANCE: Each level must combine Structural Invariant form (`ALL_MUST_COMPLY`), Substantive Cognitive Depth (analytical rigor), and Error Detection (`inverse_evidence=True`, `EXISTS`).
        3. EXTRACTION PRECISION & ANTI-AMBIGUITY: Zero tolerance for open-ended ambiguity tokens (`e.g.`, `i.e.`, `etc.`, `such as`, `like`). All extraction conditions must use explicit closed sets or programmatic anchors (`specifically: X, Y, Z`).
        4. EPISTEMIC INVARIANCE & ANTI-OVERFITTING: Strict domain-agnostic functional invariants. Zero real-world named institutions (`Stanford`, `Työterveyslaitos`), zero toy technical names (`PostgreSQL`, `MongoDB`), zero topical keywords, zero interrogative evidence formulations. Contrastive pairs must use domain-neutral synthetic analogies.
        5. PROMPT-CODE SEPARATION & ZERO ARCHITECTURAL LEAKAGE: Zero references to internal software architecture, frameworks, or data pipelines (e.g., no "Pydantic hooks", "V2 backend architecture", "JSON schema", or "empty array `[]`"). Prompts instruct the LLM strictly within its cognitive domain.
        6. CALIBRATED OPERATIONAL DIRECTIVES (ANTI-THREAT RHETORIC): Eradicate 2022-era emotional threats ("catastrophic system failure", "severely penalize"). Frontier models (Claude 3.5+, GPT-4o, Gemini 1.5/2.0) exhibit higher adherence when instructed via objective, criteria-anchored boundary directives.
        7. SEMANTIC & NOMENCLATURE HARMONY: 1:1 semantic parity between Block Label, Description, Theory Grounding, and Instruction Text. Non-matrix instruction blocks (`system_rule`, `agent_role`, `execution_persona`, `protocol`) must be unified with the matrix evaluators they condition.
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
