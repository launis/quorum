import 'package:freezed_annotation/freezed_annotation.dart';

part 'queue_stats.freezed.dart';
part 'queue_stats.g.dart';

/// **Queue Statistics Model**
///
/// Represents current state of the system's background job queue (ArQ).
/// Used for real-time monitoring in the Admin Dashboard.
@freezed
abstract class QueueStats with _$QueueStats {
  const factory QueueStats({
    /// Number of jobs currently waiting in the queue.
    @JsonKey(name: 'queued_jobs') required int queuedJobs,

    /// Number of jobs currently being processed by workers.
    /// Note: Might be 0 if deep introspection is disabled/mocked.
    @JsonKey(name: 'active_jobs') required int activeJobs,

    /// Number of jobs in the dead-letter queue (failed permanently).
    @JsonKey(name: 'dead_jobs') required int deadJobs,
  }) = _QueueStats;

  factory QueueStats.fromJson(Map<String, dynamic> json) =>
      _$QueueStatsFromJson(json);
}
