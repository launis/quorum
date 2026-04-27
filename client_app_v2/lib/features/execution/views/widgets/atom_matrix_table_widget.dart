import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Renders the atomic level breakdown for the given matrix in a tabular format.
/// Enforces Zero-Math SDUI rules: only renders data provided by the backend DTO.
class AtomMatrixTableWidget extends StatelessWidget {
  final List<MatrixScorecardRowDto> matrices;

  const AtomMatrixTableWidget({super.key, required this.matrices});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    // Filter matrices that actually have level breakdown
    final tableMatrices = matrices
        .where((m) => m.levelBreakdown != null && m.levelBreakdown!.isNotEmpty)
        .toList();
    if (tableMatrices.isEmpty) {
      return const SizedBox.shrink();
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
                  ? _buildMobileList(context, tableMatrices, theme)
                  : _buildDataTable(context, tableMatrices, theme),
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
              Expanded(
                flex: 2,
                child: Text(
                  l10n.lblLogicMatrix,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                flex: 1,
                child: Text(
                  l10n.score,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                flex: 2,
                child: Text(
                  l10n.scorecard_matrix_summary,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                flex: 4,
                child: Text(
                  l10n.xaiJustification,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              const Expanded(
                flex: 1,
                child: Text(
                  '100 %',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
        const Divider(height: 1),
        ...tableMatrices.map((m) {
          final levelMap = m.levelBreakdown!;
          final levelNames = m.levelNames ?? {};
          final sortedLevels = levelMap.keys.toList()..sort();

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 2,
                  child: Text(
                    (Localizations.localeOf(context).languageCode == 'fi'
                            ? m.labelFi
                            : m.labelEn) +
                        (m.isEvaluative ? ' *' : ''),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Expanded(
                  flex: 1,
                  child: Text(
                    '${m.score.toStringAsFixed(1)} / ${m.scaleMax?.toStringAsFixed(1) ?? '-'}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: sortedLevels.map((lvl) {
                      final display = levelMap[lvl]!;
                      final name = levelNames[lvl] ?? 'T$lvl';
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 2.0),
                        child: Text(
                          '$name: $display',
                          style: const TextStyle(fontSize: 12),
                        ),
                      );
                    }).toList(),
                  ),
                ),
                Expanded(
                  flex: 4,
                  child: Text(
                    m.justification,
                    style: const TextStyle(fontStyle: FontStyle.italic),
                  ),
                ),
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
              ],
            ),
          );
        }).expand((widget) => [widget, const Divider(height: 1)]).toList()..removeLast(),
      ],
    );
  }

  Widget _buildMobileList(
    BuildContext context,
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
        final sortedLevels = m.levelBreakdown!.keys.toList()..sort();

        return ExpansionTile(
          title: Text(
            (Localizations.localeOf(context).languageCode == 'fi'
                    ? m.labelFi
                    : m.labelEn) +
                (m.isEvaluative ? ' *' : ''),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${l10n.score}: ${m.score.toStringAsFixed(1)} / ${m.scaleMax?.toStringAsFixed(1) ?? '-'}',
              ),
              if (m.normalizedScore != null)
                Text(
                  '100 %: ${m.normalizedScore!.toStringAsFixed(1)} %',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
              if (m.justification.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  m.justification,
                  style: const TextStyle(
                    fontStyle: FontStyle.italic,
                    fontSize: 13,
                  ),
                ),
              ],
            ],
          ),
          children: sortedLevels.map((lvl) {
            final display = m.levelBreakdown![lvl]!;
            final name = m.levelNames?[lvl] ?? 'T$lvl';
            return ListTile(
              dense: true,
              title: Text(name),
              trailing: Text(
                display,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            );
          }).toList(),
        );
      },
    );
  }
}
