<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 2: Scale Projection & Atom Hydration Stage Extraction (`phase2_scale_and_atom_stage_extraction.md`)

## 1. Objective
Execute Epoch 1 Phase 1B of the `MatrixDomainParser` decomposition:
1. Extract the matrix payload unpacking stage (`unpack_matrix_payload`), mathematical scale boundary and UI display score projection stage (`compute_scale_and_score_projection` returning `[NEW]` `MatrixScaleProjectionDTO` defined in `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]`), and step TDA scorecard atom hydration stage (`hydrate_step_scorecard_atoms` returning `[NEW]` `MatrixAtomHydrationResultDTO` defined in `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]`) into `[NEW] @[backend_v2/services/matrix_parser/scale_and_atom_stage.py]`.
2. Delegate those three pipeline stages inside `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`) to `[NEW] @[backend_v2/services/matrix_parser/scale_and_atom_stage.py]` with 100% identical runtime behavior and zero changes to public signatures.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/matrix_parser/scale_and_atom_stage.py]` | Pipeline stage functions: `unpack_matrix_payload`, `compute_scale_and_score_projection`, and `hydrate_step_scorecard_atoms` |
| `[MODIFY]` | `@[backend_v2/services/matrix_domain_parser.py#L118-L732]` | Delegate payload unpacking, scale/score projection, and TDA atom hydration in `MatrixDomainParser.parse_matrices` to `[NEW] @[backend_v2/services/matrix_parser/scale_and_atom_stage.py]` |
| `[CONTEXT]` | `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]` | Stage DTO contracts (`[NEW]` `MatrixScaleProjectionDTO`, `[NEW]` `MatrixAtomHydrationResultDTO`) created in Phase 1 |
| `[CONTEXT]` | `@[docs/epic/tasks_matrix_domain_parser/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` | Existing 34-test unit suite verifying 100% behavioral parity |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Scale and Atom Stage Module backend_v2/services/matrix_parser/scale_and_atom_stage.py">
    <constraint invariant="topological_leaf_first_extraction_mandate">Extracted sub-modules MUST NEVER import from backend_v2/services/matrix_domain_parser.py.</constraint>
    <constraint invariant="mathematical_extrema_anchoring">Preserve dynamic resolution of math_min and math_max from pb_meta.computed_min and pb_meta.computed_max and Fail-Fast validation of scales_def and custom_scale_min/max.</constraint>
    <constraint invariant="ban_anonymous_state_tuples">Return strictly typed immutable MatrixScaleProjectionDTO and MatrixAtomHydrationResultDTO instances instead of multi-value tuples.</constraint>
    <action>Create `[NEW] @[backend_v2/services/matrix_parser/scale_and_atom_stage.py]` (< 320 lines) defining three stage functions relocated from `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`):
      1. `unpack_matrix_payload(block_data: Any, block_id: str) -> TraceMatrixPayloadDTO`:
         - Relocate lines 180-195 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
         - Hydrate `TraceMatrixPayloadDTO` from `TraceMatrixPayloadDTO`, `LightweightMatrixOutput` (via `TraceMatrixPayloadDTO.model_validate(block_data.model_dump(mode="python"))`), or raw payload (`TraceMatrixPayloadDTO.model_validate(block_data)`).
         - Catch `(ValidationError, TypeError, ValueError)`, log `ErrorCodes.VALIDATION_FAILED.name`, and raise `AppException` with HTTP 500 and `ErrorCodes.VALIDATION_FAILED.value`.
      2. `compute_scale_and_score_projection(matrix_payload: TraceMatrixPayloadDTO, pb_meta: MatrixPromptBlock, profile: OutputProfile, locale: str, block_id: str) -> MatrixScaleProjectionDTO`:
         - Relocate lines 196-214, 234-355, and 554-560 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
         - Compute `true_atoms`, `total_atoms`, `raw_score`, and `norm_score` when `matrix_payload.evaluated_atoms` is populated (including the `total_atoms == 0` N_A bypass log).
         - Enforce Fail-Fast checks for `pb_meta.computed_min is None or pb_meta.computed_max is None` (`ErrorCodes.CONFIGURATION_ERROR`), `not pb_meta.scales` (`ErrorCodes.CONFIGURATION_ERROR`), missing `s.name` on any scale (`ErrorCodes.VALIDATION_FAILED`), and missing `profile.custom_scale_min` or `profile.custom_scale_max` under `DisplayScale.CUSTOM` (`ErrorCodes.CONFIGURATION_ERROR`).
         - Populate `level_names`, `ui_boundary_labels`, `display_scale_min`, `display_scale_max`, `score_float` (via `scale_to_custom_range` for `DisplayScale.CUSTOM`), `ui_plot_ratio`, and `score_display_label`, returning a created `MatrixScaleProjectionDTO` instance.
      3. `hydrate_step_scorecard_atoms(results: list[Any], step_id: str, pb_meta: MatrixPromptBlock, level_names: dict[str, str], locale: str, matrix_visible_cols: list[str], step_scorecard_atoms_accum: dict[str, list[ScorecardAtomDTO]]) -> MatrixAtomHydrationResultDTO`:
         - Relocate lines 422-553 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
         - Scan `results` for matching `step_id` and `block_id == "results"`, validating `AtomResultDTO` items (`ErrorCodes.VALIDATION_FAILED` on invalid atom payload).
         - Iterate over `pb_meta.scales`, `scale.claims`, and `claim.tda_assertions` to construct `ScorecardAtomDTO` with `ReasoningStepDTO` and `QuoteEvidenceDTO.model_validate({"source_quotes": val_data.source_quotes, "source_alias": []}, context={"alias_registry": {}})`, appending each `ScorecardAtomDTO` to `evaluated_atoms_list` and `step_scorecard_atoms_accum[step_id]`.
         - Return a created `MatrixAtomHydrationResultDTO(evaluated_atoms=evaluated_atoms_list, clustered_row_sources=[])`.
      4. Declare `__all__ = ["compute_scale_and_score_projection", "hydrate_step_scorecard_atoms", "unpack_matrix_payload"]`.
    </action>
  </step>

  <step id="2" name="Delegate Scale and Atom Stages in backend_v2/services/matrix_domain_parser.py">
    <constraint invariant="two_epoch_separation_mandate">Preserve 100% identical behavior and order of Fail-Fast checks in MatrixDomainParser.parse_matrices.</constraint>
    <action>Modify `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`):
      1. Import `compute_scale_and_score_projection`, `hydrate_step_scorecard_atoms`, and `unpack_matrix_payload` from `backend_v2.services.matrix_parser.scale_and_atom_stage`.
      2. Replace inline payload validation (lines 180-195) with `matrix_payload = unpack_matrix_payload(block_data, b_id)`.
      3. Keep the `pb_meta.label` check before scale projection so Fail-Fast exception ordering remains 100% identical, then invoke `scale_proj = compute_scale_and_score_projection(matrix_payload=matrix_payload, pb_meta=pb_meta, profile=profile, locale=locale, block_id=b_id)`.
      4. Replace inline atom hydration (lines 422-553) with `atom_hydration = hydrate_step_scorecard_atoms(results=results, step_id=step_id, pb_meta=pb_meta, level_names=scale_proj.level_names, locale=locale, matrix_visible_cols=matrix_visible_cols, step_scorecard_atoms_accum=step_scorecard_atoms_accum)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` and `uv run pytest backend_v2/tests/unit/services/test_blueprint.py -k "matrix"`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_parse_matrices_custom_scale_success">
      Verifies that DisplayScale.CUSTOM projects raw_score using scale_to_custom_range into custom_scale_min..custom_scale_max and formats score_display_label.
    </contract>
    <contract type="positive" name="test_parse_matrices_atom_hydration_and_quotes">
      Verifies that evaluated AtomResultDTO items with source_quotes hydrate into ScorecardAtomDTO items with QuoteEvidenceDTO and populate step_scorecard_atoms.
    </contract>
    <contract type="negative" name="test_parse_matrices_missing_computed_min_max_fails_fast">
      Verifies that a MatrixPromptBlock with computed_min=None logs ErrorCodes.CONFIGURATION_ERROR and raises AppException(HTTP 500).
    </contract>
    <contract type="negative" name="test_parse_matrices_invalid_atom_result_payload_fails_fast">
      Verifies that malformed atom entries in the step "results" payload log ErrorCodes.VALIDATION_FAILED and raise AppException(HTTP 500).
    </contract>
  </test_contracts>
</execution_protocol>
```
