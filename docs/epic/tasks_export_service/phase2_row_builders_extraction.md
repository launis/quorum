# Phase 2 Implementation Plan: Tabular Row & Dataset Builders Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract tabular summary row and granular atom dataset builders from monolithic `@[backend_v2/services/export_service.py#L62-L1123]` into dedicated sub-modules `[NEW] @[backend_v2/services/export/summary_builder.py]` and `[NEW] @[backend_v2/services/export/atom_row_builder.py]` under Epoch 1 (Pure Structural Lift-and-Shift) with zero behavioral changes, enforcing single-pipeline streaming for Excel Tab 2 and CSV flat rows.

## Scope & Target Boundaries
- `[NEW] @[backend_v2/services/export/summary_builder.py]` (Extract `_build_summary_dtos`)
- `[NEW] @[backend_v2/services/export/atom_row_builder.py]` (Extract `_build_atom_rows` and `_build_denormalized_rows`)
- `[MODIFY] @[backend_v2/services/export_service.py#L368-L446]` (Delegate `_build_summary_dtos` to `summary_builder`)
- `[MODIFY] @[backend_v2/services/export_service.py#L448-L618]` (Delegate `_build_atom_rows` to `atom_row_builder`)
- `[MODIFY] @[backend_v2/services/export_service.py#L620-L834]` (Delegate `_build_denormalized_rows` to `atom_row_builder`)

```xml
<execution_protocol>
  <step id="1" name="CREATE_SUMMARY_BUILDER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/summary_builder.py]` containing `build_summary_dtos` lifted verbatim from `@[backend_v2/services/export_service.py#L368-L446]`.</action>
    <action>Import `resolve_context_target` from `backend_v2.services.export.metadata_resolver`.</action>
    <action>Construct `ExportMatrixSummaryRowDTO` instances streaming the 13 canonical matrix summary columns for Excel Tab 1.</action>
    <constraint invariant="zero_naked_dicts">All row outputs MUST be strictly typed immutable Pydantic V2 DTOs (`ExportMatrixSummaryRowDTO`) with `extra='forbid'`.</constraint>
  </step>

  <step id="2" name="CREATE_ATOM_ROW_BUILDER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/atom_row_builder.py]` containing `build_atom_rows` and `build_denormalized_rows` lifted verbatim from `export_service.py`.</action>
    <action>Import metadata resolution functions from `backend_v2.services.export.metadata_resolver` and text formatting utilities from `backend_v2.services.export_evidence_formatter`.</action>
    <action>Preserve single-pipeline dynamic causal proposition streaming projecting unmapped `CausalNodeDTO` instances directly into `ExportForensicAtomDTO` and `ExportDenormalizedFlatRowDTO` under `matrix_label = "Kausaalipäättely"`.</action>
    <constraint invariant="shared_builder_reuse">The rectangular atom dataset builder logic MUST maintain 1:1 parity between Excel Tab 2 and CSV flat rows without divergent branching.</constraint>
  </step>

  <step id="3" name="PROXY_DELEGATION_IN_EXPORT_SERVICE">
    <action>In `@[backend_v2/services/export_service.py#L62-L1123]`, replace method bodies of `_build_summary_dtos`, `_build_atom_rows`, and `_build_denormalized_rows` with 1-line delegations to `summary_builder` and `atom_row_builder`.</action>
    <action>Maintain identical method signatures on `ExportService` to guarantee existing unit tests remain 100% green.</action>
    <constraint invariant="strangler_fig_proxy">DO NOT delete `export_service.py` or modify caller contracts during Phase 2.</constraint>
  </step>

  <step id="4" name="VERIFY_QUALITY_GATES">
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test`.</action>
    <action>Verify all 39 unit tests pass and all 10 audit stages remain 100% green.</action>
  </step>
</execution_protocol>
```

<test_contracts>
  <regression>
    - `test_build_summary_dtos_existing_parity`: Verify 13-column summary DTO generation matches original scorecard metrics.
    - `test_build_atom_rows_existing_parity`: Verify atom row generation with forensic quotes, AI reasoning, and causal metadata.
    - `test_build_denormalized_rows_existing_parity`: Verify 22-column flat row generation combining parent matrix metrics and atom evaluations.
    - `test_causal_propositions_single_pipeline_streaming`: Verify unmapped causal propositions stream under localized causal reasoning label.
  </regression>
  <positive>
    - `test_summary_builder_direct_import`: Verify direct invocation of `build_summary_dtos` from `backend_v2.services.export.summary_builder`.
    - `test_atom_row_builder_direct_import`: Verify direct invocation of `build_atom_rows` and `build_denormalized_rows` from `backend_v2.services.export.atom_row_builder`.
  </positive>
  <negative>
    - `test_build_atom_rows_missing_matrix_raises_not_found`: Verify `build_atom_rows` raises `AppException` (404) when atom matrix definition cannot be resolved.
    - `test_build_denormalized_rows_missing_matrix_raises_not_found`: Verify `build_denormalized_rows` raises `AppException` (404) when atom matrix definition cannot be resolved.
  </negative>
</test_contracts>
