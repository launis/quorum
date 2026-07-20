# EPIC 106: OutputProfile Simplification & SDUI Unification

## 1. Goal Description
Currently, the `OutputProfile` data model (and consequently, the Admin User Interface) has become a "dumping ground" for historical features. It contains a massive, confusing list of properties (`layouts`, `content_blocks`, `synthesis`, `formatting_directives`, `visible_block_extensions`, `display_scale`, etc.). This makes the UI messy, overwhelming for admins, and fractures the architecture between "row outputs" and "summaries".

**Objective**: Radically simplify the `OutputProfile` by removing redundant, legacy, and highly specific formatting fields. We will unify the generation rules using the **Polymorphic Rule Routing (PromptBlocks)** and **Server-Driven UI (SDUI)** paradigms. The Admin UI will become clean and minimalistic, while the actual power and flexibility remain intact under the hood.

## 2. Architectural Impact & Simplification Strategy

### A. What We Will REMOVE from `OutputProfile` (Deprecation)
These fields clutter the UI and violate the Single Source of Truth, as they attempt to control things the `PromptCompiler` or SDUI should handle natively:
- `formatting_directives`: LLM formatting rules do not belong in the profile. They belong in the `PromptBlock` (e.g., as part of the `EXECUTION_PERSONA`). **Active usage** in `llm.py:L410` and `worker.py:L792` must be migrated to read from `PromptBlock` configuration.
- `synthesis` (`SynthesisConfigDTO`) **ON `OutputProfile` ONLY**: Nested synthesis configuration objects are a symptom of the old standalone Synthesis strategy. Epic 105 unifies synthesis, making this redundant. **Active usage** in `worker.py:L770-798` must be migrated (see Phase 2.5 below). Note: `OutputLayoutBlock.synthesis` (per-section synthesis) and `ReportLayoutDTO.synthesis` remain UNTOUCHED — they are per-layout overrides, not profile-level config. Sub-fields require explicit relocation:
  - `SynthesisConfigDTO.allowed_exports` → Relocate to `Workflow`-level configuration (export formats are a workflow concern, not a profile concern).
  - `SynthesisConfigDTO.allowed_mcp_tools` → Relocate to `StepRule`-level configuration (MCP tool availability is a per-step execution concern).
  - `SynthesisConfigDTO.length_constraint` → Relocate to `OutputLayoutBlock.synthesis` (per-section synthesis). This is a **presentation directive**, NOT a cognitive instruction — placing it in `PromptBlock` would violate `execution_synthesis_tier_decoupling`.
  - `SynthesisConfigDTO.historical_context_mode` → Relocate to `Workflow`-level configuration.
  - `SynthesisConfigDTO.matrix_visible_columns` → Relocate to `StepRule`-level (this controls SDUI rendering per step).
- `matrix_column_labels`: SDUI rendering control. Relocate to `StepRule`-level or to the `PromptBlock` associated with the matrix step.

### A.1. Fields EXPLICITLY RETAINED (Red-Team Validated)
The following fields were initially considered for deprecation but are **actively consumed by 3-7+ production service files** and MUST be retained:
- `layouts` (`list[OutputLayoutBlock]`): **NOT legacy.** This is the report structure backbone consumed by `blueprint.py` (`_build_layouts()`), `sdui_mapper_service.py`, `pdf_generator.py`, `llm.py`, `output_profile_service.py`, and `workflow_service.py`. Removing it would destroy the entire report generation pipeline.
- `content_blocks`: Runtime-populated SDUI synthesis block carrier actively consumed by `blueprint.py` (L896-904, L1177-1179, L1259), `sdui_mapper_service.py` (L62-71), and `execution.py` (L1218). If deprecation is desired in a future Epic, a full migration path for `blueprint.py`'s synthesis block caching logic MUST be specified first.
- `visible_block_extensions` / `visible_workflow_extensions`: **NOT over-engineered.** These typed `list[XaiExtensionType]` arrays are the admin SSOT for controlling which XAI features appear in reports. Actively consumed by `context_router.py` (L95), `blueprint.py` (L857-860), and `scoring.py` (L608-954). Boolean toggles CANNOT express selective extension visibility (e.g., "show Citation and Falsification but not Coaching").
- `display_scale`: Profile-level presentation concern. Different profiles may want different scaling for the SAME workflow step (e.g., "Executive Summary" uses `normalized_100`, "Technical Report" uses `original`). Moving to `StepRule` would break multi-profile rendering. Active usage in `blueprint.py:L254-404`.
- `max_extension_items`: Coupled to extension visibility controls. Retained.

