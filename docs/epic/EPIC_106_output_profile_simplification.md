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
- `visible_block_extensions` / `visible_workflow_extensions`: Over-engineered. Can be collapsed into simple boolean toggles or handled EXPLICITLY by the workflow definition. Any form of implicit fallback behavior is strictly forbidden.

### B. What `OutputProfile` WILL KEEP (The "Clean UI")
The UI will only present high-level, human-understandable settings:
1. **Identity**: `name`, `description` (What is this profile?).
2. **Localization & Tone**: `language`, `tone_instruction` (How should it sound?).
3. **Presentation Toggles**: `visible_metadata` (e.g., checkboxes for "Show Date", "Show Organization") and `include_diagnostic_scorecard`.

### C. Unification of "Row Outputs" vs "Summaries" (Deterministic Schema Binding)
Instead of defining "Row outputs" and "Summaries" as complex configurations inside the `OutputProfile`, they will be defined purely as **Steps in the DAG workflow**, utilizing specific **PromptBlocks**.

**CRITICAL SHIFT-TO-CODE LAW**: We cannot rely on "Implicit Magic" where the `PromptCompiler` merely tells the LLM via text to output a specific format. The LLM's returned data structure MUST be deterministically forced by a Pydantic schema via the `SchemaFactory`. The expected structure must be explicitly declared in the DAG definition.

- **Explicit Schema Declaration in DAG**: The `StepRule` class includes a new field `expected_sdui_type` (e.g. `Literal["markdown", "grid", "hero"]`) which explicitly dictates the required SDUI schema.
- If an admin wants a "Summary", they add a step mapped to a `PromptBlock` of type `SUMMARY` and set `expected_sdui_type="markdown"`. The `SchemaFactory` enforces the `MarkdownBlock` schema for Pydantic validation.
- If an admin wants a "Row Output", they add a step mapped to a `PromptBlock` of type `ROW_DATA` and set `expected_sdui_type="grid"`. The `SchemaFactory` enforces the `DataGridBlock` schema.
- **Result**: The UI for `OutputProfile` doesn't need to know *what* is being printed. It only defines the *style* (tone/language). The DAG Workflow deterministically defines *what* is printed and guarantees the correct Pydantic schema validation.

## 3. Implementation Phases

### Phase 1: Data Model Pruning (`backend_v2/models/domain/output_profile.py` & `backend_v2/models/dtos/output_profile.py`)
- Remove the deprecated fields (`layouts`, `content_blocks`, `synthesis`, `formatting_directives`, etc.) from the `OutputProfile` Domain Model and its corresponding DTOs.
- *Architectural Rule*: Quorum strictly separates database state models (Domain) and API transport models (DTO). Both layers must be pruned simultaneously to prevent boundary parsing failures.
- **Production Migration Script (Validation Crash Risk)**: Because Pydantic V2 strictly enforces schemas, merely updating `seed_data.json` is not enough for production environments. You MUST write a concrete, isolated Python migration script (e.g., `scripts/migrate_epic_106_profiles.py`). This script MUST perform two operations: (1) Physically delete the deprecated keys from all existing `OutputProfile` documents, and (2) Inject the new mandatory `expected_sdui_type` field into all existing `StepRule` definitions inside workflows to prevent "Data Starvation" crashes on backend boot.
- **SSOT Seed Data Update (Data Starvation Prevention)**: You MUST carefully modify `backend_v2/seed/seed_data.json` to strip the legacy `OutputProfile` keys AND explicitly inject the `expected_sdui_type` field into all existing steps in the workflows list. This must strictly follow the *Vault Mutation Protocol*.
- *Append-Only Law*: Executions (results) MUST NOT and do not need to be migrated. **Historical execution data has zero structural value and is considered entirely disposable during migrations.** Historical payload data is append-only and mutation is strictly prohibited.

### Phase 2: PromptCompiler Updates
- **Eradicate Split Brain (SSOT Enforcement)**: Ensure `PromptCompiler` relies strictly on `StepRule.expected_sdui_type` to inject the correct textual formatting instructions into the prompt. It MUST NOT try to guess or infer structural expectations from `PromptBlocks`. `PromptBlocks` are strictly reserved for cognitive instructions (e.g., tone, persona, constraints), while `expected_sdui_type` is the absolute Single Source of Truth for both the `SchemaFactory` (Pydantic validation) and the `PromptCompiler` (LLM instructions).
- Ensure the `OutputProfile`'s `tone_instruction` is correctly injected into the final system prompt.

### Phase 3: Flutter Admin UI Cleanup & Freezed Synchronization (Client App V2)
- **Model Synchronization (CRITICAL)**: Because Flutter uses strict JSON parsing (`disallow_unrecognized_keys`), removing fields from the backend Pydantic model WILL crash the Flutter app if the Dart model is not updated simultaneously. You MUST update the `OutputProfile` Freezed class in `client_app_v2` to remove the deprecated fields, then run `dart run build_runner build -d`.
- **API Payload Scrubbing (422 Risk)**: You MUST clean up the frontend Repository classes. If the UI repositories continue to send the old or `null` legacy keys (like `layouts`) in PUT/POST requests, the updated FastAPI router will instantly reject them with a `422 Unprocessable Entity` error. All outgoing API payloads must be scrubbed of deprecated fields.
- **UI Update**: Update the Flutter Admin Dashboard to reflect the pruned model. Replace the cluttered configuration screens with a clean, single-column settings card containing only the essential fields (Identity, Tone, Metadata Checkboxes).

## 4. Required User Review
- **Data Migration**: Deleting legacy fields like `layouts` from `seed_data.json` is a destructive action (though safe if they are obsolete). Do we need to preserve any historical layouts, or can we confidently wipe them and rely entirely on the new dynamic SDUI generation?
