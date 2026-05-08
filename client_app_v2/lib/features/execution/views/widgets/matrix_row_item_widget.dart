import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Renders a single matrix row enforcing the Zero-Math UI mandate.
class MatrixRowItemWidget extends StatelessWidget {
  final MatrixScorecardRowDto matrix;

  const MatrixRowItemWidget({super.key, required this.matrix});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isEval = matrix.isEvaluative;

    return Container(
      margin: const EdgeInsets.only(bottom: 8.0),
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      decoration: BoxDecoration(
        color: isEval
            ? theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3)
            : theme.colorScheme.surfaceContainerLow,
        border: Border.all(
          color: isEval
              ? theme.colorScheme.outlineVariant
              : theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  (Localizations.localeOf(context).languageCode == 'fi'
                          ? matrix.labelFi
                          : matrix.labelEn) +
                      (isEval ? ' *' : ''),
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: isEval ? FontWeight.bold : FontWeight.w600,
                  ),
                ),
                if (matrix.rowExplanation.isNotEmpty) ...[
                  const SizedBox(height: 8.0),
                  Text(
                    AppLocalizations.of(context)!.xaiJustification,
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 2.0),
                  Text(
                    matrix.rowExplanation,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
                const SizedBox(height: 8.0),
                _buildLevelRow(context),
              ],
            ),
          ),
          const SizedBox(width: 16.0),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                matrix.score == null
                    ? '-'
                    : '${matrix.score!.toStringAsFixed(1)} / ${matrix.scaleMax?.toStringAsFixed(1) ?? '-'}',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (matrix.normalizedScore != null)
                Text(
                  '${matrix.normalizedScore!.toStringAsFixed(1)} %',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: isEval
                        ? theme.colorScheme.primary
                        : theme.colorScheme.secondary,
                  ),
                ),
              if (matrix.trueAtoms != null &&
                  matrix.totalAtoms != null &&
                  matrix.totalAtoms! > 0)
                Text(
                  '${matrix.trueAtoms} / ${matrix.totalAtoms}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLevelRow(BuildContext context) {
    final theme = Theme.of(context);
    final levelMap = matrix.levelBreakdown ?? {};

    // Epic 24: Dynamic level rendering instead of hardcoded 1-6
    final keys = levelMap.keys.toList()..sort();

    return Wrap(
      spacing: 8.0,
      runSpacing: 4.0,
      children: keys.map((k) {
        final display = levelMap[k]!;

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 6.0, vertical: 2.0),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            border: Border.all(color: theme.colorScheme.outlineVariant),
            borderRadius: BorderRadius.circular(4.0),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                matrix.levelNames?[k] ?? 'T$k',
                style: theme.textTheme.labelSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 4),
              Text(
                display,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: display != '-'
                      ? FontWeight.bold
                      : FontWeight.normal,
                  color: display != '-'
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
