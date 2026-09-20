# Phase 2: Domain Model & Event Sourcing Hardening, Dynamic Input Closed Unions & Isolated DTO Immutability

**Overview:** Hardening domain execution models, event sourcing structures, and ingress DTOs to enforce strict zero permissive typing. Eliminate raw dictionary coercion, enforce closed discriminated unions for dynamic workflow inputs via IngressInputValue, and isolate all sub-engine manifests into frozen, immutable Pydantic V2 DTOs.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/domain/execution.py]
- `[MODIFY]` @[backend_v2/models/domain/inputs.py]
- `[MODIFY]` @[backend_v2/models/state.py]
- `[MODIFY]` @[backend_v2/models/dtos/ingress.py]
- `[MODIFY]` @[backend_v2/models/dtos/hook_state.py]
- `[MODIFY]` @[backend_v2/models/dtos/atom_result.py]
- `[MODIFY]` @[backend_v2/llm/adapters/vertex_adapter.py]
- `[MODIFY]` @[backend_v2/llm/handler.py]
- `[NEW]` @[backend_v2/models/dtos/theory_manifest.py]
- `[NEW]` @[backend_v2/models/dtos/schema_manifest.py]
- `[NEW]` @[backend_v2/tests/unit/models/dtos/test_atom_result.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established QGR018 guardrails and resolved baseline technical debt.</action>
    <action>Look forward: Verify that Phase 3 synthesis reducers and downstream processors expect strongly typed IngressInputValue and frozen DTO contracts.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/02_phase2_plan.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Closed discriminated union IngressInputValue is defined and enforced in @[backend_v2/models/domain/inputs.py].</item>
    <item>Method _coerce_raw_inputs_dict is completely demolished from @[backend_v2/models/domain/execution.py].</item>
    <item>New strongly typed DTOs InjectedTheoryManifestDTO and GeneratedSchemaManifestDTO are created with ConfigDict(strict=True, extra="forbid", frozen=True).</item>
    <item>EvaluatedAtomDTO and EvaluationFactsDTO strictly type all atom scoring and verification facts in @[backend_v2/models/dtos/atom_result.py].</item>
    <item>ResolvedIngressDTO, MCPToolDeclarationDTO, TavilySearchRequestDTO, SensorValidationContextDTO, and GenericStatusResponseDTO operate with zero dictionary fallbacks.</item>
    <item>Comprehensive unit test coverage achieved in [NEW] @[backend_v2/tests/unit/models/dtos/test_atom_result.py].</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT modify SDUI mappers or presentation serializers during Phase 2 (reserved for Phase 6).</forbidden>
    <forbidden>Do NOT modify two-pass atomizer or synthesis payload compressor in Phase 2 (reserved for Phase 3).</forbidden>
    <forbidden>Do NOT introduce fallback dictionary parsing in Pydantic validators.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/domain/execution.py]</backend>
    <backend>@[backend_v2/models/domain/inputs.py]</backend>
    <backend>@[backend_v2/models/state.py]</backend>
    <backend>@[backend_v2/models/dtos/ingress.py]</backend>
    <backend>@[backend_v2/models/dtos/hook_state.py]</backend>
    <backend>@[backend_v2/models/dtos/atom_result.py]</backend>
    <backend>@[backend_v2/llm/adapters/vertex_adapter.py]</backend>
    <backend>@[backend_v2/llm/handler.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/theory_manifest.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/schema_manifest.py]</backend>
  </touched_artifacts>

  <step id="2.1" name="Dynamic Input Closed Union IngressInputValue">
    <action>Define IngressInputValue as a closed union of primitive types (str | int | float | bool | list[str]) in @[backend_v2/models/domain/inputs.py].</action>
    <action>Eradicate loose dict[str, Any] signatures from inputs and domain state models.</action>
    <contract_freeze>
      <signature>type IngressInputValue = str | int | float | bool | list[str]</signature>
    </contract_freeze>
  </step>

  <step id="2.2" name="Domain Execution Model Hardening &amp; Demolition">
    <action>Refactor @[backend_v2/models/domain/execution.py] to eradicate _coerce_raw_inputs_dict.</action>
    <action>Enforce strict Pydantic V2 parsing on all execution domain inputs, raising explicit AppException on unmapped fields.</action>
    <demolish>REMOVE: `_coerce_raw_inputs_dict` in @[backend_v2/models/domain/execution.py]. REPLACE WITH: strict Pydantic V2 model validation on IngressInputValue.</demolish>
  </step>

  <step id="2.3" name="Theory &amp; Schema Manifest DTO Creation">
    <action>Create [NEW] @[backend_v2/models/dtos/theory_manifest.py] defining InjectedTheoryManifestDTO with strictly frozen fields.</action>
    <action>Create [NEW] @[backend_v2/models/dtos/schema_manifest.py] defining GeneratedSchemaManifestDTO with strictly frozen fields.</action>
    <contract_freeze>
      <signature>class InjectedTheoryManifestDTO(BaseModel): model_config = ConfigDict(strict=True, extra="forbid", frozen=True)</signature>
      <signature>class GeneratedSchemaManifestDTO(BaseModel): model_config = ConfigDict(strict=True, extra="forbid", frozen=True)</signature>
    </contract_freeze>
  </step>

  <step id="2.4" name="Atom Result &amp; Ingress DTO Strictness">
    <action>Refactor @[backend_v2/models/dtos/atom_result.py] to define EvaluatedAtomDTO and EvaluationFactsDTO with zero loose dictionary members.</action>
    <action>Update @[backend_v2/models/dtos/ingress.py] and @[backend_v2/models/dtos/hook_state.py] with ResolvedIngressDTO, MCPToolDeclarationDTO, TavilySearchRequestDTO, SensorValidationContextDTO, and GenericStatusResponseDTO.</action>
  </step>

  <step id="2.5" name="LLM Handler &amp; Adapter Serialization Alignment">
    <action>Update @[backend_v2/llm/adapters/vertex_adapter.py] and @[backend_v2/llm/handler.py] to accept strongly typed manifests instead of raw dictionaries.</action>
    <action>Create comprehensive unit tests in [NEW] @[backend_v2/tests/unit/models/dtos/test_atom_result.py] verifying round-trip serialization parity.</action>
  </step>

  <test_contracts>
    <test name="test_ingress_input_value_accepts_valid_types" category="positive">
      <input>Valid string, integer, float, boolean, and string list values.</input>
      <expected>Successfully parses into IngressInputValue union without type coercion errors.</expected>
    </test>
    <test name="test_ingress_input_value_rejects_nested_dict" category="negative">
      <input>Nested raw dictionary payload {"nested": {"key": "val"}}.</input>
      <expected>Raises Pydantic ValidationError or AppException, strictly forbidden.</expected>
    </test>
    <test name="test_theory_manifest_immutability" category="boundary">
      <input>Attempting to mutate attribute on instantiated InjectedTheoryManifestDTO.</input>
      <expected>Raises ValidationError or TypeError due to frozen=True immutability.</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run unit tests: uv run pytest backend_v2/tests/unit/models/dtos/test_atom_result.py</action>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/models/domain/inputs.py --test</action>
  </validation_gate>
</execution_protocol>
```
