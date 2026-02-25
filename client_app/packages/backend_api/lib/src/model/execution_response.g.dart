// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ExecutionResponseCWProxy {
  ExecutionResponse id(String id);

  ExecutionResponse workflowId(String workflowId);

  ExecutionResponse status(String status);

  ExecutionResponse startedAt(DateTime startedAt);

  ExecutionResponse completedAt(DateTime? completedAt);

  ExecutionResponse results(Map<String, Object>? results);

  ExecutionResponse inputs(Map<String, Object>? inputs);

  ExecutionResponse userId(String userId);

  ExecutionResponse organizationId(String? organizationId);

  ExecutionResponse workflowName(String? workflowName);

  ExecutionResponse startTime(DateTime? startTime);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionResponse call({
    String id,
    String workflowId,
    String status,
    DateTime startedAt,
    DateTime? completedAt,
    Map<String, Object>? results,
    Map<String, Object>? inputs,
    String userId,
    String? organizationId,
    String? workflowName,
    DateTime? startTime,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfExecutionResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfExecutionResponse.copyWith.fieldName(...)`
class _$ExecutionResponseCWProxyImpl implements _$ExecutionResponseCWProxy {
  const _$ExecutionResponseCWProxyImpl(this._value);

  final ExecutionResponse _value;

  @override
  ExecutionResponse id(String id) => this(id: id);

  @override
  ExecutionResponse workflowId(String workflowId) =>
      this(workflowId: workflowId);

  @override
  ExecutionResponse status(String status) => this(status: status);

  @override
  ExecutionResponse startedAt(DateTime startedAt) => this(startedAt: startedAt);

  @override
  ExecutionResponse completedAt(DateTime? completedAt) =>
      this(completedAt: completedAt);

  @override
  ExecutionResponse results(Map<String, Object>? results) =>
      this(results: results);

  @override
  ExecutionResponse inputs(Map<String, Object>? inputs) => this(inputs: inputs);

  @override
  ExecutionResponse userId(String userId) => this(userId: userId);

  @override
  ExecutionResponse organizationId(String? organizationId) =>
      this(organizationId: organizationId);

  @override
  ExecutionResponse workflowName(String? workflowName) =>
      this(workflowName: workflowName);

  @override
  ExecutionResponse startTime(DateTime? startTime) =>
      this(startTime: startTime);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ExecutionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ExecutionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ExecutionResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? workflowId = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? startedAt = const $CopyWithPlaceholder(),
    Object? completedAt = const $CopyWithPlaceholder(),
    Object? results = const $CopyWithPlaceholder(),
    Object? inputs = const $CopyWithPlaceholder(),
    Object? userId = const $CopyWithPlaceholder(),
    Object? organizationId = const $CopyWithPlaceholder(),
    Object? workflowName = const $CopyWithPlaceholder(),
    Object? startTime = const $CopyWithPlaceholder(),
  }) {
    return ExecutionResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      workflowId: workflowId == const $CopyWithPlaceholder()
          ? _value.workflowId
          // ignore: cast_nullable_to_non_nullable
          : workflowId as String,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      startedAt: startedAt == const $CopyWithPlaceholder()
          ? _value.startedAt
          // ignore: cast_nullable_to_non_nullable
          : startedAt as DateTime,
      completedAt: completedAt == const $CopyWithPlaceholder()
          ? _value.completedAt
          // ignore: cast_nullable_to_non_nullable
          : completedAt as DateTime?,
      results: results == const $CopyWithPlaceholder()
          ? _value.results
          // ignore: cast_nullable_to_non_nullable
          : results as Map<String, Object>?,
      inputs: inputs == const $CopyWithPlaceholder()
          ? _value.inputs
          // ignore: cast_nullable_to_non_nullable
          : inputs as Map<String, Object>?,
      userId: userId == const $CopyWithPlaceholder()
          ? _value.userId
          // ignore: cast_nullable_to_non_nullable
          : userId as String,
      organizationId: organizationId == const $CopyWithPlaceholder()
          ? _value.organizationId
          // ignore: cast_nullable_to_non_nullable
          : organizationId as String?,
      workflowName: workflowName == const $CopyWithPlaceholder()
          ? _value.workflowName
          // ignore: cast_nullable_to_non_nullable
          : workflowName as String?,
      startTime: startTime == const $CopyWithPlaceholder()
          ? _value.startTime
          // ignore: cast_nullable_to_non_nullable
          : startTime as DateTime?,
    );
  }
}

extension $ExecutionResponseCopyWith on ExecutionResponse {
  /// Returns a callable class that can be used as follows: `instanceOfExecutionResponse.copyWith(...)` or like so:`instanceOfExecutionResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ExecutionResponseCWProxy get copyWith =>
      _$ExecutionResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ExecutionResponse _$ExecutionResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'ExecutionResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'id',
            'workflow_id',
            'status',
            'started_at',
            'user_id',
          ],
        );
        final val = ExecutionResponse(
          id: $checkedConvert('id', (v) => v as String),
          workflowId: $checkedConvert('workflow_id', (v) => v as String),
          status: $checkedConvert('status', (v) => v as String),
          startedAt: $checkedConvert(
            'started_at',
            (v) => DateTime.parse(v as String),
          ),
          completedAt: $checkedConvert(
            'completed_at',
            (v) => v == null ? null : DateTime.parse(v as String),
          ),
          results: $checkedConvert(
            'results',
            (v) =>
                (v as Map<String, dynamic>?)?.map(
                  (k, e) => MapEntry(k, e as Object),
                ) ??
                {},
          ),
          inputs: $checkedConvert(
            'inputs',
            (v) =>
                (v as Map<String, dynamic>?)?.map(
                  (k, e) => MapEntry(k, e as Object),
                ) ??
                {},
          ),
          userId: $checkedConvert('user_id', (v) => v as String),
          organizationId: $checkedConvert(
            'organization_id',
            (v) => v as String?,
          ),
          workflowName: $checkedConvert('workflow_name', (v) => v as String?),
          startTime: $checkedConvert(
            'start_time',
            (v) => v == null ? null : DateTime.parse(v as String),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'workflowId': 'workflow_id',
        'startedAt': 'started_at',
        'completedAt': 'completed_at',
        'userId': 'user_id',
        'organizationId': 'organization_id',
        'workflowName': 'workflow_name',
        'startTime': 'start_time',
      },
    );

Map<String, dynamic> _$ExecutionResponseToJson(ExecutionResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'workflow_id': instance.workflowId,
      'status': instance.status,
      'started_at': instance.startedAt.toIso8601String(),
      'completed_at': ?instance.completedAt?.toIso8601String(),
      'results': ?instance.results,
      'inputs': ?instance.inputs,
      'user_id': instance.userId,
      'organization_id': ?instance.organizationId,
      'workflow_name': ?instance.workflowName,
      'start_time': ?instance.startTime?.toIso8601String(),
    };
