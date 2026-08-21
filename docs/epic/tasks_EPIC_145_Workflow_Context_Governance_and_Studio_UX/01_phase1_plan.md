# Phase 1: Cross-Domain DTO Parity, Freezed Code Generation Lock & Pre-Implementation Tech Debt Cleanups (Contract First & Zero Duct-Tape)

**Overview:** Synchronously update Python Pydantic V2 Step and StepRule models and Flutter Dart Freezed StepRule and NodeStrategy (llm and logic union variants) models with `is_system_core` and `is_synthesis_source`. Update SynthesisConfigDTO with matrix explanation overrides, add SYSTEM_PROTECTED_RESOURCE error code, update Settings with synthesis limits (retaining `max_synthesis_evaluations=40` default until Phase 3 Unbounded Mode consumer logic is deployed), remediate tech debt in StudioWorkflowService, lock Freezed code generation, and update unit tests. **NOTE: All `SynthesisPayloadCompressor` modifications are DEFERRED to Phase 3 to avoid redundant double-touch (Phase 3 completely rewrites this file).**
**Target Files:**
- `[MODIFY]` @[backend_v2/models/v2_core.py#L712-L801]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L804-L836]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L1073-L1090]
- `[MODIFY]` @[backend_v2/settings.py#L51-L710]
- `[MODIFY]` @[backend_v2/exceptions.py#L99-L277]
- `[DEFERRED TO PHASE 3]` ~~@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]~~ (Tier 0 Mutation 2: Phase 3 completely rewrites this file; all tech debt deferred)
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L448-L479]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L62]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart#L76-L116]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/workflow_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics (EPIC 144, EPIC 143). Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/v2_core.py#L712-L801], @[backend_v2/settings.py#L51-L710], and @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `is_system_core: bool = False` added to Python `Step` model in @[backend_v2/models/v2_core.py#L712-L801].
    - [ ] `is_synthesis_source: bool = True` added to Python `StepRule` model in @[backend_v2/models/v2_core.py#L804-L836].
    - [ ] `max_quotes_per_matrix: int | None = None` and `max_unmet_criteria: int | None = None` added to `SynthesisConfigDTO` in @[backend_v2/models/v2_core.py#L1073-L1090].
    - [ ] `SYSTEM_PROTECTED_RESOURCE = "SYSTEM_PROTECTED_RESOURCE"` added to `ErrorCodes` in @[backend_v2/exceptions.py#L99-L277].
    - [ ] `max_synthesis_evaluations` field gains `ge=0` constraint (default `40` retained until Phase 3 deploys Unbounded Mode consumer logic) and `max_synthesis_reasoning_length: int = 300` added in @[backend_v2/settings.py#L51-L710].
    - [ ] ~~`SynthesisPayloadCompressor` tech debt~~ **DEFERRED TO PHASE 3** (Tier 0 Mutation 2: avoids redundant double-touch before Phase 3 comprehensive rewrite).
    - [ ] `StudioWorkflowService.save_step` duck-typing `getattr(data, "organization_id", None)` replaced with direct typed attribute `data.organization_id` at @[backend_v2/services/studio/workflow_service.py#L448-L479].
    - [ ] Dart Freezed models `StepRule` (@[client_app_v2/lib/features/studio/models/workflow.dart#L54-L62]) updated with `isSynthesisSource` (default true) and `NodeStrategy.llm` / `NodeStrategy.logic` (@[client_app_v2/lib/features/studio/models/workflow.dart#L76-L116]) updated with `isSystemCore` (default false).
    - [ ] Freezed code generation executed via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build`.
    - [ ] `workflow_test.dart` updated and passing for new fields and defaults.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/exceptions.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `seed_data.json` in Phase 1 (reserved for Phase 2 Vault Protocol).
    - Do NOT modify `workflow_step_card.dart` or `step_builder_view.dart` UI widgets in Phase 1 (reserved for Phase 4).
    - Do NOT add loose fallback defaults or duck-typing `.get()` access in DTO models.
  </anti_targets>

  <step id="1" name="Pre-Implementation Technical Debt Cleanups">
    <!-- Tier 0 Mutation 2: SynthesisPayloadCompressor model_copy and [:300] tech debt DEFERRED to Phase 3 (comprehensive rewrite avoids redundant double-touch) -->
    <action>In @[backend_v2/services/studio/workflow_service.py#L448-L479], eliminate duck-typing `getattr(data, "organization_id", None)` in `save_step` and replace with direct typed attribute access `data.organization_id`.</action>
    <demolish>REMOVE: getattr(data, "organization_id", None) duck-typing at @[backend_v2/services/studio/workflow_service.py#L448-L479]. REPLACE WITH: data.organization_id typed access.</demolish>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116], replace Finnish docstring comment at line 69 with English equivalent: `/// Sealed Classes Mandate: Unknown/Fallback union types are strictly forbidden.`.</action>
    <demolish>REMOVE: Finnish docstring comment '/// Polymorfisille luokille ei sallita Unknown/Fallback -tyyppejä.' at @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116]. REPLACE WITH: '/// Sealed Classes Mandate: Unknown/Fallback union types are strictly forbidden.'.</demolish>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-existing technical debt in touched files must be resolved in Phase 1 before new features are added.</constraint>
  </step>

  <step id="2" name="Backend Pydantic Models & Settings Update">
    <action>In @[backend_v2/models/v2_core.py#L712-L801], add `is_system_core: Annotated[bool, Field(description="Whether this step blueprint is a protected system foundational component.")] = False` to `Step` model.</action>
    <action>In @[backend_v2/models/v2_core.py#L804-L836], add `is_synthesis_source: Annotated[bool, Field(description="Whether this step's narrative text output is forwarded to the synthesis LLM context.")] = True` to `StepRule` model.</action>
    <action>In @[backend_v2/models/v2_core.py#L1073-L1090], add `max_quotes_per_matrix: Annotated[int | None, Field(description="Per-profile override for quotes per matrix in explanations.")] = None` and `max_unmet_criteria: Annotated[int | None, Field(description="Per-profile override for unmet criteria per matrix.")] = None` to `SynthesisConfigDTO`.</action>
    <action>In @[backend_v2/exceptions.py#L99-L277], add `SYSTEM_PROTECTED_RESOURCE = "SYSTEM_PROTECTED_RESOURCE"` to `ErrorCodes`.</action>
    <action>In @[backend_v2/settings.py#L51-L710], add `ge=0` constraint to the EXISTING `max_synthesis_evaluations` field (retain current default `= 40`; default change to `0` is DEFERRED to Phase 3 alongside Unbounded Mode consumer logic per Tier 0 Mutation 1). Add `max_synthesis_reasoning_length: Annotated[int, Field(description="Maximum character length for semantic reasoning in synthesis payloads")] = 300` to `Settings`.</action>
    <constraint invariant="strict_configuration_segregation">Global limits must be stored in settings.py without magic numbers.</constraint>
  </step>

  <step id="3" name="Frontend Dart Freezed Models & Code Generation Lock">
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L62], add `@Default(true) @JsonKey(name: 'is_synthesis_source') bool isSynthesisSource` to `StepRule` constructor.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart#L76-L116], add `@Default(false) @JsonKey(name: 'is_system_core') bool isSystemCore` to BOTH `NodeStrategy.llm` and `NodeStrategy.logic` sealed union variants.</action>
    <action>Run Freezed code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build`.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Backend and Frontend DTOs must maintain strict 1:1 cross-domain parity.</constraint>
  </step>

  <step id="4" name="Workflow Model Unit Tests">
    <action>Update @[client_app_v2/test/features/studio/models/workflow_test.dart] to test deserialization of `isSystemCore` and `isSynthesisSource` with defaults and explicit overrides.</action>
    <action>Tier 0 Mutation 4: Rename existing test group `'Epic 11 Phase B: NodeStrategy Strict Parsing'` to `'NodeStrategy Strict Parsing'` to comply with `internal_language_and_epic_ban`.</action>
    <test_contracts>
      <test name="test_step_rule_deserializes_is_synthesis_source_default_true" category="positive">
        <input>{"id": "sr_1234567890abcdef", "task_blueprint": "sp_1234567890abcdef"}</input>
        <expected>isSynthesisSource == true</expected>
      </test>
      <test name="test_step_rule_deserializes_is_synthesis_source_explicit_false" category="positive">
        <input>{"id": "sr_1234567890abcdef", "task_blueprint": "sp_1234567890abcdef", "is_synthesis_source": false}</input>
        <expected>isSynthesisSource == false</expected>
      </test>
      <test name="test_node_strategy_llm_deserializes_is_system_core_default_false" category="positive">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "llm", "model_strategy": "fast"}</input>
        <expected>isSystemCore == false</expected>
      </test>
      <test name="test_node_strategy_llm_deserializes_is_system_core_explicit_true" category="positive">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "llm", "model_strategy": "fast", "is_system_core": true}</input>
        <expected>isSystemCore == true</expected>
      </test>
      <test name="test_node_strategy_logic_deserializes_is_system_core_explicit_true" category="positive">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "logic", "hook": "my_hook", "is_system_core": true}</input>
        <expected>isSystemCore == true</expected>
      </test>
      <!-- Tier 0 Mutation 3: Negative ISTQB tests per anti_happy_path_mandate -->
      <test name="test_node_strategy_rejects_unknown_extra_key_with_is_system_core" category="negative">
        <input>{"id": "st_1234567890abcdef", "slug": "test", "name": {"default_locale": "en"}, "type": "llm", "model_strategy": "fast", "is_system_core": false, "unknown_forbidden_key": "should_crash"}</input>
        <expected>CheckedFromJsonException thrown (disallowUnrecognizedKeys enforced)</expected>
      </test>
      <test name="test_step_rule_rejects_is_synthesis_source_wrong_type" category="negative">
        <input>{"id": "sr_1234567890abcdef", "task_blueprint": "sp_1234567890abcdef", "is_synthesis_source": "not_a_bool"}</input>
        <expected>CheckedFromJsonException or TypeError thrown (strict bool typing enforced)</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`</action>
    <action>Execute Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --test`</action>
    <action>Execute Workflow Model Test: `uv run flutter test client_app_v2/test/features/studio/models/workflow_test.dart`</action>
  </validation_gate>
</execution_protocol>
```
