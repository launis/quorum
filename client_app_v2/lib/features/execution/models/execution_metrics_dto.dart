import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_metrics_dto.freezed.dart';
part 'execution_metrics_dto.g.dart';

/// Aggregate atom-level metrics for DAG execution (SSOT).
@Freezed(equal: false)
abstract class ExecutionMetricsDTO with _$ExecutionMetricsDTO {
  const ExecutionMetricsDTO._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionMetricsDTO({
    @JsonKey(name: 'total_atoms') required int totalAtoms,
    required int evaluated,
    @JsonKey(name: 'short_circuited_na') required int shortCircuitedNa,
    @JsonKey(name: 'duration_ms') @Default(0) int durationMs,
  }) = _ExecutionMetricsDTO;

  /// Instantiates a strictly typed [ExecutionMetricsDTO] from raw JSON.
  factory ExecutionMetricsDTO.fromJson(Map<String, dynamic> json) =>
      _$ExecutionMetricsDTOFromJson(json);
}
