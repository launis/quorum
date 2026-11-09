import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/trace_context_carrier.dart';

part 'execution_metadata.freezed.dart';
part 'execution_metadata.g.dart';

/// Strongly typed global context variables DTO matching backend `GlobalContextVarsDTO`.
@Freezed(equal: false)
abstract class GlobalContextVarsDto with _$GlobalContextVarsDto {
  const GlobalContextVarsDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory GlobalContextVarsDto({
    String? language,
    @JsonKey(name: 'target_locale') String? targetLocale,
    @JsonKey(name: 'system_locale') String? systemLocale,
    @JsonKey(name: 'profile_id') String? profileId,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'initiator_id') String? initiatorId,
    @JsonKey(name: 'step_coach') Object? stepCoach,
    @JsonKey(name: 'knowledge_base') Object? knowledgeBase,
    @JsonKey(name: 'hydration_results') Object? hydrationResults,
    @JsonKey(name: 'step_linguistics') Object? stepLinguistics,
    @JsonKey(name: 'external_evidence') String? externalEvidence,
    @JsonKey(name: 'evaluative_matrices')
    Map<String, double>? evaluativeMatrices,
    @JsonKey(name: 'passivity_detected') bool? passivityDetected,
    @JsonKey(name: 'archivist_precedents') List<Object?>? archivistPrecedents,
    @JsonKey(name: 'shuffled_atoms') List<Object?>? shuffledAtoms,
    @JsonKey(name: 'profiler_metrics') Object? profilerMetrics,
    Object? distillation,
    Object? scoring,
    @JsonKey(name: 'interaction_analysis') Object? interactionAnalysis,
    Object? bibliography,
    @JsonKey(name: 'llm_anomaly_retry_requested')
    bool? llmAnomalyRetryRequested,
    @JsonKey(name: 'input_control_ratio') double? inputControlRatio,
    @JsonKey(name: 'integrity_verified_output') Object? integrityVerifiedOutput,
    @JsonKey(name: 'step_metadata') Object? stepMetadata,
  }) = _GlobalContextVarsDto;

  factory GlobalContextVarsDto.fromJson(Map<String, dynamic> json) =>
      _$GlobalContextVarsDtoFromJson(json);
}

/// Strictly typed metadata for execution runtime parameters and configuration.
@Freezed(equal: false)
abstract class ExecutionMetadata with _$ExecutionMetadata {
  const ExecutionMetadata._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionMetadata({
    @JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy,
    @JsonKey(name: 'workflow_version') @Default(1) int workflowVersion,
    @JsonKey(name: 'global_context_vars')
    GlobalContextVarsDto? globalContextVars,
    @JsonKey(name: 'provider_override') LLMProvider? providerOverride,
    @JsonKey(name: 'model_registry_id') String? modelRegistryId,
    @JsonKey(name: 'telemetry') TraceContextCarrier? telemetry,
  }) = _ExecutionMetadata;

  /// Instantiates a strictly typed [ExecutionMetadata] from raw JSON.
  factory ExecutionMetadata.fromJson(Map<String, dynamic> json) =>
      _$ExecutionMetadataFromJson(json);
}
