// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

import 'matrix_scorecard_dto.dart';
export 'matrix_scorecard_dto.dart';

part 'scorecard_dto.freezed.dart';
part 'scorecard_dto.g.dart';

@Deprecated('Use ReportDataDto. Removed in C3.')
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
