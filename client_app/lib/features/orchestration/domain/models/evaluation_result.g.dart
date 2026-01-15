// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'evaluation_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DimensionResultItem _$DimensionResultItemFromJson(Map<String, dynamic> json) =>
    _DimensionResultItem(
      dimensionId: json['dimension_id'] as String,
      score: (json['score'] as num).toDouble(),
      reasoning: json['reasoning'] as String,
    );

Map<String, dynamic> _$DimensionResultItemToJson(
  _DimensionResultItem instance,
) => <String, dynamic>{
  'dimension_id': instance.dimensionId,
  'score': instance.score,
  'reasoning': instance.reasoning,
};

_EvaluationResult _$EvaluationResultFromJson(
  Map<String, dynamic> json,
) => _EvaluationResult(
  luontiaika: json['luontiaika'] as String,
  agentti: json['agentti'] as String,
  vaihe: (json['vaihe'] as num).toDouble(),
  versio: json['versio'] as String? ?? '2.0',
  suoritusYmparisto: json['suoritus_ymparisto'] as String?,
  reasoningTrace: json['reasoning_trace'] as String?,
  metodologinenLoki: json['metodologinen_loki'] as String,
  edellisenVaiheenValidointi: json['edellisen_vaiheen_validointi'] as String,
  semanttinenTarkistussumma: json['semanttinen_tarkistussumma'] as String,
  matrixId: json['matrix_id'] as String,
  scaleMin: (json['scale_min'] as num?)?.toInt() ?? 1,
  scaleMax: (json['scale_max'] as num?)?.toInt() ?? 5,
  totalScore: (json['total_score'] as num).toDouble(),
  dimensions:
      (json['dimensions'] as List<dynamic>)
          .map((e) => DimensionResultItem.fromJson(e as Map<String, dynamic>))
          .toList(),
  criticalFindings:
      (json['critical_findings'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
);

Map<String, dynamic> _$EvaluationResultToJson(_EvaluationResult instance) =>
    <String, dynamic>{
      'luontiaika': instance.luontiaika,
      'agentti': instance.agentti,
      'vaihe': instance.vaihe,
      'versio': instance.versio,
      'suoritus_ymparisto': instance.suoritusYmparisto,
      'reasoning_trace': instance.reasoningTrace,
      'metodologinen_loki': instance.metodologinenLoki,
      'edellisen_vaiheen_validointi': instance.edellisenVaiheenValidointi,
      'semanttinen_tarkistussumma': instance.semanttinenTarkistussumma,
      'matrix_id': instance.matrixId,
      'scale_min': instance.scaleMin,
      'scale_max': instance.scaleMax,
      'total_score': instance.totalScore,
      'dimensions': instance.dimensions,
      'critical_findings': instance.criticalFindings,
    };
