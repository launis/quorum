# Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)

**Overview:** Decouple lexical verification strictness ($\zeta_{lex}$) from scoring dampening strictness ($\zeta_{score}$), establishing independent `Workflow` and Studio DTO fields, synchronizing database seed data, updating execution worker context transit, and calibrating Gate 5 Snowball morphological stemming.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L307-L324] Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)

**Target Files:**
- `[MODIFY]` @[backend_v2/models/domain/workflow.py#L25-L208]
- `[MODIFY]` @[backend_v2/models/dtos/studio.py#L89-L138]
- `[MODIFY]` @[backend_v2/models/dtos/studio.py#L582-L615]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L40-L672]
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L20538-L21331]
- `[MODIFY]` @[backend_v2/settings.py#L985-L1006]
- `[MODIFY]` @[backend_v2/workers/execution_worker.py#L75-L538]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L597-L1794]
- `[MODIFY]` @[backend_v2/services/orchestrator/extractive_sensor_service.py#L175-L728]
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py#L25-L836]
- `[MODIFY]` @[backend_v2/l10n/fi.json]
- `[MODIFY]` @[backend_v2/l10n/en.json]
- `[MODIFY]` @[backend_v2/tests/unit/workers/test_execution_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]

## Five-Axis Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Workflow Domain Model**<br>`@[backend_v2/models/domain/workflow.py#L25-L208]` | Conflating scoring dampening strictness with lexical verification strictness; using untyped or loose int fields. | Strict `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100)] = 50` SSOT contract. | Reject duplicate strictness sub-models or complex nested policy configurations. | Pydantic `ValidationError` on $s < 0$ or $s > 100$; full-duplex DTO parity via `test_dto_parity.py`. |
| **Studio Workflow DTOs**<br>`@[backend_v2/models/dtos/studio.py#L89-L138]`<br>`@[backend_v2/models/dtos/studio.py#L582-L615]` | Omitting `default_lexical_strictness_level` from `WorkflowCreateDTO` or `WorkflowUpdateDTO`, causing silent field erasure during Studio saves. | Mirror `default_lexical_strictness_level` across `WorkflowCreateDTO` and `WorkflowUpdateDTO` with strict boundary validation. | Reject separate specialized DTO classes for lexical strictness mutations. | Unit test serialization roundtrips in `test_studio.py` and `test_workflows.py`. |
| **Studio Workflow Service**<br>`@[backend_v2/services/studio/workflow_service.py#L40-L672]` | Relying on dictionary key fetching (`.get("default_lexical_strictness_level", 50)`) or loose unvalidated assignment. | Direct dot-notation attribute access and typed Pydantic instantiation during draft creation and cloning. | Avoid custom strictness validation logic; delegate 100% to Pydantic domain invariants. | Unit test workflow cloning and draft creation asserting `default_lexical_strictness_level` preservation. |
| **Database Seed Vault**<br>`@[backend_v2/seed/seed_data.json#L20538-L21331]` | Missing explicit lexical strictness field in seeded workflows; mutating qualitative prompt descriptions. | Add `"default_lexical_strictness_level": 50` to all 3 seeded workflows while keeping prompt texts 100% pristine. | Reject redundant per-step strictness overrides in seed data. | `uv run python backend_v2/seed/run_seed.py local --dry-run` validates all seeded workflows with zero errors. |
| **Settings Lexical Threshold**<br>`@[backend_v2/settings.py#L985-L1006]` | Hardcoding multiplier logic in callers (`anchor_validation_service.py`); ignoring decoupled lexical strictness. | Centralized SSOT `get_lexical_fuzz_threshold(locale, lexical_strictness_level)` computing dynamic calibrated thresholds. | Prune caller-side multiplier branches; resolve threshold deterministically in single pure function. | Unit tests in `test_linguistics.py` asserting exact thresholds across all strictness tiers (0, 30, 50, 85, 100). |
| **Execution Worker Daemon**<br>`@[backend_v2/workers/execution_worker.py#L75-L538]` | Extracting only scoring strictness; failing to transit decoupled lexical strictness to the execution engine. | Extract both `strictness_level` and `lexical_strictness_level` directly from `workflow_def` without fallback guessing. | Avoid intermediate worker-level strictness translation layers or shadow dictionary accumulators. | `test_execution_worker_transits_decoupled_strictness_parameters` asserting exact parameters passed to engine. |
| **DAG Orchestration Engine**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L597-L1794]` | Defaulting lexical strictness to scoring strictness; silent parameter drops in strategy dispatch. | Fail-fast resolution in `execute_workflow` and transit of `lexical_strictness_level` through `node_executor` and `StrategyContext`. | Avoid creating bifurcated strategy execution paths; transit parameter through standard execution context. | Unit test execution verifying `StrategyContext.lexical_strictness_level` propagation. |
| **Extractive Sensor Service**<br>`@[backend_v2/services/orchestrator/extractive_sensor_service.py#L175-L728]` | Evaluating fuzzy anchors with static default threshold regardless of workflow lexical strictness. | Accept and transit `lexical_strictness_level` in `_fuzzy_match`, `pre_evaluate`, and `batch_pre_evaluate`. | Reject parallel pre-evaluation pipelines; pass single integer strictness parameter through existing signatures. | Unit tests in `test_extractive_sensor_service.py` asserting strictness-dependent pre-evaluation decisions. |
| **Anchor Validation Service**<br>`@[backend_v2/services/orchestrator/anchor_validation_service.py#L25-L836]` | Conflating scoring strictness ($\zeta_{score} = 85$) with lexical strictness, blocking Gate 5 Snowball morphological stemming. | Accept decoupled `lexical_strictness_level` in `_is_lexically_valid`, `validate_evidence`, and `process_atom_evaluation`. | Remove redundant multiplier computation inside `_is_lexically_valid`; delegate to `get_lexical_fuzz_threshold`. | `test_strictness_decoupling_high_scoring_allows_morphology` asserting Snowball stemming succeeds when $\zeta_{score}=85, \zeta_{lex}=50$. |
| **Bilingual Localization**<br>`@[backend_v2/l10n/fi.json]`<br>`@[backend_v2/l10n/en.json]` | Hardcoding Finnish or English labels in code; missing descriptive metadata keys for lexical strictness. | Add `"metadata_lexical_strictness"` to both `fi.json` and `en.json` maintaining 100% key parity. | Avoid verbose multi-paragraph explanations in localization dictionary; keep terms clear and concise. | `test_localization_parity.py` verifying identical key sets across Finnish and English files. |
| **Worker Unit Test Suite**<br>`@[backend_v2/tests/unit/workers/test_execution_worker.py]` | Asserting happy path only without asserting propagation of decoupled strictness parameters. | Assert that `execute_workflow_job` extracts and forwards both `strictness_level` and `lexical_strictness_level` to `mock_engine`. | Avoid complex multi-service integration fixtures; test worker orchestration in pure unit isolation. | `uv run pytest backend_v2/tests/unit/workers/test_execution_worker.py` passes 100%. |
| **Anchor Validation Test Suite**<br>`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` | Missing verification that high scoring strictness permits morphological stemming when lexical strictness is normal. | Test matrix asserting: 1) $\zeta_{score}=85, \zeta_{lex}=50$ passes inflections; 2) $\zeta_{lex}=100$ rejects inflections; 3) invalid strictness raises `ValidationError`. | Avoid redundant synthetic tests; focus on high-entropy morphological inflection boundaries. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` passes 100%. |

```xml

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS">
    <action>Look backward: Verify multi-segment lexical validation is operational in @[backend_v2/services/orchestrator/anchor_validation_service.py#L25-L836].</action>
    <action>Look forward: Verify workflow models in @[backend_v2/models/domain/workflow.py#L25-L208] and seed data structure in @[backend_v2/seed/seed_data.json#L20538-L21331] before adding decoupled lexical strictness fields.</action>
    <action>Pre-implementation technical debt cleanup: Audit touched files for legacy dictionary accesses, loose `.get()` fallbacks, or unannotated fields, ensuring 100% Pydantic V2 strict typed compliance.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/04_phase4_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/domain/workflow.py#L25-L208]</backend>
    <backend>@[backend_v2/models/dtos/studio.py#L89-L138]</backend>
    <backend>@[backend_v2/models/dtos/studio.py#L582-L615]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py#L40-L672]</backend>
    <backend>@[backend_v2/seed/seed_data.json#L20538-L21331]</backend>
    <backend>@[backend_v2/settings.py#L985-L1006]</backend>
    <backend>@[backend_v2/workers/execution_worker.py#L75-L538]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py#L597-L1794]</backend>
    <backend>@[backend_v2/services/orchestrator/extractive_sensor_service.py#L175-L728]</backend>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py#L25-L836]</backend>
    <backend>@[backend_v2/l10n/fi.json]</backend>
    <backend>@[backend_v2/l10n/en.json]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_execution_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100)] = 50` added to `Workflow` in @[backend_v2/models/domain/workflow.py#L25-L208] and Studio DTOs in @[backend_v2/models/dtos/studio.py#L89-L138] and @[backend_v2/models/dtos/studio.py#L582-L615].</item>
    <item>Studio workflow CRUD service updated in @[backend_v2/services/studio/workflow_service.py#L40-L672] to transit `default_lexical_strictness_level`.</item>
    <item>All 3 seeded workflows in @[backend_v2/seed/seed_data.json#L20538-L21331] synchronized with `"default_lexical_strictness_level": 50`.</item>
    <item>`get_lexical_fuzz_threshold` in @[backend_v2/settings.py#L985-L1006] calibrated to resolve threshold dynamically from decoupled lexical strictness.</item>
    <item>`AnchorValidationService` in @[backend_v2/services/orchestrator/anchor_validation_service.py#L25-L836] updated to accept and evaluate decoupled `lexical_strictness_level`.</item>
    <item>`execution_worker.py`, `dag_executor.py`, and `extractive_sensor_service.py` updated to extract and pass `lexical_strictness_level` to `AnchorValidationService`.</item>
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
    <action>In @[backend_v2/models/domain/workflow.py#L25-L208]: Verify field `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100, description="Sovereign workflow lexical strictness level (0-100 continuous).")] = 50` on `Workflow` domain model.</action>
    <action>In @[backend_v2/models/dtos/studio.py#L89-L138]: Add field `default_lexical_strictness_level: Annotated[int, Field(default=50, ge=0, le=100, description="Lexical strictness level")] = 50` to `WorkflowCreateDTO`.</action>
    <action>In @[backend_v2/models/dtos/studio.py#L582-L615]: Add field `default_lexical_strictness_level: Annotated[int | None, Field(default=None, ge=0, le=100, description="Updated sovereign workflow lexical strictness level")] = None` to `WorkflowUpdateDTO`.</action>
    <constraint invariant="variable_and_schema_preservation_mandate">Preserve exact field nomenclature `default_lexical_strictness_level` across backend and studio DTOs.</constraint>
  </step>

  <step id="2" name="UPDATE STUDIO WORKFLOW SERVICE">
    <action>In @[backend_v2/services/studio/workflow_service.py#L40-L672]: Transit `default_lexical_strictness_level` across workflow creation, draft creation, cloning, update, and retrieval pipelines.</action>
    <constraint invariant="zero_service_layer_fallbacks">Fail-Fast if lexical strictness is out of [0, 100] integer bounds.</constraint>
  </step>

  <step id="3" name="SYNCHRONIZE DATABASE SEED VAULT &amp; LOCALIZATION STRINGS">
    <action>In @[backend_v2/seed/seed_data.json#L20538-L21331]: Add `"default_lexical_strictness_level": 50` to all 3 seeded workflow records (`wf_9d68c573802341db`, `wf_a8f1d71000000001`, `wf_b9e2d71000000002`), keeping scoring `default_strictness_level` intact.</action>
    <action>In @[backend_v2/l10n/fi.json]: Add `"metadata_lexical_strictness": "Leksikaalinen tiukkuus"`.</action>
    <action>In @[backend_v2/l10n/en.json]: Add `"metadata_lexical_strictness": "Lexical Strictness"`.</action>
    <constraint invariant="prompt_preservation_mandate">Do NOT mutate, tighten, or amputate any natural-language prompt text or description in `seed_data.json`.</constraint>
  </step>

  <step id="4" name="CALIBRATE SETTINGS LEXICAL THRESHOLD RESOLUTION">
    <action>In @[backend_v2/settings.py#L985-L1006]: Update `get_lexical_fuzz_threshold(locale: str | None = None, lexical_strictness_level: int = 50) -> float` to incorporate decoupled `lexical_strictness_level` and compute fuzzy/stemmed thresholds dynamically.</action>
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py#L25-L836]: Accept `lexical_strictness_level: int = 50` in `_is_lexically_valid`, `validate_evidence`, and `process_atom_evaluation`, delegating threshold resolution directly to `get_lexical_fuzz_threshold(locale, lexical_strictness_level=lexical_strictness_level)`.</action>
    <constraint invariant="cognitive_dampening_square_root_model">Keep score dampening strictly separated from lexical matching thresholds.</constraint>
  </step>

  <step id="5" name="TRANSIT DECOUPLED STRICTNESS IN EXECUTION PIPELINE">
    <action>In @[backend_v2/workers/execution_worker.py#L75-L538]: Extract both `default_strictness_level` and `default_lexical_strictness_level` from `Workflow` and pass them into the execution parameters.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L597-L1794]: Transit `lexical_strictness_level` through `execute_workflow`, `node_executor.execute`, and `StrategyContext` execution context.</action>
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py#L175-L728]: Update `_fuzzy_match`, `pre_evaluate`, `_batch_fuzzy_match`, and `batch_pre_evaluate` to pass `lexical_strictness_level` to `get_lexical_fuzz_threshold` and `AnchorValidationService` during evidence validation.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Single sovereign pipeline for strictness transit; zero fallback guessing.</constraint>
  </step>

  <step id="6" name="EXPAND WORKER &amp; ANCHOR VALIDATION TEST SUITES">
    <action>In @[backend_v2/tests/unit/workers/test_execution_worker.py]: Add test `test_execution_worker_transits_decoupled_strictness_parameters` verifying that `execution_worker.py` correctly extracts and propagates both strictness parameters.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]: Add test `test_strictness_decoupling_high_scoring_allows_morphology` asserting that high scoring strictness ($\zeta_{score} = 85$) with default lexical strictness ($\zeta_{lex} = 50$) permits valid Finnish grammatical case inflections via Gate 5 Snowball stemmer, while absolute lexical strictness ($\zeta_{lex} = 100$) rejects it.</action>
    <constraint invariant="universal_quality_gate">Audit and test execution must pass 100%.</constraint>
  </step>

  <test_contracts>
    <test name="test_strictness_decoupling_high_scoring_allows_morphology" category="positive">
      <input>score_strictness=85, lexical_strictness=50, candidate inflected Finnish word "johtajuus ja selkeät tavoitteet" against "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin."</input>
      <expected>Gate 5 Snowball stemmer accepts inflection; score dampening uses gamma(85)</expected>
    </test>
    <test name="test_strictness_decoupling_absolute_lexical_rejects_morphology" category="negative">
      <input>score_strictness=85, lexical_strictness=100, candidate inflected Finnish word "johtajuus ja selkeät tavoitteet"</input>
      <expected>AnchorValidationService raises SemanticEvidenceError under 100% exact match requirement</expected>
    </test>
    <test name="test_lexical_strictness_bounds_validation_negative" category="negative">
      <input>default_lexical_strictness_level=-1 or default_lexical_strictness_level=101</input>
      <expected>Pydantic ValidationError raised immediately during model validation</expected>
    </test>
    <test name="test_workflow_seed_validation_dry_run" category="positive">
      <input>uv run python backend_v2/seed/run_seed.py local --dry-run</input>
      <expected>All 3 seeded workflows validate without schema errors</expected>
    </test>
    <test name="test_get_lexical_fuzz_threshold_strictness_tiers" category="positive">
      <input>get_lexical_fuzz_threshold across strictness tiers 0, 30, 50, 85, 100 for Finnish and English</input>
      <expected>Thresholds scale with calibrated multipliers: 85.0*0.8=68.0, 85.0*0.9=76.5, 85.0*1.0=85.0, 85.0*1.02=86.7, 100.0</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute worker unit tests: `uv run pytest backend_v2/tests/unit/workers/test_execution_worker.py`.</action>
    <action>Execute anchor validation tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`.</action>
    <action>Execute dry-run seed validation: `uv run python backend_v2/seed/run_seed.py local --dry-run`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/workflow.py backend_v2/models/dtos/studio.py backend_v2/services/studio/workflow_service.py backend_v2/workers/execution_worker.py backend_v2/services/orchestrator/dag_executor.py backend_v2/services/orchestrator/extractive_sensor_service.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
