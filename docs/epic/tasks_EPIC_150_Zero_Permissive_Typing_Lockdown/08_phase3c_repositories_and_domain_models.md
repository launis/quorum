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

# Phase 3C: Repositories & Domain Models Duck-Typing Eradication

## Overview

Eliminate all remaining `isinstance(..., dict)` duck-typing checks, `# noqa: QGR012` suppressions, and non-exempt `dict[str, Any]` annotations across the Data Access Layer (Repositories) and Domain Models. Enforce the repository reconstitution firewall: internal database drivers handle persistence dictionaries while repositories reconstitute and return strictly typed Pydantic Domain models with zero dictionary leakage into callers.

## Target Files

- `[MODIFY]` `@[backend_v2/database/repositories/execution.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/component.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/components/matrix.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/audit.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/workflow.py]`
- `[MODIFY]` `@[backend_v2/models/domain/inputs.py]`
- `[MODIFY]` `@[backend_v2/models/domain/mechanical_anchors.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/evaluation_steps.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/quote_evidence.py]`
- `[MODIFY]` `@[backend_v2/models/state.py]`
- `[MODIFY]` `@[backend_v2/models/domain/archivist.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/matrix_scorecard.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 3: Hooks, Orchestrator & Repository Suppression Eradication]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/database/repositories/execution.py]</backend>
      <backend>@[backend_v2/database/repositories/component.py]</backend>
      <backend>@[backend_v2/database/repositories/components/matrix.py]</backend>
      <backend>@[backend_v2/database/repositories/audit.py]</backend>
      <backend>@[backend_v2/database/repositories/workflow.py]</backend>
      <backend>@[backend_v2/models/domain/inputs.py]</backend>
      <backend>@[backend_v2/models/domain/mechanical_anchors.py]</backend>
      <backend>@[backend_v2/models/dtos/evaluation_steps.py]</backend>
      <backend>@[backend_v2/models/dtos/quote_evidence.py]</backend>
      <backend>@[backend_v2/models/state.py]</backend>
      <backend>@[backend_v2/models/domain/archivist.py]</backend>
      <backend>@[backend_v2/models/dtos/matrix_scorecard.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="RepositoryReconstitutionFirewall">
      # Repositories map raw database driver records immediately into Pydantic models (strict=False)
      # Zero dict leakage past repository boundary
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/database/interfaces.py]</file>
    <file>@[backend_v2/database/wrapper.py]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero isinstance(..., dict) checks across repositories and domain models</item>
    <item>Zero # noqa: QGR012 suppressions in repository files</item>
    <item>Persistence drivers isolated behind 102 exempt dictionary annotations</item>
    <item>AST guardrails pass 100% clean on repositories and models in --strict mode</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 3B orchestrator hardening passes AST guardrails cleanly.</action>
    <action>Inspect repositories and domain models for remaining duck-typing checks.</action>
  </step>

  <step id="1" name="HARDEN REPOSITORY RECONSTITUTION LAYER">
    <action>In @[backend_v2/database/repositories/execution.py], eliminate 4 QGR012 suppressions and 6 non-exempt dict[str, Any] annotations via direct typed reconstitution.</action>
    <action>In @[backend_v2/database/repositories/component.py] and @[backend_v2/database/repositories/components/matrix.py], eliminate 4 isinstance(dict) checks and 9 dict[str, Any] annotations.</action>
    <action>In @[backend_v2/database/repositories/audit.py] and @[backend_v2/database/repositories/workflow.py], eliminate 2 isinstance(dict) checks and 11 dict[str, Any] annotations.</action>
  </step>

  <step id="2" name="HARDEN DOMAIN MODELS & DTOS">
    <action>In @[backend_v2/models/domain/inputs.py] (4), @[backend_v2/models/domain/mechanical_anchors.py] (3), @[backend_v2/models/dtos/evaluation_steps.py] (2), and @[backend_v2/models/dtos/quote_evidence.py] (2), eliminate isinstance(dict) checks using native Pydantic V2 validators and Discriminated Unions.</action>
    <action>In @[backend_v2/models/state.py] (2), @[backend_v2/models/domain/archivist.py] (1), and @[backend_v2/models/dtos/matrix_scorecard.py] (1), eliminate duck-typing.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_repository_reconstitutes_typed_domain_models">
      <input>Raw database record dictionary from driver</input>
      <expected>reconstitutes into strict frozen Pydantic Domain model without leaking dict</expected>
      <category>positive</category>
    </contract>
    <contract id="2" name="test_domain_models_forbid_duck_typing">
      <input>Malformed payload with untyped dictionary</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>negative</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail scan and backend audit loop on Repositories and Models:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/database/repositories/ backend_v2/models/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ backend_v2/models/ --test</command>
  </validation_gate>
</execution_protocol>
