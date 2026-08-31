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

Eliminate raw `dict[str, Any]` returns and parameters from Studio services and routers by directly instantiating and returning established SSOT models from `backend_v2/models/dtos/studio.py`. Purge obsolete `Workflow.ui_schema` and `Step.output_schema` from `backend_v2/models/v2_core.py`, define `ProviderExtraParamsDTO` for `ModelProfile.additional_params`, and eliminate orphan top-level `"step_blueprints": []` from `seed_data.json` via automated sanitization. Surgically eliminate telemetry dictionary `.get()` calls and QGR suppressions in `backend_v2/worker.py` and `backend_v2/services/blueprint.py`.

## 5-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`backend_v2/models/v2_core.py`**<br>`ModelProfile`<br>`Step`<br>`Workflow` | Banned `dict[str, Any]` fields (`ui_schema`, `output_schema`, raw `additional_params`). Banned permissive dictionary structures. | Strict `ProviderExtraParamsDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`). Purged `ui_schema` and `output_schema`. | No custom dynamic parameter parsers; rely on native Pydantic V2 model fields. | `test_provider_extra_params_extra_forbidden`, `test_workflow_ui_schema_purged`, `backend_audit_loop.py`. |
| **`backend_v2/services/studio/simulation_service.py`** | Banned `dict[str, Any]` return types and dictionary index access (`res["valid"]`, `sim["rendered_prompt"]`). | Direct instantiation of `WorkflowSimulationResponse`, `StepSimulationResponse`, and `PromptBlockSimulationResponse`. | Reuse established SSOT models from `models/dtos/studio.py`; no wrapper adapters. | `test_simulate_workflow_success` (dot-notation), `test_simulate_step_success`. |
| **`backend_v2/api/routers/studio/`**<br>`workflows.py`<br>`steps.py`<br>`prompt_blocks.py` | Banned intermediate `Model.model_validate(result)` conversions on service return values. | Directly return typed simulation response instances from service calls. | Zero wrapper conversion code in router handlers. | FastAPI OpenAPI schema verification; route unit tests. |
| **`backend_v2/models/dtos/trace.py`**<br>`backend_v2/worker.py`<br>`backend_v2/services/blueprint.py` | Banned `.get("token_usage")`, `p_tokens += usage.get(...)`, and `hasattr(strat_raw, "value")`. Banned broad `except Exception:`. | Co-located `StepTraceMetadataDTO` and `TraceEventMetadataEnvelope`. Strongly-typed dot-notation access via `TokenUsage`. | No complex trace parsing pipelines; direct typed envelope validation. | `backend_audit_loop.py` (0 QGR001, 0 QGR002 in telemetry paths), `test_worker_synthesis.py`. |
| **`backend_v2/seed/seed_data.json`**<br>`scripts/sanitize_seed_vault.py` | Banned orphan `"step_blueprints": []` root key and legacy schema fields. | Automated in-memory sanitization via `scripts/sanitize_seed_vault.py --reseed --test`. | Atomic tempfile replacement with `os.fsync` and referential integrity check. | `audit_database_atoms.py --strict`, `test_seed_vault_sanitization_clean_dump`. |

## Target Files

