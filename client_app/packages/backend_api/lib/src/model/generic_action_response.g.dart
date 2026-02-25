// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generic_action_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$GenericActionResponseCWProxy {
  GenericActionResponse status(String status);

  GenericActionResponse id(String? id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GenericActionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GenericActionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  GenericActionResponse call({String status, String? id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfGenericActionResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfGenericActionResponse.copyWith.fieldName(...)`
class _$GenericActionResponseCWProxyImpl
    implements _$GenericActionResponseCWProxy {
  const _$GenericActionResponseCWProxyImpl(this._value);

  final GenericActionResponse _value;

  @override
  GenericActionResponse status(String status) => this(status: status);

  @override
  GenericActionResponse id(String? id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `GenericActionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// GenericActionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  GenericActionResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return GenericActionResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
    );
  }
}

extension $GenericActionResponseCopyWith on GenericActionResponse {
  /// Returns a callable class that can be used as follows: `instanceOfGenericActionResponse.copyWith(...)` or like so:`instanceOfGenericActionResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$GenericActionResponseCWProxy get copyWith =>
      _$GenericActionResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GenericActionResponse _$GenericActionResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('GenericActionResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['status']);
  final val = GenericActionResponse(
    status: $checkedConvert('status', (v) => v as String),
    id: $checkedConvert('id', (v) => v as String?),
  );
  return val;
});

Map<String, dynamic> _$GenericActionResponseToJson(
  GenericActionResponse instance,
) => <String, dynamic>{'status': instance.status, 'id': ?instance.id};
