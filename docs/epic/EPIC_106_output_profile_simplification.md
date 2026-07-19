# EPIC 106: OutputProfile Simplification & SDUI Unification

## 1. Goal Description
Currently, the `OutputProfile` data model (and consequently, the Admin User Interface) has become a "dumping ground" for historical features. It contains a massive, confusing list of properties (`layouts`, `content_blocks`, `synthesis`, `formatting_directives`, `visible_block_extensions`, `display_scale`, etc.). This makes the UI messy, overwhelming for admins, and fractures the architecture between "row outputs" and "summaries".

**Objective**: Radically simplify the `OutputProfile` by removing redundant, legacy, and highly specific formatting fields. We will unify the generation rules using the **Polymorphic Rule Routing (PromptBlocks)** and **Server-Driven UI (SDUI)** paradigms. The Admin UI will become clean and minimalistic, while the actual power and flexibility remain intact under the hood.

## 2. Architectural Impact & Simplification Strategy

### A. What We Will REMOVE from `OutputProfile` (Deprecation)
These fields clutter the UI and violate the Single Source of Truth, as they attempt to control things the `PromptCompiler` or SDUI should handle natively:
- `layouts`: Legacy property trying to manually control UI layout. No active backend `.layouts` access exists. **Safe to remove.**
- `content_blocks` (ON `OutputProfile` ONLY): The `content_blocks` field on the `OutputProfile` model acts as a **static configuration template**. This is distinct from `content_blocks` as rendered SDUI output data (used in `blueprint.py`, `sdui_mapper_service.py`, `execution.py`, `synthesis_distiller.py`). Only the `OutputProfile` configuration-side `content_blocks` is deprecated. The rendered SDUI `content_blocks` data flow remains intact and will be populated by the DAG engine + `SchemaFactory` instead of being statically pre-defined on the profile.
- `formatting_directives`: LLM formatting rules do not belong in the profile. They belong in the `PromptBlock` (e.g., as part of the `EXECUTION_PERSONA`). **Active usage** in `llm.py:L410` and `worker.py:L792` must be migrated to read from `PromptBlock` configuration.
- `synthesis` (`SynthesisConfigDTO`): Nested synthesis configuration objects are a symptom of the old standalone Synthesis strategy. Epic 105 unifies synthesis, making this redundant. **Active usage** in `worker.py:L770-798` must be migrated (see Phase 2.5 below). Sub-fields require explicit relocation:
  - `SynthesisConfigDTO.allowed_exports` → Relocate to `Workflow`-level configuration (export formats are a workflow concern, not a profile concern).
  - `SynthesisConfigDTO.allowed_mcp_tools` → Relocate to `StepRule`-level configuration (MCP tool availability is a per-step execution concern).
  - `SynthesisConfigDTO.length_constraint` → Relocate to `PromptBlock` configuration (this is a cognitive instruction, not a profile setting).
  - `SynthesisConfigDTO.historical_context_mode` → Relocate to `Workflow`-level configuration.
  - `SynthesisConfigDTO.matrix_visible_columns` → Relocate to `StepRule`-level (this controls SDUI rendering per step).
- `visible_block_extensions` / `visible_workflow_extensions`: Over-engineered. Can be collapsed into simple boolean toggles or handled EXPLICITLY by the workflow definition. Any form of implicit fallback behavior is strictly forbidden.
- `display_scale`: This field controls score presentation format. Relocate to `StepRule`-level configuration, as different DAG steps may require different scaling (e.g., a summary step vs. a matrix step).
- `matrix_column_labels`: SDUI rendering control. Relocate to `StepRule`-level or to the `PromptBlock` associated with the matrix step.

### B. What `OutputProfile` WILL KEEP (The "Clean UI")
The UI will only present high-level, human-understandable settings:
1. **Identity**: `name`, `description`, `custom_preface` (What is this profile?).
2. **Localization & Tone**: `language`, `tone_instruction` (How should it sound?).
3. **Presentation Toggles**: `visible_metadata` (e.g., checkboxes for "Show Date", "Show Organization") and `include_diagnostic_scorecard`.
4. **Overrides**: `strictness_level`, `scoring_strategy` (profile-level overrides that remain valid at this scope).

### C. Unification of "Row Outputs" vs "Summaries" (Deterministic Schema Binding)
Instead of defining "Row outputs" and "Summaries" as complex configurations inside the `OutputProfile`, they will be defined purely as **Steps in the DAG workflow**, utilizing specific **PromptBlocks**.

