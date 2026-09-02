import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/block_card_registry.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 3: Detailed Section Configuration for complex SDUI blocks.
/// Provides a Master-Detail list navigation to inspect and configure individual report sections.
class ProfileSectionConfigTab extends ConsumerWidget {
  final String id;
  const ProfileSectionConfigTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final payload = formState.value;
    if (payload == null) {
      throw StateError(
        'Profile payload must not be null when rendering ProfileSectionConfigTab',
      );
    }

    final promptBlocksState = ref.watch(promptBlocksControllerProvider);
    final workflowsState = ref.watch(workflowsControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);
    final selectedSection = ref.watch(
      selectedOutputProfileConfigSectionProvider(id),
    );

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
            if (step.roleBlockId != null) {
              allowedBlockIds.add(step.roleBlockId!);
            }
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
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
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

    // Filter to only detailed blocks enabled in targetBlockOrder
    final activeDetailedBlocks = payload.targetBlockOrder
        .where((b) => BlockCardRegistry.detailedBlockTypes.contains(b))
        .toList();

    if (activeDetailedBlocks.isEmpty) {
      return ListView(
        padding: AppSpacing.p16,
        children: [
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: AppSpacing.p24,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.tune_outlined,
                    size: 48,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  AppSpacing.h16,
                  Text(
                    l10n.noDetailedSectionsActiveTitle,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  AppSpacing.h8,
                  Text(
                    l10n.noDetailedSectionsActiveSubtitle,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    // Detail View: If a section is selected, render its header with back button and its dedicated card
    if (selectedSection != null &&
        activeDetailedBlocks.contains(selectedSection)) {
      return ListView(
        padding: AppSpacing.p16,
        children: [
          Row(
            children: [
              OutlinedButton.icon(
                onPressed: () {
                  ref
                      .read(
                        selectedOutputProfileConfigSectionProvider(id).notifier,
                      )
                      .select(null);
                },
                icon: const Icon(Icons.arrow_back),
                label: Text(l10n.allSectionsListLabel),
              ),
              AppSpacing.w16,
              Expanded(
                child: Text(
                  BlockCardRegistry.getBlockTitle(selectedSection, l10n),
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          AppSpacing.h16,
          BlockCardRegistry.getBlockCard(
            key: ValueKey(selectedSection),
            type: selectedSection,
            context: context,
            profileId: id,
            payload: payload,
            updatePayload: updatePayload,
            allowedBlockIds: allowedBlockIds,
            promptBlocksState: promptBlocksState,
            dragHandle: null,
          ),
        ],
      );
    }

    // Master View: Render the list of active configurable output sections
    return ListView(
      padding: AppSpacing.p16,
      children: [
        Text(
          l10n.sectionConfigHeaderTitle,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: AppSpacing.s4),
        Text(
          l10n.sectionConfigSubtitle,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
        AppSpacing.h16,
        ...activeDetailedBlocks.map((blockType) {
          final title = BlockCardRegistry.getBlockTitle(blockType, l10n);
          final subtitle = BlockCardRegistry.getBlockSubtitle(blockType, l10n);
          final icon = BlockCardRegistry.getBlockIcon(blockType);

          return Card(
            elevation: 2,
            margin: const EdgeInsets.only(bottom: AppSpacing.s12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: ListTile(
              contentPadding: AppSpacing.p16,
              leading: CircleAvatar(
                backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                child: Icon(
                  icon,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
              ),
              title: Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              subtitle: Padding(
                padding: const EdgeInsets.only(top: AppSpacing.s4),
                child: Text(subtitle),
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                ref
                    .read(
                      selectedOutputProfileConfigSectionProvider(id).notifier,
                    )
                    .select(blockType);
              },
            ),
          );
        }),
      ],
    );
  }
}
