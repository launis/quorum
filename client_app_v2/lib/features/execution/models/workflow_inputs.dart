import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_inputs.freezed.dart';
part 'workflow_inputs.g.dart';

/// Strongly typed dynamic inputs container for client DAG execution (SSOT).
@Freezed(equal: false)
abstract class WorkflowInputs with _$WorkflowInputs {
  const WorkflowInputs._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory WorkflowInputs({
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @JsonKey(name: 'simulation_mode') @Default(false) bool simulationMode,
    @Default('en') String language,
    @JsonKey(name: 'dynamic_inputs')
    @Default({})
    Map<String, dynamic> dynamicInputs,
  }) = _WorkflowInputs;

  /// Instantiates a strictly typed [WorkflowInputs] from raw JSON.
  factory WorkflowInputs.fromJson(Map<String, dynamic> json) =>
      _$WorkflowInputsFromJson(json);
}