**CRITICAL SHIFT-TO-CODE LAW**: We cannot rely on "Implicit Magic" where the `PromptCompiler` merely tells the LLM via text to output a specific format. The LLM's returned data structure MUST be deterministically forced by a Pydantic schema via the `SchemaFactory`. The expected structure must be explicitly declared in the DAG definition.

- **Explicit Schema Declaration in DAG**: The `StepRule` class includes a new field `expected_sdui_type` (e.g. `Literal["markdown", "grid", "hero"]`) which explicitly dictates the required SDUI schema.
- If an admin wants a "Summary", they add a step mapped to a `PromptBlock` of type `SUMMARY` and set `expected_sdui_type="markdown"`. The `SchemaFactory` enforces the `MarkdownBlock` schema for Pydantic validation.
- If an admin wants a "Row Output", they add a step mapped to a `PromptBlock` of type `ROW_DATA` and set `expected_sdui_type="grid"`. The `SchemaFactory` enforces the `DataGridBlock` schema.
- **Result**: The UI for `OutputProfile` doesn't need to know *what* is being printed. It only defines the *style* (tone/language). The DAG Workflow deterministically defines *what* is printed and guarantees the correct Pydantic schema validation.

## 3. Implementation Phases

### Phase 0: Workflow Configuration Prerequisite
- **Target File**: `backend_v2/models/v2_core.py` (specifically `Workflow` class)
- **Action**: Add `allowed_exports: list[str] = Field(default_factory=list)` to the `Workflow` model.
- **Why**: Epic 106 relocates `allowed_exports` from `SynthesisConfigDTO` to the `Workflow` level. This target field MUST exist before Phase 2.5 attempts to migrate `worker.py` to use it.

### Phase 1: Data Model Pruning (`backend_v2/models/domain/output_profile.py` & `backend_v2/models/dtos/output_profile.py`)
- Remove the deprecated fields (`layouts`, `content_blocks`, `synthesis`, `formatting_directives`, etc.) from the `OutputProfile` Domain Model and its corresponding DTOs.
- *Architectural Rule*: Quorum strictly separates database state models (Domain) and API transport models (DTO). Both layers must be pruned simultaneously to prevent boundary parsing failures.
- **Production Migration Script (Validation Crash Risk)**: Because Pydantic V2 strictly enforces schemas, merely updating `seed_data.json` is not enough for production environments. You MUST write a concrete, isolated Python migration script (e.g., `scripts/migrate_epic_106_profiles.py`). This script MUST perform two operations: (1) Physically delete the deprecated keys from all existing `OutputProfile` documents, and (2) Inject the new mandatory `expected_sdui_type` field into all existing `StepRule` definitions inside workflows to prevent "Data Starvation" crashes on backend boot.
- **SSOT Seed Data Update (Data Starvation Prevention)**: You MUST carefully modify `backend_v2/seed/seed_data.json` to strip the legacy `OutputProfile` keys AND explicitly inject the `expected_sdui_type` field into all existing steps in the workflows list. This must strictly follow the *Vault Mutation Protocol*.
- *Append-Only Law*: Executions (results) MUST NOT and do not need to be migrated. **Historical execution data has zero structural value and is considered entirely disposable during migrations.** Historical payload data is append-only and mutation is strictly prohibited.

### Phase 2: PromptCompiler Updates
- **`prompt_compiler_immutability` Exception (USER APPROVED)**: This phase modifies `prompt_compiler.py`, which is protected by the `prompt_compiler_immutability` architecture rule. The user has explicitly granted permission to modify this file as part of Epic 106.
- **Eradicate Split Brain (SSOT Enforcement)**: Ensure `PromptCompiler` relies strictly on `StepRule.expected_sdui_type` to inject the correct textual formatting instructions into the prompt. It MUST NOT try to guess or infer structural expectations from `PromptBlocks`. `PromptBlocks` are strictly reserved for cognitive instructions (e.g., tone, persona, constraints), while `expected_sdui_type` is the absolute Single Source of Truth for both the `SchemaFactory` (Pydantic validation) and the `PromptCompiler` (LLM instructions).
- **Remove `formatting_directives` Dependency in `llm.py`**: The current `LLMNodeStrategy` reads `output_profile.formatting_directives` at line 410-412 of `llm.py` and injects them into the system prompt. This logic must be removed. Formatting directives are now sourced from the `PromptBlock` (e.g., `EXECUTION_PERSONA` category) by the `PromptCompiler`.
- Ensure the `OutputProfile`'s `tone_instruction` is correctly injected into the final system prompt.

