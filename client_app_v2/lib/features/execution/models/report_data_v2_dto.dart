// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'dart:convert';
import 'package:client_app/core/utils/safe_isolate.dart';

import 'matrix_scorecard_dto.dart';
import 'report_layout_dto.dart';
import 'atom_result_dto.dart';
import 'execution_metrics_dto.dart';

import 'hydrated_atom_dto.dart';
import '../../../shared/models/i18n_text.dart';
import '../../../shared/models/sdui_block_dto.dart';

part 'report_data_v2_dto.freezed.dart';
part 'report_data_v2_dto.g.dart';

@Freezed(equal: false)
abstract class ReportDataDto with _$ReportDataDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportDataDto({
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'scoring_strategy') String? scoringStrategy,
    @JsonKey(name: 'user_name') String? userName,
    @JsonKey(name: 'scoring_engine_name') String? scoringEngineName,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'local_time_str') String? localTimeStr,
    @JsonKey(name: 'custom_preface_md') String? customPrefaceMd,
    @JsonKey(name: 'profile_id') required String profileId,
    @JsonKey(name: 'profile_name') I18nText? profileName,
    @JsonKey(name: 'profile_description') I18nText? profileDescription,
    @JsonKey(name: 'available_profiles')
    @Default({})
    Map<String, I18nText> availableProfiles,
    @JsonKey(name: 'global_score') double? globalScore,
    @JsonKey(name: 'has_warning') @Default(false) bool hasWarning,
    @JsonKey(name: 'global_metrics') ExecutionMetricsDTO? globalMetrics,
    @JsonKey(name: 'inner_sdui_blocks')
    @Default([])
    List<SduiBlockDTO> innerSduiBlocks,
    @JsonKey(name: 'results') @Default([]) List<AtomResultDTO> results,
    @JsonKey(name: 'hydrated_references')
    @Default({})
    Map<String, HydratedAtomDTO> hydratedReferences,
    @JsonKey(name: 'visible_metadata')
    @Default([])
    List<String> visibleMetadata,
    @Default([]) List<ReportLayoutDto> layouts,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'org_name') String? orgName,
    @JsonKey(name: 'cost_estimate') double? costEstimate,
    @JsonKey(name: 'total_tokens') int? totalTokens,
    @JsonKey(name: 'prompt_tokens') int? promptTokens,
    @JsonKey(name: 'completion_tokens') int? completionTokens,
    @JsonKey(name: 'reasoning_tokens') int? reasoningTokens,
    @JsonKey(name: 'mcp_tool_audit')
    @Default([])
    List<McpAuditTraceDto> mcpToolAudit,
  }) = _ReportDataDto;

  factory ReportDataDto.fromJson(Map<String, dynamic> json) =>
      _$ReportDataDtoFromJson(json);

  /// Parses a heavy raw JSON string into a ReportDataDto entirely off the Main Thread.
  /// This prevents Main Thread Jank when handling large payloads.
  static Future<ReportDataDto> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ReportDataDto.fromJson(decoded);
    });
  }
}
