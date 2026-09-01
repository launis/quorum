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
        'target_locale',
        'status',
        'active_profile_id',
        'output_profile_id',
        'raw_inputs',
        'trace_version',
        'strictness_level',
        'duration_ms',
        'cost_estimate',
        'cumulative_synthesis_tokens',
        'cumulative_synthesis_cost',
        'models_used',
        'metadata',
        'error',
        'is_resumable',
        'frozen_context',
        'frozen_context_storage_path',
        'context_variables',
        'context_variables_storage_path',
        'execution_trace',
        'execution_trace_storage_path',
        'pdf_report_path',
        'source_identity_manifest',
        'step_states',
        'profile_syntheses',
        'results',
        'progress',
        'status_message',
        'created_at',
        'updated_at',
        'completed_at',
        'created_by',
        'organization_id',
        'report_data',
      ],
    );
    final val = _ExecutionRecord(
      id: $checkedConvert('id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      targetLocale: $checkedConvert('target_locale', (v) => v as String),
      status: $checkedConvert('status', (v) => _statusFromJson(v as String)),
      activeProfileId: $checkedConvert(
        'active_profile_id',
        (v) => v as String?,
      ),
      outputProfileId: $checkedConvert(
        'output_profile_id',
        (v) => v as String?,
      ),
      rawInputs: $checkedConvert(
        'raw_inputs',
        (v) => v as Map<String, dynamic>?,
      ),
      traceVersion: $checkedConvert(
        'trace_version',
        (v) => _traceVersionFromJson(v),
      ),
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt(),
      ),
      durationMs: $checkedConvert('duration_ms', (v) => (v as num?)?.toInt()),
      costEstimate: $checkedConvert(
        'cost_estimate',
        (v) => (v as num?)?.toDouble(),
      ),
      cumulativeSynthesisTokens: $checkedConvert(
        'cumulative_synthesis_tokens',
        (v) => (v as num?)?.toInt(),
      ),
      cumulativeSynthesisCost: $checkedConvert(
        'cumulative_synthesis_cost',
        (v) => (v as num?)?.toDouble(),
      ),
      modelsUsed: $checkedConvert(
        'models_used',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, (e as num).toInt()),
        ),
      ),
      metadata: $checkedConvert(
        'metadata',
        (v) => v == null
            ? null
            : ExecutionMetadata.fromJson(v as Map<String, dynamic>),
      ),
      error: $checkedConvert('error', (v) => v as String?),
      isResumable: $checkedConvert('is_resumable', (v) => v as bool?),
      frozenContext: $checkedConvert(
        'frozen_context',
        (v) => v as Map<String, dynamic>?,
      ),
      frozenContextStoragePath: $checkedConvert(
        'frozen_context_storage_path',
        (v) => v as String?,
      ),
      contextVariables: $checkedConvert(
        'context_variables',
        (v) => v as Map<String, dynamic>?,
      ),
      contextVariablesStoragePath: $checkedConvert(
        'context_variables_storage_path',
        (v) => v as String?,
      ),
      executionTrace: $checkedConvert(
        'execution_trace',
        (v) => (v as List<dynamic>?)
            ?.map((e) => e as Map<String, dynamic>)
            .toList(),
      ),
      executionTraceStoragePath: $checkedConvert(
        'execution_trace_storage_path',
        (v) => v as String?,
      ),
      pdfReportPath: $checkedConvert('pdf_report_path', (v) => v as String?),
      sourceIdentityManifest: $checkedConvert(
        'source_identity_manifest',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      stepStates: $checkedConvert(
        'step_states',
        (v) => v as Map<String, dynamic>?,
      ),
      profileSyntheses: $checkedConvert(
        'profile_syntheses',
        (v) => v as Map<String, dynamic>?,
      ),
      results: $checkedConvert('results', (v) => v as Map<String, dynamic>?),
      progress: $checkedConvert('progress', (v) => (v as num?)?.toInt()),
      statusMessage: $checkedConvert('status_message', (v) => v as String?),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      updatedAt: $checkedConvert('updated_at', (v) => v as String?),
      completedAt: $checkedConvert('completed_at', (v) => v as String?),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
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
    'targetLocale': 'target_locale',
    'activeProfileId': 'active_profile_id',
    'outputProfileId': 'output_profile_id',
    'rawInputs': 'raw_inputs',
    'traceVersion': 'trace_version',
    'strictnessLevel': 'strictness_level',
    'durationMs': 'duration_ms',
    'costEstimate': 'cost_estimate',
    'cumulativeSynthesisTokens': 'cumulative_synthesis_tokens',
    'cumulativeSynthesisCost': 'cumulative_synthesis_cost',
    'modelsUsed': 'models_used',
    'isResumable': 'is_resumable',
    'frozenContext': 'frozen_context',
    'frozenContextStoragePath': 'frozen_context_storage_path',
    'contextVariables': 'context_variables',
    'contextVariablesStoragePath': 'context_variables_storage_path',
    'executionTrace': 'execution_trace',
    'executionTraceStoragePath': 'execution_trace_storage_path',
    'pdfReportPath': 'pdf_report_path',
    'sourceIdentityManifest': 'source_identity_manifest',
    'stepStates': 'step_states',
    'profileSyntheses': 'profile_syntheses',
    'statusMessage': 'status_message',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at',
    'completedAt': 'completed_at',
    'createdBy': 'created_by',
    'organizationId': 'organization_id',
    'reportData': 'report_data',
  },
);

Map<String, dynamic> _$ExecutionRecordToJson(_ExecutionRecord instance) =>
    <String, dynamic>{
      'id': instance.id,
      'workflow_id': instance.workflowId,
      'target_locale': instance.targetLocale,
      'status': instance.status,
      'active_profile_id': instance.activeProfileId,
      'output_profile_id': instance.outputProfileId,
      'raw_inputs': instance.rawInputs,
      'trace_version': instance.traceVersion,
      'strictness_level': instance.strictnessLevel,
      'duration_ms': instance.durationMs,
      'cost_estimate': instance.costEstimate,
      'cumulative_synthesis_tokens': instance.cumulativeSynthesisTokens,
      'cumulative_synthesis_cost': instance.cumulativeSynthesisCost,
      'models_used': instance.modelsUsed,
      'metadata': instance.metadata?.toJson(),
      'error': instance.error,
      'is_resumable': instance.isResumable,
      'frozen_context': instance.frozenContext,
      'frozen_context_storage_path': instance.frozenContextStoragePath,
      'context_variables': instance.contextVariables,
      'context_variables_storage_path': instance.contextVariablesStoragePath,
      'execution_trace': instance.executionTrace,
      'execution_trace_storage_path': instance.executionTraceStoragePath,
      'pdf_report_path': instance.pdfReportPath,
      'source_identity_manifest': instance.sourceIdentityManifest,
      'step_states': instance.stepStates,
      'profile_syntheses': instance.profileSyntheses,
      'results': instance.results,
      'progress': instance.progress,
      'status_message': instance.statusMessage,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
      'completed_at': instance.completedAt,
      'created_by': instance.createdBy,
      'organization_id': instance.organizationId,
      'report_data': instance.reportData?.toJson(),
    };
