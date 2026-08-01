import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/core/theme/app_spacing.dart';

class SduiMatrixTableWidget extends StatelessWidget {
  final SduiMatrixTableBlock block;

  const SduiMatrixTableWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    if (block.axes.isEmpty || block.matrixVisibleColumns.isEmpty) {
      return const SizedBox.shrink();
    }

    final locale = Localizations.localeOf(context).languageCode;
    final visibleCols = block.matrixVisibleColumns;
    final labels = block.matrixColumnLabels;

    Widget table = SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowColor: WidgetStateProperty.all(
          Theme.of(context).colorScheme.surfaceContainerHighest,
        ),
        dataRowMaxHeight: double.infinity,
        dataRowMinHeight: 48.0,
        columnSpacing: AppSpacing.s24,
        columns: visibleCols.map((colKey) {
          final headerText = labels[colKey]?.get(locale) ?? colKey;
          return DataColumn(
            label: Expanded(
              child: Text(
                headerText,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          );
        }).toList(),
        rows: block.axes.map((axis) {
          return DataRow(
            cells: visibleCols.map((colKey) {
              Widget cellContent;
              switch (colKey) {
                case 'label':
                  cellContent = Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        axis.name + (axis.isEvaluative ? ' *' : ''),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      if (axis.description != null &&
                          axis.description!.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: AppSpacing.s4),
                          child: Text(
                            axis.description!,
                            style: Theme.of(context).textTheme.bodySmall
                                ?.copyWith(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                          ),
                        ),
                    ],
                  );
                  break;
                case 'distribution':
                case 'atomic_breakdown':
                  final breakdown = axis.levelBreakdown ?? {};
                  final names = axis.levelNames ?? {};
                  if (breakdown.isNotEmpty) {
                    final sortedKeys = breakdown.keys.toList()
                      ..sort((a, b) => b.compareTo(a));
                    cellContent = Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: sortedKeys.map((k) {
                        final numStr = int.tryParse(k) != null
                            ? int.parse(k).toString()
                            : k;
                        final hitStr = breakdown[k];
                        final name = names[k] ?? 'T$k';
                        return Text(
                          '$numStr - $name: $hitStr',
                          style: const TextStyle(fontSize: 12),
                        );
                      }).toList(),
                    );
                  } else {
                    cellContent = const Text('-');
                  }
                  break;
                case 'row_explanation':
                  cellContent = Text(
                    axis.rowExplanation,
                    style: const TextStyle(
                      fontStyle: FontStyle.italic,
                      fontSize: 12,
                    ),
                  );
                  break;
                case 'score':
                  cellContent = Text(
                    axis.scoreDisplayLabel ?? '-',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  );
                  break;
                default:
                  cellContent = const Text('-');
              }
              return DataCell(
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
                  child: SizedBox(
                    width: colKey == 'label'
                        ? 250
                        : colKey == 'row_explanation'
                        ? 300
                        : null,
                    child: cellContent,
                  ),
                ),
              );
            }).toList(),
          );
        }).toList(),
      ),
    );

    if (block.title != null) {
      return Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.s24,
          vertical: AppSpacing.s16,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              block.title!.get(locale),
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            AppSpacing.h16,
            table,
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s24,
        vertical: AppSpacing.s16,
      ),
      child: table,
    );
  }
}
