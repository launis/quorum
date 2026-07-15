import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';

/// A Polar 3D connected Radar (Spider) chart visualizing metrics across 3+ dimensions.
class LogicRadarChart extends StatelessWidget {
  const LogicRadarChart({super.key, required this.axes});

  final List<MatrixScorecardRowDto> axes;

  @override
  Widget build(BuildContext context) {
    if (axes.length < 3) {
      return const SizedBox.shrink(); // A radar chart logically requires at least 3 points
    }

    // Baseline calculation to match PDF's scale constraints
    double maxScale = 6.0;
    for (var a in axes) {
      if (a.scaleMax != null && a.scaleMax! > maxScale) maxScale = a.scaleMax!;
    }

    final dataSets = [
      RadarDataSet(
        fillColor: Theme.of(
          context,
        ).colorScheme.primary.withValues(alpha: 0.25),
        borderColor: Theme.of(context).colorScheme.primary,
        entryRadius: 4,
        dataEntries: axes.map((a) {
          final val = a.score;
          return RadarEntry(value: val ?? 0.0);
        }).toList(),
        borderWidth: 2,
      ),
    ];

    return SizedBox(
      height: 300,
      width: double.infinity,
      child: RadarChart(
        RadarChartData(
          dataSets: dataSets,
          radarBackgroundColor: Colors.transparent,
          borderData: FlBorderData(show: false),
          radarBorderData: const BorderSide(color: Colors.transparent),
          tickCount: maxScale.toInt(),
          ticksTextStyle: const TextStyle(
            color: Colors.transparent,
            fontSize: 10,
          ),
          tickBorderData: BorderSide(
            color: Theme.of(
              context,
            ).colorScheme.onSurfaceVariant.withValues(alpha: 0.2),
          ),
          gridBorderData: BorderSide(
            color: Theme.of(
              context,
            ).colorScheme.onSurfaceVariant.withValues(alpha: 0.2),
            width: 1.5,
          ),
          radarShape: RadarShape.polygon,
          getTitle: (index, angle) {
            final axisName = axes[index].name;
            final scoreStr = axes[index].score?.toStringAsFixed(1) ?? '-';

            // Re-use logic to chunk title lines like PDF
            final wrappedTitle = axisName.split(' ').join('\n');

            return RadarChartTitle(
              text: "$wrappedTitle\n($scoreStr)",
              angle: 0,
            );
          },
          titleTextStyle: TextStyle(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
        duration: const Duration(milliseconds: 150),
        curve: Curves.linear,
      ),
    );
  }
}
