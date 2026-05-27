// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/utils/json_converters.dart';

part 'model_config.freezed.dart';
part 'model_config.g.dart';

/// Freezed domain model for Model Registry configurations.
/// Enforces Fail-Fast typing and strictly matches Pydantic V2 schema.
@freezed
abstract class ModelConfig with _$ModelConfig {
  const factory ModelConfig({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    @Default('model_registry') String type,
    @Default({}) Map<String, LlmModelConfig> models,
  }) = _ModelConfig;

  factory ModelConfig.fromJson(Map<String, dynamic> json) =>
      _$ModelConfigFromJson(json);
}

/// Strongly-typed Sub-Model for individual LLM Configurations.
@freezed
abstract class LlmModelConfig with _$LlmModelConfig {
  const factory LlmModelConfig({
    @Default('unknown') String provider,
    @JsonKey(name: 'model_name') @Default('') String modelName,
    @Default(0.0) double temperature,
    @JsonKey(name: 'max_tokens') int? maxTokens,
    @JsonKey(name: 'parsing_mode') String? parsingMode,
    @JsonKey(name: 'top_p') double? topP,
    @JsonKey(name: 'top_k') int? topK,
    @JsonKey(name: 'tpm_limit') int? tpmLimit,
    @JsonKey(name: 'rpm_limit') int? rpmLimit,
    @JsonKey(name: 'supports_grounding') @Default(false) bool supportsGrounding,
    @JsonKey(name: 'is_active') @Default(false) bool isActive,
    @JsonKey(name: 'allowed_tools') @Default([]) List<String> allowedTools,
    @JsonKey(name: 'api_key') String? apiKey,
    @JsonKey(name: 'caching_strategy') String? cachingStrategy,
    @JsonKey(name: 'additional_params')
    @Default({})
    Map<String, dynamic> additionalParams,
  }) = _LlmModelConfig;

  factory LlmModelConfig.fromJson(Map<String, dynamic> json) =>
      _$LlmModelConfigFromJson(json);
}
