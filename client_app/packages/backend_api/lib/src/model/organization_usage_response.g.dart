// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_usage_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationUsageResponseCWProxy {
  OrganizationUsageResponse totalCostUsd(num totalCostUsd);

  OrganizationUsageResponse quotaLimitUsd(num quotaLimitUsd);

  OrganizationUsageResponse tpmLimit(int tpmLimit);

  OrganizationUsageResponse rpmLimit(int rpmLimit);

  OrganizationUsageResponse percentageUsed(num percentageUsed);

  OrganizationUsageResponse period(String period);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationUsageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationUsageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationUsageResponse call({
    num totalCostUsd,
    num quotaLimitUsd,
    int tpmLimit,
    int rpmLimit,
    num percentageUsed,
    String period,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganizationUsageResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganizationUsageResponse.copyWith.fieldName(...)`
class _$OrganizationUsageResponseCWProxyImpl
    implements _$OrganizationUsageResponseCWProxy {
  const _$OrganizationUsageResponseCWProxyImpl(this._value);

  final OrganizationUsageResponse _value;

  @override
  OrganizationUsageResponse totalCostUsd(num totalCostUsd) =>
      this(totalCostUsd: totalCostUsd);

  @override
  OrganizationUsageResponse quotaLimitUsd(num quotaLimitUsd) =>
      this(quotaLimitUsd: quotaLimitUsd);

  @override
  OrganizationUsageResponse tpmLimit(int tpmLimit) => this(tpmLimit: tpmLimit);

  @override
  OrganizationUsageResponse rpmLimit(int rpmLimit) => this(rpmLimit: rpmLimit);

  @override
  OrganizationUsageResponse percentageUsed(num percentageUsed) =>
      this(percentageUsed: percentageUsed);

  @override
  OrganizationUsageResponse period(String period) => this(period: period);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationUsageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationUsageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationUsageResponse call({
    Object? totalCostUsd = const $CopyWithPlaceholder(),
    Object? quotaLimitUsd = const $CopyWithPlaceholder(),
    Object? tpmLimit = const $CopyWithPlaceholder(),
    Object? rpmLimit = const $CopyWithPlaceholder(),
    Object? percentageUsed = const $CopyWithPlaceholder(),
    Object? period = const $CopyWithPlaceholder(),
  }) {
    return OrganizationUsageResponse(
      totalCostUsd: totalCostUsd == const $CopyWithPlaceholder()
          ? _value.totalCostUsd
          // ignore: cast_nullable_to_non_nullable
          : totalCostUsd as num,
      quotaLimitUsd: quotaLimitUsd == const $CopyWithPlaceholder()
          ? _value.quotaLimitUsd
          // ignore: cast_nullable_to_non_nullable
          : quotaLimitUsd as num,
      tpmLimit: tpmLimit == const $CopyWithPlaceholder()
          ? _value.tpmLimit
          // ignore: cast_nullable_to_non_nullable
          : tpmLimit as int,
      rpmLimit: rpmLimit == const $CopyWithPlaceholder()
          ? _value.rpmLimit
          // ignore: cast_nullable_to_non_nullable
          : rpmLimit as int,
      percentageUsed: percentageUsed == const $CopyWithPlaceholder()
          ? _value.percentageUsed
          // ignore: cast_nullable_to_non_nullable
          : percentageUsed as num,
      period: period == const $CopyWithPlaceholder()
          ? _value.period
          // ignore: cast_nullable_to_non_nullable
          : period as String,
    );
  }
}

extension $OrganizationUsageResponseCopyWith on OrganizationUsageResponse {
  /// Returns a callable class that can be used as follows: `instanceOfOrganizationUsageResponse.copyWith(...)` or like so:`instanceOfOrganizationUsageResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationUsageResponseCWProxy get copyWith =>
      _$OrganizationUsageResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

OrganizationUsageResponse _$OrganizationUsageResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'OrganizationUsageResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const [
        'total_cost_usd',
        'quota_limit_usd',
        'tpm_limit',
        'rpm_limit',
        'percentage_used',
        'period',
      ],
    );
    final val = OrganizationUsageResponse(
      totalCostUsd: $checkedConvert('total_cost_usd', (v) => v as num),
      quotaLimitUsd: $checkedConvert('quota_limit_usd', (v) => v as num),
      tpmLimit: $checkedConvert('tpm_limit', (v) => (v as num).toInt()),
      rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num).toInt()),
      percentageUsed: $checkedConvert('percentage_used', (v) => v as num),
      period: $checkedConvert('period', (v) => v as String),
    );
    return val;
  },
  fieldKeyMap: const {
    'totalCostUsd': 'total_cost_usd',
    'quotaLimitUsd': 'quota_limit_usd',
    'tpmLimit': 'tpm_limit',
    'rpmLimit': 'rpm_limit',
    'percentageUsed': 'percentage_used',
  },
);

Map<String, dynamic> _$OrganizationUsageResponseToJson(
  OrganizationUsageResponse instance,
) => <String, dynamic>{
  'total_cost_usd': instance.totalCostUsd,
  'quota_limit_usd': instance.quotaLimitUsd,
  'tpm_limit': instance.tpmLimit,
  'rpm_limit': instance.rpmLimit,
  'percentage_used': instance.percentageUsed,
  'period': instance.period,
};
