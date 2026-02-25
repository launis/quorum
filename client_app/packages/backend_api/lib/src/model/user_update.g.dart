// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_update.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UserUpdateCWProxy {
  UserUpdate displayName(String? displayName);

  UserUpdate role(UserRole? role);

  UserUpdate isActive(bool? isActive);

  UserUpdate password(String? password);

  UserUpdate language(String? language);

  UserUpdate themeMode(String? themeMode);

  UserUpdate organizationId(String? organizationId);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  UserUpdate call({
    String? displayName,
    UserRole? role,
    bool? isActive,
    String? password,
    String? language,
    String? themeMode,
    String? organizationId,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUserUpdate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUserUpdate.copyWith.fieldName(...)`
class _$UserUpdateCWProxyImpl implements _$UserUpdateCWProxy {
  const _$UserUpdateCWProxyImpl(this._value);

  final UserUpdate _value;

  @override
  UserUpdate displayName(String? displayName) => this(displayName: displayName);

  @override
  UserUpdate role(UserRole? role) => this(role: role);

  @override
  UserUpdate isActive(bool? isActive) => this(isActive: isActive);

  @override
  UserUpdate password(String? password) => this(password: password);

  @override
  UserUpdate language(String? language) => this(language: language);

  @override
  UserUpdate themeMode(String? themeMode) => this(themeMode: themeMode);

  @override
  UserUpdate organizationId(String? organizationId) =>
      this(organizationId: organizationId);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  UserUpdate call({
    Object? displayName = const $CopyWithPlaceholder(),
    Object? role = const $CopyWithPlaceholder(),
    Object? isActive = const $CopyWithPlaceholder(),
    Object? password = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? themeMode = const $CopyWithPlaceholder(),
    Object? organizationId = const $CopyWithPlaceholder(),
  }) {
    return UserUpdate(
      displayName: displayName == const $CopyWithPlaceholder()
          ? _value.displayName
          // ignore: cast_nullable_to_non_nullable
          : displayName as String?,
      role: role == const $CopyWithPlaceholder()
          ? _value.role
          // ignore: cast_nullable_to_non_nullable
          : role as UserRole?,
      isActive: isActive == const $CopyWithPlaceholder()
          ? _value.isActive
          // ignore: cast_nullable_to_non_nullable
          : isActive as bool?,
      password: password == const $CopyWithPlaceholder()
          ? _value.password
          // ignore: cast_nullable_to_non_nullable
          : password as String?,
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String?,
      themeMode: themeMode == const $CopyWithPlaceholder()
          ? _value.themeMode
          // ignore: cast_nullable_to_non_nullable
          : themeMode as String?,
      organizationId: organizationId == const $CopyWithPlaceholder()
          ? _value.organizationId
          // ignore: cast_nullable_to_non_nullable
          : organizationId as String?,
    );
  }
}

extension $UserUpdateCopyWith on UserUpdate {
  /// Returns a callable class that can be used as follows: `instanceOfUserUpdate.copyWith(...)` or like so:`instanceOfUserUpdate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UserUpdateCWProxy get copyWith => _$UserUpdateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserUpdate _$UserUpdateFromJson(Map<String, dynamic> json) => $checkedCreate(
  'UserUpdate',
  json,
  ($checkedConvert) {
    final val = UserUpdate(
      displayName: $checkedConvert('display_name', (v) => v as String?),
      role: $checkedConvert(
        'role',
        (v) => $enumDecodeNullable(_$UserRoleEnumMap, v),
      ),
      isActive: $checkedConvert('is_active', (v) => v as bool?),
      password: $checkedConvert('password', (v) => v as String?),
      language: $checkedConvert('language', (v) => v as String?),
      themeMode: $checkedConvert('theme_mode', (v) => v as String?),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'displayName': 'display_name',
    'isActive': 'is_active',
    'themeMode': 'theme_mode',
    'organizationId': 'organization_id',
  },
);

Map<String, dynamic> _$UserUpdateToJson(UserUpdate instance) =>
    <String, dynamic>{
      'display_name': ?instance.displayName,
      'role': ?_$UserRoleEnumMap[instance.role],
      'is_active': ?instance.isActive,
      'password': ?instance.password,
      'language': ?instance.language,
      'theme_mode': ?instance.themeMode,
      'organization_id': ?instance.organizationId,
    };

const _$UserRoleEnumMap = {
  UserRole.ROOT: 'ROOT',
  UserRole.ADMIN: 'ADMIN',
  UserRole.MANAGER: 'MANAGER',
  UserRole.MEMBER: 'MEMBER',
  UserRole.VIEWER: 'VIEWER',
};
