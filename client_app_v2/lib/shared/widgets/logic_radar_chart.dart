import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// A Polar 3D connected Radar (Spider) chart visualizing pre-computed SDUI metrics across 3+ dimensions.
class LogicRadarChart extends ConsumerWidget {
  const LogicRadarChart({super.key, required this.axes});

  final List<MatrixScorecardRowDto> axes;

  static const int _minRadarAxesCount = 3;
  static const int _defaultTickCount = 5;
  static const double _ratioMin = 0.0;
  static const double _ratioMax = 1.0;

  void _validateAxes(String locale) {
    if (axes.length < _minRadarAxesCount) {
      throw AppException.validation(
        'Fail-Fast: LogicRadarChart requires at least $_minRadarAxesCount axes, got ${axes.length}.',
      );
    }

    for (var i = 0; i < axes.length; i++) {
      final axis = axes[i];
      if (axis.blockId.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: LogicRadarChart axis[$i] blockId cannot be empty.',
        );
      }
      if (axis.name.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: LogicRadarChart axis[$i] name cannot be empty.',
        );
      }
      axis.labelI18n.get(locale);

      final hasScore =
          axis.score != null && !axis.score!.isNaN && !axis.score!.isInfinite;
      final hasPlotRatio =
          axis.uiPlotRatio != null &&
          !axis.uiPlotRatio!.isNaN &&
          !axis.uiPlotRatio!.isInfinite;

      if (!hasScore && !hasPlotRatio) {
        throw AppException.validation(
          'Fail-Fast: LogicRadarChart axis[$i] requires a valid score or uiPlotRatio.',
        );
      }

      if (hasPlotRatio &&
          (axis.uiPlotRatio! < _ratioMin || axis.uiPlotRatio! > _ratioMax)) {
        throw AppException.validation(
          'Fail-Fast: LogicRadarChart axis[$i] uiPlotRatio must be within [0.0, 1.0].',
        );
      }

      if (axis.scaleMin != null &&
          axis.scaleMax != null &&
          (axis.scaleMin!.isNaN ||
              axis.scaleMax!.isNaN ||
              axis.scaleMax! <= axis.scaleMin!)) {
        throw AppException.validation(
          'Fail-Fast: LogicRadarChart axis[$i] scaleMax must be greater than scaleMin.',
        );
      }
    }
  }

  double _resolveEntryValue(MatrixScorecardRowDto axis) {
    final ratio = axis.uiPlotRatio;
    if (ratio != null && !ratio.isNaN && !ratio.isInfinite) {
      return ratio;
    }
    final score = axis.score!;
    final minBound = axis.scaleMin;
    final maxBound = axis.scaleMax;
    if (minBound != null && maxBound != null && maxBound > minBound) {
      final normalized = (score - minBound) / (maxBound - minBound);
      return normalized.clamp(_ratioMin, _ratioMax);
    }
    return score;
  }

  int _resolveTickCount() {
    double maxScale = 0.0;
    for (final axis in axes) {
      final bound = axis.scaleMax;
      if (bound != null &&
          !bound.isNaN &&
          !bound.isInfinite &&
          bound > maxScale) {
        maxScale = bound;
      }
    }
    final resolved = maxScale.toInt();
    return resolved >= 1 ? resolved : _defaultTickCount;
  }

  String _resolveScoreDisplay(MatrixScorecardRowDto axis) {
    final displayLabel = axis.scoreDisplayLabel;
    if (displayLabel != null && displayLabel.trim().isNotEmpty) {
      return displayLabel.trim();
    }
    return axis.score!.toStringAsFixed(1);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final locale = Localizations.localeOf(context).languageCode;

    try {
      _validateAxes(locale);

      final tickCount = _resolveTickCount();
      final transparentColor = colorScheme.surface.withValues(alpha: 0.0);
      final gridColor = colorScheme.onSurfaceVariant.withValues(alpha: 0.2);

      final dataSets = [
        RadarDataSet(
          fillColor: colorScheme.primary.withValues(alpha: 0.25),
          borderColor: colorScheme.primary,
          entryRadius: AppSpacing.s4,
          dataEntries: [
            for (final axis in axes)
              RadarEntry(value: _resolveEntryValue(axis)),
          ],
          borderWidth: AppSpacing.s2,
        ),
      ];

      final hiddenTicksStyle = (textTheme.labelSmall ?? const TextStyle())
          .copyWith(color: transparentColor);
      final titleStyle = (textTheme.labelSmall ?? const TextStyle()).copyWith(
        color: colorScheme.onSurfaceVariant,
        fontWeight: FontWeight.bold,
      );

      return SizedBox(
        height: AppSpacing.s300,
        width: double.infinity,
        child: ExcludeSemantics(
          child: RadarChart(
            RadarChartData(
              dataSets: dataSets,
              radarBackgroundColor: transparentColor,
              borderData: FlBorderData(show: false),
              radarBorderData: BorderSide(color: transparentColor),
              tickCount: tickCount,
              ticksTextStyle: hiddenTicksStyle,
              tickBorderData: BorderSide(color: gridColor),
              gridBorderData: BorderSide(
                color: gridColor,
                width: AppSpacing.s2,
              ),
              radarShape: RadarShape.polygon,
              getTitle: (index, angle) {
                final axis = axes[index];
                final axisLabel = axis.labelI18n.get(locale);
                final scoreStr = _resolveScoreDisplay(axis);
                final wrappedTitle = axisLabel.split(' ').join('\n');

                return RadarChartTitle(
                  text: '$wrappedTitle\n($scoreStr)',
                  angle: 0,
                );
              },
              titleTextStyle: titleStyle,
            ),
            duration: AppDurations.fast,
            curve: Curves.linear,
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'LogicRadarChart',
            'VALIDATION_FAILED: Failed to render logic radar chart',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
