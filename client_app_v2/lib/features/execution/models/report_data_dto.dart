// ignore_for_file: invalid_annotation_target
import 'dart:convert';
import 'dart:isolate';

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/models/enums.dart';

part 'report_data_dto.freezed.dart';
part 'report_data_dto.g.dart';

/// Strictly typed DTO for a single reporting axis (e.g., metric, category).
/// Enforces Fail-Fast parsing preventing dynamic type errors via json_serializable.
@Freezed(equal: false)
abstract class ReportAxisDTO with _$ReportAxisDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportAxisDTO({
    required String name,
    String? description,
    double? score,
    required String justification,
    @JsonKey(name: 'cited_source_id') String? citedSourceId,
    @JsonKey(name: 'cited_text_quote') String? citedTextQuote,
    @JsonKey(name: 'cited_web_citation') String? citedWebCitation,

    // Epic 6: XAI Output Extensions
    String? coaching,
    double? confidence,
    String? falsification,
    @JsonKey(name: 'missing_context') String? missingContext,
    @JsonKey(name: 'risk_flag') bool? riskFlag,
    @JsonKey(name: 'remediation_steps') List<String>? remediationSteps,
    @JsonKey(name: 'emotional_sentiment') String? emotionalSentiment,
    @JsonKey(name: 'theory_link') String? theoryLink,

    @JsonKey(name: 'scale_min') @Default(0.0) double scaleMin,
    @JsonKey(name: 'scale_max') @Default(6.0) double scaleMax,
    @JsonKey(name: 'scale_labels') @Default({}) Map<String, String> scaleLabels,
    @JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,
    @JsonKey(name: 'ui_boundary_labels')
    @Default({})
    Map<String, String> uiBoundaryLabels,
  }) = _ReportAxisDTO;

  factory ReportAxisDTO.fromJson(Map<String, dynamic> json) =>
      _$ReportAxisDTOFromJson(json);
}

/// Strictly typed DTO representing a single layout block dynamically defining how to render axes.
/// Note: Added synthesis field to prevent checked JSON parsing errors.
@Freezed(equal: false)
abstract class ReportLayoutDTO with _$ReportLayoutDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportLayoutDTO({
    @JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)
    required PresetView presetView,
    @JsonKey(name: 'matrix_type') String? matrixType,
    I18nText? title,
    I18nText? description,
    @Default([]) List<ReportAxisDTO> axes,
    @JsonKey(name: 'text_delivery_mode') required String textDeliveryMode,
    Map<String, dynamic>? synthesis,
    @JsonKey(name: 'synthesis_md') String? synthesisMd,
  }) = _ReportLayoutDTO;

  factory ReportLayoutDTO.fromJson(Map<String, dynamic> json) =>
      _$ReportLayoutDTOFromJson(json);
}

/// Strictly typed DTO for a single MCP Tool Loop audit trace entry.
/// Used by XAIEvidenceBox to display AI fact-check sources.
@Freezed(equal: false)
abstract class MCPToolAuditDTO with _$MCPToolAuditDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MCPToolAuditDTO({
    String? id,
    @JsonKey(name: 'tool_id') required String toolId,
    @JsonKey(name: 'step_name') required String stepName,
    required String query,
    @JsonKey(name: 'response_summary') @Default('') String responseSummary,
    @JsonKey(name: 'source_urls') @Default([]) List<String> sourceUrls,
    String? timestamp,
    @JsonKey(name: 'duration_ms') @Default(0) int durationMs,
  }) = _MCPToolAuditDTO;

  factory MCPToolAuditDTO.fromJson(Map<String, dynamic> json) =>
      _$MCPToolAuditDTOFromJson(json);
}

/// Strictly typed DTO representing the universal V3 Render Payload.
@Freezed(equal: false)
abstract class ReportDataDTO with _$ReportDataDTO {
  const ReportDataDTO._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportDataDTO({
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'profile_id') required String profileId,
    @JsonKey(name: 'profile_name') I18nText? profileName,
    @JsonKey(name: 'available_profiles')
    @Default({})
    Map<String, I18nText> availableProfiles,
    @JsonKey(name: 'global_score') double? globalScore,
    @Default([]) List<ReportLayoutDTO> layouts,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'org_name') String? orgName,
    @JsonKey(name: 'cost_estimate') double? costEstimate,
    @JsonKey(name: 'total_tokens') int? totalTokens,
    @JsonKey(name: 'prompt_tokens') int? promptTokens,
    @JsonKey(name: 'completion_tokens') int? completionTokens,
    @JsonKey(name: 'reasoning_tokens') int? reasoningTokens,
    @JsonKey(name: 'mcp_tool_audit')
    @Default([])
    List<MCPToolAuditDTO> mcpToolAudit,
    @JsonKey(name: 'has_warning') @Default(false) bool hasWarning,
    @JsonKey(name: 'synthesized_markdown') String? synthesizedMarkdown,
    @JsonKey(name: 'visible_metadata')
    @Default([])
    List<String> visibleMetadata,
    @JsonKey(name: 'grouped_extensions')
    @Default({})
    Map<String, List<dynamic>> groupedExtensions,
    @JsonKey(name: 'penalties_applied')
    @Default([])
    List<String> penaltiesApplied,
  }) = _ReportDataDTO;

  factory ReportDataDTO.fromJson(Map<String, dynamic> json) =>
      _$ReportDataDTOFromJson(json);

  /// Parses a heavy raw JSON string into a ReportDataDTO entirely off the Main Thread.
  /// This is mandatory for large RAG synthesis payloads to prevent Main Thread Jank.
  static Future<ReportDataDTO> parseInBackground(String rawJson) async {
    return Isolate.run(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ReportDataDTO.fromJson(decoded);
    });
  }
}
