// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => User(
  id: json['id'] as String,
  slug: json['slug'] as String?,
  email: json['email'] as String,
  role:
      $enumDecodeNullable(
        _$UserRoleEnumMap,
        json['role'],
        unknownValue: UserRole.unknown,
      ) ??
      UserRole.viewer,
  organizationId: json['organization_id'] as String?,
  displayName: json['display_name'] as String?,
  createdAt: json['created_at'] as String?,
  language: json['language'] as String?,
  themeMode: json['theme_mode'] as String?,
  lastLoginAt:
      json['last_login_at'] == null
          ? null
          : DateTime.parse(json['last_login_at'] as String),
  executionCount: (json['execution_count'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
  'id': instance.id,
  'slug': instance.slug,
  'email': instance.email,
  'role': _$UserRoleEnumMap[instance.role]!,
  'organization_id': instance.organizationId,
  'display_name': instance.displayName,
  'created_at': instance.createdAt,
  'language': instance.language,
  'theme_mode': instance.themeMode,
  'last_login_at': instance.lastLoginAt?.toIso8601String(),
  'execution_count': instance.executionCount,
};

const _$UserRoleEnumMap = {
  UserRole.root: 'ROOT',
  UserRole.admin: 'ADMIN',
  UserRole.manager: 'MANAGER',
  UserRole.member: 'MEMBER',
  UserRole.viewer: 'VIEWER',
  UserRole.unknown: 'unknown',
};
