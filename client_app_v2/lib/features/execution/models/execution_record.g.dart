// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_record.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ContextVariablesDto _$ContextVariablesDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ContextVariablesDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'global_atom_blackboard',
            'matrix_reducer_output',
            'report_context',
            'step_detector',
            'evaluated_matrices',
            'variables',
          ],
        );
        final val = _ContextVariablesDto(
          globalAtomBlackboard: $checkedConvert(
            'global_atom_blackboard',
            (v) => v as String?,
          ),
          matrixReducerOutput: $checkedConvert(
            'matrix_reducer_output',
            (v) => v as String?,
          ),
          reportContext: $checkedConvert('report_context', (v) => v as String?),
          stepDetector: $checkedConvert('step_detector', (v) => v as String?),
          evaluatedMatrices: $checkedConvert(
            'evaluated_matrices',
            (v) => v as String?,
          ),
          variables: $checkedConvert(
            'variables',
            (v) =>
                (v as Map<String, dynamic>?)?.map(
                  (k, e) => MapEntry(k, e as String),
                ) ??
                const <String, String>{},
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'globalAtomBlackboard': 'global_atom_blackboard',
        'matrixReducerOutput': 'matrix_reducer_output',
        'reportContext': 'report_context',
        'stepDetector': 'step_detector',
        'evaluatedMatrices': 'evaluated_matrices',
      },
    );

Map<String, dynamic> _$ContextVariablesDtoToJson(
  _ContextVariablesDto instance,
) => <String, dynamic>{
  'global_atom_blackboard': instance.globalAtomBlackboard,
  'matrix_reducer_output': instance.matrixReducerOutput,
  'report_context': instance.reportContext,
  'step_detector': instance.stepDetector,
  'evaluated_matrices': instance.evaluatedMatrices,
  'variables': instance.variables,
};

_ExecutionTraceItemDto _$ExecutionTraceItemDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionTraceItemDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'event',
        'step_id',
        'status',
        'duration_ms',
        'detail',
      ],
    );
    final val = _ExecutionTraceItemDto(
      event: $checkedConvert('event', (v) => v as String?),
      stepId: $checkedConvert('step_id', (v) => v as String?),
      status: $checkedConvert('status', (v) => v as String?),
      durationMs: $checkedConvert('duration_ms', (v) => (v as num?)?.toInt()),
      detail: $checkedConvert('detail', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'stepId': 'step_id', 'durationMs': 'duration_ms'},
);

Map<String, dynamic> _$ExecutionTraceItemDtoToJson(
  _ExecutionTraceItemDto instance,
) => <String, dynamic>{
  'event': instance.event,
  'step_id': instance.stepId,
  'status': instance.status,
  'duration_ms': instance.durationMs,
  'detail': instance.detail,
};

_ProfileSynthesisEntryDto _$ProfileSynthesisEntryDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ProfileSynthesisEntryDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'cached',
        'variance_explanation',
        'authenticity_explanation',
        'cited_sources',
        'user_role',
        'user_role_justification',
        'created_at',
      ],
    );
    final val = _ProfileSynthesisEntryDto(
      cached: $checkedConvert('cached', (v) => v as bool? ?? false),
      varianceExplanation: $checkedConvert(
        'variance_explanation',
        (v) => v as String?,
      ),
      authenticityExplanation: $checkedConvert(
        'authenticity_explanation',
        (v) => v as String?,
      ),
      citedSources: $checkedConvert(
        'cited_sources',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const <String>[],
      ),
      userRole: $checkedConvert('user_role', (v) => v as String?),
      userRoleJustification: $checkedConvert(
        'user_role_justification',
        (v) => v as String?,
      ),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'varianceExplanation': 'variance_explanation',
    'authenticityExplanation': 'authenticity_explanation',
    'citedSources': 'cited_sources',
    'userRole': 'user_role',
    'userRoleJustification': 'user_role_justification',
    'createdAt': 'created_at',
  },
);

