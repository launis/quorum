// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'task_status_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TaskStatusResponseCWProxy {
  TaskStatusResponse status(String status);

  TaskStatusResponse stage(String? stage);

  TaskStatusResponse percent(Percent? percent);

  TaskStatusResponse error(ProblemDetail? error);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TaskStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TaskStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TaskStatusResponse call({
    String status,
    String? stage,
    Percent? percent,
    ProblemDetail? error,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTaskStatusResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTaskStatusResponse.copyWith.fieldName(...)`
class _$TaskStatusResponseCWProxyImpl implements _$TaskStatusResponseCWProxy {
  const _$TaskStatusResponseCWProxyImpl(this._value);

  final TaskStatusResponse _value;

  @override
  TaskStatusResponse status(String status) => this(status: status);

  @override
  TaskStatusResponse stage(String? stage) => this(stage: stage);

  @override
  TaskStatusResponse percent(Percent? percent) => this(percent: percent);

  @override
  TaskStatusResponse error(ProblemDetail? error) => this(error: error);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TaskStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TaskStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TaskStatusResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? stage = const $CopyWithPlaceholder(),
    Object? percent = const $CopyWithPlaceholder(),
    Object? error = const $CopyWithPlaceholder(),
  }) {
    return TaskStatusResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      stage: stage == const $CopyWithPlaceholder()
          ? _value.stage
          // ignore: cast_nullable_to_non_nullable
          : stage as String?,
      percent: percent == const $CopyWithPlaceholder()
          ? _value.percent
          // ignore: cast_nullable_to_non_nullable
          : percent as Percent?,
      error: error == const $CopyWithPlaceholder()
          ? _value.error
          // ignore: cast_nullable_to_non_nullable
          : error as ProblemDetail?,
    );
  }
}

extension $TaskStatusResponseCopyWith on TaskStatusResponse {
  /// Returns a callable class that can be used as follows: `instanceOfTaskStatusResponse.copyWith(...)` or like so:`instanceOfTaskStatusResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TaskStatusResponseCWProxy get copyWith =>
      _$TaskStatusResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TaskStatusResponse _$TaskStatusResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('TaskStatusResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status']);
      final val = TaskStatusResponse(
        status: $checkedConvert('status', (v) => v as String),
        stage: $checkedConvert('stage', (v) => v as String?),
        percent: $checkedConvert(
          'percent',
          (v) => v == null ? null : Percent.fromJson(v as Map<String, dynamic>),
        ),
        error: $checkedConvert(
          'error',
          (v) => v == null
              ? null
              : ProblemDetail.fromJson(v as Map<String, dynamic>),
        ),
      );
      return val;
    });

Map<String, dynamic> _$TaskStatusResponseToJson(TaskStatusResponse instance) =>
    <String, dynamic>{
      'status': instance.status,
      'stage': ?instance.stage,
      'percent': ?instance.percent?.toJson(),
      'error': ?instance.error?.toJson(),
    };
