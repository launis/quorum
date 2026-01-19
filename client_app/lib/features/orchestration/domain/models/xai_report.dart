import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/features/orchestration/domain/models/evaluation_result.dart';

part 'xai_report.freezed.dart';
part 'xai_report.g.dart';

/// Represents a single scorecard from a judge.
@freezed
abstract class ScoreCardItem with _$ScoreCardItem {
  const factory ScoreCardItem({
    @JsonKey(name: 'agent_name') required String agentName,
    @JsonKey(name: 'total_score') required double totalScore,
    @JsonKey(name: 'max_score') @Default(5) int maxScore,
    required String verdict,
    @Default([]) List<DimensionResultItem> dimensions,
  }) = _ScoreCardItem;

  factory ScoreCardItem.fromJson(Map<String, dynamic> json) =>
      _$ScoreCardItemFromJson(json);
}

/// The main XAI Report model.
@freezed
abstract class XAIReport with _$XAIReport {
  const factory XAIReport({
    // --- BaseJSON Metadata ---
    required Map<String, dynamic> metadata,
    @JsonKey(name: 'metodologinen_loki') required String metodologinenLoki,
    @JsonKey(name: 'edellisen_vaiheen_validointi')
    required String edellisenVaiheenValidointi,
    @JsonKey(name: 'semanttinen_tarkistussumma')
    required String semanttinenTarkistussumma,

    // --- Report Fields ---
    @JsonKey(name: 'executive_summary') required String executiveSummary,
    @JsonKey(name: 'analysis_strengths') required String analysisStrengths,
    @JsonKey(name: 'analysis_weaknesses') required String analysisWeaknesses,
    @JsonKey(name: 'analysis_opportunities') required String analysisOpportunities,
    @JsonKey(name: 'analysis_recommendations') required String analysisRecommendations,
    @JsonKey(name: 'final_verdict') required String finalVerdict,
    @JsonKey(name: 'confidence_score') required double confidenceScore,
    
    @JsonKey(name: 'xai_report_formatted') String? xaiReportFormatted,
    @JsonKey(name: 'comparison_data') Map<String, dynamic>? comparisonData,
    
    // --- New Aggregated Scores ---
    @JsonKey(name: 'score_cards') 
    @Default([]) 
    List<ScoreCardItem> scoreCards,
  }) = _XAIReport;

  factory XAIReport.fromJson(Map<String, dynamic> json) =>
      _$XAIReportFromJson(json);
}
