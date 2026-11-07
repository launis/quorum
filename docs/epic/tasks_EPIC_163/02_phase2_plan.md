<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# Phase 2: Pydantic V2 Schema Strictness — Zero Silent Defaults (`QGR020` Check 20C) & 100% PEP 593 `Annotated` (`QGR020` Check 20B)

**Overview:** Eliminate `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` (8 files, 14 fields) and `RESIDUAL_BARE_FIELD_FILES` (26 files, 209 fields) from `@[scripts/_ast_guardrails.py]`. Specifically: (1) remove all 14 silent string defaults (`= ""`, `= "unknown"`, `= "system"`) on identity, relational, and display fields across `@[backend_v2/models/auth.py#L797-L826]`, `@[backend_v2/models/auth.py#L1361-L1437]`, `@[backend_v2/models/domain/metadata.py#L21-L38]`, `@[backend_v2/models/domain/system_config.py#L210-L260]`, `@[backend_v2/models/domain/system_config.py#L377-L437]`, `@[backend_v2/models/dtos/mcp.py#L393-L431]`, `@[backend_v2/models/dtos/mcp.py#L520-L533]`, `@[backend_v2/models/dtos/mcp.py#L651-L682]`, `@[backend_v2/models/dtos/studio.py#L89-L156]`, `@[backend_v2/models/view/sdui.py#L228-L253]`, `@[backend_v2/utils/finops_trace_analyzer.py#L92-L111]`, and `@[scripts/ablation_live_executor.py#L344-L365]`; and (2) convert all 209 bare `field: T = Field(...)` declarations across the 26 files in `RESIDUAL_BARE_FIELD_FILES` to PEP 593 `Annotated[T, Field(...)]` syntax (`pydantic_annotated_fields_mandate`).

**Source:** `@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`

