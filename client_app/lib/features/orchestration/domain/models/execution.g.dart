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
