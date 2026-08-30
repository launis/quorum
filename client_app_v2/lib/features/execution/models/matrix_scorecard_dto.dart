// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';

part 'matrix_scorecard_dto.freezed.dart';
part 'matrix_scorecard_dto.g.dart';

@Freezed(equal: false)
abstract class ReasoningStepDto with _$ReasoningStepDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReasoningStepDto({
    @JsonKey(name: 'step_1_identify_premise')
    required String step1IdentifyPremise,
    @JsonKey(name: 'step_2_scan_source') required String step2ScanSource,
    @JsonKey(name: 'step_3_evaluate_anti_patterns')
    required String step3EvaluateAntiPatterns,
    @JsonKey(name: 'step_4_final_conclusion')
    required String step4FinalConclusion,
  }) = _ReasoningStepDto;

  factory ReasoningStepDto.fromJson(Map<String, dynamic> json) =>
      _$ReasoningStepDtoFromJson(json);
}

@Freezed(equal: false)
abstract class QuoteEvidenceDto with _$QuoteEvidenceDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory QuoteEvidenceDto({
    required String quote,
    @JsonKey(name: 'verified_source_ids')
    @Default([])
    List<String> verifiedSourceIds,
    @JsonKey(name: 'unverified_aliases')
    @Default([])
    List<String> unverifiedAliases,
    @JsonKey(name: 'is_verified') @Default(false) bool isVerified,
  }) = _QuoteEvidenceDto;

  factory QuoteEvidenceDto.fromJson(Map<String, dynamic> json) =>
      _$QuoteEvidenceDtoFromJson(json);
}

@Freezed(equal: false)
abstract class HumanOverrideDto with _$HumanOverrideDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory HumanOverrideDto({
    @JsonKey(name: 'new_status') required ExecutionStatus newStatus,
    required String reason,
    @JsonKey(name: 'evidence_quotes')
    required List<QuoteEvidenceDto> evidenceQuotes,
    @JsonKey(name: 'overridden_by') required String overriddenBy,
    @JsonKey(name: 'overridden_at') required DateTime overriddenAt,
  }) = _HumanOverrideDto;

  factory HumanOverrideDto.fromJson(Map<String, dynamic> json) =>
      _$HumanOverrideDtoFromJson(json);
}

@Freezed(equal: false)
abstract class ScorecardAtomDto with _$ScorecardAtomDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ScorecardAtomDto({
    @JsonKey(name: 'atom_id') required String atomId,
    required int level,
    @JsonKey(name: 'level_name') required String levelName,
    @JsonKey(name: 'claim_label') required String claimLabel,
    @JsonKey(name: 'extracted_facts')
    required Map<String, String?> extractedFacts,
    @JsonKey(name: 'exact_quotes') required List<QuoteEvidenceDto> exactQuotes,
    @JsonKey(name: 'internal_logic_en')
    required ReasoningStepDto internalLogicEn,
    ExecutionStatus? status,
    @JsonKey(name: 'semantic_reasoning') required String semanticReasoning,
    @JsonKey(name: 'contextual_override') required bool contextualOverride,
    @JsonKey(name: 'structural_location') String? structuralLocation,
    @JsonKey(name: 'human_override') HumanOverrideDto? humanOverride,
    @JsonKey(name: 'chart_display_label') required String chartDisplayLabel,
    @JsonKey(name: 'visual_intent') required VisualIntent visualIntent,
  }) = _ScorecardAtomDto;

  factory ScorecardAtomDto.fromJson(Map<String, dynamic> json) =>
      _$ScorecardAtomDtoFromJson(json);
}

