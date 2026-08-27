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

  static const List<Map<String, String>> availableColumns = [
    {'key': 'label', 'labelFi': 'Ulottuvuus', 'labelEn': 'Dimension'},
    {'key': 'distribution', 'labelFi': 'Jakauma', 'labelEn': 'Distribution'},
    {
      'key': 'row_explanation',
      'labelFi': 'Rivisyy / Peruste',
      'labelEn': 'Row Explanation',
    },
    {'key': 'quotes', 'labelFi': 'Lainaukset', 'labelEn': 'Quotes'},
    {
      'key': 'normalized_score',
      'labelFi': 'Normitettu',
      'labelEn': 'Normalized',
    },
    {'key': 'score', 'labelFi': 'Pistemäärä', 'labelEn': 'Score'},
  ];

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
              'Näytettävät sarakkeet (Visible Columns):',
              style: Theme.of(
                context,
              ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
          ),
          Wrap(
            spacing: AppSpacing.s8,
            runSpacing: AppSpacing.s4,
            children: availableColumns.map((col) {
              final key = col['key']!;
              final label = col['labelFi']!;
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
