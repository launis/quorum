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

# Phase 3A: Hook Subsystem Suppression & Duck-Typing Eradication

## Overview

Eradicate all `# noqa: QGR012` inline suppressions, `dict[str, Any]` annotations, and `isinstance(..., dict)` duck-typing checks across the 17 files in the Hook subsystem (`backend_v2/hooks/`). Implement the 3-Tiered Anti-Duck-Typing Protocol: direct DTO attribute access for typed upstream state, guarded `TypeAdapter` validation with RFC-7807 `AppException(VALIDATION_FAILED)` conversion for untrusted boundary payloads, and category pre-filtering for polymorphic state.

## Target Files

- `[MODIFY]` `@[backend_v2/hooks/scoring/falsifier_hook.py]`
- `[MODIFY]` `@[backend_v2/hooks/scoring/matrix_hook.py]`
- `[MODIFY]` `@[backend_v2/hooks/scoring/normalization_hook.py]`
- `[MODIFY]` `@[backend_v2/hooks/scoring/passivity_hook.py]`
- `[MODIFY]` `@[backend_v2/hooks/validation.py]`
- `[MODIFY]` `@[backend_v2/hooks/llm.py]`
- `[MODIFY]` `@[backend_v2/hooks/dlq_guard.py]`
- `[MODIFY]` `@[backend_v2/hooks/input_processing.py]`
- `[MODIFY]` `@[backend_v2/hooks/integrity.py]`
- `[MODIFY]` `@[backend_v2/hooks/source_verification_hook.py]`
- `[MODIFY]` `@[backend_v2/hooks/atom_flattening.py]`
- `[MODIFY]` `@[backend_v2/hooks/context_mapper.py]`
- `[MODIFY]` `@[backend_v2/hooks/archival.py]`
- `[MODIFY]` `@[backend_v2/hooks/security.py]`
- `[MODIFY]` `@[backend_v2/hooks/hydration.py]`
- `[MODIFY]` `@[backend_v2/hooks/metadata.py]`
- `[MODIFY]` `@[backend_v2/hooks/metrics.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 3: Hooks, Orchestrator & Repository Suppression Eradication]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/hooks/scoring/falsifier_hook.py]</backend>
      <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
      <backend>@[backend_v2/hooks/scoring/normalization_hook.py]</backend>
      <backend>@[backend_v2/hooks/scoring/passivity_hook.py]</backend>
      <backend>@[backend_v2/hooks/validation.py]</backend>
      <backend>@[backend_v2/hooks/llm.py]</backend>
      <backend>@[backend_v2/hooks/dlq_guard.py]</backend>
      <backend>@[backend_v2/hooks/input_processing.py]</backend>
      <backend>@[backend_v2/hooks/integrity.py]</backend>
      <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
      <backend>@[backend_v2/hooks/atom_flattening.py]</backend>
      <backend>@[backend_v2/hooks/context_mapper.py]</backend>
      <backend>@[backend_v2/hooks/archival.py]</backend>
      <backend>@[backend_v2/hooks/security.py]</backend>
      <backend>@[backend_v2/hooks/hydration.py]</backend>
      <backend>@[backend_v2/hooks/metadata.py]</backend>
      <backend>@[backend_v2/hooks/metrics.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="HookAntiDuckTypingProtocol">
      # Pattern 1: Direct DTO dot-notation
      # Pattern 2: Guarded TypeAdapter hydration with AppException(VALIDATION_FAILED)
      # Pattern 3: Category pre-filtering before polymorphic hydration
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/services/orchestrator/]</file>
    <file>@[backend_v2/database/repositories/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero # noqa: QGR012, QGR002, or QGR001 suppressions across all 17 hook files</item>
    <item>Zero isinstance(..., dict) duck-typing checks across backend_v2/hooks/</item>
    <item>All DLQ handlers log structured errors via logger.error(..., extra={"error_code": ...})</item>
    <item>AST guardrails pass 100% clean on backend_v2/hooks/ in --strict mode</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 2 quality gates and sanitization pass cleanly.</action>
    <action>Inspect all 17 hook files for QGR suppressions and isinstance(dict) patterns.</action>
  </step>

  <step id="1" name="HARDEN SCORING HOOKS">
    <action>In @[backend_v2/hooks/scoring/falsifier_hook.py], eliminate 5 dict[str, Any] annotations and 3 QGR012 suppressions via direct DTO attribute access.</action>
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py], eliminate 1 dict[str, Any] annotation and 5 QGR012 suppressions.</action>
    <action>In @[backend_v2/hooks/scoring/normalization_hook.py], eliminate 1 dict[str, Any] annotation and 3 QGR012 suppressions.</action>
    <action>In @[backend_v2/hooks/scoring/passivity_hook.py], eliminate 1 dict[str, Any] annotation and 3 QGR012 suppressions.</action>
  </step>

  <step id="2" name="HARDEN PROCESSING & VALIDATION HOOKS">
    <action>In @[backend_v2/hooks/validation.py], @[backend_v2/hooks/llm.py], @[backend_v2/hooks/dlq_guard.py], @[backend_v2/hooks/input_processing.py], @[backend_v2/hooks/integrity.py], and @[backend_v2/hooks/source_verification_hook.py], eliminate all isinstance(dict) checks and QGR suppressions using Guarded TypeAdapter hydration with RFC-7807 AppException(VALIDATION_FAILED).</action>
    <action>In @[backend_v2/hooks/atom_flattening.py], @[backend_v2/hooks/context_mapper.py], @[backend_v2/hooks/archival.py], @[backend_v2/hooks/security.py], @[backend_v2/hooks/hydration.py], @[backend_v2/hooks/metadata.py], and @[backend_v2/hooks/metrics.py], replace raw dict transformations with typed DTO access.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_hook_guarded_hydration_raises_app_exception">
      <input>malformed input payload to hook validator</input>
      <expected>raises AppException(VALIDATION_FAILED, status_code=422)</expected>
      <category>negative</category>
    </contract>
    <contract id="2" name="test_scoring_hooks_process_typed_dto_state">
      <input>ExecutionInputsDTO with valid typed dynamic inputs</input>
      <expected>returns HookDeltaDTO with strictly typed modifications</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail scan and backend audit loop on Hook subsystem:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test</command>
  </validation_gate>
</execution_protocol>
