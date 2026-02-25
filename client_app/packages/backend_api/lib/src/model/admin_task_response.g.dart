// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'admin_task_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AdminTaskResponseCWProxy {
  AdminTaskResponse status(AdminTaskResponseStatusEnum status);

  AdminTaskResponse jobId(String jobId);

  AdminTaskResponse task(String task);

  AdminTaskResponse message(String? message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AdminTaskResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AdminTaskResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AdminTaskResponse call({
    AdminTaskResponseStatusEnum status,
    String jobId,
    String task,
    String? message,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAdminTaskResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAdminTaskResponse.copyWith.fieldName(...)`
class _$AdminTaskResponseCWProxyImpl implements _$AdminTaskResponseCWProxy {
  const _$AdminTaskResponseCWProxyImpl(this._value);

  final AdminTaskResponse _value;

  @override
  AdminTaskResponse status(AdminTaskResponseStatusEnum status) =>
      this(status: status);

  @override
  AdminTaskResponse jobId(String jobId) => this(jobId: jobId);

  @override
  AdminTaskResponse task(String task) => this(task: task);

  @override
  AdminTaskResponse message(String? message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AdminTaskResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AdminTaskResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AdminTaskResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? jobId = const $CopyWithPlaceholder(),
    Object? task = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return AdminTaskResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as AdminTaskResponseStatusEnum,
      jobId: jobId == const $CopyWithPlaceholder()
          ? _value.jobId
          // ignore: cast_nullable_to_non_nullable
          : jobId as String,
      task: task == const $CopyWithPlaceholder()
          ? _value.task
          // ignore: cast_nullable_to_non_nullable
          : task as String,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String?,
    );
  }
}

extension $AdminTaskResponseCopyWith on AdminTaskResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAdminTaskResponse.copyWith(...)` or like so:`instanceOfAdminTaskResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AdminTaskResponseCWProxy get copyWith =>
      _$AdminTaskResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AdminTaskResponse _$AdminTaskResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AdminTaskResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status', 'job_id', 'task']);
      final val = AdminTaskResponse(
        status: $checkedConvert(
          'status',
          (v) => $enumDecode(_$AdminTaskResponseStatusEnumEnumMap, v),
        ),
        jobId: $checkedConvert('job_id', (v) => v as String),
        task: $checkedConvert('task', (v) => v as String),
        message: $checkedConvert('message', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {'jobId': 'job_id'});

Map<String, dynamic> _$AdminTaskResponseToJson(AdminTaskResponse instance) =>
    <String, dynamic>{
      'status': _$AdminTaskResponseStatusEnumEnumMap[instance.status]!,
      'job_id': instance.jobId,
      'task': instance.task,
      'message': ?instance.message,
    };

const _$AdminTaskResponseStatusEnumEnumMap = {
  AdminTaskResponseStatusEnum.started: 'started',
  AdminTaskResponseStatusEnum.starting: 'starting',
  AdminTaskResponseStatusEnum.failed: 'failed',
};
