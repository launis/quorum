import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

/// A 2D Scatter Plot visualizing Logic Quality.
/// X-Axis: Cognitive Level (Bloom's Taxonomy) - Depth of Thought
/// Y-Axis: Argumentation Quality (Toulmin) - Structural Integrity
class LogicMatrixChart extends StatelessWidget {
  const LogicMatrixChart({
    super.key,
    required this.bloomScore,
    required this.toulminScore,
    this.strategicScore = 2.0, // Default to middle if missing
  });

  final double bloomScore;
  final double toulminScore;
  final double strategicScore;

  @override
  Widget build(BuildContext context) {
    // Use authoritative scores from Backend (SSOT)
    final x = bloomScore;
    final y = toulminScore;

    // Quadrant label based on coordinates (Threshold 3.0)
    String quadrantLabel = "Tuntematon";
    if (x <= 0.1)
      quadrantLabel = "Ei analysoitavissa (Syöte puuttuu/riittämätön)";
    else if (x >= 3.0 && y >= 3.0)
      quadrantLabel = "Visionääri (Korkea Bloom + Vahva Toulmin)";
    else if (x < 3.0 && y >= 3.0)
      quadrantLabel = "Faktapohjainen (Matala Bloom + Vahva Toulmin)";
    else if (x >= 3.0 && y < 3.0)
      quadrantLabel = "Abstrakti (Korkea Bloom + Heikko Toulmin)";
    else
      quadrantLabel = "Pinnallinen (Matala Bloom + Heikko Toulmin)";

    // Bubble Size Calculation (Z-Axis)
    // Scale 0-4 -> Radius 8-24
    double radius = 8.0 + (strategicScore.clamp(0.0, 4.0) * 4.0);

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
              minX: 0,
              maxX: 6.5, // Allow slightly more space for "Creating" (6.0)
              minY: 0,
              maxY: 6.5,
              backgroundColor: Colors.white,
              gridData: FlGridData(
                show: true,
                drawHorizontalLine: true,
                drawVerticalLine: true,
                // Draw quadrant dividers
                checkToShowHorizontalLine: (value) => value == 3,
                checkToShowVerticalLine: (value) => value == 3,
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
                  axisNameWidget: const Text(
                    "Argumentaation Vahvuus (Toulmin)",
                    style: TextStyle(fontSize: 10),
                  ),
                  axisNameSize: 20, // Reserve space for name
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 40, // Increased for labels
                    getTitlesWidget: (value, meta) {
                      if (value == 1)
                        return const Text(
                          "Väite",
                          style: TextStyle(fontSize: 9),
                        );
                      if (value == 5)
                        return const Text(
                          "Vahva",
                          style: TextStyle(fontSize: 9),
                        );
                      return const SizedBox.shrink();
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  axisNameWidget: const Text(
                    "Kognitiivinen Syvyys (Bloom)",
                    style: TextStyle(fontSize: 10),
                  ),
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (value, meta) {
                      if (value == 1)
                        return const Text(
                          "Muisti",
                          style: TextStyle(fontSize: 9),
                        );
                      if (value == 5)
                        return const Text(
                          "Luominen",
                          style: TextStyle(fontSize: 9),
                        );
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
        const SizedBox(height: 8),
        Text(
          quadrantLabel,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 12,
            color: Colors.blueGrey,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          "Pallon koko: Strateginen Syvyys ($strategicScore/4.0)",
          style: const TextStyle(
            fontSize: 10,
            color: Colors.grey,
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
}