@Freezed(equal: false)
abstract class McpAuditTraceDto with _$McpAuditTraceDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory McpAuditTraceDto({
    String? id,
    @JsonKey(name: 'tool_id') required String toolId,
    @JsonKey(name: 'step_name') required String stepName,
    @JsonKey(name: 'claim_text') String? claimText,
    required String query,
    @JsonKey(name: 'knowledge_gap') @Default('') String knowledgeGap,
    @JsonKey(name: 'search_rationale') @Default('') String searchRationale,
    @Default('') String reasoning,
    @JsonKey(name: 'response_summary') @Default('') String responseSummary,
    @JsonKey(name: 'source_urls') @Default([]) List<String> sourceUrls,
    @JsonKey(name: 'impacted_axis_names')
    @Default([])
    List<String> impactedAxisNames,
    String? timestamp,
    @JsonKey(name: 'duration_ms') @Default(0) int durationMs,
  }) = _McpAuditTraceDto;

  factory McpAuditTraceDto.fromJson(Map<String, dynamic> json) =>
      _$McpAuditTraceDtoFromJson(json);
}

@Freezed(equal: false)
abstract class MatrixScorecardRowDto with _$MatrixScorecardRowDto {
  const MatrixScorecardRowDto._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixScorecardRowDto({
    @JsonKey(name: 'block_id') required String blockId,
    required String name,
    @JsonKey(name: 'label_i18n') required I18nText labelI18n,
    String? description,
    double? score,
    @JsonKey(name: 'score_display_label') String? scoreDisplayLabel,
    @JsonKey(name: 'scale_min') double? scaleMin,
    @JsonKey(name: 'scale_max') double? scaleMax,
    @JsonKey(name: 'normalized_score') double? normalizedScore,
    @JsonKey(name: 'true_atoms') int? trueAtoms,
    @JsonKey(name: 'total_atoms') int? totalAtoms,
    @JsonKey(name: 'row_explanation') @Default('') String rowExplanation,

    @JsonKey(name: 'cited_source_id') String? citedSourceId,
    @JsonKey(name: 'cited_text_quote') String? citedTextQuote,
    @JsonKey(name: 'cited_web_citation') String? citedWebCitation,
    @JsonKey(name: 'cited_source_title') String? citedSourceTitle,
    @JsonKey(name: 'cited_source_url') String? citedSourceUrl,

    @JsonKey(name: 'context_target') String? contextTarget,
    @JsonKey(name: 'context_target_label') I18nText? contextTargetLabel,
    @JsonKey(name: 'remediation_steps') String? remediationSteps,
    @JsonKey(name: 'coaching') String? coaching,
    @JsonKey(name: 'falsification') String? falsification,

    @JsonKey(name: 'evidence_type') EvidenceType? evidenceType,
    @JsonKey(name: 'tda_state') TDAState? tdaState,

    double? confidence,
    @JsonKey(name: 'inner_sdui_blocks')
    @Default([])
    List<SduiBlockDTO> innerSduiBlocks,

    @JsonKey(name: 'level_breakdown') Map<String, String>? levelBreakdown,
    @JsonKey(name: 'level_names') Map<String, String>? levelNames,

    @JsonKey(name: 'ui_boundary_labels') Map<String, String>? uiBoundaryLabels,

    @JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,

    @JsonKey(name: 'is_evaluative') @Default(true) bool isEvaluative,
    @JsonKey(name: 'allow_contextual_override')
    @Default(false)
    bool allowContextualOverride,
    @JsonKey(name: 'contextual_override') bool? contextualOverride,
    @JsonKey(name: 'semantic_reasoning') String? semanticReasoning,

    @JsonKey(name: 'evaluated_atoms')
    @Default([])
    List<ScorecardAtomDto> evaluatedAtoms,
    @JsonKey(name: 'clustered_row_sources')
    @Default([])
    List<McpAuditTraceDto> clusteredRowSources,

    @JsonKey(name: 'used_evidence_ids')
    @Default([])
    List<String> usedEvidenceIds,
  }) = _MatrixScorecardRowDto;

  factory MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) =>
      _$MatrixScorecardRowDtoFromJson(json);

  // Smart Getter for UI grouping by level
  Map<int, List<ScorecardAtomDto>> get atomsByLevel {
    final Map<int, List<ScorecardAtomDto>> grouped = {};
    for (final atom in evaluatedAtoms) {
      if (!grouped.containsKey(atom.level)) {
        grouped[atom.level] = [];
      }
      grouped[atom.level]!.add(atom);
    }
    return grouped;
  }
}
