# Phase 3: Backend Domain & Service Harmonization (and Test Fixtures Harmonization)

**Overview:** Update settings with tda_concept_min_length: 10, enforce StringConstraints(strip_whitespace=True, min_length=10) on TDAAssertion.concept_description, eradicate ai_description from MatrixClaim, translate Finnish descriptions and validators to English, update matrix sensor prompt builder, and atomically modernize mock claim fixtures across 23 backend test files and 1 frontend test file.
**Target Files:**
- `[MODIFY]` @[backend_v2/settings.py#L51-L716]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L226-L321]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L296-L321]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L324-L341]
- `[MODIFY]` @[backend_v2/hooks/atom_flattening.py#L34-L187]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L93-L207]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_epic93_contract_verification.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_atom_flattening.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_atomizer.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_omission.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_causal_analyst_schema.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_lazy_llm_simulation.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_epic_chain_e2e.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/domain/test_prompt_block_computed_bug.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_atom_id_order_bug.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_tier4_schema_bug.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_schema_builder.py]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L179-L228] Phase 3: Backend Domain & Service Harmonization

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/settings.py#L51-L716], @[backend_v2/models/v2_core.py#L226-L321], @[backend_v2/models/v2_core.py#L296-L321], and @[backend_v2/models/v2_core.py#L324-L341].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `tda_concept_min_length: 10` defined in @[backend_v2/settings.py#L51-L716].
    - [ ] `concept_description` updated to `StringConstraints(strip_whitespace=True, min_length=10)` in `TDAAssertion` at @[backend_v2/models/v2_core.py#L226-L321].
    - [ ] `ai_description` permanently eradicated from `MatrixClaim` in @[backend_v2/models/v2_core.py#L324-L341].
    - [ ] Finnish error messages and comments in `v2_core.py` translated to English.
    - [ ] `assertion.question` empty string validation in @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L93-L207] enforces Fail-Fast exception with RFC 7807 logger.
    - [ ] Verified @[backend_v2/hooks/atom_flattening.py#L34-L187] utilizes `tda.concept_description.strip()`.
    - [ ] All 23 backend test files and 1 frontend test file updated with valid >= 10 char concept descriptions and 0 claim `ai_description` fields.
    - [ ] Quality gates pass: `uv run python scripts/backend_audit_loop.py backend_v2 --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.
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
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT re-introduce `ai_description` on `MatrixClaim`.
    - Do NOT relax `min_length=10` on `concept_description`.
    - Do NOT add loose fallback defaults or duck typing.
  </anti_targets>

  <step id="1" name="Settings &amp; Domain Model Updates">
    <action>Modify @[backend_v2/settings.py#L51-L716]: Define `tda_concept_min_length: Annotated[int, Field(description="Minimum character length for TDA assertion concept descriptions.")] = 10`.</action>
    <action>Modify @[backend_v2/models/v2_core.py#L226-L321]: In `TDAAssertion`, update `concept_description` to `Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)] = Field(description="Concise concept definition for this assertion, not runtime instructions")`.</action>
    <action>Update adjacent Finnish descriptions on `TDAAssertion` to English: `anchor_target` and `extraction_rule`.</action>
    <action>Modify @[backend_v2/models/v2_core.py#L324-L341]: In `MatrixClaim`, delete the `ai_description: str` field entirely, leaving only `label: I18nText` and `tda_assertions: list[TDAAssertion]`.</action>
    <demolish>REMOVE: `ai_description: str` on `MatrixClaim` at @[backend_v2/models/v2_core.py#L324-L341]. REPLACE WITH: sole assertion container `tda_assertions: list[TDAAssertion]`.</demolish>
    <action>Translate Finnish error messages in `validate_math_logic` validator in @[backend_v2/models/v2_core.py#L296-L321] to English.</action>
    <constraint invariant="strict_pydantic_v2_rust">All domain models enforce extra='forbid' and strict typing.</constraint>
  </step>

  <step id="2" name="Prompt Builders &amp; Hooks Verification">
    <action>Verify @[backend_v2/hooks/atom_flattening.py#L34-L187]: Confirm `tda.concept_description.strip()` is utilized.</action>
    <action>Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L93-L207]: Enforce Fail-Fast exception with RFC 7807 structured `logger.error` if `assertion.question` is empty string before generating XML question block.</action>
  </step>

  <step id="3" name="Test Fixture Harmonization">
    <action>Update mock claims across 23 backend test files in batches, updating 39 short concept strings across 12 files to 10 or more characters and removing `ai_description` from claim fixtures.</action>
    <action>Update @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart] removing `aiDescription` parameter from `MatrixClaim` test fixtures.</action>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Execute Flutter Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</action>
  </validation_gate>
</execution_protocol>
```
