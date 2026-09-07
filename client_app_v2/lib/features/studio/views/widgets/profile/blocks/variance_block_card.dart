import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/block_card_registry.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Dedicated configuration card for TargetBlockType.varianceValidationBlock in Tab 3 (Section Config).
/// Allows configuring the localized variance synthesis directive and length constraint.
class VarianceBlockCard extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.varianceValidationBlock,
    );

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
          TextFormField(
            key: const Key('profile_variance_directive_field'),
            initialValue: payload.varianceSynthesisDirective,
            maxLines: 4,
            decoration: InputDecoration(
              labelText: l10n.profileVarianceDirectiveLabel,
              border: const OutlineInputBorder(),
            ),
            onChanged: (val) {
              final trimmed = val.trim();
              updatePayload(
                payload.copyWith(
                  varianceSynthesisDirective: trimmed.isEmpty ? null : trimmed,
                ),
              );
            },
          ),
          AppSpacing.h16,
          TextFormField(
            key: const Key('profile_variance_length_constraint_field'),
            initialValue: payload.varianceLengthConstraint?.toString() ?? '',
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: InputDecoration(
              labelText: l10n.profileVarianceLengthLabel,
              hintText: l10n.profileVarianceLengthHint,
              border: const OutlineInputBorder(),
              isDense: true,
            ),
            onChanged: (val) {
              final trimmed = val.trim();
              updatePayload(
                payload.copyWith(
                  varianceLengthConstraint: trimmed.isNotEmpty
                      ? int.tryParse(trimmed)
                      : null,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
