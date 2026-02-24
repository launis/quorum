import 'package:json_annotation/json_annotation.dart';

part 'organization.g.dart';

enum OrganizationStatus {
  @JsonValue('ACTIVE')
  active,
  @JsonValue('SUSPENDED')
  suspended,
  @JsonValue('PENDING')
  pending,
  unknown,
}

@JsonSerializable()
class Organization {
  final String id;
  final String? slug;
  final String name;

  @JsonKey(name: 'created_at')
  final String? createdAt;

  @JsonKey(name: 'updated_at')
  final String? updatedAt;

  @JsonKey(
    defaultValue: OrganizationStatus.unknown,
    unknownEnumValue: OrganizationStatus.unknown,
  )
  final OrganizationStatus status;

  @JsonKey(name: 'contact_email')
  final String? contactEmail;

  final String? tier;

  @JsonKey(name: 'tpm_limit')
  final int? tpmLimit;

  @JsonKey(name: 'rpm_limit')
  final int? rpmLimit;

  @JsonKey(name: 'quota_limit')
  final double? quotaLimit;

  const Organization({
    required this.id,
    this.slug,
    required this.name,
    this.createdAt,
    this.updatedAt,
    required this.status,
    this.contactEmail,
    this.tier,
    this.tpmLimit,
    this.rpmLimit,
    this.quotaLimit,
  });

  factory Organization.fromJson(Map<String, dynamic> json) =>
      _$OrganizationFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationToJson(this);
}
