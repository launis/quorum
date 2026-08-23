# Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation

**Overview:** Migrate Layer 1 global mandates into base system prompt static caching prefix across `PromptFactory` and `MatrixSensorPromptBuilder`, eliminate `find_value_by_key` reflection loop and `hasattr`/`getattr` calls in favor of `MechanicalAnchorsPayload` DTO, eradicate 7 `.get()` fallback chains via `ExecutionTimeResolver`, and replace `LocalizationCompiler` lazy fallback with Fail-Fast validation.

**Target Files:**
- `[NEW]` @[backend_v2/models/domain/mechanical_anchors.py]
- `[MODIFY]` @[backend_v2/models/domain/__init__.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L379-L543]
- `[NEW]` @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L22-L227]
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py#L22-L195]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_execution_time_resolver.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L251-L273] Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Wave 1 (Phases 1-4) in @[backend_v2/models/v2_core.py#L325-L340], @[backend_v2/models/prompts/global_mandates.py], @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290], @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L22-L227], and @[backend_v2/services/orchestrator/localization_compiler.py#L22-L195]. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in prompt_factory.py#L39-L290, matrix_sensor_prompt_builder.py#L18-L207, and localization_compiler.py#L22-L195.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `GLOBAL_MANDATES_XML` removed from user payload and injected into Layer 1 of `base_system_prompt` static prefix in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290].
    - [ ] `GLOBAL_MANDATES_XML` prepended into Layer 1 of static caching prefix in @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L40-L95].
    - [ ] `MechanicalAnchorsPayload` domain model created with strict typing and `model_config = ConfigDict(strict=True, extra="forbid")`.
    - [ ] Reflection loop `find_value_by_key` and all `hasattr`/`getattr` calls eradicated from @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169], replaced by typed `MechanicalAnchorsPayload` model.
    - [ ] Hardcoded slug checks replaced by polymorphic type checking in `prompt_factory.py` (specifically `category_id in ("matrix", PromptBlockCategory.MATRIX)`).
    - [ ] `ExecutionTimeResolver` created in `backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py` and 7 `.get()` fallback chains for `execution_time` eradicated in prompt_factory.py#L86-L132.
    - [ ] Lazy fallback `LANGUAGE_NAMES.get(..., "English")` in @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] and @[backend_v2/services/orchestrator/localization_compiler.py#L117-L195] replaced with Fail-Fast `AppException(VALIDATION_FAILED)`.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test`.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/localization_compiler.py --test`.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
    <knowledge_item>@[ki_strict_sdui_serialization.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/models/domain/mechanical_anchors.py]</backend>
    <backend>@[backend_v2/models/domain/__init__.py]</backend>
    <backend>@[backend_v2/models/v2_core.py#L379-L543]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L22-L227]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py#L22-L195]</backend>
    <test>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_execution_time_resolver.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]</test>
  </touched_artifacts>

  <anti_targets>
    - Do NOT inject dynamic execution variables into Layer 1 static prefix.
    - Do NOT re-introduce `getattr` or `hasattr` reflection in compiler services.
    - Do NOT use naked dictionary lookups for context data.
    - Do NOT use fallback chains (`.get(..., default)`) for mandatory localization languages.
  </anti_targets>

  <step id="1" name="Global Mandates Static Prefix Migration">
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290]:
      1. Remove `GLOBAL_MANDATES_XML` from `exec_params` (dynamic user payload).
      2. Inject `GLOBAL_MANDATES_XML.strip()` into Layer 1 of `base_system_prompt` (static prefix).
      3. Enforce exact Layer 1-3 assembly order: `GLOBAL_MANDATES_XML.strip()` -> persona instruction (or default `"You are a highly accurate, structured evaluation assistant."`) -> `<ROLE_DIRECTIVE>` -> `<EXTRACTION_PROTOCOL>` -> `<CRITERIA_GUIDELINES>` -> MCP instructions.</action>
    <action>In @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L40-L95]:
      1. Import `GLOBAL_MANDATES_XML` from `backend_v2.models.prompts.global_mandates`.
      2. In `build_caching_prefix`, prepend `GLOBAL_MANDATES_XML.strip()` into Layer 1 of `system_content` before compiled criteria blocks.</action>
    <constraint invariant="static_first_caching_topology">Global system instructions must reside 100% in the static caching prefix and never in dynamic execution parameters.</constraint>
  </step>

  <step id="2" name="Mechanical Anchors &amp; Execution Time Resolver Decomposition">
    <action>Create [NEW] @[backend_v2/models/domain/mechanical_anchors.py]:
      1. Define `MechanicalAnchorsPayload(V2CoreBase)` with fields: `word_count: int = Field(default=0)`, `say_do_gap: float = Field(default=0.0)`, `automation_bias: float = Field(default=0.0)`, `performative_patterns: list[PerformativePattern] = Field(default_factory=list)`.
      2. Implement `from_context(cls, data: dict[str, Any] | None) -> MechanicalAnchorsPayload` to extract anchors deterministically from context maps without reflection loops.
      3. Implement `to_xml(self) -> str` to generate `<mechanical_anchors>` XML string.
      4. Export in @[backend_v2/models/domain/__init__.py] and re-export in @[backend_v2/models/v2_core.py#L379-L543].</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290]:
      1. Delete `find_value_by_key` reflection loop at @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169] and eradicate all `hasattr` and `getattr` calls.
      2. Replace hardcoded slug check (`"matrix_causal_analyst"`, `"block_taskperformativity"`) with polymorphic category check (specifically `b.category_id in ("matrix", PromptBlockCategory.MATRIX)`).
      3. Construct `MechanicalAnchorsPayload.from_context(llm_context_data)` and serialize via `payload.to_xml()`.</action>
    <demolish>REMOVE: `find_value_by_key` reflection loop at @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169]. REPLACE WITH: typed `MechanicalAnchorsPayload`.</demolish>
    <action>Create [NEW] @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]:
      1. Define `ExecutionTimeResolver` class with `@staticmethod resolve(llm_context_data: dict[str, Any] | None, execution_id: str | None = None) -> datetime.datetime | None`.
      2. Implement deterministic resolution sequence: (A) Client dynamic inputs (`raw_inputs.dynamic_inputs`), (B) Disk file mtime for execution inputs, (C) Database metadata timestamps (`metadata.created_at`, `raw_inputs.timestamp`).
      3. In `prompt_factory.py`, replace 7 `.get()` fallback chains with `execution_time = ExecutionTimeResolver.resolve(llm_context_data, execution_id)`.</action>
    <demolish>REMOVE: 7 `.get()` fallback chains at prompt_factory.py#L86-L132. REPLACE WITH: `ExecutionTimeResolver.resolve()`.</demolish>
    <action>In @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] and @[backend_v2/services/orchestrator/localization_compiler.py#L117-L195]:
      1. In `compile_static_instructions` and `compile_dynamic_instructions`, replace `LANGUAGE_NAMES.get(target_locale.split("-")[0].lower(), "English")` with explicit dictionary membership check.
      2. If target language key is not in `LANGUAGE_NAMES`, log error and raise `AppException(message=f"Unsupported target locale '{target_locale}'", status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})`.</action>
    <demolish>REMOVE: `LANGUAGE_NAMES.get(..., "English")` at @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] and @[backend_v2/services/orchestrator/localization_compiler.py#L117-L195]. REPLACE WITH: Fail-Fast `AppException(VALIDATION_FAILED)`.</demolish>
    <constraint invariant="anti_god_file_dumping">Every discrete domain concept (mechanical anchors, execution time resolution) MUST reside in its own dedicated module.</constraint>
    <constraint invariant="universal_fail_fast">Missing or invalid localization keys MUST fail fast with AppException instead of falling back to English defaults.</constraint>
  </step>

  <step id="3" name="Unit Test Modernization &amp; ISTQB Negative Partition Coverage">
    <action>Modify @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]:
      1. Update assertions to verify `GLOBAL_MANDATES_XML` (`<global_system_mandates>`) is in `payload.base_system_prompt` and NOT in `payload.user_payload`.
      2. Modernize anchor tests to test `MechanicalAnchorsPayload` with typed metrics and phrase patterns.
      3. Add negative test verifying that `PromptFactory` contains zero `hasattr` or `getattr` calls via AST inspection.</action>
    <action>Modify @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py]:
      1. Update assertions to verify `GLOBAL_MANDATES_XML` is present in `payload.base_system_prompt` alongside role persona and extraction protocol.</action>
    <action>Create [NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_execution_time_resolver.py]:
      1. Positive Test: Resolves client-supplied `document_date` from `dynamic_inputs`.
      2. Positive Test: Resolves physical input file `st_mtime` from `data/files/executions/<id>/inputs/`.
      3. Positive Test: Resolves context metadata timestamp fallback.
      4. Negative Test 1: Empty context dictionary returns `None`.
      5. Negative Test 2: Invalid context types return `None` safely without exception.</action>
    <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py]:
      1. Test supported locales (specifically: `"en"`, `"fi"`, `"sv"`, `"de"`, `"fr"`, `"es"`) resolve successfully.
      2. Negative Test 1: Unsupported locale in `compile_static_instructions` raises `AppException` with `ErrorCodes.VALIDATION_FAILED` (400).
      3. Negative Test 2: Unsupported locale in `compile_dynamic_instructions` raises `AppException` with `ErrorCodes.VALIDATION_FAILED` (400).</action>
    <action>Modify @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]:
      1. Add test asserting `GLOBAL_MANDATES_XML` is present in `build_caching_prefix` static system message.</action>
    <constraint invariant="anti_happy_path_mandate">Every modified service MUST have dedicated negative test cases asserting Fail-Fast behavior on invalid inputs.</constraint>
  </step>

  <validation_gate>
    <action>Execute Prompt Factory Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test`</action>
    <action>Execute Execution Time Resolver Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py --test`</action>
    <action>Execute Localization Compiler Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/localization_compiler.py --test`</action>
    <action>Execute Matrix Sensor Prompt Builder Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py --test`</action>
    <action>Execute Global Backend Quality Gate: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
  </validation_gate>
</execution_protocol>
```
