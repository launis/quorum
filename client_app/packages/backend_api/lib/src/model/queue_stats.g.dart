// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'queue_stats.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$QueueStatsCWProxy {
  QueueStats queuedJobs(int queuedJobs);

  QueueStats activeJobs(int activeJobs);

  QueueStats deadJobs(int deadJobs);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `QueueStats(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// QueueStats(...).copyWith(id: 12, name: "My name")
  /// ````
  QueueStats call({int queuedJobs, int activeJobs, int deadJobs});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfQueueStats.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfQueueStats.copyWith.fieldName(...)`
class _$QueueStatsCWProxyImpl implements _$QueueStatsCWProxy {
  const _$QueueStatsCWProxyImpl(this._value);

  final QueueStats _value;

  @override
  QueueStats queuedJobs(int queuedJobs) => this(queuedJobs: queuedJobs);

  @override
  QueueStats activeJobs(int activeJobs) => this(activeJobs: activeJobs);

  @override
  QueueStats deadJobs(int deadJobs) => this(deadJobs: deadJobs);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `QueueStats(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// QueueStats(...).copyWith(id: 12, name: "My name")
  /// ````
  QueueStats call({
    Object? queuedJobs = const $CopyWithPlaceholder(),
    Object? activeJobs = const $CopyWithPlaceholder(),
    Object? deadJobs = const $CopyWithPlaceholder(),
  }) {
    return QueueStats(
      queuedJobs: queuedJobs == const $CopyWithPlaceholder()
          ? _value.queuedJobs
          // ignore: cast_nullable_to_non_nullable
          : queuedJobs as int,
      activeJobs: activeJobs == const $CopyWithPlaceholder()
          ? _value.activeJobs
          // ignore: cast_nullable_to_non_nullable
          : activeJobs as int,
      deadJobs: deadJobs == const $CopyWithPlaceholder()
          ? _value.deadJobs
          // ignore: cast_nullable_to_non_nullable
          : deadJobs as int,
    );
  }
}

extension $QueueStatsCopyWith on QueueStats {
  /// Returns a callable class that can be used as follows: `instanceOfQueueStats.copyWith(...)` or like so:`instanceOfQueueStats.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$QueueStatsCWProxy get copyWith => _$QueueStatsCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

QueueStats _$QueueStatsFromJson(Map<String, dynamic> json) => $checkedCreate(
  'QueueStats',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['queued_jobs', 'active_jobs', 'dead_jobs'],
    );
    final val = QueueStats(
      queuedJobs: $checkedConvert('queued_jobs', (v) => (v as num).toInt()),
      activeJobs: $checkedConvert('active_jobs', (v) => (v as num).toInt()),
      deadJobs: $checkedConvert('dead_jobs', (v) => (v as num).toInt()),
    );
    return val;
  },
  fieldKeyMap: const {
    'queuedJobs': 'queued_jobs',
    'activeJobs': 'active_jobs',
    'deadJobs': 'dead_jobs',
  },
);

Map<String, dynamic> _$QueueStatsToJson(QueueStats instance) =>
    <String, dynamic>{
      'queued_jobs': instance.queuedJobs,
      'active_jobs': instance.activeJobs,
      'dead_jobs': instance.deadJobs,
    };
