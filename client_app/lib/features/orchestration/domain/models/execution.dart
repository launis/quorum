import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution.freezed.dart';
part 'execution.g.dart';

/// Represents the status of an Audit Execution.
///
/// Mirrors the backend's status machine:
/// - pending: Created but not started.
/// - running: Currently executing a step.
/// - completed: Finished successfully with a result.
/// - failed: Terminated due to an error.
enum ExecutionStatus { pending, running, completed, failed, unknown }

/// A strict, immutable representation of an Audit Workflow Execution.
///
/// This model uses a Sealed Class (Union) pattern discriminated by the [status] field.
/// This ensures type-safe access to fields that only exist in certain states
/// (e.g., [result] is only available when [status] is [completed]).
///
/// Business Logic:
/// - [id]: The unique UUID of the execution (maps to backend `execution_id`).
/// - [inputs]: The initial data provided to the workflow.
/// - result: The final output (e.g., XAI Report), only present on completion.
@Freezed(unionKey: 'status', unionValueCase: FreezedUnionCase.snake)
sealed class Execution with _$Execution {
  /// State: Execution is queued or initialized.
  const factory Execution.pending({
    @JsonKey(name: 'execution_id') required String id,
    @JsonKey(name: 'start_time') required DateTime createdAt,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @Default(ExecutionStatus.pending) ExecutionStatus status,
  }) = ExecutionPending;

  /// State: Execution is actively processing steps.
  const factory Execution.running({
    @JsonKey(name: 'execution_id') required String id,
    @JsonKey(name: 'start_time') required DateTime createdAt,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @Default(ExecutionStatus.running) ExecutionStatus status,
  }) = ExecutionRunning;

  /// State: Execution has finished successfully.
  ///
  /// Contains the [result] payload.
  const factory Execution.completed({
    @JsonKey(name: 'execution_id') required String id,
    @JsonKey(name: 'start_time') required DateTime createdAt,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,

    /// The final output of the workflow (e.g., the Report object).
    /// Only available in completed state.
    @Default({}) Map<String, dynamic> result,

    /// Optional formatted markdown report, if pre-rendered.
    @JsonKey(name: 'xai_report_formatted') String? xaiReport,

    @Default(ExecutionStatus.completed) ExecutionStatus status,
  }) = ExecutionCompleted;

  /// State: Execution failed or was rejected.
  const factory Execution.failed({
    @JsonKey(name: 'execution_id') required String id,
    @JsonKey(name: 'start_time') required DateTime createdAt,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,

    /// Error message or failure reason.
    String? error,

    @Default(ExecutionStatus.failed) ExecutionStatus status,
  }) = ExecutionFailed;

  /// Fallback for unknown states or future backend updates.
  const factory Execution.unknown({
    @JsonKey(name: 'execution_id') required String id,
    @JsonKey(name: 'start_time') required DateTime createdAt,
    @Default(ExecutionStatus.unknown) ExecutionStatus status,
    Map<String, dynamic>? result,
    String? error,
  }) = ExecutionUnknown;

  factory Execution.fromJson(Map<String, dynamic> json) =>
      _$ExecutionFromJson(json);
}
