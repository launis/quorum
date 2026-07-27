# Phase 0: Backend Domain Model Refactoring (Separation of Concerns)

## Targets
- `@[c:\src\quorum\backend_v2\models\v2_core.py]`
- `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- `@[c:\src\quorum\backend_v2\models\dtos\output_profile.py]`
- `@[c:\src\quorum\backend_v2\models\domain\output_profile.py]`

```xml
<execution_protocol>
  <constraint invariant="anti_semantic_drift_renaming">Do not rename existing fields without approval.</constraint>
  <constraint invariant="universal_fail_fast">Enforce Fail-Fast on missing data.</constraint>
  <constraint invariant="sdui_contract_fracture_prevention">Ensure DTOs are correctly typed and updated.</constraint>

  <step id="0_1" name="Refactor SynthesisConfigDTO and OutputLayoutBlock">
    <action>Remove `matrix_visible_columns` from `SynthesisConfigDTO` in `v2_core.py`.</action>
    <action>Add `matrix_visible_columns: list[str] = Field(default_factory=list)` to `OutputLayoutBlock` in `v2_core.py`.</action>
    <action>Add `matrix_visible_columns: list[str] = Field(default_factory=list)` to `ReportLayoutDTO` in `v2_core.py`.</action>
    <action>HARD DEPRECATION: Completely REMOVE `matrix_visible_columns` from `ReportDataDTO` in `v2_core.py`.</action>
    <action>Update `backend_v2/models/dtos/output_profile.py` if `OutputLayoutBlock` changes affect it.</action>
    <demolish>REMOVE: `matrix_visible_columns` field from SynthesisConfigDTO and ReportDataDTO. REPLACE WITH: Addition to OutputLayoutBlock and ReportLayoutDTO.</demolish>
  </step>

  <step id="0_2" name="GlobalSynthesisDTO User Role Support">
    <action>Add `user_role: str | None = None` and `user_role_justification: str | None = None` to `GlobalSynthesisDTO` in `v2_core.py`.</action>
    <action>Add `user_role_label: I18nText | None = None` to `OutputProfile` in `v2_core.py`.</action>
  </step>

  <step id="0_3" name="Update Blueprint Service">
    <action>In `backend_v2/services/blueprint.py`, read `matrix_visible_columns` exclusively from the `3d_matrix` layout block and propagate it to `ReportLayoutDTO`.</action>
    <action>Replace `getattr(lay, "synthesis", None)` with direct access `lay.synthesis`.</action>
    <action>Implement Fail-Fast for user role extraction: If `OutputProfile` has `user_role_label` but `global_synthesis.user_role` is None, raise `AppException`.</action>
    <demolish>REMOVE: `syn_profile = None` logic and `matrix_visible_cols = syn.matrix_visible_columns if syn else fallback_cols`. REPLACE WITH: Extraction from active 3d_matrix layout block.</demolish>
  </step>

  <step id="0_4" name="Update Jinja Template">
    <action>In `backend_v2/templates/report_template.jinja2`, dynamically find the layout where `preset_view == '3d_matrix'` and extract `layout.matrix_visible_columns`.</action>
    <action>Delete the hardcoded fallback `['label', 'score', 'distribution', 'row_explanation']`.</action>
    <demolish>REMOVE: `if report_data.matrix_visible_columns else [default_list]` logic. REPLACE WITH: Direct layout access and failure if empty.</demolish>
  </step>

  <step id="0_5" name="Testing &amp; Quality Gate Plan">
    <action>Run backend audit loop on all modified files: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`.</action>
  </step>
</execution_protocol>
```
