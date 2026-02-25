// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'problem_detail.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ProblemDetailCWProxy {
  ProblemDetail type(String type);

  ProblemDetail title(String title);

  ProblemDetail status(int status);

  ProblemDetail detail(String detail);

  ProblemDetail instance(String? instance);

  ProblemDetail extensions(Map<String, Object>? extensions);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProblemDetail(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProblemDetail(...).copyWith(id: 12, name: "My name")
  /// ````
  ProblemDetail call({
    String type,
    String title,
    int status,
    String detail,
    String? instance,
    Map<String, Object>? extensions,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfProblemDetail.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfProblemDetail.copyWith.fieldName(...)`
class _$ProblemDetailCWProxyImpl implements _$ProblemDetailCWProxy {
  const _$ProblemDetailCWProxyImpl(this._value);

  final ProblemDetail _value;

  @override
  ProblemDetail type(String type) => this(type: type);

  @override
  ProblemDetail title(String title) => this(title: title);

  @override
  ProblemDetail status(int status) => this(status: status);

  @override
  ProblemDetail detail(String detail) => this(detail: detail);

  @override
  ProblemDetail instance(String? instance) => this(instance: instance);

  @override
  ProblemDetail extensions(Map<String, Object>? extensions) =>
      this(extensions: extensions);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProblemDetail(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProblemDetail(...).copyWith(id: 12, name: "My name")
  /// ````
  ProblemDetail call({
    Object? type = const $CopyWithPlaceholder(),
    Object? title = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? detail = const $CopyWithPlaceholder(),
    Object? instance = const $CopyWithPlaceholder(),
    Object? extensions = const $CopyWithPlaceholder(),
  }) {
    return ProblemDetail(
      type: type == const $CopyWithPlaceholder()
          ? _value.type
          // ignore: cast_nullable_to_non_nullable
          : type as String,
      title: title == const $CopyWithPlaceholder()
          ? _value.title
          // ignore: cast_nullable_to_non_nullable
          : title as String,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as int,
      detail: detail == const $CopyWithPlaceholder()
          ? _value.detail
          // ignore: cast_nullable_to_non_nullable
          : detail as String,
      instance: instance == const $CopyWithPlaceholder()
          ? _value.instance
          // ignore: cast_nullable_to_non_nullable
          : instance as String?,
      extensions: extensions == const $CopyWithPlaceholder()
          ? _value.extensions
          // ignore: cast_nullable_to_non_nullable
          : extensions as Map<String, Object>?,
    );
  }
}

extension $ProblemDetailCopyWith on ProblemDetail {
  /// Returns a callable class that can be used as follows: `instanceOfProblemDetail.copyWith(...)` or like so:`instanceOfProblemDetail.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ProblemDetailCWProxy get copyWith => _$ProblemDetailCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ProblemDetail _$ProblemDetailFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ProblemDetail', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['type', 'title', 'status', 'detail']);
  final val = ProblemDetail(
    type: $checkedConvert('type', (v) => v as String),
    title: $checkedConvert('title', (v) => v as String),
    status: $checkedConvert('status', (v) => (v as num).toInt()),
    detail: $checkedConvert('detail', (v) => v as String),
    instance: $checkedConvert('instance', (v) => v as String?),
    extensions: $checkedConvert(
      'extensions',
      (v) =>
          (v as Map<String, dynamic>?)?.map((k, e) => MapEntry(k, e as Object)),
    ),
  );
  return val;
});

Map<String, dynamic> _$ProblemDetailToJson(ProblemDetail instance) =>
    <String, dynamic>{
      'type': instance.type,
      'title': instance.title,
      'status': instance.status,
      'detail': instance.detail,
      'instance': ?instance.instance,
      'extensions': ?instance.extensions,
    };
