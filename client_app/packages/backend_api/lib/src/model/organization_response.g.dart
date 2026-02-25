// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationResponseCWProxy {
  OrganizationResponse id(String id);

  OrganizationResponse name(String name);

  OrganizationResponse tier(String tier);

  OrganizationResponse contactEmail(String? contactEmail);

  OrganizationResponse createdAt(String? createdAt);

  OrganizationResponse billingId(String? billingId);

  OrganizationResponse subscriptionStatus(
    SubscriptionStatus? subscriptionStatus,
  );

  OrganizationResponse quotaLimit(num? quotaLimit);

  OrganizationResponse tpmLimit(int? tpmLimit);

  OrganizationResponse rpmLimit(int? rpmLimit);

  OrganizationResponse status(String? status);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationResponse call({
    String id,
    String name,
    String tier,
    String? contactEmail,
    String? createdAt,
    String? billingId,
    SubscriptionStatus? subscriptionStatus,
    num? quotaLimit,
    int? tpmLimit,
    int? rpmLimit,
    String? status,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganizationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganizationResponse.copyWith.fieldName(...)`
class _$OrganizationResponseCWProxyImpl
    implements _$OrganizationResponseCWProxy {
  const _$OrganizationResponseCWProxyImpl(this._value);

  final OrganizationResponse _value;

  @override
  OrganizationResponse id(String id) => this(id: id);

  @override
  OrganizationResponse name(String name) => this(name: name);

  @override
  OrganizationResponse tier(String tier) => this(tier: tier);

  @override
  OrganizationResponse contactEmail(String? contactEmail) =>
      this(contactEmail: contactEmail);

  @override
  OrganizationResponse createdAt(String? createdAt) =>
      this(createdAt: createdAt);

  @override
  OrganizationResponse billingId(String? billingId) =>
      this(billingId: billingId);

  @override
  OrganizationResponse subscriptionStatus(
    SubscriptionStatus? subscriptionStatus,
  ) => this(subscriptionStatus: subscriptionStatus);

  @override
  OrganizationResponse quotaLimit(num? quotaLimit) =>
      this(quotaLimit: quotaLimit);

  @override
  OrganizationResponse tpmLimit(int? tpmLimit) => this(tpmLimit: tpmLimit);

  @override
  OrganizationResponse rpmLimit(int? rpmLimit) => this(rpmLimit: rpmLimit);

  @override
  OrganizationResponse status(String? status) => this(status: status);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? tier = const $CopyWithPlaceholder(),
    Object? contactEmail = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
    Object? billingId = const $CopyWithPlaceholder(),
    Object? subscriptionStatus = const $CopyWithPlaceholder(),
    Object? quotaLimit = const $CopyWithPlaceholder(),
    Object? tpmLimit = const $CopyWithPlaceholder(),
    Object? rpmLimit = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
  }) {
    return OrganizationResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      tier: tier == const $CopyWithPlaceholder()
          ? _value.tier
          // ignore: cast_nullable_to_non_nullable
          : tier as String,
      contactEmail: contactEmail == const $CopyWithPlaceholder()
          ? _value.contactEmail
          // ignore: cast_nullable_to_non_nullable
          : contactEmail as String?,
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as String?,
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
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
    );
  }
}

extension $OrganizationResponseCopyWith on OrganizationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfOrganizationResponse.copyWith(...)` or like so:`instanceOfOrganizationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationResponseCWProxy get copyWith =>
      _$OrganizationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

OrganizationResponse _$OrganizationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'OrganizationResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['id', 'name', 'tier']);
    final val = OrganizationResponse(
      id: $checkedConvert('id', (v) => v as String),
      name: $checkedConvert('name', (v) => v as String),
      tier: $checkedConvert('tier', (v) => v as String),
      contactEmail: $checkedConvert('contact_email', (v) => v as String?),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
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
      rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num?)?.toInt() ?? 60),
      status: $checkedConvert('status', (v) => v as String? ?? 'PENDING'),
    );
    return val;
  },
  fieldKeyMap: const {
    'contactEmail': 'contact_email',
    'createdAt': 'created_at',
    'billingId': 'billing_id',
    'subscriptionStatus': 'subscription_status',
    'quotaLimit': 'quota_limit',
    'tpmLimit': 'tpm_limit',
    'rpmLimit': 'rpm_limit',
  },
);

Map<String, dynamic> _$OrganizationResponseToJson(
  OrganizationResponse instance,
) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'tier': instance.tier,
  'contact_email': ?instance.contactEmail,
  'created_at': ?instance.createdAt,
  'billing_id': ?instance.billingId,
  'subscription_status':
      ?_$SubscriptionStatusEnumMap[instance.subscriptionStatus],
  'quota_limit': ?instance.quotaLimit,
  'tpm_limit': ?instance.tpmLimit,
  'rpm_limit': ?instance.rpmLimit,
  'status': ?instance.status,
};

const _$SubscriptionStatusEnumMap = {
  SubscriptionStatus.active: 'active',
  SubscriptionStatus.pastDue: 'past_due',
  SubscriptionStatus.canceled: 'canceled',
  SubscriptionStatus.trial: 'trial',
};
