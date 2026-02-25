//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'queue_stats.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class QueueStats {
  /// Returns a new [QueueStats] instance.
  QueueStats({

    required  this.queuedJobs,

    required  this.activeJobs,

    required  this.deadJobs,
  });

      /// Number of jobs currently waiting in the queue.
  @JsonKey(
    
    name: r'queued_jobs',
    required: true,
    
  )


  final int queuedJobs;



      /// Number of jobs currently being processed.
  @JsonKey(
    
    name: r'active_jobs',
    required: true,
    
  )


  final int activeJobs;



      /// Number of jobs in the dead letter queue (failed).
  @JsonKey(
    
    name: r'dead_jobs',
    required: true,
    
  )


  final int deadJobs;





    @override
    bool operator ==(Object other) => identical(this, other) || other is QueueStats &&
      other.queuedJobs == queuedJobs &&
      other.activeJobs == activeJobs &&
      other.deadJobs == deadJobs;

    @override
    int get hashCode =>
        queuedJobs.hashCode +
        activeJobs.hashCode +
        deadJobs.hashCode;

  factory QueueStats.fromJson(Map<String, dynamic> json) => _$QueueStatsFromJson(json);

  Map<String, dynamic> toJson() => _$QueueStatsToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

