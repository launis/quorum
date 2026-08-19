import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 3: Output layout block list and target block ordering.
class ProfileLayoutsTab extends ConsumerWidget {
  final String id;
  const ProfileLayoutsTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) return const SizedBox.shrink();

    final promptBlocksState = ref.watch(promptBlocksControllerProvider);
    final workflowsState = ref.watch(workflowsControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    final String selectedWorkflowId = payload.workflowId;
    final Set<String> allowedBlockIds = {};

    if (selectedWorkflowId.isNotEmpty &&
        workflowsState.hasValue &&
        stepsState.hasValue) {
      final workflows = workflowsState.value!.cast<Workflow>();
      final steps = stepsState.value!.cast<NodeStrategy>();

      final Workflow? workflow = workflows
          .where((w) => w.id == selectedWorkflowId)
          .firstOrNull;

      if (workflow != null) {
        final taskBlueprintIds = workflow.steps
            .map((s) => s.taskBlueprint)
            .toSet();

        for (final step in steps) {
          if (taskBlueprintIds.contains(step.id)) {
            if (step.roleBlockId != null) allowedBlockIds.add(step.roleBlockId!);
            if (step.extractionProtocolBlockId != null) {
              allowedBlockIds.add(step.extractionProtocolBlockId!);
            }
            allowedBlockIds.addAll(step.criteriaBlockIds);
          }
        }
      }
    }

    if (selectedWorkflowId.isEmpty) {
      return ListView(
        padding: AppSpacing.p16,
        children: [
          Card(
            child: Padding(
              padding: AppSpacing.p16,
              child: Center(
                child: Text(
                  l10n.workflowSelectWarning,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ],
      );
    }

    return ListView(
      padding: AppSpacing.p16,
      children: [
        LayoutEditorCard(
          layouts: payload.layouts,
          onChanged: (val) {
            updatePayload(payload.copyWith(layouts: val));
          },
          allowedBlockIds: allowedBlockIds,
          promptBlocksState: promptBlocksState,
        ),
        AppSpacing.h24,
        Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  l10n.targetBlockOrderTitle,
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                AppSpacing.h8,
                Text(
                  l10n.targetBlockOrderSubtitle,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                AppSpacing.h16,
                ReorderableListView(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  onReorder: (oldIndex, newIndex) {
                    if (oldIndex < newIndex) {
                      newIndex -= 1;
                    }
                    final list = List<TargetBlockType>.from(
                      payload.targetBlockOrder,
                    );
                    final item = list.removeAt(oldIndex);
                    list.insert(newIndex, item);
                    updatePayload(payload.copyWith(targetBlockOrder: list));
                  },
                  children: payload.targetBlockOrder.map((blockType) {
                    return ListTile(
                      key: ValueKey(blockType),
                      title: Text(blockType.name),
                      trailing: const Icon(Icons.drag_handle),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
