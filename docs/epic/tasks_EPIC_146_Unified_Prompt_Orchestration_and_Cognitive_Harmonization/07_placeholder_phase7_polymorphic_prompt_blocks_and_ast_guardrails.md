# Phase 7: Polymorphic AnyPromptBlock Discriminated Union & AST Guardrails

**Overview:** Refactor monolithic `PromptBlock` into strict Pydantic Discriminated Union `AnyPromptBlock` in `backend_v2/models/domain/prompt_blocks.py` and Freezed Sealed Class in Flutter (`client_app_v2/lib/features/studio/models/prompt_block.dart`), update seed registry with `TypeAdapter(AnyPromptBlock)`, maintain backward-compatible re-exports in `v2_core.py` and `simulation_service.py`, and enforce 10 AST guardrails in `test_ast_prompt_xml_sovereignty.py`.
**Target Files:**
- `[NEW]` @[backend_v2/models/domain/prompt_blocks.py]
- `[MODIFY]` @[backend_v2/models/domain/__init__.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L381-L545]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L462-L545]
- `[MODIFY]` @[backend_v2/seed/seed_registry.py]
- `[MODIFY]` @[backend_v2/models/dtos/studio.py]
- `[MODIFY]` @[backend_v2/services/studio/simulation_service.py#L140-L195]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/prompt_block.dart]
- `[NEW]` @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] Phase 7: Polymorphic AnyPromptBlock Discriminated Union & AST Guardrails

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify baseline state from Phase 6 in @[backend_v2/models/v2_core.py#L381-L545], @[backend_v2/models/domain/mechanical_anchors.py], and @[backend_v2/models/prompts/global_mandates.py]. Confirm that Layer 1 global mandates are static and reflection helpers (find_value_by_key, hasattr, getattr) are eliminated.</action>
    <action>Look forward: Verify requirements for Phase 7 in @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] and ensure seamless forward compatibility for Phase 8 Clean Stack compiler pattern matching.</action>
    <constraint invariant="zero_legacy_state_support">Zero tolerance for legacy duck-typing validators or backward compatibility bridges.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `AnyPromptBlock` discriminated union with `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock` created in [NEW] @[backend_v2/models/domain/prompt_blocks.py] with strict `ConfigDict(strict=True, extra='forbid', frozen=True)`.
    - [x] Monolithic flat `PromptBlock` and runtime duck-typing validator `pre_validate_block_consistency` removed from @[backend_v2/models/v2_core.py#L381-L545] and @[backend_v2/models/v2_core.py#L462-L545], replaced by clean re-exports of `AnyPromptBlock`, `PromptBlockBase`, `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`, and alias `PromptBlock = AnyPromptBlock`.
    - [x] `backend_v2/models/domain/__init__.py` exports all prompt block classes and registers `AnyPromptBlock` in `DOMAIN_REGISTRY`.
    - [x] `backend_v2/seed/seed_registry.py` maps `prompt_blocks` collection to `TypeAdapter(AnyPromptBlock)`.
    - [x] `backend_v2/models/dtos/studio.py` aligns `PromptBlockResponseDTO` to `AnyPromptBlock` discriminated union.
    - [x] `backend_v2/services/studio/simulation_service.py` implements polymorphic `match data:` handling across `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, and `ProtocolPromptBlock` to extract instruction text cleanly.
    - [x] Dart `PromptBlock` refactored to sealed union class with `@Freezed(unionKey: 'category_id', equal: false) sealed class PromptBlock with _$PromptBlock` in @[client_app_v2/lib/features/studio/models/prompt_block.dart] with factory constructors (`matrix`, `systemRule`, `executionPersona`, `agentRole`, `protocol`, `runtimeVariables`, `taskDefinition`) and static isolate parsers.
    - [x] 10 AST tests created in [NEW] @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py] and passing.
    - [x] Quality gates pass: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/prompt_blocks.py --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.
    - [x] Domain parity test passes: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
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
    <backend>[NEW] @[backend_v2/models/domain/prompt_blocks.py]</backend>
    <backend>@[backend_v2/models/domain/__init__.py]</backend>
    <backend>@[backend_v2/models/v2_core.py#L381-L545]</backend>
    <backend>@[backend_v2/seed/seed_registry.py]</backend>
    <backend>@[backend_v2/models/dtos/studio.py]</backend>
    <backend>@[backend_v2/services/studio/simulation_service.py#L140-L195]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</frontend>
    <backend>[NEW] @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT keep flat monolithic PromptBlock with optional fields.
    - Do NOT allow default=None on required MatrixPromptBlock fields.
    - Do NOT allow catch-all unknown union types.
    - Do NOT omit computed_min / computed_max properties from MatrixPromptBlock.
    - Do NOT break cross-domain parity between Python discriminated union and Flutter Freezed sealed union.
  </anti_targets>

  <step id="1" name="Pydantic Discriminated Union Creation &amp; Seed Registry Alignment">
    <action>Create [NEW] @[backend_v2/models/domain/prompt_blocks.py] implementing strict Pydantic V2 Discriminated Union architecture (@[ki_god_code_prevention.md], @[ki_polymorphic_rule_routing.md]):
      1. Define `StrictStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]`.
      2. Define `PromptBlockBase(V2CoreBase)` with `ConfigDict(strict=True, extra='forbid', frozen=True)` containing shared attributes:
         - `id: Annotated[str, Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$")]`
         - `slug: StrictStr`
         - `organization_id: str | None = None`
         - `label: I18nText`
         - `description: I18nText`
         - `output_extensions: list[str] = Field(default_factory=list)`
         - `ai_description: str | None = None`
         - `theory_grounding: TheoryGrounding | None = None`
      3. Define `MatrixPromptBlock(PromptBlockBase)`:
         - `category_id: Literal[PromptBlockCategory.MATRIX] = PromptBlockCategory.MATRIX`
         - `type: Literal[BlockDataType.FLOAT, BlockDataType.INT] = BlockDataType.FLOAT`
         - `is_evaluative: Literal[True] = True`
         - `allow_decimals: bool = False`
         - `allow_contextual_override: bool = False`
         - `is_lightweight_protocol: bool = False`
         - `scales: list[MatrixScale] = Field(min_length=1)`
         - `rows: list[MatrixRow] | None = None`
         - `columns: list[I18nText] | None = None`
         - `@property def computed_min(self) -> int:` returns `min(s.score for s in self.scales)`
         - `@property def computed_max(self) -> int:` returns `max(s.score for s in self.scales)`
      4. Define `SystemRulePromptBlock(PromptBlockBase)`:
         - `category_id: Literal[PromptBlockCategory.SYSTEM_RULE, PromptBlockCategory.RUNTIME_VARIABLES, PromptBlockCategory.TASK_DEFINITION] = PromptBlockCategory.SYSTEM_RULE`
         - `type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING, BlockDataType.PANEL, BlockDataType.COMPLIANCE, BlockDataType.QUESTION, BlockDataType.CRITERIA] = BlockDataType.INSTRUCTION`
         - `is_evaluative: bool = False`
         - `allow_decimals: bool = False`
         - `is_lightweight_protocol: bool = False`
         - `instruction_text: StrictStr | None = None`
      5. Define `PersonaPromptBlock(PromptBlockBase)`:
         - `category_id: Literal[PromptBlockCategory.EXECUTION_PERSONA, PromptBlockCategory.AGENT_ROLE] = PromptBlockCategory.EXECUTION_PERSONA`
         - `type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING] = BlockDataType.INSTRUCTION`
         - `is_evaluative: bool = False`
         - `allow_decimals: bool = False`
         - `is_lightweight_protocol: bool = False`
         - `role_enforcement: StrictStr | None = None`
         - `tone_directives: list[StrictStr] = Field(default_factory=list)`
      6. Define `ProtocolPromptBlock(PromptBlockBase)`:
         - `category_id: Literal[PromptBlockCategory.PROTOCOL] = PromptBlockCategory.PROTOCOL`
         - `type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING] = BlockDataType.INSTRUCTION`
         - `is_evaluative: bool = False`
         - `allow_decimals: bool = False`
         - `is_lightweight_protocol: bool = False`
         - `protocol_instructions: StrictStr | None = None`
      7. Define `AnyPromptBlock = Annotated[MatrixPromptBlock | SystemRulePromptBlock | PersonaPromptBlock | ProtocolPromptBlock, Field(discriminator="category_id")]` and type alias `PromptBlock = AnyPromptBlock`.</action>
    <action>Update @[backend_v2/models/domain/__init__.py]: Export `AnyPromptBlock`, `PromptBlockBase`, `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock` and register in `DOMAIN_REGISTRY`.</action>
    <action>Update @[backend_v2/models/v2_core.py#L381-L545]: Eradicate monolithic flat `PromptBlock` class and duck-typing validator `pre_validate_block_consistency` at @[backend_v2/models/v2_core.py#L462-L545]. Re-export `AnyPromptBlock`, `PromptBlockBase`, `MatrixPromptBlock`, `SystemRulePromptBlock`, `PersonaPromptBlock`, `ProtocolPromptBlock`, and `PromptBlock = AnyPromptBlock`.</action>
    <demolish>REMOVE: monolithic `PromptBlock` and `pre_validate_block_consistency` at @[backend_v2/models/v2_core.py#L381-L545] and @[backend_v2/models/v2_core.py#L462-L545]. REPLACE WITH: `AnyPromptBlock` discriminated union.</demolish>
    <action>Update @[backend_v2/seed/seed_registry.py]: Map `"prompt_blocks"` to `TypeAdapter(AnyPromptBlock)`.</action>
    <action>Update @[backend_v2/models/dtos/studio.py]: Align `PromptBlockResponseDTO` to `AnyPromptBlock`.</action>
    <action>Update @[backend_v2/services/studio/simulation_service.py#L140-L195]: Update `simulate_prompt_block` to polymorphically match `data` and read instruction text safely across all `AnyPromptBlock` variants.</action>
    <constraint invariant="polymorphic_promptblock_mandate">All prompt blocks must parse polymorphically through AnyPromptBlock discriminated by category_id.</constraint>
    <constraint invariant="mathematical_extrema_anchoring">computed_min and computed_max must be implemented as dynamic @property methods on MatrixPromptBlock calculating min and max from the scales array.</constraint>
  </step>

  <step id="2" name="Flutter Freezed Sealed Class Synchronous Parity">
    <action>Refactor Dart `PromptBlock` in @[client_app_v2/lib/features/studio/models/prompt_block.dart] into a Freezed sealed union class:
      1. `@Freezed(unionKey: 'category_id', equal: false) sealed class PromptBlock with _$PromptBlock`
      2. Factory constructors for each category variant matching the backend discriminator:
         - `@FreezedUnionValue('matrix') const factory PromptBlock.matrix(...)`
         - `@FreezedUnionValue('system_rule') const factory PromptBlock.systemRule(...)`
         - `@FreezedUnionValue('execution_persona') const factory PromptBlock.executionPersona(...)`
         - `@FreezedUnionValue('agent_role') const factory PromptBlock.agentRole(...)`
         - `@FreezedUnionValue('protocol') const factory PromptBlock.protocol(...)`
         - `@FreezedUnionValue('runtime_variables') const factory PromptBlock.runtimeVariables(...)`
         - `@FreezedUnionValue('task_definition') const factory PromptBlock.taskDefinition(...)`
      3. Implement computed properties for `computedMin` and `computedMax` on `MatrixPromptBlock`.
      4. Retain background isolate static parsing methods `parseInBackground` and `parseListInBackground`.</action>
    <action>Execute build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build` (`dart run build_runner build --delete-conflicting-outputs`).</action>
    <constraint invariant="sdui_contract_fracture_prevention">Backend Pydantic AnyPromptBlock and Flutter Freezed PromptBlock must maintain 1:1 cross-domain serialization parity.</constraint>
  </step>

  <step id="3" name="AST XML Sovereignty Guardrails Test Suite">
    <action>Create [NEW] @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py] with 10 static AST and model purity tests (@[ki_ast_guardrail_testing.md]):
      1. `test_ast_domain_models_strict_frozen_config`: Verifies via `ast.parse` that all classes in `backend_v2/models/domain/prompt_blocks.py` define `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`.
      2. `test_ast_any_prompt_block_discriminator`: Verifies via AST that `AnyPromptBlock` uses `Field(discriminator="category_id")`.
      3. `test_ast_matrix_prompt_block_scales_required`: Verifies via AST that `MatrixPromptBlock` defines `scales` with `min_length=1`.
      4. `test_prompt_factory_ast_no_hasattr_getattr`: Verifies via AST that `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` contains 0 `hasattr` and 0 `getattr` calls.
      5. `test_prompt_factory_ast_no_find_value_by_key`: Verifies via AST that `prompt_factory.py` contains 0 `find_value_by_key` function definitions or calls.
      6. `test_prompt_factory_ast_no_slug_checks`: Verifies via AST that `prompt_factory.py` contains 0 `.slug` accesses or comparisons.
      7. `test_prompt_factory_ast_no_naked_dicts_in_mechanical_anchors`: Verifies via AST that `prompt_factory.py` contains 0 naked dict traversals (`isinstance(x, dict)`) for mechanical anchors.
      8. `test_ast_xml_layer_ordering_compliance`: Verifies via AST/static inspection that prompt builders structure Layer 1 -> Layer 2 -> Layer 3 -> Layer 4.
      9. `test_ast_guardrail_catches_new_hasattr_getattr_negative`: Proves AST scanner detects violations by passing a mock AST node containing `hasattr`/`getattr`.
      10. `test_ast_guardrail_catches_missing_strict_model_config_negative`: Proves AST scanner detects violations by passing a mock AST node of a domain model missing `strict=True` or `extra="forbid"`.</action>
    <constraint invariant="ast_guardrail_mandate">All static architectural rules must be mathematically guarded via Python ast module scanners.</constraint>
    <constraint invariant="anti_happy_path_mandate">AST test suite must contain explicit negative tests (mock invalid nodes) proving failure interception.</constraint>
  </step>

  <validation_gate>
    <action>Execute AST Guardrails: `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py`</action>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/prompt_blocks.py --test`</action>
    <action>Execute Flutter Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`</action>
    <action>Execute Flutter Domain Parity Test: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test`</action>
  </validation_gate>
</execution_protocol>
```

