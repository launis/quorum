// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'async_job_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AsyncJobResponseCWProxy {
  AsyncJobResponse jobId(String jobId);

  AsyncJobResponse status(String status);

  AsyncJobResponse message(String? message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AsyncJobResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AsyncJobResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AsyncJobResponse call({String jobId, String status, String? message});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAsyncJobResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAsyncJobResponse.copyWith.fieldName(...)`
class _$AsyncJobResponseCWProxyImpl implements _$AsyncJobResponseCWProxy {
  const _$AsyncJobResponseCWProxyImpl(this._value);

  final AsyncJobResponse _value;

  @override
  AsyncJobResponse jobId(String jobId) => this(jobId: jobId);

  @override
  AsyncJobResponse status(String status) => this(status: status);

  @override
  AsyncJobResponse message(String? message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AsyncJobResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AsyncJobResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AsyncJobResponse call({
    Object? jobId = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return AsyncJobResponse(
      jobId: jobId == const $CopyWithPlaceholder()
          ? _value.jobId
          // ignore: cast_nullable_to_non_nullable
          : jobId as String,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String?,
    );
  }
}

extension $AsyncJobResponseCopyWith on AsyncJobResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAsyncJobResponse.copyWith(...)` or like so:`instanceOfAsyncJobResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AsyncJobResponseCWProxy get copyWith => _$AsyncJobResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AsyncJobResponse _$AsyncJobResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AsyncJobResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['job_id', 'status']);
      final val = AsyncJobResponse(
        jobId: $checkedConvert('job_id', (v) => v as String),
        status: $checkedConvert('status', (v) => v as String),
        message: $checkedConvert('message', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {'jobId': 'job_id'});

Map<String, dynamic> _$AsyncJobResponseToJson(AsyncJobResponse instance) =>
    <String, dynamic>{
      'job_id': instance.jobId,
      'status': instance.status,
      'message': ?instance.message,
    };
