// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_metadata.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

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
            (v) => v as Map<String, dynamic>?,
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
      'global_context_vars': instance.globalContextVars,
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
