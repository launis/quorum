// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:client_app/shared/models/i18n_text.dart';

part 'scorecard_dto.freezed.dart';
part 'scorecard_dto.g.dart';

@Freezed(equal: false)
abstract class ScorecardResponseDto with _$ScorecardResponseDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ScorecardResponseDto({
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'global_average') double? globalAverage,
    @JsonKey(name: 'evaluative_matrices')
    @Default([])
    List<MatrixScorecardRowDto> evaluativeMatrices,
    @JsonKey(name: 'informational_matrices')
    @Default([])
    List<MatrixScorecardRowDto> informationalMatrices,
  }) = _ScorecardResponseDto;

  factory ScorecardResponseDto.fromJson(Map<String, dynamic> json) =>
      _$ScorecardResponseDtoFromJson(json);
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
    @JsonKey(name: 'scale_min') double? scaleMin,
    @JsonKey(name: 'scale_max') double? scaleMax,
    @JsonKey(name: 'normalized_score') double? normalizedScore,
    @JsonKey(name: 'true_atoms') int? trueAtoms,
    @JsonKey(name: 'total_atoms') int? totalAtoms,
    @JsonKey(name: 'row_explanation') @Default('') String rowExplanation,

    @JsonKey(name: 'cited_source_id') String? citedSourceId,
    @JsonKey(name: 'cited_text_quote') String? citedTextQuote,
    @JsonKey(name: 'cited_web_citation') String? citedWebCitation,

    @JsonKey(name: 'evidence_type') EvidenceType? evidenceType,
    @JsonKey(name: 'tda_state') TDAState? tdaState,

    // Epic 6: XAI Output Extensions
    String? coaching,
    double? confidence,
    String? falsification,
    @JsonKey(name: 'missing_context') String? missingContext,
    @JsonKey(name: 'risk_flag') bool? riskFlag,
    @JsonKey(name: 'remediation_steps') String? remediationSteps,
    @JsonKey(name: 'emotional_sentiment') String? emotionalSentiment,
    @JsonKey(name: 'theory_link') String? theoryLink,

    @JsonKey(name: 'level_breakdown') Map<String, String>? levelBreakdown,
    @JsonKey(name: 'level_names') Map<String, String>? levelNames,

    @JsonKey(name: 'ui_boundary_labels') Map<String, String>? uiBoundaryLabels,

    @JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,

    @JsonKey(name: 'is_evaluative') @Default(true) bool isEvaluative,
    @JsonKey(name: 'contextual_override') bool? contextualOverride,
    @JsonKey(name: 'semantic_reasoning') String? semanticReasoning,

    // Epic 88: Unified Forensic Traceability
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

  // Epic 88 Phase 3: Smart Getter for UI grouping by level
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
abstract class ScorecardAtomDto with _$ScorecardAtomDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ScorecardAtomDto({
    @JsonKey(name: 'atom_id') required String atomId,
    required int level,
    @JsonKey(name: 'level_name') required String levelName,
    @JsonKey(name: 'claim_label') required String claimLabel,
    @JsonKey(name: 'extracted_facts')
    required Map<String, String?> extractedFacts,
    @JsonKey(name: 'exact_quotes') required List<String> exactQuotes,
    @JsonKey(name: 'internal_logic_en')
    required ReasoningStepDto internalLogicEn,
    String? status,
    @JsonKey(name: 'semantic_reasoning') required String semanticReasoning,
    @JsonKey(name: 'contextual_override') required bool contextualOverride,
    @JsonKey(name: 'structural_location') required String structuralLocation,
  }) = _ScorecardAtomDto;

  factory ScorecardAtomDto.fromJson(Map<String, dynamic> json) =>
      _$ScorecardAtomDtoFromJson(json);
}
