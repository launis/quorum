import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_step.freezed.dart';
part 'workflow_step.g.dart';

/// Represents a single step in a workflow execution.
///
/// Refreshed generation.
/// Mirrors `backend/models/workflow.py` -> `WorkflowStep`.
@freezed
abstract class WorkflowStep with _$WorkflowStep {
  const factory WorkflowStep({
    /// Unique step identifier, e.g., 'safety_check'
    required String id,

    /// Legacy human-readable identifier
    String? slug,

    /// Human-readable name of the step
    @JsonKey(defaultValue: 'Unnamed Step') @Default('Unnamed Step') String name,

    /// Registry Task Name (matches @register_task name)
    @JsonKey(name: 'task_key') required String taskKey,

    /// Maps task inputs to state values. Example: {'text': '$inputs.history_text'}
    @Default({}) Map<String, String> inputs,

    /// Optional static config for the task
    @Default({}) Map<String, dynamic> config,
  }) = _WorkflowStep;

  factory WorkflowStep.fromJson(Map<String, dynamic> json) =>
      _$WorkflowStepFromJson(json);
}
