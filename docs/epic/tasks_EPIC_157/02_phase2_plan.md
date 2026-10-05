# Phase 2: System Exceptions, Hooks, LLM Caching Contract & Core Lockdown

**Overview:** Retype `AppException.details` to `dict[str, JsonValue] | None` (blast radius: 32 mypy errors in 5 files), define [NEW] `ProblemDetailDTO` with explicit `.model_dump(mode="json", exclude_none=True)` serialization at the FastAPI network boundary (`main.py`, `core/rate_limit.py`), define [NEW] `CachingPayloadResultDTO` contract owned by `BaseLLMAdapter.prepare_caching_payload`, and eradicate the remaining hook, LLM, and core violations (including dynamic model field dictionary typing in `core/registry.py`).

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L369-L405] Phase 2: System Exceptions, Hooks, LLM Caching Contract & Core Lockdown

**Target Files:**
- `[MODIFY]` @[backend_v2/exceptions.py]
- `[MODIFY]` @[backend_v2/main.py#L314-L342]
- `[MODIFY]` @[backend_v2/main.py#L441-L470]
- `[MODIFY]` @[backend_v2/core/rate_limit.py#L21-L50]
- `[MODIFY]` @[backend_v2/core/registry.py#L477-L908]
- `[MODIFY]` @[backend_v2/tests/unit/test_exceptions.py]
- `[MODIFY]` @[backend_v2/database/repositories/components/prompt_block.py]
- `[MODIFY]` @[backend_v2/services/ingress/smart_ingress_resolver.py]
- `[MODIFY]` @[backend_v2/hooks/validation.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py#L83-L564]
- `[MODIFY]` @[backend_v2/hooks/scoring/passivity_hook.py]
- `[MODIFY]` @[backend_v2/hooks/linguistics.py]
- `[MODIFY]` @[backend_v2/hooks/source_verification_hook.py]
- `[MODIFY]` @[backend_v2/llm/caching_service.py#L35-L61]
- `[MODIFY]` @[backend_v2/llm/client.py#L357-L725]
- `[MODIFY]` @[backend_v2/llm/client.py#L727-L905]
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py#L151-L166]
- `[MODIFY]` @[backend_v2/llm/adapters/ai_studio_adapter.py#L96-L290]
- `[MODIFY]` @[backend_v2/llm/adapters/anthropic_adapter.py#L20-L96]
- `[MODIFY]` @[backend_v2/llm/adapters/mock_adapter.py#L25-L39]
- `[MODIFY]` @[backend_v2/llm/adapters/openai_adapter.py#L25-L43]
- `[MODIFY]` @[backend_v2/llm/adapters/vertex_adapter.py#L115-L347]
- `[MODIFY]` @[backend_v2/llm/ingress_pipeline.py]
- `[MODIFY]` @[backend_v2/llm/schema_builder.py]
- `[MODIFY]` @[backend_v2/llm/mock_data.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_mock_data.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_mock.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/exceptions.py]`, `@[backend_v2/main.py#L314-L342]`, `@[backend_v2/main.py#L441-L470]`, `@[backend_v2/core/rate_limit.py#L21-L50]`, `@[backend_v2/tests/unit/test_exceptions.py]` | Banned permissive typing `dict[str, Any]` in RFC 7807 problem details. Banned raw dictionary returns from `to_problem_detail()`. Banned passing unvalidated dicts to Starlette `JSONResponse`. | `AppException.details: dict[str, JsonValue] \| None`. Define [NEW] `ProblemDetailDTO` with explicit fields `type`, `title`, `status`, `detail`, `instance`, `extensions`. At network boundary in `main.py` and `core/rate_limit.py`, call `.model_dump(mode="json", exclude_none=True)`. | Pruned speculative custom error serializer hierarchies; use standard Pydantic V2 JSON mode dumping. | `uv run mypy backend_v2/exceptions.py backend_v2/main.py backend_v2/core/rate_limit.py` = 0 errors. `backend_v2/tests/unit/test_exceptions.py` asserts roundtrip serialization. |
| `@[backend_v2/database/repositories/components/prompt_block.py]`, `@[backend_v2/services/ingress/smart_ingress_resolver.py]`, `@[backend_v2/hooks/validation.py]`, `@[backend_v2/hooks/input_processing.py]` | Banned passing non-JSON objects or unvalidated nested structures to `details` keyword argument of `AppException` subclasses. | Resolve 5 caller sites by passing typed `dict[str, JsonValue]` structures (`list[str]`, `dict[str, Sequence[str]]`, `list[ErrorDetails]`). | Pruned custom dict wrapper models; use typed JSON value mappings. | `uv run mypy backend_v2` reports 0 errors across all 5 exception caller files. |
| `@[backend_v2/hooks/scoring/matrix_hook.py#L83-L564]`, `@[backend_v2/hooks/scoring/passivity_hook.py]`, `@[backend_v2/hooks/linguistics.py]`, `@[backend_v2/hooks/source_verification_hook.py]` | Banned 3 parallel nested maps keyed by matrix ID (`dict[str, dict[float, LevelStatsDTO]]`, `dict[str, dict[str, ExecutionStatus]]`, `dict[str, dict[str, list[str]]]`). Banned loose dict annotations in linguistics and verification hooks. | Define [NEW] `MatrixAggregationStateDTO` encapsulating score levels, status map, and reasons. Define [NEW] `LinguisticAnalysisDTO` in `hooks/linguistics.py`. | Pruned separate DTOs for parallel maps; unify into one cohesive aggregation state model. | `uv run python scripts/audit_dict_eradication.py backend_v2/hooks --strict` reports 0 violations. |
| `@[backend_v2/llm/caching_service.py#L35-L61]`, `@[backend_v2/llm/client.py#L357-L725]`, `@[backend_v2/llm/client.py#L727-L905]`, `@[backend_v2/llm/adapters/base_adapter.py#L151-L166]`, `@[backend_v2/llm/adapters/ai_studio_adapter.py#L96-L290]`, `@[backend_v2/llm/adapters/anthropic_adapter.py#L20-L96]`, `@[backend_v2/llm/adapters/mock_adapter.py#L25-L39]`, `@[backend_v2/llm/adapters/openai_adapter.py#L25-L43]`, `@[backend_v2/llm/adapters/vertex_adapter.py#L115-L347]` | Banned anonymous tuple return `tuple[list[LLMMessageDTO] \| list[dict[str, Any]], dict[str, Any]]` from `prepare_caching_payload`. Banned provider dict materialization outside adapter boundary. | Define [NEW] `CachingPayloadResultDTO` owned by `BaseLLMAdapter.prepare_caching_payload` contract. Confine provider-native dictionary creation strictly to exempt adapter files and `provider.py`. | Pruned redundant caching serialization bridges. | `Select-String -Path backend_v2/llm/adapters/*.py, backend_v2/llm/caching_service.py -Pattern "tuple\[list\[LLMMessageDTO\]"` returns 0 matches. |
| `@[backend_v2/core/registry.py#L477-L908]`, `@[backend_v2/llm/ingress_pipeline.py]`, `@[backend_v2/llm/schema_builder.py]`, `@[backend_v2/llm/mock_data.py]`, `@[backend_v2/tests/unit/test_mock_data.py]`, `@[backend_v2/tests/unit/test_mock.py]` | Banned naked `dict[type[Any], Any]` in `MOCK_REGISTRY`. Banned untyped dynamic model field definitions in `core/registry.py`. Banned `dict[str, Any]` in `get_fallback_data`. | Retype `MOCK_REGISTRY` to `dict[type[BaseModel], BaseModel]`. Strongly type dynamic model field mappings in `core/registry.py`. Retype `get_fallback_data` to return typed `BaseModel` mock instances. | Pruned untyped registry lookups; enforce strict Pydantic model inheritance. | `uv run python scripts/audit_dict_eradication.py backend_v2/core/registry.py backend_v2/llm/mock_data.py backend_v2/llm/schema_builder.py --strict` = 0. `uv run pytest backend_v2/tests/unit/test_mock_data.py backend_v2/tests/unit/test_mock.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 completed successfully, establishing the path-based BOUNDARY_EXEMPTION_FILES SSOT, QGR026, Stage 9/10 baseline ledger, and all 30 model retypings.</action>
    <action>Look forward: Verify that retyping AppException.details, ProblemDetailDTO, and CachingPayloadResultDTO locks core system contracts before test persistence migration in Phases 3-7.</action>
    <constraint>If any Phase 1 model contract is broken or mypy baseline fails, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/02_phase2_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>AppException.details is retyped to dict[str, JsonValue] | None across backend_v2/exceptions.py.</item>
    <item>ProblemDetailDTO is implemented and returned by to_problem_detail() with .model_dump(mode="json", exclude_none=True) at FastAPI boundaries.</item>
    <item>All 32 mypy errors across the 5 exception caller files are completely resolved.</item>
    <item>prepare_caching_payload is refactored to return CachingPayloadResultDTO across BaseLLMAdapter and all 6 adapter implementations.</item>
    <item>Matrix hook parallel maps are unified into MatrixAggregationStateDTO.</item>
    <item>Core registry dynamic models and mock data registry are strongly typed.</item>
    <item>uv run mypy backend_v2 reports 0 errors.</item>
    <item>uv run python scripts/audit_dict_eradication.py backend_v2 --strict reports 0 residual violations outside in_memory_repositories.py.</item>
    <item>Global quality gate uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes cleanly.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 2 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify test persistence mocks in hooks, services, or workers during Phase 2 (quarantined strictly for Phases 3-6).</anti_target>
    <anti_target>Do NOT modify Flutter UI code during Phase 2 (quarantined strictly for Phase 8 and Phase 12).</anti_target>
    <anti_target>Do NOT remove # noqa comments or # type: ignore comments during Phase 2 (quarantined strictly for Phases 9-10).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/exceptions.py]</backend>
    <backend>@[backend_v2/main.py]</backend>
    <backend>@[backend_v2/core/rate_limit.py]</backend>
    <backend>@[backend_v2/core/registry.py]</backend>
    <backend>@[backend_v2/database/repositories/components/prompt_block.py]</backend>
    <backend>@[backend_v2/services/ingress/smart_ingress_resolver.py]</backend>
    <backend>@[backend_v2/hooks/validation.py]</backend>
    <backend>@[backend_v2/hooks/input_processing.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/passivity_hook.py]</backend>
    <backend>@[backend_v2/hooks/linguistics.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/llm/caching_service.py]</backend>
    <backend>@[backend_v2/llm/client.py]</backend>
    <backend>@[backend_v2/llm/adapters/base_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/ai_studio_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/anthropic_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/mock_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/openai_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/vertex_adapter.py]</backend>
    <backend>@[backend_v2/llm/ingress_pipeline.py]</backend>
    <backend>@[backend_v2/llm/schema_builder.py]</backend>
    <backend>@[backend_v2/llm/mock_data.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <contract name="ProblemDetailDTO">
      Define [NEW] ProblemDetailDTO with fields: type: str, title: str, status: int, detail: str, instance: str | None, extensions: dict[str, JsonValue]. ConfigDict(strict=True, extra="forbid", frozen=True).
    </contract>
    <contract name="CachingPayloadResultDTO">
      Define [NEW] CachingPayloadResultDTO owned by BaseLLMAdapter.prepare_caching_payload. ConfigDict(strict=True, extra="forbid", frozen=True).
    </contract>
    <contract name="MatrixAggregationStateDTO">
      Define [NEW] MatrixAggregationStateDTO with fields: score_levels: dict[float, LevelStatsDTO], status_map: dict[str, ExecutionStatus], reasons: dict[str, list[str]]. ConfigDict(strict=True, extra="forbid", frozen=True).
    </contract>
    <contract name="LinguisticAnalysisDTO">
      Define [NEW] LinguisticAnalysisDTO in hooks/linguistics.py. ConfigDict(strict=True, extra="forbid", frozen=True).
    </contract>
  </contract_freeze>

  <step id="1" name="System Exceptions &amp; ProblemDetailDTO RFC 7807 Network Boundary">
    <action>In `@[backend_v2/exceptions.py]`, retype AppException.details to dict[str, JsonValue] | None and define [NEW] ProblemDetailDTO returned by to_problem_detail().</action>
    <action>In `@[backend_v2/main.py#L314-L342]` and `@[backend_v2/main.py#L441-L470]`, serialize ProblemDetailDTO via .model_dump(mode="json", exclude_none=True) before passing to JSONResponse.</action>
    <action>In `@[backend_v2/core/rate_limit.py#L21-L50]`, serialize ProblemDetailDTO via .model_dump(mode="json", exclude_none=True) before passing to JSONResponse.</action>
    <action>In `@[backend_v2/tests/unit/test_exceptions.py]`, add roundtrip serialization tests for ProblemDetailDTO and non-JSON value rejection assertions.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">RFC 7807 error details must be strongly typed and serializable without naked dictionaries.</constraint>
  </step>

  <step id="2" name="Exception Details Invariant Callers Migration">
    <action>In `@[backend_v2/database/repositories/components/prompt_block.py]`, pass typed list[str] to details argument of AppException subclass.</action>
    <action>In `@[backend_v2/services/ingress/smart_ingress_resolver.py]`, pass typed dict[str, Sequence[str]] and list[str] to details argument of AppException subclasses.</action>
    <action>In `@[backend_v2/hooks/validation.py]`, pass typed warning structures conforming to dict[str, JsonValue] to details argument.</action>
    <action>In `@[backend_v2/hooks/input_processing.py]`, pass typed error details conforming to dict[str, JsonValue] to details argument.</action>
    <constraint invariant="universal_fail_fast">Exception details must satisfy the dict[str, JsonValue] | None contract without type suppressions.</constraint>
  </step>

  <step id="3" name="LLM Caching Contract &amp; Adapter Migration">
    <action>In `@[backend_v2/llm/caching_service.py#L35-L61]`, refactor prepare_caching_payload to return CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/client.py#L357-L725]` and `@[backend_v2/llm/client.py#L727-L905]`, update run_structured_task and run_chat callers of prepare_caching_payload to consume CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/adapters/base_adapter.py#L151-L166]`, declare abstract method prepare_caching_payload returning CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/adapters/ai_studio_adapter.py#L96-L290]`, implement prepare_caching_payload returning CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/adapters/anthropic_adapter.py#L20-L96]`, implement prepare_caching_payload returning CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/adapters/mock_adapter.py#L25-L39]`, implement prepare_caching_payload returning CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/adapters/openai_adapter.py#L25-L43]`, implement prepare_caching_payload returning CachingPayloadResultDTO.</action>
    <action>In `@[backend_v2/llm/adapters/vertex_adapter.py#L115-L347]`, implement prepare_caching_payload returning CachingPayloadResultDTO.</action>
    <constraint invariant="ban_anonymous_state_tuples">Anonymous tuple returns across caching services and adapters are strictly prohibited.</constraint>
  </step>

  <step id="4" name="Matrix Hook &amp; Scoring Aggregation State DTOs">
    <action>In `@[backend_v2/hooks/scoring/matrix_hook.py#L83-L564]`, define [NEW] MatrixAggregationStateDTO and replace the 3 parallel nested maps with a single typed aggregation state mapping.</action>
    <action>In `@[backend_v2/hooks/scoring/passivity_hook.py]`, update passivity penalty state extraction to consume MatrixAggregationStateDTO.</action>
    <constraint invariant="the_zero_compromise_pledge">Primitive obsession nested maps must be replaced with frozen Pydantic V2 DTOs.</constraint>
  </step>

  <step id="5" name="Linguistics &amp; Source Verification Hooks Retyping">
    <action>In `@[backend_v2/hooks/linguistics.py]`, define [NEW] LinguisticAnalysisDTO and eliminate naked dict annotations across linguistic metric calculators.</action>
    <action>In `@[backend_v2/hooks/source_verification_hook.py]`, retype verification state and context payloads to strictly typed DTO models.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero permissive typing across execution hooks.</constraint>
  </step>

  <step id="6" name="Core Registry Dynamic Models &amp; Mock Data Typing">
    <action>In `@[backend_v2/core/registry.py#L477-L908]`, replace loose dictionary annotations on dynamic model fields with typed field mappings.</action>
    <action>In `@[backend_v2/llm/ingress_pipeline.py]`, retype pipeline stage dictionaries to strongly typed Pydantic models.</action>
    <action>In `@[backend_v2/llm/schema_builder.py]`, retype schema building maps to dict[str, JsonValue].</action>
    <action>In `@[backend_v2/llm/mock_data.py]`, retype MOCK_REGISTRY to dict[type[BaseModel], BaseModel] and update get_fallback_data to return typed BaseModel mock instances.</action>
    <action>In `@[backend_v2/tests/unit/test_mock_data.py]`, update mock registry assertions for typed BaseModel returns.</action>
    <action>In `@[backend_v2/tests/unit/test_mock.py]`, update mock LLM assertions for typed model responses.</action>
    <constraint invariant="the_zero_compromise_pledge">Mock registries and schema builders must operate on typed models.</constraint>
  </step>

  <test_contracts>
    <test name="test_problem_detail_dto_roundtrip" category="positive">
      <input>AppException with status 400, title "Bad Request", and extensions {"code": "VALIDATION_FAILED"}</input>
      <expected>to_problem_detail() returns ProblemDetailDTO with exact field values</expected>
    </test>
    <test name="test_problem_detail_dto_serialization_omits_none" category="boundary">
      <input>ProblemDetailDTO with instance=None</input>
      <expected>.model_dump(mode="json", exclude_none=True) excludes the "instance" key from serialized dictionary</expected>
    </test>
    <test name="test_caching_payload_result_dto_validation" category="positive">
      <input>CachingPayloadResultDTO with messages and provider payload attributes</input>
      <expected>Validates successfully under ConfigDict(strict=True, extra="forbid")</expected>
    </test>
    <test name="test_matrix_aggregation_state_dto_rejects_unknown_attribute" category="negative">
      <input>MatrixAggregationStateDTO(score_levels={}, status_map={}, reasons={}, extra_key=123)</input>
      <expected>Raises ValidationError under extra='forbid'</expected>
    </test>
    <test name="test_linguistic_analysis_dto_validation" category="positive">
      <input>LinguisticAnalysisDTO with token counts, sentence structures, and lexical metrics</input>
      <expected>Instantiates cleanly with frozen=True</expected>
    </test>
    <test name="test_mock_registry_rejects_non_basemodel_key" category="negative">
      <input>MOCK_REGISTRY key of type object or int</input>
      <expected>Type-checker flags error under dict[type[BaseModel], BaseModel] contract</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute Type Checker: `uv run mypy backend_v2` reports 0 errors.</action>
    <action>Execute Caching Payload Scan: `Select-String -Path backend_v2/llm/adapters/*.py, backend_v2/llm/caching_service.py -Pattern "tuple\[list\[LLMMessageDTO\]"` returns 0 matches.</action>
    <action>Execute Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports 0 residual violations outside in_memory_repositories.py.</action>
    <action>Execute Unit Tests: `uv run pytest backend_v2/tests/unit/test_exceptions.py backend_v2/tests/unit/test_mock_data.py backend_v2/tests/unit/test_mock.py` passes cleanly.</action>
    <action>Execute Global Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes cleanly.</action>
  </validation_gate>
</execution_protocol>
```
