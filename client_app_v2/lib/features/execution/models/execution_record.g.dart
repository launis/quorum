// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_record.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionRecord _$ExecutionRecordFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionRecord',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'workflow_id',
        'status',
        'trace_version',
        'strictness_level',
        'created_at',
        'cost_estimate',
        'metadata',
        'error',
        'is_resumable',
        'frozen_context',
        'step_states',
        'results',
        'report_data',
      ],
    );
    final val = _ExecutionRecord(
      id: $checkedConvert('id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      status: $checkedConvert('status', (v) => _statusFromJson(v as String)),
      traceVersion: $checkedConvert(
        'trace_version',
        (v) => _traceVersionFromJson(v),
      ),
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt(),
      ),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      costEstimate: $checkedConvert(
        'cost_estimate',
        (v) => (v as num?)?.toDouble(),
      ),
      metadata: $checkedConvert('metadata', (v) => v as Map<String, dynamic>?),
      error: $checkedConvert('error', (v) => v as String?),
      isResumable: $checkedConvert('is_resumable', (v) => v as bool?),
      frozenContext: $checkedConvert(
        'frozen_context',
        (v) => v as Map<String, dynamic>?,
      ),
      stepStates: $checkedConvert(
        'step_states',
        (v) => v as Map<String, dynamic>?,
      ),
      results: $checkedConvert('results', (v) => v as Map<String, dynamic>?),
      reportData: $checkedConvert(
        'report_data',
        (v) => v == null
            ? null
            : ReportDataDto.fromJson(v as Map<String, dynamic>),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'traceVersion': 'trace_version',
    'strictnessLevel': 'strictness_level',
    'createdAt': 'created_at',
    'costEstimate': 'cost_estimate',
    'isResumable': 'is_resumable',
    'frozenContext': 'frozen_context',
    'stepStates': 'step_states',
    'reportData': 'report_data',
  },
);

Map<String, dynamic> _$ExecutionRecordToJson(_ExecutionRecord instance) =>
    <String, dynamic>{
      'id': instance.id,
      'workflow_id': instance.workflowId,
      'status': instance.status,
      'trace_version': instance.traceVersion,
      'strictness_level': instance.strictnessLevel,
      'created_at': instance.createdAt,
      'cost_estimate': instance.costEstimate,
      'metadata': instance.metadata,
      'error': instance.error,
      'is_resumable': instance.isResumable,
      'frozen_context': instance.frozenContext,
      'step_states': instance.stepStates,
      'results': instance.results,
      'report_data': instance.reportData?.toJson(),
    };
