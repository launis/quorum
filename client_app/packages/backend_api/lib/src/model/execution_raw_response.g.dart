// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_raw_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ExecutionRawResponseCWProxy {
  ExecutionRawResponse id(String id);

  ExecutionRawResponse workflowId(String? workflowId);

  ExecutionRawResponse status(String? status);

  ExecutionRawResponse startedAt(DateTime? startedAt);

  ExecutionRawResponse completedAt(DateTime? completedAt);

  ExecutionRawResponse durationSeconds(num? durationSeconds);

  ExecutionRawResponse inputs(Map<String, Object>? inputs);

  ExecutionRawResponse results(Map<String, Object>? results);

  ExecutionRawResponse state(Map<String, Object>? state);

  ExecutionRawResponse userId(String? userId);

  ExecutionRawResponse agentOutputs(Map<String, Object>? agentOutputs);

  ExecutionRawResponse hookOutputs(Map<String, Object>? hookOutputs);

  ExecutionRawResponse xaiReport(String? xaiReport);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionRawResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionRawResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionRawResponse call({
    String id,
    String? workflowId,
    String? status,
    DateTime? startedAt,
    DateTime? completedAt,
    num? durationSeconds,
    Map<String, Object>? inputs,
    Map<String, Object>? results,
    Map<String, Object>? state,
    String? userId,
    Map<String, Object>? agentOutputs,
    Map<String, Object>? hookOutputs,
    String? xaiReport,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfExecutionRawResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfExecutionRawResponse.copyWith.fieldName(...)`
class _$ExecutionRawResponseCWProxyImpl
    implements _$ExecutionRawResponseCWProxy {
  const _$ExecutionRawResponseCWProxyImpl(this._value);

  final ExecutionRawResponse _value;

  @override
  ExecutionRawResponse id(String id) => this(id: id);

  @override
  ExecutionRawResponse workflowId(String? workflowId) =>
      this(workflowId: workflowId);

  @override
  ExecutionRawResponse status(String? status) => this(status: status);

  @override
  ExecutionRawResponse startedAt(DateTime? startedAt) =>
      this(startedAt: startedAt);

  @override
  ExecutionRawResponse completedAt(DateTime? completedAt) =>
      this(completedAt: completedAt);

  @override
  ExecutionRawResponse durationSeconds(num? durationSeconds) =>
      this(durationSeconds: durationSeconds);

  @override
  ExecutionRawResponse inputs(Map<String, Object>? inputs) =>
      this(inputs: inputs);

  @override
  ExecutionRawResponse results(Map<String, Object>? results) =>
      this(results: results);

  @override
  ExecutionRawResponse state(Map<String, Object>? state) => this(state: state);

  @override
  ExecutionRawResponse userId(String? userId) => this(userId: userId);

  @override
  ExecutionRawResponse agentOutputs(Map<String, Object>? agentOutputs) =>
      this(agentOutputs: agentOutputs);

  @override
  ExecutionRawResponse hookOutputs(Map<String, Object>? hookOutputs) =>
      this(hookOutputs: hookOutputs);

  @override
  ExecutionRawResponse xaiReport(String? xaiReport) =>
      this(xaiReport: xaiReport);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionRawResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionRawResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionRawResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? workflowId = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? startedAt = const $CopyWithPlaceholder(),
    Object? completedAt = const $CopyWithPlaceholder(),
    Object? durationSeconds = const $CopyWithPlaceholder(),
    Object? inputs = const $CopyWithPlaceholder(),
    Object? results = const $CopyWithPlaceholder(),
    Object? state = const $CopyWithPlaceholder(),
    Object? userId = const $CopyWithPlaceholder(),
    Object? agentOutputs = const $CopyWithPlaceholder(),
    Object? hookOutputs = const $CopyWithPlaceholder(),
    Object? xaiReport = const $CopyWithPlaceholder(),
  }) {
    return ExecutionRawResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      workflowId: workflowId == const $CopyWithPlaceholder()
          ? _value.workflowId
          // ignore: cast_nullable_to_non_nullable
          : workflowId as String?,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
      startedAt: startedAt == const $CopyWithPlaceholder()
          ? _value.startedAt
          // ignore: cast_nullable_to_non_nullable
          : startedAt as DateTime?,
      completedAt: completedAt == const $CopyWithPlaceholder()
          ? _value.completedAt
          // ignore: cast_nullable_to_non_nullable
          : completedAt as DateTime?,
      durationSeconds: durationSeconds == const $CopyWithPlaceholder()
          ? _value.durationSeconds
          // ignore: cast_nullable_to_non_nullable
          : durationSeconds as num?,
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as Map<String, Object>?,
      results: results == const $CopyWithPlaceholder()
          ? _value.results
          // ignore: cast_nullable_to_non_nullable
          : results as Map<String, Object>?,
      state: state == const $CopyWithPlaceholder()
          ? _value.state
          // ignore: cast_nullable_to_non_nullable
          : state as Map<String, Object>?,
      userId: userId == const $CopyWithPlaceholder()
          ? _value.userId
          // ignore: cast_nullable_to_non_nullable
          : userId as String?,
      agentOutputs: agentOutputs == const $CopyWithPlaceholder()
          ? _value.agentOutputs
          // ignore: cast_nullable_to_non_nullable
          : agentOutputs as Map<String, Object>?,
      hookOutputs: hookOutputs == const $CopyWithPlaceholder()
          ? _value.hookOutputs
          // ignore: cast_nullable_to_non_nullable
          : hookOutputs as Map<String, Object>?,
      xaiReport: xaiReport == const $CopyWithPlaceholder()
          ? _value.xaiReport
          // ignore: cast_nullable_to_non_nullable
          : xaiReport as String?,
    );
  }
}

extension $ExecutionRawResponseCopyWith on ExecutionRawResponse {
  /// Returns a callable class that can be used as follows: `instanceOfExecutionRawResponse.copyWith(...)` or like so:`instanceOfExecutionRawResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ExecutionRawResponseCWProxy get copyWith =>
      _$ExecutionRawResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ExecutionRawResponse _$ExecutionRawResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ExecutionRawResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const [
        'id',
        'workflow_id',
        'status',
        'started_at',
        'completed_at',
        'user_id',
      ],
    );
    final val = ExecutionRawResponse(
      id: $checkedConvert('id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String?),
      status: $checkedConvert('status', (v) => v as String?),
      startedAt: $checkedConvert(
        'started_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      completedAt: $checkedConvert(
        'completed_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      durationSeconds: $checkedConvert('duration_seconds', (v) => v as num?),
      inputs: $checkedConvert(
        'inputs',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ) ??
            {},
      ),
      results: $checkedConvert(
        'results',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ) ??
            {},
      ),
      state: $checkedConvert(
        'state',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ) ??
            {},
      ),
      userId: $checkedConvert('user_id', (v) => v as String?),
      agentOutputs: $checkedConvert(
        'agent_outputs',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ) ??
            {},
      ),
      hookOutputs: $checkedConvert(
        'hook_outputs',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ) ??
            {},
      ),
      xaiReport: $checkedConvert('xai_report', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'startedAt': 'started_at',
    'completedAt': 'completed_at',
    'durationSeconds': 'duration_seconds',
    'userId': 'user_id',
    'agentOutputs': 'agent_outputs',
    'hookOutputs': 'hook_outputs',
    'xaiReport': 'xai_report',
  },
);

Map<String, dynamic> _$ExecutionRawResponseToJson(
  ExecutionRawResponse instance,
) => <String, dynamic>{
  'id': instance.id,
  'workflow_id': instance.workflowId,
  'status': instance.status,
  'started_at': instance.startedAt?.toIso8601String(),
  'completed_at': instance.completedAt?.toIso8601String(),
  'duration_seconds': ?instance.durationSeconds,
  'inputs': ?instance.inputs,
  'results': ?instance.results,
  'state': ?instance.state,
  'user_id': instance.userId,
  'agent_outputs': ?instance.agentOutputs,
  'hook_outputs': ?instance.hookOutputs,
  'xai_report': ?instance.xaiReport,
};
