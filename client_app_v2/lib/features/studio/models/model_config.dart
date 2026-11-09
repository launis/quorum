import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/utils/json_converters.dart';

part 'model_config.freezed.dart';
part 'model_config.g.dart';

/// Strongly typed provider extra parameters DTO matching backend `ProviderExtraParamsDTO`.
@freezed
abstract class ProviderExtraParamsDto with _$ProviderExtraParamsDto {
  const ProviderExtraParamsDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ProviderExtraParamsDto({
    double? temperature,
    @JsonKey(name: 'top_p') double? topP,
    @JsonKey(name: 'top_k') int? topK,
    @JsonKey(name: 'max_output_tokens') int? maxOutputTokens,
    @JsonKey(name: 'reasoning_effort') String? reasoningEffort,
    @JsonKey(name: 'vertex_location') String? vertexLocation,
  }) = _ProviderExtraParamsDto;

  factory ProviderExtraParamsDto.fromJson(Map<String, dynamic> json) =>
      _$ProviderExtraParamsDtoFromJson(json);
}

/// Freezed domain model for Model Registry configurations.
/// Enforces Fail-Fast typing and strictly matches Pydantic V2 schema.
@Freezed(equal: false)
abstract class ModelConfig with _$ModelConfig {
  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ModelConfig({
    @StrictOpaqueIdConverter() required String id,
    @Default('Default Model Registry') String name,
    String? slug,
    @Default('model_registry') String type,
    @JsonKey(name: 'default_provider')
    @Default('ai_studio')
    String defaultProvider,
    @JsonKey(name: 'tier_definitions')
    @Default(<String, LlmModelConfig>{})
    Map<String, LlmModelConfig> tierDefinitions,
  }) = _ModelConfig;

  factory ModelConfig.fromJson(Map<String, dynamic> json) =>
      _$ModelConfigFromJson(json);
}

/// Strongly-typed Sub-Model for individual LLM Configurations.
@Freezed(equal: false)
abstract class LlmModelConfig with _$LlmModelConfig {
  const LlmModelConfig._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory LlmModelConfig({
    @Default('unknown') String provider,
    @JsonKey(name: 'model_name') @Default('') String modelName,
    @Default(0.0) double temperature,
    @JsonKey(name: 'max_tokens') int? maxTokens,
    @JsonKey(name: 'parsing_mode') String? parsingMode,
    @JsonKey(name: 'top_p') double? topP,
    @JsonKey(name: 'top_k') int? topK,
    @JsonKey(name: 'frequency_penalty') double? frequencyPenalty,
    @JsonKey(name: 'presence_penalty') double? presencePenalty,
    @JsonKey(name: 'tpm_limit') int? tpmLimit,
    @JsonKey(name: 'rpm_limit') int? rpmLimit,
    @JsonKey(name: 'supports_grounding') @Default(false) bool supportsGrounding,
    @JsonKey(name: 'is_active') @Default(false) bool isActive,
    @JsonKey(name: 'allowed_tools')
    @Default(<String>[])
    List<String> allowedTools,
    @JsonKey(name: 'api_key') String? apiKey,
    @JsonKey(name: 'caching_strategy') String? cachingStrategy,
    @JsonKey(name: 'thinking_budget_tokens') int? thinkingBudgetTokens,
    @JsonKey(name: 'additional_params')
    @Default(ProviderExtraParamsDto())
    ProviderExtraParamsDto additionalParams,
  }) = _LlmModelConfig;

  factory LlmModelConfig.fromJson(Map<String, dynamic> json) =>
      _$LlmModelConfigFromJson(json);

  String? get reasoningEffort => additionalParams.reasoningEffort;

  LlmModelConfig withReasoningEffort(String? val) {
    return copyWith(
      additionalParams: additionalParams.copyWith(reasoningEffort: val),
    );
  }
}
