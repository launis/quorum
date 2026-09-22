import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Renders a Server-Driven UI (SDUI) matrix table block displaying dimensions,
/// evaluated criteria, evidence quotes, citations, and normalized scores.
class SduiMatrixTableWidget extends StatelessWidget {
  final SduiMatrixTableBlock block;

  const SduiMatrixTableWidget({super.key, required this.block});

  static List<String> _sortBreakdownKeys(Map<String, String> breakdown) {
    if (breakdown.isEmpty) return const [];
    final list = breakdown.keys.toList();
    list.sort((a, b) => b.compareTo(a));
    return list;
  }

  static List<int> _sortLevelIntKeys(
    Map<int, List<ScorecardAtomDto>> atomsByLevel,
  ) {
    if (atomsByLevel.isEmpty) return const [];
    final list = atomsByLevel.keys.toList();
    list.sort((a, b) => b.compareTo(a));
    return list;
  }

  @override
  Widget build(BuildContext context) {
    if (block.axes.isEmpty || block.matrixVisibleColumns.isEmpty) {
      return const SizedBox();
    }

    final locale = Localizations.localeOf(context).languageCode;
    final l10n = AppLocalizations.of(context)!;
    final visibleCols = block.matrixVisibleColumns;
    final labels = block.matrixColumnLabels;

    final hasEvaluative = block.axes.any((a) => a.isEvaluative);
    final hasOverride = block.axes.any((a) => a.allowContextualOverride);

    final table = SingleChildScrollView(
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
          final breakdown = axis.levelBreakdown ?? {};
          final sortedBreakdownKeys = _sortBreakdownKeys(breakdown);
          final sortedLevels = _sortLevelIntKeys(axis.atomsByLevel);

          return DataRow(
            cells: visibleCols.map((colKey) {
              Widget cellContent;
              switch (colKey) {
                case 'label':
                  final targetLabel =
                      axis.contextTargetLabel?.get(locale) ??
                      axis.contextTarget;
                  cellContent = ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 350),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          axis.labelI18n.get(locale) +
                              (axis.isEvaluative ? ' *' : '') +
                              (axis.allowContextualOverride ? ' **' : ''),
                          style: const TextStyle(fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
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
                                borderRadius: BorderRadius.circular(
                                  AppSpacing.s4,
                                ),
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
                                overflow: TextOverflow.ellipsis,
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
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                      ],
                    ),
                  );
                  break;
                case 'context_target':
                  final targetText =
                      axis.contextTargetLabel?.get(locale) ??
                      axis.contextTarget;
                  cellContent = ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 350),
                    child: Text(
                      targetText ?? '-',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 12,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                  break;
                case 'distribution':
                case 'atomic_breakdown':
                  cellContent = _MatrixSummaryDistributionCell(
                    breakdown: breakdown,
                    sortedKeys: sortedBreakdownKeys,
                    levelNames: axis.levelNames,
                  );
                  break;
                case 'row_explanation':
                  cellContent = ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 350),
                    child: Text(
                      axis.rowExplanation,
                      style: const TextStyle(
                        fontStyle: FontStyle.italic,
                        fontSize: 12,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                  break;
                case 'criteria':
                  cellContent = _MatrixSummaryCriteriaCell(
                    criteriaAtoms: axis.evaluatedAtoms,
                    atomsByLevel: axis.atomsByLevel,
                    sortedLevels: sortedLevels,
                    levelNames: axis.levelNames,
                  );
                  break;
                case 'quotes':
                  cellContent = _MatrixSummaryQuotesCell(
                    quoteAtoms: axis.evaluatedAtoms,
                    atomsByLevel: axis.atomsByLevel,
                    sortedLevels: sortedLevels,
                    levelNames: axis.levelNames,
                    allowContextualOverride: axis.allowContextualOverride,
                  );
                  break;
                case 'source':
                  final title = axis.citedSourceTitle;
                  final url = axis.citedSourceUrl;
                  final webCitation = axis.citedWebCitation;
                  final clustered = axis.clusteredRowSources;

                  if (title != null || url != null) {
                    cellContent = ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 350),
                      child: Padding(
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
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.primary,
                                    decoration: TextDecoration.underline,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w500,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              )
                            : Text(
                                title!,
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w500,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                      ),
                    );
                  } else if (webCitation != null && webCitation.isNotEmpty) {
                    cellContent = ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 350),
                      child: Padding(
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
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                    );
                  } else if (clustered.isNotEmpty) {
                    cellContent = ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 350),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: clustered.map((src) {
                          return Padding(
                            padding: const EdgeInsets.only(
                              bottom: AppSpacing.s2,
                            ),
                            child: Text(
                              '${src.stepName}: ${src.query}',
                              style: const TextStyle(fontSize: 10),
                              overflow: TextOverflow.ellipsis,
                            ),
                          );
                        }).toList(),
                      ),
                    );
                  } else {
                    cellContent = const Text('-');
                  }
                  break;
                case 'normalized_score':
                  cellContent = _MatrixSummaryScoreCell(
                    uiPlotRatio: axis.uiPlotRatio,
                    isNormalized: true,
                  );
                  break;
                case 'score':
                  cellContent = _MatrixSummaryScoreCell(
                    scoreLabel: axis.scoreDisplayLabel,
                    isNormalized: false,
                  );
                  break;
                default:
                  cellContent = const Text('-');
              }
              return DataCell(
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 350),
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
                ),
              );
            }).toList(),
          );
        }).toList(),
      ),
    );

    final content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        table,
        if (hasEvaluative || hasOverride) ...[
          AppSpacing.h8,
          if (hasEvaluative)
            Text(
              l10n.matrixEvaluativeAsteriskLegend,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontStyle: FontStyle.italic,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          if (hasOverride)
            Text(
              l10n.matrixOverrideAsteriskLegend,
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

class _MatrixSummaryCriteriaCell extends StatelessWidget {
  final List<ScorecardAtomDto> criteriaAtoms;
  final Map<int, List<ScorecardAtomDto>> atomsByLevel;
  final List<int> sortedLevels;
  final Map<String, String>? levelNames;

  const _MatrixSummaryCriteriaCell({
    required this.criteriaAtoms,
    required this.atomsByLevel,
    required this.sortedLevels,
    this.levelNames,
  });

  @override
  Widget build(BuildContext context) {
    if (criteriaAtoms.isEmpty) {
      return const Text('-');
    }

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 350),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: sortedLevels.map((lvl) {
          final lvlName = levelNames?[lvl.toString()] ?? '';
          final lvlAtoms = atomsByLevel[lvl] ?? [];
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
                overflow: TextOverflow.ellipsis,
              ),
              AppSpacing.h4,
              ...lvlAtoms.map((atom) {
                final displayLabel =
                    atom.chartDisplayLabel.isNotEmpty &&
                        atom.chartDisplayLabel != 'N/A'
                    ? atom.chartDisplayLabel
                    : (atom.claimLabel.isNotEmpty ? atom.claimLabel : '-');
                return Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.s4),
                  child: Text(
                    '- $displayLabel',
                    style: TextStyle(
                      fontWeight: atom.status == ExecutionStatus.passed
                          ? FontWeight.bold
                          : FontWeight.normal,
                      fontSize: 11,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                );
              }),
              AppSpacing.h4,
            ],
          );
        }).toList(),
      ),
    );
  }
}

