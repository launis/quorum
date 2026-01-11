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

  const Organization({
    required this.id,
    required this.name,
    this.createdAt,
    this.updatedAt,
    required this.status,
    this.contactEmail,
    this.tier,
  });

  factory Organization.fromJson(Map<String, dynamic> json) =>
      _$OrganizationFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationToJson(this);
}
