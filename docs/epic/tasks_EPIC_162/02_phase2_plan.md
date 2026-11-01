<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# Phase 2: Studio `Workflow` & `OutputProfile` Stale `target_blocks` Synchronization & Error FilterChip UI

**Overview:** Resolve Chapter 6 of `@[docs/arkkitehtuurin_parannuskohteet.md#L232-329]` (`@[docs/arkkitehtuurin_parannuskohteet.md#L232-259]`). When a step is deleted from a `Workflow` in `WorkflowStepsTab._deleteStep` (`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L91-124]`) and the workflow is saved via `StudioWorkflowService.save_workflow` (`@[backend_v2/services/studio/workflow_service.py#L283-321]`), automatically prune orphaned `blk_...` references from all linked `OutputProfile` entities (`matrix_synthesis_groups[*].target_blocks`, `variance_target_block`, and `user_role_target_block`) using positive-ID-set membership (`Workflow.get_allowed_prompt_block_targets` in `@[backend_v2/models/domain/workflow.py#L174-193]` and `Workflow.get_allowed_layout_targets` in `@[backend_v2/models/domain/workflow.py#L195-213]`) while preserving `OutputProfile.validate_variance_target_block_coherence` (`@[backend_v2/models/domain/output_profile.py#L225-253]`), `OutputProfile.validate_matrix_graphs_coherence` (`@[backend_v2/models/domain/output_profile.py#L255-269]`), and `MatrixSynthesisGroup.validate_dimensional_cardinality` (`@[backend_v2/models/domain/synthesis.py#L237-280]`). Strengthen `StudioOutputProfileService.save_output_profile` (`@[backend_v2/services/studio/output_profile_service.py#L26-L295]` / `@[backend_v2/services/studio/output_profile_service.py#L96-155]`) to validate `variance_target_block` and `user_role_target_block` against `allowed_prompt_blocks`, and update `MatrixGraphItemEditor` (`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L47-53]` and `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]`) and `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L41-72]` with localized `.arb` strings (`@[client_app_v2/lib/l10n/app_en.arb#L2963-2983]` and `@[client_app_v2/lib/l10n/app_fi.arb#L2213-2233]`) so any unsaved stale block ID in `group.targetBlocks` renders as a removable error-styled `FilterChip`.

**Source:** `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` Phase 2: Studio `Workflow` & `OutputProfile` Stale `target_blocks` Synchronization & Error FilterChip UI

