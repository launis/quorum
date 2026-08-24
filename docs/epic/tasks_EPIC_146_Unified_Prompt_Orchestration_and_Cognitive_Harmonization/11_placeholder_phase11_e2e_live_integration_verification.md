# Phase 11: End-to-End Live Integration Verification Gate & Knowledge Synchronization

**Overview:** Execute core model and blueprint parser remediation, live LLM E2E integration test verification gate, update Knowledge Item `ki_llm_extraction_architecture.md` with Zero-XML UI paradigm and 4-Layer Clean Stack Model, and synchronize `.agents/rules/05_llm_architecture.md` to mandate compiler-level XML assembly sovereignty and ban manual XML authoring in UI/seed data.

**Target Files:**
- `[MODIFY]` @[backend_v2/models/v2_core.py]
- `[MODIFY]` @[backend_v2/models/state.py]
- `[MODIFY]` @[backend_v2/services/blueprint.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_epic_chain_e2e.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_lazy_llm_simulation.py]
- `[MODIFY]` @[C:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]
- `[MODIFY]` @[.agents/rules/05_llm_architecture.md]

**Context Files:**
- `[CONTEXT]` @[backend_v2/models/prompts/global_mandates.py]
- `[CONTEXT]` @[backend_v2/models/domain/prompt_blocks.py]
- `[CONTEXT]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]
- `[CONTEXT]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]
- `[CONTEXT]` @[backend_v2/services/orchestrator/localization_compiler.py]
- `[CONTEXT]` @[backend_v2/tests/integration/test_integration_real_llm.py]
- `[CONTEXT]` @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] Phase 11: End-to-End Live Integration Verification Gate

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify baseline state from Phase 10 in @[backend_v2/seed/seed_data.json] and @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]. Confirm that seed vault pruning completed cleanly, 17 candidate blocks were pruned from step criteria, and database re-seeding passed 100%.</action>
    <action>Look forward: Verify requirements for Phase 11 in @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] and ensure:
      1. Circular import between `v2_core.py` and `state.py` is permanently eliminated.
      2. `BlueprintTransformer` utilizes `PromptBlockAdapter.validate_python` for polymorphic prompt block parsing.
      3. E2E integration test suite (`test_epic_chain_e2e.py` and `test_lazy_llm_simulation.py`) passes 100% with ISTQB negative test coverage.
      4. Live LLM E2E integration test gate passes with zero errors.
      5. Knowledge Item `@[C:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]` is updated with the Zero-XML UI paradigm and 4-Layer Clean Stack Model specification.
      6. `@[.agents/rules/05_llm_architecture.md]` is synchronized enforcing compiler-level XML generation sovereignty and strict prompt caching invariants.
    </action>
    <constraint invariant="zero_legacy_state_support">Zero tolerance for legacy fallback bridges or un-audited state. System instructions must be 100% static in Layer 1-3, dynamic context placed exclusively in Layer 4 user payload.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `@[backend_v2/models/v2_core.py]` circular import with `state.py` eliminated by removing late imports of `ErrorTraceEvent, TombstoneEvent, TraceEvent` and moving `ExecutionRecord.model_rebuild` to `state.py`.
    - [ ] `@[backend_v2/models/state.py]` updated with `ExecutionRecord.model_rebuild(_types_namespace=_state_localns)` resolving deferred annotations alongside `ExecutionCoreFields`.
    - [ ] `@[backend_v2/services/blueprint.py]` updated to import `PromptBlockAdapter` and parse blocks via `PromptBlockAdapter.validate_python(b_dict)` instead of `PromptBlock.model_validate`.
    - [ ] `@[backend_v2/tests/integration/test_epic_chain_e2e.py]` modernized with valid `mock_pb` fixtures and 3 ISTQB negative test scenarios (NEG-01: 404 on missing profile, NEG-02: 400 on missing locale, NEG-03: 500 on malformed matrix payload).
    - [ ] `@[backend_v2/tests/integration/test_lazy_llm_simulation.py]` modernized to instantiate `MatrixPromptBlock` constructor.
    - [ ] Integration suite `uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py backend_v2/tests/integration/test_lazy_llm_simulation.py` passes 100%.
    - [ ] Live LLM verification gate passes via `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` (Windows/PowerShell).
    - [ ] Knowledge Item `@[C:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]` updated with:
      1. `zero_xml_ui_paradigm`: UI capture of discrete natural-language fields (`objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`) and complete ban on manual XML entry in UI/seed data.
      2. `four_layer_clean_stack_model`: Layer 1 Global Mandates SSOT (`GLOBAL_MANDATES_XML`), Layer 2 Persona/Role Enforcement, Layer 3 Protocol/Rubric Heuristics, Layer 4 Dynamic User Execution Parameters.
      3. Static-First Caching Topology (90%+ latency reduction, 75%+ FinOps savings).
    - [ ] `@[.agents/rules/05_llm_architecture.md]` synchronized with:
      1. Rule `compiler_xml_sovereignty_mandate`: Enforcing that XML tags are generated exclusively by backend compilers (`PromptFactory`, `MatrixSensorPromptBuilder`, `LocalizationCompiler`), banning raw XML authoring in UI models and `seed_data.json`.
      2. Rule `four_layer_clean_stack_hierarchy`: Defining the 4-layer hierarchy and static-first caching topology.
    - [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2/tests/integration/test_epic_chain_e2e.py --test`.
    - [ ] Full frontend audit loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
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
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/models/state.py]</backend>
    <backend>@[backend_v2/services/blueprint.py]</backend>
    <backend>@[backend_v2/tests/integration/test_epic_chain_e2e.py]</backend>
    <backend>@[backend_v2/tests/integration/test_lazy_llm_simulation.py]</backend>
    <backend>@[.agents/rules/05_llm_architecture.md]</backend>
    <backend>@[C:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT skip live E2E verification gate.
    - Do NOT re-introduce manual XML formatting into Studio UI forms or seed data.
    - Do NOT bypass Pydantic `extra='forbid'` or strict typing.
  </anti_targets>

  <step id="1" name="Core Model Circular Import Decoupling &amp; Blueprint Adapter Fix">
    <action>In @[backend_v2/models/v2_core.py]: Eradicate the late import `from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent` at lines 1634-1644 and remove `ExecutionRecord.model_rebuild()` from `v2_core.py`.</action>
    <action>In @[backend_v2/models/state.py]: Update `from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace` and append `ExecutionRecord.model_rebuild(_types_namespace=_state_localns)` immediately following `ExecutionCoreFields.model_rebuild(_types_namespace=_state_localns)` at line 180.</action>
    <action>In @[backend_v2/services/blueprint.py]: Update import to `from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, PromptBlockAdapter`, change typing `blocks_by_id: dict[str, AnyPromptBlock]`, and replace `b = PromptBlock.model_validate(b_dict, strict=False)` at line 197 with `b = PromptBlockAdapter.validate_python(b_dict)`.</action>
  </step>

  <step id="2" name="Integration Test Suite Modernization &amp; ISTQB Negative Partitions">
    <action>In @[backend_v2/tests/integration/test_epic_chain_e2e.py]:
      1. Modernize `mock_pb` fixture to conform to `MatrixPromptBlock` schema without legacy `ai_description` and with valid BARS scales and TDA assertions.
      2. Implement 3 explicit ISTQB negative test scenarios:
         - `test_epic_chain_e2e_invalid_profile_raises_app_exception`: Assert `AppException` (status 404, `ErrorCodes.RESOURCE_NOT_FOUND`) when requesting non-existent output profile ID.
         - `test_epic_chain_e2e_missing_locale_raises_app_exception`: Assert `AppException` (status 400, `ErrorCodes.VALIDATION_FAILED`) when neither request nor execution metadata provides a locale.
         - `test_epic_chain_e2e_malformed_matrix_payload_raises_app_exception`: Assert `AppException` (status 500, `ErrorCodes.VALIDATION_FAILED`) when matrix step output contains non-dict payload.
    </action>
    <action>In @[backend_v2/tests/integration/test_lazy_llm_simulation.py]: Update `criteria_block` instantiation from `PromptBlock(...)` to `MatrixPromptBlock(...)`.</action>
    <action>Verify that `uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py backend_v2/tests/integration/test_lazy_llm_simulation.py` runs and passes 100%.</action>
  </step>

  <step id="3" name="Live LLM E2E REST API Verification Gate">
    <action>Execute live E2E integration test gate using Windows PowerShell:
      `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
    </action>
  </step>

  <step id="4" name="Knowledge Item Synchronization (4-Layer Clean Stack &amp; Zero-XML UI)">
    <action>Update `@[C:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]` with new architectural invariant sections:
      1. `<rule_block id="zero_xml_ui_paradigm">`:
         - Authors in Studio UI write discrete natural-language fields (`objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`, `instruction_text`).
         - Direct entry of XML tags (`<system_directive>`, `<role>`, `<rules>`) or ALL-CAPS directive anchors by humans is strictly banned.
         - UI provides a read-only live preview of the backend-compiled XML representation.
      2. `<rule_block id="four_layer_clean_stack_model">`:
         - Layer 1 (Global Mandates SSOT): Centralized universal system directives in `backend_v2/models/prompts/global_mandates.py` (`GLOBAL_MANDATES_XML`) automatically prepended by the compiler into the static caching prefix.
         - Layer 2 (Persona &amp; Role Enforcement): Domain persona rules from `PersonaPromptBlock.role_enforcement` and `tone_directives`.
         - Layer 3 (Protocol &amp; Rubric Heuristics): Extraction protocol rules from `ProtocolPromptBlock.protocol_instructions` and BARS evaluative rubric directives (`objective`, `evaluation_rules`, `banned_concepts`, `<theory_context>`).
         - Layer 4 (Dynamic User Execution Context): Sliced source documents, user inputs, runtime variables (`execution_time`, `alias_map`), and structured output schema instructions.
      3. `<rule_block id="static_first_caching_topology">`:
         - Layers 1-3 form a 100% static, deterministic system prompt prefix enabling Google DeepMind Gemini and Anthropic Claude context caching (up to 90% latency reduction and 75% FinOps cost efficiency).
         - Dynamic data is strictly isolated in Layer 4 user messages.
    </action>
  </step>

  <step id="5" name="LLM Architecture Rule Synchronization (05_llm_architecture.md)">
    <action>Update `@[.agents/rules/05_llm_architecture.md]` adding:
      1. `<rule_block id="compiler_xml_sovereignty_mandate">`:
         - Banned pattern: Writing XML tags (`<system_directive>`, `<role>`, `<rules>`, `<objective>`) in user-facing UI forms, domain models, or `seed_data.json`.
         - Mandatory pattern: All XML tags MUST be compiled programmatically by the backend compiler layer (`PromptFactory`, `MatrixSensorPromptBuilder`, `LocalizationCompiler`). UI and database store pure text and structured arrays.
         - Catastrophic reason: Manual XML entry allows human typos to break parser hierarchies, causes prompt injection vulnerabilities, and creates un-auditable semantic drift.
      2. `<rule_block id="four_layer_clean_stack_hierarchy">`:
         - Mandatory pattern: All system prompts MUST be compiled following the strict 4-Layer Clean Stack hierarchy (Layer 1 Global Mandates -> Layer 2 Persona -> Layer 3 Protocol/Rubric -> Layer 4 User Context).
         - Catastrophic reason: Violating the 4-layer ordering breaks foundational model attention hierarchies and prevents context caching.
    </action>
  </step>

  <validation_gate>
    <action>Execute Local Integration Suite: `uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py backend_v2/tests/integration/test_lazy_llm_simulation.py`</action>
    <action>Execute Live E2E Verification: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` (PowerShell)</action>
    <action>Execute Global Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/tests/integration/test_epic_chain_e2e.py --test`</action>
    <action>Execute Global Flutter Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</action>
    <action>Execute AST Prompt XML Sovereignty Tests: `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py`</action>
  </validation_gate>
</execution_protocol>
```
