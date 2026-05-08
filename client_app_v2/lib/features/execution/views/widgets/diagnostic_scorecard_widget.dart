import 'package:flutter/material.dart';

import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

/// The master entrypoint component for the Diagnostic Scorecard UI.
class DiagnosticScorecardWidget extends StatelessWidget {
  final double? globalAverage;
  final List<MatrixScorecardRowDto> evaluativeMatrices;
  final List<MatrixScorecardRowDto> informationalMatrices;
  final List<String> visibleColumns;

  const DiagnosticScorecardWidget({
    super.key,
    this.globalAverage,
    required this.evaluativeMatrices,
    required this.informationalMatrices,
    required this.visibleColumns,
  });

  @override
  Widget build(BuildContext context) {
    if (visibleColumns.isEmpty) {
      return const SizedBox(); // Matrix skipped if visibleColumns is empty
    }
    if (evaluativeMatrices.isEmpty && informationalMatrices.isEmpty) {
      return const SizedBox(); // Scorecard not applicable
    }
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (globalAverage != null) ...[
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 24.0,
                vertical: 20.0,
              ),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    theme.colorScheme.primaryContainer,
                    theme.colorScheme.primaryContainer.withValues(alpha: 0.8),
                  ],
                ),
                borderRadius: BorderRadius.circular(12.0),
                border: Border.all(
                  color: theme.colorScheme.primary.withValues(alpha: 0.2),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.scorecard_global_average,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onPrimaryContainer,
                    ),
                  ),
                  Text(
                    globalAverage!.toStringAsFixed(2),
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                      color: theme.colorScheme.onPrimaryContainer,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
          ],

          AtomMatrixTableWidget(
            matrices: [...evaluativeMatrices, ...informationalMatrices],
            visibleColumns: visibleColumns,
          ),
        ],
      ),
    );
  }
}
