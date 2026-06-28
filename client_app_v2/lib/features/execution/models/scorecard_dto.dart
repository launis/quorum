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
    @JsonKey(name: 'quotes_list') List<String>? quotesList,
    @JsonKey(name: 'row_forensics') RowForensicsDto? forensics,

    @JsonKey(name: 'used_evidence_ids')
    @Default([])
    List<String> usedEvidenceIds,
  }) = _MatrixScorecardRowDto;

  factory MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) =>
      _$MatrixScorecardRowDtoFromJson(json);
}

@Freezed(equal: false)
abstract class EvidenceQuoteDto with _$EvidenceQuoteDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory EvidenceQuoteDto({
    required String id,
    required String text,
    @JsonKey(name: 'source_reference') String? sourceReference,
    @JsonKey(name: 'user_rejected') @Default(false) bool userRejected,
    @JsonKey(name: 'rejection_reason') String? rejectionReason,
    @JsonKey(name: 'is_mcp_verified') @Default(false) bool isMcpVerified,
    @JsonKey(name: 'used_evidence_ids')
    @Default([])
    List<String> usedEvidenceIds,
  }) = _EvidenceQuoteDto;

  factory EvidenceQuoteDto.fromJson(Map<String, dynamic> json) =>
      _$EvidenceQuoteDtoFromJson(json);
}

@Freezed(equal: false)
abstract class LevelQuotesDto with _$LevelQuotesDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory LevelQuotesDto({
    required int level,
    @JsonKey(name: 'level_name') required String levelName,
    @Default([]) List<EvidenceQuoteDto> quotes,
  }) = _LevelQuotesDto;

  factory LevelQuotesDto.fromJson(Map<String, dynamic> json) =>
      _$LevelQuotesDtoFromJson(json);
}

@Freezed(equal: false)
abstract class RowForensicsDto with _$RowForensicsDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory RowForensicsDto({
    @JsonKey(name: 'level_quotes')
    @Default([])
    List<LevelQuotesDto> levelQuotes,
    @JsonKey(name: 'all_evidence_rejected')
    @Default(false)
    bool allEvidenceRejected,
  }) = _RowForensicsDto;

  factory RowForensicsDto.fromJson(Map<String, dynamic> json) =>
      _$RowForensicsDtoFromJson(json);
}
