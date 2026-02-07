import 'package:freezed_annotation/freezed_annotation.dart';

part 'evaluation_result.freezed.dart';
part 'evaluation_result.g.dart';

/// Result for a single dimension in the evaluation matrix.
@freezed
abstract class DimensionResultItem with _$DimensionResultItem {
  const factory DimensionResultItem({
    @JsonKey(name: 'dimension_id') required String dimensionId,
    @JsonKey(name: 'dimension_label') @Default('') String dimensionLabel,
    required double score, // Python allows int|float, Dart uses double
    required String reasoning,
  }) = _DimensionResultItem;

  factory DimensionResultItem.fromJson(Map<String, dynamic> json) =>
      _$DimensionResultItemFromJson(json);
}

/// Result of a dynamic evaluation.
///
/// Matches `BaseJSON` metadata + `EvaluationResult` fields from backend.
@freezed
abstract class EvaluationResult with _$EvaluationResult {
  const factory EvaluationResult({
    // --- BaseJSON Metadata ---
    required String luontiaika,
    required String agentti,
    required double vaihe,
    @Default('2.0') String versio,
    @JsonKey(name: 'suoritus_ymparisto') String? suoritusYmparisto,

    // --- BaseJSON Common Fields ---
    @JsonKey(name: 'reasoning_trace') String? reasoningTrace,
    @JsonKey(name: 'metodologinen_loki') required String metodologinenLoki,
    @JsonKey(name: 'edellisen_vaiheen_validointi')
    required String edellisenVaiheenValidointi,
    @JsonKey(name: 'semanttinen_tarkistussumma')
    required String semanttinenTarkistussumma,

    // --- EvaluationResult Specifics ---
    @JsonKey(name: 'matrix_id') required String matrixId,
    @JsonKey(name: 'scale_min') @Default(1) int scaleMin,
    @JsonKey(name: 'scale_max') @Default(5) int scaleMax,
    @JsonKey(name: 'total_score') required double totalScore,
    required List<DimensionResultItem> dimensions,
    @JsonKey(name: 'critical_findings')
    @Default([])
    List<String> criticalFindings,
  }) = _EvaluationResult;

  factory EvaluationResult.fromJson(Map<String, dynamic> json) =>
      _$EvaluationResultFromJson(json);
}
