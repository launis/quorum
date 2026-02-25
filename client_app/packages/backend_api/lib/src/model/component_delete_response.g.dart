// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'component_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ComponentDeleteResponseCWProxy {
  ComponentDeleteResponse status(String status);

  ComponentDeleteResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentDeleteResponse call({String status, String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfComponentDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfComponentDeleteResponse.copyWith.fieldName(...)`
class _$ComponentDeleteResponseCWProxyImpl
    implements _$ComponentDeleteResponseCWProxy {
  const _$ComponentDeleteResponseCWProxyImpl(this._value);

  final ComponentDeleteResponse _value;

  @override
  ComponentDeleteResponse status(String status) => this(status: status);

  @override
  ComponentDeleteResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ComponentDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ComponentDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ComponentDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return ComponentDeleteResponse(
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

extension $ComponentDeleteResponseCopyWith on ComponentDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfComponentDeleteResponse.copyWith(...)` or like so:`instanceOfComponentDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ComponentDeleteResponseCWProxy get copyWith =>
      _$ComponentDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ComponentDeleteResponse _$ComponentDeleteResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ComponentDeleteResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status', 'id']);
  final val = ComponentDeleteResponse(
    status: $checkedConvert('status', (v) => v as String),
    id: $checkedConvert('id', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$ComponentDeleteResponseToJson(
  ComponentDeleteResponse instance,
) => <String, dynamic>{'status': instance.status, 'id': instance.id};
