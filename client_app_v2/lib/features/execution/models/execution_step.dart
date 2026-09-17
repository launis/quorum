// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_step.freezed.dart';
part 'execution_step.g.dart';

/// Strongly typed real-time status and FinOps tracking for DAG nodes (SSOT).
@Freezed(equal: false)
abstract class ExecutionStep with _$ExecutionStep {
  const ExecutionStep._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionStep({
    required String id,
    required String label,
    required String status,
    @JsonKey(name: 'last_error') String? lastError,
    @JsonKey(name: 'message_code') String? messageCode,
    @JsonKey(name: 'model_strategy') String? modelStrategy,
    @JsonKey(name: 'physical_model') String? physicalModel,
    @JsonKey(name: 'system_fingerprint') String? systemFingerprint,
    @JsonKey(name: 'prompt_tokens') @Default(0) int promptTokens,
    @JsonKey(name: 'completion_tokens') @Default(0) int completionTokens,
    @JsonKey(name: 'cached_tokens') @Default(0) int cachedTokens,
    @JsonKey(name: 'reasoning_tokens') @Default(0) int reasoningTokens,
    @JsonKey(name: 'cost_usd') @Default(0.0) double costUsd,
    @JsonKey(name: 'duration_ms') @Default(0) int durationMs,
    @JsonKey(name: 'chunk_count') @Default(1) int chunkCount,
    @JsonKey(name: 'scorecard_atoms')
    @Default({})
    Map<String, dynamic> scorecardAtoms,
  }) = _ExecutionStep;

  /// Instantiates a strictly typed [ExecutionStep] from raw JSON.
  factory ExecutionStep.fromJson(Map<String, dynamic> json) =>
      _$ExecutionStepFromJson(json);
}
