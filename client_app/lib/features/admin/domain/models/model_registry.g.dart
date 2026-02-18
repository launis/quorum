// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_registry.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LLMProviderConfig _$LLMProviderConfigFromJson(Map<String, dynamic> json) =>
    _LLMProviderConfig(
      id: json['id'] as String,
      provider: json['provider'] as String,
      modelName: json['model_name'] as String,
      apiKey: json['api_key'] as String?,
      baseUrl: json['base_url'] as String?,
      temperature: (json['temperature'] as num?)?.toDouble() ?? 0.7,
      tpmLimit: (json['tpm_limit'] as num?)?.toInt() ?? 0,
      rpmLimit: (json['rpm_limit'] as num?)?.toInt() ?? 0,
      defaultMaxTokens: (json['default_max_tokens'] as num?)?.toInt(),
      vertexLocation: json['vertex_location'] as String?,
      supportsGrounding: json['supports_grounding'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
      additionalParams:
          json['additional_params'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$LLMProviderConfigToJson(_LLMProviderConfig instance) =>
    <String, dynamic>{
      'id': instance.id,
      'provider': instance.provider,
      'model_name': instance.modelName,
      'api_key': instance.apiKey,
      'base_url': instance.baseUrl,
      'temperature': instance.temperature,
      'tpm_limit': instance.tpmLimit,
      'rpm_limit': instance.rpmLimit,
      'default_max_tokens': instance.defaultMaxTokens,
      'vertex_location': instance.vertexLocation,
      'supports_grounding': instance.supportsGrounding,
      'is_active': instance.isActive,
      'additional_params': instance.additionalParams,
    };

_AdHocTestRequest _$AdHocTestRequestFromJson(Map<String, dynamic> json) =>
    _AdHocTestRequest(
      provider: json['provider'] as String,
      apiKey: json['api_key'] as String?,
      systemInstruction: json['system_instruction'] as String,
      userPrompt: json['user_prompt'] as String,
      modelParams: json['model_params'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$AdHocTestRequestToJson(_AdHocTestRequest instance) =>
    <String, dynamic>{
      'provider': instance.provider,
      'api_key': instance.apiKey,
      'system_instruction': instance.systemInstruction,
      'user_prompt': instance.userPrompt,
      'model_params': instance.modelParams,
    };

_AdHocTestResult _$AdHocTestResultFromJson(Map<String, dynamic> json) =>
    _AdHocTestResult(
      content: json['content'] as String,
      latencyMs: (json['latency_ms'] as num).toDouble(),
      status: json['status'] as String,
    );

Map<String, dynamic> _$AdHocTestResultToJson(_AdHocTestResult instance) =>
    <String, dynamic>{
      'content': instance.content,
      'latency_ms': instance.latencyMs,
      'status': instance.status,
    };
