# Cognitive Instruction Harmonization: Single Source of Truth for TDA Assertions

This implementation plan eliminates the historical migration debt between `MatrixClaim.ai_description` and `TDAAssertion.concept_description` across the database seed vault, Python backend models, Flutter studio client, and associated test suites.

## User Review Required

> [!IMPORTANT]
> **Zero Legacy Compatibility & Ruthless Deletion**:
> - `MatrixClaim.ai_description` is permanently eliminated from both backend Pydantic models (`MatrixClaim`) and frontend Freezed models (`MatrixClaim`).
> - In `seed_data.json`, 70 claims where `TDAAssertion.concept_description` is currently empty (`""`) will have their instruction migrated from `MatrixClaim.ai_description` into `TDAAssertion.concept_description`.
> - All 152 `ai_description` keys on `MatrixClaim` instances in `seed_data.json` will be deleted.
> - `TDAAssertion.concept_description` will enforce `StringConstraints(strip_whitespace=True, min_length=10)`.
> - **Global Config Sovereignty**: The minimum length threshold (10 characters) is centrally defined in `backend_v2/settings.py` (`tda_concept_min_length`) and mirrored in `client_app_v2/lib/core/models/enums.dart` (`SystemUiConstraints.tdaConceptMinLength`), eliminating magic numbers across both tiers.

> [!NOTE]
> **Prompt Preservation Guarantee**:
> In accordance with the Prompt Preservation Mandate, no natural-language qualitative instruction text will be truncated or altered during migration. The 70 instructions are moved verbatim into `concept_description`.

---

## Open Questions

None. The architectural requirements, affected files, line boundaries, and test matrices are fully resolved deterministically.

---

## Proposed Changes

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

### Target and Context Files

#### Context Files (Read-Only)
- `@[docs/arkkitehtuurin_parannuskohteet.md#L244-L417]`
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/01-python-backend.md]`
- `@[.agents/rules/02_flutter_desktop.md]`
- `@[.agents/rules/03_seed_vault.md]`
- `@[.agents/rules/04_directory_reference.md]`
- `@[.agents/rules/05_llm_architecture.md]`
- `@[ki_god_code_prevention.md]`
- `@[ki_ast_guardrail_testing.md]`
- `@[ki_python_314_concurrency_strictness.md]`

#### Target Files (Modifications & Additions)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]`
- `[MODIFY]` `@[backend_v2/settings.py#L110-L145]`
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L226-L321]`
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L324-L341]`
- `[MODIFY]` `@[backend_v2/hooks/atom_flattening.py#L120-L160]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L125-L160]`
- `[MODIFY]` `@[backend_v2/services/studio/simulation_service.py#L150-L200]`
- `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart#L375-L385]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/prompt_block.dart#L125-L165]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L30-L200]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart#L150-L200]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L1175-L1200]`
- `[NEW]` `@[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py]`
- `[MODIFY]` Unit & Integration Test Suites:
  - `@[backend_v2/tests/unit/services/test_blueprint.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]`
  - `@[backend_v2/tests/unit/test_epic93_contract_verification.py]`
  - `@[backend_v2/tests/unit/test_worker.py]`
  - `@[backend_v2/tests/unit/hooks/test_atom_flattening.py]`
  - `@[backend_v2/tests/unit/hooks/test_scoring.py]`
  - `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_atomizer.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_omission.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_causal_analyst_schema.py]`
  - `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py]`
  - `@[backend_v2/tests/integration/test_lazy_llm_simulation.py]`
  - `@[backend_v2/tests/integration/test_epic_chain_e2e.py]`
  - `@[backend_v2/tests/unit/models/domain/test_prompt_block_computed_bug.py]`
  - `@[backend_v2/tests/unit/services/orchestrator/test_atom_id_order_bug.py]`
  - `@[backend_v2/tests/unit/test_tier4_schema_bug.py]`
  - `@[backend_v2/tests/unit/test_schema_builder.py]`
  - `@[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart]`

---

## Canonical Execution Protocol

