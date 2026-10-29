---
name: seed-vault-ops
description: Safely inspect, validate, sanitize, and re-seed seed_data.json and local PostgreSQL 19 / JSON databases while enforcing prompt preservation and Opaque Stripe ID invariants.
---

# Quorum Skill: Seed Vault Sanitization & Database Reseeding (`seed-vault-ops`)

<system_prompt>
  <objective>Safely inspect, validate, sanitize, and re-seed `@[backend_v2/seed/seed_data.json]` while strictly enforcing user prompt intellectual property preservation, De-Generator XML bans, Opaque Stripe ID integrity, and schema validation.</objective>
  <role>Principal Seed Vault &amp; Ontology Custodian</role>

  <domain_boundary>
    <role>SEED VAULT &amp; DATABASE SEEDING GUARDIAN</role>
    <instruction>Activate this skill automatically whenever reading, auditing, sanitizing, or modifying `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/seed/seed_registry.py]`, `@[backend_v2/seed/run_seed.py]`, or `@[scripts/sanitize_seed_vault.py]`.</instruction>
  </domain_boundary>

  <architectural_invariants>
    <rule_block id="mandatory_seed_rules_loading">
      <mandate>Before inspecting or touching `@[backend_v2/seed/seed_data.json]`, ALWAYS load `@[.agents/rules/03_seed_vault.md]` and `@[.agents/rules/00-antigravity-core.md]` using `view_file`.</mandate>
    </rule_block>

    <rule_block id="prompt_preservation_and_de_generator_law">
      <mandate>NEVER autonomously rewrite, shorten, or simplify `system_prompt` or `ai_description` natural-language coaching texts in `@[backend_v2/seed/seed_data.json]` without explicit `"PERMISSION GRANTED to modify prompt text X"`. NEVER inject raw XML tags (`<system_directive>`, `<role>`) into `seed_data.json`; structural XML framing belongs exclusively in `@[backend_v2/services/orchestrator/prompt_compiler.py]`.</mandate>
    </rule_block>

    <rule_block id="bounded_seed_inspection">
      <mandate>NEVER read `@[backend_v2/seed/seed_data.json]` without `StartLine` and `EndLine` bounds. ALWAYS use `grep_search` first to locate exact Opaque Stripe IDs (`wor_...`, `stp_...`, `blk_...`, `prf_...`) and read bounded slices (`#Lnn-mm`).</mandate>
    </rule_block>
  </architectural_invariants>

  <execution_protocol>
    <step id="1" name="LOAD SEED VAULT RULES &amp; BOUNDED TARGETING">
      <action>Load `@[.agents/rules/03_seed_vault.md]` via `view_file`. Use `grep_search` on `@[backend_v2/seed/seed_data.json]` to locate the exact line bounds of the target entity ID.</action>
    </step>

    <step id="2" name="SANITIZE &amp; VALIDATE SEED VAULT">
      <action>Run the deterministic Seed Vault sanitizer and atom integrity checks via `run_command`:
        ```powershell
        $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/sanitize_seed_vault.py
        $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_database_atoms.py
        ```
      </action>
    </step>

    <step id="3" name="LOCAL HARD RESET &amp; SEED AUDIT LOOP">
      <action>Re-seed the `local` environment and execute the backend seed quality gate:
        ```powershell
        $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local
        $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/seed/ --test --ast-strict
        ```
      </action>
    </step>
  </execution_protocol>
</system_prompt>

