# Phase 1: Pre-Requisite Technical Debt Cleanups & AST Guardrails (Backend)

**Overview:** Eliminate duck typing and lazy fallbacks in simulation service, un-skip and fix broken unit test fixture in test_tier4_schema_bug.py, verify test_schema_builder.py, and establish 9 AST and seed guardrails in test_ast_matrix_claim_guardrails.py to mathematically enforce MatrixClaim ai_description eradication and TDAAssertion concept_description constraints per @[docs/arkkitehtuurin_parannuskohteet.md#L244-L417].
**Target Files:**
- `[MODIFY]` @[backend_v2/services/studio/simulation_service.py#L140-L195]
- `[MODIFY]` @[backend_v2/tests/unit/test_tier4_schema_bug.py#L9-L75]
- `[MODIFY]` @[backend_v2/tests/unit/test_schema_builder.py]
- `[NEW]` @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/studio/simulation_service.py#L140-L195], @[backend_v2/tests/unit/test_tier4_schema_bug.py#L9-L75], and @[backend_v2/tests/unit/test_schema_builder.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Duck typing `getattr(claim, 'ai_description', None)` eliminated from @[backend_v2/services/studio/simulation_service.py#L140-L195].
    - [x] Lazy fallback `rendered = data.ai_description or ""` replaced with explicit `None` check, and raw dictionary localization fallback replaced with `claim.label.resolve("en")` in @[backend_v2/services/studio/simulation_service.py#L140-L195].
    - [x] Pre-existing broken test @[backend_v2/tests/unit/test_tier4_schema_bug.py#L9-L75] un-skipped, `concept_description` fixed to plain string with 10 or more characters, and claim fixture validated.
    - [x] @[backend_v2/tests/unit/test_schema_builder.py] verified to confirm `ai_description` references `PromptBlock` rather than `MatrixClaim`.
    - [x] 9 AST and seed guardrails implemented in [NEW] @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py] with live Phase 1 tests, negative mock tests, and aspirational anchors passing.
    - [x] Quality gate `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py --test` passes.
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
    <backend>@[backend_v2/services/studio/simulation_service.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/models/v2_core.py` in Phase 1 (reserved for Phase 3).
    - Do NOT modify `backend_v2/seed/seed_data.json` in Phase 1 (reserved for Phase 2).
    - Do NOT modify Flutter frontend files in this backend plan.
  </anti_targets>

  <step id="1" name="Simulation Service Technical Debt Cleanup">
    <action>Eliminate duck typing in @[backend_v2/services/studio/simulation_service.py#L140-L195] by replacing `getattr(claim, 'ai_description', None)` with direct iteration over `claim.tda_assertions` reading `tda.concept_description`.</action>
    <demolish>REMOVE: `getattr(claim, 'ai_description', None)` at @[backend_v2/services/studio/simulation_service.py#L140-L195]. REPLACE WITH: direct iteration over `claim.tda_assertions`.</demolish>
    <action>Clean up lazy fallback in @[backend_v2/services/studio/simulation_service.py#L140-L195] (`rendered = data.ai_description or ""` ) by replacing with explicit `None` check, and replace raw dictionary fallback lookup (`claim.label.translations.get(...)`) with strongly-typed `claim.label.resolve("en")`.</action>
    <demolish>REMOVE: `rendered = data.ai_description or ""` at @[backend_v2/services/studio/simulation_service.py#L140-L195]. REPLACE WITH: explicit `None` check.</demolish>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-existing technical debt in touched backend files must be resolved in Phase 1 before domain model modifications in Phase 3.</constraint>
  </step>

  <step id="2" name="Unit Test Fixtures Remediation">
    <action>Un-skip and fix pre-existing broken test in @[backend_v2/tests/unit/test_tier4_schema_bug.py#L9-L75]: remove `@pytest.mark.skip`, fix `concept_description` from legacy `I18nText` dictionary to plain string with 10 or more characters, retain valid string `ai_description` on claim fixture (satisfying current `v2_core.py` `MatrixClaim` schema until Phase 3 modernization), and assert that malformed LLM outputs fail schema validation.</action>
    <action>Verify @[backend_v2/tests/unit/test_schema_builder.py] to confirm `ai_description` refers to `PromptBlock` (retained) rather than `MatrixClaim`.</action>
    <constraint invariant="anti_test_skipping_mandate">Skipped tests must be un-skipped and adapted to comply with strictness invariants.</constraint>
  </step>

  <step id="3" name="AST and Seed Guardrail Suite Creation">
    <action>Create [NEW] @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py] with 9 AST and seed guardrail tests per @[ki_ast_guardrail_testing.md] (live Phase 1 checks, negative mock tests, and aspirational anchors):</action>
    <test_contracts>
      <test name="test_seed_claims_have_no_ai_description" category="positive">
        <input>backend_v2/seed/seed_data.json</input>
        <expected>0 matrix claims in seed_data.json contain ai_description</expected>
      </test>
      <test name="test_seed_claims_all_tda_assertions_have_valid_concept_description" category="positive">
        <input>backend_v2/seed/seed_data.json</input>
        <expected>All 152 tda_assertions have concept_description with len >= 10</expected>
      </test>
      <test name="test_settings_tda_concept_min_length_defined" category="positive">
        <input>backend_v2/settings.py</input>
        <expected>Settings defines tda_concept_min_length == 10</expected>
      </test>
      <test name="test_ast_matrix_claim_has_no_ai_description_field" category="positive">
        <input>backend_v2/models/v2_core.py AST</input>
        <expected>MatrixClaim class does not define ai_description</expected>
      </test>
      <test name="test_ast_tda_assertion_has_string_constraints_min_length_10" category="positive">
        <input>backend_v2/models/v2_core.py AST</input>
        <expected>TDAAssertion.concept_description enforces min_length=10</expected>
      </test>
      <test name="test_simulation_service_ast_no_claim_ai_description_access" category="positive">
        <input>backend_v2/services/studio/simulation_service.py AST</input>
        <expected>Contains 0 getattr(claim, 'ai_description', ...) or claim.ai_description accesses</expected>
      </test>
      <test name="test_simulation_service_ast_no_hasattr_getattr" category="positive">
        <input>backend_v2/services/studio/simulation_service.py AST</input>
        <expected>Contains 0 getattr and 0 hasattr calls</expected>
      </test>
      <test name="test_ast_guardrail_catches_invalid_matrix_claim_negative" category="negative">
        <input>Mock AST node of MatrixClaim containing ai_description: str</input>
        <expected>AST scanner detects violation and fails validation</expected>
      </test>
      <test name="test_ast_guardrail_catches_missing_string_constraints_negative" category="negative">
        <input>Mock AST node of TDAAssertion without StringConstraints(min_length=10)</input>
        <expected>AST scanner detects violation and fails validation</expected>
      </test>
    </test_contracts>
    <constraint invariant="ast_guardrail_mandate">AST Guardrail tests mathematically enforce structural invariants before and during refactoring.</constraint>
  </step>

  <validation_gate>
    <action>Execute Guardrails Unit Test Suite: `uv run pytest backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py`</action>
    <action>Execute Tier 4 Schema Bug Test: `uv run pytest backend_v2/tests/unit/test_tier4_schema_bug.py`</action>
    <action>Execute Schema Builder Test: `uv run pytest backend_v2/tests/unit/test_schema_builder.py`</action>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/simulation_service.py --test`</action>
  </validation_gate>
</execution_protocol>
```
