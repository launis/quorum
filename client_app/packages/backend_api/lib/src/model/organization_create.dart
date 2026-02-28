//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization_create.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class OrganizationCreate {
  /// Returns a new [OrganizationCreate] instance.
  OrganizationCreate({
    required this.name,

    required this.adminEmail,

    required this.adminPassword,

    required this.adminName,

    this.tpmLimit = 100000,

    this.rpmLimit = 60,
  });

  @JsonKey(name: r'name', required: true)
  final String name;

  @JsonKey(name: r'admin_email', required: true)
  final String adminEmail;

  @JsonKey(name: r'admin_password', required: true)
  final String adminPassword;

  @JsonKey(name: r'admin_name', required: true)
  final String adminName;

  @JsonKey(defaultValue: 100000, name: r'tpm_limit', required: false)
  final int? tpmLimit;

  @JsonKey(defaultValue: 60, name: r'rpm_limit', required: false)
  final int? rpmLimit;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is OrganizationCreate &&
          other.name == name &&
          other.adminEmail == adminEmail &&
          other.adminPassword == adminPassword &&
          other.adminName == adminName &&
          other.tpmLimit == tpmLimit &&
          other.rpmLimit == rpmLimit;

  @override
  int get hashCode =>
      name.hashCode +
      adminEmail.hashCode +
      adminPassword.hashCode +
      adminName.hashCode +
      tpmLimit.hashCode +
      rpmLimit.hashCode;

  factory OrganizationCreate.fromJson(Map<String, dynamic> json) =>
      _$OrganizationCreateFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationCreateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
