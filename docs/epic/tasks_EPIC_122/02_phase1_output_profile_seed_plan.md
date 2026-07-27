# Phase 1: OutputProfile Configuration in seed_data.json

## Targets
- `@[c:\src\quorum\backend_v2\seed\seed_data.json]`

```xml
<execution_protocol>
  <constraint invariant="universal_fail_fast">Ensure the modified JSON strictly matches the OutputProfile Pydantic schema.</constraint>

  <step id="2_1" name="Update Target OutputProfile in Seed Data">
    <action>Write a Python script in `scratch/` to determine the precise StartLine and EndLine of the OutputProfile with id `prf_5d6e7f8091a2b3c4` in `seed_data.json`.</action>
    <action>Using the discovered line bounds, execute `multi_replace_file_content` to surgically modify the profile without exceeding the context window limits.</action>
    <action>Locate the primary OutputProfile (e.g., 'holistic_audit', id: `prf_5d6e7f8091a2b3c4`) in `seed_data.json`.</action>
    <action>Update `visible_metadata` array to include: `"date", "execution_id", "organization", "user", "scoring_engine", "strictness"`.</action>
    <action>Ensure `custom_preface` is set with `default_locale` and `translations` for the static blocks injection (e.g., english and finnish).</action>
    <action>Add `user_role_label` (e.g., User Role / Käyttäjärooli).</action>
    <action>Update `visible_block_extensions` to include `"justification", "coaching", "falsification", "remediation_steps"`.</action>
  </step>

  <step id="2_2" name="Configure layouts Array">
    <action>Configure the `layouts` array for the target OutputProfile to include the exact sequence specified in Phase 1 of EPIC 122.</action>
    <action>Ensure the `3d_matrix` preset block correctly defines `matrix_visible_columns` as `["label", "distribution", "row_explanation", "normalized_score", "score"]`, along with `extension_labels` and `matrix_column_labels`.</action>
    <action>Add the new `1d_metrics` blocks for GLOBAL SCORE and JARGON RATIO with their respective `target_blocks`.</action>
    <action>Add `text_only` blocks for PENALTIES &amp; AUDIT TRAIL, and SOURCES, mapping their `target_blocks` appropriately.</action>
  </step>

  <step id="2_3" name="Testing &amp; Quality Gate Plan">
    <action>Run the seed dry-run command: `uv run python backend_v2/seed/run_seed.py local --dry-run` to validate JSON integrity.</action>
  </step>
</execution_protocol>
```
