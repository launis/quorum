// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/tda_state.dart';

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
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixScorecardRowDto({
    @JsonKey(name: 'block_id') required String blockId,
    required String name,
    @JsonKey(name: 'label_fi') required String labelFi,
    @JsonKey(name: 'label_en') required String labelEn,
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
  }) = _MatrixScorecardRowDto;

  factory MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) =>
      _$MatrixScorecardRowDtoFromJson(json);
}
