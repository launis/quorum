import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/block_card_registry.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 3: Visual Block Builder driven by targetBlockOrder and BlockCardRegistry.
class ProfileLayoutsTab extends ConsumerWidget {
  final String id;
  const ProfileLayoutsTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) {
      throw StateError(
        'Profile payload must not be null when rendering ProfileLayoutsTab',
      );
    }

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
            if (step.roleBlockId != null)
              allowedBlockIds.add(step.roleBlockId!);
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

    final inactiveBlocks = TargetBlockType.values
        .where(
          (b) =>
              b != TargetBlockType.synthesisTextBlock &&
              !payload.targetBlockOrder.contains(b),
        )
        .toList();

    return ListView(
      padding: AppSpacing.p16,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              l10n.reportVisualBlocksHeader,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              l10n.activeBlocksCount(payload.targetBlockOrder.length),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.s4),
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
            final list = List<TargetBlockType>.from(payload.targetBlockOrder);
            final item = list.removeAt(oldIndex);
            list.insert(newIndex, item);
            updatePayload(payload.copyWith(targetBlockOrder: list));
          },
          children: payload.targetBlockOrder.asMap().entries.map((entry) {
            final idx = entry.key;
            final blockType = entry.value;

            return BlockCardRegistry.getBlockCard(
              key: ValueKey(blockType),
              type: blockType,
              context: context,
              profileId: id,
              payload: payload,
              updatePayload: updatePayload,
              allowedBlockIds: allowedBlockIds,
              promptBlocksState: promptBlocksState,
              dragHandle: ReorderableDragStartListener(
                index: idx,
                child: const Padding(
                  padding: EdgeInsets.all(AppSpacing.s4),
                  child: Icon(Icons.drag_handle),
                ),
              ),
            );
          }).toList(),
        ),
        if (inactiveBlocks.isNotEmpty) ...[
          AppSpacing.h16,
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              side: BorderSide(
                color: Theme.of(context).colorScheme.outlineVariant,
              ),
            ),
            child: Padding(
              padding: AppSpacing.p12,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.availableBlocksHeader,
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.s8),
                  Wrap(
                    spacing: AppSpacing.s8,
                    runSpacing: AppSpacing.s4,
                    children: inactiveBlocks.map((b) {
                      return ActionChip(
                        avatar: const Icon(Icons.add, size: 16),
                        label: Text(BlockCardRegistry.getBlockTitle(b, l10n)),
                        onPressed: () {
                          final newOrder = List<TargetBlockType>.from(
                            payload.targetBlockOrder,
                          )..add(b);
                          final syncExtensions =
                              BlockCardRegistry.syncWorkflowExtensionsMap[b];
                          final newWorkflowExtensions =
                              List<XaiExtensionType>.from(
                                payload.visibleWorkflowExtensions,
                              );
                          if (syncExtensions != null) {
                            for (final ext in syncExtensions) {
                              if (!newWorkflowExtensions.contains(ext)) {
                                newWorkflowExtensions.add(ext);
                              }
                            }
                          }
                          updatePayload(
                            payload.copyWith(
                              targetBlockOrder: newOrder,
                              visibleWorkflowExtensions: newWorkflowExtensions,
                            ),
                          );
                        },
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }
}
