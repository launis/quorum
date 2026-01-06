// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Execution _$ExecutionFromJson(Map<String, dynamic> json) => Execution(
  executionId: json['execution_id'] as String?,
  workflowId: json['workflow_id'] as String?,
  status: json['status'] as String?,
  inputs: json['inputs'] as Map<String, dynamic>? ?? {},
  startTime: json['start_time'] as String?,
  endTime: json['end_time'] as String?,
  organizationId: json['organization_id'] as String?,
);

Map<String, dynamic> _$ExecutionToJson(Execution instance) => <String, dynamic>{
  'execution_id': instance.executionId,
  'workflow_id': instance.workflowId,
  'status': instance.status,
  'inputs': instance.inputs,
  'start_time': instance.startTime,
  'end_time': instance.endTime,
  'organization_id': instance.organizationId,
};
