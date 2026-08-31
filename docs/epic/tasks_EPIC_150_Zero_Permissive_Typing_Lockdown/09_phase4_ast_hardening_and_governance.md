<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# Phase 4: AST Hardening, Knowledge Base & Architectural Governance Lockdown

## Overview

Harden the AST guardrail engine (`scripts/_ast_guardrails.py`) to `FATAL` severity for all non-test, non-exempt files. Register the Multi-Category Exemption Register, create the new Knowledge Item `ki_zero_permissive_typing.md`, update existing Knowledge Items (`ki_seed_vault_verification_and_sanitization.md`, `ki_ast_guardrail_engine.md`), synchronize architectural rules (`01-python-backend.md`, `03_seed_vault.md`), and execute full-stack deterministic invariant verification.

## Target Files

- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[MODIFY]` `@[scripts/backend_audit_loop.py]`
- `[MODIFY]` `@[.agents/rules/01-python-backend.md]`
- `[MODIFY]` `@[.agents/rules/03_seed_vault.md]`
- `[NEW]` `@[ki_zero_permissive_typing.md]` (in knowledge base artifacts)
- `[MODIFY]` `@[ki_seed_vault_verification_and_sanitization.md]`
- `[MODIFY]` `@[ki_ast_guardrail_engine.md]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 4: AST Hardening & Governance Lockdown]</epic_anchor>
    <touched_artifacts>
      <backend>@[scripts/_ast_guardrails.py]</backend>
      <backend>@[scripts/backend_audit_loop.py]</backend>
      <backend>@[.agents/rules/01-python-backend.md]</backend>
      <backend>@[.agents/rules/03_seed_vault.md]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="ASTGuardrailFatalSeverity">
      # QGR001 (reflection), QGR002 (.get fallbacks), QGR012 (isinstance dict) set universally to FATAL
      # Explicit boundary exemption set: {"interfaces.py", "wrapper.py", "driver.py", "tinydb_driver.py", "firestore_driver.py", "logging_config.py", "exceptions.py"}
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[client_app_v2/]</file>
    <file>@[backend_v2/seed/seed_data.json]</file>
  </anti_targets>

  <dod_checklist>
    <item>AST guardrails QGR001, QGR002, QGR012 upgraded to universal FATAL severity</item>
    <item>Explicit boundary exemption register locked in _ast_guardrails.py</item>
    <item>Stage 4 of backend_audit_loop.py runs AST guardrails in --strict mode</item>
    <item>ki_zero_permissive_typing.md created in Knowledge Base</item>
    <item>ki_seed_vault_verification_and_sanitization.md and ki_ast_guardrail_engine.md synchronized</item>
    <item>.agents/rules/01-python-backend.md and 03_seed_vault.md updated with zero-tolerance mandates</item>
    <item>Zero-violation deterministic checks pass (0 QGR noqa, 0 isinstance dict in non-exempt files, exactly 102 exempt dict annotations)</item>
    <item>Full backend audit loop passes 100% green</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phases 1, 2, and 3 code migrations are complete and green.</action>
    <action>Run initial AST guardrail scan to baseline any residual violations.</action>
  </step>

  <step id="1" name="HARDEN AST GUARDRAIL ENGINE & AUDIT LOOP">
    <action>In @[scripts/_ast_guardrails.py], upgrade QGR001, QGR002, and QGR012 to FATAL severity for all non-test files. Register explicit boundary exemption set: {"interfaces.py", "wrapper.py", "driver.py", "tinydb_driver.py", "firestore_driver.py", "logging_config.py", "exceptions.py"}.</action>
    <action>In @[scripts/backend_audit_loop.py], update Stage 4 to invoke _ast_guardrails.py in --strict mode with zero-tolerance exit code.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py], add regression unit tests ensuring raw dict prompt messages and reflection in domain layers are statically rejected.</action>
  </step>

  <step id="2" name="CREATE & UPDATE KNOWLEDGE ITEMS">
    <action>Create Knowledge Item ki_zero_permissive_typing.md documenting Zero Permissive Typing architecture, DTO replacement patterns, boundary exemptions, and AST prevention mechanisms.</action>
    <action>Update @[ki_seed_vault_verification_and_sanitization.md] to document Two-Phase Pre-Flight In-Memory validation in seeder and Pydantic V2 Clean-Dump lifecycle.</action>
    <action>Update @[ki_ast_guardrail_engine.md] SSOT table: QGR001, QGR002, QGR012 universally FATAL with documented boundary exemptions.</action>
  </step>

  <step id="3" name="SYNCHRONIZE ARCHITECTURAL RULES">
    <action>In @[.agents/rules/01-python-backend.md], update no_naked_dicts_in_state, duck_typing_token_shield_ban, and strict_attribute_integrity to mandate absolute zero tolerance.</action>
    <action>In @[.agents/rules/03_seed_vault.md], mandate Two-Phase Pre-Flight validation, ban unregistered top-level collections, and mandate running sanitize_seed_vault.py --reseed --test.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_ast_guardrails_fatal_rejection_on_dict_messages">
      <input>Python source code declaring list[dict[str, Any]] in prompt or service layers</input>
      <expected>AST scanner returns FATAL error and exits non-zero</expected>
      <category>boundary</category>
    </contract>
    <contract id="2" name="test_ast_guardrails_allows_exempt_driver_annotations">
      <input>Python source code in backend_v2/database/interfaces.py with dict[str, Any]</input>
      <expected>AST scanner permits exempt annotations and exits 0</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run full backend verification, AST guardrails, and deterministic checks:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/ --test</command>
    <command>uv run python backend_v2/seed/run_seed.py local --dry-run</command>
    <command>uv run python scripts/sanitize_seed_vault.py --reseed --test</command>
    <command>uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py -v</command>
  </validation_gate>
</execution_protocol>
