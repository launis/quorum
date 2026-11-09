// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_metadata.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GlobalContextVarsDto _$GlobalContextVarsDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_GlobalContextVarsDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'language',
        'target_locale',
        'system_locale',
        'profile_id',
        'organization_id',
        'initiator_id',
        'step_coach',
        'knowledge_base',
        'hydration_results',
        'step_linguistics',
        'external_evidence',
        'evaluative_matrices',
        'passivity_detected',
        'archivist_precedents',
        'shuffled_atoms',
        'profiler_metrics',
        'distillation',
        'scoring',
        'interaction_analysis',
        'bibliography',
        'llm_anomaly_retry_requested',
        'input_control_ratio',
        'integrity_verified_output',
        'step_metadata',
      ],
    );
    final val = _GlobalContextVarsDto(
      language: $checkedConvert('language', (v) => v as String?),
      targetLocale: $checkedConvert('target_locale', (v) => v as String?),
      systemLocale: $checkedConvert('system_locale', (v) => v as String?),
      profileId: $checkedConvert('profile_id', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      initiatorId: $checkedConvert('initiator_id', (v) => v as String?),
      stepCoach: $checkedConvert('step_coach', (v) => v),
      knowledgeBase: $checkedConvert('knowledge_base', (v) => v),
      hydrationResults: $checkedConvert('hydration_results', (v) => v),
      stepLinguistics: $checkedConvert('step_linguistics', (v) => v),
      externalEvidence: $checkedConvert(
        'external_evidence',
        (v) => v as String?,
      ),
      evaluativeMatrices: $checkedConvert(
        'evaluative_matrices',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, (e as num).toDouble()),
        ),
      ),
      passivityDetected: $checkedConvert(
        'passivity_detected',
        (v) => v as bool?,
      ),
      archivistPrecedents: $checkedConvert(
        'archivist_precedents',
        (v) => v as List<dynamic>?,
      ),
      shuffledAtoms: $checkedConvert(
        'shuffled_atoms',
        (v) => v as List<dynamic>?,
      ),
      profilerMetrics: $checkedConvert('profiler_metrics', (v) => v),
      distillation: $checkedConvert('distillation', (v) => v),
      scoring: $checkedConvert('scoring', (v) => v),
      interactionAnalysis: $checkedConvert('interaction_analysis', (v) => v),
      bibliography: $checkedConvert('bibliography', (v) => v),
      llmAnomalyRetryRequested: $checkedConvert(
        'llm_anomaly_retry_requested',
        (v) => v as bool?,
      ),
      inputControlRatio: $checkedConvert(
        'input_control_ratio',
        (v) => (v as num?)?.toDouble(),
      ),
      integrityVerifiedOutput: $checkedConvert(
        'integrity_verified_output',
        (v) => v,
      ),
      stepMetadata: $checkedConvert('step_metadata', (v) => v),
    );
    return val;
  },
  fieldKeyMap: const {
    'targetLocale': 'target_locale',
    'systemLocale': 'system_locale',
    'profileId': 'profile_id',
    'organizationId': 'organization_id',
    'initiatorId': 'initiator_id',
    'stepCoach': 'step_coach',
    'knowledgeBase': 'knowledge_base',
    'hydrationResults': 'hydration_results',
    'stepLinguistics': 'step_linguistics',
    'externalEvidence': 'external_evidence',
    'evaluativeMatrices': 'evaluative_matrices',
    'passivityDetected': 'passivity_detected',
    'archivistPrecedents': 'archivist_precedents',
    'shuffledAtoms': 'shuffled_atoms',
    'profilerMetrics': 'profiler_metrics',
    'interactionAnalysis': 'interaction_analysis',
    'llmAnomalyRetryRequested': 'llm_anomaly_retry_requested',
    'inputControlRatio': 'input_control_ratio',
    'integrityVerifiedOutput': 'integrity_verified_output',
    'stepMetadata': 'step_metadata',
  },
);

Map<String, dynamic> _$GlobalContextVarsDtoToJson(
  _GlobalContextVarsDto instance,
) => <String, dynamic>{
  'language': instance.language,
  'target_locale': instance.targetLocale,
  'system_locale': instance.systemLocale,
  'profile_id': instance.profileId,
  'organization_id': instance.organizationId,
  'initiator_id': instance.initiatorId,
  'step_coach': instance.stepCoach,
  'knowledge_base': instance.knowledgeBase,
  'hydration_results': instance.hydrationResults,
  'step_linguistics': instance.stepLinguistics,
  'external_evidence': instance.externalEvidence,
  'evaluative_matrices': instance.evaluativeMatrices,
  'passivity_detected': instance.passivityDetected,
  'archivist_precedents': instance.archivistPrecedents,
  'shuffled_atoms': instance.shuffledAtoms,
  'profiler_metrics': instance.profilerMetrics,
  'distillation': instance.distillation,
  'scoring': instance.scoring,
  'interaction_analysis': instance.interactionAnalysis,
  'bibliography': instance.bibliography,
  'llm_anomaly_retry_requested': instance.llmAnomalyRetryRequested,
  'input_control_ratio': instance.inputControlRatio,
  'integrity_verified_output': instance.integrityVerifiedOutput,
  'step_metadata': instance.stepMetadata,
};

_ExecutionMetadata _$ExecutionMetadataFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionMetadata',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'matrix_sampling_strategy',
            'workflow_version',
            'global_context_vars',
            'provider_override',
            'model_registry_id',
            'telemetry',
          ],
        );
        final val = _ExecutionMetadata(
          matrixSamplingStrategy: $checkedConvert(
            'matrix_sampling_strategy',
            (v) => (v as num?)?.toInt(),
          ),
          workflowVersion: $checkedConvert(
            'workflow_version',
            (v) => (v as num?)?.toInt() ?? 1,
          ),
          globalContextVars: $checkedConvert(
            'global_context_vars',
            (v) => v == null
                ? null
                : GlobalContextVarsDto.fromJson(v as Map<String, dynamic>),
          ),
          providerOverride: $checkedConvert(
            'provider_override',
            (v) => $enumDecodeNullable(_$LLMProviderEnumMap, v),
          ),
          modelRegistryId: $checkedConvert(
            'model_registry_id',
            (v) => v as String?,
          ),
          telemetry: $checkedConvert(
            'telemetry',
            (v) => v == null
                ? null
                : TraceContextCarrier.fromJson(v as Map<String, dynamic>),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'matrixSamplingStrategy': 'matrix_sampling_strategy',
        'workflowVersion': 'workflow_version',
        'globalContextVars': 'global_context_vars',
        'providerOverride': 'provider_override',
        'modelRegistryId': 'model_registry_id',
      },
    );

Map<String, dynamic> _$ExecutionMetadataToJson(_ExecutionMetadata instance) =>
    <String, dynamic>{
      'matrix_sampling_strategy': instance.matrixSamplingStrategy,
      'workflow_version': instance.workflowVersion,
      'global_context_vars': instance.globalContextVars?.toJson(),
      'provider_override': _$LLMProviderEnumMap[instance.providerOverride],
      'model_registry_id': instance.modelRegistryId,
      'telemetry': instance.telemetry?.toJson(),
    };

const _$LLMProviderEnumMap = {
  LLMProvider.vertexAi: 'vertex_ai',
  LLMProvider.aiStudio: 'ai_studio',
  LLMProvider.openai: 'openai',
  LLMProvider.anthropic: 'anthropic',
  LLMProvider.azureOpenai: 'azure_openai',
  LLMProvider.local: 'local',
};
