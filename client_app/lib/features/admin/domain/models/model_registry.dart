// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'model_registry.freezed.dart';
part 'model_registry.g.dart';

@freezed
abstract class LLMProviderConfig with _$LLMProviderConfig {
  const factory LLMProviderConfig({
    required String id,
    required String provider,
    @JsonKey(name: 'model_name') required String modelName,
    @JsonKey(name: 'api_key') String? apiKey,
    @JsonKey(name: 'base_url') String? baseUrl,
    @Default(0.7) double temperature,
    @JsonKey(name: 'tpm_limit') @Default(0) int tpmLimit,
    @JsonKey(name: 'rpm_limit') @Default(0) int rpmLimit,
    @JsonKey(name: 'default_max_tokens') int? defaultMaxTokens,
    @JsonKey(name: 'vertex_location') String? vertexLocation,
    @JsonKey(name: 'supports_grounding') @Default(false) bool supportsGrounding,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'additional_params')
    @Default({})
    Map<String, dynamic> additionalParams,
  }) = _LLMProviderConfig;

  factory LLMProviderConfig.fromJson(Map<String, dynamic> json) =>
      _$LLMProviderConfigFromJson(json);
}

@freezed
abstract class AdHocTestRequest with _$AdHocTestRequest {
  const factory AdHocTestRequest({
    required String provider,
    @JsonKey(name: 'api_key') String? apiKey,
    @JsonKey(name: 'system_instruction') required String systemInstruction,
    @JsonKey(name: 'user_prompt') required String userPrompt,
    @JsonKey(name: 'model_params')
    @Default({})
    Map<String, dynamic> modelParams,
  }) = _AdHocTestRequest;

  factory AdHocTestRequest.fromJson(Map<String, dynamic> json) =>
      _$AdHocTestRequestFromJson(json);
}

@freezed
abstract class AdHocTestResult with _$AdHocTestResult {
  const factory AdHocTestResult({
    required String content,
    @JsonKey(name: 'latency_ms') required double latencyMs,
    required String status,
  }) = _AdHocTestResult;

  factory AdHocTestResult.fromJson(Map<String, dynamic> json) =>
      _$AdHocTestResultFromJson(json);
}
