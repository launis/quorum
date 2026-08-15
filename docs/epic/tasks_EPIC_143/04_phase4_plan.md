# Phase 4: SDUI Presentation & XAI Highlights Fair Distribution

**Overview:** Fix Phase 3 (SDUI Presentation) Primacy Bias and Category Starvation in XAI Highlights accordion rendering by integrating `ranked_round_robin_select`, eliminating duck-typing, and introducing strict graceful UI degradation when XAI is disabled.
**Target Files:**
- `[MODIFY]` @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1, Phase 2, and Phase 3. Verify ranked_round_robin utility, distiller wiring, and hardened MatrixExplanationService pass all tests.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py] and @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `XaiHighlightsAdapter.build` integrates `ranked_round_robin_select` to curate highlights across active extension types ranked by informativeness/length.
    - [ ] Graceful UI degradation implemented: returns `[]` immediately if `profile.visible_block_extensions` is empty/None or `profile.max_extension_items` is zero/None.
    - [ ] Duck-typing eliminated (`isinstance(item, dict)`, `.get()`, `getattr()`): validates raw items into `XaiHighlightItem` with warning logging on parse failure.
    - [ ] Primacy Bias and Category Starvation eliminated in SDUI accordion rendering without requiring Flutter DTO or database schema changes.
    - [ ] Unit tests in @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py] updated and expanded with 4 new tests.
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/01-python-backend.md]
    - @[.agents/rules/05_llm_architecture.md]
    - @[ki_god_code_prevention.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_context_enriched_decompose_verify.md]
    - @[ki_llm_extraction_architecture.md]
    - @[ki_topological_engine.md]
    - @[ki_execution_engine_protocol.md]
    - @[ki_matrix_sensor_prompt_builder.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT modify Flutter Dart Freezed DTOs in client_app_v2 (SDUI presentation schema is invariant).
    - Do NOT use duck-typing (.get(), getattr(), isinstance(dict)) in XaiHighlightsAdapter.
    - Do NOT hardcode fallback strings for missing extension labels.
  </anti_targets>

  <step id="1" name="XAI Highlights SDUI Adapter Hardening &amp; Round-Robin Fair Distribution">
    <action>Modify @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py] (function `build`):
1. Import `ranked_round_robin_select` from `backend_v2.utils.ranked_round_robin`, `XaiHighlightItem` from `backend_v2.models.dtos.synthesis`, and `ErrorCodes` from `backend_v2.exceptions`.
2. Graceful UI degradation: if not profile.visible_block_extensions or not profile.max_extension_items: return [].
3. Validate raw highlight items strictly using XaiHighlightItem.model_validate(raw_item, strict=False) inside a try/except (ValidationError, ValueError) block with warning log.
4. Pre-filter and curate highlights using ranked_round_robin_select:
   - items=valid_highlights
   - group_key=lambda h: h.extension_type
   - rank_key=lambda h: len(h.content)
   - max_items=len(profile.visible_block_extensions) * profile.max_extension_items
   - reverse_rank=True
5. Populate AccordionBlock and AlertBlock children from curated_highlights, preserving XAI_AESTHETICS_RULES and Fail-Fast dictionary lookups.
    </action>
    <constraint invariant="the_zero_compromise_pledge">Eliminate all duck-typing and fallback defaults in SDUI presentation logic.</constraint>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure SDUI block output structures remain 100% compliant with existing Flutter client parsers.</constraint>
  </step>

  <step id="2" name="XAI Highlights SDUI Adapter Unit Tests">
    <action>Modify @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]:
1. Add test_build_graceful_degradation_disabled_extensions (visible_block_extensions=[] returns []).
2. Add test_build_graceful_degradation_zero_max_items (max_extension_items=0 returns []).
3. Add test_build_ranked_round_robin_distribution (verifies fair interleaving across coaching, falsification, and remediation_steps with longest content prioritized).
4. Add test_build_malformed_highlight_item_skipped (verifies malformed dict is logged and skipped while valid items render).
    </action>
    <test_contracts>
      <test name="test_build_graceful_degradation_disabled_extensions" category="boundary">
        <input>context with profile.visible_block_extensions=[]</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_graceful_degradation_zero_max_items" category="boundary">
        <input>context with profile.max_extension_items=0</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_ranked_round_robin_distribution" category="positive">
        <input>highlights with 3 categories having 4 items each, max_items=2 per category</input>
        <expected>accordions receive longest items interleaved equitably without Primacy Bias</expected>
      </test>
      <test name="test_build_malformed_highlight_item_skipped" category="error_path">
        <input>highlights containing malformed dict missing required content</input>
        <expected>logs warning with INVALID_OUTPUT_SCHEMA and renders valid items</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    Run automated unit tests and audit loops:
    `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py`
    `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters/ --test`
    `uv run pytest backend_v2/tests/e2e/test_golden_master_sdui.py`
    `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
  </validation_gate>
</execution_protocol>
```
