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
            'target_locale',
            'profile_id',
            'matrix_sampling_strategy',
            'workflow_version',
            'user_id',
            'organization_id',
            'global_context_vars',
            'execution_summary',
            'step_metrics',
            'dag_cost_usd',
            'prompt_tokens',
            'completion_tokens',
            'cached_tokens',
            'reasoning_tokens',
          ],
        );
        final val = _ExecutionMetadata(
          targetLocale: $checkedConvert('target_locale', (v) => v as String),
          profileId: $checkedConvert('profile_id', (v) => v as String?),
          matrixSamplingStrategy: $checkedConvert(
            'matrix_sampling_strategy',
            (v) => (v as num?)?.toInt() ?? 10,
          ),
          workflowVersion: $checkedConvert(
            'workflow_version',
            (v) => (v as num?)?.toInt() ?? 1,
          ),
          userId: $checkedConvert('user_id', (v) => v as String?),
          organizationId: $checkedConvert(
            'organization_id',
            (v) => v as String?,
          ),
          globalContextVars: $checkedConvert(
            'global_context_vars',
            (v) => v as Map<String, dynamic>?,
          ),
          executionSummary: $checkedConvert(
            'execution_summary',
            (v) => v as Map<String, dynamic>?,
          ),
          stepMetrics: $checkedConvert(
            'step_metrics',
            (v) => v as Map<String, dynamic>?,
          ),
          dagCostUsd: $checkedConvert(
            'dag_cost_usd',
            (v) => (v as num?)?.toDouble(),
          ),
          promptTokens: $checkedConvert(
            'prompt_tokens',
            (v) => (v as num?)?.toInt(),
          ),
          completionTokens: $checkedConvert(
            'completion_tokens',
            (v) => (v as num?)?.toInt(),
          ),
          cachedTokens: $checkedConvert(
            'cached_tokens',
            (v) => (v as num?)?.toInt(),
          ),
          reasoningTokens: $checkedConvert(
            'reasoning_tokens',
            (v) => (v as num?)?.toInt(),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'targetLocale': 'target_locale',
        'profileId': 'profile_id',
        'matrixSamplingStrategy': 'matrix_sampling_strategy',
        'workflowVersion': 'workflow_version',
        'userId': 'user_id',
        'organizationId': 'organization_id',
        'globalContextVars': 'global_context_vars',
        'executionSummary': 'execution_summary',
        'stepMetrics': 'step_metrics',
        'dagCostUsd': 'dag_cost_usd',
        'promptTokens': 'prompt_tokens',
        'completionTokens': 'completion_tokens',
        'cachedTokens': 'cached_tokens',
        'reasoningTokens': 'reasoning_tokens',
      },
    );

Map<String, dynamic> _$ExecutionMetadataToJson(_ExecutionMetadata instance) =>
    <String, dynamic>{
      'target_locale': instance.targetLocale,
      'profile_id': instance.profileId,
      'matrix_sampling_strategy': instance.matrixSamplingStrategy,
      'workflow_version': instance.workflowVersion,
      'user_id': instance.userId,
      'organization_id': instance.organizationId,
      'global_context_vars': instance.globalContextVars,
      'execution_summary': instance.executionSummary,
      'step_metrics': instance.stepMetrics,
      'dag_cost_usd': instance.dagCostUsd,
      'prompt_tokens': instance.promptTokens,
      'completion_tokens': instance.completionTokens,
      'cached_tokens': instance.cachedTokens,
      'reasoning_tokens': instance.reasoningTokens,
    };
