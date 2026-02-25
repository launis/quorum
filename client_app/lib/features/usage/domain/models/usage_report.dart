import 'package:json_annotation/json_annotation.dart';

part 'usage_report.g.dart';

@JsonSerializable()
class TokenUsage {
  @JsonKey(name: 'prompt_tokens')
  final int promptTokens;

  @JsonKey(name: 'completion_tokens')
  final int completionTokens;

  @JsonKey(name: 'total_tokens')
  final int totalTokens;

  @JsonKey(name: 'cost_usd')
  final double costUsd;

  const TokenUsage({
    this.promptTokens = 0,
    this.completionTokens = 0,
    this.totalTokens = 0,
    this.costUsd = 0.0,
  });

  factory TokenUsage.fromJson(Map<String, dynamic> json) =>
      _$TokenUsageFromJson(json);

  Map<String, dynamic> toJson() => _$TokenUsageToJson(this);
}

@JsonSerializable()
class UsageReport {
  final String scope;

  @JsonKey(name: 'entity_id')
  final String? entityId;

  final String period;
  final TokenUsage usage;

  @JsonKey(name: 'quota_limit_usd')
  final double? quotaLimitUsd;

  @JsonKey(name: 'percentage_used')
  final double? percentageUsed;

  const UsageReport({
    required this.scope,
    this.entityId,
    required this.period,
    required this.usage,
    this.quotaLimitUsd,
    this.percentageUsed,
  });

  factory UsageReport.fromJson(Map<String, dynamic> json) =>
      _$UsageReportFromJson(json);

  Map<String, dynamic> toJson() => _$UsageReportToJson(this);
}
