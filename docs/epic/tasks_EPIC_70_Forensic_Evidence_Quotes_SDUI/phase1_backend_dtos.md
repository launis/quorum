# Phase 1: Backend DTOs & Schema Updates (EPIC 70)

## Objective
Update the core Pydantic backend definitions to support the "quotes" visible column requirement, as defined in EPIC 70. This creates the foundational schema changes for downstream SDUI logic and Flutter UI.

## Execution Steps

### 1. Update `matrix_visible_columns` Defaults
**Target:** `c:\src\quorum\backend_v2\models\v2_core.py`
- In `SynthesisConfigDTO` (around line 826): Update `matrix_visible_columns` field description to include the `"quotes"` option. Note that it's a `list[str]`, so no strict Literal constraint needs updating, but the documentation/default should be clarified if necessary.
- In `ReportDataDTO` (around line 875): Same as above. Ensure the schema allows `quotes` as a valid string in the list.

### 2. Extend `MatrixScorecardRowDTO`
**Target:** `c:\src\quorum\backend_v2\models\v2_core.py`
- Add a new field `quotes_list: list[str] | None = Field(default=None, description="Array of exact quotes hoisted from successful atoms. Truncated to 150 chars each.")` to `MatrixScorecardRowDTO` (around line 805).
- Ensure strict adherence to the **Fail-Fast** architecture by defaulting to `None` but typing it explicitly. 

### 3. Verification
- Verify that `uv run pytest` passes on model definitions.
- Inspect `backend_v2\seed\seed_data.json` if any mock data needs updating to pass strict Pydantic model checks. If not, proceed.

## Architectural Invariants
- **Rule 1: the_zero_compromise_pledge:** No `.get("default")` fallbacks permitted in business logic. Strict Pydantic validation is absolutely mandatory.
- **Rule 7: zero_defaults_mandate:** DTO models MUST NOT use default values if the missing data is critical. Standard functions and methods are STRICTLY PROHIBITED from using mutable types (e.g., list, dict) as default arguments (B006). Always use `None` and initialize the mutable object inside the function block (or use `default_factory=list`).
- **Rule 78: zero_field_renaming_mandate:** NEVER autonomously rename existing Pydantic model fields (e.g., `row_explanation`). Renaming fields breaks database schema mappings and causes Fail-Fast validation errors downstream.
- Do NOT delete existing fields (e.g., `row_explanation`), this is purely additive at the DTO level.
