// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'compilation_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CompilationResponseCWProxy {
  CompilationResponse status(String status);

  CompilationResponse compositeStepId(String compositeStepId);

  CompilationResponse newSteps(List<String> newSteps);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CompilationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CompilationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  CompilationResponse call({
    String status,
    String compositeStepId,
    List<String> newSteps,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCompilationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCompilationResponse.copyWith.fieldName(...)`
class _$CompilationResponseCWProxyImpl implements _$CompilationResponseCWProxy {
  const _$CompilationResponseCWProxyImpl(this._value);

  final CompilationResponse _value;

  @override
  CompilationResponse status(String status) => this(status: status);

  @override
  CompilationResponse compositeStepId(String compositeStepId) =>
      this(compositeStepId: compositeStepId);

  @override
  CompilationResponse newSteps(List<String> newSteps) =>
      this(newSteps: newSteps);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CompilationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CompilationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  CompilationResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? compositeStepId = const $CopyWithPlaceholder(),
    Object? newSteps = const $CopyWithPlaceholder(),
  }) {
    return CompilationResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      compositeStepId: compositeStepId == const $CopyWithPlaceholder()
          ? _value.compositeStepId
          // ignore: cast_nullable_to_non_nullable
          : compositeStepId as String,
      newSteps: newSteps == const $CopyWithPlaceholder()
          ? _value.newSteps
          // ignore: cast_nullable_to_non_nullable
          : newSteps as List<String>,
    );
  }
}

extension $CompilationResponseCopyWith on CompilationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfCompilationResponse.copyWith(...)` or like so:`instanceOfCompilationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CompilationResponseCWProxy get copyWith =>
      _$CompilationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CompilationResponse _$CompilationResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'CompilationResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const ['status', 'composite_step_id', 'new_steps'],
        );
        final val = CompilationResponse(
          status: $checkedConvert('status', (v) => v as String),
          compositeStepId: $checkedConvert(
            'composite_step_id',
            (v) => v as String,
          ),
          newSteps: $checkedConvert(
            'new_steps',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'compositeStepId': 'composite_step_id',
        'newSteps': 'new_steps',
      },
    );

Map<String, dynamic> _$CompilationResponseToJson(
  CompilationResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'composite_step_id': instance.compositeStepId,
  'new_steps': instance.newSteps,
};
