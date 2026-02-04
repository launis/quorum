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