**Target Files:**
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L283-321]`
- `[MODIFY] @[backend_v2/services/studio/output_profile_service.py#L96-155]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb#L2963-2983]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb#L2213-2233]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L41-72]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L267-L278]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L501-L587]`
- `[MODIFY] @[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart#L209-291]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/services/studio/workflow_service.py#L283-321]`**<br>**`@[backend_v2/services/studio/output_profile_service.py#L96-155]`** | Leaving orphaned `blk_...` IDs in linked `OutputProfile` entities when workflow steps are deleted on `save_workflow`, and omitting `variance_target_block` / `user_role_target_block` validation against `allowed_prompt_blocks` in `save_output_profile`. | Auto-prune stale block IDs from linked `OutputProfile` models in `StudioWorkflowService._sync_output_profiles_for_workflow` using `get_allowed_prompt_block_targets` and `get_allowed_layout_targets`, coerce `view_type` when remaining `target_blocks` count drops below the dimensionality threshold, and enforce Fail-Fast `ErrorCodes.VALIDATION_FAILED` in `StudioOutputProfileService.save_output_profile`. | Zero background cron jobs or database triggers; synchronize deterministically inside `save_workflow`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/workflow_service.py backend_v2/services/studio/output_profile_service.py --test --ast-strict` |
| **`@[client_app_v2/lib/l10n/app_en.arb#L2963-2983]`**<br>**`@[client_app_v2/lib/l10n/app_fi.arb#L2213-2233]`**<br>**`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]`**<br>**`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L41-72]`** | Silently filtering out stale block IDs in `MatrixGraphItemEditor.matrixBlocks` (`#L47-53`) so the user cannot see or deselect orphaned IDs still present in `group.targetBlocks`. | Compute `staleBlockIds` in `MatrixGraphItemEditor` and render removable error-styled `FilterChip` items using `Theme.of(context).colorScheme.errorContainer` and `l10n.staleTargetBlockChipLabel(staleId)`. | Zero cross-feature Riverpod listeners between workflow and profile editors; derive stale chips purely from `allowedBlockIds` and `group.targetBlocks`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/ --build` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 completion in `@[docs/epic/EPIC_162_tracker.md]` and read `@[backend_v2/services/studio/workflow_service.py#L283-321]`, `@[backend_v2/services/studio/output_profile_service.py#L96-155]`, `@[backend_v2/models/domain/workflow.py#L174-193]`, `@[backend_v2/models/domain/workflow.py#L195-213]`, `@[backend_v2/models/domain/output_profile.py#L225-253]`, `@[backend_v2/models/domain/output_profile.py#L255-269]`, `@[backend_v2/models/domain/synthesis.py#L237-280]`, and `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L47-53]` / `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]`.</action>
    <action>Look forward: Verify Step 2.1 implements backend auto-pruning in `StudioWorkflowService.save_workflow` and strict `allowed_prompt_blocks` validation in `StudioOutputProfileService.save_output_profile`, and Step 2.2 adds localized `.arb` keys and renders removable error-styled `FilterChip` widgets in `MatrixGraphItemEditor`.</action>
    <constraint invariant="positive_id_set_filtering_mandate">All target block membership checks MUST use positive set membership against `workflow.get_allowed_prompt_block_targets(all_steps)` and `workflow.get_allowed_layout_targets(all_steps)`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md] and @[docs/epic/EPIC_162_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_workflow_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]</backend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`StudioWorkflowService.save_workflow` (@[backend_v2/services/studio/workflow_service.py#L283-321]) invokes `_sync_output_profiles_for_workflow(saved)` to prune stale `target_blocks`, `variance_target_block`, and `user_role_target_block` references from all linked `OutputProfile` entities while maintaining `MatrixSynthesisGroup.validate_dimensional_cardinality`, `OutputProfile.validate_matrix_graphs_coherence`, and `OutputProfile.validate_variance_target_block_coherence` invariants.</item>
    <item>`StudioOutputProfileService.save_output_profile` (@[backend_v2/services/studio/output_profile_service.py#L96-155]) validates `profile.variance_target_block` and `profile.user_role_target_block` against `workflow.get_allowed_prompt_block_targets(all_steps)`, logging an RFC 7807 `logger.error` and raising `AppException(ErrorCodes.VALIDATION_FAILED, status_code=400)` on mismatch.</item>
    <item>`staleTargetBlockChipLabel` added to @[client_app_v2/lib/l10n/app_en.arb#L2963-2983] and @[client_app_v2/lib/l10n/app_fi.arb#L2213-2233] and generated via `flutter gen-l10n`.</item>
    <item>`MatrixGraphItemEditor` (@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305]) renders removable error-styled `FilterChip` widgets for stale block IDs in `group.targetBlocks` and passes `flutter_audit_loop.py --build` and `audit_flutter_theme_sovereignty.py`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT use negative string filtering (`not b.startswith(...)`) when resolving allowed prompt blocks; use `workflow.get_allowed_prompt_block_targets(all_steps)` and `workflow.get_allowed_layout_targets(all_steps)` exclusively.</anti_target>
    <anti_target>Do NOT hardcode colors (`Colors.red`) or literal English/Finnish text in `MatrixGraphItemEditor`; use `Theme.of(context).colorScheme.errorContainer` / `onErrorContainer` and `AppLocalizations` (`no_magic_strings_l10n`, `design_token_absolute_rule`).</anti_target>
  </anti_targets>

  <step id="2.1" name="Backend StudioWorkflowService.save_workflow Auto-Pruning &amp; StudioOutputProfileService.save_output_profile Target Block Validation">
    <action>In @[backend_v2/services/studio/workflow_service.py#L283-321], implement `_sync_output_profiles_for_workflow(self, workflow: Workflow) -> None` and invoke it at the end of `StudioWorkflowService.save_workflow` before returning `saved`:
    1. Fetch `all_steps = await self.workflow_repo.get_all_steps()` and `all_profiles = await self.output_profile_repo.get_all_output_profiles()`.
    2. Compute `allowed_prompt_blocks = workflow.get_allowed_prompt_block_targets(all_steps)` and `allowed_layout_targets = workflow.get_allowed_layout_targets(all_steps)`.
    3. For each `profile` in `all_profiles` where `profile.workflow_id == workflow.id`:
       - Filter each `group.target_blocks` in `profile.matrix_synthesis_groups` to `[b for b in group.target_blocks if b in allowed_layout_targets]`. If `filtered_targets` is empty, omit the group; if `group.view_type == "matrix_3d"` and `len(filtered_targets) == 2`, coerce `view_type` to `MatrixViewType("compare_2d")`; if `group.view_type in ("compare_2d", "matrix_3d")` and `len(filtered_targets) == 1`, coerce `view_type` to `MatrixViewType("metrics_1d")`. If `updated_groups` becomes empty and `TargetBlockType.MATRIX_GRAPHS_BLOCK` is in `profile.target_block_order`, remove `TargetBlockType.MATRIX_GRAPHS_BLOCK` from `target_block_order`.
       - If `profile.variance_target_block is not None` and `profile.variance_target_block not in allowed_prompt_blocks`, set `variance_target_block = None`, remove `TargetBlockType.VARIANCE_VALIDATION_BLOCK` from `target_block_order`, and remove `XaiExtensionType.VARIANCE_VALIDATION` from `visible_workflow_extensions`.
       - If `profile.user_role_target_block is not None` and `profile.user_role_target_block not in allowed_prompt_blocks`, set `user_role_target_block = None`.
       - When any field changed, instantiate `updated_profile = profile.model_copy(update=...)`, validate via `OutputProfile.model_validate(updated_profile.model_dump())`, and persist via `await self.output_profile_repo.save_output_profile(updated_profile)`.</action>
    <action>In @[backend_v2/services/studio/output_profile_service.py#L96-155], extend `StudioOutputProfileService.save_output_profile` to compute `allowed_prompt_blocks = workflow.get_allowed_prompt_block_targets(all_steps)` and validate that `profile.variance_target_block` (when not `None`) and `profile.user_role_target_block` (when not `None`) belong to `allowed_prompt_blocks`, logging a structured `logger.error` with `ErrorCodes.VALIDATION_FAILED.name` and raising `AppException(ErrorCodes.VALIDATION_FAILED, status_code=400)` on mismatch.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L267-L278] and @[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L501-L587], add positive, boundary, and negative unit tests verifying automatic pruning of stale `target_blocks`, `view_type` dimensionality coercion (`MATRIX_3D -> COMPARE_2D -> METRICS_1D` and empty-group removal), `variance_target_block` / `user_role_target_block` pruning on `save_workflow`, and Fail-Fast HTTP 400 rejection in `save_output_profile`.</action>
    <constraint invariant="in_place_upsert_standard_mandate">All `OutputProfile` updates triggered during `save_workflow` MUST mutate in-place under their existing `profile.id` and pass full root `OutputProfile` schema validation before persistence.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/workflow_service.py backend_v2/services/studio/output_profile_service.py backend_v2/tests/unit/services/studio/test_workflow_service.py backend_v2/tests/unit/services/studio/test_output_profile_service.py --test --ast-strict</audit_command>
  </step>

  <step id="2.2" name="Localization .arb Strings &amp; Flutter MatrixGraphItemEditor Error FilterChip Rendering">
    <action>In @[client_app_v2/lib/l10n/app_en.arb#L2963-2983] and @[client_app_v2/lib/l10n/app_fi.arb#L2213-2233], add `"staleTargetBlockChipLabel": "Removed from workflow: {blockId}"` (English) and `"staleTargetBlockChipLabel": "Poistettu työnkulusta: {blockId}"` (Finnish) with `@staleTargetBlockChipLabel` placeholder metadata for `blockId` (`String`), and run `flutter gen-l10n`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L260-305] and @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L41-72], compute `final staleBlockIds = allowedBlockIds.isEmpty ? const &lt;String&gt;[] : group.targetBlocks.where((id) =&gt; !allowedBlockIds.contains(id)).toList();` and render a selected error `FilterChip` for each `staleId` in `staleBlockIds` inside the `Wrap` children list using `Theme.of(context).colorScheme.errorContainer`, `Theme.of(context).colorScheme.onErrorContainer`, `avatar: Icon(Icons.warning_amber_rounded, size: 16, color: Theme.of(context).colorScheme.onErrorContainer)`, and `label: Text(l10n.staleTargetBlockChipLabel(staleId))`, where `onSelected` removes `staleId` from `group.targetBlocks` via `onUpdate(group.copyWith(targetBlocks: newTargets))`.</action>
    <action>In @[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart#L209-291] (`@[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart#L1-291]`), add widget unit tests verifying that stale block IDs in `group.targetBlocks` outside `allowedBlockIds` render as error `FilterChip` widgets with `Removed from workflow: <id>` and that tapping the chip removes the stale block ID via `onUpdate`.</action>
    <constraint invariant="studio_unified_visual_design_system">Error `FilterChip` widgets MUST use `Theme.of(context).colorScheme` tokens (`errorContainer`, `onErrorContainer`, `error`) and `AppLocalizations` with zero hardcoded colors or strings.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/ --build</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_flutter_theme_sovereignty.py</audit_command>
  </step>

  <test_contracts>
    <test name="test_save_workflow_prunes_stale_target_blocks_and_coerces_view_type_on_linked_output_profiles" category="positive">
      <input>Workflow with 2 remaining matrix blocks saved after deleting a 3rd step; linked OutputProfile has a MATRIX_3D group referencing all 3 blocks and variance_target_block pointing to the deleted block</input>
      <expected>Linked OutputProfile is persisted with the deleted block removed from target_blocks, group.view_type coerced to COMPARE_2D, variance_target_block set to None, and VARIANCE_VALIDATION_BLOCK removed from target_block_order</expected>
    </test>
    <test name="test_save_workflow_removes_empty_matrix_synthesis_group_and_matrix_graphs_block_when_all_targets_deleted" category="boundary">
      <input>Workflow saved with zero remaining matrix blocks while linked OutputProfile has 1 MatrixSynthesisGroup and TargetBlockType.MATRIX_GRAPHS_BLOCK in target_block_order</input>
      <expected>Linked OutputProfile is persisted with matrix_synthesis_groups=[] and TargetBlockType.MATRIX_GRAPHS_BLOCK removed from target_block_order without failing validate_matrix_graphs_coherence</expected>
    </test>
    <test name="test_save_output_profile_rejects_stale_variance_target_block_with_validation_failed" category="negative">
      <input>StudioOutputProfileService.save_output_profile called with profile.variance_target_block="blk_01960000000070008000000000000099" not present in workflow.get_allowed_prompt_block_targets</input>
      <expected>Raises AppException with ErrorCodes.VALIDATION_FAILED (status_code=400)</expected>
    </test>
    <test name="test_save_output_profile_rejects_stale_user_role_target_block_with_validation_failed" category="negative">
      <input>StudioOutputProfileService.save_output_profile called with profile.user_role_target_block="blk_01960000000070008000000000000098" not present in workflow.get_allowed_prompt_block_targets</input>
      <expected>Raises AppException with ErrorCodes.VALIDATION_FAILED (status_code=400)</expected>
    </test>
    <test name="test_matrix_graph_item_editor_renders_and_removes_stale_target_block_chip" category="positive">
      <input>MatrixGraphItemEditor rendered with allowedBlockIds={"blk_valid_1"} and group.targetBlocks=["blk_valid_1", "blk_stale_2"]</input>
      <expected>Displays FilterChip with "Removed from workflow: blk_stale_2" and warning icon; tapping the chip invokes onUpdate with targetBlocks=["blk_valid_1"]</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 2 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/workflow_service.py backend_v2/services/studio/output_profile_service.py backend_v2/tests/unit/services/studio/test_workflow_service.py backend_v2/tests/unit/services/studio/test_output_profile_service.py --test --ast-strict`.</action>
    <action>Run Phase 2 Flutter quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/ --build` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_flutter_theme_sovereignty.py`.</action>
  </validation_gate>
</execution_protocol>
