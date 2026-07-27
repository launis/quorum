# Phase 1 & 4: Backend Model Strictness Hardening & Test Fixture Migration

This plan replaces unstructured list[dict[str, Any]] fields with strict `list[AnySduiBlock]` discriminated unions in the backend core models and DTOs, and simultaneously updates test fixtures and seed data to prevent CI/CD failures.

**Target Files**:
- `@[c:\src\quorum\backend_v2\models\v2_core.py]` [MODIFY]
- `@[c:\src\quorum\backend_v2\models\dtos\output_profile.py]` [MODIFY]
- `@[c:\src\quorum\backend_v2\seed\seed_data.json]` [MODIFY]
- `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]` [MODIFY]

```xml
<execution_protocol level="2_execute">
  <constraint invariant="strict_pydantic_v2_rust">Force the Fail-Fast pipeline by using strict models instead of dictionaries.</constraint>
  <constraint invariant="the_no_legacy_mandate">Legacy support is strictly prohibited. Do not use fallbacks for old execution traces.</constraint>
  <step id="1" name="Update V2 Core Models">
    <action>Modify `@[c:\src\quorum\backend_v2\models\v2_core.py]`.</action>
    <action>Import `AnySduiBlock` from `backend_v2.models.view.sdui`.</action>
    <demolish>REMOVE: `content_blocks: list[dict[str, Any]]` from `OutputProfile`, `EmbeddedOutputProfile`, `RenderedSynthesisCache`.</demolish>
    <action>Replace with `content_blocks: list[AnySduiBlock] = Field(default_factory=list)`.</action>
    <demolish>REMOVE: `synthesis_blocks: list[dict[str, Any]] | None` from `OutputLayoutBlock`, `ReportLayoutDTO`.</demolish>
    <action>Replace with `synthesis_blocks: list[AnySduiBlock] | None = Field(default=None)`.</action>
    <demolish>REMOVE: `section_syntheses: dict[str, list[dict[str, Any]]]` from `RenderedSynthesisCache`.</demolish>
    <action>Replace with `section_syntheses: dict[str, list[AnySduiBlock]]`.</action>
  </step>
  <step id="2" name="Update Output Profile DTOs">
    <action>Modify `@[c:\src\quorum\backend_v2\models\dtos\output_profile.py]`.</action>
    <demolish>REMOVE: `content_blocks: list[dict[str, Any]]`.</demolish>
    <action>Replace with `content_blocks: list[AnySduiBlock]` in `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.</action>
  </step>
  <step id="3" name="Test Fixture Migration">
    <action>Use grep_search to find all tests using `content_blocks` or `synthesis_blocks` (e.g., in `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]`).</action>
    <action>Rewrite mock dictionaries to either instantiate `AnySduiBlock` models directly or ensure the JSON mocks contain valid `block_type` discriminator fields.</action>
  </step>
  <step id="4" name="Seed Data Verification">
    <action>Modify `@[c:\src\quorum\backend_v2\seed\seed_data.json]`.</action>
    <action>Verify all `output_profiles` have `content_blocks` arrays that conform to the `AnySduiBlock` schema (empty arrays `[]` are fine).</action>
  </step>
</execution_protocol>
```
## Testing & Quality Gate Plan
- Run backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- Re-seed database: `uv run python backend_v2/seed/run_seed.py local`
