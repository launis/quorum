import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Renders a single matrix row enforcing the Zero-Math UI mandate.
class MatrixRowItemWidget extends StatelessWidget {
  final MatrixScorecardRowDto matrix;

  const MatrixRowItemWidget({super.key, required this.matrix});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isEval = matrix.isEvaluative;
    final isDlq = matrix.tdaState is Dlq;

    final bgColor = isDlq
        ? Colors.grey.shade200
        : isEval
        ? theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3)
        : theme.colorScheme.surfaceContainerLow;

    return Container(
      margin: const EdgeInsets.only(bottom: AppSpacing.s8),
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s16,
        vertical: AppSpacing.s12,
      ),
      decoration: BoxDecoration(
        color: bgColor,
        border: Border.all(
          color: isDlq
              ? Colors.grey.shade400
              : isEval
              ? theme.colorScheme.outlineVariant
              : theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
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
                          ? (matrix.labelI18n.get('fi'))
                          : (matrix.labelI18n.get('en'))) +
                      (isEval ? ' *' : ''),
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: isEval ? FontWeight.bold : FontWeight.w600,
                  ),
                ),
                if (matrix.rowExplanation.isNotEmpty) ...[
                  AppSpacing.h8,
                  Text(
                    AppLocalizations.of(context)!.xaiJustification,
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isDlq
                          ? Colors.grey.shade700
                          : theme.colorScheme.primary,
                    ),
                  ),
                  AppSpacing.h2,
                  Text(
                    matrix.rowExplanation,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: isDlq
                          ? Colors.grey.shade800
                          : theme.colorScheme.onSurfaceVariant,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
                if (isDlq) ...[
                  AppSpacing.h8,
                  Tooltip(
                    message: (matrix.tdaState as Dlq).backendTrace,
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.warning_amber_rounded,
                          size: 16,
                          color: Colors.orange.shade800,
                        ),
                        AppSpacing.w4,
                        Text(
                          (matrix.tdaState as Dlq).userReason,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: Colors.orange.shade900,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                AppSpacing.h8,
                _buildLevelRow(context),
                if (matrix.innerSduiBlocks.isNotEmpty) ...[
                  AppSpacing.h12,
                  SduiBlocksRenderer(blocks: matrix.innerSduiBlocks),
                ],
              ],
            ),
          ),
          AppSpacing.w16,
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

    // Dynamic level rendering instead of hardcoded 1-6
    final keys = levelMap.keys.toList()..sort();

    return Wrap(
      spacing: AppSpacing.s8,
      runSpacing: AppSpacing.s4,
      children: keys.map((k) {
        final display = levelMap[k]!;

        return Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s6,
            vertical: AppSpacing.s2,
          ),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            border: Border.all(color: theme.colorScheme.outlineVariant),
            borderRadius: BorderRadius.circular(AppSpacing.s4),
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
              AppSpacing.w4,
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
