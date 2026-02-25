// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_admin_view.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UserAdminViewCWProxy {
  UserAdminView email(String email);

  UserAdminView displayName(String? displayName);

  UserAdminView role(UserRole? role);

  UserAdminView organizationId(String? organizationId);

  UserAdminView isActive(bool? isActive);

  UserAdminView language(UserAdminViewLanguageEnum? language);

  UserAdminView themeMode(UserAdminViewThemeModeEnum? themeMode);

  UserAdminView id(String id);

  UserAdminView slug(String? slug);

  UserAdminView createdAt(DateTime createdAt);

  UserAdminView createdBy(String? createdBy);

  UserAdminView lastLoginAt(DateTime? lastLoginAt);

  UserAdminView executionCount(int? executionCount);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserAdminView(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserAdminView(...).copyWith(id: 12, name: "My name")
  /// ````
  UserAdminView call({
    String email,
    String? displayName,
    UserRole? role,
    String? organizationId,
    bool? isActive,
    UserAdminViewLanguageEnum? language,
    UserAdminViewThemeModeEnum? themeMode,
    String id,
    String? slug,
    DateTime createdAt,
    String? createdBy,
    DateTime? lastLoginAt,
    int? executionCount,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUserAdminView.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUserAdminView.copyWith.fieldName(...)`
class _$UserAdminViewCWProxyImpl implements _$UserAdminViewCWProxy {
  const _$UserAdminViewCWProxyImpl(this._value);

  final UserAdminView _value;

  @override
  UserAdminView email(String email) => this(email: email);

  @override
  UserAdminView displayName(String? displayName) =>
      this(displayName: displayName);

  @override
  UserAdminView role(UserRole? role) => this(role: role);

  @override
  UserAdminView organizationId(String? organizationId) =>
      this(organizationId: organizationId);

  @override
  UserAdminView isActive(bool? isActive) => this(isActive: isActive);

  @override
  UserAdminView language(UserAdminViewLanguageEnum? language) =>
      this(language: language);

  @override
  UserAdminView themeMode(UserAdminViewThemeModeEnum? themeMode) =>
      this(themeMode: themeMode);

  @override
  UserAdminView id(String id) => this(id: id);

  @override
  UserAdminView slug(String? slug) => this(slug: slug);

  @override
  UserAdminView createdAt(DateTime createdAt) => this(createdAt: createdAt);

  @override
  UserAdminView createdBy(String? createdBy) => this(createdBy: createdBy);

  @override
  UserAdminView lastLoginAt(DateTime? lastLoginAt) =>
      this(lastLoginAt: lastLoginAt);

  @override
  UserAdminView executionCount(int? executionCount) =>
      this(executionCount: executionCount);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UserAdminView(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UserAdminView(...).copyWith(id: 12, name: "My name")
  /// ````
  UserAdminView call({
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
    Object? lastLoginAt = const $CopyWithPlaceholder(),
    Object? executionCount = const $CopyWithPlaceholder(),
  }) {
    return UserAdminView(
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
          : language as UserAdminViewLanguageEnum?,
      themeMode: themeMode == const $CopyWithPlaceholder()
          ? _value.themeMode
          // ignore: cast_nullable_to_non_nullable
          : themeMode as UserAdminViewThemeModeEnum?,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
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
      lastLoginAt: lastLoginAt == const $CopyWithPlaceholder()
          ? _value.lastLoginAt
          // ignore: cast_nullable_to_non_nullable
          : lastLoginAt as DateTime?,
      executionCount: executionCount == const $CopyWithPlaceholder()
          ? _value.executionCount
          // ignore: cast_nullable_to_non_nullable
          : executionCount as int?,
    );
  }
}

extension $UserAdminViewCopyWith on UserAdminView {
  /// Returns a callable class that can be used as follows: `instanceOfUserAdminView.copyWith(...)` or like so:`instanceOfUserAdminView.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UserAdminViewCWProxy get copyWith => _$UserAdminViewCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserAdminView _$UserAdminViewFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'UserAdminView',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['email', 'id', 'created_at']);
    final val = UserAdminView(
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
            $enumDecodeNullable(_$UserAdminViewLanguageEnumEnumMap, v) ?? UserAdminViewLanguageEnum.fi,
      ),
      themeMode: $checkedConvert(
        'theme_mode',
        (v) =>
            $enumDecodeNullable(_$UserAdminViewThemeModeEnumEnumMap, v) ??
            UserAdminViewThemeModeEnum.system,
      ),
      id: $checkedConvert('id', (v) => v as String),
      slug: $checkedConvert('slug', (v) => v as String?),
      createdAt: $checkedConvert(
        'created_at',
        (v) => DateTime.parse(v as String),
      ),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
      lastLoginAt: $checkedConvert(
        'last_login_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      executionCount: $checkedConvert(
        'execution_count',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
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
    'lastLoginAt': 'last_login_at',
    'executionCount': 'execution_count',
  },
);

Map<String, dynamic> _$UserAdminViewToJson(UserAdminView instance) =>
    <String, dynamic>{
      'email': instance.email,
      'display_name': ?instance.displayName,
      'role': ?_$UserRoleEnumMap[instance.role],
      'organization_id': ?instance.organizationId,
      'is_active': ?instance.isActive,
      'language': ?_$UserAdminViewLanguageEnumEnumMap[instance.language],
      'theme_mode': ?_$UserAdminViewThemeModeEnumEnumMap[instance.themeMode],
      'id': instance.id,
      'slug': ?instance.slug,
      'created_at': instance.createdAt.toIso8601String(),
      'created_by': ?instance.createdBy,
      'last_login_at': ?instance.lastLoginAt?.toIso8601String(),
      'execution_count': ?instance.executionCount,
    };

const _$UserRoleEnumMap = {
  UserRole.ROOT: 'ROOT',
  UserRole.ADMIN: 'ADMIN',
  UserRole.MANAGER: 'MANAGER',
  UserRole.MEMBER: 'MEMBER',
  UserRole.VIEWER: 'VIEWER',
};

const _$UserAdminViewLanguageEnumEnumMap = {
  UserAdminViewLanguageEnum.fi: 'fi',
  UserAdminViewLanguageEnum.en: 'en',
  UserAdminViewLanguageEnum.sv: 'sv',
};

const _$UserAdminViewThemeModeEnumEnumMap = {
  UserAdminViewThemeModeEnum.system: 'system',
  UserAdminViewThemeModeEnum.light: 'light',
  UserAdminViewThemeModeEnum.dark: 'dark',
};
