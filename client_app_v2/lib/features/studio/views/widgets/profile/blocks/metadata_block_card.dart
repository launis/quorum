import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

/// Config card for metadataBlock allowing checklist toggling of visible metadata fields.
class MetadataBlockCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  static const List<String> availableMetadataFields = [
    'date',
    'organization',
    'user',
    'scoring_engine',
    'strictness',
    'cost',
    'tokens',
  ];

  const MetadataBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.metadataBlock,
    );

    return BaseBlockCard(
      blockType: TargetBlockType.metadataBlock,
      title: l10n.blockMetadataTitle,
      subtitle: l10n.blockMetadataSubtitle,
      icon: Icons.info_outline,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.metadataBlock)) {
            newOrder.add(TargetBlockType.metadataBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.metadataBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.visibleMetadataFieldsLabel,
            style: Theme.of(
              context,
            ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: AppSpacing.s8),
          Wrap(
            spacing: AppSpacing.s8,
            runSpacing: AppSpacing.s4,
            children: availableMetadataFields.map((field) {
              final isSelected = payload.visibleMetadata.contains(field);
              return FilterChip(
                label: Text(field),
                selected: isSelected,
                onSelected: (selected) {
                  final newFields = List<String>.from(payload.visibleMetadata);
                  if (selected) {
                    if (!newFields.contains(field)) {
                      newFields.add(field);
                    }
                  } else {
                    newFields.remove(field);
                  }
                  updatePayload(payload.copyWith(visibleMetadata: newFields));
                },
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
