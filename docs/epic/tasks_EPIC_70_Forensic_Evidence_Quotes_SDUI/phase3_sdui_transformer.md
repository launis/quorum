# Phase 3: SDUI Transformer Update (EPIC 70)

## Objective
Update the `BlueprintTransformer` service to process the `"quotes"` visibility option. It will extract hoisted quotes from `content_payload` and map them to the `quotes_list` field in `MatrixScorecardRowDTO`, while applying truncation logic.

## Execution Steps

### 1. Update `BlueprintTransformer` Logic
**Target:** `c:\src\quorum\backend_v2\services\blueprint.py`
- Locate the matrix hydration logic where `MatrixScorecardRowDTO` is built.
- Check if `"quotes"` is in `matrix_visible_columns`.
- If `"quotes"` is active:
  - Fetch the `atom_quotes` array from `execution_record.context_variables.get("content_payload", {})` specific to the current matrix `block_id`.
  - Iterate through the quotes, truncate each string to 150 characters, appending `...` if truncated.
  - Set the resulting array to the newly added `quotes_list` field.
  - Clear the `row_explanation` field (set to empty string) because the Epic specifies that if quotes are requested, they replace the explanation to save space.
- If `"quotes"` is not active, behave as before (preserve `row_explanation` if `"row_explanation"` is in the list).

### 2. Verification
- Verify that API calls fetching the `ReportDataDTO` correctly include the truncated `quotes_list` when the profile has `quotes` in its `matrix_visible_columns`.
- Check backend logs for any unhandled exceptions during blueprint rendering.

## Architectural Invariants
- **Rule 23: zero_service_layer_fallbacks:** No `.get(key, default)` dictionary access is allowed in service or controller layers. Rely entirely on strictly validated Pydantic properties.
- **Rule 30: tripartite_rendering_boundary:** The Backend MUST NOT hardcode or generate pre-rendered Markdown tables. The Backend produces purely raw DTO data; textual rendering is localized via L10n Enum reference keys. The Flutter frontend retains sole responsibility for Zero-Math rendering.
- **Rule 49: synthesis_pure_functions:** Data synthesis functions MUST adhere to the "Pure Functions" paradigm. Utilize O(1) dictionary lookups to eliminate expensive nested loops.
- **Rule 50: execution_synthesis_tier_decoupling:** Strictly decouple the execution phase (LLM inference, database modifications) from the reporting phase (data synthesis and formatting). Honor the boundary: Formatting logic must reside entirely in `blueprint.py`, not in the Flutter UI or the `scoring.py` hook.
