// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => User(
  uid: json['uid'] as String,
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
);

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
  'uid': instance.uid,
  'email': instance.email,
  'role': _$UserRoleEnumMap[instance.role]!,
  'organization_id': instance.organizationId,
  'display_name': instance.displayName,
  'created_at': instance.createdAt,
};

const _$UserRoleEnumMap = {
  UserRole.root: 'ROOT',
  UserRole.admin: 'ADMIN',
  UserRole.manager: 'MANAGER',
  UserRole.member: 'MEMBER',
  UserRole.viewer: 'VIEWER',
  UserRole.unknown: 'unknown',
};