**Target Files:**
- `[MODIFY] @[backend_v2/models/auth.py#L797-L826]`
- `[MODIFY] @[backend_v2/models/auth.py#L1361-L1437]`
- `[MODIFY] @[backend_v2/models/domain/metadata.py#L21-L38]`
- `[MODIFY] @[backend_v2/models/domain/system_config.py#L210-L260]`
- `[MODIFY] @[backend_v2/models/domain/system_config.py#L377-L437]`
- `[MODIFY] @[backend_v2/models/dtos/mcp.py#L393-L431]`
- `[MODIFY] @[backend_v2/models/dtos/mcp.py#L520-L533]`
- `[MODIFY] @[backend_v2/models/dtos/mcp.py#L651-L682]`
- `[MODIFY] @[backend_v2/models/dtos/studio.py#L89-L156]`
- `[MODIFY] @[backend_v2/models/view/sdui.py#L228-L253]`
- `[MODIFY] @[backend_v2/utils/finops_trace_analyzer.py#L92-L111]`
- `[MODIFY] @[scripts/ablation_live_executor.py#L344-L365]`
- `[MODIFY] @[backend_v2/core/hook_registry.py#HookDefinition]`
- `[MODIFY] @[backend_v2/core/registry.py#L78-L99]`
- `[MODIFY] @[backend_v2/exceptions.py#ProblemDetails]`
- `[MODIFY] @[backend_v2/models/chunking.py#DocumentChunk]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L216-L394]`
- `[MODIFY] @[backend_v2/models/domain/inputs.py#ExpectedInput]`
- `[MODIFY] @[backend_v2/models/domain/matrix.py#ScaleItem]`
- `[MODIFY] @[backend_v2/models/domain/output_profile.py#L44-L355]`
- `[MODIFY] @[backend_v2/models/domain/prompt_blocks.py#L38-L61]`
- `[MODIFY] @[backend_v2/models/domain/step.py#L42-L194]`
- `[MODIFY] @[backend_v2/models/domain/system_config.py#SystemConfigBase]`
- `[MODIFY] @[backend_v2/models/domain/workflow.py#L25-L213]`
- `[MODIFY] @[backend_v2/models/dtos/context_variables.py#PromptContextVariablesDTO]`
- `[MODIFY] @[backend_v2/models/dtos/engine.py#PromptEngineRequest]`
- `[MODIFY] @[backend_v2/models/dtos/hook_state.py#NormalizationHookState]`
- `[MODIFY] @[backend_v2/models/dtos/quote_evidence.py#L143-L251]`
- `[MODIFY] @[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]`
- `[MODIFY] @[backend_v2/models/dtos/theory_manifest.py#TheoryManifestDTO]`
- `[MODIFY] @[backend_v2/models/dtos/workflow_schema.py#WorkflowInputFieldSchema]`
- `[MODIFY] @[backend_v2/models/execution_core.py#ExecutionSummarySnapshot]`
- `[MODIFY] @[backend_v2/models/llm.py#TokenUsage]`
- `[MODIFY] @[backend_v2/models/state.py#AdapterContext]`
- `[MODIFY] @[backend_v2/models/view/sdui.py#GlobalScoreBlock]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#PackedSourcePayload]`
- `[MODIFY] @[scripts/diff_executions.py#StepTelemetrySummary]`
- `[MODIFY] @[scripts/reconcile_storage.py#L58-L69]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/auth.py#L797-L826]`**<br>**`@[backend_v2/models/auth.py#L1361-L1437]`**<br>**`@[backend_v2/models/domain/metadata.py#L21-L38]`**<br>**`@[backend_v2/models/domain/system_config.py#L210-L260]`**<br>**`@[backend_v2/models/domain/system_config.py#L377-L437]`**<br>**`@[backend_v2/models/dtos/mcp.py#L393-L431]`**<br>**`@[backend_v2/models/dtos/mcp.py#L520-L533]`**<br>**`@[backend_v2/models/dtos/mcp.py#L651-L682]`**<br>**`@[backend_v2/models/dtos/studio.py#L89-L156]`**<br>**`@[backend_v2/models/view/sdui.py#L228-L253]`**<br>**`@[backend_v2/utils/finops_trace_analyzer.py#L92-L111]`**<br>**`@[scripts/ablation_live_executor.py#L344-L365]`** | Silent string defaults (`= ""`, `= "unknown"`, `= "system"`) on identity, relational, and display fields (`target_id`, `storage_mode`, `updated_by`, `sys_initiator_id`, `name`, `slug`, `gateway_id`, `mcp_gateway_id`, `title`, `step_id`, `id`) exempted under `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` (`QGR020` Check 20C). | Require explicit caller values on all 14 fields (and explicit nullable `str \| None = None` on `WorkflowCreateDTO.mcp_gateway_id`), synchronize callers and `@[backend_v2/tests/factories/model_factories.py]`, and delete `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` from `@[scripts/_ast_guardrails.py]`. | Zero custom `@field_validator` shims for empty-string fallback coercion; fail fast at Pydantic V2 schema validation. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/utils/finops_trace_analyzer.py scripts/ablation_live_executor.py --test --ast-strict` |
| **`@[backend_v2/core/hook_registry.py#HookDefinition]`**<br>**`@[backend_v2/core/registry.py#L78-L99]`**<br>**`@[backend_v2/exceptions.py#ProblemDetails]`**<br>**`@[backend_v2/models/chunking.py#DocumentChunk]`**<br>**`@[backend_v2/models/domain/execution.py#L216-L394]`**<br>**`@[backend_v2/models/domain/inputs.py#ExpectedInput]`**<br>**`@[backend_v2/models/domain/matrix.py#ScaleItem]`**<br>**`@[backend_v2/models/domain/output_profile.py#L44-L355]`**<br>**`@[backend_v2/models/domain/prompt_blocks.py#L38-L61]`**<br>**`@[backend_v2/models/domain/step.py#L42-L194]`**<br>**`@[backend_v2/models/domain/system_config.py#SystemConfigBase]`**<br>**`@[backend_v2/models/domain/workflow.py#L25-L213]`**<br>**`@[backend_v2/models/dtos/context_variables.py#PromptContextVariablesDTO]`**<br>**`@[backend_v2/models/dtos/engine.py#PromptEngineRequest]`**<br>**`@[backend_v2/models/dtos/hook_state.py#NormalizationHookState]`**<br>**`@[backend_v2/models/dtos/quote_evidence.py#L143-L251]`**<br>**`@[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]`**<br>**`@[backend_v2/models/dtos/theory_manifest.py#TheoryManifestDTO]`**<br>**`@[backend_v2/models/dtos/workflow_schema.py#WorkflowInputFieldSchema]`**<br>**`@[backend_v2/models/execution_core.py#ExecutionSummarySnapshot]`**<br>**`@[backend_v2/models/llm.py#TokenUsage]`**<br>**`@[backend_v2/models/state.py#AdapterContext]`**<br>**`@[backend_v2/models/view/sdui.py#GlobalScoreBlock]`**<br>**`@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#PackedSourcePayload]`**<br>**`@[scripts/diff_executions.py#StepTelemetrySummary]`**<br>**`@[scripts/reconcile_storage.py#L58-L69]`**<br>**`@[scripts/_ast_guardrails.py]`** | Legacy `field: T = Field(...)` bare declarations across 26 files exempted under `RESIDUAL_BARE_FIELD_FILES` (`QGR020` Check 20B). | Convert all 209 fields across all 26 files to PEP 593 `Annotated[T, Field(...)]` syntax (with `= default` outside `Annotated` only for valid non-identity defaults) and delete `RESIDUAL_BARE_FIELD_FILES` from `@[scripts/_ast_guardrails.py]`. | Zero bare `Field(...)` assignments anywhere in `backend_v2/` or `scripts/`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/ backend_v2/models/ backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py scripts/ --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 completion in `@[docs/epic/EPIC_163_tracker.md]` and read `@[scripts/_ast_guardrails.py]` (`RESIDUAL_DEFAULT_VALUE_MODEL_FILES`, `RESIDUAL_BARE_FIELD_FILES`, and `_ZERO_DEFAULT_FIELD_NAMES`).</action>
    <action>Look forward: Verify Step 2.1 removes all 14 silent defaults across the 8 files in `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and updates callers/factories, Step 2.2 converts all bare `Field(...)` declarations in `backend_v2/core/`, `backend_v2/exceptions.py`, and `backend_v2/models/domain/` to PEP 593 `Annotated[T, Field(...)]`, and Step 2.3 converts all bare `Field(...)` declarations in `backend_v2/models/dtos/`, `backend_v2/models/view/`, `backend_v2/services/`, and `scripts/` and deletes both `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES` from `@[scripts/_ast_guardrails.py]`.</action>
    <constraint invariant="pydantic_annotated_fields_mandate">Every Pydantic field using `Field(...)` MUST declare metadata inside `Annotated[T, Field(...)]`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md] and @[docs/epic/EPIC_163_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/auth.py]</backend>
    <backend>@[backend_v2/models/domain/metadata.py]</backend>
    <backend>@[backend_v2/models/domain/system_config.py]</backend>
    <backend>@[backend_v2/models/dtos/mcp.py]</backend>
    <backend>@[backend_v2/models/dtos/studio.py]</backend>
    <backend>@[backend_v2/models/view/sdui.py]</backend>
    <backend>@[backend_v2/utils/finops_trace_analyzer.py]</backend>
    <backend>@[scripts/ablation_live_executor.py]</backend>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/core/registry.py]</backend>
    <backend>@[backend_v2/exceptions.py]</backend>
    <backend>@[backend_v2/models/chunking.py]</backend>
    <backend>@[backend_v2/models/domain/execution.py]</backend>
    <backend>@[backend_v2/models/domain/inputs.py]</backend>
    <backend>@[backend_v2/models/domain/matrix.py]</backend>
    <backend>@[backend_v2/models/domain/output_profile.py]</backend>
    <backend>@[backend_v2/models/domain/prompt_blocks.py]</backend>
    <backend>@[backend_v2/models/domain/step.py]</backend>
    <backend>@[backend_v2/models/domain/workflow.py]</backend>
    <backend>@[backend_v2/models/dtos/context_variables.py]</backend>
    <backend>@[backend_v2/models/dtos/engine.py]</backend>
    <backend>@[backend_v2/models/dtos/hook_state.py]</backend>
    <backend>@[backend_v2/models/dtos/quote_evidence.py]</backend>
    <backend>@[backend_v2/models/dtos/schema_manifest.py]</backend>
    <backend>@[backend_v2/models/dtos/theory_manifest.py]</backend>
    <backend>@[backend_v2/models/dtos/workflow_schema.py]</backend>
    <backend>@[backend_v2/models/execution_core.py]</backend>
    <backend>@[backend_v2/models/llm.py]</backend>
    <backend>@[backend_v2/models/state.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]</backend>
    <backend>@[scripts/diff_executions.py]</backend>
    <backend>@[scripts/reconcile_storage.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`RESIDUAL_DEFAULT_VALUE_MODEL_FILES` is deleted from `@[scripts/_ast_guardrails.py]`, and all 8 previously exempted files require explicit identity, relational, and display fields (`QGR020` Check 20C).</item>
    <item>`RESIDUAL_BARE_FIELD_FILES` is deleted from `@[scripts/_ast_guardrails.py]`, and all 26 previously exempted files use PEP 593 `Annotated[T, Field(...)]` syntax (`QGR020` Check 20B).</item>
    <item>`@[backend_v2/tests/factories/model_factories.py]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` pass 100% under `--ast-strict`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT duplicate `Field(...)` both inside `Annotated[T, Field(...)]` and on the right-hand side `= Field(...)` (`eleven_point_ast_dict_eradication_and_boundary_firewall`).</anti_target>
    <anti_target>Do NOT replace `= ""` on identity/display fields with another non-`None` placeholder string (`zero_defaults_mandate`).</anti_target>
  </anti_targets>

  <step id="2.1" name="Eradicate Silent Identity, Relational &amp; Display Defaults Across All 8 Files in RESIDUAL_DEFAULT_VALUE_MODEL_FILES (QGR020 Check 20C)">
    <action>In @[backend_v2/models/auth.py#L797-L826] and @[backend_v2/models/auth.py#L1361-L1437], remove silent defaults `= ""` on `ImpersonationResponse.target_id`, `= "unknown"` on `TenantSecretDTO.storage_mode`, and `= "system"` on `TenantSecretDTO.updated_by`. In @[backend_v2/models/domain/metadata.py#L21-L38], remove silent default `= "system"` on `sys_initiator_id`. In @[backend_v2/models/domain/system_config.py#L210-L260] and @[backend_v2/models/domain/system_config.py#L377-L437], remove silent defaults `= ""` on `SystemConfigModelRegistry.name` and `SystemConfigMCPGateways.slug`.</action>
    <action>In @[backend_v2/models/dtos/mcp.py#L393-L431], @[backend_v2/models/dtos/mcp.py#L520-L533], and @[backend_v2/models/dtos/mcp.py#L651-L682], remove silent defaults `= ""` on `gateway_id` and `= "unknown"` on `name`. In @[backend_v2/models/dtos/studio.py#L89-L156], update `mcp_gateway_id` on `WorkflowCreateDTO` from `= ""` to `Annotated[str | None, Field(default=None, ...)] = None`. In @[backend_v2/models/view/sdui.py#L228-L253], remove silent default `= ""` on `ReportView.title`. In @[backend_v2/utils/finops_trace_analyzer.py#L92-L111], remove silent default `= "unknown"` on `TraceStepRecord.step_id`. In @[scripts/ablation_live_executor.py#L344-L365], remove silent defaults `= ""` on `SeedRegistryEntryDTO.id` and `SeedRegistryEntryDTO.name`. Synchronize `@[backend_v2/tests/factories/model_factories.py]` and all callers instantiating these models.</action>
    <constraint invariant="zero_defaults_mandate">Identity, relational, and display fields (`id`, `slug`, `name`, `title`, `storage_mode`, `updated_by`, `target_id`, `step_id`, `gateway_id`, `sys_initiator_id`) MUST NOT declare non-`None` scalar defaults.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/auth.py backend_v2/models/domain/metadata.py backend_v2/models/domain/system_config.py backend_v2/models/dtos/mcp.py backend_v2/models/dtos/studio.py backend_v2/models/view/sdui.py backend_v2/utils/finops_trace_analyzer.py scripts/ablation_live_executor.py backend_v2/tests/factories/model_factories.py --test --ast-strict</audit_command>
  </step>

  <step id="2.2" name="Convert Bare Field(...) Declarations in Core Registries, Exceptions &amp; Domain Models to PEP 593 Annotated (QGR020 Check 20B Part 1)">
    <action>In @[backend_v2/core/hook_registry.py#HookDefinition], @[backend_v2/core/registry.py#L78-L99], @[backend_v2/exceptions.py#ProblemDetails], @[backend_v2/models/chunking.py#DocumentChunk], @[backend_v2/models/domain/execution.py#L216-L394], @[backend_v2/models/domain/inputs.py#ExpectedInput], @[backend_v2/models/domain/matrix.py#ScaleItem], @[backend_v2/models/domain/output_profile.py#L44-L355], @[backend_v2/models/domain/prompt_blocks.py#L38-L61], @[backend_v2/models/domain/step.py#L42-L194], @[backend_v2/models/domain/system_config.py#SystemConfigBase], and @[backend_v2/models/domain/workflow.py#L25-L213], convert every `field: T = Field(...)` declaration to PEP 593 `Annotated[T, Field(...)]` syntax.</action>
    <constraint invariant="pydantic_annotated_fields_mandate">Never combine bare type annotations with `= Field(...)`; place `Field(...)` inside `Annotated[T, Field(...)]`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/hook_registry.py backend_v2/core/registry.py backend_v2/exceptions.py backend_v2/models/chunking.py backend_v2/models/domain/ --test --ast-strict</audit_command>
  </step>

  <step id="2.3" name="Convert Bare Field(...) Declarations in DTOs, View Models, Services &amp; Scripts and Delete QGR020 Residual Ledgers (QGR020 Check 20B Part 2)">
    <action>In @[backend_v2/models/dtos/context_variables.py#PromptContextVariablesDTO], @[backend_v2/models/dtos/engine.py#PromptEngineRequest], @[backend_v2/models/dtos/hook_state.py#NormalizationHookState], @[backend_v2/models/dtos/quote_evidence.py#L143-L251], @[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO], @[backend_v2/models/dtos/theory_manifest.py#TheoryManifestDTO], @[backend_v2/models/dtos/workflow_schema.py#WorkflowInputFieldSchema], @[backend_v2/models/execution_core.py#ExecutionSummarySnapshot], @[backend_v2/models/llm.py#TokenUsage], @[backend_v2/models/state.py#AdapterContext], @[backend_v2/models/view/sdui.py#GlobalScoreBlock], @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#PackedSourcePayload], @[scripts/diff_executions.py#StepTelemetrySummary], and @[scripts/reconcile_storage.py#L58-L69], convert every `field: T = Field(...)` declaration to PEP 593 `Annotated[T, Field(...)]` syntax.</action>
    <action>In @[scripts/_ast_guardrails.py] and @[backend_v2/tests/unit/scripts/test_ast_guardrails.py], delete `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES` from `__all__`, module constants, and `QuorumGuardrailVisitor`, and update unit test assertions to verify zero residual exemptions for `QGR020`.</action>
    <constraint invariant="ast_guardrail_mandate">Static AST guardrail `QGR020` MUST enforce Check 20B and Check 20C across 100% of files with zero residual exemption sets.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py scripts/diff_executions.py scripts/reconcile_storage.py scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_qgr020_passes_across_all_models_and_scripts_with_zero_residual_sets" category="positive">
      <input>Scan all 31 files previously in `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES` via `scan_files_for_guardrails`</input>
      <expected>Returns 0 `QGR020` violations with both residual sets removed from `scripts/_ast_guardrails.py`</expected>
    </test>
    <test name="test_report_view_and_tenant_secret_dto_reject_missing_required_fields" category="negative">
      <input>Instantiate `ReportView` without `title` or `TenantSecretDTO` without `storage_mode` / `updated_by`</input>
      <expected>Raises `pydantic.ValidationError` immediately (no silent `""`, `"unknown"`, or `"system"` fallback)</expected>
    </test>
    <test name="test_qgr020_flags_bare_field_assignment_as_fatal" category="negative">
      <input>Pydantic model snippet containing `count: int = Field(default=0, description="Count")` scanned by `scan_source_code_for_guardrails`</input>
      <expected>Emits `GuardrailSeverity.FATAL` `QGR020` Check 20B violation</expected>
    </test>
    <test name="test_qgr020_flags_silent_string_default_on_identity_field_as_fatal" category="boundary">
      <input>Pydantic model snippet containing `title: Annotated[str, Field(default="", description="Title")] = ""` scanned by `scan_source_code_for_guardrails`</input>
      <expected>Emits `GuardrailSeverity.FATAL` `QGR020` Check 20C violation</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 2 quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/ backend_v2/models/ backend_v2/utils/finops_trace_analyzer.py backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py scripts/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```