### Phase 2.5: Worker Rendering Pipeline Migration & Atomic `formatting_directives` Removal
- **Root Cause**: `worker.py` lines 770-798 directly read `SynthesisConfigDTO` fields (`system_prompt`, `length_constraint`, `tone_instruction`) and `OutputProfile.formatting_directives` to construct synthesis prompts. `llm.py` lines 410-412 also read `OutputProfile.formatting_directives`.
- **Migration Strategy**: The worker's rendering pipeline must be refactored to source its synthesis instructions from the DAG-produced data:
  1. The synthesis system prompt MUST be sourced from the `PromptBlock` associated with the synthesis step (retrieved via `StepRule.task_blueprint` → `Step.criteria_block_ids`).
  2. `length_constraint` and `tone_instruction` MUST be sourced from the `PromptBlock` configuration.
  3. `formatting_directives` MUST be removed from the worker's prompt construction and `llm.py`'s prompt construction AT THE SAME TIME. The `PromptCompiler` (Phase 2) handles this via `PromptBlock` injection.
  4. `allowed_exports` MUST be read from the `Workflow`-level configuration (new field from Phase 0).
- **Atomic Commit Mandate**: You MUST remove the `formatting_directives` references from BOTH `worker.py` AND `llm.py` in the exact same atomic Git commit. Epic 105 assumes `llm.py` is cleaned up by Epic 106, so this must be perfectly synchronized to prevent `AttributeError` crashes in reasoning steps.
- **Fail-Fast Mandate**: After migration, the worker MUST NOT contain any `.get()` or `hasattr()` fallbacks for the removed fields. If a required configuration is missing from the `PromptBlock` or `Workflow`, the system MUST crash with an explicit `AppException(ErrorCodes.CONFIGURATION_ERROR)`.

### Phase 3: Flutter Admin UI Cleanup & Freezed Synchronization (Client App V2)
- **Model Synchronization (CRITICAL)**: Because Flutter uses strict JSON parsing (`disallow_unrecognized_keys`), removing fields from the backend Pydantic model WILL crash the Flutter app if the Dart model is not updated simultaneously. You MUST update the `OutputProfile` Freezed class in `client_app_v2` to remove the deprecated fields, then run `dart run build_runner build -d`.
- **Flutter Parity Gate**: Backend `output_profile.py` Pydantic deletions MUST NOT be deployed to any non-local environment until `dart run build_runner build -d` has completed successfully AND `test_enum_parity.py` passes. This is a hard deployment gate.
- **API Payload Scrubbing (422 Risk)**: You MUST clean up the frontend Repository classes. If the UI repositories continue to send the old or `null` legacy keys (like `layouts`) in PUT/POST requests, the updated FastAPI router will instantly reject them with a `422 Unprocessable Entity` error. All outgoing API payloads must be scrubbed of deprecated fields.
- **UI Update**: Update the Flutter Admin Dashboard to reflect the pruned model. Replace the cluttered configuration screens with a clean, single-column settings card containing only the essential fields (Identity, Tone, Metadata Checkboxes).

## 4. Required User Review
- **Data Migration**: Deleting legacy fields like `layouts` from `seed_data.json` is a destructive action (though safe if they are obsolete). Do we need to preserve any historical layouts, or can we confidently wipe them and rely entirely on the new dynamic SDUI generation?
- **`SynthesisConfigDTO` Sub-Field Relocation**: Confirm the proposed relocation targets for `allowed_exports` (→ Workflow), `allowed_mcp_tools` (→ StepRule), `length_constraint` (→ PromptBlock), `historical_context_mode` (→ Workflow), `matrix_visible_columns` (→ StepRule).
- **`display_scale` & `matrix_column_labels` Relocation**: Confirm relocation to `StepRule`-level configuration.

## 5. Cross-Epic Synchronization (Epic 104 & 105)
- **Execution Order**: This Epic MUST be executed **LAST** (after Epic 104 and 105). You cannot safely delete the `synthesis` object from `OutputProfile` or `seed_data.json` until Epic 105 has completely eliminated the `PreHydratedSynthesisStrategy` (which currently reads those fields).
- **Synergy with "Dumb" Engines**: Epic 105 ensures that the engines no longer parse schemas. This perfectly delegates the schema responsibility to the `PromptCompiler` and `SchemaFactory`, which this Epic (106) explicitly controls via the new `StepRule.expected_sdui_type`. **Architectural Lock**: The introduction of `expected_sdui_type` must be synchronized precisely with Epic 105's `LLMNodeStrategy` pre-compilation update to ensure `SynthesisEngine` receives the correct schema payload.
