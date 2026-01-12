// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'queue_stats.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_QueueStats _$QueueStatsFromJson(Map<String, dynamic> json) => _QueueStats(
  queuedJobs: (json['queued_jobs'] as num).toInt(),
  activeJobs: (json['active_jobs'] as num).toInt(),
  deadJobs: (json['dead_jobs'] as num).toInt(),
);

Map<String, dynamic> _$QueueStatsToJson(_QueueStats instance) =>
    <String, dynamic>{
      'queued_jobs': instance.queuedJobs,
      'active_jobs': instance.activeJobs,
      'dead_jobs': instance.deadJobs,
    };
