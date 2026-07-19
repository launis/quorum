# EPIC 106: OutputProfile Simplification & SDUI Unification

## 1. Goal Description
Currently, the `OutputProfile` data model (and consequently, the Admin User Interface) has become a "dumping ground" for historical features. It contains a massive, confusing list of properties (`layouts`, `content_blocks`, `synthesis`, `formatting_directives`, `visible_block_extensions`, `display_scale`, etc.). This makes the UI messy, overwhelming for admins, and fractures the architecture between "row outputs" and "summaries".

**Objective**: Radically simplify the `OutputProfile` by removing redundant, legacy, and highly specific formatting fields. We will unify the generation rules using the **Polymorphic Rule Routing (PromptBlocks)** and **Server-Driven UI (SDUI)** paradigms. The Admin UI will become clean and minimalistic, while the actual power and flexibility remain intact under the hood.

## 2. Architectural Impact & Simplification Strategy

### A. What We Will REMOVE from `OutputProfile` (Deprecation)
These fields clutter the UI and violate the Single Source of Truth, as they attempt to control things the `PromptCompiler` or SDUI should handle natively:
- `layouts` & `content_blocks`: Legacy properties trying to manually control UI layout. Replaced entirely by SDUI dynamic JSON (`HeroInsightBlock`, `DataGridBlock`, `MarkdownBlock`).
- `formatting_directives`: LLM formatting rules do not belong in the profile. They belong in the `PromptBlock` (e.g., as part of the `EXECUTION_PERSONA`).
- `synthesis`: Nested synthesis configuration objects are a symptom of the old standalone Synthesis strategy. Epic 105 unifies synthesis, making this redundant.
- `visible_block_extensions` / `visible_workflow_extensions`: Over-engineered. Can be collapsed into simple boolean toggles or handled implicitly by the workflow definition.

### B. What `OutputProfile` WILL KEEP (The "Clean UI")
The UI will only present high-level, human-understandable settings:
1. **Identity**: `name`, `description` (What is this profile?).
2. **Localization & Tone**: `language`, `tone_instruction` (How should it sound?).
3. **Presentation Toggles**: `visible_metadata` (e.g., checkboxes for "Show Date", "Show Organization") and `include_diagnostic_scorecard`.

### C. Unification of "Row Outputs" vs "Summaries"
Instead of defining "Row outputs" and "Summaries" as complex configurations inside the `OutputProfile`, they will be defined purely as **Steps in the DAG workflow**, utilizing specific **PromptBlocks**:
- If an admin wants a "Summary", they add a step mapped to a `PromptBlock` of type `SUMMARY`. The `PromptCompiler` reads this and tells the LLM to output a `MarkdownBlock`.
- If an admin wants a "Row Output", they add a step mapped to a `PromptBlock` of type `ROW_DATA`. The `PromptCompiler` reads this and tells the LLM to output a `DataGridBlock`.
- **Result**: The UI for `OutputProfile` doesn't need to know *what* is being printed. It only defines the *style* (tone/language). The DAG Workflow defines *what* is printed.

## 3. Implementation Phases

### Phase 1: Data Model Pruning (`models/v2_core.py`)
- Remove the deprecated fields (`layouts`, `content_blocks`, `synthesis`, `formatting_directives`, etc.) from the `OutputProfile` Pydantic model.
- Run migrations (or update `seed_data.json`) to strip these keys from existing database documents to prevent Pydantic validation errors.

### Phase 2: PromptCompiler Updates
- Ensure `PromptCompiler` relies strictly on the `criteria_block_ids` (PromptBlocks) to determine whether the LLM should generate SDUI `DataGridBlocks` (for row outputs) or `MarkdownBlocks` (for summaries).
- Ensure the `OutputProfile`'s `tone_instruction` is correctly injected into the final system prompt.

### Phase 3: Flutter Admin UI Cleanup & Freezed Synchronization (Client App V2)
- **Model Synchronization (CRITICAL)**: Because Flutter uses strict JSON parsing (`disallow_unrecognized_keys`), removing fields from the backend Pydantic model WILL crash the Flutter app if the Dart model is not updated simultaneously. You MUST update the `OutputProfile` Freezed class in `client_app_v2` to remove the deprecated fields, then run `dart run build_runner build -d`.
- **UI Update**: Update the Flutter Admin Dashboard to reflect the pruned model. Replace the cluttered configuration screens with a clean, single-column settings card containing only the essential fields (Identity, Tone, Metadata Checkboxes).

## 4. Required User Review
- **Data Migration**: Deleting legacy fields like `layouts` from `seed_data.json` is a destructive action (though safe if they are obsolete). Do we need to preserve any historical layouts, or can we confidently wipe them and rely entirely on the new dynamic SDUI generation?
