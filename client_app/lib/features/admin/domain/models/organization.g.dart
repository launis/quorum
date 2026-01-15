// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Organization _$OrganizationFromJson(Map<String, dynamic> json) => Organization(
  id: json['id'] as String,
  name: json['name'] as String,
  createdAt: json['created_at'] as String?,
  updatedAt: json['updated_at'] as String?,
  status:
      $enumDecodeNullable(
        _$OrganizationStatusEnumMap,
        json['status'],
        unknownValue: OrganizationStatus.unknown,
      ) ??
      OrganizationStatus.unknown,
  contactEmail: json['contact_email'] as String?,
  tier: json['tier'] as String?,
  tpmLimit: (json['tpm_limit'] as num?)?.toInt(),
  rpmLimit: (json['rpm_limit'] as num?)?.toInt(),
  quotaLimit: (json['quota_limit'] as num?)?.toDouble(),
);

Map<String, dynamic> _$OrganizationToJson(Organization instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
      'status': _$OrganizationStatusEnumMap[instance.status]!,
      'contact_email': instance.contactEmail,
      'tier': instance.tier,
      'tpm_limit': instance.tpmLimit,
      'rpm_limit': instance.rpmLimit,
      'quota_limit': instance.quotaLimit,
    };

const _$OrganizationStatusEnumMap = {
  OrganizationStatus.active: 'ACTIVE',
  OrganizationStatus.suspended: 'SUSPENDED',
  OrganizationStatus.pending: 'PENDING',
  OrganizationStatus.unknown: 'unknown',
};
