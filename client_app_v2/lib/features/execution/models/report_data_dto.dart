// ignore_for_file: invalid_annotation_target
import 'package:client_app/core/utils/safe_isolate.dart';
import 'dart:convert';

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

part 'report_data_dto.freezed.dart';
part 'report_data_dto.g.dart';

/// Polymorphic SDUI Block DTO enforcing the Tripartite Rendering Boundary
@Freezed(unionKey: 'block_type')
sealed class SduiBlockDTO with _$SduiBlockDTO {
  const SduiBlockDTO._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('paragraph')
  const factory SduiBlockDTO.paragraph({
    required String text,
    @Default([]) List<int> citations,
    @Default([]) List<String> exactQuotes,
  }) = SduiParagraphBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('bullet_list')
  const factory SduiBlockDTO.bulletList({
    required List<SduiBulletListItemDTO> items,
  }) = SduiBulletListBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('alert_box')
  const factory SduiBlockDTO.alertBox({
    required String text,
    required String severity,
    @Default([]) List<int> citations,
    @Default([]) List<String> exactQuotes,
  }) = SduiAlertBoxBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('hero_insight')
  const factory SduiBlockDTO.heroInsight({
    required String text,
    @Default([]) List<int> citations,
    @Default([]) List<String> exactQuotes,
  }) = SduiHeroInsightBlock;

  @JsonSerializable(disallowUnrecognizedKeys: true)
  @FreezedUnionValue('markdown')
  const factory SduiBlockDTO.markdown({required String text}) =
      SduiMarkdownBlock;

  factory SduiBlockDTO.fromJson(Map<String, dynamic> json) =>
      _$SduiBlockDTOFromJson(json);
}

/// Strictly typed DTO for individual bullet list items from the backend
@Freezed(equal: false)
abstract class SduiBulletListItemDTO with _$SduiBulletListItemDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory SduiBulletListItemDTO({
    required String text,
    @Default([]) List<int> citations,
    @Default([]) List<String> exactQuotes,
  }) = _SduiBulletListItemDTO;

  factory SduiBulletListItemDTO.fromJson(Map<String, dynamic> json) =>
      _$SduiBulletListItemDTOFromJson(json);
}

/// Strictly typed DTO representing a single layout block dynamically defining how to render axes.
/// Note: Added synthesis field to prevent checked JSON parsing errors.
@Freezed(equal: false)
abstract class ReportLayoutDTO with _$ReportLayoutDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportLayoutDTO({
    @JsonKey(name: 'preset_view') required PresetView presetView,
    @JsonKey(name: 'matrix_type') String? matrixType,
    I18nText? title,
    I18nText? description,
    @Default([]) List<MatrixScorecardRowDto> axes,
    @Default(['label', 'score', 'distribution', 'row_explanation'])
    @JsonKey(name: 'visible_columns')
    List<String> visibleColumns,
    @JsonKey(name: 'text_delivery_mode') required String textDeliveryMode,
    Map<String, dynamic>? synthesis,
    @JsonKey(name: 'synthesis_blocks')
    @Default([])
    List<SduiBlockDTO> synthesisBlocks,
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
    @JsonKey(name: 'claim_text') String? claimText,
    required String query,
    @Default('') String reasoning,
    @JsonKey(name: 'knowledge_gap') String? knowledgeGap,
    @JsonKey(name: 'search_rationale') String? searchRationale,
    @JsonKey(name: 'response_summary') @Default('') String responseSummary,
    @JsonKey(name: 'source_urls') @Default([]) List<String> sourceUrls,
    @JsonKey(name: 'impacted_axis_names')
    @Default([])
    List<String> impactedAxisNames,
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
    @JsonKey(name: 'local_time_str') String? localTimeStr,
    @JsonKey(name: 'org_name') String? orgName,
    @JsonKey(name: 'user_name') String? userName,
    @JsonKey(name: 'scoring_engine_name') String? scoringEngineName,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'custom_preface_md') String? customPrefaceMd,
    @JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,
    @JsonKey(name: 'cost_estimate') double? costEstimate,
    @JsonKey(name: 'total_tokens') int? totalTokens,
    @JsonKey(name: 'prompt_tokens') int? promptTokens,
    @JsonKey(name: 'completion_tokens') int? completionTokens,
    @JsonKey(name: 'reasoning_tokens') int? reasoningTokens,
    @JsonKey(name: 'mcp_tool_audit')
    @Default([])
    List<MCPToolAuditDTO> mcpToolAudit,
    @JsonKey(name: 'has_warning') @Default(false) bool hasWarning,
    @JsonKey(name: 'content_blocks')
    @Default([])
    List<SduiBlockDTO> contentBlocks,
    @JsonKey(name: 'visible_metadata')
    @Default([])
    List<String> visibleMetadata,
    @JsonKey(name: 'grouped_extensions')
    @Default({})
    Map<String, List<dynamic>> groupedExtensions,
    @JsonKey(name: 'penalties_applied')
    @Default([])
    List<String> penaltiesApplied,
    @JsonKey(name: 'evaluative_matrices')
    @Default([])
    List<MatrixScorecardRowDto> evaluativeMatrices,
    @JsonKey(name: 'informational_matrices')
    @Default([])
    List<MatrixScorecardRowDto> informationalMatrices,
    @JsonKey(name: 'matrix_visible_columns')
    @Default(['label', 'score', 'distribution', 'row_explanation'])
    List<String> matrixVisibleColumns,
  }) = _ReportDataDTO;

  factory ReportDataDTO.fromJson(Map<String, dynamic> json) =>
      _$ReportDataDTOFromJson(json);

  /// Parses a heavy raw JSON string into a ReportDataDTO entirely off the Main Thread.
  /// This is mandatory for large RAG synthesis payloads to prevent Main Thread Jank.
  static Future<ReportDataDTO> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ReportDataDTO.fromJson(decoded);
    });
  }
}
