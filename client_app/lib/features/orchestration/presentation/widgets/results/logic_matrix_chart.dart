import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

/// A 2D Scatter Plot visualizing Logic Quality.
/// X-Axis: Cognitive Level (Bloom's Taxonomy) - Depth of Thought
/// Y-Axis: Argumentation Quality (Toulmin) - Structural Integrity
class LogicMatrixChart extends StatelessWidget {
  const LogicMatrixChart({
    super.key,
    required this.bloomLevel,
    required this.toulminArguments,
  });

  final String bloomLevel;
  final List<dynamic> toulminArguments;

  @override
  Widget build(BuildContext context) {
    debugPrint("LogicMatrixChart received bloomLevel: '$bloomLevel' (Code units: ${bloomLevel.codeUnits})");
    final x = _calculateBloomScore(bloomLevel);
    final y = _calculateToulminScore(toulminArguments);

    // Quadrant label based on coordinates
    String quadrantLabel = "Tuntematon";
    if (x == 0.0) quadrantLabel = "Ei analysoitavissa (Syöte puuttuu/riittämätön)";
    else if (x >= 3 && y >= 3) quadrantLabel = "Visionääri (Korkea Bloom + Vahva Toulmin)";
    else if (x < 3 && y >= 3) quadrantLabel = "Faktapohjainen (Matala Bloom + Vahva Toulmin)";
    else if (x >= 3 && y < 3) quadrantLabel = "Abstrakti (Korkea Bloom + Heikko Toulmin)";
    else quadrantLabel = "Pinnallinen (Matala Bloom + Heikko Toulmin)";

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
                    radius: 12,
                    color: Colors.blueAccent,
                    strokeColor: Colors.white,
                    strokeWidth: 2,
                  ),
                ),
              ],
              minX: 0,
              maxX: 6,
              minY: 0,
              maxY: 6,
              backgroundColor: Colors.white,
              gridData: FlGridData(
                show: true,
                drawHorizontalLine: true,
                drawVerticalLine: true,
                // Draw quadrant dividers
                checkToShowHorizontalLine: (value) => value == 3,
                checkToShowVerticalLine: (value) => value == 3,
                getDrawingHorizontalLine: (value) => FlLine(
                   color: Colors.grey.withValues(alpha: 0.5), 
                   strokeWidth: 2,
                   dashArray: [5, 5]
                ),
                getDrawingVerticalLine: (value) => FlLine(
                   color: Colors.grey.withValues(alpha: 0.5), 
                   strokeWidth: 2,
                   dashArray: [5, 5]
                ),
              ),
              titlesData: FlTitlesData(
                show: true,
                leftTitles: AxisTitles(
                  axisNameWidget: const Text("Argumentaation Vahvuus (Toulmin)", style: TextStyle(fontSize: 10)),
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 30,
                    getTitlesWidget: (value, meta) {
                       if (value == 1) return const Text("Väite", style: TextStyle(fontSize: 9));
                       if (value == 5) return const Text("Vahva", style: TextStyle(fontSize: 9));
                       return const SizedBox.shrink();
                    }
                  ),
                ),
                bottomTitles: AxisTitles(
                  axisNameWidget: const Text("Kognitiivinen Syvyys (Bloom)", style: TextStyle(fontSize: 10)),
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (value, meta) {
                       if (value == 1) return const Text("Muisti", style: TextStyle(fontSize: 9));
                       if (value == 5) return const Text("Luominen", style: TextStyle(fontSize: 9));
                       return const SizedBox.shrink();
                    }
                  ),
                ),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
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
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.blueGrey),
        )
      ],
    );
  }

  double _calculateBloomScore(String level) {
    final lower = level.toLowerCase();
    // English (Primary)
    if (lower.contains("creating")) return 5.5;
    if (lower.contains("evaluating")) return 4.5;
    if (lower.contains("analyzing")) return 3.5;
    if (lower.contains("applying")) return 2.5;
    if (lower.contains("understanding")) return 1.5;
    if (lower.contains("remembering")) return 0.5;

    // Finnish (Legacy Backward Compatibility)
    if (lower.contains("luominen")) return 5.5;
    if (lower.contains("arviointi")) return 4.5;
    if (lower.contains("analysointi")) return 3.5;
    if (lower.contains("soveltaminen")) return 2.5;
    if (lower.contains("ymmärtäminen")) return 1.5;
    if (lower.contains("muistaminen")) return 0.5;

    // Handle "Not Detected" / Missing Prompt cases
    if (lower.contains("ei havaittu") ||
        lower.contains("not detected") ||
        lower.contains("puuttuu") ||
        lower.contains("missing") ||
        lower.contains("n/a")) {
      return 0.0;
    }

    return 3.0; // Default middle for unknown valid levels
  }

  double _calculateToulminScore(List<dynamic> args) {
    if (args.isEmpty) return 0.5;

    double totalScore = 0;
    for (final arg in args) {
      double score = 1.0; // Base: Claim
      if (arg['warrant'] != null && arg['warrant'].toString().length > 5) score += 2.0;
      if (arg['backing'] != null && arg['backing'].toString().length > 5) score += 2.0;
      totalScore += score;
    }

    final avg = totalScore / args.length;
    // Cap at 5.5
    return avg > 5.5 ? 5.5 : avg;
  }
}
