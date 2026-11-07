import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/trace_context_carrier.dart';

part 'execution_metadata.freezed.dart';
part 'execution_metadata.g.dart';

/// Phase 5, Step 5.1: Strongly typed global context variables DTO matching backend `GlobalContextVarsDTO`.
@freezed
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
    @JsonKey(name: 'step_coach') Map<String, String>? stepCoach,
    @JsonKey(name: 'knowledge_base') Map<String, String>? knowledgeBase,
    @JsonKey(name: 'hydration_results') String? hydrationResults,
    @JsonKey(name: 'step_linguistics') String? stepLinguistics,
    @JsonKey(name: 'external_evidence') String? externalEvidence,
    @JsonKey(name: 'evaluative_matrices')
    Map<String, double>? evaluativeMatrices,
    @JsonKey(name: 'passivity_detected') bool? passivityDetected,
    @JsonKey(name: 'archivist_precedents') List<String>? archivistPrecedents,
    @JsonKey(name: 'shuffled_atoms') List<String>? shuffledAtoms,
    @JsonKey(name: 'profiler_metrics') String? profilerMetrics,
    String? distillation,
    String? scoring,
    @JsonKey(name: 'interaction_analysis') String? interactionAnalysis,
    String? bibliography,
    @JsonKey(name: 'llm_anomaly_retry_requested')
    bool? llmAnomalyRetryRequested,
    @JsonKey(name: 'input_control_ratio') double? inputControlRatio,
    @JsonKey(name: 'integrity_verified_output') String? integrityVerifiedOutput,
    @JsonKey(name: 'step_metadata') String? stepMetadata,
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
