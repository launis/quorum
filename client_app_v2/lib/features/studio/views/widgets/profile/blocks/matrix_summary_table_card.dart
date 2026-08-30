import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Dedicated configuration card for matrixSummaryTableBlock with column visibility selection.
class MatrixSummaryTableCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  static const List<String> availableColumnKeys = [
    'label',
    'context_target',
    'distribution',
    'row_explanation',
    'criteria',
    'quotes',
    'source',
    'normalized_score',
    'score',
  ];

  static String getColumnLabel(BuildContext context, String key) {
    final l10n = AppLocalizations.of(context)!;
    switch (key) {
      case 'label':
        return l10n.studioMatrixColLabel;
      case 'context_target':
        return l10n.studioMatrixColContextTarget;
      case 'distribution':
        return l10n.studioMatrixColDistribution;
      case 'row_explanation':
        return l10n.studioMatrixColRowExplanation;
      case 'criteria':
        return l10n.studioMatrixColCriteria;
      case 'quotes':
        return l10n.studioMatrixColQuotes;
      case 'source':
        return l10n.studioMatrixColSource;
      case 'normalized_score':
        return l10n.studioMatrixColNormalized;
      case 'score':
        return l10n.studioMatrixColScore;
      default:
        return key;
    }
  }

  const MatrixSummaryTableCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.matrixSummaryTableBlock,
    );
    final visibleCols = payload.matrixVisibleColumns;

    return BaseBlockCard(
      blockType: TargetBlockType.matrixSummaryTableBlock,
      title: l10n.blockMatrixSummaryTitle,
      subtitle: l10n.blockMatrixSummarySubtitle,
      icon: Icons.table_chart_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.matrixSummaryTableBlock)) {
            newOrder.add(TargetBlockType.matrixSummaryTableBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.matrixSummaryTableBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: Text(
              l10n.studioMatrixVisibleColumnsTitle,
              style: Theme.of(
                context,
              ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
          ),
          Wrap(
            spacing: AppSpacing.s8,
            runSpacing: AppSpacing.s4,
            children: availableColumnKeys.map((key) {
              final label = getColumnLabel(context, key);
              final isSelected = visibleCols.contains(key);

              return FilterChip(
                label: Text(label),
                selected: isSelected,
                onSelected: (selected) {
                  final newCols = List<String>.from(visibleCols);
                  if (selected) {
                    if (!newCols.contains(key)) {
                      newCols.add(key);
                    }
                  } else {
                    newCols.remove(key);
                  }
                  updatePayload(
                    payload.copyWith(matrixVisibleColumns: newCols),
                  );
                },
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
