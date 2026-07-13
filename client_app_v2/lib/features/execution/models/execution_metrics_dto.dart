// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_metrics_dto.freezed.dart';
part 'execution_metrics_dto.g.dart';

@freezed
abstract class ExecutionMetricsDTO with _$ExecutionMetricsDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionMetricsDTO({
    @JsonKey(name: 'total_atoms') required int totalAtoms,
    required int evaluated,
    @JsonKey(name: 'short_circuited_na') required int shortCircuitedNa,
    @JsonKey(name: 'duration_ms') @Default(0) int durationMs,
  }) = _ExecutionMetricsDTO;

  factory ExecutionMetricsDTO.fromJson(Map<String, dynamic> json) =>
      _$ExecutionMetricsDTOFromJson(json);
}
