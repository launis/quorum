# Phase 1: Database Seed Restoration Plan

**Objective:** Restore the database seed data for holistic audit profile and matrix extensions, removing emoji prefixes and syncing the test fixtures.
**Target Files:**
- `@[c:\src\quorum\backend_v2\seed\seed_data.json#L7800-L11000]`
- `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json]`
- `@[c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json]`

```xml
<execution_protocol>
  <step id="1" name="Restore Holistic Audit Profile Synthesis Prompt">
    <action>Target @[c:\src\quorum\backend_v2\seed\seed_data.json#L7800-L11000]. Locate the first `text_only` layout named `"YHTEENVETO"` in the `holistic_audit` profile (around lines 9470-9550).</action>
    <action>Restore its `synthesis.system_prompt` and `synthesis.preamble_text` by pulling the exact original strings from commit `22b16208` using `git show 22b16208:backend_v2/seed/seed_data.json` to prevent hallucination.</action>
    <constraint invariant="database_schema_hallucination">Do not dynamically hallucinate the prompt.</constraint>
  </step>

  <step id="2" name="Set Row Explanations Block ID">
    <action>For matrix layouts (`2d_compare`, `3d_matrix`) with synthesis in `@[c:\src\quorum\backend_v2\seed\seed_data.json#L7800-L11000]`, explicitly set `"row_explanations_block_id": "sp_row_explanations"`.</action>
    <action>Ensure the `3d_matrix` layout block explicitly contains the array `"matrix_visible_columns": ["label", "distribution", "row_explanation", "normalized_score", "score"]`.</action>
  </step>

  <step id="3" name="Remove Emojis from Extension Labels">
    <action>Locate all 12 instances of the `extension_labels` block used across various matrices between lines 7900 and 11000 in `@[c:\src\quorum\backend_v2\seed\seed_data.json#L7800-L11000]`.</action>
    <action>Programmatically remove all Unicode emojis and the immediately following space character from the `extension_labels` strings across all 12 locations.</action>
    <demolish>REMOVE: Any hardcoded emojis in the label strings. REPLACE WITH: Pure text strings.</demolish>
  </step>

  <step id="4" name="Sync Test Fixtures">
    <action>Use `grep_search` to check if `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json]` or `@[c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json]` assert on emoji-prefixed `extension_labels` strings.</action>
    <action>Update them atomically to match the stripped labels.</action>
  </step>

  <step id="5" name="Testing &amp; Quality Gate Plan">
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/seed/seed_data.json`</action>
    <constraint invariant="quality_gate_delegation">Execute the universal quality gate.</constraint>
    <action>Verify changes via `git diff` and perform an atomic `git commit`.</action>
  </step>
</execution_protocol>
```
