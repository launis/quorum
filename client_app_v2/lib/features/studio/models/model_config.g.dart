// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ModelConfig _$ModelConfigFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_ModelConfig', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'slug', 'type', 'models']);
      final val = _ModelConfig(
        id: $checkedConvert(
          'id',
          (v) => const StrictOpaqueIdConverter().fromJson(v as String),
        ),
        slug: $checkedConvert('slug', (v) => v as String?),
        type: $checkedConvert('type', (v) => v as String? ?? 'model_registry'),
        models: $checkedConvert(
          'models',
          (v) =>
              (v as Map<String, dynamic>?)?.map(
                (k, e) => MapEntry(
                  k,
                  LlmModelConfig.fromJson(e as Map<String, dynamic>),
                ),
              ) ??
              const {},
        ),
      );
      return val;
    });

Map<String, dynamic> _$ModelConfigToJson(_ModelConfig instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'type': instance.type,
      'models': instance.models.map((k, e) => MapEntry(k, e.toJson())),
    };

_LlmModelConfig _$LlmModelConfigFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_LlmModelConfig',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'provider',
        'model_name',
        'temperature',
        'max_tokens',
        'parsing_mode',
        'top_p',
        'top_k',
        'tpm_limit',
        'rpm_limit',
        'supports_grounding',
        'is_active',
        'allowed_tools',
        'api_key',
        'caching_strategy',
        'additional_params',
      ],
    );
    final val = _LlmModelConfig(
      provider: $checkedConvert('provider', (v) => v as String? ?? 'unknown'),
      modelName: $checkedConvert('model_name', (v) => v as String? ?? ''),
      temperature: $checkedConvert(
        'temperature',
        (v) => (v as num?)?.toDouble() ?? 0.0,
      ),
      maxTokens: $checkedConvert('max_tokens', (v) => (v as num?)?.toInt()),
      parsingMode: $checkedConvert('parsing_mode', (v) => v as String?),
      topP: $checkedConvert('top_p', (v) => (v as num?)?.toDouble()),
      topK: $checkedConvert('top_k', (v) => (v as num?)?.toInt()),
      tpmLimit: $checkedConvert('tpm_limit', (v) => (v as num?)?.toInt()),
      rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num?)?.toInt()),
      supportsGrounding: $checkedConvert(
        'supports_grounding',
        (v) => v as bool? ?? false,
      ),
      isActive: $checkedConvert('is_active', (v) => v as bool? ?? false),
      allowedTools: $checkedConvert(
        'allowed_tools',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      apiKey: $checkedConvert('api_key', (v) => v as String?),
      cachingStrategy: $checkedConvert('caching_strategy', (v) => v as String?),
      additionalParams: $checkedConvert(
        'additional_params',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'modelName': 'model_name',
    'maxTokens': 'max_tokens',
    'parsingMode': 'parsing_mode',
    'topP': 'top_p',
    'topK': 'top_k',
    'tpmLimit': 'tpm_limit',
    'rpmLimit': 'rpm_limit',
    'supportsGrounding': 'supports_grounding',
    'isActive': 'is_active',
    'allowedTools': 'allowed_tools',
    'apiKey': 'api_key',
    'cachingStrategy': 'caching_strategy',
    'additionalParams': 'additional_params',
  },
);

Map<String, dynamic> _$LlmModelConfigToJson(_LlmModelConfig instance) =>
    <String, dynamic>{
      'provider': instance.provider,
      'model_name': instance.modelName,
      'temperature': instance.temperature,
      'max_tokens': instance.maxTokens,
      'parsing_mode': instance.parsingMode,
      'top_p': instance.topP,
      'top_k': instance.topK,
      'tpm_limit': instance.tpmLimit,
      'rpm_limit': instance.rpmLimit,
      'supports_grounding': instance.supportsGrounding,
      'is_active': instance.isActive,
      'allowed_tools': instance.allowedTools,
      'api_key': instance.apiKey,
      'caching_strategy': instance.cachingStrategy,
      'additional_params': instance.additionalParams,
    };
