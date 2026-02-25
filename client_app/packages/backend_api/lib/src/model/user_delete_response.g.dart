// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_delete_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UserDeleteResponseCWProxy {
  UserDeleteResponse status(String status);

  UserDeleteResponse id(String id);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  UserDeleteResponse call({String status, String id});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUserDeleteResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUserDeleteResponse.copyWith.fieldName(...)`
class _$UserDeleteResponseCWProxyImpl implements _$UserDeleteResponseCWProxy {
  const _$UserDeleteResponseCWProxyImpl(this._value);

  final UserDeleteResponse _value;

  @override
  UserDeleteResponse status(String status) => this(status: status);

  @override
  UserDeleteResponse id(String id) => this(id: id);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserDeleteResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserDeleteResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  UserDeleteResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
  }) {
    return UserDeleteResponse(
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

extension $UserDeleteResponseCopyWith on UserDeleteResponse {
  /// Returns a callable class that can be used as follows: `instanceOfUserDeleteResponse.copyWith(...)` or like so:`instanceOfUserDeleteResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UserDeleteResponseCWProxy get copyWith =>
      _$UserDeleteResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserDeleteResponse _$UserDeleteResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('UserDeleteResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status', 'id']);
      final val = UserDeleteResponse(
        status: $checkedConvert('status', (v) => v as String),
        id: $checkedConvert('id', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$UserDeleteResponseToJson(UserDeleteResponse instance) =>
    <String, dynamic>{'status': instance.status, 'id': instance.id};
