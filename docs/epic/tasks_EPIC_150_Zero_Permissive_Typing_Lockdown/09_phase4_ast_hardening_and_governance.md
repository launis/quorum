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

## 5-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **AST Guardrail Engine** (`@[scripts/_ast_guardrails.py]`) | Banned localized `services/` / `hooks/` soft checks allowing reflection/duck-typing in other domain directories (`models/`, `database/`, `api/`). | Universal `FATAL` severity for QGR001 (reflection), QGR002 (`.get()` fallbacks), and QGR012 (`isinstance(..., dict)`) across all non-test files, with explicit `BOUNDARY_EXEMPTION_FILES` set. | Pruned complex path regexes in favor of exact filename set membership check (`Path(filepath).name in BOUNDARY_EXEMPTION_FILES`). | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v` & `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` (0 violations). |
| **Backend Audit Loop** (`@[scripts/backend_audit_loop.py]`) | Banned silent bypass of AST violations in Stage 4. | Stage 4 enforces zero-tolerance FATAL rejection in standard mode and zero-tolerance unsuppressed violation rejection in `--ast-strict` mode. | Pruned redundant sub-process wrappers; invoke `scan_files_for_guardrails()` directly within python runtime. | `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --ast-strict` |
| **Knowledge Base Artifacts** (`@[ki_zero_permissive_typing.md]`, `@[ki_ast_guardrail_engine.md]`, `@[ki_seed_vault_verification_and_sanitization.md]`) | Banned outdated documentation referencing raw dictionary passing or soft AST guardrail severities. | SSOT documentation of Zero Permissive Typing, Two-Phase Seeder Pre-Flight In-Memory validation, and universal FATAL AST rules. | Pruned redundant architectural prose; preserve rigid XML blocks and concise Markdown SSOT tables. | Manual verification of KI artifacts and `/tier7-describe-architecture` compatibility. |
| **Architectural Rules** (`@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/03_seed_vault.md]`) | Banned ambiguous language permitting `extra="ignore"` or dictionary state transit. | Absolute zero-tolerance mandates for `no_naked_dicts_in_state`, `duck_typing_token_shield_ban`, and `strict_attribute_integrity`. | Pruned speculative rule blocks; keep rule files concise and authoritative. | Verified via AST guardrail scanning of rules and full backend audit. |
| **AST Unit Test Suite** (`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`) | Banned tests asserting `WARNING` for reflection or duck-typing in non-exempt domain code. | ISTQB positive and negative partition coverage verifying FATAL rejection across all non-test files and proper boundary exemption handling. | Pruned ad-hoc test utilities; leverage existing `_scan_snippet` helper. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v` |

## Target Files

- `[MODIFY]` `@[scripts/_ast_guardrails.py#L43-L367]`
- `[MODIFY]` `@[scripts/backend_audit_loop.py#L268-L286]`
- `[MODIFY]` `@[.agents/rules/01-python-backend.md#L113-L116]`
- `[MODIFY]` `@[.agents/rules/03_seed_vault.md#L40-L50]`
- `[NEW]` `@[ki_zero_permissive_typing.md]` (in knowledge base artifacts)
- `[MODIFY]` `@[ki_seed_vault_verification_and_sanitization.md#L1-L102]`
- `[MODIFY]` `@[ki_ast_guardrail_engine.md#L8-L26]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L106-L750]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 4: AST Hardening & Governance Lockdown]</epic_anchor>
    <touched_artifacts>
      <backend>@[scripts/_ast_guardrails.py]</backend>
      <backend>@[scripts/backend_audit_loop.py]</backend>
      <backend>@[.agents/rules/01-python-backend.md]</backend>
      <backend>@[.agents/rules/03_seed_vault.md]</backend>
      <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
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
    <item>AST guardrails QGR001, QGR002, QGR012 upgraded to universal FATAL severity across all non-test files</item>
    <item>Explicit boundary exemption register locked in _ast_guardrails.py (BOUNDARY_EXEMPTION_FILES)</item>
    <item>Stage 4 of backend_audit_loop.py runs AST guardrails with zero-tolerance exit codes</item>
    <item>ki_zero_permissive_typing.md created in Knowledge Base with complete architecture SSOT</item>
    <item>ki_seed_vault_verification_and_sanitization.md and ki_ast_guardrail_engine.md synchronized</item>
    <item>.agents/rules/01-python-backend.md and 03_seed_vault.md updated with zero-tolerance mandates</item>
    <item>Zero-violation deterministic checks pass (0 QGR noqa, 0 isinstance dict in non-exempt files, exactly 102 exempt dict annotations)</item>
    <item>Full backend audit loop passes 100% green</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK & PRE-IMPLEMENTATION CLEANUPS">
    <action>Verify that Phases 1, 2, and 3 code migrations are complete, committed, and 100% green.</action>
    <action>Run initial AST guardrail scan: `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` to baseline any residual violations.</action>
    <action>Verify zero unresolved `# noqa: QGR` suppressions in domain code outside explicit test files.</action>
  </step>

  <step id="1" name="HARDEN AST GUARDRAIL ENGINE & AUDIT LOOP">
    <action>In @[scripts/_ast_guardrails.py#L43-L367]:
      1. Define `BOUNDARY_EXEMPTION_FILES: set[str] = {"interfaces.py", "wrapper.py", "driver.py", "tinydb_driver.py", "firestore_driver.py", "logging_config.py", "exceptions.py"}`.
      2. In `QuorumGuardrailVisitor.__init__`, set `self._is_boundary_exempt = Path(filepath).name in BOUNDARY_EXEMPTION_FILES`.
      3. Upgrade `QGR001` (reflection), `QGR002` (`.get()` fallbacks), and `QGR012` (`isinstance(..., dict)` checks and `match/case dict`) severity to `GuardrailSeverity.FATAL` for all files where `not self._is_test_file and not self._is_boundary_exempt`.
    </action>
    <action>In @[scripts/backend_audit_loop.py#L268-L286], verify Stage 4 accurately traps FATAL violations and enforces strict zero-tolerance behavior when `--ast-strict` is specified.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L106-L750], update tests to verify universal `FATAL` severity on domain files and proper pass-through on boundary exempt files.</action>
  </step>

  <step id="2" name="CREATE & UPDATE KNOWLEDGE ITEMS">
    <action>Create Knowledge Item `ki_zero_permissive_typing.md` in knowledge base artifacts directory documenting:
      - Multi-Tier DTO Architecture & Pure Dot-Notation Access
      - Two-Phase Seeder Pre-Flight In-Memory Validation & Reseed Protocol
      - Repository Reconstitution Firewall (Zero Dict Leakage)
      - AST Guardrail Engine Enforcement & Universal FATAL Severity
      - Multi-Category Exemption Register SSOT
    </action>
    <action>Update @[ki_seed_vault_verification_and_sanitization.md#L1-L102] to document Two-Phase Pre-Flight In-Memory validation in seeder and Pydantic V2 Clean-Dump lifecycle.</action>
    <action>Update @[ki_ast_guardrail_engine.md#L8-L26] SSOT table: QGR001, QGR002, QGR012 universally FATAL with documented boundary exemptions.</action>
  </step>

  <step id="3" name="SYNCHRONIZE ARCHITECTURAL RULES">
    <action>In @[.agents/rules/01-python-backend.md#L113-L116], update `no_naked_dicts_in_state`, `duck_typing_token_shield_ban`, and `strict_attribute_integrity` to mandate absolute zero tolerance and document boundary firewall patterns.</action>
    <action>In @[.agents/rules/03_seed_vault.md#L40-L50], mandate Two-Phase Pre-Flight validation, ban unregistered top-level collections, and mandate running `sanitize_seed_vault.py --reseed --test`.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_ast_guardrails_fatal_rejection_on_dict_messages">
      <input>Python source code declaring `isinstance(payload, dict)` in `backend_v2/models/sample.py`</input>
      <expected>AST scanner returns `QGR012` with `FATAL` severity and exits non-zero</expected>
      <category>boundary</category>
    </contract>
    <contract id="2" name="test_ast_guardrails_allows_exempt_driver_annotations">
      <input>Python source code in `backend_v2/database/interfaces.py` with `dict[str, Any]`</input>
      <expected>AST scanner permits exempt boundary annotations and exits 0</expected>
      <category>positive</category>
    </contract>
    <contract id="3" name="test_ast_guardrails_qgr001_fatal_in_models">
      <input>Python source code with `getattr(obj, "attr")` in `backend_v2/models/domain.py`</input>
      <expected>AST scanner returns `QGR001` with `FATAL` severity</expected>
      <category>boundary</category>
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
