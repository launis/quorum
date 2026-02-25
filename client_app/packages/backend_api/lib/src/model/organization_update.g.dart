// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_update.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationUpdateCWProxy {
  OrganizationUpdate name(String? name);

  OrganizationUpdate tier(String? tier);

  OrganizationUpdate contactEmail(String? contactEmail);

  OrganizationUpdate billingId(String? billingId);

  OrganizationUpdate subscriptionStatus(SubscriptionStatus? subscriptionStatus);

  OrganizationUpdate quotaLimit(num? quotaLimit);

  OrganizationUpdate tpmLimit(int? tpmLimit);

  OrganizationUpdate rpmLimit(int? rpmLimit);

  OrganizationUpdate settingsOverride(Map<String, Object>? settingsOverride);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationUpdate call({
    String? name,
    String? tier,
    String? contactEmail,
    String? billingId,
    SubscriptionStatus? subscriptionStatus,
    num? quotaLimit,
    int? tpmLimit,
    int? rpmLimit,
    Map<String, Object>? settingsOverride,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganizationUpdate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganizationUpdate.copyWith.fieldName(...)`
class _$OrganizationUpdateCWProxyImpl implements _$OrganizationUpdateCWProxy {
  const _$OrganizationUpdateCWProxyImpl(this._value);

  final OrganizationUpdate _value;

  @override
  OrganizationUpdate name(String? name) => this(name: name);

  @override
  OrganizationUpdate tier(String? tier) => this(tier: tier);

  @override
  OrganizationUpdate contactEmail(String? contactEmail) =>
      this(contactEmail: contactEmail);

  @override
  OrganizationUpdate billingId(String? billingId) => this(billingId: billingId);

  @override
  OrganizationUpdate subscriptionStatus(
    SubscriptionStatus? subscriptionStatus,
  ) => this(subscriptionStatus: subscriptionStatus);

  @override
  OrganizationUpdate quotaLimit(num? quotaLimit) =>
      this(quotaLimit: quotaLimit);

  @override
  OrganizationUpdate tpmLimit(int? tpmLimit) => this(tpmLimit: tpmLimit);

  @override
  OrganizationUpdate rpmLimit(int? rpmLimit) => this(rpmLimit: rpmLimit);

  @override
  OrganizationUpdate settingsOverride(Map<String, Object>? settingsOverride) =>
      this(settingsOverride: settingsOverride);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationUpdate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationUpdate(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationUpdate call({
    Object? name = const $CopyWithPlaceholder(),
    Object? tier = const $CopyWithPlaceholder(),
    Object? contactEmail = const $CopyWithPlaceholder(),
    Object? billingId = const $CopyWithPlaceholder(),
    Object? subscriptionStatus = const $CopyWithPlaceholder(),
    Object? quotaLimit = const $CopyWithPlaceholder(),
    Object? tpmLimit = const $CopyWithPlaceholder(),
    Object? rpmLimit = const $CopyWithPlaceholder(),
    Object? settingsOverride = const $CopyWithPlaceholder(),
  }) {
    return OrganizationUpdate(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
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
      settingsOverride: settingsOverride == const $CopyWithPlaceholder()
          ? _value.settingsOverride
          // ignore: cast_nullable_to_non_nullable
          : settingsOverride as Map<String, Object>?,
    );
  }
}

extension $OrganizationUpdateCopyWith on OrganizationUpdate {
  /// Returns a callable class that can be used as follows: `instanceOfOrganizationUpdate.copyWith(...)` or like so:`instanceOfOrganizationUpdate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationUpdateCWProxy get copyWith =>
      _$OrganizationUpdateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

OrganizationUpdate _$OrganizationUpdateFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'OrganizationUpdate',
      json,
      ($checkedConvert) {
        final val = OrganizationUpdate(
          name: $checkedConvert('name', (v) => v as String?),
          tier: $checkedConvert('tier', (v) => v as String?),
          contactEmail: $checkedConvert('contact_email', (v) => v as String?),
          billingId: $checkedConvert('billing_id', (v) => v as String?),
          subscriptionStatus: $checkedConvert(
            'subscription_status',
            (v) => $enumDecodeNullable(_$SubscriptionStatusEnumMap, v),
          ),
          quotaLimit: $checkedConvert('quota_limit', (v) => v as num?),
          tpmLimit: $checkedConvert('tpm_limit', (v) => (v as num?)?.toInt()),
          rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num?)?.toInt()),
          settingsOverride: $checkedConvert(
            'settings_override',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'contactEmail': 'contact_email',
        'billingId': 'billing_id',
        'subscriptionStatus': 'subscription_status',
        'quotaLimit': 'quota_limit',
        'tpmLimit': 'tpm_limit',
        'rpmLimit': 'rpm_limit',
        'settingsOverride': 'settings_override',
      },
    );

Map<String, dynamic> _$OrganizationUpdateToJson(OrganizationUpdate instance) =>
    <String, dynamic>{
      'name': ?instance.name,
      'tier': ?instance.tier,
      'contact_email': ?instance.contactEmail,
      'billing_id': ?instance.billingId,
      'subscription_status':
          ?_$SubscriptionStatusEnumMap[instance.subscriptionStatus],
      'quota_limit': ?instance.quotaLimit,
      'tpm_limit': ?instance.tpmLimit,
      'rpm_limit': ?instance.rpmLimit,
      'settings_override': ?instance.settingsOverride,
    };

const _$SubscriptionStatusEnumMap = {
  SubscriptionStatus.active: 'active',
  SubscriptionStatus.pastDue: 'past_due',
  SubscriptionStatus.canceled: 'canceled',
  SubscriptionStatus.trial: 'trial',
};
