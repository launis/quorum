import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class ScoreCardRadar extends StatelessWidget {
  final Map<String, dynamic> cardData;

  const ScoreCardRadar({super.key, required this.cardData});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final l10n = AppLocalizations.of(context)!;

    // Use dimensions or fallback if empty
    final rawDimensions = cardData['dimensions'] as List<dynamic>? ?? [];
    final dimensions = rawDimensions
        .map((e) => e as Map<String, dynamic>)
        .toList();

    final dimensionsNotEmpty = dimensions.isNotEmpty;

    final hasData = dimensionsNotEmpty;
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
                        cardData['agentName']?.toString() ??
                            l10n.sharedUnknownAgent,
                        style: textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: colorScheme.secondary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        cardData['verdict']?.toString() ?? "",
                        style: textTheme.bodyMedium?.copyWith(
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
                // Total Score Badge
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    shape: BoxShape.circle,
                    border: Border.all(color: colorScheme.primary, width: 2),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        cardData['totalScore'] != null
                            ? (cardData['totalScore'] is num
                                      ? (cardData['totalScore'] as num)
                                            .toDouble()
                                      : double.tryParse(
                                              cardData['totalScore'].toString(),
                                            ) ??
                                            0.0)
                                  .toStringAsFixed(1)
                            : "N/A",
                        style: textTheme.titleLarge?.copyWith(
                          color: colorScheme.onPrimaryContainer,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      Text(
                        l10n.scaleInfo(
                          (cardData['minScore'] as num?)?.toInt() ?? 1,
                          (cardData['maxScore'] as num?)?.toInt() ?? 5,
                        ),
                        style: textTheme.bodySmall?.copyWith(
                          color: colorScheme.onPrimaryContainer.withValues(
                            alpha: 0.7,
                          ),
                          fontSize: 8,
                        ),
                      ),
                    ],
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
                            .map(
                              (d) => RadarEntry(
                                value: (d['score'] as num?)?.toDouble() ?? 0.0,
                              ),
                            )
                            .toList(),
                        borderWidth: 2,
                      ),
                    ],
                    radarBackgroundColor: Colors.transparent,
                    borderData: FlBorderData(show: false),
                    radarBorderData: const BorderSide(
                      color: Colors.transparent,
                    ),
                    titlePositionPercentageOffset: 0.2,
                    titleTextStyle: textTheme.bodySmall?.copyWith(fontSize: 10),
                    getTitle: (index, angle) {
                      if (index >= dimensions.length)
                        return const RadarChartTitle(text: '');

                      final d = dimensions[index];
                      // strict translation of dimensionLabel key
                      final label = _translateDimension(
                        d['dimensionLabel']?.toString() ?? '',
                        l10n,
                      );

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
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Text(l10n.noDetailedData),
                ),
              ),

            // Detailed Breakdown List
            if (hasData) ...[
              const SizedBox(height: 24),
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  l10n.detailedBreakdown,
                  style: textTheme.titleSmall!.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              ...dimensions.map((d) {
                final label = _translateDimension(
                  d['dimensionLabel']?.toString() ?? '',
                  l10n,
                );
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
                        ((d['score'] as num?)?.toDouble() ?? 0.0)
                            .toStringAsFixed(0),
                        style: textTheme.titleMedium!.copyWith(
                          color: colorScheme.onPrimaryContainer,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    title: Text(
                      label,
                      style: textTheme.titleSmall!.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Padding(
                      padding: const EdgeInsets.only(top: 4.0),
                      child: Text(
                        (d['reasoning']?.toString() ?? '').replaceAll(
                          RegExp(r'^Havainto:\s*', caseSensitive: false),
                          '',
                        ),
                        style: textTheme.bodyMedium,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ],
          ],
        ),
      ),
    );
  }

  /// Translates the observation key sent by the backend logic matrices
  /// into localized UI strings per the "No-String" API Policy.
  String _translateDimension(String key, AppLocalizations l10n) {
    return switch (key) {
      'lblFidelity' => l10n.lblFidelity,
      'lblAbductiveReasoning' => l10n.lblAbductiveReasoning,
      'lblCredibility' => l10n.lblCredibility,
      'lblTextMetrics' => l10n.lblTextMetrics,
      'lblBias' => l10n.lblBias,
      'lblIntent' => l10n.lblIntent,
      'lblPsychProfile' => l10n.lblPsychProfile,
      'lblFactCheck' => l10n.lblFactCheck,
      'lblEthicalObservation' => l10n.lblEthicalObservation,
      'lblAuthenticity' => l10n.lblAuthenticity,
      'lblHeuristics' => l10n.lblHeuristics,
      'lblComplianceAnalysis' => l10n.lblComplianceAnalysis,
      'lblMethodologicalLog' => l10n.lblMethodologicalLog,
      'lblCognitiveLevel' => l10n.lblCognitiveLevel,
      'lblStrategicDepth' => l10n.lblStrategicDepth,
      'lblArguments' => l10n.lblArguments,
      'lblBloomScore' => l10n.lblBloomScore,
      'lblToulminScore' => l10n.lblToulminScore,
      'lblLogicMatrix' => l10n.lblLogicMatrix,
      'lblControlRatio' => l10n.lblControlRatio,
      'lblRoleAndPosition' => l10n.lblRoleAndPosition,
      'lblCriticalQuestions' => l10n.lblCriticalQuestions,
      'lblWaltonScheme' => l10n.lblWaltonScheme,
      'lblCausalAudit' => l10n.lblCausalAudit,
      'lblCounterfactualTest' => l10n.lblCounterfactualTest,
      'lblObservation' => l10n.lblObservation,
      'lblQuestion' => l10n.lblQuestion,
      'lblEvidenceHeld' => l10n.lblEvidenceHeld,
      // Fallback for legacy items that might contain plain text already
      _ => key.isNotEmpty ? key : l10n.errorUnknown,
    };
  }
}
