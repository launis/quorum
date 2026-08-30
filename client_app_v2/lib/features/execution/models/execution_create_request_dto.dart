// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_create_request_dto.freezed.dart';
part 'execution_create_request_dto.g.dart';

/// Strictly typed request DTO for starting a workflow execution.
/// Matches backend `ExecutionCreate` model in `backend_v2/models/v2_core.py`.
@Freezed(equal: false)
abstract class ExecutionCreateRequestDto with _$ExecutionCreateRequestDto {
  const ExecutionCreateRequestDto._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionCreateRequestDto({
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'target_locale') required String targetLocale,
    @JsonKey(name: 'raw_inputs') @Default({}) Map<String, dynamic> rawInputs,
    @JsonKey(name: 'profile_id') String? profileId,
    @JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy,
  }) = _ExecutionCreateRequestDto;

  /// Instantiates a strictly typed [ExecutionCreateRequestDto] from raw JSON.
  factory ExecutionCreateRequestDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionCreateRequestDtoFromJson(json);
}
