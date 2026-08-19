import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';

/// Dedicated configuration card for matrixSummaryTableBlock.
class MatrixSummaryTableCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  static const List<String> availableColumns = [
    'label',
    'atomic_breakdown',
    'row_explanation',
    'normalized_score',
    'score',
    'quotes',
  ];

  const MatrixSummaryTableCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  OutputLayoutBlock _resolveSummaryBlock() {
    return payload.layouts
            .where((l) => l.presetView == PresetView.matrixSummary)
            .firstOrNull ??
        const OutputLayoutBlock(
          presetView: PresetView.matrixSummary,
          matrixVisibleColumns: ['label', 'score'],
          targetBlocks: ['*'],
        );
  }

  void _saveSummaryBlock(OutputLayoutBlock updatedBlock) {
    final newLayouts = List<OutputLayoutBlock>.from(payload.layouts);
    final idx = newLayouts.indexWhere(
      (l) => l.presetView == PresetView.matrixSummary,
    );
    if (idx >= 0) {
      newLayouts[idx] = updatedBlock;
    } else {
      newLayouts.add(updatedBlock);
    }
    updatePayload(payload.copyWith(layouts: newLayouts));
  }

  @override
  Widget build(BuildContext context) {
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.matrixSummaryTableBlock,
    );
    final summaryBlock = _resolveSummaryBlock();

    return BaseBlockCard(
      blockType: TargetBlockType.matrixSummaryTableBlock,
      title: 'Matrix Summary Table',
      subtitle:
          'Tabular overview of matrix evaluations, atomic breakdown, and scores',
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
          Text(
            'Visible Table Columns',
            style: Theme.of(
              context,
            ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: AppSpacing.s8),
          Wrap(
            spacing: AppSpacing.s8,
            runSpacing: AppSpacing.s4,
            children: availableColumns.map((col) {
              final isSelected = summaryBlock.matrixVisibleColumns.contains(
                col,
              );
              return FilterChip(
                label: Text(col),
                selected: isSelected,
                onSelected: (selected) {
                  final newCols = List<String>.from(
                    summaryBlock.matrixVisibleColumns,
                  );
                  if (selected) {
                    if (!newCols.contains(col)) newCols.add(col);
                  } else {
                    newCols.remove(col);
                  }
                  _saveSummaryBlock(
                    summaryBlock.copyWith(matrixVisibleColumns: newCols),
                  );
                },
              );
            }).toList(),
          ),
          if (summaryBlock.matrixVisibleColumns.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.s16),
            Text(
              'Column Label Overrides',
              style: Theme.of(
                context,
              ).textTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: AppSpacing.s8),
            for (final col in summaryBlock.matrixVisibleColumns) ...[
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                child: I18nTextField(
                  label: 'Column Label: $col',
                  initialData: summaryBlock.matrixColumnLabels[col],
                  onChanged: (val) {
                    final newLabels = Map<String, dynamic>.from(
                      summaryBlock.matrixColumnLabels,
                    );
                    if (val.translations.isEmpty) {
                      newLabels.remove(col);
                    } else {
                      newLabels[col] = val;
                    }
                    _saveSummaryBlock(
                      summaryBlock.copyWith(
                        matrixColumnLabels: newLabels.cast(),
                      ),
                    );
                  },
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }
}
