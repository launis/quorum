import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/trace_context_carrier.dart';

part 'execution_metadata.freezed.dart';
part 'execution_metadata.g.dart';

/// Strictly typed metadata for execution runtime parameters and configuration.
@Freezed(equal: false)
abstract class ExecutionMetadata with _$ExecutionMetadata {
  const ExecutionMetadata._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionMetadata({
    @JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy,
    @JsonKey(name: 'workflow_version') @Default(1) int workflowVersion,
    @JsonKey(name: 'global_context_vars')
    Map<String, Object?>? globalContextVars,
    @JsonKey(name: 'provider_override') LLMProvider? providerOverride,
    @JsonKey(name: 'model_registry_id') String? modelRegistryId,
    @JsonKey(name: 'telemetry') TraceContextCarrier? telemetry,
  }) = _ExecutionMetadata;

  /// Instantiates a strictly typed [ExecutionMetadata] from raw JSON.
  factory ExecutionMetadata.fromJson(Map<String, dynamic> json) =>
      _$ExecutionMetadataFromJson(json);
}
