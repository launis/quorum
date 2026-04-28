import 'dart:math' as math;
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

/// A 2D Scatter Plot visualizing metrics across 2 or 3 dimensions.
class LogicMatrixChart extends StatelessWidget {
  const LogicMatrixChart({
    super.key,
    required this.xAxis,
    required this.yAxis,
    this.zAxis,
  });

  final MatrixScorecardRowDto xAxis;
  final MatrixScorecardRowDto yAxis;
  final MatrixScorecardRowDto? zAxis;

  double _calculateMarginRatio(double min, double max) {
    final double range = max - min;
    if (range <= 0) return 0.15;
    final double val = math.max(1.0, range - 0.001);
    final int exponent = (math.log(val) / math.ln10).floor();
    final double margin = math.pow(10, exponent).toDouble();
    return margin / range;
  }

  @override
  Widget build(BuildContext context) {
    // Coordinate mapping using Server-Driven UI ratios
    // Fallback to 0.5 if missing so it sits exactly in the middle.
    final x = xAxis.uiPlotRatio ?? 0.5;
    final y = yAxis.uiPlotRatio ?? 0.5;

    const double xMin = 0.0;
    const double xMax = 1.0;
    const double yMin = 0.0;
    const double yMax = 1.0;

    // Calculate middle line for grid quadrants
    const xMid = 0.5;
    const yMid = 0.5;

    // Bubble Size Calculation contextually derived from absolute magnitude
    double radius = 12.0;
    if (zAxis != null) {
      // Use the pre-computed Backend SDUI ratio!
      final double pct = zAxis!.uiPlotRatio ?? 0.5;
      // Massive visual contrast for Z-axis detection (12px to 72px diameter)
      radius = 6.0 + (pct.clamp(0.0, 1.0) * 30.0);
    }

    final double xMargin = _calculateMarginRatio(
      xAxis.scaleMin ?? 1.0,
      xAxis.scaleMax ?? 5.0,
    );
    final double yMargin = _calculateMarginRatio(
      yAxis.scaleMin ?? 1.0,
      yAxis.scaleMax ?? 5.0,
    );

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 250,
          child: ScatterChart(
            ScatterChartData(
              scatterSpots: [
                ScatterSpot(
                  x,
                  y,
                  dotPainter: FlDotCirclePainter(
                    radius: radius,
                    color: Theme.of(context).colorScheme.primary.withValues(
                      alpha: 0.7,
                    ), // Transparent for overlapping
                    strokeColor: Theme.of(context).colorScheme.primary,
                    strokeWidth: 2,
                  ),
                ),
              ],
              minX:
                  xMin -
                  xMargin, // Dynamic visual padding based on logarithmic scale rules
              maxX: xMax + xMargin,
              minY: yMin - yMargin,
              maxY: yMax + yMargin,
              backgroundColor: Theme.of(context).colorScheme.surface,
              gridData: FlGridData(
                show: true,
                drawHorizontalLine: true,
                drawVerticalLine: true,
                // Draw quadrant dividers
                checkToShowHorizontalLine: (value) => value == yMid,
                checkToShowVerticalLine: (value) => value == xMid,
                getDrawingHorizontalLine: (value) => FlLine(
                  color: Theme.of(
                    context,
                  ).colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                  strokeWidth: 2,
                  dashArray: [5, 5],
                ),
                getDrawingVerticalLine: (value) => FlLine(
                  color: Theme.of(
                    context,
                  ).colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
                  strokeWidth: 2,
                  dashArray: [5, 5],
                ),
              ),
              titlesData: FlTitlesData(
                show: true,
                leftTitles: AxisTitles(
                  axisNameWidget: Text(
                    "Y: ${yAxis.name} (${yAxis.score} / ${yAxis.scaleMax})",
                    style: const TextStyle(fontSize: 10),
                  ),
                  axisNameSize: 20, // Reserve space for name
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 30,
                    interval: 1.0,
                    getTitlesWidget: (value, meta) {
                      if (value == 0.0 && yAxis.scaleMin != null) {
                        return Padding(
                          padding: const EdgeInsets.only(right: 6.0),
                          child: Text(
                            yAxis.scaleMin!.toStringAsFixed(1),
                            style: const TextStyle(fontSize: 10),
                            textAlign: TextAlign.right,
                          ),
                        );
                      } else if (value == 1.0 && yAxis.scaleMax != null) {
                        return Padding(
                          padding: const EdgeInsets.only(right: 6.0),
                          child: Text(
                            yAxis.scaleMax!.toStringAsFixed(1),
                            style: const TextStyle(fontSize: 10),
                            textAlign: TextAlign.right,
                          ),
                        );
                      }
                      return const SizedBox.shrink();
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  axisNameWidget: Padding(
                    padding: const EdgeInsets.only(top: 12.0),
                    child: Text(
                      "X: ${xAxis.name} (${xAxis.score} / ${xAxis.scaleMax})",
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  axisNameSize: 28,
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 30,
                    interval: 1.0,
                    getTitlesWidget: (value, meta) {
                      if (value == 0.0 && xAxis.scaleMin != null) {
                        return Padding(
                          padding: const EdgeInsets.only(top: 6.0),
                          child: Text(
                            xAxis.scaleMin!.toStringAsFixed(1),
                            style: const TextStyle(fontSize: 10),
                            textAlign: TextAlign.center,
                          ),
                        );
                      } else if (value == 1.0 && xAxis.scaleMax != null) {
                        return Padding(
                          padding: const EdgeInsets.only(top: 6.0),
                          child: Text(
                            xAxis.scaleMax!.toStringAsFixed(1),
                            style: const TextStyle(fontSize: 10),
                            textAlign: TextAlign.center,
                          ),
                        );
                      }
                      return const SizedBox.shrink();
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
                  color: Theme.of(
                    context,
                  ).colorScheme.onSurfaceVariant.withValues(alpha: 0.2),
                ),
              ),
            ),
          ),
        ),
        if (zAxis != null) ...[
          const SizedBox(height: 12),
          Text(
            "Z (Pallon Koko): ${zAxis!.name} (${zAxis!.score} / ${zAxis!.scaleMax})",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 10,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ],
    );
  }
}