### B. What `OutputProfile` WILL KEEP (The "Clean UI")
The UI will only present high-level, human-understandable settings:
1. **Identity**: `name`, `description`, `custom_preface` (What is this profile?).
2. **Localization & Tone**: `language`, `tone_instruction` (How should it sound?).
3. **Presentation Toggles**: `visible_metadata` (e.g., checkboxes for "Show Date", "Show Organization"), `include_diagnostic_scorecard`, `display_scale`.
4. **XAI Visibility**: `visible_block_extensions`, `visible_workflow_extensions`, `max_extension_items`.
5. **Overrides**: `strictness_level`, `scoring_strategy` (profile-level overrides that remain valid at this scope).
6. **Report Structure**: `layouts` (list of `OutputLayoutBlock` defining report sections).

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
- **Action**: Add `allowed_exports: list[Literal["pdf", "docx", "raw_json"]] = Field(...)` and `historical_context_mode: LaxHistoricalContextMode = Field(...)` to the `Workflow` model. (Per `zero_defaults_mandate`, default factories for critical structural data are forbidden. The seed data MUST explicitly define these fields). Note: Epic 104 revealed the danger of magic strings (`list[str]`), so strict Pydantic Literal typings MUST be enforced here.
- **Why**: Epic 106 relocates `allowed_exports` and `historical_context_mode` from `SynthesisConfigDTO` to the `Workflow` level. These target fields MUST exist before Phase 2.5 attempts to migrate `worker.py` to use them.