- `[MODIFY]` `@[backend_v2/models/v2_core.py#L352-L382]` (ModelProfile & ProviderExtraParamsDTO)
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L484-L578]` (Step output_schema purge)
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L1111-L1244]` (Workflow ui_schema purge)
- `[MODIFY]` `@[backend_v2/models/dtos/studio.py#L109-L171]` (StepCreateDTO output_schema purge)
- `[MODIFY]` `@[backend_v2/models/dtos/trace.py#L27-L32]` (StepTraceMetadataDTO & TraceEventMetadataEnvelope)
- `[MODIFY]` `@[backend_v2/services/studio/simulation_service.py#L31-L273]` (StudioSimulationService)
- `[MODIFY]` `@[backend_v2/services/studio/workflow_service.py#L39-L640]` (StudioWorkflowService)
- `[MODIFY]` `@[backend_v2/services/studio/system_config_service.py#L23-L463]` (StudioSystemConfigService)
- `[MODIFY]` `@[backend_v2/services/studio/prompt_block_service.py#L27-L256]` (StudioPromptBlockService)
- `[MODIFY]` `@[backend_v2/services/studio/output_profile_service.py#L22-L270]` (StudioOutputProfileService)
- `[MODIFY]` `@[backend_v2/api/routers/studio/workflows.py#L83-L101]` (simulate_workflow)
- `[MODIFY]` `@[backend_v2/api/routers/studio/steps.py#L26-L46]` (simulate_step)
- `[MODIFY]` `@[backend_v2/api/routers/studio/prompt_blocks.py#L28-L48]` (simulate_prompt_block)
- `[MODIFY]` `@[backend_v2/services/execution.py#L1415-L1434]` (get_workflow_ui_schema)
- `[MODIFY]` `@[backend_v2/services/blueprint.py#L62-L699]` (BlueprintTransformer)
- `[MODIFY]` `@[backend_v2/worker.py#L125-L455]` (execute_workflow_job)
- `[MODIFY]` `@[backend_v2/worker.py#L627-L1388]` (generate_profile_synthesis_and_pdf_task)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]` (Purge orphan step_blueprints & ui_schema)
- `[MODIFY]` `@[scripts/sanitize_seed_vault.py#L424-L478]` (run_seed_vault_sanitization)
- `[MODIFY]` `@[backend_v2/tests/unit/services/studio/test_simulation_service.py#L55-L101]` (test_simulate_workflow_success)

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 2: Service & Studio Layer DTO Elimination]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/models/v2_core.py#L352-L382]</backend>
      <backend>@[backend_v2/models/v2_core.py#L484-L578]</backend>
      <backend>@[backend_v2/models/v2_core.py#L1111-L1244]</backend>
      <backend>@[backend_v2/models/dtos/studio.py#L109-L171]</backend>
      <backend>@[backend_v2/models/dtos/trace.py#L27-L32]</backend>
      <backend>@[backend_v2/services/studio/simulation_service.py#L31-L273]</backend>
      <backend>@[backend_v2/services/studio/workflow_service.py#L39-L640]</backend>
      <backend>@[backend_v2/services/studio/system_config_service.py#L23-L463]</backend>
      <backend>@[backend_v2/services/studio/prompt_block_service.py#L27-L256]</backend>
      <backend>@[backend_v2/services/studio/output_profile_service.py#L22-L270]</backend>
      <backend>@[backend_v2/api/routers/studio/workflows.py#L83-L101]</backend>
      <backend>@[backend_v2/api/routers/studio/steps.py#L26-L46]</backend>
      <backend>@[backend_v2/api/routers/studio/prompt_blocks.py#L28-L48]</backend>
      <backend>@[backend_v2/services/execution.py#L1415-L1434]</backend>
      <backend>@[backend_v2/services/blueprint.py#L62-L699]</backend>
      <backend>@[backend_v2/worker.py#L125-L455]</backend>
      <backend>@[backend_v2/worker.py#L627-L1388]</backend>
      <backend>@[scripts/sanitize_seed_vault.py#L424-L478]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="StudioSimulationService">
      async def simulate_workflow(self, initiator: TokenData, data: Workflow) -> WorkflowSimulationResponse
      async def simulate_step(self, initiator: TokenData, data: Step, mock_inputs: dict[str, str]) -> StepSimulationResponse
      async def simulate_prompt_block(self, initiator: TokenData, data: PromptBlock, mock_inputs: dict[str, str]) -> PromptBlockSimulationResponse
    </interface>
    <interface id="ProviderExtraParamsDTO">
      class ProviderExtraParamsDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          temperature: float | None = None
          top_p: float | None = None
          top_k: int | None = None
          max_output_tokens: int | None = None
    </interface>
    <interface id="StepTraceMetadataDTO">
      class StepTraceMetadataDTO(BaseDTO):
          model_config = ConfigDict(strict=True, extra="forbid")
          task_blueprint: str | None = None
          model_strategy: str = "unknown"
          chunk_size: int = 1
          token_usage: TokenUsage = Field(default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0))
          execution_id: str | None = None
          workflow_id: str | None = None
          step_id: str | None = None
          initiator_id: str | None = None
          timestamp_isot: str | None = None
          unix_time: int | None = None
          v2_engine: bool | None = None
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/hooks/scoring/]</file>
    <file>@[backend_v2/database/repositories/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item checked="true">StudioSimulationService returns WorkflowSimulationResponse, StepSimulationResponse, PromptBlockSimulationResponse directly</item>
    <item checked="true">Studio routers eliminate intermediate model_validate() dictionary conversions</item>
    <item checked="true">Workflow.ui_schema and Step.output_schema purged from models/v2_core.py and models/dtos/studio.py</item>
    <item checked="true">ModelProfile.additional_params typed as ProviderExtraParamsDTO</item>
    <item checked="true">seed_data.json sanitized via scripts/sanitize_seed_vault.py --reseed --test; orphan step_blueprints purged</item>
    <item checked="true">worker.py eliminates telemetry dictionary .get() calls and uses StepTraceMetadataDTO</item>
    <item checked="true">blueprint.py eliminates 1 QGR001 reflection and QGR012 duck-typing checks</item>
    <item checked="true">test_simulation_service.py migrated to 100% dot-notation attribute access</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION CLEANUPS">
    <action>Verify that Phase 2A progress and registry contracts compile cleanly.</action>
    <action>In @[backend_v2/services/studio/workflow_service.py#L39-L640], fix comma syntax in multi-exception clause to standard tuple syntax.</action>
    <action>In @[backend_v2/services/blueprint.py#L62-L699], replace hasattr(strat_raw, "value") with isinstance(strat_raw, ScoringStrategy) to eliminate QGR001.</action>
  </step>

  <step id="1" name="PURGE OBSOLETE SEED SCHEMAS &amp; DEFINE PROVIDER EXTRA PARAMS">
    <action>In @[backend_v2/models/v2_core.py#L352-L382], create ProviderExtraParamsDTO and type ModelProfile.additional_params as ProviderExtraParamsDTO = Field(default_factory=ProviderExtraParamsDTO).</action>
    <action>In @[backend_v2/models/v2_core.py#L484-L578], purge Step.output_schema.</action>
    <action>In @[backend_v2/models/v2_core.py#L1111-L1244], purge Workflow.ui_schema.</action>
    <action>In @[backend_v2/models/dtos/studio.py#L109-L171], purge StepCreateDTO.output_schema.</action>
    <action>In @[backend_v2/services/execution.py#L1415-L1434], update get_workflow_ui_schema to dynamically return {"expected_inputs": [inp.model_dump(mode="json") for inp in workflow.expected_inputs]}.</action>
    <action>In @[scripts/sanitize_seed_vault.py#L424-L478] and @[backend_v2/seed/seed_data.json], purge orphan "step_blueprints": [] collection and execute automated sanitization via scripts/sanitize_seed_vault.py --reseed --test.</action>
  </step>

  <step id="2" name="MODERNIZE STUDIO SERVICES &amp; ROUTERS">
    <action>In @[backend_v2/models/dtos/trace.py#L27-L32], create StepTraceMetadataDTO and update TraceEventMetadataEnvelope.</action>
    <action>In @[backend_v2/services/studio/simulation_service.py#L31-L273], eliminate dict[str, Any] return types. Refactor simulate_workflow to return WorkflowSimulationResponse, simulate_step to return StepSimulationResponse, and simulate_prompt_block to return PromptBlockSimulationResponse.</action>
    <action>In @[backend_v2/api/routers/studio/workflows.py#L83-L101], @[backend_v2/api/routers/studio/steps.py#L26-L46], and @[backend_v2/api/routers/studio/prompt_blocks.py#L28-L48], remove intermediate model_validate() dictionary conversions; return strongly typed simulation DTOs directly from service calls.</action>
    <action>In @[backend_v2/services/studio/workflow_service.py#L39-L640], @[backend_v2/services/studio/system_config_service.py#L23-L463], @[backend_v2/services/studio/prompt_block_service.py#L27-L256], and @[backend_v2/services/studio/output_profile_service.py#L22-L270], ensure draft creation methods pass clean domain payloads without obsolete fields.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_simulation_service.py#L55-L101], migrate all test assertions from dictionary subscription (res["valid"]) to direct typed attribute access (res.valid).</action>
  </step>

  <step id="3" name="SURGICAL HARDENING OF WORKER &amp; BLUEPRINT">
    <action>In @[backend_v2/services/blueprint.py#L62-L699], eliminate QGR012 duck-typing checks by validating structured payloads with TraceScoringPayloadDTO, EvidenceOverrideDTO, and StepTraceMetadataDTO.</action>
    <action>In @[backend_v2/worker.py#L125-L455] and @[backend_v2/worker.py#L627-L1388], eliminate telemetry dictionary .get() calls by hydrating TraceEventMetadataEnvelope and accessing StepTraceMetadataDTO and TokenUsage attributes directly.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_studio_simulation_returns_strict_dtos">
      <input>valid simulation requests for workflow, step, and prompt block</input>
      <expected>returns instances of WorkflowSimulationResponse, StepSimulationResponse, PromptBlockSimulationResponse with typed properties</expected>
      <category>positive</category>
    </contract>
    <contract id="2" name="test_provider_extra_params_extra_forbidden">
      <input>ProviderExtraParamsDTO(temperature=0.7, unknown_field="invalid")</input>
      <expected>raises pydantic.ValidationError on unknown extra field</expected>
      <category>negative</category>
    </contract>
    <contract id="3" name="test_provider_extra_params_type_strictness">
      <input>ProviderExtraParamsDTO(max_output_tokens="two_thousand")</input>
      <expected>raises pydantic.ValidationError on type mismatch</expected>
      <category>negative</category>
    </contract>
    <contract id="4" name="test_step_trace_metadata_extra_forbidden">
      <input>StepTraceMetadataDTO(task_blueprint="step_1", fake_key=123)</input>
      <expected>raises pydantic.ValidationError on forbidden extra field</expected>
      <category>negative</category>
    </contract>
    <contract id="5" name="test_seed_vault_sanitization_clean_dump">
      <input>run scripts/sanitize_seed_vault.py --reseed --test</input>
      <expected>exits 0, zero unregistered keys, zero validation errors, orphan step_blueprints eradicated</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop and seed vault verification on Phase 2 targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/studio/ backend_v2/api/routers/studio/ backend_v2/services/blueprint.py backend_v2/worker.py backend_v2/models/v2_core.py backend_v2/models/dtos/studio.py --test</command>
    <command>uv run python scripts/sanitize_seed_vault.py --reseed --test</command>
    <command>uv run python scripts/audit_database_atoms.py --strict</command>
  </validation_gate>
</execution_protocol>

