import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class SduiMatrixTableWidget extends StatelessWidget {
  final SduiMatrixTableBlock block;

  const SduiMatrixTableWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    if (block.axes.isEmpty || block.matrixVisibleColumns.isEmpty) {
      return const SizedBox.shrink();
    }

    final locale = Localizations.localeOf(context).languageCode;
    final l10n = AppLocalizations.of(context);
    final visibleCols = block.matrixVisibleColumns;
    final labels = block.matrixColumnLabels;

    final hasEvaluative = block.axes.any((a) => a.isEvaluative);
    final hasOverride = block.axes.any((a) => a.allowContextualOverride);

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
                        axis.name +
                            (axis.isEvaluative ? ' *' : '') +
                            (axis.allowContextualOverride ? ' **' : ''),
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
                case 'quotes':
                  final atoms = axis.evaluatedAtoms;
                  if (atoms.isNotEmpty) {
                    final grouped = axis.atomsByLevel;
                    final sortedLevels = grouped.keys.toList()
                      ..sort((a, b) => b.compareTo(a));
                    cellContent = Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: sortedLevels.map((lvl) {
                        final lvlName = axis.levelNames?[lvl.toString()] ?? '';
                        final lvlAtoms = grouped[lvl] ?? [];
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '$lvl - $lvlName',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 11,
                              ),
                            ),
                            AppSpacing.h4,
                            ...lvlAtoms.map((atom) {
                              return Padding(
                                padding: const EdgeInsets.only(
                                  bottom: AppSpacing.s4,
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      '- ${atom.chartDisplayLabel}',
                                      style: TextStyle(
                                        fontWeight:
                                            atom.status ==
                                                ExecutionStatus.passed
                                            ? FontWeight.bold
                                            : FontWeight.normal,
                                        fontSize: 11,
                                      ),
                                    ),
                                    if (atom.exactQuotes.isNotEmpty)
                                      ...atom.exactQuotes.map((q) {
                                        return Padding(
                                          padding: const EdgeInsets.only(
                                            left: AppSpacing.s8,
                                            top: AppSpacing.s2,
                                          ),
                                          child: Text(
                                            '"${q.quote}"',
                                            style: TextStyle(
                                              fontSize: 10,
                                              fontStyle: FontStyle.italic,
                                              color: Theme.of(
                                                context,
                                              ).colorScheme.onSurfaceVariant,
                                            ),
                                          ),
                                        );
                                      }),
                                  ],
                                ),
                              );
                            }),
                            AppSpacing.h4,
                          ],
                        );
                      }).toList(),
                    );
                  } else {
                    cellContent = const Text('-');
                  }
                  break;
                case 'normalized_score':
                  final ratio = axis.uiPlotRatio;
                  if (ratio != null) {
                    cellContent = Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.s8,
                        vertical: AppSpacing.s4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        border: Border.all(color: Colors.green.shade200),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        '${(ratio * 100).toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade800,
                          fontSize: 12,
                        ),
                      ),
                    );
                  } else {
                    cellContent = const Text('-');
                  }
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
                        : colKey == 'quotes'
                        ? 350
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

    Widget content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        table,
        if (hasEvaluative || hasOverride) ...[
          AppSpacing.h8,
          if (hasEvaluative)
            Text(
              l10n?.matrixEvaluativeAsteriskLegend ??
                  '* = Evaluative Matrix (Impacts global score)',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontStyle: FontStyle.italic,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          if (hasOverride)
            Text(
              l10n?.matrixOverrideAsteriskLegend ??
                  '** = Contextual override allowed',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontStyle: FontStyle.italic,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
        ],
      ],
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
            content,
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s24,
        vertical: AppSpacing.s16,
      ),
      child: content,
    );
  }
}
