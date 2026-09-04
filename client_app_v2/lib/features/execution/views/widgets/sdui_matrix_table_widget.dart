import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
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
                  final targetLabel =
                      axis.contextTargetLabel?.get(locale) ??
                      axis.contextTarget;
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
                      if (targetLabel != null && targetLabel.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: AppSpacing.s2),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: AppSpacing.s4,
                              vertical: AppSpacing.s2,
                            ),
                            decoration: BoxDecoration(
                              color: Theme.of(
                                context,
                              ).colorScheme.surfaceContainerHighest,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              targetLabel,
                              style: Theme.of(context).textTheme.labelSmall
                                  ?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.onSurfaceVariant,
                                  ),
                            ),
                          ),
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
                case 'context_target':
                  final targetText =
                      axis.contextTargetLabel?.get(locale) ??
                      axis.contextTarget;
                  cellContent = Text(
                    targetText ?? '-',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
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
                case 'criteria':
                  final criteriaAtoms = axis.evaluatedAtoms;
                  if (criteriaAtoms.isNotEmpty) {
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
                                child: Text(
                                  '- ${atom.chartDisplayLabel.isNotEmpty && atom.chartDisplayLabel != "N/A" ? atom.chartDisplayLabel : (atom.claimLabel.isNotEmpty ? atom.claimLabel : "-")}',
                                  style: TextStyle(
                                    fontWeight:
                                        atom.status == ExecutionStatus.passed
                                        ? FontWeight.bold
                                        : FontWeight.normal,
                                    fontSize: 11,
                                  ),
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
                case 'quotes':
                  final quoteAtoms = axis.evaluatedAtoms;
                  final hasAnyQuotes = quoteAtoms.any(
                    (a) =>
                        a.exactQuotes.isNotEmpty ||
                        (axis.allowContextualOverride &&
                            a.contextualOverride &&
                            a.status == ExecutionStatus.passed),
                  );
                  if (hasAnyQuotes) {
                    final grouped = axis.atomsByLevel;
                    final sortedLevels = grouped.keys.toList()
                      ..sort((a, b) => b.compareTo(a));
                    cellContent = Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: sortedLevels
                          .where((lvl) {
                            final lvlAtoms = grouped[lvl] ?? [];
                            return lvlAtoms.any(
                              (a) =>
                                  a.exactQuotes.isNotEmpty ||
                                  (axis.allowContextualOverride &&
                                      a.contextualOverride &&
                                      a.status == ExecutionStatus.passed),
                            );
                          })
                          .map((lvl) {
                            final lvlName =
                                axis.levelNames?[lvl.toString()] ?? '';
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
                                ...lvlAtoms
                                    .where(
                                      (atom) =>
                                          atom.exactQuotes.isNotEmpty ||
                                          (axis.allowContextualOverride &&
                                              atom.contextualOverride &&
                                              atom.status ==
                                                  ExecutionStatus.passed),
                                    )
                                    .map((atom) {
                                      if (atom.exactQuotes.isNotEmpty) {
                                        return Padding(
                                          padding: const EdgeInsets.only(
                                            bottom: AppSpacing.s4,
                                          ),
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              if (atom.claimLabel
                                                  .trim()
                                                  .isNotEmpty)
                                                Padding(
                                                  padding:
                                                      const EdgeInsets.only(
                                                        left: AppSpacing.s4,
                                                        bottom: AppSpacing.s2,
                                                      ),
                                                  child: Text(
                                                    '${atom.claimLabel.trim()}:',
                                                    style: const TextStyle(
                                                      fontWeight:
                                                          FontWeight.w600,
                                                      fontSize: 10,
                                                    ),
                                                  ),
                                                ),
                                              ...atom.exactQuotes.map((q) {
                                                return Padding(
                                                  padding:
                                                      const EdgeInsets.only(
                                                        left: AppSpacing.s4,
                                                        top: AppSpacing.s2,
                                                      ),
                                                  child: Text(
                                                    '"${q.quote}"',
                                                    style: TextStyle(
                                                      fontSize: 10,
                                                      fontStyle:
                                                          FontStyle.italic,
                                                      color: Theme.of(context)
                                                          .colorScheme
                                                          .onSurfaceVariant,
                                                    ),
                                                  ),
                                                );
                                              }),
                                            ],
                                          ),
                                        );
                                      } else {
                                        final explanation =
                                            atom.semanticReasoning
                                                .trim()
                                                .isNotEmpty
                                            ? atom.semanticReasoning.trim()
                                            : (atom.claimLabel.trim().isNotEmpty
                                                  ? atom.claimLabel.trim()
                                                  : '-');
                                        final labelPrefix =
                                            atom.claimLabel.trim().isNotEmpty
                                            ? '${atom.claimLabel.trim()}: '
                                            : '';
                                        return Padding(
                                          padding: const EdgeInsets.only(
                                            left: AppSpacing.s4,
                                            bottom: AppSpacing.s4,
                                            top: AppSpacing.s2,
                                          ),
                                          child: Text.rich(
                                            TextSpan(
                                              style: TextStyle(
                                                fontSize: 10,
                                                color: Theme.of(
                                                  context,
                                                ).colorScheme.onSurfaceVariant,
                                              ),
                                              children: [
                                                TextSpan(
                                                  text: '** $labelPrefix',
                                                  style: const TextStyle(
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                                TextSpan(
                                                  text: explanation,
                                                  style: const TextStyle(
                                                    fontStyle: FontStyle.italic,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        );
                                      }
                                    }),
                                AppSpacing.h4,
                              ],
                            );
                          })
                          .toList(),
                    );
                  } else {
                    cellContent = const Text('-');
                  }
                  break;
                case 'source':
                  final title = axis.citedSourceTitle;
                  final url = axis.citedSourceUrl;
                  final webCitation = axis.citedWebCitation;
                  final clustered = axis.clusteredRowSources;

                  if (title != null || url != null) {
                    cellContent = Padding(
                      padding: const EdgeInsets.symmetric(
                        vertical: AppSpacing.s4,
                      ),
                      child: url != null
                          ? InkWell(
                              onTap: () {
                                final uri = Uri.tryParse(url);
                                if (uri != null) {
                                  launchUrl(
                                    uri,
                                    mode: LaunchMode.externalApplication,
                                  );
                                }
                              },
                              child: Text(
                                title ?? url,
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.primary,
                                  decoration: TextDecoration.underline,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            )
                          : Text(
                              title!,
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                    );
                  } else if (webCitation != null && webCitation.isNotEmpty) {
                    cellContent = Padding(
                      padding: const EdgeInsets.symmetric(
                        vertical: AppSpacing.s4,
                      ),
                      child: InkWell(
                        onTap: () {
                          final uri = Uri.tryParse(webCitation);
                          if (uri != null) {
                            launchUrl(
                              uri,
                              mode: LaunchMode.externalApplication,
                            );
                          }
                        },
                        child: Text(
                          webCitation,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.primary,
                            decoration: TextDecoration.underline,
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    );
                  } else if (clustered.isNotEmpty) {
                    cellContent = Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: clustered.map((src) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: AppSpacing.s2),
                          child: Text(
                            '${src.stepName}: ${src.query}',
                            style: const TextStyle(fontSize: 10),
                          ),
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
                        '${(ratio * 100).toStringAsFixed(1)} %',
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
                  final scoreLabel = axis.scoreDisplayLabel;
                  if (scoreLabel != null && scoreLabel != '-') {
                    cellContent = Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.s8,
                        vertical: AppSpacing.s4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        border: Border.all(color: Colors.blue.shade200),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        scoreLabel,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue.shade800,
                          fontSize: 12,
                        ),
                      ),
                    );
                  } else {
                    cellContent = const Text('-');
                  }
                  break;
                default:
                  cellContent = const Text('-');
              }
              return DataCell(
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
                  child: SizedBox(
                    width: colKey == 'label'
                        ? 220
                        : colKey == 'context_target'
                        ? 140
                        : colKey == 'distribution'
                        ? 180
                        : colKey == 'row_explanation'
                        ? 260
                        : colKey == 'criteria'
                        ? 260
                        : colKey == 'quotes'
                        ? 260
                        : colKey == 'source'
                        ? 220
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
