import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_create_request_dto.freezed.dart';
part 'execution_create_request_dto.g.dart';

/// Strictly typed request DTO for starting a workflow execution.
/// Matches backend `ExecutionCreate` model in `backend_v2/models/domain/execution.py`.
@Freezed(equal: false)
abstract class ExecutionCreateRequestDto with _$ExecutionCreateRequestDto {
  const ExecutionCreateRequestDto._();

  // Replace Map<String, Object?> rawInputs with typed WorkflowInputs DTO
  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionCreateRequestDto({
    @JsonKey(name: 'workflow_id')
    @StrictOpaqueIdConverter()
    required String workflowId,
    @JsonKey(name: 'target_locale') required String targetLocale,
    @JsonKey(name: 'raw_inputs')
    @Default(WorkflowInputs())
    WorkflowInputs rawInputs,
    @JsonKey(name: 'profile_id') String? profileId,
    @JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy,
  }) = _ExecutionCreateRequestDto;

  /// Instantiates a strictly typed [ExecutionCreateRequestDto] from raw JSON.
  factory ExecutionCreateRequestDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionCreateRequestDtoFromJson(json);
}
