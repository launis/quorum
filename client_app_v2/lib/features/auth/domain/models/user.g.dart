// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_User _$UserFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_User',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'email',
        'role',
        'organization_id',
        'name',
        'created_at',
        'language',
        'theme_mode',
        'last_login_at',
        'execution_count',
        'is_active',
        'created_by',
      ],
    );
    final val = _User(
      id: $checkedConvert('id', (v) => v as String),
      slug: $checkedConvert('slug', (v) => v as String?),
      email: $checkedConvert('email', (v) => v as String),
      role: $checkedConvert('role', (v) => $enumDecode(_$UserRoleEnumMap, v)),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      name: $checkedConvert('name', (v) => v as String?),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      language: $checkedConvert('language', (v) => v as String?),
      themeMode: $checkedConvert('theme_mode', (v) => v as String?),
      lastLoginAt: $checkedConvert(
        'last_login_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      executionCount: $checkedConvert(
        'execution_count',
        (v) => (v as num?)?.toInt(),
      ),
      isActive: $checkedConvert('is_active', (v) => v as bool?),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'createdAt': 'created_at',
    'themeMode': 'theme_mode',
    'lastLoginAt': 'last_login_at',
    'executionCount': 'execution_count',
    'isActive': 'is_active',
    'createdBy': 'created_by',
  },
);

Map<String, dynamic> _$UserToJson(_User instance) => <String, dynamic>{
  'id': instance.id,
  'slug': instance.slug,
  'email': instance.email,
  'role': instance.role.toJson(),
  'organization_id': instance.organizationId,
  'name': instance.name,
  'created_at': instance.createdAt,
  'language': instance.language,
  'theme_mode': instance.themeMode,
  'last_login_at': instance.lastLoginAt?.toIso8601String(),
  'execution_count': instance.executionCount,
  'is_active': instance.isActive,
  'created_by': instance.createdBy,
};

const _$UserRoleEnumMap = {
  UserRole.root: 'ROOT',
  UserRole.admin: 'ADMIN',
  UserRole.manager: 'MANAGER',
  UserRole.member: 'MEMBER',
  UserRole.viewer: 'VIEWER',
  UserRole.unknown: 'UNKNOWN',
};
