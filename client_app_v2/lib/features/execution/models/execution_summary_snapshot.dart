import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_summary_snapshot.freezed.dart';
part 'execution_summary_snapshot.g.dart';

/// Typed DTO snapshot for non-FinOps execution telemetry (SSOT).
@Freezed(equal: false)
abstract class ExecutionSummarySnapshot with _$ExecutionSummarySnapshot {
  const ExecutionSummarySnapshot._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionSummarySnapshot({
    @JsonKey(name: 'strictness_level') @Default(100) int strictnessLevel,
    @JsonKey(name: 'is_ensemble_run') @Default(false) bool isEnsembleRun,
    @JsonKey(name: 'is_degraded') @Default(false) bool isDegraded,
    @JsonKey(name: 'system_concurrency_snapshot')
    @Default({})
    Map<String, int> systemConcurrencySnapshot,
  }) = _ExecutionSummarySnapshot;

  /// Instantiates a strictly typed [ExecutionSummarySnapshot] from raw JSON.
  factory ExecutionSummarySnapshot.fromJson(Map<String, dynamic> json) =>
      _$ExecutionSummarySnapshotFromJson(json);
}
