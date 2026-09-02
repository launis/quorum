// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_step.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionStep _$ExecutionStepFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionStep',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'label',
            'status',
            'last_error',
            'message_code',
            'model_strategy',
            'physical_model',
            'system_fingerprint',
            'prompt_tokens',
            'completion_tokens',
            'cached_tokens',
            'reasoning_tokens',
            'cost_usd',
            'duration_ms',
            'chunk_count',
            'scorecard_atoms',
          ],
        );
        final val = _ExecutionStep(
          id: $checkedConvert('id', (v) => v as String),
          label: $checkedConvert('label', (v) => v as String),
          status: $checkedConvert('status', (v) => v as String),
          lastError: $checkedConvert('last_error', (v) => v as String?),
          messageCode: $checkedConvert('message_code', (v) => v as String?),
          modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
          physicalModel: $checkedConvert('physical_model', (v) => v as String?),
          systemFingerprint: $checkedConvert(
            'system_fingerprint',
            (v) => v as String?,
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
          costUsd: $checkedConvert(
            'cost_usd',
            (v) => (v as num?)?.toDouble() ?? 0.0,
          ),
          durationMs: $checkedConvert(
            'duration_ms',
            (v) => (v as num?)?.toInt() ?? 0,
          ),
          chunkCount: $checkedConvert(
            'chunk_count',
            (v) => (v as num?)?.toInt() ?? 1,
          ),
          scorecardAtoms: $checkedConvert(
            'scorecard_atoms',
            (v) => v as Map<String, dynamic>? ?? const {},
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'lastError': 'last_error',
        'messageCode': 'message_code',
        'modelStrategy': 'model_strategy',
        'physicalModel': 'physical_model',
        'systemFingerprint': 'system_fingerprint',
        'promptTokens': 'prompt_tokens',
        'completionTokens': 'completion_tokens',
        'cachedTokens': 'cached_tokens',
        'reasoningTokens': 'reasoning_tokens',
        'costUsd': 'cost_usd',
        'durationMs': 'duration_ms',
        'chunkCount': 'chunk_count',
        'scorecardAtoms': 'scorecard_atoms',
      },
    );

Map<String, dynamic> _$ExecutionStepToJson(_ExecutionStep instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'status': instance.status,
      'last_error': instance.lastError,
      'message_code': instance.messageCode,
      'model_strategy': instance.modelStrategy,
      'physical_model': instance.physicalModel,
      'system_fingerprint': instance.systemFingerprint,
      'prompt_tokens': instance.promptTokens,
      'completion_tokens': instance.completionTokens,
      'cached_tokens': instance.cachedTokens,
      'reasoning_tokens': instance.reasoningTokens,
      'cost_usd': instance.costUsd,
      'duration_ms': instance.durationMs,
      'chunk_count': instance.chunkCount,
      'scorecard_atoms': instance.scorecardAtoms,
    };
