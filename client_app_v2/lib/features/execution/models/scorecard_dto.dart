// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'scorecard_dto.freezed.dart';
part 'scorecard_dto.g.dart';

@Freezed(equal: false)
abstract class ScorecardResponseDto with _$ScorecardResponseDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ScorecardResponseDto({
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'global_average') double? globalAverage,
    @JsonKey(name: 'evaluative_matrices')
    @Default([])
    List<MatrixScorecardRowDto> evaluativeMatrices,
    @JsonKey(name: 'informational_matrices')
    @Default([])
    List<MatrixScorecardRowDto> informationalMatrices,
  }) = _ScorecardResponseDto;

  factory ScorecardResponseDto.fromJson(Map<String, dynamic> json) =>
      _$ScorecardResponseDtoFromJson(json);
}

@Freezed(equal: false)
abstract class MatrixScorecardRowDto with _$MatrixScorecardRowDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixScorecardRowDto({
    @JsonKey(name: 'block_id') required String blockId,
    @JsonKey(name: 'label_fi') required String labelFi,
    @JsonKey(name: 'label_en') required String labelEn,
    required double score,
    @JsonKey(name: 'scale_max') double? scaleMax,
    @JsonKey(name: 'normalized_score') double? normalizedScore,
    @JsonKey(name: 'true_atoms') int? trueAtoms,
    @JsonKey(name: 'total_atoms') int? totalAtoms,
    @Default('') String justification,
    @JsonKey(name: 'missing_context') @Default('') String missingContext,
    @JsonKey(name: 'level_breakdown')
    Map<String, Map<String, int>>? levelBreakdown,
    @JsonKey(name: 'is_evaluative') @Default(true) bool isEvaluative,
  }) = _MatrixScorecardRowDto;

  factory MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) =>
      _$MatrixScorecardRowDtoFromJson(json);
}
