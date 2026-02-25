// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationCWProxy {
  Organization id(String? id);

  Organization slug(String? slug);

  Organization name(String name);

  Organization createdAt(DateTime? createdAt);

  Organization isActive(bool? isActive);

  Organization tier(String? tier);

  Organization contactEmail(String? contactEmail);

  Organization billingId(String? billingId);

  Organization subscriptionStatus(SubscriptionStatus? subscriptionStatus);

  Organization quotaLimit(num? quotaLimit);

  Organization tpmLimit(int? tpmLimit);

  Organization rpmLimit(int? rpmLimit);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Organization(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Organization(...).copyWith(id: 12, name: "My name")
  /// ````
  Organization call({
    String? id,
    String? slug,
    String name,
    DateTime? createdAt,
    bool? isActive,
    String? tier,
    String? contactEmail,
    String? billingId,
    SubscriptionStatus? subscriptionStatus,
    num? quotaLimit,
    int? tpmLimit,
    int? rpmLimit,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganization.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganization.copyWith.fieldName(...)`
class _$OrganizationCWProxyImpl implements _$OrganizationCWProxy {
  const _$OrganizationCWProxyImpl(this._value);

  final Organization _value;

  @override
  Organization id(String? id) => this(id: id);

  @override
  Organization slug(String? slug) => this(slug: slug);

  @override
  Organization name(String name) => this(name: name);

  @override
  Organization createdAt(DateTime? createdAt) => this(createdAt: createdAt);

  @override
  Organization isActive(bool? isActive) => this(isActive: isActive);

  @override
  Organization tier(String? tier) => this(tier: tier);

  @override
  Organization contactEmail(String? contactEmail) =>
      this(contactEmail: contactEmail);

  @override
  Organization billingId(String? billingId) => this(billingId: billingId);

  @override
  Organization subscriptionStatus(SubscriptionStatus? subscriptionStatus) =>
      this(subscriptionStatus: subscriptionStatus);

  @override
  Organization quotaLimit(num? quotaLimit) => this(quotaLimit: quotaLimit);

  @override
  Organization tpmLimit(int? tpmLimit) => this(tpmLimit: tpmLimit);

  @override
  Organization rpmLimit(int? rpmLimit) => this(rpmLimit: rpmLimit);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Organization(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Organization(...).copyWith(id: 12, name: "My name")
  /// ````
  Organization call({
    Object? id = const $CopyWithPlaceholder(),
    Object? slug = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
    Object? isActive = const $CopyWithPlaceholder(),
    Object? tier = const $CopyWithPlaceholder(),
    Object? contactEmail = const $CopyWithPlaceholder(),
    Object? billingId = const $CopyWithPlaceholder(),
    Object? subscriptionStatus = const $CopyWithPlaceholder(),
    Object? quotaLimit = const $CopyWithPlaceholder(),
    Object? tpmLimit = const $CopyWithPlaceholder(),
    Object? rpmLimit = const $CopyWithPlaceholder(),
  }) {
    return Organization(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
      slug: slug == const $CopyWithPlaceholder()
          ? _value.slug
          // ignore: cast_nullable_to_non_nullable
          : slug as String?,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as DateTime?,
      isActive: isActive == const $CopyWithPlaceholder()
          ? _value.isActive
          // ignore: cast_nullable_to_non_nullable
          : isActive as bool?,
      tier: tier == const $CopyWithPlaceholder()
          ? _value.tier
          // ignore: cast_nullable_to_non_nullable
          : tier as String?,
      contactEmail: contactEmail == const $CopyWithPlaceholder()
          ? _value.contactEmail
          // ignore: cast_nullable_to_non_nullable
          : contactEmail as String?,
      billingId: billingId == const $CopyWithPlaceholder()
          ? _value.billingId
          // ignore: cast_nullable_to_non_nullable
          : billingId as String?,
      subscriptionStatus: subscriptionStatus == const $CopyWithPlaceholder()
          ? _value.subscriptionStatus
          // ignore: cast_nullable_to_non_nullable
          : subscriptionStatus as SubscriptionStatus?,
      quotaLimit: quotaLimit == const $CopyWithPlaceholder()
          ? _value.quotaLimit
          // ignore: cast_nullable_to_non_nullable
          : quotaLimit as num?,
      tpmLimit: tpmLimit == const $CopyWithPlaceholder()
          ? _value.tpmLimit
          // ignore: cast_nullable_to_non_nullable
          : tpmLimit as int?,
      rpmLimit: rpmLimit == const $CopyWithPlaceholder()
          ? _value.rpmLimit
          // ignore: cast_nullable_to_non_nullable
          : rpmLimit as int?,
    );
  }
}

extension $OrganizationCopyWith on Organization {
  /// Returns a callable class that can be used as follows: `instanceOfOrganization.copyWith(...)` or like so:`instanceOfOrganization.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationCWProxy get copyWith => _$OrganizationCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Organization _$OrganizationFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'Organization',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['name']);
        final val = Organization(
          id: $checkedConvert('id', (v) => v as String?),
          slug: $checkedConvert('slug', (v) => v as String?),
          name: $checkedConvert('name', (v) => v as String),
          createdAt: $checkedConvert(
            'created_at',
            (v) => v == null ? null : DateTime.parse(v as String),
          ),
          isActive: $checkedConvert('is_active', (v) => v as bool? ?? true),
          tier: $checkedConvert('tier', (v) => v as String? ?? 'standard'),
          contactEmail: $checkedConvert('contact_email', (v) => v as String?),
          billingId: $checkedConvert('billing_id', (v) => v as String?),
          subscriptionStatus: $checkedConvert(
            'subscription_status',
            (v) =>
                $enumDecodeNullable(_$SubscriptionStatusEnumMap, v) ??
                SubscriptionStatus.trial,
          ),
          quotaLimit: $checkedConvert('quota_limit', (v) => v as num? ?? 10.0),
          tpmLimit: $checkedConvert(
            'tpm_limit',
            (v) => (v as num?)?.toInt() ?? 100000,
          ),
          rpmLimit: $checkedConvert(
            'rpm_limit',
            (v) => (v as num?)?.toInt() ?? 60,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'createdAt': 'created_at',
        'isActive': 'is_active',
        'contactEmail': 'contact_email',
        'billingId': 'billing_id',
        'subscriptionStatus': 'subscription_status',
        'quotaLimit': 'quota_limit',
        'tpmLimit': 'tpm_limit',
        'rpmLimit': 'rpm_limit',
      },
    );

Map<String, dynamic> _$OrganizationToJson(Organization instance) =>
    <String, dynamic>{
      'id': ?instance.id,
      'slug': ?instance.slug,
      'name': instance.name,
      'created_at': ?instance.createdAt?.toIso8601String(),
      'is_active': ?instance.isActive,
      'tier': ?instance.tier,
      'contact_email': ?instance.contactEmail,
      'billing_id': ?instance.billingId,
      'subscription_status':
          ?_$SubscriptionStatusEnumMap[instance.subscriptionStatus],
      'quota_limit': ?instance.quotaLimit,
      'tpm_limit': ?instance.tpmLimit,
      'rpm_limit': ?instance.rpmLimit,
    };

const _$SubscriptionStatusEnumMap = {
  SubscriptionStatus.active: 'active',
  SubscriptionStatus.pastDue: 'past_due',
  SubscriptionStatus.canceled: 'canceled',
  SubscriptionStatus.trial: 'trial',
};
