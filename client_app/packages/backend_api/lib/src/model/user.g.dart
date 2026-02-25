// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UserCWProxy {
  User email(String email);

  User displayName(String? displayName);

  User role(UserRole? role);

  User organizationId(String? organizationId);

  User isActive(bool? isActive);

  User language(UserLanguageEnum? language);

  User themeMode(UserThemeModeEnum? themeMode);

  User id(String? id);

  User slug(String? slug);

  User createdAt(DateTime createdAt);

  User createdBy(String? createdBy);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `User(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// User(...).copyWith(id: 12, name: "My name")
  /// ````
  User call({
    String email,
    String? displayName,
    UserRole? role,
    String? organizationId,
    bool? isActive,
    UserLanguageEnum? language,
    UserThemeModeEnum? themeMode,
    String? id,
    String? slug,
    DateTime createdAt,
    String? createdBy,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUser.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUser.copyWith.fieldName(...)`
class _$UserCWProxyImpl implements _$UserCWProxy {
  const _$UserCWProxyImpl(this._value);

  final User _value;

  @override
  User email(String email) => this(email: email);

  @override
  User displayName(String? displayName) => this(displayName: displayName);

  @override
  User role(UserRole? role) => this(role: role);

  @override
  User organizationId(String? organizationId) =>
      this(organizationId: organizationId);

  @override
  User isActive(bool? isActive) => this(isActive: isActive);

  @override
  User language(UserLanguageEnum? language) => this(language: language);

  @override
  User themeMode(UserThemeModeEnum? themeMode) => this(themeMode: themeMode);

  @override
  User id(String? id) => this(id: id);

  @override
  User slug(String? slug) => this(slug: slug);

  @override
  User createdAt(DateTime createdAt) => this(createdAt: createdAt);

  @override
  User createdBy(String? createdBy) => this(createdBy: createdBy);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `User(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// User(...).copyWith(id: 12, name: "My name")
  /// ````
  User call({
    Object? email = const $CopyWithPlaceholder(),
    Object? displayName = const $CopyWithPlaceholder(),
    Object? role = const $CopyWithPlaceholder(),
    Object? organizationId = const $CopyWithPlaceholder(),
    Object? isActive = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? themeMode = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
    Object? createdBy = const $CopyWithPlaceholder(),
  }) {
    return User(
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
          : language as UserLanguageEnum?,
      themeMode: themeMode == const $CopyWithPlaceholder()
          ? _value.themeMode
          // ignore: cast_nullable_to_non_nullable
          : themeMode as UserThemeModeEnum?,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
      slug: slug == const $CopyWithPlaceholder()
          ? _value.slug
          // ignore: cast_nullable_to_non_nullable
          : slug as String?,
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as DateTime,
      createdBy: createdBy == const $CopyWithPlaceholder()
          ? _value.createdBy
          // ignore: cast_nullable_to_non_nullable
          : createdBy as String?,
    );
  }
}

extension $UserCopyWith on User {
  /// Returns a callable class that can be used as follows: `instanceOfUser.copyWith(...)` or like so:`instanceOfUser.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UserCWProxy get copyWith => _$UserCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => $checkedCreate(
  'User',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['email', 'created_at']);
    final val = User(
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
        (v) => $enumDecodeNullable(_$UserLanguageEnumEnumMap, v) ?? UserLanguageEnum.fi,
      ),
      themeMode: $checkedConvert(
        'theme_mode',
        (v) => $enumDecodeNullable(_$UserThemeModeEnumEnumMap, v) ?? UserThemeModeEnum.system,
      ),
      id: $checkedConvert('id', (v) => v as String?),
      slug: $checkedConvert('slug', (v) => v as String?),
      createdAt: $checkedConvert(
        'created_at',
        (v) => DateTime.parse(v as String),
      ),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'displayName': 'display_name',
    'organizationId': 'organization_id',
    'isActive': 'is_active',
    'themeMode': 'theme_mode',
    'createdAt': 'created_at',
    'createdBy': 'created_by',
  },
);

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
  'email': instance.email,
  'display_name': ?instance.displayName,
  'role': ?_$UserRoleEnumMap[instance.role],
  'organization_id': ?instance.organizationId,
  'is_active': ?instance.isActive,
  'language': ?_$UserLanguageEnumEnumMap[instance.language],
  'theme_mode': ?_$UserThemeModeEnumEnumMap[instance.themeMode],
  'id': ?instance.id,
  'slug': ?instance.slug,
  'created_at': instance.createdAt.toIso8601String(),
  'created_by': ?instance.createdBy,
};

const _$UserRoleEnumMap = {
  UserRole.ROOT: 'ROOT',
  UserRole.ADMIN: 'ADMIN',
  UserRole.MANAGER: 'MANAGER',
  UserRole.MEMBER: 'MEMBER',
  UserRole.VIEWER: 'VIEWER',
};

const _$UserLanguageEnumEnumMap = {
  UserLanguageEnum.fi: 'fi',
  UserLanguageEnum.en: 'en',
  UserLanguageEnum.sv: 'sv',
};

const _$UserThemeModeEnumEnumMap = {
  UserThemeModeEnum.system: 'system',
  UserThemeModeEnum.light: 'light',
  UserThemeModeEnum.dark: 'dark',
};
