# Phase 2: Python Backend Schema & Enum Migration Plan

**Objective:** Migrate Python Pydantic schemas, Enums, and Trace payloads to support pure SDUI, deleting legacy flat string fields and GlobalSynthesisDTO.
**Target Files:**
- `@[c:\src\quorum\backend_v2\models\v2_core.py]`
- `@[c:\src\quorum\backend_v2\models\view\sdui.py]`
- `@[c:\src\quorum\backend_v2\models\enums.py]`
- `@[c:\src\quorum\backend_v2\models\dtos\trace.py]`
- `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json]`
- `@[c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\test_enum_parity.py]`

```xml
<execution_protocol>
  <step id="1" name="Update Enums and Literals">
    <action>In `@[c:\src\quorum\backend_v2\models\enums.py]`, add `ERROR = "error"` to `VisualIntent`.</action>
    <action>In `@[c:\src\quorum\backend_v2\models\view\sdui.py]`, expand `AlertBlock.severity` Literal to `Literal["info", "warning", "critical_override", "success", "error"]`.</action>
    <action>In `@[c:\src\quorum\backend_v2\models\enums.py]`, create a new `UiVariant(StrEnum)` enum with values `DEFAULT = "default"`, `SUCCESS = "success"`, `WARNING = "warning"`, `ERROR = "error"`, `NEUTRAL = "neutral"`, and create alias `LaxUiVariant = Annotated[UiVariant, Field(strict=False)]`.</action>
    <constraint invariant="cross_language_enum_parity">Enums mapped for UI must maintain strict parity.</constraint>
  </step>

  <step id="2" name="Migrate TraceMatrixPayloadDTO and TraceMatrixExtensionsDTO">
    <action>In `@[c:\src\quorum\backend_v2\models\dtos\trace.py]`, create `TraceMatrixExtensionsDTO(BaseDTO)` with `model_config = ConfigDict(strict=True, frozen=True, extra="forbid")`.</action>
    <action>Add fields to `TraceMatrixExtensionsDTO`. You MUST type every field exactly as `Annotated[type | None, Field(default=None)]`. Types are: `coaching` (str), `falsification` (str), `remediation_steps` (str), `missing_context` (str), `emotional_sentiment` (str), `theory_link` (str), `risk_flag` (bool), `confidence` (float), `evidence_type` (str), `source_id` (str), `citation` (str), `google_citation` (str), `contextual_override` (bool), and `semantic_reasoning` (str).</action>
    <action>In `TraceMatrixPayloadDTO`, update `extensions` to `Annotated[TraceMatrixExtensionsDTO | None, Field(default=None, description="Additional extensions")]`.</action>
    <demolish>REMOVE: The loose `dict[str, Any]` type for `extensions`. REPLACE WITH: Strict `TraceMatrixExtensionsDTO`.</demolish>
    <constraint invariant="strict_pydantic_v2_rust">Enforce strict Pydantic V2 schemas with extra="forbid".</constraint>
  </step>

  <step id="3" name="Migrate MatrixScorecardRowDTO and Delete Legacy Fields">
    <action>In `@[c:\src\quorum\backend_v2\models\v2_core.py]`, update `MatrixScorecardRowDTO` to include `inner_sdui_blocks: list[AnySduiBlock] = Field(default_factory=list)`.</action>
    <action>Delete legacy STRING XAI fields from `MatrixScorecardRowDTO`: `coaching`, `falsification`, `missing_context`, `risk_flag`, `remediation_steps`, `emotional_sentiment`, `theory_link`.</action>
    <action>Retain `confidence: float | None` as-is.</action>
    <demolish>REMOVE: `coaching`, `falsification`, `missing_context`, `risk_flag`, `remediation_steps`, `emotional_sentiment`, `theory_link` fields.</demolish>
  </step>

  <step id="4" name="Delete GlobalSynthesisDTO and Migrate Views">
    <action>In `@[c:\src\quorum\backend_v2\models\v2_core.py]`, delete `GlobalSynthesisDTO` entirely.</action>
    <action>Delete the `global_synthesis` field from `ReportDataDTO`.</action>
    <action>Refactor `ReportView.status_theme` to `Annotated[VisualIntent, Field(default=VisualIntent.SUCCESS)]`.</action>
    <action>Refactor `AssessmentView.uiVariant` to `Annotated[LaxUiVariant, Field(...)]`.</action>
    <demolish>REMOVE: `GlobalSynthesisDTO` class and `global_synthesis` field.</demolish>
  </step>

  <step id="5" name="Fix SDUI List[Any] Leaks">
    <action>In `@[c:\src\quorum\backend_v2\models\view\sdui.py]`, update `SduiGridBlock.items` to `Annotated[list[str], Field(default_factory=list)]`.</action>
    <action>Update `SduiQuoteCard.citations` to `Annotated[list[int], Field(default_factory=list)]`.</action>
    <demolish>REMOVE: `list[Any]` type hints in `SduiGridBlock` and `SduiQuoteCard`.</demolish>
  </step>

  <step id="6" name="Update Test Fixtures and Parity Checks">
    <action>In `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json]` and `@[c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json]`, programmatically remove legacy flat string fields (`coaching`, `falsification`, etc) from the JSON, and add an empty `inner_sdui_blocks: []` array to every row to match the new schema.</action>
    <action>In `@[c:\src\quorum\backend_v2\tests\unit\models\test_enums.py]`, add a new `test_parity_ui_variant()` check to assert exact parity between Python `UiVariant` and Dart `UiVariant`.</action>
  </step>

  <step id="7" name="Testing &amp; Quality Gate Plan">
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/`</action>
    <constraint invariant="quality_gate_delegation">Execute the universal quality gate.</constraint>
    <action>Verify changes via `git diff` and perform an atomic `git commit`.</action>
  </step>
</execution_protocol>
```
