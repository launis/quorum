import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

class ScoreCard extends ConsumerWidget {
  final String label;
  final double? value;
  final double? maxValue;
  final String? description;

  const ScoreCard({
    super.key,
    required this.label,
    required this.value,
    this.maxValue,
    this.description,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final semanticColors = context.semanticColors;
    final l10n = AppLocalizations.of(context)!;

    try {
      if (label.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: ScoreCard label cannot be empty.',
        );
      }

      if (maxValue != null && (!maxValue!.isFinite || maxValue! <= 0)) {
        throw AppException.validation(
          'Fail-Fast: ScoreCard maxValue must be a finite positive number.',
        );
      }

      final effectiveMax = maxValue ?? 5.0;

      if (value != null) {
        if (!value!.isFinite || value! < 0 || value! > effectiveMax) {
          throw AppException.validation(
            'Fail-Fast: ScoreCard value must be between 0 and $effectiveMax.',
          );
        }
      }

      final cleanDescription = description?.trim();

      if (value == null) {
        return Card(
          elevation: 0,
          color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.s12),
            side: BorderSide(
              color: colorScheme.outlineVariant.withValues(alpha: 0.5),
            ),
          ),
          child: Padding(
            padding: AppSpacing.p12,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                AppSpacing.h8,
                if (cleanDescription != null &&
                    cleanDescription.isNotEmpty) ...[
                  Text(
                    cleanDescription,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant.withValues(
                        alpha: 0.5,
                      ),
                    ),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  AppSpacing.h8,
                ],
                Text(
                  l10n.dataUnavailable,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        );
      }

      final ratio = value! / effectiveMax;
      final scoreColor =
          Color.lerp(colorScheme.error, semanticColors.success, ratio) ??
          colorScheme.onSurfaceVariant;

      return Card(
        elevation: 0,
        color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
          side: BorderSide(color: colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: AppSpacing.p12,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      label,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: colorScheme.onSurfaceVariant,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  AppSpacing.w8,
                  Flexible(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.s8,
                        vertical: AppSpacing.s2,
                      ),
                      decoration: BoxDecoration(
                        color: scoreColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(AppSpacing.s12),
                        border: Border.all(
                          color: scoreColor.withValues(alpha: 0.2),
                        ),
                      ),
                      child: Text(
                        _formatScore(context, value!),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.labelLarge?.copyWith(
                          color: scoreColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              if (cleanDescription != null && cleanDescription.isNotEmpty) ...[
                AppSpacing.h8,
                Text(
                  cleanDescription,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ScoreCard',
            'VALIDATION_FAILED: Failed to render ScoreCard',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  String _formatScore(BuildContext context, double val) {
    final locale = Localizations.localeOf(context).toString();
    final fmt = NumberFormat.decimalPattern(locale);

    if (val % 1 == 0) {
      return fmt.format(val.toInt());
    }

    final decimalFmt = NumberFormat.decimalPatternDigits(
      locale: locale,
      decimalDigits: 1,
    );
    return decimalFmt.format(val);
  }
}
