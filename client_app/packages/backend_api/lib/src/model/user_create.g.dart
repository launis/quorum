// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_create.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UserCreateCWProxy {
  UserCreate email(String email);

  UserCreate displayName(String? displayName);

  UserCreate role(UserRole? role);

  UserCreate organizationId(String? organizationId);

  UserCreate isActive(bool? isActive);

  UserCreate language(UserCreateLanguageEnum? language);

  UserCreate themeMode(UserCreateThemeModeEnum? themeMode);

  UserCreate password(String? password);

  UserCreate createdBy(String? createdBy);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  UserCreate call({
    String email,
    String? displayName,
    UserRole? role,
    String? organizationId,
    bool? isActive,
    UserCreateLanguageEnum? language,
    UserCreateThemeModeEnum? themeMode,
    String? password,
    String? createdBy,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUserCreate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUserCreate.copyWith.fieldName(...)`
class _$UserCreateCWProxyImpl implements _$UserCreateCWProxy {
  const _$UserCreateCWProxyImpl(this._value);

  final UserCreate _value;

  @override
  UserCreate email(String email) => this(email: email);

  @override
  UserCreate displayName(String? displayName) => this(displayName: displayName);

  @override
  UserCreate role(UserRole? role) => this(role: role);

  @override
  UserCreate organizationId(String? organizationId) =>
      this(organizationId: organizationId);

  @override
  UserCreate isActive(bool? isActive) => this(isActive: isActive);

  @override
  UserCreate language(UserCreateLanguageEnum? language) =>
      this(language: language);

  @override
  UserCreate themeMode(UserCreateThemeModeEnum? themeMode) =>
      this(themeMode: themeMode);

  @override
  UserCreate password(String? password) => this(password: password);

  @override
  UserCreate createdBy(String? createdBy) => this(createdBy: createdBy);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  UserCreate call({
    Object? email = const $CopyWithPlaceholder(),
    Object? displayName = const $CopyWithPlaceholder(),
    Object? role = const $CopyWithPlaceholder(),
    Object? organizationId = const $CopyWithPlaceholder(),
    Object? isActive = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? themeMode = const $CopyWithPlaceholder(),
    Object? password = const $CopyWithPlaceholder(),
    Object? createdBy = const $CopyWithPlaceholder(),
  }) {
    return UserCreate(
      email: email == const $CopyWithPlaceholder()
          ? _value.email
          // ignore: cast_nullable_to_non_nullable
          : email as String,
      displayName: displayName == const $CopyWithPlaceholder()
          ? _value.displayName
          // ignore: cast_nullable_to_non_nullable
          : displayName as String?,
      role: role == const $CopyWithPlaceholder()
          ? _value.role
          // ignore: cast_nullable_to_non_nullable
          : role as UserRole?,
      organizationId: organizationId == const $CopyWithPlaceholder()
          ? _value.organizationId
          // ignore: cast_nullable_to_non_nullable
          : organizationId as String?,
      isActive: isActive == const $CopyWithPlaceholder()
          ? _value.isActive
          // ignore: cast_nullable_to_non_nullable
          : isActive as bool?,
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as UserCreateLanguageEnum?,
      themeMode: themeMode == const $CopyWithPlaceholder()
          ? _value.themeMode
          // ignore: cast_nullable_to_non_nullable
          : themeMode as UserCreateThemeModeEnum?,
      password: password == const $CopyWithPlaceholder()
          ? _value.password
          // ignore: cast_nullable_to_non_nullable
          : password as String?,
      createdBy: createdBy == const $CopyWithPlaceholder()
          ? _value.createdBy
          // ignore: cast_nullable_to_non_nullable
          : createdBy as String?,
    );
  }
}

extension $UserCreateCopyWith on UserCreate {
  /// Returns a callable class that can be used as follows: `instanceOfUserCreate.copyWith(...)` or like so:`instanceOfUserCreate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UserCreateCWProxy get copyWith => _$UserCreateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserCreate _$UserCreateFromJson(Map<String, dynamic> json) => $checkedCreate(
  'UserCreate',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['email']);
    final val = UserCreate(
      email: $checkedConvert('email', (v) => v as String),
      displayName: $checkedConvert('display_name', (v) => v as String?),
      role: $checkedConvert(
        'role',
        (v) => $enumDecodeNullable(_$UserRoleEnumMap, v) ?? UserRole.MEMBER,
      ),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      isActive: $checkedConvert('is_active', (v) => v as bool? ?? true),
      language: $checkedConvert(
        'language',
        (v) =>
            $enumDecodeNullable(_$UserCreateLanguageEnumEnumMap, v) ??
            UserCreateLanguageEnum.fi,
      ),
      themeMode: $checkedConvert(
        'theme_mode',
        (v) =>
            $enumDecodeNullable(_$UserCreateThemeModeEnumEnumMap, v) ??
            UserCreateThemeModeEnum.system,
      ),
      password: $checkedConvert('password', (v) => v as String?),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'displayName': 'display_name',
    'organizationId': 'organization_id',
    'isActive': 'is_active',
    'themeMode': 'theme_mode',
    'createdBy': 'created_by',
  },
);

Map<String, dynamic> _$UserCreateToJson(UserCreate instance) =>
    <String, dynamic>{
      'email': instance.email,
      'display_name': ?instance.displayName,
      'role': ?_$UserRoleEnumMap[instance.role],
      'organization_id': ?instance.organizationId,
      'is_active': ?instance.isActive,
      'language': ?_$UserCreateLanguageEnumEnumMap[instance.language],
      'theme_mode': ?_$UserCreateThemeModeEnumEnumMap[instance.themeMode],
      'password': ?instance.password,
      'created_by': ?instance.createdBy,
    };

const _$UserRoleEnumMap = {
  UserRole.ROOT: 'ROOT',
  UserRole.ADMIN: 'ADMIN',
  UserRole.MANAGER: 'MANAGER',
  UserRole.MEMBER: 'MEMBER',
  UserRole.VIEWER: 'VIEWER',
};

const _$UserCreateLanguageEnumEnumMap = {
  UserCreateLanguageEnum.fi: 'fi',
  UserCreateLanguageEnum.en: 'en',
  UserCreateLanguageEnum.sv: 'sv',
};

const _$UserCreateThemeModeEnumEnumMap = {
  UserCreateThemeModeEnum.system: 'system',
  UserCreateThemeModeEnum.light: 'light',
  UserCreateThemeModeEnum.dark: 'dark',
};
