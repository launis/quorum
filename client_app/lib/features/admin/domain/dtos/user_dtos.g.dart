// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_dtos.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UserCreateDto _$UserCreateDtoFromJson(Map<String, dynamic> json) =>
    _UserCreateDto(
      email: json['email'] as String,
      password: json['password'] as String,
      displayName: json['display_name'] as String,
      role: $enumDecode(_$UserRoleEnumMap, json['role']),
      organizationId: json['organization_id'] as String?,
    );

Map<String, dynamic> _$UserCreateDtoToJson(_UserCreateDto instance) =>
    <String, dynamic>{
      'email': instance.email,
      'password': instance.password,
      'display_name': instance.displayName,
      'role': _$UserRoleEnumMap[instance.role]!,
      'organization_id': instance.organizationId,
    };

const _$UserRoleEnumMap = {
  UserRole.root: 'ROOT',
  UserRole.admin: 'ADMIN',
  UserRole.manager: 'MANAGER',
  UserRole.member: 'MEMBER',
  UserRole.viewer: 'VIEWER',
  UserRole.unknown: 'unknown',
};

_UserUpdateDto _$UserUpdateDtoFromJson(Map<String, dynamic> json) =>
    _UserUpdateDto(
      displayName: json['display_name'] as String?,
      role: $enumDecodeNullable(_$UserRoleEnumMap, json['role']),
      isActive: json['is_active'] as bool?,
      organizationId: json['organization_id'] as String?,
    );

Map<String, dynamic> _$UserUpdateDtoToJson(_UserUpdateDto instance) =>
    <String, dynamic>{
      'display_name': instance.displayName,
      'role': _$UserRoleEnumMap[instance.role],
      'is_active': instance.isActive,
      'organization_id': instance.organizationId,
    };
