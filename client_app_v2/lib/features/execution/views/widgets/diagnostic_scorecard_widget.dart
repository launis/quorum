import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/shared/widgets/global_error_view.dart';
import 'package:client_app/features/execution/controllers/scorecard_controller.dart';
import 'package:client_app/features/execution/views/widgets/matrix_row_item_widget.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// The master entrypoint component for the Diagnostic Scorecard UI.
class DiagnosticScorecardWidget extends ConsumerWidget {
  final String executionId;

  const DiagnosticScorecardWidget({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final asyncScorecard = ref.watch(scorecardControllerProvider(executionId));

    return switch (asyncScorecard) {
      AsyncData(:final value) => _buildContent(context, value, l10n),
      AsyncError(:final error, :final stackTrace) => GlobalErrorView(
        error: error,
        stackTrace: stackTrace,
        onAction: () =>
            ref.invalidate(scorecardControllerProvider(executionId)),
        actionLabel: l10n.retry,
      ),
      _ => const Center(child: CircularProgressIndicator()),
    };
  }

  Widget _buildContent(BuildContext context, var value, AppLocalizations l10n) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (value.globalAverage != null) ...[
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
                    value.globalAverage!.toStringAsFixed(2),
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
          if (value.evaluativeMatrices.isNotEmpty) ...[
            Text(
              l10n.scorecard_evaluative_matrices_title,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ...value.evaluativeMatrices.map(
              (m) => MatrixRowItemWidget(matrix: m),
            ),
            const SizedBox(height: 32),
          ],
          if (value.informationalMatrices.isNotEmpty) ...[
            Text(
              l10n.scorecard_informational_matrices_title,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            ...value.informationalMatrices.map(
              (m) => MatrixRowItemWidget(matrix: m),
            ),
            const SizedBox(height: 32),
          ],
          AtomMatrixTableWidget(
            matrices: [
              ...value.evaluativeMatrices,
              ...value.informationalMatrices,
            ],
          ),
        ],
      ),
    );
  }
}
