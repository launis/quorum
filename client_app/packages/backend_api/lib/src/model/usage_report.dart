//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/token_usage.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'usage_report.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class UsageReport {
  /// Returns a new [UsageReport] instance.
  UsageReport({
    required this.scope,

    this.entityId,

    required this.period,

    this.usage,

    this.quotaLimitUsd,

    this.percentageUsed,
  });

  /// Scope of the report (system, organization, user).
  @JsonKey(name: r'scope', required: true)
  final String scope;

  @JsonKey(name: r'entity_id', required: false)
  final String? entityId;

  /// Reporting period (e.g., '2026-02', 'all-time').
  @JsonKey(name: r'period', required: true)
  final String period;

  /// Aggregated token and cost statistics.
  @JsonKey(name: r'usage', required: false)
  final TokenUsage? usage;

  @JsonKey(name: r'quota_limit_usd', required: false)
  final num? quotaLimitUsd;

  @JsonKey(name: r'percentage_used', required: false)
  final num? percentageUsed;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UsageReport &&
          other.scope == scope &&
          other.entityId == entityId &&
          other.period == period &&
          other.usage == usage &&
          other.quotaLimitUsd == quotaLimitUsd &&
          other.percentageUsed == percentageUsed;

  @override
  int get hashCode =>
      scope.hashCode +
      (entityId == null ? 0 : entityId.hashCode) +
      period.hashCode +
      usage.hashCode +
      (quotaLimitUsd == null ? 0 : quotaLimitUsd.hashCode) +
      (percentageUsed == null ? 0 : percentageUsed.hashCode);

  factory UsageReport.fromJson(Map<String, dynamic> json) =>
      _$UsageReportFromJson(json);

  Map<String, dynamic> toJson() => _$UsageReportToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