```xml
<execution_protocol version="1.0">
  <phase id="1" name="TECHNICAL_DEBT_CLEANUP_AND_AST_GUARDRAILS">
    <step id="1.1" name="BUILD_AST_AND_SCHEMA_GUARDRAILS">
      <action>Create [NEW] @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py] enforcing static AST validation and database seed constraints.</action>
      <constraint invariant="ast_guardrail_mandate">
        The guardrail suite must contain:
        1. test_seed_claims_have_no_ai_description: Asserts 0 matrix claims in seed_data.json contain ai_description.
        2. test_seed_claims_all_tda_assertions_have_valid_concept_description: Asserts all 152 tda_assertions have concept_description with length >= 10.
        3. test_settings_tda_concept_min_length_defined: Asserts backend_v2/settings.py defines tda_concept_min_length == 10.
        4. test_ast_matrix_claim_has_no_ai_description_field: Verifies via ast.parse that MatrixClaim class in @[backend_v2/models/v2_core.py#L324-L341] does not define ai_description.
        5. test_ast_tda_assertion_has_string_constraints_min_length_10: Verifies via AST that TDAAssertion.concept_description in @[backend_v2/models/v2_core.py#L226-L321] enforces min_length=10.
        6. test_simulation_service_ast_no_claim_ai_description_access: Asserts @[backend_v2/services/studio/simulation_service.py#L22-L253] contains no getattr(claim, 'ai_description', ...) or claim.ai_description accesses.
        7. test_ast_guardrail_catches_invalid_matrix_claim_negative: Proves AST scanner detects violations by passing a mock AST node of MatrixClaim containing ai_description: str.
        8. test_ast_guardrail_catches_missing_string_constraints_negative: Proves AST scanner detects violations by passing a mock AST node of TDAAssertion without StringConstraints(min_length=10).
      </constraint>
    </step>
    <step id="1.2" name="SCOPED_BOY_SCOUT_INSPECTION">
      <action>Eliminate duck typing in @[backend_v2/services/studio/simulation_service.py#L170-L200] by replacing getattr(claim, 'ai_description', None) with direct iteration over claim.tda_assertions reading tda.concept_description.</action>
      <action>Clean up lazy fallback at @[backend_v2/services/studio/simulation_service.py#L159] (`rendered = data.ai_description or ""`) by replacing with explicit None check.</action>
      <constraint invariant="zero_service_layer_fallbacks">
        Duck typing using getattr and lazy or-fallback operators are strictly prohibited. Access concept_description from tda_assertions directly.
      </constraint>
    </step>
    <step id="1.3" name="PRE_FLIGHT_FIXTURE_AUDIT">
      <action>Un-skip and fix pre-existing broken test in @[backend_v2/tests/unit/test_tier4_schema_bug.py#L1-L60]: remove `@pytest.mark.skip`, fix concept_description from I18nText dictionary to plain string with >= 10 characters, and remove ai_description from claim fixture.</action>
      <action>Verify @[backend_v2/tests/unit/test_schema_builder.py#L16] to confirm ai_description refers to PromptBlock (retained) rather than MatrixClaim.</action>
      <constraint invariant="anti_test_skipping_mandate">
        Skipping tests is strictly forbidden. Adapt and un-skip test_tier4_schema_bug.py to enforce modern V2 architecture.
      </constraint>
    </step>
  </phase>

  <phase id="2" name="SEED_DATA_MIGRATION_AND_VAULT_MUTATION">
    <step id="2.1" name="SEED_BACKUP_CREATION">
      <action>Create a timestamped backup of @[backend_v2/seed/seed_data.json] in backend_v2/seed/backups/ via PowerShell Copy-Item.</action>
      <constraint invariant="vault_mutation_protocol">
        Ensure backend_v2/seed/backups/ directory exists before copying.
      </constraint>
    </step>
    <step id="2.2" name="SEED_DATA_MIGRATION">
      <action>Surgically migrate @[backend_v2/seed/seed_data.json]:</action>
      <action>1. Execute a read-only validation script from scratch/ to verify all 70 target claims.</action>
      <action>2. For all 70 claims where TDAAssertion.concept_description is empty, copy MatrixClaim.ai_description into TDAAssertion.concept_description verbatim.</action>
      <action>3. Delete the ai_description key from all 152 MatrixClaim objects in prompt_blocks.</action>
      <constraint invariant="prompt_preservation_mandate">
        All qualitative prompt texts must be preserved with 100% mathematical fidelity.
      </constraint>
    </step>
    <step id="2.3" name="SEED_INTEGRITY_AND_RESEED">
      <action>Validate JSON parsing of @[backend_v2/seed/seed_data.json] and execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`.</action>
      <constraint invariant="local_data_ephemeral_nature">
        Re-seed local database to sync in-memory TinyDB state with updated seed vault.
      </constraint>
    </step>
    <checkpoint id="session_handover_phase_2">
      <action>Perform atomic git commit for Phase 1 and Phase 2. Execute /tier5-session-handover to refresh context before Phase 3.</action>
    </checkpoint>
  </phase>

  <phase id="3" name="BACKEND_DOMAIN_AND_SERVICE_HARMONIZATION">
    <step id="3.1" name="UPDATE_SETTINGS_AND_PYDANTIC_MODELS">
      <action>Modify @[backend_v2/settings.py#L110-L145]: Define `tda_concept_min_length: Annotated[int, Field(description="Minimum character length for TDA assertion concept descriptions.")] = 10`.</action>
      <action>Modify @[backend_v2/models/v2_core.py#L226-L321] and @[backend_v2/models/v2_core.py#L324-L341]:</action>
      <action>1. In TDAAssertion, update concept_description to `Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)] = Field(description="Concise concept definition for this assertion, not runtime instructions")`.</action>
      <action>2. Update adjacent Finnish descriptions on TDAAssertion to English: anchor_target (`description="Target anchor to search for during extraction"`) and extraction_rule (`description="The extraction rule that data must satisfy"`).</action>
      <action>3. In MatrixClaim, delete the `ai_description: str` field entirely, leaving only `label: I18nText` and `tda_assertions: list[TDAAssertion]`.</action>
      <action>4. Boy Scout: Replace historical comment at @[backend_v2/models/v2_core.py#L268] (`# Phase 4: Monolingual concept description for LLM (migrated from flat ai_rule_description)`) with present-tense description: `# Monolingual concept description consumed by the LLM extraction pipeline`.</action>
      <action>5. Boy Scout: Translate 3 Finnish error messages in `validate_math_logic` validator at @[backend_v2/models/v2_core.py#L296-L321] to English:
        - L307: `"Inverse evidence (poison detection) strictly requires 'EXISTS' aggregation mode."`
        - L314: `"EXTRACTIVE_SENSOR track requires at least one fact in facts_to_find."`
        - L318: `"EXTRACTIVE_SENSOR track requires a defined logical_expression."`</action>
      <constraint invariant="pydantic_annotated_fields_mandate">
        Use PEP 593 Annotated syntax with StringConstraints for validation bounds and English-only documentation strings.
      </constraint>
      <constraint invariant="strict_configuration_segregation">
        Global threshold limits must be defined in settings.py SSOT rather than hardcoded in business logic.
      </constraint>
      <constraint invariant="internal_language_and_epic_ban">
        All error messages, comments, and descriptions must be exclusively in English. Historical context comments violate documentation_present_tense_mandate.
      </constraint>
    </step>
    <step id="3.2" name="UPDATE_ATOM_FLATTENING_HOOK">
      <action>Update @[backend_v2/hooks/atom_flattening.py#L120-L160] to consume `tda.concept_description` directly without manual `.strip()` defensive calls.</action>
      <constraint invariant="the_duct_tape_ban">
        Rely strictly on Pydantic StringConstraints strip_whitespace rather than ad-hoc string manipulation.
      </constraint>
    </step>
    <step id="3.3" name="UPDATE_MATRIX_SENSOR_PROMPT_BUILDER">
      <action>Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L125-L160]:</action>
      <action>Enforce Fail-Fast exception if assertion.question is empty string before generating XML question block.</action>
      <constraint invariant="rfc7807_dual_reporting_mandate">
        Precede AppException with structured logger.error call referencing ErrorCodes.VALIDATION_FAILED.
      </constraint>
    </step>
    <checkpoint id="session_handover_phase_3">
      <action>Perform atomic git commit for Phase 3. Execute /tier5-session-handover before Phase 4.</action>
    </checkpoint>
  </phase>

  <phase id="4" name="FLUTTER_STUDIO_CLIENT_HARMONIZATION">
    <step id="4.1" name="UPDATE_CENTRALIZED_ENUMS_AND_FREEZED_MODELS">
      <action>Modify @[client_app_v2/lib/core/models/enums.dart#L375-L385]: Add `tdaConceptMinLength(10)` to `SystemUiConstraints` enum to mirror backend config SSOT.</action>
      <action>Modify @[client_app_v2/lib/features/studio/models/prompt_block.dart#L125-L165]:</action>
      <action>1. In `TDAAssertion.create` factory (L136), replace `tdaId: 'tda_${uuidHex.substring(0, 16)}'` with `tdaId: 'tda_$uuidHex'` to produce 32 hex chars, removing manual substring clipping and ensuring 1:1 regex parity with backend `^tda_[a-f0-9]{32}$`.</action>
      <action>2. Remove `required String aiDescription` from MatrixClaim Freezed model definition.</action>
      <action>Run build runner: `dart run build_runner build --delete-conflicting-outputs`.</action>
      <constraint invariant="centralized_frontend_enums">
        Centralize client-side bounds and constraints in enums.dart SystemUiConstraints for 1:1 parity with backend settings.
      </constraint>
      <constraint invariant="sdui_contract_fracture_prevention">
        Synchronously maintain 1:1 DTO serialization parity between Backend and Flutter client.
      </constraint>
    </step>
    <step id="4.2" name="UPDATE_SCALE_EDITOR_MODAL">
      <action>Modify @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L30-L200]:</action>
      <action>1. In _addClaim, instantiate MatrixClaim with label and tdaAssertions containing default TDAAssertion.create(conceptDescription: 'CRITICAL MANDATE: ', inverseEvidence: false, aggregationMode: AggregationMode.exists).</action>
      <action>2. Remove the claim.aiDescription TextFormField.</action>
      <action>3. Ensure rule editing routes directly to claim.tdaAssertions.first.conceptDescription with form validator checking `value.trim().length >= SystemUiConstraints.tdaConceptMinLength.value`.</action>
      <action>4. Boy Scout: Clean up redundant duplicate `const SizedBox(height: 16)` at L185.</action>
      <constraint invariant="silent_json_fallbacks">
        Do not use fallback strings. Bind directly to TDAAssertion fields and validate using centralized SystemUiConstraints enum.
      </constraint>
    </step>
    <step id="4.3" name="UPDATE_BARS_MATRIX_BUILDER_VIEW">
      <action>Modify @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart#L150-L200]:</action>
      <action>Replace display of claim.aiDescription with `claim.tdaAssertions.isNotEmpty ? claim.tdaAssertions.first.conceptDescription : ''` (guaranteed non-empty by min_length=10 schema constraint governed by backend settings / frontend SystemUiConstraints.tdaConceptMinLength).</action>
      <constraint invariant="the_duct_tape_ban">
        Do not use arbitrary fallback strings. Rely on schema non-empty invariant.
      </constraint>
    </step>
    <step id="4.4" name="UPDATE_PROMPT_BLOCK_BUILDER_VIEW">
      <action>Modify @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L1175-L1200]:</action>
      <action>Update default MatrixClaim instantiation in showDialog to omit aiDescription and supply valid tdaAssertions via TDAAssertion.create.</action>
      <constraint invariant="zero_deprecation_mandate">
        Eliminate all references to removed aiDescription parameter.
      </constraint>
    </step>
    <checkpoint id="session_handover_phase_4">
      <action>Perform atomic git commit for Phase 4. Execute /tier5-session-handover before Phase 5.</action>
    </checkpoint>
  </phase>

  <phase id="5" name="TEST_SUITE_HARMONIZATION_AND_QUALITY_GATES">
    <step id="5.1" name="UPDATE_BACKEND_TEST_FIXTURES">
      <action>Update mock claims and MatrixClaim instantiations across all 23 backend test files in 2 batches, ensuring all 39 short concept_description strings across 12 test files are updated to valid descriptions with length >= 10:</action>
      <action>Batch 1 (Core Services &amp; Hooks):</action>
      <action>1. @[backend_v2/tests/unit/services/test_blueprint.py] (Update claims and replace 4 short concept strings 'concept', 'concept 0', 'concept 1' with >= 10 chars)</action>
      <action>2. @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py] (Replace 11 short concept strings 'Concept', 'Alpha', 'Beta', 'A', 'B', 'L1', 'L2', 'L5', 'Multi' with >= 10 chars)</action>
      <action>3. @[backend_v2/tests/unit/test_epic93_contract_verification.py] (Replace short concept 'Concept' with >= 10 chars)</action>
      <action>4. @[backend_v2/tests/unit/test_worker.py] (Update claim fixtures to remove ai_description)</action>
      <action>5. @[backend_v2/tests/unit/hooks/test_atom_flattening.py] (Update MatrixClaim fixtures)</action>
      <action>6. @[backend_v2/tests/unit/hooks/test_scoring.py] (Update raw claim dictionaries)</action>
      <action>7. @[backend_v2/tests/unit/services/test_matrix_domain_parser.py] (Update claim fixtures)</action>
      <action>8. @[backend_v2/tests/unit/services/orchestrator/test_atomizer.py] (Replace 3 short concept strings 'Test rule', 'Rule 1', 'Rule 2' with >= 10 chars)</action>
      <action>9. @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py] (Replace 7 short concept strings 'desc' with >= 10 chars)</action>
      <action>10. @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py] (Update matrix block mock)</action>
      <action>11. @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_omission.py] (Replace short concept 'Test' with >= 10 chars)</action>
      <action>Checkpoint: Commit Batch 1 test fixes before proceeding to Batch 2.</action>
      <action>Batch 2a (Orchestration &amp; Strategies — 6 files):</action>
      <action>12. @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py] (Update raw claim dictionaries)</action>
      <action>13. @[backend_v2/tests/unit/services/orchestrator/test_causal_analyst_schema.py] (Update raw claim dictionaries)</action>
      <action>14. @[backend_v2/tests/unit/services/studio/test_workflow_service.py] (Replace short concept 'Concept' with >= 10 chars)</action>
      <action>15. @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py] (Replace 4 short concept strings 'mock' with >= 10 chars)</action>
      <action>16. @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py] (Replace 2 short concept strings 'Atom 1', 'Atom 2' with >= 10 chars)</action>
      <action>17. @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py] (Replace short concept 'Atom 1' with >= 10 chars)</action>
      <action>Checkpoint: Commit Batch 2a test fixes before proceeding to Batch 2b.</action>
      <action>Batch 2b (Integration, Bugs &amp; Verification — 6 files):</action>
      <action>18. @[backend_v2/tests/integration/test_lazy_llm_simulation.py] (Update MatrixClaim fixtures)</action>
      <action>19. @[backend_v2/tests/integration/test_epic_chain_e2e.py] (Replace 2 short concept strings 'concept', 'concept 2' with >= 10 chars)</action>
      <action>20. @[backend_v2/tests/unit/models/domain/test_prompt_block_computed_bug.py] (Replace 2 short concept strings 'bad', 'good' with >= 10 chars)</action>
      <action>21. @[backend_v2/tests/unit/services/orchestrator/test_atom_id_order_bug.py] (Update raw claim dictionaries)</action>
      <action>22. @[backend_v2/tests/unit/test_tier4_schema_bug.py] (Un-skip and fix fixture dictionary)</action>
      <action>23. @[backend_v2/tests/unit/test_schema_builder.py] (Verify PromptBlock.ai_description parity)</action>
      <constraint invariant="anti_tdd_trap">
        Do not maintain legacy fixtures with ai_description on claims. Update fixtures to supply valid TDAAssertion with concept_description >= 10 characters.
      </constraint>
    </step>
    <step id="5.2" name="UPDATE_FRONTEND_TEST_FIXTURES">
      <action>Update @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart] removing aiDescription parameter from MatrixClaim test fixtures.</action>
      <constraint invariant="zero_deprecation_mandate">
        All Flutter tests must compile with zero deprecation warnings.
      </constraint>
    </step>
    <step id="5.3" name="EXECUTE_GLOBAL_QUALITY_GATES">
      <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
      <action>Run flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.</action>
      <constraint invariant="quality_gate_execution">
        Both backend and frontend audit loops must pass with 100% success and 0 typing/linter errors.
      </constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **AST & Schema Guardrails**:
   `uv run pytest backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py`
