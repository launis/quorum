import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class UnifiedMetricGauge extends ConsumerWidget {
  final String label;
  final double value;
  final double max;
  final String description;
  final String? descriptionSecondary;
  final String displayValue;
  final Color? color;
  final List<String>? axisLabels;
  final bool isOrdinal;

  static const int _labelFlex = 3;
  static const int _barFlex = 5;
  static const int _valueFlex = 2;
  static const double _segmentMarginHorizontal = 1.0;
  static const double _dialogIconSize = 20.0;

  const UnifiedMetricGauge({
    super.key,
    required this.label,
    required this.value,
    required this.max,
    required this.description,
    this.descriptionSecondary,
    required this.displayValue,
    this.color,
    this.axisLabels,
    this.isOrdinal = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    try {
      if (label.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: UnifiedMetricGauge requires a non-empty label.',
        );
      }
      if (displayValue.trim().isEmpty) {
        throw AppException.validation(
          "Fail-Fast: UnifiedMetricGauge requires a non-empty displayValue for '$label'.",
        );
      }
      if (description.trim().isEmpty) {
        throw AppException.validation(
          "Fail-Fast: UnifiedMetricGauge requires a non-empty description for '$label'.",
        );
      }
      if (max.isNaN || max.isInfinite || max <= 0) {
        throw AppException.validation(
          "Fail-Fast: UnifiedMetricGauge '$label' requires finite max > 0, got $max.",
        );
      }
      if (value.isNaN || value.isInfinite || value < 0 || value > max) {
        throw AppException.validation(
          "Fail-Fast: UnifiedMetricGauge '$label' value $value is out of bounds [0, $max].",
        );
      }

      final effectiveColor = color ?? colorScheme.primary;
      final int totalSegments = max.toInt();
      final int filledSegments = value.toInt();
      final currentAxisLabels = axisLabels;

      final mainRow = Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.s4),
        child: Row(
          children: [
            Expanded(
              flex: _labelFlex,
              child: Tooltip(
                message: description,
                waitDuration: AppDurations.medium,
                showDuration: AppDurations.display,
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: colorScheme.onSurface,
                  ),
                ),
              ),
            ),
            AppSpacing.w8,
            Expanded(
              flex: _barFlex,
              child: SizedBox(
                height: AppSpacing.s12,
                child: Row(
                  children: List.generate(totalSegments, (index) {
                    final isFilled = isOrdinal
                        ? (index == filledSegments - 1)
                        : (index < filledSegments);
                    return Expanded(
                      child: Container(
                        margin: const EdgeInsets.symmetric(
                          horizontal: _segmentMarginHorizontal,
                        ),
                        decoration: BoxDecoration(
                          color: isFilled
                              ? effectiveColor
                              : colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(AppSpacing.s2),
                        ),
                      ),
                    );
                  }),
                ),
              ),
            ),
            AppSpacing.w12,
            Expanded(
              flex: _valueFlex,
              child: Text(
                displayValue,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.end,
                style: textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: colorScheme.onSurface,
                ),
              ),
            ),
            AppSpacing.w8,
            _buildHelpTrigger(context, l10n, colorScheme),
          ],
        ),
      );

      if (currentAxisLabels == null || currentAxisLabels.isEmpty) {
        return mainRow;
      }

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          mainRow,
          Row(
            children: [
              const Expanded(flex: _labelFlex, child: SizedBox()),
              AppSpacing.w8,
              Expanded(
                flex: _barFlex,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: _buildAlignedLabels(
                    context,
                    currentAxisLabels,
                    totalSegments,
                  ),
                ),
              ),
              AppSpacing.w12,
              const Expanded(flex: _valueFlex, child: SizedBox()),
              AppSpacing.w8,
              AppSpacing.w16,
            ],
          ),
        ],
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'UnifiedMetricGauge',
            'VALIDATION_FAILED: Failed to render UnifiedMetricGauge',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  Widget _buildHelpTrigger(
    BuildContext context,
    AppLocalizations l10n,
    ColorScheme colorScheme,
  ) {
    return Tooltip(
      message: l10n.sharedMoreInfoTooltip,
      child: InkWell(
        mouseCursor: SystemMouseCursors.click,
        borderRadius: BorderRadius.circular(AppSpacing.s4),
        onTap: () => _showHelpDialog(context),
        child: Icon(
          Icons.help_outline,
          size: AppSpacing.s16,
          color: colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }

  void _showHelpDialog(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;
    final secondaryText = descriptionSecondary;

    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.info_outline,
              size: _dialogIconSize,
              color: colorScheme.primary,
            ),
            AppSpacing.w8,
            Expanded(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(description, style: textTheme.bodyMedium),
            if (secondaryText != null && secondaryText.trim().isNotEmpty) ...[
              AppSpacing.h12,
              const Divider(),
              AppSpacing.h8,
              Text(
                secondaryText,
                style: textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(l10n.sharedOk),
          ),
        ],
      ),
    );
  }

  List<Widget> _buildAlignedLabels(
    BuildContext context,
    List<String> labels,
    int segmentCount,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    if (labels.length == segmentCount) {
      return labels
          .map(
            (l) => Expanded(
              child: Text(
                l,
                maxLines: 1,
                textAlign: TextAlign.center,
                overflow: TextOverflow.ellipsis,
                style: textTheme.labelSmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          )
          .toList();
    }

    return labels
        .map(
          (l) => Flexible(
            child: Text(
              l,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: textTheme.labelSmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        )
        .toList();
  }
}
