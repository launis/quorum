// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ExecutionPending _$ExecutionPendingFromJson(Map<String, dynamic> json) =>
    ExecutionPending(
      id: json['execution_id'] as String,
      createdAt: DateTime.parse(json['start_time'] as String),
      workflowName: json['workflow_name'] as String?,
      organizationId: json['organization_id'] as String?,
      userId: json['user_id'] as String?,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      currentStepName: json['current_step_name'] as String?,
      status:
          $enumDecodeNullable(_$ExecutionStatusEnumMap, json['status']) ??
          ExecutionStatus.pending,
    );

Map<String, dynamic> _$ExecutionPendingToJson(ExecutionPending instance) =>
    <String, dynamic>{
      'execution_id': instance.id,
      'start_time': instance.createdAt.toIso8601String(),
      'workflow_name': instance.workflowName,
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'inputs': instance.inputs,
      'current_step_name': instance.currentStepName,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
    };

const _$ExecutionStatusEnumMap = {
  ExecutionStatus.pending: 'pending',
  ExecutionStatus.started: 'started',
  ExecutionStatus.running: 'running',
  ExecutionStatus.completed: 'completed',
  ExecutionStatus.failed: 'failed',
  ExecutionStatus.rejected: 'rejected',
  ExecutionStatus.interrupted: 'interrupted',
  ExecutionStatus.unknown: 'unknown',
};

ExecutionStarted _$ExecutionStartedFromJson(Map<String, dynamic> json) =>
    ExecutionStarted(
      id: json['execution_id'] as String,
      createdAt: DateTime.parse(json['start_time'] as String),
      workflowName: json['workflow_name'] as String?,
      organizationId: json['organization_id'] as String?,
      userId: json['user_id'] as String?,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      currentStepName: json['current_step_name'] as String?,
      status:
          $enumDecodeNullable(_$ExecutionStatusEnumMap, json['status']) ??
          ExecutionStatus.started,
    );

Map<String, dynamic> _$ExecutionStartedToJson(ExecutionStarted instance) =>
    <String, dynamic>{
      'execution_id': instance.id,
      'start_time': instance.createdAt.toIso8601String(),
      'workflow_name': instance.workflowName,
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'inputs': instance.inputs,
      'current_step_name': instance.currentStepName,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
    };

ExecutionRunning _$ExecutionRunningFromJson(Map<String, dynamic> json) =>
    ExecutionRunning(
      id: json['execution_id'] as String,
      createdAt: DateTime.parse(json['start_time'] as String),
      workflowName: json['workflow_name'] as String?,
      organizationId: json['organization_id'] as String?,
      userId: json['user_id'] as String?,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      currentStepName: json['current_step_name'] as String?,
      status:
          $enumDecodeNullable(_$ExecutionStatusEnumMap, json['status']) ??
          ExecutionStatus.running,
    );

Map<String, dynamic> _$ExecutionRunningToJson(ExecutionRunning instance) =>
    <String, dynamic>{
      'execution_id': instance.id,
      'start_time': instance.createdAt.toIso8601String(),
      'workflow_name': instance.workflowName,
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'inputs': instance.inputs,
      'current_step_name': instance.currentStepName,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
    };

