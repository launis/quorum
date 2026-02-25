// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StepDeleteResponseCWProxy {
  StepDeleteResponse status(String status);

  StepDeleteResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  StepDeleteResponse call({String status, String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfStepDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfStepDeleteResponse.copyWith.fieldName(...)`
class _$StepDeleteResponseCWProxyImpl implements _$StepDeleteResponseCWProxy {
  const _$StepDeleteResponseCWProxyImpl(this._value);

  final StepDeleteResponse _value;

  @override
  StepDeleteResponse status(String status) => this(status: status);

  @override
  StepDeleteResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  StepDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return StepDeleteResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
    );
  }
}

extension $StepDeleteResponseCopyWith on StepDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfStepDeleteResponse.copyWith(...)` or like so:`instanceOfStepDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StepDeleteResponseCWProxy get copyWith =>
      _$StepDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StepDeleteResponse _$StepDeleteResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('StepDeleteResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status', 'id']);
      final val = StepDeleteResponse(
        status: $checkedConvert('status', (v) => v as String),
        id: $checkedConvert('id', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$StepDeleteResponseToJson(StepDeleteResponse instance) =>
    <String, dynamic>{'status': instance.status, 'id': instance.id};
