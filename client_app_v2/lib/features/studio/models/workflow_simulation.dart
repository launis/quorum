import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_simulation.freezed.dart';
part 'workflow_simulation.g.dart';

/// Full structural DAG validation result for complex multi-agent workflows.
///
/// Matches backend SSOT `WorkflowSimulationResponse` in `backend_v2/models/dtos/studio.py`.
@Freezed(equal: false)
abstract class WorkflowSimulationResponse with _$WorkflowSimulationResponse {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory WorkflowSimulationResponse({
    @Default(true) bool valid,
    @Default([]) List<String> errors,
    @JsonKey(name: 'step_status') @Default({}) Map<String, String> stepStatus,
    @JsonKey(name: 'execution_order') @Default([]) List<String> executionOrder,
    @Default({}) Map<String, dynamic> trace,
  }) = _WorkflowSimulationResponse;

  factory WorkflowSimulationResponse.fromJson(Map<String, dynamic> json) =>
      _$WorkflowSimulationResponseFromJson(json);
}
