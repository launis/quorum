import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// A 2D Scatter Plot visualizing pre-computed SDUI metrics across 2 or 3 dimensions.
class LogicMatrixChart extends ConsumerWidget {
  const LogicMatrixChart({
    super.key,
    required this.xAxis,
    required this.yAxis,
    this.zAxis,
  });

  final MatrixScorecardRowDto xAxis;
  final MatrixScorecardRowDto yAxis;
  final MatrixScorecardRowDto? zAxis;

  static const double _axisMin = 0.0;
  static const double _axisMid = 0.5;
  static const double _axisMax = 1.0;
  static const double _plotViewportMargin = 0.15;
  static const double _chartHeight = 250.0;
  static const double _defaultDotRadius = 12.0;
  static const double _minZDotRadius = 6.0;
  static const double _maxZDotRadiusDelta = 30.0;
  static const double _leftAxisNameSize = 20.0;
  static const double _bottomAxisNameSize = 28.0;
  static const double _sideTitlesReservedSize = 30.0;

  void _validateAxis(
    MatrixScorecardRowDto axis,
    String axisRole,
    String locale,
  ) {
    if (axis.blockId.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: LogicMatrixChart $axisRole blockId cannot be empty.',
      );
    }
    if (axis.name.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: LogicMatrixChart $axisRole name cannot be empty.',
      );
    }
    // Enforce strict translation fallback validation on labelI18n.
    axis.labelI18n.get(locale);

    final ratio = axis.uiPlotRatio;
    if (ratio == null ||
        ratio.isNaN ||
        ratio.isInfinite ||
        ratio < _axisMin ||
        ratio > _axisMax) {
      throw AppException.validation(
        'Fail-Fast: LogicMatrixChart $axisRole uiPlotRatio must be within [0.0, 1.0].',
      );
    }

    final minBound = axis.scaleMin;
    final maxBound = axis.scaleMax;
    if (minBound == null ||
        maxBound == null ||
        minBound.isNaN ||
        maxBound.isNaN ||
        maxBound <= minBound) {
      throw AppException.validation(
        'Fail-Fast: LogicMatrixChart $axisRole scaleMin and scaleMax must be valid with scaleMax > scaleMin.',
      );
    }

    final scoreVal = axis.score;
    if (scoreVal == null || scoreVal.isNaN || scoreVal.isInfinite) {
      throw AppException.validation(
        'Fail-Fast: LogicMatrixChart $axisRole score cannot be null or NaN.',
      );
    }
  }

  String _resolveAxisDisplayName(MatrixScorecardRowDto axis, String locale) {
    final translated = axis.labelI18n.get(locale);
    if (axis.name.trim().isNotEmpty && axis.name != translated) {
      return axis.name;
    }
    return translated;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).languageCode;

    try {
      _validateAxis(xAxis, 'xAxis', locale);
      _validateAxis(yAxis, 'yAxis', locale);
      final currentZAxis = zAxis;
      if (currentZAxis != null) {
        _validateAxis(currentZAxis, 'zAxis', locale);
      }

      final double x = xAxis.uiPlotRatio!;
      final double y = yAxis.uiPlotRatio!;

      double radius = _defaultDotRadius;
      if (currentZAxis != null) {
        final double pct = currentZAxis.uiPlotRatio!;
        radius = _minZDotRadius + (pct * _maxZDotRadiusDelta);
      }

      final xLabelName = _resolveAxisDisplayName(xAxis, locale);
      final yLabelName = _resolveAxisDisplayName(yAxis, locale);
      final xScoreStr = xAxis.score!.toStringAsFixed(1);
      final xMaxStr = xAxis.scaleMax!.toStringAsFixed(1);
      final yScoreStr = yAxis.score!.toStringAsFixed(1);
      final yMaxStr = yAxis.scaleMax!.toStringAsFixed(1);

      final axisLabelStyle = theme.textTheme.labelSmall?.copyWith(
        color: theme.colorScheme.onSurfaceVariant,
      );
      final boldAxisLabelStyle = axisLabelStyle?.copyWith(
        fontWeight: FontWeight.bold,
      );

      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            height: _chartHeight,
            child: ExcludeSemantics(
              child: ScatterChart(
                ScatterChartData(
                  scatterSpots: [
                    ScatterSpot(
                      x,
                      y,
                      dotPainter: FlDotCirclePainter(
                        radius: radius,
                        color: theme.colorScheme.primary.withValues(alpha: 0.7),
                        strokeColor: theme.colorScheme.primary,
                        strokeWidth: AppSpacing.s2,
                      ),
                    ),
                  ],
                  minX: _axisMin - _plotViewportMargin,
                  maxX: _axisMax + _plotViewportMargin,
                  minY: _axisMin - _plotViewportMargin,
                  maxY: _axisMax + _plotViewportMargin,
                  backgroundColor: theme.colorScheme.surface,
                  gridData: FlGridData(
                    show: true,
                    drawHorizontalLine: true,
                    drawVerticalLine: true,
                    checkToShowHorizontalLine: (value) => value == _axisMid,
                    checkToShowVerticalLine: (value) => value == _axisMid,
                    getDrawingHorizontalLine: (value) => FlLine(
                      color: theme.colorScheme.onSurfaceVariant.withValues(
                        alpha: 0.5,
                      ),
                      strokeWidth: AppSpacing.s2,
                      dashArray: [5, 5],
                    ),
                    getDrawingVerticalLine: (value) => FlLine(
                      color: theme.colorScheme.onSurfaceVariant.withValues(
                        alpha: 0.5,
                      ),
                      strokeWidth: AppSpacing.s2,
                      dashArray: [5, 5],
                    ),
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    leftTitles: AxisTitles(
                      axisNameWidget: Text(
                        l10n.matrixChartYAxisLabel(
                          yLabelName,
                          yScoreStr,
                          yMaxStr,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: axisLabelStyle,
                      ),
                      axisNameSize: _leftAxisNameSize,
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: _sideTitlesReservedSize,
                        interval: _axisMax,
                        getTitlesWidget: (value, meta) {
                          if (value == _axisMin) {
                            return Padding(
                              padding: const EdgeInsets.only(
                                right: AppSpacing.s6,
                              ),
                              child: Text(
                                yAxis.scaleMin!.toStringAsFixed(1),
                                style: axisLabelStyle,
                                textAlign: TextAlign.right,
                              ),
                            );
                          } else if (value == _axisMax) {
                            return Padding(
                              padding: const EdgeInsets.only(
                                right: AppSpacing.s6,
                              ),
                              child: Text(
                                yAxis.scaleMax!.toStringAsFixed(1),
                                style: axisLabelStyle,
                                textAlign: TextAlign.right,
                              ),
                            );
                          }
                          return const SizedBox();
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      axisNameWidget: Padding(
                        padding: const EdgeInsets.only(top: AppSpacing.s12),
                        child: Text(
                          l10n.matrixChartXAxisLabel(
                            xLabelName,
                            xScoreStr,
                            xMaxStr,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: boldAxisLabelStyle,
                        ),
                      ),
                      axisNameSize: _bottomAxisNameSize,
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: _sideTitlesReservedSize,
                        interval: _axisMax,
                        getTitlesWidget: (value, meta) {
                          if (value == _axisMin) {
                            return Padding(
                              padding: const EdgeInsets.only(
                                top: AppSpacing.s6,
                              ),
                              child: Text(
                                xAxis.scaleMin!.toStringAsFixed(1),
                                style: axisLabelStyle,
                                textAlign: TextAlign.center,
                              ),
                            );
                          } else if (value == _axisMax) {
                            return Padding(
                              padding: const EdgeInsets.only(
                                top: AppSpacing.s6,
                              ),
                              child: Text(
                                xAxis.scaleMax!.toStringAsFixed(1),
                                style: axisLabelStyle,
                                textAlign: TextAlign.center,
                              ),
                            );
                          }
                          return const SizedBox();
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border.all(
                      color: theme.colorScheme.onSurfaceVariant.withValues(
                        alpha: 0.2,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          if (currentZAxis != null) ...[
            AppSpacing.h12,
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Flexible(
                  child: Text(
                    l10n.matrixChartZAxisLabel(
                      _resolveAxisDisplayName(currentZAxis, locale),
                      currentZAxis.score!.toStringAsFixed(1),
                      currentZAxis.scaleMax!.toStringAsFixed(1),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: boldAxisLabelStyle,
                  ),
                ),
              ],
            ),
          ],
        ],
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'LogicMatrixChart',
            'VALIDATION_FAILED: Failed to render logic matrix chart',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
