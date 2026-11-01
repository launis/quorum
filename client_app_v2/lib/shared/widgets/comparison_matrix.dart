import 'dart:io';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class _ParsedComparisonRow {
  final String observation;
  final num leftScore;
  final num rightScore;
  final double delta;
  final String? leftReasoning;
  final String? rightReasoning;

  const _ParsedComparisonRow({
    required this.observation,
    required this.leftScore,
    required this.rightScore,
    required this.delta,
    this.leftReasoning,
    this.rightReasoning,
  });
}

class ComparisonMatrix extends ConsumerWidget {
  final Map<String, Object?> comparisonData;

  const ComparisonMatrix({super.key, required this.comparisonData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    try {
      final rowsRaw = comparisonData['rows'];
      if (rowsRaw == null) {
        return _buildEmptyCard(l10n);
      }
      if (rowsRaw is! List) {
        throw AppException.validation(
          'Fail-Fast: comparisonData["rows"] must be a List.',
        );
      }

      if (rowsRaw.isEmpty) {
        return _buildEmptyCard(l10n);
      }

      final leftLabelRaw = comparisonData['left_label'];
      if (leftLabelRaw is! String || leftLabelRaw.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: Missing or invalid left_label in comparisonData.',
        );
      }

      final rightLabelRaw = comparisonData['right_label'];
      if (rightLabelRaw is! String || rightLabelRaw.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: Missing or invalid right_label in comparisonData.',
        );
      }

      final parsedRows = <_ParsedComparisonRow>[];
      for (var i = 0; i < rowsRaw.length; i++) {
        final rawRow = rowsRaw[i];
        if (rawRow is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Row at index $i must be a Map<String, Object?>.',
          );
        }

        final observation = rawRow['observation'];
        if (observation is! String || observation.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid observation at row $i.',
          );
        }

        final left = rawRow['left'];
        if (left is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid left payload at row $i.',
          );
        }

        final right = rawRow['right'];
        if (right is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid right payload at row $i.',
          );
        }

        final leftScore = left['score'];
        if (leftScore is! num) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid numeric left.score at row $i.',
          );
        }

        final rightScore = right['score'];
        if (rightScore is! num) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid numeric right.score at row $i.',
          );
        }

        final deltaRaw = rawRow['delta'];
        if (deltaRaw is! num) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid numeric delta at row $i.',
          );
        }

        final leftReasoning = left['reasoning'];
        if (leftReasoning != null && leftReasoning is! String) {
          throw AppException.validation(
            'Fail-Fast: Invalid left.reasoning type at row $i.',
          );
        }

        final rightReasoning = right['reasoning'];
        if (rightReasoning != null && rightReasoning is! String) {
          throw AppException.validation(
            'Fail-Fast: Invalid right.reasoning type at row $i.',
          );
        }

        parsedRows.add(
          _ParsedComparisonRow(
            observation: observation,
            leftScore: leftScore,
            rightScore: rightScore,
            delta: deltaRaw.toDouble(),
            leftReasoning: leftReasoning as String?,
            rightReasoning: rightReasoning as String?,
          ),
        );
      }

      return Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
          side: BorderSide(color: theme.colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                l10n.sharedComparativeEvaluation,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              AppSpacing.h16,
              Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: Text(
                      l10n.lblObservation,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: theme.colorScheme.secondary,
                      ),
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Text(
                      leftLabelRaw,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: theme.colorScheme.secondary,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Text(
                      rightLabelRaw,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: theme.colorScheme.secondary,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Text(
                      l10n.sharedDeltaColumnHeader,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: theme.colorScheme.secondary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ),
              const Divider(),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: parsedRows.length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  return _buildRow(
                    context,
                    parsedRows[index],
                    leftLabelRaw,
                    rightLabelRaw,
                  );
                },
              ),
            ],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ComparisonMatrix',
            'VALIDATION_FAILED: Failed to render comparison matrix',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  Widget _buildEmptyCard(AppLocalizations l10n) {
    return Card(
      child: Padding(
        padding: AppSpacing.p16,
        child: Text(l10n.sharedNoComparisonData),
      ),
    );
  }

  Widget _buildRow(
    BuildContext context,
    _ParsedComparisonRow row,
    String leftLabel,
    String rightLabel,
  ) {
    final theme = Theme.of(context);
    final hasLeftReasoning =
        row.leftReasoning != null && row.leftReasoning!.isNotEmpty;
    final hasRightReasoning =
        row.rightReasoning != null && row.rightReasoning!.isNotEmpty;

    return Semantics(
      excludeSemantics: Platform.isWindows,
      child: ExpansionTile(
        title: Row(
          children: [
            Expanded(
              flex: 3,
              child: Text(
                row.observation.toUpperCase(),
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Expanded(
              flex: 2,
              child: Text(
                row.leftScore.toString(),
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Expanded(
              flex: 2,
              child: Text(
                row.rightScore.toString(),
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Expanded(flex: 2, child: _renderDelta(context, row.delta)),
          ],
        ),
        shape: const Border(),
        childrenPadding: AppSpacing.p12,
        children: [
          if (hasLeftReasoning)
            _reasoningBlock(context, leftLabel, row.leftReasoning!),
          if (hasLeftReasoning && hasRightReasoning) AppSpacing.h8,
          if (hasRightReasoning)
            _reasoningBlock(context, rightLabel, row.rightReasoning!),
        ],
      ),
    );
  }

  Widget _renderDelta(BuildContext context, double delta) {
    final theme = Theme.of(context);
    if (delta == 0) {
      return Center(
        child: Text(
          '=',
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      );
    }
    final isPos = delta > 0;
    final color = isPos
        ? context.semanticColors.success
        : theme.colorScheme.error;
    final icon = isPos ? Icons.arrow_upward : Icons.arrow_downward;

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: AppSpacing.s12, color: color),
        Flexible(
          child: Text(
            delta.abs().toStringAsFixed(1),
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _reasoningBlock(BuildContext context, String label, String text) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label:',
          style: theme.textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(text, style: theme.textTheme.bodySmall),
      ],
    );
  }
}
