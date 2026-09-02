import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/block_card_registry.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Dedicated configuration card for TargetBlockType.varianceValidationBlock in Tab 3 (Section Config).
/// Allows configuring the performativity detector step ID and localized variance synthesis directive.
class VarianceBlockCard extends ConsumerWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  const VarianceBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.varianceValidationBlock,
    );

    final workflowsState = ref.watch(workflowsControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);

    final List<NodeStrategy> availableSteps = [];
    if (payload.workflowId.isNotEmpty &&
        workflowsState.hasValue &&
        stepsState.hasValue) {
      final workflows = workflowsState.value!.cast<Workflow>();
      final steps = stepsState.value!.cast<NodeStrategy>();
      final workflow = workflows
          .where((w) => w.id == payload.workflowId)
          .firstOrNull;

      if (workflow != null) {
        final taskBlueprintIds = workflow.steps
            .map((s) => s.taskBlueprint)
            .toSet();
        for (final step in steps) {
          if (taskBlueprintIds.contains(step.id)) {
            availableSteps.add(step);
          }
        }
      }
    }

    final selectedStepId = payload.performativityDetectorStepId;
    final isValidSelection =
        selectedStepId != null &&
        availableSteps.any((s) => s.id == selectedStepId);

    return BaseBlockCard(
      blockType: TargetBlockType.varianceValidationBlock,
      title: BlockCardRegistry.getBlockTitle(
        TargetBlockType.varianceValidationBlock,
        l10n,
      ),
      subtitle: BlockCardRegistry.getBlockSubtitle(
        TargetBlockType.varianceValidationBlock,
        l10n,
      ),
      icon: BlockCardRegistry.getBlockIcon(
        TargetBlockType.varianceValidationBlock,
      ),
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        final newWorkflowExtensions = List<XaiExtensionType>.from(
          payload.visibleWorkflowExtensions,
        );

        if (enabled) {
          if (!newOrder.contains(TargetBlockType.varianceValidationBlock)) {
            newOrder.add(TargetBlockType.varianceValidationBlock);
          }
          if (!newWorkflowExtensions.contains(
            XaiExtensionType.varianceValidation,
          )) {
            newWorkflowExtensions.add(XaiExtensionType.varianceValidation);
          }
        } else {
          newOrder.remove(TargetBlockType.varianceValidationBlock);
          newWorkflowExtensions.remove(XaiExtensionType.varianceValidation);
        }

        updatePayload(
          payload.copyWith(
            targetBlockOrder: newOrder,
            visibleWorkflowExtensions: newWorkflowExtensions,
          ),
        );
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            l10n.variancePerformativityDetectorStepLabel,
            style: Theme.of(
              context,
            ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          AppSpacing.h8,
          DropdownButtonFormField<String?>(
            initialValue: isValidSelection ? selectedStepId : null,
            isExpanded: true,
            decoration: InputDecoration(
              border: const OutlineInputBorder(),
              isDense: true,
              hintText: l10n.variancePerformativityDetectorStepHint,
            ),
            items: [
              DropdownMenuItem<String?>(
                value: null,
                child: Text(
                  l10n.variancePerformativityDetectorNone,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
              ...availableSteps.map((step) {
                final localizedName =
                    step.name.translations[l10n.localeName] ??
                    step.name.translations['en'] ??
                    step.slug;
                return DropdownMenuItem<String?>(
                  value: step.id,
                  child: Text(
                    '$localizedName (${step.slug})',
                    overflow: TextOverflow.ellipsis,
                  ),
                );
              }),
            ],
            onChanged: (val) {
              updatePayload(
                payload.copyWith(performativityDetectorStepId: val),
              );
            },
          ),
          AppSpacing.h16,
          I18nTextField(
            label: l10n.profileVarianceDirectiveLabel,
            initialData: payload.varianceSynthesisDirective,
            onChanged: (val) {
              final isEmpty =
                  val.translations.isEmpty ||
                  val.translations.values.every((v) => v.trim().isEmpty);
              updatePayload(
                payload.copyWith(
                  varianceSynthesisDirective: isEmpty ? null : val,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
