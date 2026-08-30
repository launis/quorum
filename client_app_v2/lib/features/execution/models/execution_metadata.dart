// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_metadata.freezed.dart';
part 'execution_metadata.g.dart';

/// Strictly typed metadata for execution runtime parameters and telemetry.
@Freezed(equal: false)
abstract class ExecutionMetadata with _$ExecutionMetadata {
  const ExecutionMetadata._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionMetadata({
    @JsonKey(name: 'target_locale') required String targetLocale,
    @JsonKey(name: 'profile_id') String? profileId,
    @JsonKey(name: 'matrix_sampling_strategy')
    @Default(10)
    int matrixSamplingStrategy,
    @JsonKey(name: 'workflow_version') @Default(1) int workflowVersion,
    @JsonKey(name: 'user_id') String? userId,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'global_context_vars')
    Map<String, dynamic>? globalContextVars,
    @JsonKey(name: 'execution_summary') Map<String, dynamic>? executionSummary,
    @JsonKey(name: 'step_metrics') Map<String, dynamic>? stepMetrics,
    @JsonKey(name: 'dag_cost_usd') double? dagCostUsd,
    @JsonKey(name: 'prompt_tokens') int? promptTokens,
    @JsonKey(name: 'completion_tokens') int? completionTokens,
    @JsonKey(name: 'cached_tokens') int? cachedTokens,
    @JsonKey(name: 'reasoning_tokens') int? reasoningTokens,
  }) = _ExecutionMetadata;

  /// Instantiates a strictly typed [ExecutionMetadata] from raw JSON.
  factory ExecutionMetadata.fromJson(Map<String, dynamic> json) =>
      _$ExecutionMetadataFromJson(json);
}