class _MatrixSummaryQuotesCell extends StatelessWidget {
  final List<ScorecardAtomDto> quoteAtoms;
  final Map<int, List<ScorecardAtomDto>> atomsByLevel;
  final List<int> sortedLevels;
  final Map<String, String>? levelNames;
  final bool allowContextualOverride;

  const _MatrixSummaryQuotesCell({
    required this.quoteAtoms,
    required this.atomsByLevel,
    required this.sortedLevels,
    this.levelNames,
    required this.allowContextualOverride,
  });

  @override
  Widget build(BuildContext context) {
    final hasAnyQuotes = quoteAtoms.any(
      (a) =>
          a.exactQuotes.isNotEmpty ||
          (allowContextualOverride &&
              a.contextualOverride &&
              a.status == ExecutionStatus.passed),
    );

    if (!hasAnyQuotes) {
      return const Text('-');
    }

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 350),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: sortedLevels
            .where((lvl) {
              final lvlAtoms = atomsByLevel[lvl] ?? [];
              return lvlAtoms.any(
                (a) =>
                    a.exactQuotes.isNotEmpty ||
                    (allowContextualOverride &&
                        a.contextualOverride &&
                        a.status == ExecutionStatus.passed),
              );
            })
            .map((lvl) {
              final lvlName = levelNames?[lvl.toString()] ?? '';
              final lvlAtoms = atomsByLevel[lvl] ?? [];
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
                    overflow: TextOverflow.ellipsis,
                  ),
                  AppSpacing.h4,
                  ...lvlAtoms
                      .where(
                        (atom) =>
                            atom.exactQuotes.isNotEmpty ||
                            (allowContextualOverride &&
                                atom.contextualOverride &&
                                atom.status == ExecutionStatus.passed),
                      )
                      .map((atom) {
                        if (atom.exactQuotes.isNotEmpty) {
                          return Padding(
                            padding: const EdgeInsets.only(
                              bottom: AppSpacing.s4,
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                if (atom.claimLabel.trim().isNotEmpty)
                                  Padding(
                                    padding: const EdgeInsets.only(
                                      left: AppSpacing.s4,
                                      bottom: AppSpacing.s2,
                                    ),
                                    child: Text(
                                      '${atom.claimLabel.trim()}:',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w600,
                                        fontSize: 10,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ...atom.exactQuotes.map((q) {
                                  return Padding(
                                    padding: const EdgeInsets.only(
                                      left: AppSpacing.s4,
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
                                if (atom.semanticReasoning.trim().isNotEmpty)
                                  Padding(
                                    padding: const EdgeInsets.only(
                                      left: AppSpacing.s4,
                                      top: AppSpacing.s2,
                                    ),
                                    child: Text(
                                      '↳ ${atom.semanticReasoning.trim()}',
                                      style:
                                          (Theme.of(
                                                    context,
                                                  ).textTheme.bodySmall ??
                                                  const TextStyle(fontSize: 10))
                                              .copyWith(
                                                fontSize: 10,
                                                color: Theme.of(context)
                                                    .colorScheme
                                                    .onSurfaceVariant
                                                    .withValues(alpha: 0.8),
                                              ),
                                    ),
                                  ),
                              ],
                            ),
                          );
                        } else {
                          final explanation =
                              atom.semanticReasoning.trim().isNotEmpty
                              ? atom.semanticReasoning.trim()
                              : (atom.claimLabel.trim().isNotEmpty
                                    ? atom.claimLabel.trim()
                                    : '-');
                          final labelPrefix = atom.claimLabel.trim().isNotEmpty
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
      ),
    );
  }
}

class _MatrixSummaryDistributionCell extends StatelessWidget {
  final Map<String, String> breakdown;
  final List<String> sortedKeys;
  final Map<String, String>? levelNames;

  const _MatrixSummaryDistributionCell({
    required this.breakdown,
    required this.sortedKeys,
    this.levelNames,
  });

  @override
  Widget build(BuildContext context) {
    if (breakdown.isEmpty) {
      return const Text('-');
    }

    final names = levelNames ?? {};
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 350),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: sortedKeys.map((k) {
          final numStr = int.tryParse(k) != null ? int.parse(k).toString() : k;
          final hitStr = breakdown[k];
          final name = names[k] ?? 'T$k';
          return Text(
            '$numStr - $name: $hitStr',
            style: const TextStyle(fontSize: 12),
            overflow: TextOverflow.ellipsis,
          );
        }).toList(),
      ),
    );
  }
}

class _MatrixSummaryScoreCell extends StatelessWidget {
  final String? scoreLabel;
  final double? uiPlotRatio;
  final bool isNormalized;

  const _MatrixSummaryScoreCell({
    this.scoreLabel,
    this.uiPlotRatio,
    required this.isNormalized,
  });

  @override
  Widget build(BuildContext context) {
    if (isNormalized) {
      if (uiPlotRatio == null) {
        return const Text('-');
      }
      return Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.s8,
          vertical: AppSpacing.s4,
        ),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.tertiaryContainer,
          border: Border.all(
            color: Theme.of(context).colorScheme.outlineVariant,
          ),
          borderRadius: BorderRadius.circular(AppSpacing.s4),
        ),
        child: Text(
          '${(uiPlotRatio! * 100).toStringAsFixed(1)} %',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.onTertiaryContainer,
            fontSize: 12,
          ),
        ),
      );
    } else {
      if (scoreLabel == null || scoreLabel == '-') {
        return const Text('-');
      }
      return Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.s8,
          vertical: AppSpacing.s4,
        ),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primaryContainer,
          border: Border.all(
            color: Theme.of(context).colorScheme.outlineVariant,
          ),
          borderRadius: BorderRadius.circular(AppSpacing.s4),
        ),
        child: Text(
          scoreLabel!,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.onPrimaryContainer,
            fontSize: 12,
          ),
        ),
      );
    }
  }
}
