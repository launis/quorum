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
    // Coordinate mapping
    final x = xAxis.score;
    final y = yAxis.score;

    final double xMin = xAxis.scaleMin < xAxis.scaleMax ? xAxis.scaleMin : 0.0;
    final double xMax =
        xAxis.scaleMax > xAxis.scaleMin
            ? xAxis.scaleMax
            : (xAxis.scaleMin + 6.0);
    final double yMin = yAxis.scaleMin < yAxis.scaleMax ? yAxis.scaleMin : 0.0;
    final double yMax =
        yAxis.scaleMax > yAxis.scaleMin
            ? yAxis.scaleMax
            : (yAxis.scaleMin + 6.0);

    // Calculate middle line for grid quadrants
    final xMid = (xMin + xMax) / 2;
    final yMid = (yMin + yMax) / 2;

    // Bubble Size Calculation contextually derived from absolute magnitude
    double radius = 12.0;
    if (zAxis != null) {
      double zMin = zAxis!.scaleMin;
      double zMax = zAxis!.scaleMax;
      if (zMax <= zMin) zMax = zMin + 1.0; // Protect div by zero

      double pct = (zAxis!.score - zMin) / (zMax - zMin);
      radius = 8.0 + (pct.clamp(0.0, 1.0) * 16.0); // 8 to 24
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
                    color: Colors.blueAccent.withValues(
                      alpha: 0.7,
                    ), // Transparent for overlapping
                    strokeColor: Colors.blue[900]!,
                    strokeWidth: 2,
                  ),
                ),
              ],
              minX: xMin,
              maxX: xMax + ((xMax - xMin) * 0.05), // Visual padding
              minY: yMin,
              maxY: yMax + ((yMax - yMin) * 0.05),
              backgroundColor: Colors.white,
              gridData: FlGridData(
                show: true,
                drawHorizontalLine: true,
                drawVerticalLine: true,
                // Draw quadrant dividers
                checkToShowHorizontalLine: (value) => value == yMid,
                checkToShowVerticalLine: (value) => value == xMid,
                getDrawingHorizontalLine:
                    (value) => FlLine(
                      color: Colors.grey.withValues(alpha: 0.5),
                      strokeWidth: 2,
                      dashArray: [5, 5],
                    ),
                getDrawingVerticalLine:
                    (value) => FlLine(
                      color: Colors.grey.withValues(alpha: 0.5),
                      strokeWidth: 2,
                      dashArray: [5, 5],
                    ),
              ),
              titlesData: FlTitlesData(
                show: true,
                leftTitles: AxisTitles(
                  axisNameWidget: Text(
                    yAxis.name,
                    style: const TextStyle(fontSize: 10),
                  ),
                  axisNameSize: 20, // Reserve space for name
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60, // Increased for labels
                    interval:
                        1.0, // Force interval to 1.0 to prevent missing labels
                    getTitlesWidget: (value, meta) {
                      final strVal = value.toStringAsFixed(0);
                      // Use integer representation if it's a clean int for cleaner map lookup
                      final key =
                          value == value.toInt() ? strVal : value.toString();
                      final label =
                          yAxis.scaleLabels[key] ??
                          yAxis.scaleLabels[value.toString()];

                      if (label != null) {
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
                      xAxis.name,
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
                    interval: 1.0, // Force interval to 1.0
                    getTitlesWidget: (value, meta) {
                      final strVal = value.toStringAsFixed(0);
                      final key =
                          value == value.toInt() ? strVal : value.toString();
                      final label =
                          xAxis.scaleLabels[key] ??
                          xAxis.scaleLabels[value.toString()];

                      if (label != null) {
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
                border: Border.all(color: Colors.grey.withValues(alpha: 0.2)),
              ),
            ),
          ),
        ),
        if (zAxis != null) ...[
          const SizedBox(height: 8),
          Text(
            "${zAxis!.name} (${zAxis!.score} / ${zAxis!.scaleMax})",
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 10,
              color: Colors.blueGrey,
            ),
          ),
        ],
      ],
    );
  }
}
