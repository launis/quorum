// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_create_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationCreateRequestCWProxy {
  OrganizationCreateRequest id(String? id);

  OrganizationCreateRequest name(String name);

  OrganizationCreateRequest tier(String? tier);

  OrganizationCreateRequest contactEmail(String? contactEmail);

  OrganizationCreateRequest billingId(String? billingId);

  OrganizationCreateRequest subscriptionStatus(
    SubscriptionStatus? subscriptionStatus,
  );

  OrganizationCreateRequest quotaLimit(num? quotaLimit);

  OrganizationCreateRequest settingsOverride(
    Map<String, Object>? settingsOverride,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationCreateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationCreateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationCreateRequest call({
    String? id,
    String name,
    String? tier,
    String? contactEmail,
    String? billingId,
    SubscriptionStatus? subscriptionStatus,
    num? quotaLimit,
    Map<String, Object>? settingsOverride,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganizationCreateRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganizationCreateRequest.copyWith.fieldName(...)`
class _$OrganizationCreateRequestCWProxyImpl
    implements _$OrganizationCreateRequestCWProxy {
  const _$OrganizationCreateRequestCWProxyImpl(this._value);

  final OrganizationCreateRequest _value;

  @override
  OrganizationCreateRequest id(String? id) => this(id: id);

  @override
  OrganizationCreateRequest name(String name) => this(name: name);

  @override
  OrganizationCreateRequest tier(String? tier) => this(tier: tier);

  @override
  OrganizationCreateRequest contactEmail(String? contactEmail) =>
      this(contactEmail: contactEmail);

  @override
  OrganizationCreateRequest billingId(String? billingId) =>
      this(billingId: billingId);

  @override
  OrganizationCreateRequest subscriptionStatus(
    SubscriptionStatus? subscriptionStatus,
  ) => this(subscriptionStatus: subscriptionStatus);

  @override
  OrganizationCreateRequest quotaLimit(num? quotaLimit) =>
      this(quotaLimit: quotaLimit);

  @override
  OrganizationCreateRequest settingsOverride(
    Map<String, Object>? settingsOverride,
  ) => this(settingsOverride: settingsOverride);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationCreateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationCreateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationCreateRequest call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? tier = const $CopyWithPlaceholder(),
    Object? contactEmail = const $CopyWithPlaceholder(),
    Object? billingId = const $CopyWithPlaceholder(),
    Object? subscriptionStatus = const $CopyWithPlaceholder(),
    Object? quotaLimit = const $CopyWithPlaceholder(),
    Object? settingsOverride = const $CopyWithPlaceholder(),
  }) {
    return OrganizationCreateRequest(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String?,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
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
      settingsOverride: settingsOverride == const $CopyWithPlaceholder()
          ? _value.settingsOverride
          // ignore: cast_nullable_to_non_nullable
          : settingsOverride as Map<String, Object>?,
    );
  }
}

extension $OrganizationCreateRequestCopyWith on OrganizationCreateRequest {
  /// Returns a callable class that can be used as follows: `instanceOfOrganizationCreateRequest.copyWith(...)` or like so:`instanceOfOrganizationCreateRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationCreateRequestCWProxy get copyWith =>
      _$OrganizationCreateRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

OrganizationCreateRequest _$OrganizationCreateRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'OrganizationCreateRequest',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['name']);
    final val = OrganizationCreateRequest(
      id: $checkedConvert('id', (v) => v as String?),
      name: $checkedConvert('name', (v) => v as String),
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
    'settingsOverride': 'settings_override',
  },
);

Map<String, dynamic> _$OrganizationCreateRequestToJson(
  OrganizationCreateRequest instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'name': instance.name,
  'tier': ?instance.tier,
  'contact_email': ?instance.contactEmail,
  'billing_id': ?instance.billingId,
  'subscription_status':
      ?_$SubscriptionStatusEnumMap[instance.subscriptionStatus],
  'quota_limit': ?instance.quotaLimit,
  'settings_override': ?instance.settingsOverride,
};

const _$SubscriptionStatusEnumMap = {
  SubscriptionStatus.active: 'active',
  SubscriptionStatus.pastDue: 'past_due',
  SubscriptionStatus.canceled: 'canceled',
  SubscriptionStatus.trial: 'trial',
};
