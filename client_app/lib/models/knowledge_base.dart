import 'package:freezed_annotation/freezed_annotation.dart';

part 'knowledge_base.freezed.dart';
part 'knowledge_base.g.dart';

@freezed
abstract class IngestionStatus with _$IngestionStatus {
  const factory IngestionStatus({
    @JsonKey(name: 'job_id') required String jobId,
    required String status, // processing, completed, failed
    required int progress,
    required String stage,
    IngestionSummary? result,
    String? error,
  }) = _IngestionStatus;

  factory IngestionStatus.fromJson(Map<String, dynamic> json) =>
      _$IngestionStatusFromJson(json);
}

@freezed
abstract class IngestionSummary with _$IngestionSummary {
  const factory IngestionSummary({
    @JsonKey(name: 'concepts_count') @Default(0) int conceptsCount,
    @JsonKey(name: 'references_count') @Default(0) int referencesCount,
    @JsonKey(name: 'claims_count') @Default(0) int claimsCount,
    @JsonKey(name: 'file_size') @Default(0) int fileSize,
    required String filename,
  }) = _IngestionSummary;

  factory IngestionSummary.fromJson(Map<String, dynamic> json) =>
      _$IngestionSummaryFromJson(json);
}

@freezed
abstract class KnowledgeModelStrategy with _$KnowledgeModelStrategy {
  const factory KnowledgeModelStrategy({
    required String id,
    String? slug,
    @JsonKey(name: 'model_name') required String modelName,
    String? provider,
  }) = _KnowledgeModelStrategy;

  factory KnowledgeModelStrategy.fromJson(Map<String, dynamic> json) =>
      _$KnowledgeModelStrategyFromJson(json);
}
