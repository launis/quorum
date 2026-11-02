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

_TokenExchangeRequestDto _$TokenExchangeRequestDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_TokenExchangeRequestDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'firebase_token',
        'target_user_id',
        'service_auth_secret',
      ],
    );
    final val = _TokenExchangeRequestDto(
      firebaseToken: $checkedConvert('firebase_token', (v) => v as String?),
      targetUserId: $checkedConvert('target_user_id', (v) => v as String?),
      serviceAuthSecret: $checkedConvert(
        'service_auth_secret',
        (v) => v as String?,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'firebaseToken': 'firebase_token',
    'targetUserId': 'target_user_id',
    'serviceAuthSecret': 'service_auth_secret',
  },
);

Map<String, dynamic> _$TokenExchangeRequestDtoToJson(
  _TokenExchangeRequestDto instance,
) => <String, dynamic>{
  'firebase_token': ?instance.firebaseToken,
  'target_user_id': ?instance.targetUserId,
  'service_auth_secret': ?instance.serviceAuthSecret,
};

_TokenExchangeResponseDto _$TokenExchangeResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_TokenExchangeResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'access_token',
        'token_type',
        'expires_in_seconds',
        'user',
      ],
    );
    final val = _TokenExchangeResponseDto(
      accessToken: $checkedConvert('access_token', (v) => v as String),
      tokenType: $checkedConvert('token_type', (v) => v as String? ?? 'bearer'),
      expiresInSeconds: $checkedConvert(
        'expires_in_seconds',
        (v) => (v as num).toInt(),
      ),
      user: $checkedConvert(
        'user',
        (v) => User.fromJson(v as Map<String, dynamic>),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'accessToken': 'access_token',
    'tokenType': 'token_type',
    'expiresInSeconds': 'expires_in_seconds',
  },
);

Map<String, dynamic> _$TokenExchangeResponseDtoToJson(
  _TokenExchangeResponseDto instance,
) => <String, dynamic>{
  'access_token': instance.accessToken,
  'token_type': instance.tokenType,
  'expires_in_seconds': instance.expiresInSeconds,
  'user': instance.user.toJson(),
};

_LogoutRequestDto _$LogoutRequestDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_LogoutRequestDto',
      json,
      ($checkedConvert) {
        $checkKeys(json, allowedKeys: const ['revoke_all_sessions']);
        final val = _LogoutRequestDto(
          revokeAllSessions: $checkedConvert(
            'revoke_all_sessions',
            (v) => v as bool? ?? false,
          ),
        );
        return val;
      },
      fieldKeyMap: const {'revokeAllSessions': 'revoke_all_sessions'},
    );

Map<String, dynamic> _$LogoutRequestDtoToJson(_LogoutRequestDto instance) =>
    <String, dynamic>{'revoke_all_sessions': instance.revokeAllSessions};

_LogoutResponseDto _$LogoutResponseDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_LogoutResponseDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['status', 'revoked_jti', 'all_sessions_revoked'],
        );
        final val = _LogoutResponseDto(
          status: $checkedConvert('status', (v) => v as String? ?? 'revoked'),
          revokedJti: $checkedConvert('revoked_jti', (v) => v as String),
          allSessionsRevoked: $checkedConvert(
            'all_sessions_revoked',
            (v) => v as bool,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'revokedJti': 'revoked_jti',
        'allSessionsRevoked': 'all_sessions_revoked',
      },
    );

Map<String, dynamic> _$LogoutResponseDtoToJson(_LogoutResponseDto instance) =>
    <String, dynamic>{
      'status': instance.status,
      'revoked_jti': instance.revokedJti,
      'all_sessions_revoked': instance.allSessionsRevoked,
    };

_UserCreate _$UserCreateFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_UserCreate',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'email',
        'name',
        'role',
        'organization_id',
        'is_active',
        'language',
        'theme_mode',
        'created_by',
        'password',
      ],
    );
    final val = _UserCreate(
      email: $checkedConvert('email', (v) => v as String),
      name: $checkedConvert('name', (v) => v as String?),
      role: $checkedConvert(
        'role',
        (v) => $enumDecodeNullable(_$UserRoleEnumMap, v) ?? UserRole.member,
      ),
      organizationId: $checkedConvert('organization_id', (v) => v as String),
      isActive: $checkedConvert('is_active', (v) => v as bool? ?? true),
      language: $checkedConvert('language', (v) => v as String?),
      themeMode: $checkedConvert('theme_mode', (v) => v as String?),
      createdBy: $checkedConvert('created_by', (v) => v as String?),
      password: $checkedConvert('password', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isActive': 'is_active',
    'themeMode': 'theme_mode',
    'createdBy': 'created_by',
  },
);

Map<String, dynamic> _$UserCreateToJson(_UserCreate instance) =>
    <String, dynamic>{
      'email': instance.email,
      'name': ?instance.name,
      'role': instance.role.toJson(),
      'organization_id': instance.organizationId,
      'is_active': instance.isActive,
      'language': ?instance.language,
      'theme_mode': ?instance.themeMode,
      'created_by': ?instance.createdBy,
      'password': ?instance.password,
    };

_UserUpdate _$UserUpdateFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_UserUpdate',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'name',
        'role',
        'organization_id',
        'is_active',
        'language',
        'theme_mode',
        'password',
      ],
    );
    final val = _UserUpdate(
      name: $checkedConvert('name', (v) => v as String?),
      role: $checkedConvert(
        'role',
        (v) => $enumDecodeNullable(_$UserRoleEnumMap, v),
      ),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      isActive: $checkedConvert('is_active', (v) => v as bool?),
      language: $checkedConvert('language', (v) => v as String?),
      themeMode: $checkedConvert('theme_mode', (v) => v as String?),
      password: $checkedConvert('password', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isActive': 'is_active',
    'themeMode': 'theme_mode',
  },
);

Map<String, dynamic> _$UserUpdateToJson(_UserUpdate instance) =>
    <String, dynamic>{
      'name': ?instance.name,
      'role': ?instance.role?.toJson(),
      'organization_id': ?instance.organizationId,
      'is_active': ?instance.isActive,
      'language': ?instance.language,
      'theme_mode': ?instance.themeMode,
      'password': ?instance.password,
    };
