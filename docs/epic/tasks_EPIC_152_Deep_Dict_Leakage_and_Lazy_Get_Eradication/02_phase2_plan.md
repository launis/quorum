# Phase 2: Domain Model & Event Sourcing Hardening, Dynamic Input Closed Unions & Isolated DTO Immutability

**Overview:** Hardening domain execution models, event sourcing structures, and ingress DTOs to enforce strict zero permissive typing. Eliminate raw dictionary coercion, enforce closed discriminated unions for dynamic workflow inputs via IngressInputValue and DomainInputValue, isolate all sub-engine manifests into frozen, immutable Pydantic V2 DTOs, and eradicate dynamic reflection (getattr, hasattr, object.__setattr__) and duck-typing across domain models, adapters, and ingress resolvers.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/domain/execution.py#L47-L176]
- `[MODIFY]` @[backend_v2/models/domain/inputs.py#L16-L91]
- `[MODIFY]` @[backend_v2/models/state.py#L57-L158]
- `[MODIFY]` @[backend_v2/models/dtos/ingress.py#L50-L68]
- `[MODIFY]` @[backend_v2/models/dtos/hook_state.py#L20-L48]
- `[MODIFY]` @[backend_v2/models/dtos/atom_result.py#L63-L128]
- `[MODIFY]` @[backend_v2/llm/adapters/vertex_adapter.py#L360-L440]
- `[MODIFY]` @[backend_v2/llm/handler.py#L390-L435]
- `[MODIFY]` @[backend_v2/services/document_extraction.py#L111-L169]
- `[MODIFY]` @[backend_v2/services/ingress/smart_ingress_resolver.py#L45-L125]
- `[MODIFY]` @[backend_v2/models/dtos/base.py#L47-L59]
- `[NEW]` @[backend_v2/models/dtos/theory_manifest.py]
- `[NEW]` @[backend_v2/models/dtos/schema_manifest.py]
- `[NEW]` @[backend_v2/tests/unit/models/dtos/test_atom_result.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/domain/test_execution.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/domain/test_inputs.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/test_state.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established QGR018 guardrails and resolved baseline technical debt.</action>
    <action>Look forward: Verify that Phase 3 synthesis reducers and downstream processors expect strongly typed IngressInputValue and frozen DTO contracts.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/02_phase2_plan.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Closed discriminated unions IngressInputValue and DomainInputValue are defined and enforced in @[backend_v2/models/domain/inputs.py#L16-L91].</item>
    <item>Method _coerce_raw_inputs_dict is completely demolished from @[backend_v2/models/dtos/hook_state.py#L20-L48].</item>
    <item>Method _resolve_matrix_sampling_strategy in @[backend_v2/models/domain/execution.py#L104-L110] is hardened, eliminating isinstance(data, dict) and # noqa: QGR012.</item>
    <item>New strongly typed DTOs InjectedTheoryManifestDTO and GeneratedSchemaManifestDTO are created with ConfigDict(strict=True, extra="forbid", frozen=True).</item>
    <item>EvaluatedAtomDTO and EvaluationFactsDTO strictly type all atom scoring and verification facts in @[backend_v2/models/dtos/atom_result.py#L63-L128].</item>
    <item>AtomResultDTO.validate_cognitive_vs_system_state eliminates object.__setattr__ and # noqa: QGR001 in favor of Fail-Fast ValueError validation.</item>
    <item>VertexAdapter.sanitize_messages in @[backend_v2/llm/adapters/vertex_adapter.py#L360-L440] eradicates getattr, tc.get(), and # noqa: QGR001 via OpenAIToolCallDTO pre-validation.</item>
    <item>ModelGardenHandler.discover_ai_studio_models in @[backend_v2/llm/handler.py#L390-L435] eradicates getattr and # noqa: QGR001 via direct SDK model attribute access.</item>
    <item>DocumentExtractionService.process_ingress_payload in @[backend_v2/services/document_extraction.py#L111-L169] eradicates duck-typing and # noqa: QGR012 by checking isinstance(val, Base64Attachment).</item>
    <item>SmartIngressResolver.resolve in @[backend_v2/services/ingress/smart_ingress_resolver.py#L45-L125] eradicates Python 2 comma exceptions and types inputs with IngressInputValue.</item>
    <item>ResolvedIngressDTO in @[backend_v2/models/dtos/ingress.py#L50-L68] operates with zero dictionary fallbacks.</item>
    <item>DataStarvationEvent in @[backend_v2/models/dtos/base.py#L47-L59] verified and enforced with authoritative event_type: Literal["starvation"] = "starvation".</item>
    <item>Comprehensive unit test coverage achieved in [NEW] @[backend_v2/tests/unit/models/dtos/test_atom_result.py], test_inputs.py, and test_execution.py.</item>
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
    <forbidden>Do NOT modify SDUI mappers or presentation serializers during Phase 2 (reserved for Phase 6; includes GenericStatusResponseDTO).</forbidden>
    <forbidden>Do NOT modify two-pass atomizer or synthesis payload compressor in Phase 2 (reserved for Phase 3).</forbidden>
    <forbidden>Do NOT introduce fallback dictionary parsing in Pydantic validators.</forbidden>
    <forbidden>Do NOT create Phase 5 MCP and Sensor DTOs during Phase 2 (specifically quarantined for Phase 5: MCPToolDeclarationDTO, TavilySearchRequestDTO, SensorValidationContextDTO).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/domain/execution.py#L47-L176]</backend>
    <backend>@[backend_v2/models/domain/inputs.py#L16-L91]</backend>
    <backend>@[backend_v2/models/state.py#L57-L158]</backend>
    <backend>@[backend_v2/models/dtos/ingress.py#L50-L68]</backend>
    <backend>@[backend_v2/models/dtos/hook_state.py#L20-L48]</backend>
    <backend>@[backend_v2/models/dtos/atom_result.py#L63-L128]</backend>
    <backend>@[backend_v2/llm/adapters/vertex_adapter.py#L360-L440]</backend>
    <backend>@[backend_v2/llm/handler.py#L390-L435]</backend>
    <backend>@[backend_v2/services/document_extraction.py#L111-L169]</backend>
    <backend>@[backend_v2/services/ingress/smart_ingress_resolver.py#L45-L125]</backend>
    <backend>@[backend_v2/models/dtos/base.py#L47-L59]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/theory_manifest.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/schema_manifest.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/models/dtos/test_atom_result.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_inputs.py]</backend>
    <backend>@[backend_v2/tests/unit/models/test_state.py]</backend>
  </touched_artifacts>

  <pre_implementation_cleanups>
    <cleanup id="C1" target="@[backend_v2/models/dtos/atom_result.py#L63-L128]">
      <description>Eradicate 4x object.__setattr__ mutations and # noqa: QGR001 comments (Lines 109, 111, 113, 121).</description>
      <remedy>Replace in-place mutation with strict Fail-Fast ValueError raises in @model_validator(mode="after").</remedy>
    </cleanup>
    <cleanup id="C2" target="@[backend_v2/llm/adapters/vertex_adapter.py#L360-L440]">
      <description>Eradicate getattr(tc, 'id', None), tc.get('id'), and # noqa: QGR001 (Lines 396-400).</description>
      <remedy>Normalize tool calls into OpenAIToolCallDTO before loop processing and access tc.id via static dot-notation.</remedy>
    </cleanup>
    <cleanup id="C3" target="@[backend_v2/llm/handler.py#L390-L435]">
      <description>Eradicate getattr(m, 'name', None) and # noqa: QGR001 (Line 414).</description>
      <remedy>Directly access m.name on typed Google GenAI SDK Model instance or validate into DiscoveredModelDTO.</remedy>
    </cleanup>
    <cleanup id="C4" target="@[backend_v2/services/document_extraction.py#L111-L169]">
      <description>Eradicate duck-typing isinstance(val, dict) and 'content_base64' in val and delete # noqa: QGR012 (Line 119).</description>
      <remedy>Inspect isinstance(val, Base64Attachment) directly on validated IngressInputValue.</remedy>
    </cleanup>
    <cleanup id="C5" target="@[backend_v2/services/ingress/smart_ingress_resolver.py#L45-L125]">
      <description>Eradicate Python 2 comma exception except ValidationError, TypeError, ValueError: (Line 88) and naked dict annotations (Lines 72, 76).</description>
      <remedy>Type resolved as dict[str, IngressInputValue] and catch with PEP 3110 syntax except (ValidationError, TypeError, ValueError):.</remedy>
    </cleanup>
    <cleanup id="C6" target="@[backend_v2/models/domain/inputs.py#L16-L91]">
      <description>Eradicate duck-typing try: 'content_base64' in v except TypeError: in prevent_base64_pollution (Lines 78-81).</description>
      <remedy>Base64 exclusion from domain models is mathematically guaranteed by DomainInputValue closed union at Rust type level.</remedy>
    </cleanup>
    <cleanup id="C7" target="@[backend_v2/models/domain/execution.py#L104-L110]">
      <description>Eradicate isinstance(data, dict) and # noqa: QGR012 in _resolve_matrix_sampling_strategy (Line 101).</description>
      <remedy>Replace mode='before' dictionary mutation with direct Field(default_factory=...) initialization.</remedy>
    </cleanup>
    <cleanup id="C8" target="@[backend_v2/models/dtos/hook_state.py#L20-L48]">
      <description>Demolish _coerce_raw_inputs_dict mode='before' validator that coerces str to dict (Lines 25-30).</description>
      <remedy>Enforce strict Pydantic V2 model validation on DomainInputValue with zero ad-hoc type coercion.</remedy>
    </cleanup>
  </pre_implementation_cleanups>

  <directives_table>
    <table_data>
| 1. Target Scope &amp; Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification &amp; Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/domain/inputs.py#L16-L91]` | Naked `dict[str, Any]` dynamic_inputs, duck-typing `try: "content_base64" in v` | Closed unions `IngressInputValue` (permitting `Base64Attachment`) and `DomainInputValue` (excluding `Base64Attachment`); strict `dict[str, IngressInputValue]` / `dict[str, DomainInputValue]` | Prune manual base64 inspection loops; Pydantic type validation enforces exclusion natively | Unit tests asserting ValidationError on arbitrary nested dicts and Base64Attachment in DomainInputValue |
| `@[backend_v2/models/domain/execution.py#L47-L176]` | `injected_theory: dict[str, Any]`, `generated_schemas: dict[str, dict[str, Any]]`, `raw_atoms: list[dict[str, Any]]`, `isinstance(data, dict)` in `_resolve_matrix_sampling_strategy` | Strongly typed frozen DTOs: `InjectedTheoryManifestDTO`, `GeneratedSchemaManifestDTO`, `list[EvaluatedAtomDTO]`; `Field(default_factory=...)` on matrix_sampling_strategy | Eliminate before-validator dictionary tampering and `# noqa: QGR012` suppression | `test_execution.py` asserting Pydantic validation with `extra="forbid"` and zero QGR012 violations |
| `@[backend_v2/models/dtos/hook_state.py#L20-L48]` | `_coerce_raw_inputs_dict` mode="before" string-to-dict coercion; naked `raw_inputs` and `dynamic_inputs` dicts | Demolish `_coerce_raw_inputs_dict`; type `raw_inputs` and `dynamic_inputs` as `dict[str, DomainInputValue]` | Demolish legacy single-string coercion hack; caller must supply valid domain input mapping | Unit tests asserting ValidationError on malformed string raw_inputs |
| `@[backend_v2/models/dtos/ingress.py#L50-L68]` | `resolved_inputs: Annotated[dict[str, Any], ...]` | Strongly typed `resolved_inputs: Annotated[dict[str, IngressInputValue], ...]` | Eliminate permissive dictionary values in ingress resolution | Unit tests in `test_smart_ingress_resolver.py` asserting typed IngressInputValue instances |
| `@[backend_v2/models/dtos/atom_result.py#L63-L128]` | `object.__setattr__(self, ...)` in-place post-validation state mutations; `# noqa: QGR001` suppressions | Strict Fail-Fast in `@model_validator(mode="after")` raising `ValueError` on contradictory cognitive states; define `EvaluatedAtomDTO` and `EvaluationFactsDTO` | Eradicate in-place mutation of frozen models; eliminate all `# noqa: QGR001` suppressions | `test_atom_result.py` verifying model immutability and ValueError on contradictory states |
| `@[backend_v2/llm/adapters/vertex_adapter.py#L360-L440]` | `getattr(tc, "id", None)`, `tc.get("id")`, `isinstance(tc, dict)`, `# noqa: QGR001`, `# noqa: QGR012` | Pre-validate tool calls into `OpenAIToolCallDTO` before sanitization loop; direct dot-notation `tc.id` | Eliminate 3-branch duck-typing ladder in `sanitize_messages` | Unit test in `test_vertex_adapter.py` verifying tool call sanitization with zero reflection |
| `@[backend_v2/llm/handler.py#L390-L435]` | `getattr(m, "name", None) or ""` reflection and `# noqa: QGR001` suppression | Direct attribute access `m.name` on typed Google GenAI SDK model or `DiscoveredModelDTO` validation | Eliminate reflection queries and empty string fallbacks | `test_llm_handler.py` asserting clean model enumeration without QGR001 suppressions |
| `@[backend_v2/services/document_extraction.py#L111-L169]` | `isinstance(val, dict) and "content_base64" in val` duck-typing; `# noqa: QGR012` suppression | Direct `isinstance(val, Base64Attachment)` inspection on validated `ingress.dynamic_inputs` | Eliminate ad-hoc dictionary checks; utilize typed `IngressInputValue` union | `test_document_extraction.py` validating attachment extraction without QGR012 |
| `@[backend_v2/services/ingress/smart_ingress_resolver.py#L45-L125]` | Python 2 `except ValidationError, TypeError, ValueError:` syntax; `resolved: dict[str, Any]` | PEP 3110 `except (ValidationError, TypeError, ValueError):`; `resolved: dict[str, IngressInputValue]` | Eradicate legacy comma exception syntax and naked dict accumulators | Unit tests in `test_smart_ingress_resolver.py` passing with typed DTO assertions |
| `@[backend_v2/models/dtos/base.py#L47-L59]` | Risk of unverified `DataStarvationEvent` discriminator in synthesis reducers | Retain and enforce authoritative `event_type: Literal["starvation"] = "starvation"` with `frozen=True` and `extra="forbid"` | Maintain flat, minimal model without redundant discriminator wrappers | Pydantic roundtrip serialization test confirming `event_type == "starvation"` |
    </table_data>
  </directives_table>

  <step id="2.1" name="Dynamic Input Closed Unions IngressInputValue &amp; DomainInputValue">
    <action>Define IngressInputValue as a closed union of allowed ingress types in @[backend_v2/models/domain/inputs.py#L16-L91]: Base64Attachment | GuidedReflectionInputDTO | str | int | float | bool | list[str].</action>
    <action>Define DomainInputValue as a closed union of validated domain inputs in @[backend_v2/models/domain/inputs.py#L16-L91]: GuidedReflectionInputDTO | str | int | float | bool | list[str] (Base64Attachment strictly excluded).</action>
    <action>Refactor WorkflowInputsIngress.dynamic_inputs to dict[str, IngressInputValue] and WorkflowInputs.dynamic_inputs to dict[str, DomainInputValue].</action>
    <action>Eradicate duck-typing try: "content_base64" in v from WorkflowInputs.prevent_base64_pollution.</action>
    <contract_freeze>
      <signature>type IngressInputValue = Annotated[Base64Attachment | GuidedReflectionInputDTO | str | int | float | bool | list[str], Field(description="Strict closed union of allowed ingress workflow input values")]</signature>
      <signature>type DomainInputValue = Annotated[GuidedReflectionInputDTO | str | int | float | bool | list[str], Field(description="Strict closed union of extracted domain inputs (Base64Attachment strictly excluded)")]</signature>
    </contract_freeze>
  </step>

  <step id="2.2" name="Domain Execution Model Hardening &amp; Demolition">
    <action>Refactor @[backend_v2/models/dtos/hook_state.py#L20-L48] to completely demolish _coerce_raw_inputs_dict.</action>
    <action>Refactor ExecutionInputsDTO.raw_inputs and dynamic_inputs to dict[str, DomainInputValue].</action>
    <action>Refactor @[backend_v2/models/domain/execution.py#L47-L176]:</action>
    <action>- Replace FrozenContext.injected_theory: dict[str, Any] with InjectedTheoryManifestDTO.</action>
    <action>- Replace FrozenContext.generated_schemas: dict[str, dict[str, Any]] with GeneratedSchemaManifestDTO.</action>
    <action>- Replace EvaluatedMatrixContextDTO.raw_atoms: list[dict[str, Any]] with list[EvaluatedAtomDTO].</action>
    <action>- Refactor ExecutionCreate._resolve_matrix_sampling_strategy to eradicate isinstance(data, dict) and # noqa: QGR012 in favor of Field(default_factory=...).</action>
    <demolish>REMOVE: `_coerce_raw_inputs_dict` in @[backend_v2/models/dtos/hook_state.py#L20-L48]. REPLACE WITH: strict Pydantic V2 model validation on DomainInputValue.</demolish>
    <demolish>REMOVE: `isinstance(data, dict)` in @[backend_v2/models/domain/execution.py#L104-L110]. REPLACE WITH: Field(default_factory=...) default initialization.</demolish>
  </step>

  <step id="2.3" name="Theory &amp; Schema Manifest DTO Creation">
    <action>Create [NEW] @[backend_v2/models/dtos/theory_manifest.py] defining InjectedTheoryManifestDTO with strictly frozen fields.</action>
    <action>Create [NEW] @[backend_v2/models/dtos/schema_manifest.py] defining GeneratedSchemaManifestDTO with strictly frozen fields.</action>
    <contract_freeze>
      <signature>class InjectedTheoryManifestDTO(V2CoreBase): model_config = ConfigDict(strict=True, extra="forbid", frozen=True)</signature>
      <signature>class GeneratedSchemaManifestDTO(V2CoreBase): model_config = ConfigDict(strict=True, extra="forbid", frozen=True)</signature>
    </contract_freeze>
  </step>

  <step id="2.4" name="Atom Result Immutability &amp; Ingress DTO Strictness">
    <action>Refactor @[backend_v2/models/dtos/atom_result.py#L63-L128]:</action>
    <action>- Eradicate 4x object.__setattr__ mutations and # noqa: QGR001 suppressions from validate_cognitive_vs_system_state.</action>
    <action>- Enforce Fail-Fast raising ValueError on contradictory states (failed atoms cannot have contextual_override, is_inverse_evidence, or source_quote; passed atoms with override/inverse must have source_quote is None).</action>
    <action>- Define EvaluatedAtomDTO and EvaluationFactsDTO with ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>Refactor @[backend_v2/models/dtos/ingress.py#L50-L68]:</action>
    <action>- Update ResolvedIngressDTO.resolved_inputs from dict[str, Any] to dict[str, IngressInputValue].</action>
  </step>

  <step id="2.5" name="LLM Handler &amp; Adapter Reflection Eradication">
    <action>Refactor @[backend_v2/llm/adapters/vertex_adapter.py#L360-L440]:</action>
    <action>- Pre-validate tool calls into OpenAIToolCallDTO before loop processing.</action>
    <action>- Access tc.id via static dot-notation, eradicating getattr, tc.get(), and # noqa: QGR001.</action>
    <action>Refactor @[backend_v2/llm/handler.py#L390-L435]:</action>
    <action>- Access m.name directly on typed Google GenAI SDK Model instance or validate via DiscoveredModelDTO.</action>
    <action>- Eradicate getattr(m, "name", None) or "" and delete # noqa: QGR001.</action>
  </step>

  <step id="2.6" name="Document Extraction &amp; Smart Ingress Hardening">
    <action>Refactor @[backend_v2/services/document_extraction.py#L111-L169]:</action>
    <action>- Inspect isinstance(val, Base64Attachment) directly on validated ingress.dynamic_inputs, eradicating duck-typing and # noqa: QGR012.</action>
    <action>Refactor @[backend_v2/services/ingress/smart_ingress_resolver.py#L45-L125]:</action>
    <action>- Replace legacy comma exception except ValidationError, TypeError, ValueError: with PEP 3110 syntax.</action>
    <action>- Type resolved container as dict[str, IngressInputValue].</action>
    <action>Verify @[backend_v2/models/dtos/base.py#L47-L59] retains DataStarvationEvent authoritative event_type: Literal["starvation"] = "starvation".</action>
  </step>

  <test_contracts>
    <test name="test_ingress_input_value_accepts_valid_types" category="positive">
      <input>Valid string, integer, float, boolean, Base64Attachment, GuidedReflectionInputDTO, and string list values.</input>
      <expected>Successfully parses into IngressInputValue union without type coercion errors.</expected>
    </test>
    <test name="test_ingress_input_value_rejects_nested_dict" category="negative">
      <input>Nested raw dictionary payload {"nested": {"key": "val"}}.</input>
      <expected>Raises Pydantic ValidationError or AppException, strictly forbidden.</expected>
    </test>
    <test name="test_domain_input_value_rejects_base64_attachment" category="negative">
      <input>Base64Attachment instance passed to DomainInputValue / WorkflowInputs.dynamic_inputs.</input>
      <expected>Raises Pydantic ValidationError Fail-Fast, mathematically preventing base64 pollution.</expected>
    </test>
    <test name="test_theory_manifest_immutability" category="boundary">
      <input>Attempting to mutate attribute on instantiated InjectedTheoryManifestDTO.</input>
      <expected>Raises ValidationError or TypeError due to frozen=True immutability.</expected>
    </test>
    <test name="test_schema_manifest_immutability" category="boundary">
      <input>Attempting to mutate attribute on instantiated GeneratedSchemaManifestDTO.</input>
      <expected>Raises ValidationError or TypeError due to frozen=True immutability.</expected>
    </test>
    <test name="test_atom_result_rejects_failed_with_contextual_override" category="negative">
      <input>AtomResultDTO with status=FAILED and contextual_override=True.</input>
      <expected>Raises ValidationError Fail-Fast with zero object.__setattr__ mutation.</expected>
    </test>
    <test name="test_atom_result_rejects_failed_with_source_quote" category="negative">
      <input>AtomResultDTO with status=FAILED and source_quote="Some quote".</input>
      <expected>Raises ValidationError Fail-Fast with zero object.__setattr__ mutation.</expected>
    </test>
    <test name="test_atom_result_rejects_passed_with_override_and_quote" category="negative">
      <input>AtomResultDTO with status=PASSED, contextual_override=True, and source_quote="Quote".</input>
      <expected>Raises ValidationError Fail-Fast with zero object.__setattr__ mutation.</expected>
    </test>
    <test name="test_vertex_adapter_sanitizes_tool_calls_without_reflection" category="positive">
      <input>Assistant message with tool_calls containing OpenAIToolCallDTO instances and dict payloads.</input>
      <expected>Sanitizes messages cleanly, accessing tc.id via static dot-notation with zero QGR001 violations.</expected>
    </test>
    <test name="test_execution_inputs_rejects_raw_string_without_coercion" category="negative">
      <input>Raw string passed to ExecutionInputsDTO(raw_inputs="hello").</input>
      <expected>Raises ValidationError Fail-Fast due to demolished _coerce_raw_inputs_dict.</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run unit tests: uv run pytest backend_v2/tests/unit/models/domain/test_execution.py backend_v2/tests/unit/models/domain/test_inputs.py backend_v2/tests/unit/models/test_state.py -v</action>
    <action>Run new atom result tests: uv run pytest backend_v2/tests/unit/models/dtos/test_atom_result.py -v</action>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/models --test</action>
    <action>Run AST guardrail check: uv run python scripts/_ast_guardrails.py backend_v2/models/domain/execution.py backend_v2/models/domain/inputs.py backend_v2/models/dtos/atom_result.py backend_v2/llm/adapters/vertex_adapter.py backend_v2/llm/handler.py backend_v2/services/document_extraction.py</action>
  </validation_gate>
</execution_protocol>
```
