// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'update_role_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UpdateRoleRequestCWProxy {
  UpdateRoleRequest role(UserRole role);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UpdateRoleRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UpdateRoleRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  UpdateRoleRequest call({UserRole role});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUpdateRoleRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUpdateRoleRequest.copyWith.fieldName(...)`
class _$UpdateRoleRequestCWProxyImpl implements _$UpdateRoleRequestCWProxy {
  const _$UpdateRoleRequestCWProxyImpl(this._value);

  final UpdateRoleRequest _value;

  @override
  UpdateRoleRequest role(UserRole role) => this(role: role);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UpdateRoleRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UpdateRoleRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  UpdateRoleRequest call({Object? role = const $CopyWithPlaceholder()}) {
    return UpdateRoleRequest(
      role: role == const $CopyWithPlaceholder()
          ? _value.role
          // ignore: cast_nullable_to_non_nullable
          : role as UserRole,
    );
  }
}

extension $UpdateRoleRequestCopyWith on UpdateRoleRequest {
  /// Returns a callable class that can be used as follows: `instanceOfUpdateRoleRequest.copyWith(...)` or like so:`instanceOfUpdateRoleRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UpdateRoleRequestCWProxy get copyWith =>
      _$UpdateRoleRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UpdateRoleRequest _$UpdateRoleRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('UpdateRoleRequest', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['role']);
      final val = UpdateRoleRequest(
        role: $checkedConvert('role', (v) => $enumDecode(_$UserRoleEnumMap, v)),
      );
      return val;
    });

Map<String, dynamic> _$UpdateRoleRequestToJson(UpdateRoleRequest instance) =>
    <String, dynamic>{'role': _$UserRoleEnumMap[instance.role]!};

const _$UserRoleEnumMap = {
  UserRole.ROOT: 'ROOT',
  UserRole.ADMIN: 'ADMIN',
  UserRole.MANAGER: 'MANAGER',
  UserRole.MEMBER: 'MEMBER',
  UserRole.VIEWER: 'VIEWER',
};
