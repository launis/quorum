import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart'; // REQUIRED FOR ReportAxisDTO

/// A 2D Scatter Plot visualizing metrics across 2 or 3 dimensions.
class LogicMatrixChart extends StatelessWidget {
  const LogicMatrixChart({
    super.key,
    required this.xAxis,
    required this.yAxis,
    this.zAxis,
  });

  final ReportAxisDTO xAxis;
  final ReportAxisDTO yAxis;
  final ReportAxisDTO? zAxis;

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

    return Column(
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
              minX: xMin,
              maxX: xMax + 0.05, // Visual padding
              minY: yMin,
              maxY: yMax + 0.05,
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
                    "Y: ${yAxis.name}",
                    style: const TextStyle(fontSize: 10),
                  ),
                  axisNameSize: 20, // Reserve space for name
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60, // Increased for labels
                    interval: 1.0, // Only 0.0 and 1.0 labels!
                    getTitlesWidget: (value, meta) {
                      final strVal = value.toStringAsFixed(1);
                      final label = yAxis.uiBoundaryLabels[strVal];

                      if (label != null && label.isNotEmpty) {
                        return Padding(
                          padding: const EdgeInsets.only(right: 6.0),
                          child: Text(
                            label,
                            style: const TextStyle(fontSize: 9),
                            maxLines: 2,
                            textAlign: TextAlign.right,
                            overflow: TextOverflow.ellipsis,
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
                      "X: ${xAxis.name}",
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  axisNameSize: 28,
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60,
                    interval: 1.0, // Only 0.0 and 1.0 labels
                    getTitlesWidget: (value, meta) {
                      final strVal = value.toStringAsFixed(1);
                      final label = xAxis.uiBoundaryLabels[strVal];

                      if (label != null && label.isNotEmpty) {
                        Widget textWidget = SizedBox(
                          width: 80,
                          child: Text(
                            label,
                            style: const TextStyle(fontSize: 9),
                            maxLines: 3,
                            textAlign: TextAlign.center,
                            overflow: TextOverflow.ellipsis,
                          ),
                        );

                        // Prevent edge labels from bleeding out of the chart bounds
                        double offsetX = 0;
                        if (value == xMin) {
                          offsetX = 30; // Shift right to avoid Y-axis overlap
                        } else if (value == xMax) {
                          offsetX = -30; // Shift left to stay inside the screen
                        }

                        return Padding(
                          padding: const EdgeInsets.only(top: 6.0),
                          child: Transform.translate(
                            offset: Offset(offsetX, 0),
                            child: textWidget,
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
            "Z (Pallon Koko): ${zAxis!.name} (${zAxis!.score ?? 'N/A'} / ${zAxis!.scaleMax})",
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