### Phase 1: Data Model Pruning (`backend_v2/models/v2_core.py` & `backend_v2/models/dtos/output_profile.py`)
- Remove the deprecated fields (`synthesis`, `formatting_directives`, `matrix_column_labels`) from the `OutputProfile` Domain Model, `EmbeddedOutputProfile`, and ALL corresponding DTOs (`OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, `OutputProfileResponseDTO`, `OutputProfileConfig` in `lightweight_matrix.py`).
- *Architectural Rule*: Quorum strictly separates database state models (Domain) and API transport models (DTO). Both layers must be pruned simultaneously to prevent boundary parsing failures.
- **Development Phase Clean Slate Wipe (No Legacy Support)**: Since the system is in active development, we do NOT need complex zero-downtime migrations. Simply update `backend_v2/seed/seed_data.json` manually: 
  1. **OutputProfile Pruning**: Delete the confirmed deprecated keys (`synthesis`, `formatting_directives`, `matrix_column_labels`). You MUST keep identity, tone, presentation, XAI visibility, layouts, content_blocks, display_scale, and override fields.
  2. **Workflow Step Validation**: Verify that the mandatory `expected_sdui_type` (already injected via Epic 105) exists in all `StepRule` definitions within the `workflows` array. (e.g., Use `"grid"` for standard evaluation steps, and `"markdown"` for synthesis steps).
- **Strict Typing Enforcement**: The `expected_sdui_type` field on the `StepRule` class in `v2_core.py` was introduced in Epic 105. Epic 106 now relies on it as the absolute Single Source of Truth to drive `SchemaFactory` validation and prompt injection, enforcing absolute Fail-Fast logic.
- **Database Reset**: After modifying the seed data, developers MUST run the database wipe workflow (`run_seed.py local`) to flush the old data and load the clean seed. No backward compatibility is required.

### Phase 1.5: Legacy Unit Test Mock Migration (Lesson from Epic 104)
- **Root Cause**: Because `OutputProfile` and its DTOs enforce strict parsing (`ConfigDict(extra="forbid")`), deleting fields like `synthesis` will instantly crash any existing unit tests that pass old mock data.
- **Action**: You MUST perform a global audit of `backend_v2/tests/` (e.g., `test_output_profile.py`, `test_blueprint.py`, `test_api_clone_endpoints.py`, etc.) and scrub the `synthesis` and `formatting_directives` keys from all mock dictionary fixtures. If this is skipped, the CI pipeline will fail catastrophically with `ValidationError: extra fields not permitted`.
- **Atomic Commits**: This Phase, along with Phase 1 and Phase 2.5 MUST be committed atomically. Epic 104 successfully proved that data structure changes (Phase 1) and worker wiring (Phase 2.5) cannot be decoupled without breaking the runtime.

### Phase 2: SchemaFactory & PromptCompiler Updates
- **Pydantic Strictness & Seed Data Migration**: Update the `StepRule.expected_sdui_type` literal in `v2_core.py` to explicitly include `"grid"`. A Python script MUST be created and executed to safely migrate `seed_data.json` by assigning `"expected_sdui_type": "grid"` to all steps missing this field, preventing startup validation crashes.
- **`prompt_compiler_immutability` Exception (USER APPROVED)**: This phase modifies `prompt_compiler.py`, which is protected by the `prompt_compiler_immutability` architecture rule. The user has explicitly granted permission to modify this file as part of Epic 106.
- **Eradicate Split Brain (SSOT Enforcement)**: Ensure `PromptCompiler` relies strictly on `StepRule.expected_sdui_type` to inject the correct textual formatting instructions into the prompt. It MUST NOT try to guess or infer structural expectations from `PromptBlocks`. `PromptBlocks` are strictly reserved for cognitive instructions (e.g., tone, persona, constraints), while `expected_sdui_type` is the absolute Single Source of Truth for both the `SchemaFactory` (Pydantic validation) and the `PromptCompiler` (LLM instructions).
- **Interface Threading Gap**: The `PromptCompiler.build_dynamic_schema()` method signature MUST be updated to explicitly accept the new `expected_sdui_type` parameter. Furthermore, `llm.py` MUST explicitly extract `expected_sdui_type=step.expected_sdui_type` and pass it to this method.
- **SchemaFactory Registry Pattern (Open-Closed Principle)**: The current `SchemaFactory` uses hardcoded string matching (e.g., `if "sp_7a..."`) to route schemas. This MUST be eradicated. You MUST implement a **Strategy + Registry Pattern** to map `expected_sdui_type` values to Pydantic models:
  - Create a static registry (e.g., `backend_v2/core/registry.py`) mapping string keys (`"markdown"`, `"grid"`) to specific `SchemaBuilderStrategy` classes.
  - `"markdown"` maps to a strategy that returns the static `GlobalSynthesisDTO` (eliminating unnecessary `create_model()` overhead).
  - `"grid"` maps to a strategy that encapsulates the dynamic column generation logic.
  - The `SchemaFactory` becomes a "dumb" delegator. Massive if/else routing blocks and dynamic `eval()` execution are STRICTLY FORBIDDEN.
  - **Registry Eager Loading & Fail-Fast Mandate**: The registry implementation MUST ensure 'Eager Loading' by explicitly importing all concrete `SchemaBuilderStrategy` classes at system startup (e.g. in `__init__.py`). Furthermore, if `expected_sdui_type` requests an unmapped key, the `SchemaFactory` MUST NOT fall back to native Python errors (like `KeyError`); it MUST immediately trigger a deterministic Fail-Fast response by raising an explicit `AppException(ErrorCodes.SCHEMA_ERROR)`.
- **Remove `formatting_directives` Dependency in `llm.py`**: The current `LLMNodeStrategy` reads `output_profile.formatting_directives` at line 410-412 of `llm.py` and injects them into the system prompt. This logic must be removed. Formatting directives are now sourced from the `PromptBlock` (e.g., `EXECUTION_PERSONA` category) by the `PromptCompiler`.
- Ensure the `OutputProfile`'s `tone_instruction` is correctly injected into the final system prompt.

### Phase 2.5: Worker Rendering Pipeline Migration & Atomic `formatting_directives` Removal
- **Root Cause**: `worker.py` lines 770-798 directly read `SynthesisConfigDTO` fields (`system_prompt`, `length_constraint`, `tone_instruction`) and `OutputProfile.formatting_directives` to construct synthesis prompts. `llm.py` lines 410-412 also read `OutputProfile.formatting_directives`.
- **Migration Strategy**: The worker's rendering pipeline must be refactored to source its synthesis instructions from the DAG-produced data:
  1. The synthesis system prompt MUST be sourced from the `PromptBlock` associated with the synthesis step. To comply with the Service Layer Hydration Firewall, the worker MUST retrieve the blocks via an injected `repository.get_prompt_block(...)` call, and safely hydrate the dictionary into the Pydantic model using `PromptBlock.model_validate(pb_dict, strict=False)` (enforcing the `pydantic_pure_hydration_boundary` rule).
  2. `length_constraint` MUST be sourced from `OutputLayoutBlock.synthesis` (per-section synthesis configuration). Per `execution_synthesis_tier_decoupling`, length constraints are presentation directives that MUST NOT live on `PromptBlock`. The `tone_instruction`, however, MUST strictly continue to be sourced from the `OutputProfile` configuration (preserving it as the SSOT for global tone).
  3. `formatting_directives` MUST be removed from the worker's prompt construction and `llm.py`'s prompt construction AT THE SAME TIME. The `PromptCompiler` (Phase 2) handles this via `PromptBlock` injection.
  4. `allowed_exports` MUST be read from the `Workflow`-level configuration (new field from Phase 0).
- **Atomic Commit Mandate**: You MUST remove the `formatting_directives` references from BOTH `worker.py` AND `llm.py` in the exact same atomic Git commit. Epic 105 assumes `llm.py` is cleaned up by Epic 106, so this must be perfectly synchronized to prevent `AttributeError` crashes in reasoning steps.
- **Fail-Fast Mandate**: After migration, the worker MUST NOT contain any `.get()` or `hasattr()` fallbacks for the removed fields. If a layout defines synthesis (`if synthesis_cfg:`), but the `synthesis_block_id` is missing or the block cannot be found in the database, the system MUST immediately crash with an explicit `AppException(ErrorCodes.CONFIGURATION_ERROR)`.
- **Test Mock Blast Radius**: Because the worker will now execute `repo.get_prompt_block()`, you MUST explicitly update `tests/unit/test_worker_synthesis.py` so that its `AsyncMock` returns a valid `PromptBlock` dictionary, preventing "Fake Red" failures triggered by the new Fail-Fast logic.

### Phase 3: Flutter Admin UI Cleanup & Freezed Synchronization (Client App V2)
- **Model Synchronization (CRITICAL)**: Because Flutter uses strict JSON parsing (`disallow_unrecognized_keys`), removing fields from the backend Pydantic model WILL crash the Flutter app if the Dart model is not updated simultaneously. You MUST update the `OutputProfile` Freezed class in `client_app_v2` to remove the deprecated fields. The models MUST then be regenerated using the native Quorum loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build`.
- **Flutter Parity Gate**: Backend `output_profile.py` Pydantic deletions MUST NOT be deployed to any non-local environment until the Flutter audit loop has completed successfully AND `test_enum_parity.py` passes.
- **API Payload Scrubbing**: You MUST clean up the frontend Repository classes. All outgoing API payloads must be scrubbed of deprecated fields to prevent 422 errors. Since this is a development environment, thick client backward compatibility (version gates) is NOT required. We rely on a clean slate.
- **UI Update & Import Scrubbing**: Update the Flutter Admin Dashboard to reflect the pruned model. You MUST remove the `SynthesisEditorCard` usage from `profile_editor_view.dart` and `output_profile_crud_view.dart`. *Critical Red-Team Finding*: You MUST also delete the associated `import` statements for the synthesis editor card, otherwise Dart's strict analyzer will fail the build. *(Note: `formatting_directives` and `matrix_column_labels` UI controls were already removed in a previous PR; no UI ghost-hunting is required for them).*
- **Freezed `SynthesisConfigDTO` Scope Audit**: The `synthesis_config_dto.dart` Freezed model in `client_app_v2/lib/features/execution/models/` MUST be audited. If it is ONLY consumed via `OutputProfile`, it MUST be deleted. If it is also consumed via `OutputLayoutBlock.synthesis` or `ReportLayoutDTO.synthesis`, update the import path accordingly. Do NOT leave orphaned Freezed models.

## 4. Required User Review
- **`SynthesisConfigDTO` Sub-Field Relocation**: Confirm the proposed relocation targets for `allowed_exports` (→ Workflow), `allowed_mcp_tools` (→ StepRule), `length_constraint` (→ OutputLayoutBlock.synthesis, NOT PromptBlock), `historical_context_mode` (→ Workflow), `matrix_visible_columns` (→ StepRule).
- **`matrix_column_labels` Relocation**: Confirm relocation to `StepRule`-level configuration.
- **`expected_sdui_type` Propagation**: Confirm the threading path: `StepRule` → `DAGExecutor` → `LLMNodeStrategy.execute()` → `SchemaFactory.build_dynamic_schema()`. The `SchemaFactory` API signature will need a new parameter.
- **Append-Only Clarification (USER RESOLVED)**: Quorum's Append-Only rule strictly applies to runtime execution data (traces, generated files, logs). It DOES NOT apply to base system configurations like `seed_data.json` or Pydantic domains. Configuration states MUST be radically and atomically purged (e.g., deleting all historical `layouts` arrays) to preserve the Single Source of Truth. No historical configuration fallbacks are permitted.

## 5. Cross-Epic Synchronization (Epic 104 & 105)
- **Development Phase Sync**: Because we are in development and do not require zero-downtime migrations, Epics 105 and 106 can theoretically be deployed simultaneously (Big Bang). However, logically, Epic 106's data structure pruning (`expected_sdui_type` reliance) pairs perfectly with Epic 105's elimination of `PreHydratedSynthesisStrategy`.
- **Synergy with "Dumb" Engines**: Epic 105 ensures that the engines no longer parse schemas. This perfectly delegates the schema responsibility to the `PromptCompiler` and `SchemaFactory`, which this Epic (106) explicitly controls via the new `StepRule.expected_sdui_type`.
