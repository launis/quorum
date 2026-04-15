import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

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
                  matrix.labelFi,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: isEval ? FontWeight.bold : FontWeight.w600,
                  ),
                ),
                if (matrix.justification.isNotEmpty) ...[
                  const SizedBox(height: 4.0),
                  Text(
                    matrix.justification,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 16.0),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (matrix.normalizedScore != null)
                Text(
                  '${matrix.normalizedScore!.toStringAsFixed(1)} / ${matrix.scaleMax?.toStringAsFixed(1) ?? '1.0'}',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: isEval
                        ? theme.colorScheme.primary
                        : theme.colorScheme.secondary,
                  ),
                )
              else
                Text(
                  matrix.score.toStringAsFixed(1),
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              if (matrix.trueAtoms != null &&
                  matrix.totalAtoms != null &&
                  matrix.totalAtoms! > 0)
                Text(
                  '${matrix.trueAtoms} / ${matrix.totalAtoms} Hits',
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
}
