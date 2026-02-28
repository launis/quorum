//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/subscription_status.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class Organization {
  /// Returns a new [Organization] instance.
  Organization({
    this.id,

    this.slug,

    required this.name,

    this.createdAt,

    this.isActive = true,

    this.tier = 'standard',

    this.contactEmail,

    this.billingId,

    this.subscriptionStatus = SubscriptionStatus.trial,

    this.quotaLimit = 10.0,

    this.tpmLimit = 100000,

    this.rpmLimit = 60,
  });

  /// Unique Organization ID (e.g. 'nokia-v1')
  @JsonKey(name: r'id', required: false)
  final String? id;

  @JsonKey(name: r'slug', required: false)
  final String? slug;

  /// Display Name
  @JsonKey(name: r'name', required: true)
  final String name;

  @JsonKey(name: r'created_at', required: false)
  final DateTime? createdAt;

  /// Subscription status
  @JsonKey(defaultValue: true, name: r'is_active', required: false)
  final bool? isActive;

  /// Service Tier
  @JsonKey(defaultValue: 'standard', name: r'tier', required: false)
  final String? tier;

  @JsonKey(name: r'contact_email', required: false)
  final String? contactEmail;

  @JsonKey(name: r'billing_id', required: false)
  final String? billingId;

  /// Current billing status
  @JsonKey(
    defaultValue: SubscriptionStatus.trial,
    name: r'subscription_status',
    required: false,
  )
  final SubscriptionStatus? subscriptionStatus;

  /// Monthly API call quota (USD)
  // minimum: 0.0
  @JsonKey(defaultValue: 10.0, name: r'quota_limit', required: false)
  final num? quotaLimit;

  /// Tokens Per Minute Limit
  // minimum: 1000
  @JsonKey(defaultValue: 100000, name: r'tpm_limit', required: false)
  final int? tpmLimit;

  /// Requests Per Minute Limit
  // minimum: 1
  @JsonKey(defaultValue: 60, name: r'rpm_limit', required: false)
  final int? rpmLimit;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Organization &&
          other.id == id &&
          other.slug == slug &&
          other.name == name &&
          other.createdAt == createdAt &&
          other.isActive == isActive &&
          other.tier == tier &&
          other.contactEmail == contactEmail &&
          other.billingId == billingId &&
          other.subscriptionStatus == subscriptionStatus &&
          other.quotaLimit == quotaLimit &&
          other.tpmLimit == tpmLimit &&
          other.rpmLimit == rpmLimit;

  @override
  int get hashCode =>
      id.hashCode +
      (slug == null ? 0 : slug.hashCode) +
      name.hashCode +
      (createdAt == null ? 0 : createdAt.hashCode) +
      isActive.hashCode +
      tier.hashCode +
      (contactEmail == null ? 0 : contactEmail.hashCode) +
      (billingId == null ? 0 : billingId.hashCode) +
      subscriptionStatus.hashCode +
      quotaLimit.hashCode +
      tpmLimit.hashCode +
      rpmLimit.hashCode;

  factory Organization.fromJson(Map<String, dynamic> json) =>
      _$OrganizationFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
