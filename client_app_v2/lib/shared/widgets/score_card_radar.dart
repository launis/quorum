import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

@immutable
class ScoreCardDimensionData {
  final String dimensionLabel;
  final double? score;
  final String reasoning;

  const ScoreCardDimensionData({
    required this.dimensionLabel,
    required this.score,
    this.reasoning = '',
  });
}

@immutable
class ScoreCardRadarData {
  final String? agentName;
  final String? verdict;
  final double? totalScore;
  final int minScore;
  final int maxScore;
  final List<ScoreCardDimensionData> dimensions;
  final bool isCorrupted;

  const ScoreCardRadarData({
    this.agentName,
    this.verdict,
    this.totalScore,
    this.minScore = 1,
    this.maxScore = 5,
    this.dimensions = const <ScoreCardDimensionData>[],
    this.isCorrupted = false,
  });
}

class ScoreCardRadar extends ConsumerWidget {
  final ScoreCardRadarData cardData;

  const ScoreCardRadar({super.key, required this.cardData});

  static const int _minRadarDimensionsCount = 3;
  static const double _badgeDimension = 60.0;
  static const double _avatarDimension = 40.0;
  static const double _radarHeight = 200.0;
  static const double _titlePositionOffset = 0.2;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    try {
      if (cardData.isCorrupted) {
        throw AppException.validation(
          'Fail-Fast: ScoreCardRadar cardData is corrupted.',
        );
      }

      final dimensionsList = cardData.dimensions;
      final dimensions =
          <({String dimensionLabel, double score, String reasoning})>[];

      for (var i = 0; i < dimensionsList.length; i++) {
        final item = dimensionsList[i];

        final rawLabel = item.dimensionLabel.trim();
        if (rawLabel.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: ScoreCardRadar dimension[$i] dimensionLabel cannot be empty.',
          );
        }

        final parsedScore = item.score;
        if (parsedScore == null) {
          throw AppException.validation(
            'Fail-Fast: ScoreCardRadar dimension[$i] score is required.',
          );
        }

        if (parsedScore.isNaN || parsedScore.isInfinite) {
          throw AppException.validation(
            'Fail-Fast: ScoreCardRadar dimension[$i] score must be finite.',
          );
        }

        final rawReasoning = item.reasoning;
        dimensions.add((
          dimensionLabel: rawLabel,
          score: parsedScore,
          reasoning: rawReasoning.replaceAll(
            RegExp(r'^Havainto:\s*', caseSensitive: false),
            '',
          ),
        ));
      }

      final minScore = cardData.minScore;
      final maxScore = cardData.maxScore;
      if (maxScore <= minScore) {
        throw AppException.validation(
          'Fail-Fast: ScoreCardRadar maxScore ($maxScore) must be greater than minScore ($minScore).',
        );
      }

      final totalScoreDisplay = _resolveTotalScoreDisplay(
        cardData.totalScore,
        l10n,
      );

      final hasData = dimensions.isNotEmpty;
      final canShowRadar = dimensions.length >= _minRadarDimensionsCount;
      final transparentColor = colorScheme.surface.withValues(alpha: 0.0);

      final rawAgentName = cardData.agentName?.trim() ?? '';
      final agentName = rawAgentName.isNotEmpty
          ? rawAgentName
          : l10n.sharedUnknownAgent;
      final verdict = cardData.verdict?.trim() ?? '';

      return Card(
        elevation: AppSpacing.s4,
        margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          agentName,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: colorScheme.secondary,
                          ),
                        ),
                        if (verdict.isNotEmpty) ...[
                          AppSpacing.h4,
                          Text(
                            verdict,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: textTheme.bodyMedium?.copyWith(
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  AppSpacing.w12,
                  Container(
                    width: _badgeDimension,
                    height: _badgeDimension,
                    decoration: BoxDecoration(
                      color: colorScheme.primaryContainer,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: colorScheme.primary,
                        width: AppSpacing.s2,
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          totalScoreDisplay,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: textTheme.titleMedium?.copyWith(
                            color: colorScheme.onPrimaryContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          l10n.scaleInfo(minScore, maxScore),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: textTheme.labelSmall?.copyWith(
                            color: colorScheme.onPrimaryContainer.withValues(
                              alpha: 0.7,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const Divider(height: AppSpacing.s24),
              if (canShowRadar)
                SizedBox(
                  height: _radarHeight,
                  child: ExcludeSemantics(
                    child: RadarChart(
                      RadarChartData(
                        radarTouchData: RadarTouchData(enabled: false),
                        dataSets: [
                          RadarDataSet(
                            fillColor: colorScheme.primary.withValues(
                              alpha: 0.2,
                            ),
                            borderColor: colorScheme.primary,
                            entryRadius: AppSpacing.s2,
                            dataEntries: [
                              for (final d in dimensions)
                                RadarEntry(value: d.score),
                            ],
                            borderWidth: AppSpacing.s2,
                          ),
                        ],
                        radarBackgroundColor: transparentColor,
                        borderData: FlBorderData(show: false),
                        radarBorderData: BorderSide(color: transparentColor),
                        titlePositionPercentageOffset: _titlePositionOffset,
                        titleTextStyle: textTheme.labelSmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                        getTitle: (index, angle) {
                          if (index >= dimensions.length) {
                            return const RadarChartTitle(text: '');
                          }
                          final d = dimensions[index];
                          final label = _translateDimension(
                            d.dimensionLabel,
                            l10n,
                          );
                          return RadarChartTitle(text: label);
                        },
                        tickCount: 1,
                        ticksTextStyle: textTheme.labelSmall?.copyWith(
                          color: transparentColor,
                        ),
                        gridBorderData: BorderSide(
                          color: colorScheme.outlineVariant.withValues(
                            alpha: 0.2,
                          ),
                        ),
                      ),
                    ),
                  ),
                )
              else if (!hasData)
                Center(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: AppSpacing.s24,
                    ),
                    child: Text(
                      l10n.noDetailedData,
                      style: textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ),
              if (hasData) ...[
                AppSpacing.h24,
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    l10n.detailedBreakdown,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                AppSpacing.h8,
                for (final d in dimensions)
                  Container(
                    margin: const EdgeInsets.only(bottom: AppSpacing.s8),
                    decoration: BoxDecoration(
                      color: colorScheme.surfaceContainer,
                      borderRadius: BorderRadius.circular(AppSpacing.s8),
                      border: Border.all(color: colorScheme.outlineVariant),
                    ),
                    child: ListTile(
                      leading: Container(
                        width: _avatarDimension,
                        height: _avatarDimension,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: colorScheme.primaryContainer,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          d.score.toStringAsFixed(1),
                          style: textTheme.titleMedium?.copyWith(
                            color: colorScheme.onPrimaryContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      title: Text(
                        _translateDimension(d.dimensionLabel, l10n),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: AppSpacing.s4),
                        child: Text(d.reasoning, style: textTheme.bodyMedium),
                      ),
                    ),
                  ),
              ],
            ],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ScoreCardRadar',
            'VALIDATION_FAILED: Failed to render ScoreCardRadar',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  String _resolveTotalScoreDisplay(double? rawTotal, AppLocalizations l10n) {
    if (rawTotal == null) {
      return l10n.dataUnavailable;
    }
    if (rawTotal.isNaN || rawTotal.isInfinite) {
      throw AppException.validation(
        'Fail-Fast: ScoreCardRadar totalScore must be finite.',
      );
    }
    return rawTotal.toStringAsFixed(1);
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
      _ => key.isNotEmpty ? key : l10n.errorUnknown,
    };
  }
}
