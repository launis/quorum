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
              l10n.atomicBreakdownTitle,
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
    // Extract unique levels across all matrices to build columns
    final allLevels = <String>{};
    for (var m in tableMatrices) {
      allLevels.addAll(m.levelBreakdown!.keys);
    }
    final sortedLevels = allLevels.toList()..sort();

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowColor: WidgetStatePropertyAll(
          theme.colorScheme.surfaceContainerHighest,
        ),
        columns: [
          const DataColumn(label: Text('Matrix')),
          const DataColumn(label: Text('Total Hits')),
          ...sortedLevels.map((lvl) => DataColumn(label: Text(lvl))),
        ],
        rows: tableMatrices.map((m) {
          final levelMap = m.levelBreakdown!;
          return DataRow(
            cells: [
              DataCell(
                SizedBox(
                  width: 200,
                  child: Text(
                    m.labelFi, // Or locale selected...
                    style: const TextStyle(fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
              DataCell(
                Text(
                  (m.trueAtoms != null && m.totalAtoms != null)
                      ? '${m.trueAtoms} / ${m.totalAtoms}'
                      : '-',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              ...sortedLevels.map((lvl) {
                final stats = levelMap[lvl];
                if (stats == null) return const DataCell(Text('-'));
                final hits = stats['hits'] ?? stats['true_atoms'] ?? 0;
                final total = stats['total'] ?? stats['total_atoms'] ?? 0;
                return DataCell(Text('$hits / $total'));
              }),
            ],
          );
        }).toList(),
      ),
    );
  }

  Widget _buildMobileList(
    BuildContext context,
    List<MatrixScorecardRowDto> tableMatrices,
    ThemeData theme,
  ) {
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
            m.labelFi,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text(
            (m.trueAtoms != null && m.totalAtoms != null)
                ? 'Total Hits: ${m.trueAtoms} / ${m.totalAtoms}'
                : '',
          ),
          children: sortedLevels.map((lvl) {
            final stats = m.levelBreakdown![lvl]!;
            final hits = stats['hits'] ?? stats['true_atoms'] ?? 0;
            final total = stats['total'] ?? stats['total_atoms'] ?? 0;
            return ListTile(
              dense: true,
              title: Text(lvl),
              trailing: Text(
                '$hits / $total',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            );
          }).toList(),
        );
      },
    );
  }
}
