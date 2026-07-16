import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/human_override_dialog.dart';
import 'package:client_app/theme/app_colors.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

/// Renders the atomic level breakdown for the given matrix in a tabular format.
/// Enforces Zero-Math SDUI rules: only renders data provided by the backend DTO.
class AtomMatrixTableWidget extends ConsumerWidget {
  final List<MatrixScorecardRowDto> matrices;
  final List<String> visibleColumns;
  final String executionId;

  const AtomMatrixTableWidget({
    super.key,
    required this.matrices,
    required this.visibleColumns,
    required this.executionId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    // Filter matrices that actually have level breakdown
    final tableMatrices = matrices
        .where((m) => m.levelBreakdown != null && m.levelBreakdown!.isNotEmpty)
        .toList();
    if (tableMatrices.isEmpty || visibleColumns.isEmpty) {
      return const SizedBox();
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        // Macro-Breakpoint standard: if too small, use ListView pattern
        final isSmallScreen = constraints.maxWidth < 600;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              l10n.scorecard_matrix_summary,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: theme.colorScheme.outlineVariant),
                borderRadius: BorderRadius.circular(8.0),
              ),
              child: isSmallScreen
                  ? _buildMobileList(context, ref, tableMatrices, theme)
                  : _buildDataTable(context, ref, tableMatrices, theme),
            ),
            if (tableMatrices.any((m) => m.isEvaluative)) ...[
              const SizedBox(height: 8),
              Text(
                l10n.matrixEvaluativeAsteriskLegend,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontStyle: FontStyle.italic,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ],
        );
      },
    );
  }

  Widget _buildDataTable(
    BuildContext context,
    WidgetRef ref,
    List<MatrixScorecardRowDto> tableMatrices,
    ThemeData theme,
  ) {
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          color: theme.colorScheme.surfaceContainerHighest,
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Row(
            children: [
              if (visibleColumns.contains('label'))
                Expanded(
                  flex: 3,
                  child: Text(
                    l10n.lblLogicMatrix,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              if (visibleColumns.contains('distribution') ||
                  visibleColumns.contains('atomic_breakdown'))
                Expanded(
                  flex: 3,
                  child: Text(
                    l10n.atomicBreakdownTitle,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              if (visibleColumns.contains('row_explanation'))
                Expanded(
                  flex: 3,
                  child: Text(
                    l10n.rowExplanationTitle,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              if (visibleColumns.contains('quotes'))
                const Expanded(
                  flex: 3,
                  child: Text(
                    'Lainaukset (quotes)',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              if (visibleColumns.contains('normalized_score'))
                Expanded(
                  flex: 1,
                  child: Text(
                    l10n.normalizedScore,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              if (visibleColumns.contains('score'))
                Expanded(
                  flex: 1,
                  child: Text(
                    l10n.score,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
            ],
          ),
        ),
        const Divider(height: 1),
        ...tableMatrices
            .map((m) {
              final levelMap = m.levelBreakdown!;
              final levelNames = m.levelNames ?? {};
              final sortedLevels = levelMap.keys.toList()
                ..sort((a, b) {
                  final numA = double.tryParse(a) ?? 0;
                  final numB = double.tryParse(b) ?? 0;
                  return numB.compareTo(numA);
                });

              return Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16.0,
                  vertical: 12.0,
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (visibleColumns.contains('label'))
                      Expanded(
                        flex: 3,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Wrap(
                              crossAxisAlignment: WrapCrossAlignment.center,
                              children: [
                                Text(
                                  (Localizations.localeOf(
                                                context,
                                              ).languageCode ==
                                              'fi'
                                          ? (m.labelI18n.get('fi'))
                                          : (m.labelI18n.get('en'))) +
                                      (m.isEvaluative ? ' *' : ''),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            if (m.description != null &&
                                m.description!.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(top: 4.0),
                                child: Text(
                                  m.description!,
                                  style: const TextStyle(
                                    fontSize: 10,
                                    color: Colors.black54,
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    if (visibleColumns.contains('distribution') ||
                        visibleColumns.contains('atomic_breakdown'))
                      Expanded(
                        flex: 3,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: sortedLevels.map((lvl) {
                            final display = levelMap[lvl]!;
                            final name = levelNames[lvl] ?? 'T$lvl';
                            final numLvl = double.tryParse(lvl)?.toInt() ?? lvl;
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 2.0),
                              child: Text(
                                '$numLvl - $name: $display',
                                style: const TextStyle(fontSize: 12),
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    if (visibleColumns.contains('row_explanation'))
                      Expanded(
                        flex: 3,
                        child: Text(
                          m.rowExplanation,
                          style: const TextStyle(
                            fontSize: 13,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    if (visibleColumns.contains('quotes'))
                      Expanded(
                        flex: 3,
                        child: _buildQuotesColumn(context, ref, m),
                      ),
                    if (visibleColumns.contains('normalized_score'))
                      Expanded(
                        flex: 1,
                        child: Text(
                          m.normalizedScore != null
                              ? '${m.normalizedScore!.toStringAsFixed(1)} %'
                              : '-',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ),
                    if (visibleColumns.contains('score'))
                      Expanded(
                        flex: 1,
                        child: Text(
                          m.score == null
                              ? '-'
                              : '${m.score!.toStringAsFixed(1)} / ${m.scaleMax?.toStringAsFixed(1) ?? '-'}',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                  ],
                ),
              );
            })
            .expand((widget) => [widget, const Divider(height: 1)])
            .toList()
          ..removeLast(),
      ],
    );
  }

  Widget _buildMobileList(
    BuildContext context,
    WidgetRef ref,
    List<MatrixScorecardRowDto> tableMatrices,
    ThemeData theme,
  ) {
    final l10n = AppLocalizations.of(context)!;
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: tableMatrices.length,
      separatorBuilder: (context, index) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final m = tableMatrices[index];
        final sortedLevels = m.levelBreakdown!.keys.toList()
          ..sort((a, b) {
            final numA = double.tryParse(a) ?? 0;
            final numB = double.tryParse(b) ?? 0;
            return numB.compareTo(numA);
          });

        return ExpansionTile(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text(
                    (Localizations.localeOf(context).languageCode == 'fi'
                            ? (m.labelI18n.get('fi'))
                            : (m.labelI18n.get('en'))) +
                        (m.isEvaluative ? ' *' : ''),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              if (m.description != null && m.description!.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 4.0),
                  child: Text(
                    m.description!,
                    style: const TextStyle(
                      fontSize: 10,
                      color: Colors.black54,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
            ],
          ),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (visibleColumns.contains('score'))
                Text(
                  m.score == null
                      ? '${l10n.score}: -'
                      : '${l10n.score}: ${m.score!.toStringAsFixed(1)} / ${m.scaleMax?.toStringAsFixed(1) ?? '-'}',
                ),
              if (visibleColumns.contains('normalized_score') &&
                  m.normalizedScore != null)
                Text(
                  '100 %: ${m.normalizedScore!.toStringAsFixed(1)} %',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
              if (visibleColumns.contains('row_explanation'))
                Padding(
                  padding: const EdgeInsets.only(top: 4.0),
                  child: Text(
                    m.rowExplanation,
                    style: const TextStyle(
                      fontSize: 13,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              if (visibleColumns.contains('quotes'))
                Padding(
                  padding: const EdgeInsets.only(top: 8.0),
                  child: _buildQuotesColumn(context, ref, m),
                ),
            ],
          ),
          children:
              (visibleColumns.contains('distribution') ||
                  visibleColumns.contains('atomic_breakdown'))
              ? sortedLevels.map((lvl) {
                  final display = m.levelBreakdown![lvl]!;
                  final name = m.levelNames?[lvl] ?? 'T$lvl';
                  final numLvl = double.tryParse(lvl)?.toInt() ?? lvl;
                  return ListTile(
                    dense: true,
                    title: Text('$numLvl - $name: $display'),
                  );
                }).toList()
              : [],
        );
      },
    );
  }

  Widget _buildQuotesColumn(
    BuildContext context,
    WidgetRef ref,
    MatrixScorecardRowDto m,
  ) {
    if (m.atomsByLevel.isEmpty) {
      return const Text(
        '-',
        style: TextStyle(
          fontSize: 13,
          fontStyle: FontStyle.italic,
          color: Colors.grey,
        ),
      );
    }

    final sortedLevels = m.atomsByLevel.keys.toList()
      ..sort((a, b) => b.compareTo(a));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: sortedLevels.map((level) {
        final atoms = m.atomsByLevel[level]!;
        final levelName = m.levelNames?['$level'] ?? 'T$level';

        return Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '$level - $levelName',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              Builder(
                builder: (context) {
                  final itemsToRender = <Widget>[];

                  for (final atom in atoms) {
                    final lowerStatus = atom.status?.toLowerCase() ?? '';
                    // Filter non-renderable atoms from Display Tier
                    final isSkipped =
                        lowerStatus == 'skipped' ||
                        lowerStatus == 'none' ||
                        lowerStatus == 'dlq' ||
                        atom.semanticReasoning.startsWith(
                          'Chunk Processing Failed',
                        );
                    if (isSkipped) continue;

                    bool hasOverride = atom.humanOverride != null;
                    final isPass = hasOverride
                        ? (atom.humanOverride!.newStatus.toUpperCase() ==
                                  'PASS' ||
                              atom.humanOverride!.newStatus.toUpperCase() ==
                                  'CONTESTED')
                        : (atom.status?.toUpperCase() == 'PASS' ||
                              atom.status?.toUpperCase() == 'CONTESTED');

                    // 1. AI Evidence rendering
                    final aiQuotes = _buildQuoteWidgets(
                      atom.exactQuotes,
                      isPass,
                      hasOverride,
                    ); // Fade if overridden

                    // 2. Human Override rendering
                    Widget? overrideBox;
                    if (hasOverride) {
                      final humanQuotes = _buildQuoteWidgets(
                        atom.humanOverride!.evidenceQuotes,
                        isPass,
                        false,
                      );
                      overrideBox = Container(
                        margin: const EdgeInsets.only(top: 8.0, bottom: 4.0),
                        padding: const EdgeInsets.all(8.0),
                        decoration: BoxDecoration(
                          color: Colors.amber.withValues(alpha: 0.1),
                          border: Border.all(color: Colors.amber.shade300),
                          borderRadius: BorderRadius.circular(4.0),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(
                                  Icons.gavel,
                                  size: 16,
                                  color: Colors.amber,
                                ),
                                const SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    "👨‍⚖️ Ihmisen päätös (EU AI Act)",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.amber.shade900,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              "Perustelu: ${atom.humanOverride!.reason}",
                              style: TextStyle(
                                fontStyle: FontStyle.italic,
                                color: Colors.amber.shade900,
                                fontSize: 12,
                              ),
                            ),
                            if (humanQuotes.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(top: 6.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: humanQuotes,
                                ),
                              ),
                          ],
                        ),
                      );
                    }

                    itemsToRender.add(
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('- ', style: TextStyle(fontSize: 13)),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          atom.chartDisplayLabel,
                                          style: TextStyle(
                                            fontSize: 13,
                                            fontWeight: isPass
                                                ? FontWeight.bold
                                                : FontWeight.normal,
                                            color: AppColors.fromIntent(
                                              atom.visualIntent,
                                            ),
                                          ),
                                        ),
                                      ),
                                      IconButton(
                                        icon: const Icon(Icons.gavel, size: 16),
                                        tooltip: 'Yliohjaa päätös',
                                        onPressed: () {
                                          showDialog(
                                            context: context,
                                            builder: (ctx) =>
                                                HumanOverrideDialog(
                                                  atom: atom,
                                                  executionId: executionId,
                                                ),
                                          ).then((wasSaved) {
                                            if (wasSaved == true) {
                                              // Triggers a refresh of the report view optimally
                                              // by invalidating the reportProvider.
                                              // In a real app we'd dispatch an event or use ref.invalidate
                                              ScaffoldMessenger.of(
                                                context,
                                              ).showSnackBar(
                                                const SnackBar(
                                                  content: Text(
                                                    'Päätös yliohjattu! Päivitä raportti nähdäksesi muutokset.',
                                                  ),
                                                ),
                                              );
                                            }
                                          });
                                        },
                                        constraints: const BoxConstraints(
                                          minWidth: 24,
                                          minHeight: 24,
                                        ),
                                        padding: EdgeInsets.zero,
                                      ),
                                    ],
                                  ),
                                  if (aiQuotes.isNotEmpty)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 2.0),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: aiQuotes,
                                      ),
                                    ),
                                  if (atom.semanticReasoning.isNotEmpty)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 4.0),
                                      child: Text(
                                        '${AppLocalizations.of(context)!.lblReasoning}: ${atom.semanticReasoning}',
                                        style: TextStyle(
                                          fontSize: 12,
                                          fontStyle: FontStyle.italic,
                                          color: isPass
                                              ? (hasOverride
                                                    ? Colors.black26
                                                    : Colors.black54)
                                              : (hasOverride
                                                    ? Colors.black26
                                                    : Colors.black38),
                                        ),
                                      ),
                                    ),
                                  if (overrideBox != null) overrideBox,
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }

                  if (itemsToRender.isEmpty) {
                    return const Padding(
                      padding: EdgeInsets.only(bottom: 4.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('- ', style: TextStyle(fontSize: 13)),
                          Expanded(
                            child: Text(
                              '-',
                              style: TextStyle(
                                fontSize: 13,
                                fontStyle: FontStyle.italic,
                                color: Colors.grey,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }

                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: itemsToRender,
                  );
                },
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  List<Widget> _buildQuoteWidgets(
    List<QuoteEvidenceDto> quotes,
    bool isPass,
    bool isFaded,
  ) {
    final uniqueQuotes = <String>{};
    final parsedQuotes = <Widget>[];
    for (final q in quotes) {
      final disp = q.displayName ?? q.sourceId;
      final uniqueKey = '${disp ?? 'unknown'}::${q.quoteText}';
      if (!uniqueQuotes.add(uniqueKey)) continue;

      parsedQuotes.add(
        Padding(
          padding: const EdgeInsets.only(top: 4.0),
          child: RichText(
            text: TextSpan(
              style: TextStyle(
                fontSize: 13,
                color: isFaded ? Colors.black38 : Colors.black87,
              ),
              children: [
                if (disp != null && disp.isNotEmpty) ...[
                  WidgetSpan(
                    alignment: PlaceholderAlignment.middle,
                    child: Container(
                      margin: const EdgeInsets.only(right: 6.0),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6.0,
                        vertical: 2.0,
                      ),
                      decoration: BoxDecoration(
                        color: isFaded
                            ? Colors.grey.withValues(alpha: 0.1)
                            : Colors.blue.withValues(alpha: 0.1),
                        border: Border.all(
                          color: isFaded
                              ? Colors.grey.withValues(alpha: 0.3)
                              : Colors.blue.withValues(alpha: 0.3),
                        ),
                        borderRadius: BorderRadius.circular(4.0),
                      ),
                      child: Text(
                        disp.toUpperCase(),
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: isFaded ? Colors.grey[600] : Colors.blue[800],
                        ),
                      ),
                    ),
                  ),
                ],
                TextSpan(
                  text: q.quoteText,
                  style: isPass && !isFaded
                      ? const TextStyle(fontWeight: FontWeight.bold)
                      : null,
                ),
              ],
            ),
          ),
        ),
      );
    }
    return parsedQuotes;
  }
}
