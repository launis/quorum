// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'xai_report.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ScoreCardItem _$ScoreCardItemFromJson(Map<String, dynamic> json) =>
    _ScoreCardItem(
      agentName: json['agent_name'] as String,
      totalScore: (json['total_score'] as num?)?.toDouble(),
      minScore: (json['min_score'] as num?)?.toInt(),
      maxScore: (json['max_score'] as num?)?.toInt(),
      verdict: json['verdict'] as String?,
      dimensions:
          (json['dimensions'] as List<dynamic>?)
              ?.map(
                (e) => DimensionResultItem.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const [],
    );

Map<String, dynamic> _$ScoreCardItemToJson(_ScoreCardItem instance) =>
    <String, dynamic>{
      'agent_name': instance.agentName,
      'total_score': instance.totalScore,
      'min_score': instance.minScore,
      'max_score': instance.maxScore,
      'verdict': instance.verdict,
      'dimensions': instance.dimensions,
    };

_XAIReport _$XAIReportFromJson(Map<String, dynamic> json) => _XAIReport(
  metadata: json['metadata'] as Map<String, dynamic>,
  metodologinenLoki: json['metodologinen_loki'] as String?,
  edellisenVaiheenValidointi: json['edellisen_vaiheen_validointi'] as String?,
  semanttinenTarkistussumma: json['semanttinen_tarkistussumma'] as String,
  executiveSummary: json['executive_summary'] as String?,
  analysisStrengths: json['analysis_strengths'] as String?,
  analysisWeaknesses: json['analysis_weaknesses'] as String?,
  analysisOpportunities: json['analysis_opportunities'] as String?,
  analysisRecommendations: json['analysis_recommendations'] as String?,
  finalVerdict: json['final_verdict'] as String?,
  confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
  xaiReportFormatted: json['xai_report_formatted'] as String?,
  comparisonData: json['comparison_data'] as Map<String, dynamic>?,
  scoreCards:
      (json['score_cards'] as List<dynamic>?)
          ?.map((e) => ScoreCardItem.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$XAIReportToJson(_XAIReport instance) =>
    <String, dynamic>{
      'metadata': instance.metadata,
      'metodologinen_loki': instance.metodologinenLoki,
      'edellisen_vaiheen_validointi': instance.edellisenVaiheenValidointi,
      'semanttinen_tarkistussumma': instance.semanttinenTarkistussumma,
      'executive_summary': instance.executiveSummary,
      'analysis_strengths': instance.analysisStrengths,
      'analysis_weaknesses': instance.analysisWeaknesses,
      'analysis_opportunities': instance.analysisOpportunities,
      'analysis_recommendations': instance.analysisRecommendations,
      'final_verdict': instance.finalVerdict,
      'confidence_score': instance.confidenceScore,
      'xai_report_formatted': instance.xaiReportFormatted,
      'comparison_data': instance.comparisonData,
      'score_cards': instance.scoreCards,
    };
