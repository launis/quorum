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

# Phase 2B: Studio Services, Core Seed Models & Vault Sanitization

## Overview

Eliminate raw `dict[str, Any]` returns and parameters from Studio services and routers by directly instantiating and returning established SSOT models from `backend_v2/models/dtos/studio.py`. Purge obsolete `Workflow.ui_schema` and `Step.output_schema` from `backend_v2/models/v2_core.py`, define `ProviderExtraParamsDTO` for `ModelProfile.additional_params`, and eliminate orphan top-level `"step_blueprints": []` from `seed_data.json` via automated sanitization. Surgically eliminate telemetry dictionary `.get()` and QGR suppressions in `backend_v2/worker.py` and `blueprint.py`.

## Target Files

- `[MODIFY]` `@[backend_v2/services/studio/simulation_service.py]`
- `[MODIFY]` `@[backend_v2/services/studio/workflow_service.py]`
- `[MODIFY]` `@[backend_v2/services/studio/system_config_service.py]`
- `[MODIFY]` `@[backend_v2/services/studio/prompt_block_service.py]`
- `[MODIFY]` `@[backend_v2/services/studio/output_profile_service.py]`
- `[MODIFY]` `@[backend_v2/api/routers/studio/workflows.py]`
- `[MODIFY]` `@[backend_v2/api/routers/studio/steps.py]`
- `[MODIFY]` `@[backend_v2/api/routers/studio/prompt_blocks.py]`
- `[MODIFY]` `@[backend_v2/services/blueprint.py]`
- `[MODIFY]` `@[backend_v2/worker.py]`
- `[MODIFY]` `@[backend_v2/models/v2_core.py]`
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]`
- `[MODIFY]` `@[scripts/sanitize_seed_vault.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/studio/test_simulation_service.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 2: Service & Studio Layer DTO Elimination]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/services/studio/simulation_service.py]</backend>
      <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
      <backend>@[backend_v2/services/studio/system_config_service.py]</backend>
      <backend>@[backend_v2/services/studio/prompt_block_service.py]</backend>
      <backend>@[backend_v2/services/studio/output_profile_service.py]</backend>
      <backend>@[backend_v2/api/routers/studio/workflows.py]</backend>
      <backend>@[backend_v2/api/routers/studio/steps.py]</backend>
      <backend>@[backend_v2/api/routers/studio/prompt_blocks.py]</backend>
      <backend>@[backend_v2/services/blueprint.py]</backend>
      <backend>@[backend_v2/worker.py]</backend>
      <backend>@[backend_v2/models/v2_core.py]</backend>
      <backend>@[scripts/sanitize_seed_vault.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="StudioSimulationService">
      async def simulate_workflow(...) -> WorkflowSimulationResponse
      async def simulate_step(...) -> StepSimulationResponse
      async def simulate_prompt_block(...) -> PromptBlockSimulationResponse
    </interface>
    <interface id="ProviderExtraParamsDTO">
      class ProviderExtraParamsDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          temperature: float | None = None
          top_p: float | None = None
          top_k: int | None = None
          max_output_tokens: int | None = None
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/hooks/scoring/]</file>
    <file>@[backend_v2/database/repositories/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>StudioSimulationService returns WorkflowSimulationResponse, StepSimulationResponse, PromptBlockSimulationResponse directly</item>
    <item>Studio routers eliminate intermediate model_validate() dictionary conversions</item>
    <item>Workflow.ui_schema and Step.output_schema purged from models/v2_core.py</item>
    <item>ModelProfile.additional_params typed as ProviderExtraParamsDTO</item>
    <item>seed_data.json sanitized via scripts/sanitize_seed_vault.py --reseed --test; orphan step_blueprints purged</item>
    <item>worker.py eliminates 8 QGR003 suppressions, 21 dict[str, Any] annotations, and telemetry .get() calls</item>
    <item>blueprint.py eliminates 1 QGR001 and 11 QGR012 suppressions</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 2A progress and registry contracts compile cleanly.</action>
    <action>Inspect backend_v2/models/v2_core.py and backend_v2/worker.py.</action>
  </step>

  <step id="1" name="PURGE OBSOLETE SEED SCHEMAS & DEFINE PROVIDER EXTRA PARAMS">
    <action>In @[backend_v2/models/v2_core.py], purge Workflow.ui_schema: dict[str, Any] and Step.output_schema: dict[str, Any] | None.</action>
    <action>In @[backend_v2/models/v2_core.py], define ProviderExtraParamsDTO and type ModelProfile.additional_params with it.</action>
    <action>In @[scripts/sanitize_seed_vault.py] and @[backend_v2/seed/seed_data.json], purge orphan "step_blueprints": [] collection and execute automated sanitization via scripts/sanitize_seed_vault.py --reseed --test.</action>
  </step>

  <step id="2" name="MODERNIZE STUDIO SERVICES & ROUTERS">
    <action>In @[backend_v2/services/studio/simulation_service.py], eliminate dict[str, Any] return types and mock_inputs parameters. Refactor simulate_workflow to return WorkflowSimulationResponse, simulate_step to return StepSimulationResponse, and simulate_prompt_block to return PromptBlockSimulationResponse.</action>
    <action>In @[backend_v2/api/routers/studio/workflows.py], @[backend_v2/api/routers/studio/steps.py], and @[backend_v2/api/routers/studio/prompt_blocks.py], remove intermediate model_validate() dictionary conversions; return strongly typed simulation DTOs directly.</action>
    <action>In @[backend_v2/services/studio/workflow_service.py], @[backend_v2/services/studio/system_config_service.py], @[backend_v2/services/studio/prompt_block_service.py], and @[backend_v2/services/studio/output_profile_service.py], replace draft_dict: dict[str, Any] with typed domain models.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_simulation_service.py], update assertions to verify DTO attributes directly.</action>
  </step>

  <step id="3" name="SURGICAL HARDENING OF WORKER & BLUEPRINT">
    <action>In @[backend_v2/services/blueprint.py], eliminate 1 QGR001 reflection and 11 QGR012 suppressions.</action>
    <action>In @[backend_v2/worker.py], remove 8 QGR003 suppressions and 21 dict[str, Any] annotations. Add RFC-7807 structured logging to DLQ handlers and replace L260-L285 telemetry .get() with typed TraceEventMetadataEnvelope and TokenUsage.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_studio_simulation_returns_strict_dtos">
      <input>valid simulation request</input>
      <expected>returns instance of StepSimulationResponse with typed properties</expected>
      <category>positive</category>
    </contract>
    <contract id="2" name="test_seed_vault_sanitization_clean_dump">
      <input>run scripts/sanitize_seed_vault.py --reseed --test</input>
      <expected>exits 0, zero unregistered keys, zero validation errors</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop and seed vault verification on Phase 2 targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/core/ backend_v2/worker.py backend_v2/models/v2_core.py --test</command>
    <command>uv run python scripts/sanitize_seed_vault.py --reseed --test</command>
    <command>uv run python scripts/audit_database_atoms.py --strict</command>
  </validation_gate>
</execution_protocol>
