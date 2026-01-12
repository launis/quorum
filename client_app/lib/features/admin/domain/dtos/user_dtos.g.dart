// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_dtos.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

// ignore: non_constant_identifier_names
_UserCreateDto _$UserCreateDtoFromJson(Map<String, dynamic> json) =>
    _UserCreateDto(
      email: json['email'] as String,
      password: json['password'] as String,
      displayName: json['display_name'] as String,
      role: $enumDecode(_$UserRoleEnumMap, json['role']),
      organizationId: json['organization_id'] as String?,
    );

// ignore: non_constant_identifier_names
Map<String, dynamic> _$UserCreateDtoToJson(_UserCreateDto instance) {
  final val = <String, dynamic>{
    'email': instance.email,
    'password': instance.password,
    'display_name': instance.displayName,
    'role': _$UserRoleEnumMap[instance.role]!,
  };

  void writeNotNull(String key, dynamic value) {
    if (value != null) {
      val[key] = value;
    }
  }

  writeNotNull('organization_id', instance.organizationId);
  return val;
}

const _$UserRoleEnumMap = {
  UserRole.root: 'ROOT',
  UserRole.admin: 'ADMIN',
  UserRole.manager: 'MANAGER',
  UserRole.member: 'MEMBER',
  UserRole.viewer: 'VIEWER',
  UserRole.unknown: 'unknown',
};

// ignore: non_constant_identifier_names
_UserUpdateDto _$UserUpdateDtoFromJson(Map<String, dynamic> json) =>
    _UserUpdateDto(
      displayName: json['display_name'] as String?,
      role: $enumDecodeNullable(_$UserRoleEnumMap, json['role']),
      isActive: json['is_active'] as bool?,
    );

// ignore: non_constant_identifier_names
Map<String, dynamic> _$UserUpdateDtoToJson(_UserUpdateDto instance) {
  final val = <String, dynamic>{};

  void writeNotNull(String key, dynamic value) {
    if (value != null) {
      val[key] = value;
    }
  }

  writeNotNull('display_name', instance.displayName);
  writeNotNull('role', _$UserRoleEnumMap[instance.role]);
  writeNotNull('is_active', instance.isActive);
  return val;
}
