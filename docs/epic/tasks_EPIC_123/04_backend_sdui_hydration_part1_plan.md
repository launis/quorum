# Phase 4: Producer Logic (Backend SDUI Hydration - Part 1: Global & Variance) Plan

This plan migrates the backend blueprint to hydrate global synthesis and variance data directly into SDUI Blocks instead of passing raw string fields.

### Human Overview
- **Target Files**: `backend_v2/services/blueprint.py`
- **Test Files**: `backend_v2/tests/unit/services/test_blueprint.py`
- **Goals**: Map `executive_summary`, `user_role`, and `user_role_justification` into strictly typed `ParagraphBlock`s. Map `variance_validation` into `SduiGridBlock` and `AlertBlock`. Implement telemetry SDUI blocks.

```xml
<system_prompt>
  <objective>Refactor backend blueprint logic to map global synthesis and variance data directly into SDUI blocks.</objective>
  <role>Principal Solutions Architect</role>
  
  <execution_protocol level="2_execute">
    <step id="1" name="GLOBAL SYNTHESIS HYDRATION">
      <action>Modify @[c:\src\quorum\backend_v2\services\blueprint.py].</action>
      <action>Extract `executive_summary`, `user_role`, and `user_role_justification` from the `profile_cache` (`RenderedSynthesisCache`) within `BlueprintTransformer.build_report_dto`.</action>
      <action>Convert these fields into strictly typed `ParagraphBlock` instances from `backend_v2.models.view.sdui` if they contain data.</action>
      <action>Append these new `ParagraphBlock` instances into the `content_blocks` array (around line 950) so they are seamlessly injected into the primary `ReportLayoutDTO`'s `synthesis_blocks` array.</action>
      <constraint invariant="tripartite_rendering_boundary">Do NOT hardcode UI layouts (like tables) in the Markdown strings. Just use standard markdown content.</constraint>
      <constraint invariant="fail_fast_hydration_mandate">Ensure `profile_cache` exists before attempting extraction. Use strict Pydantic V2 instantiation for the SDUI blocks.</constraint>
    </step>

    <step id="2" name="VARIANCE VALIDATION HYDRATION">
      <action>Modify `_extract_matrices_and_extensions` in @[c:\src\quorum\backend_v2\services\blueprint.py].</action>
      <demolish>REMOVE: Appending of the `variance_validation` naked dictionary to `grouped_extensions[wf_ext]`.</demolish>
      <action>Map the variance verification results into typed SDUI blocks (`SduiGridBlock` and `AlertBlock`) specifically into the `inner_sdui_blocks` array of the corresponding `MatrixScorecardRowDTO`.</action>
      <action>Specifically and exhaustively: use an `SduiGridBlock` (strict 2-column grid for "Mekaaninen" and "Kognitiivinen" metrics) and an `AlertBlock` (for the verdict). Ensure the grid items are coerced to `str` to satisfy the strict `list[str]` typing.</action>
      <constraint invariant="frozen_state_mutability">Because `MatrixScorecardRowDTO` inherits from `V2CoreBase` (frozen state), you MUST NOT mutate `.inner_sdui_blocks` in place. You MUST use `.model_copy(update={'inner_sdui_blocks': [...]})` or instantiate it cleanly.</constraint>
      <constraint invariant="the_no_legacy_mandate">Do NOT create a domain-specific `SduiVarianceBlock`. Strictly reuse existing polymorphic SDUI blocks.</constraint>
    </step>

    <step id="3" name="TELEMETRY HYDRATION">
      <action>Modify @[c:\src\quorum\backend_v2\services\blueprint.py].</action>
      <action>Update `_hydrate_printable_sources_block` and `_hydrate_jargon_ratio_block` methods.</action>
      <action>Ensure they explicitly instantiate and return strictly typed `ParagraphBlock` objects within their `list[AnySduiBlock]` returns.</action>
      <constraint invariant="sdui_contract_fracture_prevention">Ensure that the `ParagraphBlock` usage perfectly aligns with the Flutter frontend `SduiBlockDTO.paragraph` serialization.</constraint>
    </step>

    <step id="4" name="TEST FIXTURE SYNC & AUDIT">
      <action>Search for and identify the relevant unit tests for `blueprint.py` specifically: `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]`. Update them to reflect the new SDUI block outputs instead of `GlobalSynthesisDTO` or raw strings.</action>
      <action>Explicitly add negative test scenarios (at least 2) for missing data in the synthesis and variance blocks as mandated by `anti_happy_path_mandate`.</action>
      <action>Run the backend audit script to verify type constraints and test integrity:</action>
      <action>`uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`</action>
      <constraint invariant="atomic_checkpoint_mandate">If the audit script passes, explicitly instruct the user to atomic commit these backend hydration changes before proceeding to Phase 5.</constraint>
    </step>
  </execution_protocol>
</system_prompt>
