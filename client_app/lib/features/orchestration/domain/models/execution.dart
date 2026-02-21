import 'package:client_app/features/orchestration/domain/models/evaluation_result.dart';
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
/// - rejected: Rejected by quota or policy.
/// - interrupted: Stopped mid-execution.
enum ExecutionStatus {
  pending,
  started,
  running,
  completed,
  failed,
  rejected,
  interrupted,
  cancelling,
  unknown,
}

/// A strict, immutable representation of an Audit Workflow Execution.
///
/// This model uses a Sealed Class (Union) pattern discriminated by the `status` field.
/// This ensures type-safe access to fields that only exist in certain states
/// (e.g., `result` is only available when `status` is `completed`).
///
/// Business Logic:
/// - `id`: The unique UUID of the execution (maps to backend `execution_id`).
/// - `inputs`: The initial data provided to the workflow.
/// - `result`: The final output (e.g., XAI Report), only present on completion.
@Freezed(unionKey: 'status', unionValueCase: FreezedUnionCase.snake)
sealed class Execution with _$Execution {
  /// State: Execution is queued or initialized.
  const factory Execution.pending({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    @Default(ExecutionStatus.pending) ExecutionStatus status,
  }) = ExecutionPending;

  /// State: Execution has started but is not yet processing steps (or early initialization).
  const factory Execution.started({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    @Default(ExecutionStatus.started) ExecutionStatus status,
  }) = ExecutionStarted;

  // ... (keeping other factories as they are, assume tool handles text correctly) ...
  // Wait, I need to be careful not to delete the middle of the file.
  // The tool instructions say: "TargetContent... This must be a unique substring".
  // I should split this into two edits or use multi_replace.
  // Actually, I just need to remove the annotation on line ~38 and update line ~109.
  // Let's use multi_replace for safety.

  /// State: Execution is actively processing steps.
  const factory Execution.running({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    @Default(ExecutionStatus.running) ExecutionStatus status,
  }) = ExecutionRunning;

  /// State: Execution has finished successfully.
  ///
  /// Contains the [result] payload.
  const factory Execution.completed({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,

    /// The final output of the workflow (e.g., the Report object).
    /// Only available in completed state.
    @JsonKey(name: 'results') @Default({}) Map<String, dynamic> result,

    /// Optional formatted markdown report, if pre-rendered.
    @JsonKey(name: 'xai_report_formatted') String? xaiReport,

    /// Dynamic Evaluation Results (New Multi-Matrix System)
    /// Key = Step ID (e.g. "step_judge_cognitive")
    @JsonKey(name: 'audit_results')
    @Default({})
    Map<String, EvaluationResult> auditResults,

    /// Usage Metrics (Cost Tracking)
    @Default({}) Map<String, dynamic> usage,

    /// Agent Outputs (Typed as Maps for now, or generic structures)
    @JsonKey(name: 'step_guard') Map<String, dynamic>? stepGuard,
    @JsonKey(name: 'step_analyst') Map<String, dynamic>? stepAnalyst,
    @JsonKey(name: 'step_profiler') Map<String, dynamic>? stepProfiler,
    @JsonKey(name: 'step_logician') Map<String, dynamic>? stepLogician,
    @JsonKey(name: 'step_falsifier') Map<String, dynamic>? stepFalsifier,
    @JsonKey(name: 'step_overseer') Map<String, dynamic>? stepOverseer,
    @JsonKey(name: 'step_causal') Map<String, dynamic>? stepCausal,
    @JsonKey(name: 'step_detector') Map<String, dynamic>? stepDetector,
    @JsonKey(name: 'step_judge') Map<String, dynamic>? stepJudge,
    @JsonKey(name: 'step_judge_cognitive')
    Map<String, dynamic>? stepJudgeCognitive,
    @JsonKey(name: 'step_archivist') Map<String, dynamic>? stepArchivist,
    @JsonKey(name: 'step_coach') Map<String, dynamic>? stepCoach,
    @JsonKey(name: 'step_interaction') Map<String, dynamic>? stepInteraction,
    @JsonKey(name: 'step_panel') Map<String, dynamic>? stepPanel,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,

    @Default(ExecutionStatus.completed) ExecutionStatus status,
  }) = ExecutionCompleted;

  /// State: Execution was rejected.
  const factory Execution.rejected({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    String? error,
    @Default(ExecutionStatus.rejected) ExecutionStatus status,
  }) = ExecutionRejected;

  /// State: Execution failed or was rejected.
  const factory Execution.failed({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,

    /// Error message or failure reason.
    String? error,
    @Default(ExecutionStatus.failed) ExecutionStatus status,
  }) = ExecutionFailed;

  /// State: Execution was interrupted.
  const factory Execution.interrupted({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    String? error,
    @Default(ExecutionStatus.interrupted) ExecutionStatus status,
  }) = ExecutionInterrupted;

  /// State: Execution is being cancelled.
  const factory Execution.cancelling({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    @Default(ExecutionStatus.cancelling) ExecutionStatus status,
  }) = ExecutionCancelling;

  /// Fallback for unknown states or future backend updates.
  const factory Execution.unknown({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'started_at') required DateTime createdAt,
    @JsonKey(name: 'workflow_name') String? workflowName,
    @Default({}) Map<String, dynamic> inputs,
    @JsonKey(name: 'current_step_name') String? currentStepName,
    @JsonKey(name: 'current_step_index') int? currentStepIndex,
    @JsonKey(name: 'total_steps') int? totalSteps,
    @JsonKey(name: 'workflow_steps') List<String>? workflowSteps,
    @Default(ExecutionStatus.unknown) ExecutionStatus status,
    Map<String, dynamic>? result,
    String? error,
  }) = ExecutionUnknown;

  factory Execution.fromJson(Map<String, dynamic> json) =>
      _$ExecutionFromJson(json);
}
