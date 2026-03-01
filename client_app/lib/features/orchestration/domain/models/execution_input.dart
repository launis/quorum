import 'package:client_app/features/orchestration/domain/models/execution_file.dart';
import 'package:client_app/features/orchestration/domain/models/guided_reflection.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_input.freezed.dart';
part 'execution_input.g.dart';

/// Payload for starting a new execution.
///
/// Maps to `WorkflowExecutionRequest` in the backend.
@freezed
sealed class ExecutionInput with _$ExecutionInput {
  const factory ExecutionInput({
    /// The UUID of the workflow definition to instantiate.
    @JsonKey(name: 'workflow_id') required String workflowId,

    /// Key-value pairs representing the initial input state (e.g. source text).
    @Default({}) Map<String, dynamic> inputs,

    /// File attachments to be uploaded via Multipart request.
    /// Not serialized to JSON as the repository handles FormData construction manually.
    @Default({})
    @JsonKey(includeToJson: false)
    Map<String, ExecutionFile> files,

    /// Optional structured guided reflection form data
    @JsonKey(name: 'guided_reflection') GuidedReflectionDTO? guidedReflection,
  }) = _ExecutionInput;

  factory ExecutionInput.fromJson(Map<String, dynamic> json) =>
      _$ExecutionInputFromJson(json);
}
