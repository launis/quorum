import 'package:freezed_annotation/freezed_annotation.dart';
import 'workflow.dart';

part 'workflow_ui_schema.freezed.dart';
part 'workflow_ui_schema.g.dart';

/// Schema response for dynamic frontend rendering of workflow input expectations.
///
/// Matches backend SSOT `WorkflowSchemaResponseDTO` in `backend_v2/models/dtos/workflow_schema.py`.
@Freezed(equal: false)
abstract class WorkflowUiSchema with _$WorkflowUiSchema {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory WorkflowUiSchema({
    @JsonKey(name: 'expected_inputs')
    @Default([])
    List<ExpectedInput> expectedInputs,
  }) = _WorkflowUiSchema;

  factory WorkflowUiSchema.fromJson(Map<String, dynamic> json) =>
      _$WorkflowUiSchemaFromJson(json);
}
