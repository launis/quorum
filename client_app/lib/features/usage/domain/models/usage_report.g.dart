// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_report.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TokenUsage _$TokenUsageFromJson(Map<String, dynamic> json) => TokenUsage(
  promptTokens: (json['prompt_tokens'] as num?)?.toInt() ?? 0,
  completionTokens: (json['completion_tokens'] as num?)?.toInt() ?? 0,
  totalTokens: (json['total_tokens'] as num?)?.toInt() ?? 0,
  costUsd: (json['cost_usd'] as num?)?.toDouble() ?? 0.0,
);

Map<String, dynamic> _$TokenUsageToJson(TokenUsage instance) =>
    <String, dynamic>{
      'prompt_tokens': instance.promptTokens,
      'completion_tokens': instance.completionTokens,
      'total_tokens': instance.totalTokens,
      'cost_usd': instance.costUsd,
    };

UsageReport _$UsageReportFromJson(Map<String, dynamic> json) => UsageReport(
  scope: json['scope'] as String,
  entityId: json['entity_id'] as String?,
  period: json['period'] as String,
  usage: TokenUsage.fromJson(json['usage'] as Map<String, dynamic>),
  quotaLimitUsd: (json['quota_limit_usd'] as num?)?.toDouble(),
  percentageUsed: (json['percentage_used'] as num?)?.toDouble(),
);

Map<String, dynamic> _$UsageReportToJson(UsageReport instance) =>
    <String, dynamic>{
      'scope': instance.scope,
      'entity_id': instance.entityId,
      'period': instance.period,
      'usage': instance.usage,
      'quota_limit_usd': instance.quotaLimitUsd,
      'percentage_used': instance.percentageUsed,
    };
