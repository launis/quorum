// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_user_create.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationUserCreateCWProxy {
  OrganizationUserCreate email(String email);

  OrganizationUserCreate displayName(String displayName);

  OrganizationUserCreate role(UserRole role);

  OrganizationUserCreate password(String? password);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationUserCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationUserCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationUserCreate call({
    String email,
    String displayName,
    UserRole role,
    String? password,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganizationUserCreate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganizationUserCreate.copyWith.fieldName(...)`
class _$OrganizationUserCreateCWProxyImpl
    implements _$OrganizationUserCreateCWProxy {
  const _$OrganizationUserCreateCWProxyImpl(this._value);

  final OrganizationUserCreate _value;

  @override
  OrganizationUserCreate email(String email) => this(email: email);

  @override
  OrganizationUserCreate displayName(String displayName) =>
      this(displayName: displayName);

  @override
  OrganizationUserCreate role(UserRole role) => this(role: role);

  @override
  OrganizationUserCreate password(String? password) => this(password: password);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationUserCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationUserCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationUserCreate call({
    Object? email = const $CopyWithPlaceholder(),
    Object? displayName = const $CopyWithPlaceholder(),
    Object? role = const $CopyWithPlaceholder(),
    Object? password = const $CopyWithPlaceholder(),
  }) {
    return OrganizationUserCreate(
      email: email == const $CopyWithPlaceholder()
          ? _value.email
          // ignore: cast_nullable_to_non_nullable
          : email as String,
      displayName: displayName == const $CopyWithPlaceholder()
          ? _value.displayName
          // ignore: cast_nullable_to_non_nullable
          : displayName as String,
      role: role == const $CopyWithPlaceholder()
          ? _value.role
          // ignore: cast_nullable_to_non_nullable
          : role as UserRole,
      password: password == const $CopyWithPlaceholder()
          ? _value.password
          // ignore: cast_nullable_to_non_nullable
          : password as String?,
    );
  }
}

extension $OrganizationUserCreateCopyWith on OrganizationUserCreate {
  /// Returns a callable class that can be used as follows: `instanceOfOrganizationUserCreate.copyWith(...)` or like so:`instanceOfOrganizationUserCreate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationUserCreateCWProxy get copyWith =>
      _$OrganizationUserCreateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

OrganizationUserCreate _$OrganizationUserCreateFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('OrganizationUserCreate', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['email', 'display_name', 'role']);
  final val = OrganizationUserCreate(
    email: $checkedConvert('email', (v) => v as String),
    displayName: $checkedConvert('display_name', (v) => v as String),
    role: $checkedConvert('role', (v) => $enumDecode(_$UserRoleEnumMap, v)),
    password: $checkedConvert('password', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {'displayName': 'display_name'});

Map<String, dynamic> _$OrganizationUserCreateToJson(
  OrganizationUserCreate instance,
) => <String, dynamic>{
  'email': instance.email,
  'display_name': instance.displayName,
  'role': _$UserRoleEnumMap[instance.role]!,
  'password': ?instance.password,
};

const _$UserRoleEnumMap = {
  UserRole.ROOT: 'ROOT',
  UserRole.ADMIN: 'ADMIN',
  UserRole.MANAGER: 'MANAGER',
  UserRole.MEMBER: 'MEMBER',
  UserRole.VIEWER: 'VIEWER',
};
