// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_report.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$UsageReportCWProxy {
  UsageReport scope(String scope);

  UsageReport entityId(String? entityId);

  UsageReport period(String period);

  UsageReport usage(TokenUsage? usage);

  UsageReport quotaLimitUsd(num? quotaLimitUsd);

  UsageReport percentageUsed(num? percentageUsed);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UsageReport(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UsageReport(...).copyWith(id: 12, name: "My name")
  /// ````
  UsageReport call({
    String scope,
    String? entityId,
    String period,
    TokenUsage? usage,
    num? quotaLimitUsd,
    num? percentageUsed,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfUsageReport.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfUsageReport.copyWith.fieldName(...)`
class _$UsageReportCWProxyImpl implements _$UsageReportCWProxy {
  const _$UsageReportCWProxyImpl(this._value);

  final UsageReport _value;

  @override
  UsageReport scope(String scope) => this(scope: scope);

  @override
  UsageReport entityId(String? entityId) => this(entityId: entityId);

  @override
  UsageReport period(String period) => this(period: period);

  @override
  UsageReport usage(TokenUsage? usage) => this(usage: usage);

  @override
  UsageReport quotaLimitUsd(num? quotaLimitUsd) =>
      this(quotaLimitUsd: quotaLimitUsd);

  @override
  UsageReport percentageUsed(num? percentageUsed) =>
      this(percentageUsed: percentageUsed);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `UsageReport(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// UsageReport(...).copyWith(id: 12, name: "My name")
  /// ````
  UsageReport call({
    Object? scope = const $CopyWithPlaceholder(),
    Object? entityId = const $CopyWithPlaceholder(),
    Object? period = const $CopyWithPlaceholder(),
    Object? usage = const $CopyWithPlaceholder(),
    Object? quotaLimitUsd = const $CopyWithPlaceholder(),
    Object? percentageUsed = const $CopyWithPlaceholder(),
  }) {
    return UsageReport(
      scope: scope == const $CopyWithPlaceholder()
          ? _value.scope
          // ignore: cast_nullable_to_non_nullable
          : scope as String,
      entityId: entityId == const $CopyWithPlaceholder()
          ? _value.entityId
          // ignore: cast_nullable_to_non_nullable
          : entityId as String?,
      period: period == const $CopyWithPlaceholder()
          ? _value.period
          // ignore: cast_nullable_to_non_nullable
          : period as String,
      usage: usage == const $CopyWithPlaceholder()
          ? _value.usage
          // ignore: cast_nullable_to_non_nullable
          : usage as TokenUsage?,
      quotaLimitUsd: quotaLimitUsd == const $CopyWithPlaceholder()
          ? _value.quotaLimitUsd
          // ignore: cast_nullable_to_non_nullable
          : quotaLimitUsd as num?,
      percentageUsed: percentageUsed == const $CopyWithPlaceholder()
          ? _value.percentageUsed
          // ignore: cast_nullable_to_non_nullable
          : percentageUsed as num?,
    );
  }
}

extension $UsageReportCopyWith on UsageReport {
  /// Returns a callable class that can be used as follows: `instanceOfUsageReport.copyWith(...)` or like so:`instanceOfUsageReport.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$UsageReportCWProxy get copyWith => _$UsageReportCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UsageReport _$UsageReportFromJson(Map<String, dynamic> json) => $checkedCreate(
  'UsageReport',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['scope', 'period']);
    final val = UsageReport(
      scope: $checkedConvert('scope', (v) => v as String),
      entityId: $checkedConvert('entity_id', (v) => v as String?),
      period: $checkedConvert('period', (v) => v as String),
      usage: $checkedConvert(
        'usage',
        (v) =>
            v == null ? null : TokenUsage.fromJson(v as Map<String, dynamic>),
      ),
      quotaLimitUsd: $checkedConvert('quota_limit_usd', (v) => v as num?),
      percentageUsed: $checkedConvert('percentage_used', (v) => v as num?),
    );
    return val;
  },
  fieldKeyMap: const {
    'entityId': 'entity_id',
    'quotaLimitUsd': 'quota_limit_usd',
    'percentageUsed': 'percentage_used',
  },
);

Map<String, dynamic> _$UsageReportToJson(UsageReport instance) =>
    <String, dynamic>{
      'scope': instance.scope,
      'entity_id': ?instance.entityId,
      'period': instance.period,
      'usage': ?instance.usage?.toJson(),
      'quota_limit_usd': ?instance.quotaLimitUsd,
      'percentage_used': ?instance.percentageUsed,
    };
