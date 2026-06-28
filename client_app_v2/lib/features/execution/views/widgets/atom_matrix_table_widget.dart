import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Renders the atomic level breakdown for the given matrix in a tabular format.
/// Enforces Zero-Math SDUI rules: only renders data provided by the backend DTO.
class AtomMatrixTableWidget extends ConsumerWidget {
  final List<MatrixScorecardRowDto> matrices;
  final List<String> visibleColumns;

  const AtomMatrixTableWidget({
    super.key,
    required this.matrices,
    required this.visibleColumns,
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
                                if (m.forensics?.allEvidenceRejected == true)
                                  Padding(
                                    padding: const EdgeInsets.only(left: 4.0),
                                    child: Tooltip(
                                      message: l10n.quote_rejected_warning,
                                      child: const Icon(
                                        Icons.warning,
                                        color: Colors.amber,
                                        size: 16,
                                      ),
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
                  if (m.forensics?.allEvidenceRejected == true)
                    Padding(
                      padding: const EdgeInsets.only(left: 4.0),
                      child: Tooltip(
                        message: l10n.quote_rejected_warning,
                        child: const Icon(
                          Icons.warning,
                          color: Colors.amber,
                          size: 16,
                        ),
                      ),
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
    if (m.forensics == null || m.forensics!.levelQuotes.isEmpty) {
      return const Text(
        '-',
        style: TextStyle(
          fontSize: 13,
          fontStyle: FontStyle.italic,
          color: Colors.grey,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: m.forensics!.levelQuotes.map((lq) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${lq.level} - ${lq.levelName}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 4),
              ...lq.quotes.map((q) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 4.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('- ', style: TextStyle(fontSize: 13)),
                      Expanded(
                        child: Text(
                          q.text,
                          style: TextStyle(
                            fontSize: 13,
                            decoration: q.userRejected
                                ? TextDecoration.lineThrough
                                : null,
                            color: q.userRejected
                                ? Colors.red.withValues(alpha: 0.6)
                                : null,
                          ),
                        ),
                      ),
                      if (q.isMcpVerified && !q.userRejected)
                        const Padding(
                          padding: EdgeInsets.only(left: 4.0),
                          child: Icon(
                            Icons.verified,
                            color: Colors.green,
                            size: 16,
                          ),
                        ),
                      if (!q.userRejected)
                        Padding(
                          padding: const EdgeInsets.only(left: 4.0),
                          child: InkWell(
                            onTap: () => _showRejectDialog(context, ref, q.id),
                            child: const Icon(
                              Icons.close,
                              color: Colors.red,
                              size: 16,
                            ),
                          ),
                        ),
                    ],
                  ),
                );
              }),
            ],
          ),
        );
      }).toList(),
    );
  }

  void _showRejectDialog(BuildContext context, WidgetRef ref, String quoteId) {
    final l10n = AppLocalizations.of(context)!;
    final reasonController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.reject_quote_title),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(l10n.reject_quote_confirm),
            const SizedBox(height: 16),
            TextField(
              controller: reasonController,
              decoration: InputDecoration(
                hintText: l10n.reject_quote_reason_hint,
                border: const OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(l10n.cancel),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            onPressed: () {
              final reason = reasonController.text.trim();
              final executionId =
                  ref.read(executionControllerProvider).value?['id'] as String?;
              if (executionId != null) {
                ref
                    .read(executionControllerProvider.notifier)
                    .rejectEvidenceQuote(
                      executionId,
                      quoteId,
                      reason.isNotEmpty ? reason : null,
                    );
              }
              Navigator.of(ctx).pop();
            },
            child: Text(l10n.reject_quote_title),
          ),
        ],
      ),
    );
  }
}
