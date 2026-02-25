// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'knowledge_job_status_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$KnowledgeJobStatusResponseCWProxy {
  KnowledgeJobStatusResponse jobId(String jobId);

  KnowledgeJobStatusResponse status(String status);

  KnowledgeJobStatusResponse progress(int progress);

  KnowledgeJobStatusResponse stage(String stage);

  KnowledgeJobStatusResponse result(dynamic result);

  KnowledgeJobStatusResponse error(String? error);

  KnowledgeJobStatusResponse errorCode(String? errorCode);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeJobStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeJobStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeJobStatusResponse call({
    String jobId,
    String status,
    int progress,
    String stage,
    dynamic result,
    String? error,
    String? errorCode,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfKnowledgeJobStatusResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfKnowledgeJobStatusResponse.copyWith.fieldName(...)`
class _$KnowledgeJobStatusResponseCWProxyImpl
    implements _$KnowledgeJobStatusResponseCWProxy {
  const _$KnowledgeJobStatusResponseCWProxyImpl(this._value);

  final KnowledgeJobStatusResponse _value;

  @override
  KnowledgeJobStatusResponse jobId(String jobId) => this(jobId: jobId);

  @override
  KnowledgeJobStatusResponse status(String status) => this(status: status);

  @override
  KnowledgeJobStatusResponse progress(int progress) => this(progress: progress);

  @override
  KnowledgeJobStatusResponse stage(String stage) => this(stage: stage);

  @override
  KnowledgeJobStatusResponse result(dynamic result) => this(result: result);

  @override
  KnowledgeJobStatusResponse error(String? error) => this(error: error);

  @override
  KnowledgeJobStatusResponse errorCode(String? errorCode) =>
      this(errorCode: errorCode);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeJobStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeJobStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeJobStatusResponse call({
    Object? jobId = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? progress = const $CopyWithPlaceholder(),
    Object? stage = const $CopyWithPlaceholder(),
    Object? result = const $CopyWithPlaceholder(),
    Object? error = const $CopyWithPlaceholder(),
    Object? errorCode = const $CopyWithPlaceholder(),
  }) {
    return KnowledgeJobStatusResponse(
      jobId: jobId == const $CopyWithPlaceholder()
          ? _value.jobId
          // ignore: cast_nullable_to_non_nullable
          : jobId as String,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      progress: progress == const $CopyWithPlaceholder()
          ? _value.progress
          // ignore: cast_nullable_to_non_nullable
          : progress as int,
      stage: stage == const $CopyWithPlaceholder()
          ? _value.stage
          // ignore: cast_nullable_to_non_nullable
          : stage as String,
      result: result == const $CopyWithPlaceholder()
          ? _value.result
          // ignore: cast_nullable_to_non_nullable
          : result as dynamic,
      error: error == const $CopyWithPlaceholder()
          ? _value.error
          // ignore: cast_nullable_to_non_nullable
          : error as String?,
      errorCode: errorCode == const $CopyWithPlaceholder()
          ? _value.errorCode
          // ignore: cast_nullable_to_non_nullable
          : errorCode as String?,
    );
  }
}

extension $KnowledgeJobStatusResponseCopyWith on KnowledgeJobStatusResponse {
  /// Returns a callable class that can be used as follows: `instanceOfKnowledgeJobStatusResponse.copyWith(...)` or like so:`instanceOfKnowledgeJobStatusResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$KnowledgeJobStatusResponseCWProxy get copyWith =>
      _$KnowledgeJobStatusResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

KnowledgeJobStatusResponse _$KnowledgeJobStatusResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'KnowledgeJobStatusResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['job_id', 'status', 'progress', 'stage'],
    );
    final val = KnowledgeJobStatusResponse(
      jobId: $checkedConvert('job_id', (v) => v as String),
      status: $checkedConvert('status', (v) => v as String),
      progress: $checkedConvert('progress', (v) => (v as num).toInt()),
      stage: $checkedConvert('stage', (v) => v as String),
      result: $checkedConvert('result', (v) => v),
      error: $checkedConvert('error', (v) => v as String?),
      errorCode: $checkedConvert('error_code', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'jobId': 'job_id', 'errorCode': 'error_code'},
);

Map<String, dynamic> _$KnowledgeJobStatusResponseToJson(
  KnowledgeJobStatusResponse instance,
) => <String, dynamic>{
  'job_id': instance.jobId,
  'status': instance.status,
  'progress': instance.progress,
  'stage': instance.stage,
  'result': ?instance.result,
  'error': ?instance.error,
  'error_code': ?instance.errorCode,
};
