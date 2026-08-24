# Phase 8: Clean Stack Compiler Layer Assembly

**Overview:** Update PromptFactory, LocalizationCompiler, SimulationService, and MatrixSensorPromptBuilder to use pattern matching across polymorphic AnyPromptBlock variants, assembling deterministic Zero-XML fields into strict XML hierarchies.
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L42-L187]
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py#L23-L216]
- `[MODIFY]` @[backend_v2/services/studio/simulation_service.py#L28-L270]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L232]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_simulation_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] Phase 8: Clean Stack Compiler Layer Assembly

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify baseline state from Phase 7 in @[backend_v2/models/domain/prompt_blocks.py], @[backend_v2/models/v2_core.py], and @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]. Confirm that AnyPromptBlock is a strict discriminated union with MatrixPromptBlock, SystemRulePromptBlock, PersonaPromptBlock, and ProtocolPromptBlock.</action>
    <action>Look forward: Verify requirements for Phase 8 in @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] and ensure prompt_factory.py, localization_compiler.py, simulation_service.py, and matrix_sensor_prompt_builder.py dispatch cleanly via pattern matching.</action>
    <constraint invariant="zero_legacy_state_support">Zero tolerance for legacy hasattr/getattr fallback bridges or raw string category comparisons.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `prompt_factory.py` dispatches polymorphic blocks via `match block:` to extract discrete instruction fields (`role_enforcement`, `protocol_instructions`, `instruction_text`) without unvalidated property lookups.
    - [x] `prompt_factory.py` uses `isinstance(block_model, MatrixPromptBlock)` and checks `block_model.scales` safely for atom-to-block mapping without MyPy union attribute errors.
    - [x] `localization_compiler.py` dispatches polymorphic blocks via `match block:` to extract discrete instruction fields (`instruction_text`, `role_enforcement`, `protocol_instructions`, `objective`) and substitute `{TARGET_LANGUAGE}` and `{CURRENT_DATE}`.
    - [x] `simulation_service.py` dispatches polymorphic blocks via `match data:` to extract discrete instruction fields cleanly, rendering Zero-XML fields and matrix scales without accessing unvalidated properties.
    - [x] `matrix_sensor_prompt_builder.py` instantiates concrete `SystemRulePromptBlock` instances in `_create_ephemeral_block`, compiles Zero-XML fields (`objective`, `evaluation_rules`, `banned_concepts`) into XML tags, and formats `theory_context` without `source_url`.
    - [x] Unit test suites `test_prompt_factory.py`, `test_localization_compiler.py`, `test_simulation_service.py`, and `test_matrix_sensor_prompt_builder.py` pass 100% with ISTQB negative partition coverage.
    - [x] Quality gates pass: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/simulation_service.py --test`.
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
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L42-L187]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py#L23-L216]</backend>
    <backend>@[backend_v2/services/studio/simulation_service.py#L28-L270]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L232]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_simulation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT call `PromptBlock(...)` as a constructor; instantiate concrete sub-models (`SystemRulePromptBlock`, `MatrixPromptBlock`, etc.) or parse via `PromptBlockAdapter.validate_python(...)`.
    - Do NOT access non-existent `ai_description` on sub-models without matching or checking availability.
    - Do NOT include `source_url` inside prompt context XML.
    - Do NOT use duck typing (`hasattr`, `getattr`) for field extraction.
  </anti_targets>

  <step id="1" name="PromptFactory Polymorphic Assembly Modernization">
    <action>Update @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L42-L187]:
      1. Import concrete prompt block models `MatrixPromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`, `SystemRulePromptBlock` from `backend_v2.models.domain.prompt_blocks`.
      2. Modernize grounded step check on line 103:
         ```python
         is_grounded_step = any(isinstance(b, MatrixPromptBlock) for b in criteria_blocks)
         ```
      3. In `PromptFactory.build`:
         - Modernize Layer 1 Persona resolution (lines 114-117):
           ```python
           persona = "You are a highly accurate, structured evaluation assistant."
           if execution_persona_block:
               match execution_persona_block:
                   case PersonaPromptBlock(role_enforcement=role_text) if role_text:
                       persona = role_text.strip()
                   case SystemRulePromptBlock(instruction_text=text) if text:
                       persona = text.strip()
                   case _ if execution_persona_block.ai_description:
                       persona = execution_persona_block.ai_description.strip()
           base_system_prompt += f"\n\n{persona}"
           ```
         - Modernize Layer 2 Role Directive resolution (lines 120-122):
           ```python
           if role_block:
               role_text = ""
               match role_block:
                   case PersonaPromptBlock(role_enforcement=text) if text:
                       role_text = text.strip()
                   case SystemRulePromptBlock(instruction_text=text) if text:
                       role_text = text.strip()
                   case _ if role_block.ai_description:
                       role_text = role_block.ai_description.strip()
               if role_text:
                   base_system_prompt += f"\n\n<ROLE_DIRECTIVE>\n{role_text}\n</ROLE_DIRECTIVE>"
           ```
         - Modernize Layer 2 Protocol Directive resolution (lines 124-127):
           ```python
           if protocol_block:
               proto_text = ""
               match protocol_block:
                   case ProtocolPromptBlock(protocol_instructions=text) if text:
                       proto_text = text.strip()
                   case SystemRulePromptBlock(instruction_text=text) if text:
                       proto_text = text.strip()
                   case _ if protocol_block.ai_description:
                       proto_text = protocol_block.ai_description.strip()
               if proto_text:
                   base_system_prompt += f"\n\n<EXTRACTION_PROTOCOL>\n{proto_text}\n</EXTRACTION_PROTOCOL>"
           ```
         - Modernize `atom_to_block_ids` mapping loop (lines 159-160):
           ```python
           for block_model in criteria_blocks:
               if isinstance(block_model, MatrixPromptBlock) and block_model.scales:
                   b_id = block_model.id
                   if not b_id:
                       continue
                   for scale in block_model.scales:
                       for claim in scale.claims:
                           tda_assertions = claim.tda_assertions
                           if tda_assertions and len(tda_assertions) > 0:
                               for tda in tda_assertions:
                                   aid = str(tda.tda_id)
                                   if aid not in atom_to_block_ids:
                                       atom_to_block_ids[aid] = set()
                                   mock_block_set = atom_to_block_ids[aid]
                                   mock_block_set.add(b_id)
                           else:
                               msg = f"PromptBlock '{b_id}' claim is missing mandatory 'tda_assertions' during runtime."
                               logger.error("[%s] %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                               raise AppException(
                                   message=msg,
                                   status_code=500,
                                   details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                               )
           ```</action>
    <constraint invariant="polymorphic_promptblock_mandate">PromptFactory must dispatch prompt blocks via pattern matching on concrete sub-types.</constraint>
  </step>

  <step id="2" name="LocalizationCompiler Pattern Matching Dispatch &amp; Exception Tightening">
    <action>Update @[backend_v2/services/orchestrator/localization_compiler.py#L23-L216]:
      1. Import concrete prompt block models `MatrixPromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`, `SystemRulePromptBlock` from `backend_v2.models.domain.prompt_blocks`. Also import `ValidationError` from `pydantic`.
      2. In `resolve_i18n`: Tighten `except Exception as e:` on line 55 to `except (ValidationError, ValueError) as e:`.
      3. In `compile_static_instructions(self, blocks: list[PromptBlock], target_locale: str) -> str`:
         - Filter: `for block in blocks:` where `not isinstance(block, MatrixPromptBlock) and block.category_id != PromptBlockCategory.RUNTIME_VARIABLES:`
         - Extract instruction text polymorphically:
           ```python
           desc = ""
           match block:
               case SystemRulePromptBlock(instruction_text=text) if text:
                   desc = text
               case PersonaPromptBlock(role_enforcement=text) if text:
                   desc = text
               case ProtocolPromptBlock(protocol_instructions=text) if text:
                   desc = text
               case _ if block.ai_description:
                   desc = block.ai_description
           ```
         - If `not desc`:
           ```python
           block_id = block.id
           msg = f"PromptBlock '{block_id}' is missing mandatory instruction text."
           logger.error(
               "PromptBlock is missing mandatory instruction text.",
               extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
           )
           raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
           ```
         - Replace `{TARGET_LANGUAGE}` with `target_lang_name`.
         - Append `<STATIC_INSTRUCTION label="{label}">\n{desc}\n</STATIC_INSTRUCTION>`.
      4. In `compile_dynamic_instructions(self, blocks: list[PromptBlock], target_locale: str, execution_time: datetime.datetime | str | None = None) -> str`:
         - For blocks where `block.category_id == PromptBlockCategory.RUNTIME_VARIABLES`:
           ```python
           label = self.resolve_i18n(block.label, "en")
           desc = ""
           match block:
               case SystemRulePromptBlock(instruction_text=text) if text:
                   desc = text
               case _ if block.ai_description:
                   desc = block.ai_description
           if not desc:
               block_id = block.id
               msg = f"PromptBlock '{block_id}' is missing mandatory 'instruction_text' or 'ai_description'."
               logger.error(
                   "PromptBlock is missing mandatory instruction text.",
                   extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
               )
               raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
           ```
           Perform `{CURRENT_DATE}`, `{DYNAMIC_TIME}`, `{TARGET_LANGUAGE}` substitutions.
           Append `<DYNAMIC_INSTRUCTION label="{label}">\n{desc}\n</DYNAMIC_INSTRUCTION>`.</action>
    <constraint invariant="cross_language_mapping_mandate">All dynamic language tags must map strictly to supported language taxonomies without lazy defaults.</constraint>
  </step>

  <step id="3" name="StudioSimulationService Zero-XML &amp; Matrix Rendering">
    <action>Update @[backend_v2/services/studio/simulation_service.py#L28-L270]:
      1. In `simulate_prompt_block(self, initiator: TokenData, data: PromptBlock, mock_inputs: dict[str, Any]) -> dict[str, Any]`:
         - Modernize base text extraction via exhaustive pattern matching:
           ```python
           match data:
               case MatrixPromptBlock():
                   rendered = data.ai_description or ""
               case SystemRulePromptBlock():
                   rendered = data.instruction_text or data.ai_description or ""
               case PersonaPromptBlock():
                   rendered = data.role_enforcement or data.ai_description or ""
               case ProtocolPromptBlock():
                   rendered = data.protocol_instructions or data.ai_description or ""
           ```
         - If `isinstance(data, MatrixPromptBlock) and data.scales:`
           Render `\n\n--- EVALUATION SCALES ---\n`, score points, claim labels, and `tda.concept_description` lines.
      2. In `simulate_step(self, initiator: TokenData, data: Step, mock_inputs: dict[str, Any])`:
         Ensure prompt block rendering resolves `sim["rendered_prompt"]` cleanly.</action>
    <constraint invariant="fail_fast_hydration_mandate">Missing referenced blocks or malformed models must Fail-Fast with structured errors.</constraint>
  </step>

  <step id="4" name="MatrixSensorPromptBuilder Ephemeral Instantiation &amp; XML Assembly">
    <action>Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L232]:
      1. Import concrete `SystemRulePromptBlock` from `backend_v2.models.domain.prompt_blocks`.
      2. Update `_create_ephemeral_block`:
         ```python
         @staticmethod
         def _create_ephemeral_block(
             block_id: str, category_id: PromptBlockCategory, ai_desc: str
         ) -> SystemRulePromptBlock:
             """Helper to create a valid SystemRulePromptBlock for in-memory compilation."""
             return SystemRulePromptBlock(
                 id=block_id,
                 slug=block_id,
                 organization_id="system",
                 label=I18nText(default_locale="en", translations={"en": block_id}),
                 description=I18nText(default_locale="en", translations={"en": block_id}),
                 instruction_text=ai_desc,
                 ai_description=ai_desc,
                 category_id=category_id,
                 type=BlockDataType.INSTRUCTION,
                 output_extensions=[],
             )
         ```
      3. In `build_caching_prefix`:
         - If `matrix_context` is provided and `matrix_context.matrix_objective`:
           Append ephemeral `SystemRulePromptBlock` with `ai_desc=matrix_context.matrix_objective`.
         - If `matrix_context.theory_grounding` and `matrix_context.theory_grounding.citation_reference`:
           Wrap citation into `<theory_context>\n{citation}\n</theory_context>` while strictly excluding `source_url`.
         - Prepend `GLOBAL_MANDATES_XML.strip()` to Layer 1 of static prefix.</action>
    <constraint invariant="ephemeral_caching_topology">The static caching prefix must be 100% deterministic and static across executions.</constraint>
  </step>

  <step id="5" name="Unit Test Modernization &amp; ISTQB Negative Partition Coverage">
    <action>Update test fixtures and add negative partition tests across test files:
      1. @[backend_v2/tests/unit/services/studio/test_simulation_service.py]:
         - Replace `PromptBlock(...)` constructor calls in tests (`test_simulate_prompt_block_simple`, `test_simulate_prompt_block_none_ai_description`, `test_simulate_prompt_block_matrix_scales`, `test_simulate_step_success`) with concrete sub-models:
           - `SystemRulePromptBlock` for `SYSTEM_RULE` blocks with `instruction_text` and `ai_description`.
           - `MatrixPromptBlock` for `MATRIX` blocks with `scales`.
           - `PersonaPromptBlock` for `AGENT_ROLE` blocks with `role_enforcement` and `ai_description`.
         - Add negative partition test `test_simulate_prompt_block_polymorphic_subtypes` verifying `PersonaPromptBlock`, `ProtocolPromptBlock`, `SystemRulePromptBlock`, and `MatrixPromptBlock` rendering.
      2. @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]:
         - Add unit test `test_create_ephemeral_block_returns_system_rule_prompt_block` proving `_create_ephemeral_block` returns a concrete `SystemRulePromptBlock` instance.
         - Verify negative partition test `test_build_compiled_prompt_empty_assertion_question_raises_app_exception` passes cleanly.
      3. @[backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py]:
         - Add test cases covering `PersonaPromptBlock`, `ProtocolPromptBlock`, `SystemRulePromptBlock` in `compile_static_instructions`.
         - Add negative test `test_compile_static_instructions_missing_instruction_text_raises_configuration_error` for `SystemRulePromptBlock(instruction_text=None, ai_description=None)`.
      4. @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]:
         - Add polymorphic test cases passing concrete `PersonaPromptBlock(role_enforcement=...)`, `ProtocolPromptBlock(protocol_instructions=...)`, and `SystemRulePromptBlock(instruction_text=...)` as role, protocol, and persona blocks.
         - Verify negative test `test_prompt_factory_missing_tda_assertions` passes cleanly.</action>
    <constraint invariant="anti_happy_path_mandate">Every test file must maintain at least 2 negative partition tests for invalid inputs, missing fields, or AppException paths.</constraint>
  </step>

  <validation_gate>
    <action>Execute Prompt Factory Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py`</action>
    <action>Execute Localization Compiler Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py`</action>
    <action>Execute Simulation Service Tests: `uv run pytest backend_v2/tests/unit/services/studio/test_simulation_service.py`</action>
    <action>Execute Matrix Sensor Prompt Builder Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`</action>
    <action>Execute AST XML Sovereignty Guardrails: `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py`</action>
    <action>Execute Backend Audit Loop on all modified targets:
      `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py --test`
      `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/localization_compiler.py --test`
      `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/simulation_service.py --test`
      `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py --test`
    </action>
  </validation_gate>
</execution_protocol>
```



