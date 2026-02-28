//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization_usage_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class OrganizationUsageResponse {
  /// Returns a new [OrganizationUsageResponse] instance.
  OrganizationUsageResponse({
    required this.totalCostUsd,

    required this.quotaLimitUsd,

    required this.tpmLimit,

    required this.rpmLimit,

    required this.percentageUsed,

    required this.period,
  });

  @JsonKey(name: r'total_cost_usd', required: true)
  final num totalCostUsd;

  @JsonKey(name: r'quota_limit_usd', required: true)
  final num quotaLimitUsd;

  @JsonKey(name: r'tpm_limit', required: true)
  final int tpmLimit;

  @JsonKey(name: r'rpm_limit', required: true)
  final int rpmLimit;

  @JsonKey(name: r'percentage_used', required: true)
  final num percentageUsed;

  @JsonKey(name: r'period', required: true)
  final String period;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is OrganizationUsageResponse &&
          other.totalCostUsd == totalCostUsd &&
          other.quotaLimitUsd == quotaLimitUsd &&
          other.tpmLimit == tpmLimit &&
          other.rpmLimit == rpmLimit &&
          other.percentageUsed == percentageUsed &&
          other.period == period;

  @override
  int get hashCode =>
      totalCostUsd.hashCode +
      quotaLimitUsd.hashCode +
      tpmLimit.hashCode +
      rpmLimit.hashCode +
      percentageUsed.hashCode +
      period.hashCode;

  factory OrganizationUsageResponse.fromJson(Map<String, dynamic> json) =>
      _$OrganizationUsageResponseFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationUsageResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