Map<String, dynamic> _$ProfileSynthesisEntryDtoToJson(
  _ProfileSynthesisEntryDto instance,
) => <String, dynamic>{
  'cached': instance.cached,
  'variance_explanation': instance.varianceExplanation,
  'authenticity_explanation': instance.authenticityExplanation,
  'cited_sources': instance.citedSources,
  'user_role': instance.userRole,
  'user_role_justification': instance.userRoleJustification,
  'created_at': instance.createdAt,
};

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
        'workflow_version',
        'state_version',
        'active_profile_id',
        'output_profile_id',
        'raw_inputs',
        'duration_ms',
        'cost_estimate',
        'prompt_tokens',
        'completion_tokens',
        'cached_tokens',
        'reasoning_tokens',
        'dag_cost_usd',
        'cumulative_synthesis_tokens',
        'cumulative_synthesis_cost',
        'models_used',
        'execution_summary',
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
        'steps',
        'step_states',
        'profile_syntheses',
        'progress',
        'status_message',
        'created_at',
        'updated_at',
        'completed_at',
        'created_by',
        'organization_id',
      ],
    );
    final val = _ExecutionRecord(
      id: $checkedConvert('id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      targetLocale: $checkedConvert('target_locale', (v) => v as String),
      status: $checkedConvert('status', (v) => _statusFromJson(v as String)),
      workflowVersion: $checkedConvert(
        'workflow_version',
        (v) => (v as num?)?.toInt() ?? 1,
      ),
      stateVersion: $checkedConvert(
        'state_version',
        (v) => (v as num?)?.toInt() ?? 1,
      ),
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
        (v) => v == null
            ? null
            : WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
      durationMs: $checkedConvert('duration_ms', (v) => (v as num?)?.toInt()),
      costEstimate: $checkedConvert(
        'cost_estimate',
        (v) => (v as num?)?.toDouble(),
      ),
      promptTokens: $checkedConvert(
        'prompt_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      completionTokens: $checkedConvert(
        'completion_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      cachedTokens: $checkedConvert(
        'cached_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      reasoningTokens: $checkedConvert(
        'reasoning_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      dagCostUsd: $checkedConvert(
        'dag_cost_usd',
        (v) => (v as num?)?.toDouble() ?? 0.0,
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
      executionSummary: $checkedConvert(
        'execution_summary',
        (v) => v == null
            ? null
            : ExecutionSummarySnapshot.fromJson(v as Map<String, dynamic>),
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
        (v) => v == null
            ? null
            : FrozenContextSnapshot.fromJson(v as Map<String, dynamic>),
      ),
      frozenContextStoragePath: $checkedConvert(
        'frozen_context_storage_path',
        (v) => v as String?,
      ),
      contextVariables: $checkedConvert(
        'context_variables',
        (v) => v == null
            ? null
            : ContextVariablesDto.fromJson(v as Map<String, dynamic>),
      ),
      contextVariablesStoragePath: $checkedConvert(
        'context_variables_storage_path',
        (v) => v as String?,
      ),
      executionTrace: $checkedConvert(
        'execution_trace',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) => ExecutionTraceItemDto.fromJson(e as Map<String, dynamic>),
            )
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
      steps: $checkedConvert(
        'steps',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => ExecutionStep.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      stepStates: $checkedConvert(
        'step_states',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) =>
              MapEntry(k, ExecutionStep.fromJson(e as Map<String, dynamic>)),
        ),
      ),
      profileSyntheses: $checkedConvert(
        'profile_syntheses',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(
            k,
            ProfileSynthesisEntryDto.fromJson(e as Map<String, dynamic>),
          ),
        ),
      ),
      progress: $checkedConvert('progress', (v) => (v as num?)?.toInt()),
      statusMessage: $checkedConvert('status_message', (v) => v as String?),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      updatedAt: $checkedConvert('updated_at', (v) => v as String?),
      completedAt: $checkedConvert('completed_at', (v) => v as String?),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'targetLocale': 'target_locale',
    'workflowVersion': 'workflow_version',
    'stateVersion': 'state_version',
    'activeProfileId': 'active_profile_id',
    'outputProfileId': 'output_profile_id',
    'rawInputs': 'raw_inputs',
    'durationMs': 'duration_ms',
    'costEstimate': 'cost_estimate',
    'promptTokens': 'prompt_tokens',
    'completionTokens': 'completion_tokens',
    'cachedTokens': 'cached_tokens',
    'reasoningTokens': 'reasoning_tokens',
    'dagCostUsd': 'dag_cost_usd',
    'cumulativeSynthesisTokens': 'cumulative_synthesis_tokens',
    'cumulativeSynthesisCost': 'cumulative_synthesis_cost',
    'modelsUsed': 'models_used',
    'executionSummary': 'execution_summary',
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
  },
);

Map<String, dynamic> _$ExecutionRecordToJson(
  _ExecutionRecord instance,
) => <String, dynamic>{
  'id': instance.id,
  'workflow_id': instance.workflowId,
  'target_locale': instance.targetLocale,
  'status': instance.status,
  'workflow_version': instance.workflowVersion,
  'state_version': instance.stateVersion,
  'active_profile_id': instance.activeProfileId,
  'output_profile_id': instance.outputProfileId,
  'raw_inputs': instance.rawInputs?.toJson(),
  'duration_ms': instance.durationMs,
  'cost_estimate': instance.costEstimate,
  'prompt_tokens': instance.promptTokens,
  'completion_tokens': instance.completionTokens,
  'cached_tokens': instance.cachedTokens,
  'reasoning_tokens': instance.reasoningTokens,
  'dag_cost_usd': instance.dagCostUsd,
  'cumulative_synthesis_tokens': instance.cumulativeSynthesisTokens,
  'cumulative_synthesis_cost': instance.cumulativeSynthesisCost,
  'models_used': instance.modelsUsed,
  'execution_summary': instance.executionSummary?.toJson(),
  'metadata': instance.metadata?.toJson(),
  'error': instance.error,
  'is_resumable': instance.isResumable,
  'frozen_context': instance.frozenContext?.toJson(),
  'frozen_context_storage_path': instance.frozenContextStoragePath,
  'context_variables': instance.contextVariables?.toJson(),
  'context_variables_storage_path': instance.contextVariablesStoragePath,
  'execution_trace': instance.executionTrace?.map((e) => e.toJson()).toList(),
  'execution_trace_storage_path': instance.executionTraceStoragePath,
  'pdf_report_path': instance.pdfReportPath,
  'source_identity_manifest': instance.sourceIdentityManifest,
  'steps': instance.steps.map((e) => e.toJson()).toList(),
  'step_states': instance.stepStates?.map((k, e) => MapEntry(k, e.toJson())),
  'profile_syntheses': instance.profileSyntheses?.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'progress': instance.progress,
  'status_message': instance.statusMessage,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'completed_at': instance.completedAt,
  'created_by': instance.createdBy,
  'organization_id': instance.organizationId,
};
