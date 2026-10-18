# Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)

**Overview:** Decouple lexical verification strictness ($\zeta_{lex}$) from scoring dampening strictness ($\zeta_{score}$), establishing independent `Workflow` and Studio DTO fields, synchronizing database seed data, updating execution worker context transit, and calibrating Gate 5 Snowball morphological stemming.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L307-L324] Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)

**Target Files:**
- `[MODIFY]` @[backend_v2/models/domain/workflow.py]
- `[MODIFY]` @[backend_v2/models/dtos/studio.py]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py]
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L20538-L21331]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/workers/execution_worker.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/extractive_sensor_service.py]
- `[MODIFY]` @[backend_v2/l10n/fi.json]
- `[MODIFY]` @[backend_v2/l10n/en.json]
- `[MODIFY]` @[backend_v2/tests/unit/workers/test_execution_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify multi-segment lexical validation is operational in @[backend_v2/services/orchestrator/anchor_validation_service.py].</action>
    <action>Look forward: Verify workflow models in @[backend_v2/models/domain/workflow.py] and seed data structure in @[backend_v2/seed/seed_data.json#L20538-L21331] before adding decoupled lexical strictness fields.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/domain/workflow.py]</backend>
    <backend>@[backend_v2/models/dtos/studio.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json#L20538-L21331]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/workers/execution_worker.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/extractive_sensor_service.py]</backend>
    <backend>@[backend_v2/l10n/fi.json]</backend>
    <backend>@[backend_v2/l10n/en.json]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_execution_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)` added to `Workflow` in @[backend_v2/models/domain/workflow.py] and Studio DTOs in @[backend_v2/models/dtos/studio.py].</item>
    <item>Studio workflow CRUD service updated in @[backend_v2/services/studio/workflow_service.py] to transit `default_lexical_strictness_level`.</item>
    <item>All 8 seeded workflows in @[backend_v2/seed/seed_data.json#L20538-L21331] synchronized with `default_lexical_strictness_level: 50`.</item>
    <item>`get_lexical_fuzz_threshold` in @[backend_v2/settings.py] calibrated to resolve threshold from decoupled lexical strictness.</item>
    <item>`execution_worker.py`, `dag_executor.py`, and `extractive_sensor_service.py` updated to pass `lexical_strictness_level` to `AnchorValidationService`.</item>
    <item>Localization keys for lexical strictness added to @[backend_v2/l10n/fi.json] and @[backend_v2/l10n/en.json].</item>
    <item>Unit tests in @[backend_v2/tests/unit/workers/test_execution_worker.py] and @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py] pass 100%.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT mutate qualitative prompt texts or persona instructions in `seed_data.json`.</anti_target>
    <anti_target>Do NOT conflate scoring dampening power curves with morphological stemming thresholds.</anti_target>
    <anti_target>Do NOT use language-level defaults or fallback lookups when resolving strictness.</anti_target>
  </anti_targets>

  <step id="1" name="EXPAND WORKFLOW DOMAIN MODEL &amp; STUDIO DTOS">
    <action>In @[backend_v2/models/domain/workflow.py]: Add field `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)` to the `Workflow` domain model.</action>
    <action>In @[backend_v2/models/dtos/studio.py]: Add field `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)` to `WorkflowCreateDTO` and related studio transfer models.</action>
    <constraint invariant="variable_and_schema_preservation_mandate">Preserve exact field nomenclature `default_lexical_strictness_level` across backend and studio DTOs.</constraint>
  </step>

  <step id="2" name="UPDATE STUDIO WORKFLOW SERVICE">
    <action>In @[backend_v2/services/studio/workflow_service.py]: Transit `default_lexical_strictness_level` across workflow creation, update, and retrieval pipelines.</action>
    <constraint invariant="zero_service_layer_fallbacks">Fail-Fast if lexical strictness is out of [0, 100] integer bounds.</constraint>
  </step>

  <step id="3" name="SYNCHRONIZE DATABASE SEED VAULT &amp; LOCALIZATION STRINGS">
    <action>In @[backend_v2/seed/seed_data.json#L20538-L21331]: Add `"default_lexical_strictness_level": 50` to all 8 seeded workflow records, keeping scoring `default_strictness_level: 50` intact.</action>
    <action>In @[backend_v2/l10n/fi.json] and @[backend_v2/l10n/en.json]: Add localization keys and descriptive labels for lexical verification strictness.</action>
    <constraint invariant="prompt_preservation_mandate">Do NOT mutate, tighten, or amputate any natural-language prompt text or description in `seed_data.json`.</constraint>
  </step>

  <step id="4" name="CALIBRATE SETTINGS LEXICAL THRESHOLD RESOLUTION">
    <action>In @[backend_v2/settings.py]: Update `get_lexical_fuzz_threshold` to accept decoupled `lexical_strictness_level` and compute fuzzy/stemmed thresholds dynamically.</action>
    <constraint invariant="cognitive_dampening_square_root_model">Keep score dampening strictly separated from lexical matching thresholds.</constraint>
  </step>

  <step id="5" name="TRANSIT DECOUPLED STRICTNESS IN EXECUTION PIPELINE">
    <action>In @[backend_v2/workers/execution_worker.py]: Extract both `default_strictness_level` and `default_lexical_strictness_level` from `Workflow` and pass them into the execution parameters.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py]: Transit `lexical_strictness_level` through `GlobalContextVarsDTO` or execution context.</action>
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py]: Pass `lexical_strictness_level` to `AnchorValidationService` during evidence validation.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Single sovereign pipeline for strictness transit; zero fallback guessing.</constraint>
  </step>

  <step id="6" name="EXPAND WORKER &amp; ANCHOR VALIDATION TEST SUITES">
    <action>In @[backend_v2/tests/unit/workers/test_execution_worker.py]: Add test verifying that `execution_worker.py` correctly extracts and propagates both strictness parameters.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]: Add test asserting that high scoring strictness ($\zeta_{score} = 85$) with default lexical strictness ($\zeta_{lex} = 50$) permits valid Finnish grammatical case inflections via Gate 5 Snowball stemmer.</action>
    <constraint invariant="universal_quality_gate">Audit and test execution must pass 100%.</constraint>
  </step>

  <test_contracts>
    <test name="test_strictness_decoupling_high_scoring_allows_morphology" category="positive">
      <input>score_strictness=85, lexical_strictness=50, candidate inflected Finnish word</input>
      <expected>Gate 5 Snowball stemmer accepts inflection; score dampening uses gamma(85)</expected>
    </test>
    <test name="test_workflow_seed_validation_dry_run" category="positive">
      <input>uv run python backend_v2/seed/run_seed.py local --dry-run</input>
      <expected>All 8 seeded workflows validate without schema errors</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute worker unit tests: `uv run pytest backend_v2/tests/unit/workers/test_execution_worker.py`.</action>
    <action>Execute anchor validation tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`.</action>
    <action>Execute dry-run seed validation: `uv run python backend_v2/seed/run_seed.py local --dry-run`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/workflow.py backend_v2/models/dtos/studio.py backend_v2/services/studio/workflow_service.py backend_v2/workers/execution_worker.py backend_v2/services/orchestrator/dag_executor.py backend_v2/services/orchestrator/extractive_sensor_service.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