ExecutionCompleted _$ExecutionCompletedFromJson(Map<String, dynamic> json) =>
    ExecutionCompleted(
      id: json['execution_id'] as String,
      createdAt: DateTime.parse(json['start_time'] as String),
      workflowName: json['workflow_name'] as String?,
      organizationId: json['organization_id'] as String?,
      userId: json['user_id'] as String?,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      currentStepName: json['current_step_name'] as String?,
      result: json['result'] as Map<String, dynamic>? ?? const {},
      xaiReport: json['xai_report_formatted'] as String?,
      auditResults:
          (json['audit_results'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(
              k,
              EvaluationResult.fromJson(e as Map<String, dynamic>),
            ),
          ) ??
          const {},
      usage: json['usage'] as Map<String, dynamic>? ?? const {},
      stepGuard: json['step_guard'] as Map<String, dynamic>?,
      stepAnalyst: json['step_analyst'] as Map<String, dynamic>?,
      stepProfiler: json['step_profiler'] as Map<String, dynamic>?,
      stepLogician: json['step_logician'] as Map<String, dynamic>?,
      stepFalsifier: json['step_falsifier'] as Map<String, dynamic>?,
      stepOverseer: json['step_overseer'] as Map<String, dynamic>?,
      stepCausal: json['step_causal'] as Map<String, dynamic>?,
      stepDetector: json['step_detector'] as Map<String, dynamic>?,
      stepJudge: json['step_judge'] as Map<String, dynamic>?,
      stepJudgeCognitive: json['step_judge_cognitive'] as Map<String, dynamic>?,
      stepArchivist: json['step_archivist'] as Map<String, dynamic>?,
      stepCoach: json['step_coach'] as Map<String, dynamic>?,
      stepInteraction: json['step_interaction'] as Map<String, dynamic>?,
      stepPanel: json['step_panel'] as Map<String, dynamic>?,
      status:
          $enumDecodeNullable(_$ExecutionStatusEnumMap, json['status']) ??
          ExecutionStatus.completed,
    );

Map<String, dynamic> _$ExecutionCompletedToJson(ExecutionCompleted instance) =>
    <String, dynamic>{
      'execution_id': instance.id,
      'start_time': instance.createdAt.toIso8601String(),
      'workflow_name': instance.workflowName,
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'inputs': instance.inputs,
      'current_step_name': instance.currentStepName,
      'result': instance.result,
      'xai_report_formatted': instance.xaiReport,
      'audit_results': instance.auditResults,
      'usage': instance.usage,
      'step_guard': instance.stepGuard,
      'step_analyst': instance.stepAnalyst,
      'step_profiler': instance.stepProfiler,
      'step_logician': instance.stepLogician,
      'step_falsifier': instance.stepFalsifier,
      'step_overseer': instance.stepOverseer,
      'step_causal': instance.stepCausal,
      'step_detector': instance.stepDetector,
      'step_judge': instance.stepJudge,
      'step_judge_cognitive': instance.stepJudgeCognitive,
      'step_archivist': instance.stepArchivist,
      'step_coach': instance.stepCoach,
      'step_interaction': instance.stepInteraction,
      'step_panel': instance.stepPanel,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
    };

ExecutionFailed _$ExecutionFailedFromJson(Map<String, dynamic> json) =>
    ExecutionFailed(
      id: json['execution_id'] as String,
      createdAt: DateTime.parse(json['start_time'] as String),
      workflowName: json['workflow_name'] as String?,
      organizationId: json['organization_id'] as String?,
      userId: json['user_id'] as String?,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      currentStepName: json['current_step_name'] as String?,
      error: json['error'] as String?,
      status:
          $enumDecodeNullable(_$ExecutionStatusEnumMap, json['status']) ??
          ExecutionStatus.failed,
    );

Map<String, dynamic> _$ExecutionFailedToJson(ExecutionFailed instance) =>
    <String, dynamic>{
      'execution_id': instance.id,
      'start_time': instance.createdAt.toIso8601String(),
      'workflow_name': instance.workflowName,
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'inputs': instance.inputs,
      'current_step_name': instance.currentStepName,
      'error': instance.error,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
    };

ExecutionUnknown _$ExecutionUnknownFromJson(Map<String, dynamic> json) =>
    ExecutionUnknown(
      id: json['execution_id'] as String,
      createdAt: DateTime.parse(json['start_time'] as String),
      workflowName: json['workflow_name'] as String?,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      currentStepName: json['current_step_name'] as String?,
      status:
          $enumDecodeNullable(_$ExecutionStatusEnumMap, json['status']) ??
          ExecutionStatus.unknown,
      result: json['result'] as Map<String, dynamic>?,
      error: json['error'] as String?,
    );

Map<String, dynamic> _$ExecutionUnknownToJson(ExecutionUnknown instance) =>
    <String, dynamic>{
      'execution_id': instance.id,
      'start_time': instance.createdAt.toIso8601String(),
      'workflow_name': instance.workflowName,
      'inputs': instance.inputs,
      'current_step_name': instance.currentStepName,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
      'result': instance.result,
      'error': instance.error,
    };
