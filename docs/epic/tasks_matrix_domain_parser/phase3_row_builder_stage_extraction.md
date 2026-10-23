<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 3: Context Target Resolution & Row Builder Stage Extraction (`phase3_row_builder_stage_extraction.md`)

## 1. Objective
Execute Epoch 1 Phase 1C of the `MatrixDomainParser` decomposition:
1. Extract axis name and collision resolution (`resolve_unique_axis_name`), axis description resolution (`resolve_axis_description`), three-tier deterministic context target resolution (`resolve_context_target` returning `[NEW]` `MatrixContextTargetResultDTO` defined in `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]`), and `MatrixScorecardRowDTO` construction (`build_matrix_scorecard_row`) into `[NEW] @[backend_v2/services/matrix_parser/row_builder_stage.py]`.
2. Delegate those four pipeline functions inside `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`) to `[NEW] @[backend_v2/services/matrix_parser/row_builder_stage.py]` with 100% identical runtime behavior, reducing `MatrixDomainParser` to a clean `< 150`-line orchestrator facade ready for Phase 4 atomic package cutover.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/matrix_parser/row_builder_stage.py]` | Stage functions: `resolve_unique_axis_name`, `resolve_axis_description`, `resolve_context_target`, and `build_matrix_scorecard_row` |
| `[MODIFY]` | `@[backend_v2/services/matrix_domain_parser.py#L118-L732]` | Delegate axis label resolution, context target resolution, and `MatrixScorecardRowDTO` assembly in `MatrixDomainParser.parse_matrices` to `[NEW] @[backend_v2/services/matrix_parser/row_builder_stage.py]` |
| `[CONTEXT]` | `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]` | Stage DTO contracts (`[NEW]` `MatrixScaleProjectionDTO`, `[NEW]` `MatrixAtomHydrationResultDTO`, `[NEW]` `MatrixContextTargetResultDTO`) created in Phase 1 |
| `[CONTEXT]` | `@[docs/epic/tasks_matrix_domain_parser/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` | Existing 34-test unit suite verifying 100% behavioral parity |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Row Builder Stage Module backend_v2/services/matrix_parser/row_builder_stage.py">
    <constraint invariant="topological_leaf_first_extraction_mandate">Extracted sub-modules MUST NEVER import from backend_v2/services/matrix_domain_parser.py.</constraint>
    <constraint invariant="dynamic_vs_static_localization_ssot_mandate">Preserve Three-Tier Deterministic Context Target Resolution using ExpectedInput.label and LocalizationService.translate.</constraint>
    <constraint invariant="ban_anonymous_state_tuples">Return strictly typed immutable MatrixContextTargetResultDTO and MatrixScorecardRowDTO instances.</constraint>
    <action>Create `[NEW] @[backend_v2/services/matrix_parser/row_builder_stage.py]` (< 250 lines) defining four stage functions relocated from `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`):
      1. `resolve_unique_axis_name(pb_meta: MatrixPromptBlock, block_id: str, step_id: str, locale: str, workflow_steps: dict[str, StepRule], all_parsed_matrices: dict[str, MatrixScorecardRowDTO]) -> str`:
         - Relocate lines 215-229 and 356-365 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
         - Validate `pb_meta.label` (logging `ErrorCodes.CONFIGURATION_ERROR.name` and raising `AppException` with HTTP 500 if missing), resolve `axis_name = pb_meta.label.resolve(locale)` (falling back to `block_id` when empty), and disambiguate collisions against `all_parsed_matrices.values()` using `workflow_steps[step_id].id` and `collision_counter`.
      2. `resolve_axis_description(pb_meta: MatrixPromptBlock, locale: str) -> str`:
         - Relocate lines 230-233 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
      3. `resolve_context_target(step_id: str, pb_meta: MatrixPromptBlock, workflow_steps: dict[str, StepRule], expected_inputs_map: dict[str, ExpectedInput] | None) -> MatrixContextTargetResultDTO`:
         - Relocate lines 566-619 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
         - Resolve `step_input_keys` from `step_rule.input_mappings.values()`, apply Tier 1 (Single-Input Step), Tier 2 (Multi-Input Step with `pb_meta.target_input_key`), and Tier 3 (`ExpectedInput.label` or `LocalizationService.translate`), returning a created `MatrixContextTargetResultDTO(context_target=context_target, context_target_label=context_target_label)`.
      4. `build_matrix_scorecard_row(block_id: str, axis_name: str, axis_description: str, pb_meta: MatrixPromptBlock, matrix_payload: TraceMatrixPayloadDTO, scale_proj: MatrixScaleProjectionDTO, axis_level_breakdown: dict[str, str] | None, cleaned_explanation: str, atom_hydration: MatrixAtomHydrationResultDTO, context_target_res: MatrixContextTargetResultDTO) -> MatrixScorecardRowDTO`:
         - Relocate lines 620-713 of `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`.
         - Map `matrix_payload.extensions`, `pb_meta.theory_grounding` (`citation_reference` and `source_url`), `validated_evidence_type`, and stage DTO fields into `MatrixScorecardRowDTO`.
      5. Declare `__all__ = ["build_matrix_scorecard_row", "resolve_axis_description", "resolve_context_target", "resolve_unique_axis_name"]`.
    </action>
  </step>

  <step id="2" name="Delegate Context Target and Row Builder Stages in backend_v2/services/matrix_domain_parser.py">
    <constraint invariant="two_epoch_separation_mandate">Keep MatrixDomainParser.parse_matrices public signature and Fail-Fast exception ordering 100% identical.</constraint>
    <action>Modify `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`):
      1. Import `build_matrix_scorecard_row`, `resolve_axis_description`, `resolve_context_target`, and `resolve_unique_axis_name` from `backend_v2.services.matrix_parser.row_builder_stage`.
      2. Replace inline label check, axis description, and collision disambiguation with `axis_name = resolve_unique_axis_name(pb_meta=pb_meta, block_id=b_id, step_id=step_id, locale=locale, workflow_steps=workflow_steps, all_parsed_matrices=all_parsed_matrices)` and `axis_description = resolve_axis_description(pb_meta=pb_meta, locale=locale)` while preserving exact Fail-Fast check order (`unpack_matrix_payload` -> `pb_meta.label` check inside `resolve_unique_axis_name` -> `compute_scale_and_score_projection`).
      3. Replace inline context target resolution (lines 566-619) with `context_target_res = resolve_context_target(step_id=step_id, pb_meta=pb_meta, workflow_steps=workflow_steps, expected_inputs_map=expected_inputs_map)`.
      4. Replace inline `MatrixScorecardRowDTO` construction (lines 620-713) with `row_dto = build_matrix_scorecard_row(block_id=b_id, axis_name=axis_name, axis_description=axis_description, pb_meta=pb_meta, matrix_payload=matrix_payload, scale_proj=scale_proj, axis_level_breakdown=axis_level_breakdown, cleaned_explanation=cleaned_explanation, atom_hydration=atom_hydration, context_target_res=context_target_res)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` and `uv run pytest backend_v2/tests/unit/services/test_blueprint.py -k "matrix"`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_parse_matrices_axis_name_collision_disambiguation">
      Verifies that multiple steps evaluating the same MatrixPromptBlock disambiguate axis names using step_id and collision_counter ("Axis (stp_2)", "Axis (stp_2 1)").
    </contract>
    <contract type="positive" name="test_parse_matrices_context_target_three_tier_resolution">
      Verifies Tier 1 single-input resolution, Tier 2 multi-input target_input_key resolution ("chat_log", "product_text", "all"), and Tier 3 ExpectedInput.label vs LocalizationService translation resolution.
    </contract>
    <contract type="negative" name="test_parse_matrices_missing_label_fails_fast">
      Verifies that a MatrixPromptBlock with empty or missing label logs ErrorCodes.CONFIGURATION_ERROR and raises AppException(HTTP 500).
    </contract>
    <contract type="negative" name="test_parse_matrices_unrecognized_evidence_type_coerces_to_none">
      Verifies that an unrecognized evidence_type string on MatrixExtensionsDTO resolves validated_evidence_type to None rather than leaking an invalid literal.
    </contract>
  </test_contracts>
</execution_protocol>
```
