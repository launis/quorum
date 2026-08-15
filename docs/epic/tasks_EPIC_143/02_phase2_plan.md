# Phase 2: Distiller Unfiltered Context Pipeline & Locale Hoisting

**Overview:** Remove the flawed `target_blocks` filter from `synthesis_distiller.py`, pass complete cognitive execution state to `<source>` prompt blocks and `MatrixExplanationService`, hoist and unify `target_locale` validation at hook entry, purge the deprecated `"language"` key from `state_delta`, and create comprehensive distiller wiring tests.
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify ranked_round_robin utility exists and passes tests.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/orchestrator/synthesis_distiller.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] AST boundary verification pre-step executed for @[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L323].
    - [ ] `target_locale` validation hoisted to the start of `synthesis_distiller_hook` with strict Fail-Fast checks for non-empty string.
    - [ ] Parameter renamed from `language` to `target_locale` in `_build_title_map`.
    - [ ] `target_blocks` filter loop confirmed completely deleted from `synthesis_distiller.py`.
    - [ ] `available_dtos` contains unfiltered execution state and is passed directly to `<source>` prompt blocks generation and `MatrixExplanationService.assemble_matrices_to_explain`.
    - [ ] Deprecated `"language": target_locale` key purged from `HookResult.state_delta` (exporting ONLY `"target_locale"`).
    - [ ] Comprehensive wiring unit tests implemented in `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py].
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/01-python-backend.md]
    - @[.agents/rules/05_llm_architecture.md]
    - @[ki_god_code_prevention.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_context_enriched_decompose_verify.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_llm_extraction_architecture.md]
    - @[ki_topological_engine.md]
    - @[ki_execution_engine_protocol.md]
    - @[ki_matrix_sensor_prompt_builder.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT filter available_dtos against output_profile.layouts[].target_blocks in the distiller hook.
    - Do NOT retain dual-export fallbacks ("language": target_locale) in HookResult.state_delta.
    - Do NOT touch MatrixExplanationService internal implementation in Phase 2 (handled in Phase 3).
  </anti_targets>

  <step id="1" name="AST Boundary Verification Pre-Step (God File Mandate)">
    <action>Write and execute a temporary Python AST verification script in the scratch directory to extract exact lineno and end_lineno of synthesis_distiller_hook (L159-L323) and _build_title_map (L111-L156) in @[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L323].</action>
    <constraint invariant="ast_boundary_verification_mandate">Per ki_god_code_prevention.md, you MUST NOT rely on grep_search to find method boundaries in files exceeding 300 lines.</constraint>
  </step>

  <step id="2" name="Synthesis Distiller Locale Hoisting &amp; Legacy Key Purge">
    <action>[ALREADY_IMPLEMENTED] - Target_blocks pruning removal, locale hoisting, and assemble_matrices_to_explain call verified within @[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L323].
[ALREADY_IMPLEMENTED] - _build_title_map parameter renaming verified at @[backend_v2/services/orchestrator/synthesis_distiller.py#L111-L156].
    </action>
    <action>In @[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L323], execute demolition of the legacy `"language"` key:
    <demolish>
REMOVE: `"language": target_locale,` inside HookResult.state_delta in synthesis_distiller_hook.
REPLACE WITH: Complete removal of the line, keeping only `"target_locale": target_locale,` in state_delta.
    </demolish>
    </action>
    <constraint invariant="the_no_legacy_mandate">Zero Backwards Compatibility: legacy "language" key must be completely purged from HookResult.state_delta.</constraint>
  </step>

  <step id="3" name="Synthesis Distiller Wiring Unit Tests">
    <action>Create `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py] to test:
1. synthesis_distiller_hook passes unfiltered available_dtos to both &lt;source&gt; block distillation (distilled_inputs) and MatrixExplanationService along with target_locale.
2. synthesis_distiller_hook fails fast with AppException(VALIDATION_FAILED) when target_locale is missing from state.metadata or contains whitespace-only strings.
3. distilled_inputs preserves upstream cognitive sensor findings and verbatim evidence quotes.
4. result.state_delta contains "target_locale" and STRICTLY DOES NOT contain "language", proving Zero Backwards Compatibility (the_no_legacy_mandate).
    </action>
    <test_contracts>
      <test name="test_synthesis_distiller_wiring_passes_unfiltered_dtos" category="positive">
        <input>HookState with 2 cognitive sensor steps and 1 matrix step</input>
        <expected>distilled_inputs contains all 3 steps in &lt;source&gt; blocks, matrices_to_explain receives all 3 steps</expected>
      </test>
      <test name="test_synthesis_distiller_wiring_missing_target_locale_raises_app_exception" category="error_path">
        <input>HookState with metadata missing "target_locale"</input>
        <expected>raises AppException with error_code VALIDATION_FAILED</expected>
      </test>
      <test name="test_synthesis_distiller_wiring_whitespace_target_locale_raises_app_exception" category="boundary">
        <input>HookState with metadata["target_locale"] = "   "</input>
        <expected>raises AppException with error_code VALIDATION_FAILED</expected>
      </test>
      <test name="test_synthesis_distiller_wiring_state_delta_purges_legacy_language_key" category="positive">
        <input>Valid HookState execution</input>
        <expected>"target_locale" in result.state_delta and "language" not in result.state_delta</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    Run automated unit tests:
    `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py`
    `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_distiller.py --test`
  </validation_gate>
</execution_protocol>
```