2. **Backend Unit & Integration Test Suite**:
   `uv run python scripts/backend_audit_loop.py backend_v2 --test`
3. **Frontend Flutter Test Suite**:
   `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
4. **Live Integration E2E Test Gate**:
   - Windows (PowerShell): `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`
   - Unix (Bash): `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`

### Anti-Happy-Path Negative Test Scenarios
1. **Scenario NEG-01 (TDA Concept Too Short)**:
   - Input: Instantiate `TDAAssertion` with `concept_description="Short"`.
   - Expected Output: Pydantic raises `ValidationError` due to `min_length=10`.
2. **Scenario NEG-02 (MatrixClaim with ai_description)**:
   - Input: Attempt to parse dictionary `{"label": {"translations": {"en": "Claim"}}, "ai_description": "Legacy text", "tda_assertions": [...]}` as `MatrixClaim`.
   - Expected Output: Pydantic raises `ValidationError` with `extra_forbidden` for `ai_description`.
3. **Scenario NEG-03 (MatrixSensorPromptBuilder Empty Question)**:
   - Input: Trigger `MatrixSensorPromptBuilder.build_compiled_prompt` where an assertion in `matrix_assertions_map` has an empty `question=""`.
   - Expected Output: Raises `AppException` with `ErrorCodes.VALIDATION_FAILED`.
4. **Scenario NEG-04 (AST Scanner Negative Violation Detection)**:
   - Input: Pass AST snippet of a class `MatrixClaim` containing `ai_description: str` to `test_ast_guardrail_catches_invalid_matrix_claim_negative`.
   - Expected Output: AST validator returns boolean detection flag confirming forbidden field violation is caught.
