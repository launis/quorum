// ignore_for_file: invalid_annotation_target
import 'package:client_app/core/models/enums.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'report_artifact.freezed.dart';
part 'report_artifact.g.dart';

/// Storage artifact paths for materialized reports across different formats.
@Freezed(equal: false)
abstract class ReportStoragePaths with _$ReportStoragePaths {
  const ReportStoragePaths._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportStoragePaths({
    @JsonKey(name: 'pdf_path') String? pdfPath,
    @JsonKey(name: 'sdui_json_path') String? sduiJsonPath,
    @JsonKey(name: 'excel_path') String? excelPath,
    @JsonKey(name: 'csv_path') String? csvPath,
  }) = _ReportStoragePaths;

  factory ReportStoragePaths.fromJson(Map<String, dynamic> json) =>
      _$ReportStoragePathsFromJson(json);
}

/// Execution and FinOps telemetry metadata captured during report generation.
@Freezed(equal: false)
abstract class ReportMetadata with _$ReportMetadata {
  const ReportMetadata._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportMetadata({
    @JsonKey(name: 'cost_usd') double? costUsd,
    @JsonKey(name: 'duration_ms') int? durationMs,
    @JsonKey(name: 'tokens_used') int? tokensUsed,
    @JsonKey(name: 'llm_model') String? llmModel,
    @JsonKey(name: 'provider') String? provider,
    @JsonKey(name: 'cognitive_tier') CognitiveTier? cognitiveTier,
    @JsonKey(name: 'model_registry_id') String? modelRegistryId,
    @JsonKey(name: 'thinking_tokens') int? thinkingTokens,
  }) = _ReportMetadata;

  factory ReportMetadata.fromJson(Map<String, dynamic> json) =>
      _$ReportMetadataFromJson(json);
}

/// Tabular row item for B2B structured data extraction and forensic evidence.
@Freezed(equal: false)
abstract class ReportRowItem with _$ReportRowItem {
  const ReportRowItem._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportRowItem({
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'report_id') required String reportId,
    @JsonKey(name: 'metric_key') required String metricKey,
    @JsonKey(name: 'metric_label') required String metricLabel,
    required double score,
    @JsonKey(name: 'max_scale') required double maxScale,
    required double weight,
    String? reasoning,
    String? quote,
  }) = _ReportRowItem;

  factory ReportRowItem.fromJson(Map<String, dynamic> json) =>
      _$ReportRowItemFromJson(json);
}

/// Materialized, independently versioned report artifact domain model.
@Freezed(equal: false)
abstract class ReportArtifact with _$ReportArtifact {
  const ReportArtifact._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportArtifact({
    required String id,
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'profile_id') required String profileId,
    required String locale,
    required String title,
    required ReportStatus status,
    @JsonKey(name: 'storage_paths')
    @Default(ReportStoragePaths())
    ReportStoragePaths storagePaths,
    @JsonKey(name: 'metadata')
    @Default(ReportMetadata())
    ReportMetadata metadata,
    @JsonKey(name: 'custom_preface_md') String? customPrefaceMd,
    @JsonKey(name: 'error_message') String? errorMessage,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
  }) = _ReportArtifact;

  factory ReportArtifact.fromJson(Map<String, dynamic> json) =>
      _$ReportArtifactFromJson(json);
}

/// Lightweight summary model for report list views and selector chips.
@Freezed(equal: false)
abstract class ReportArtifactSummary with _$ReportArtifactSummary {
  const ReportArtifactSummary._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportArtifactSummary({
    required String id,
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'profile_id') required String profileId,
    required String locale,
    required String title,
    required ReportStatus status,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
  }) = _ReportArtifactSummary;

  factory ReportArtifactSummary.fromJson(Map<String, dynamic> json) =>
      _$ReportArtifactSummaryFromJson(json);
}
