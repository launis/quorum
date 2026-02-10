import 'package:client_app/features/orchestration/domain/models/xai_report.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class ScoreCardRadar extends StatelessWidget {
  final ScoreCardItem card;

  const ScoreCardRadar({super.key, required this.card});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    // Use dimensions or fallback if empty
    final dimensions = card.dimensions.isNotEmpty
        ? card.dimensions
        : [
            // Dummy breakdown if missing, to ensure chart renders something
            // In production, we might hide the chart or show "No Data"
          ];

    final hasData = dimensions.isNotEmpty;
    final canShowRadar = dimensions.length >= 3;

    return Card(
      elevation: 4,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Header: Agent Name and Verdict
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        card.agentName,
                        style: textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: colorScheme.secondary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        card.verdict,
                        style: textTheme.bodyMedium?.copyWith(
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
                // Total Score Badge
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    card.totalScore.toStringAsFixed(1),
                    style: textTheme.headlineSmall?.copyWith(
                      color: colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            
            // Radar Chart Section
            if (canShowRadar)
              SizedBox(
                height: 200,
                child: RadarChart(
                  RadarChartData(
                    radarTouchData: RadarTouchData(enabled: false),
                    dataSets: [
                      RadarDataSet(
                        fillColor: colorScheme.primary.withAlpha(50), 
                        borderColor: colorScheme.primary,
                        entryRadius: 2,
                        dataEntries: dimensions
                            .map((d) => RadarEntry(value: d.score))
                            .toList(),
                        borderWidth: 2,
                      ),
                    ],
                    radarBackgroundColor: Colors.transparent,
                    borderData: FlBorderData(show: false),
                    radarBorderData: const BorderSide(color: Colors.transparent),
                    titlePositionPercentageOffset: 0.2,
                    titleTextStyle: textTheme.bodySmall?.copyWith(fontSize: 10),
                    getTitle: (index, angle) {
                      if (index >= dimensions.length) return const RadarChartTitle(text: '');
                      
                      final d = dimensions[index];
                      // Strict Mode: No fallback to ID
                      final label = d.dimensionLabel.isNotEmpty ? d.dimensionLabel : ''; 
                      
                      return RadarChartTitle(text: label); 
                    },
                    tickCount: 1,
                    ticksTextStyle: const TextStyle(color: Colors.transparent),
                    gridBorderData: BorderSide(
                      color: colorScheme.outlineVariant.withAlpha(50), 
                      width: 1,
                    ),
                  ),
                ),
              )
            else if (!hasData)
              const Center(
                child: Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Text("No detailed dimension data available."),
                ),
              ),
              
            // Detailed Breakdown List
            if (hasData) ...[
                 const SizedBox(height: 24),
                 Align(
                   alignment: Alignment.centerLeft,
                   child: Text(
                     "Detailed Breakdown",
                     style: textTheme.titleSmall!.copyWith(fontWeight: FontWeight.bold),
                   ),
                 ),
                 const SizedBox(height: 8),
                 ...dimensions.map((d) {
                    final label = d.dimensionLabel.isNotEmpty ? d.dimensionLabel : "Unknown";
                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(
                        color: colorScheme.surfaceContainer,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: colorScheme.outlineVariant),
                      ),
                      child: ListTile(
                        leading: Container(
                          width: 40,
                          height: 40,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                             color: colorScheme.primaryContainer,
                             shape: BoxShape.circle,
                          ),
                          child: Text(
                             d.score.toStringAsFixed(0),
                             style: textTheme.titleMedium!.copyWith(
                               color: colorScheme.onPrimaryContainer, 
                               fontWeight: FontWeight.bold
                             ),
                          ),
                        ),
                        title: Text(
                            label, 
                            style: textTheme.titleSmall!.copyWith(fontWeight: FontWeight.bold)
                        ),
                        subtitle: Padding(
                          padding: const EdgeInsets.only(top: 4.0),
                          child: Text(
                            d.reasoning,
                            style: textTheme.bodyMedium,
                          ),
                        ),
                      ),
                    );
                 }).toList(),
            ]
          ],
        ),
      ),
    );
  }
}
