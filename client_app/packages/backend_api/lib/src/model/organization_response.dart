//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/subscription_status.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class OrganizationResponse {
  /// Returns a new [OrganizationResponse] instance.
  OrganizationResponse({
    required this.id,

    required this.name,

    required this.tier,

    this.contactEmail,

    this.createdAt,

    this.billingId,

    this.subscriptionStatus = SubscriptionStatus.trial,

    this.quotaLimit = 10.0,

    this.tpmLimit = 100000,

    this.rpmLimit = 60,

    this.status = 'PENDING',
  });

  @JsonKey(name: r'id', required: true)
  final String id;

  @JsonKey(name: r'name', required: true)
  final String name;

  @JsonKey(name: r'tier', required: true)
  final String tier;

  @JsonKey(name: r'contact_email', required: false)
  final String? contactEmail;

  @JsonKey(name: r'created_at', required: false)
  final String? createdAt;

  @JsonKey(name: r'billing_id', required: false)
  final String? billingId;

  @JsonKey(
    defaultValue: SubscriptionStatus.trial,
    name: r'subscription_status',
    required: false,
  )
  final SubscriptionStatus? subscriptionStatus;

  @JsonKey(defaultValue: 10.0, name: r'quota_limit', required: false)
  final num? quotaLimit;

  @JsonKey(defaultValue: 100000, name: r'tpm_limit', required: false)
  final int? tpmLimit;

  @JsonKey(defaultValue: 60, name: r'rpm_limit', required: false)
  final int? rpmLimit;

  @JsonKey(defaultValue: 'PENDING', name: r'status', required: false)
  final String? status;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is OrganizationResponse &&
          other.id == id &&
          other.name == name &&
          other.tier == tier &&
          other.contactEmail == contactEmail &&
          other.createdAt == createdAt &&
          other.billingId == billingId &&
          other.subscriptionStatus == subscriptionStatus &&
          other.quotaLimit == quotaLimit &&
          other.tpmLimit == tpmLimit &&
          other.rpmLimit == rpmLimit &&
          other.status == status;

  @override
  int get hashCode =>
      id.hashCode +
      name.hashCode +
      tier.hashCode +
      (contactEmail == null ? 0 : contactEmail.hashCode) +
      (createdAt == null ? 0 : createdAt.hashCode) +
      (billingId == null ? 0 : billingId.hashCode) +
      subscriptionStatus.hashCode +
      quotaLimit.hashCode +
      tpmLimit.hashCode +
      rpmLimit.hashCode +
      status.hashCode;

  factory OrganizationResponse.fromJson(Map<String, dynamic> json) =>
      _$OrganizationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
