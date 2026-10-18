import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';

part 'causal_discovery_dto.freezed.dart';
part 'causal_discovery_dto.g.dart';

@Freezed(equal: false)
abstract class CausalNodeDto with _$CausalNodeDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory CausalNodeDto({
    @JsonKey(name: 'node_id') required String nodeId,
    required String claim,
    @JsonKey(name: 'source_quotes') List<String>? sourceQuotes,
    @JsonKey(name: 'paragraph_ref') String? paragraphRef,
    required ExecutionStatus status,
    @JsonKey(name: 'blame_parent_ids') @Default([]) List<String> blameParentIds,
    @JsonKey(name: 'dependent_child_ids')
    @Default([])
    List<String> dependentChildIds,
    @JsonKey(name: 'tda_score') double? tdaScore,
    @JsonKey(name: 'tda_level_key') String? tdaLevelKey,
    @JsonKey(name: 'source_input_key') @Default(null) String? sourceInputKey,
  }) = _CausalNodeDto;

  factory CausalNodeDto.fromJson(Map<String, dynamic> json) =>
      _$CausalNodeDtoFromJson(json);
}

@Freezed(equal: false)
abstract class CausalEdgeDto with _$CausalEdgeDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory CausalEdgeDto({
    @JsonKey(name: 'source_id') required String sourceId,
    @JsonKey(name: 'target_id') required String targetId,
    required String reasoning,
  }) = _CausalEdgeDto;

  factory CausalEdgeDto.fromJson(Map<String, dynamic> json) =>
      _$CausalEdgeDtoFromJson(json);
}

@Freezed(equal: false)
abstract class CausalRootCauseDiagnosisDto with _$CausalRootCauseDiagnosisDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory CausalRootCauseDiagnosisDto({
    @JsonKey(name: 'failing_node_id') required String failingNodeId,
    @JsonKey(name: 'root_cause_parent_id') required String rootCauseParentId,
    @JsonKey(name: 'paragraph_ref') required String paragraphRef,
    required String explanation,
    @JsonKey(name: 'penalty_points') required double penaltyPoints,
    @JsonKey(name: 'root_cause_type')
    @Default(CausalRootCauseType.nodeFailure)
    CausalRootCauseType rootCauseType,
  }) = _CausalRootCauseDiagnosisDto;

  factory CausalRootCauseDiagnosisDto.fromJson(Map<String, dynamic> json) =>
      _$CausalRootCauseDiagnosisDtoFromJson(json);
}

@Freezed(equal: false)
abstract class AntiFluffAuditDto with _$AntiFluffAuditDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory AntiFluffAuditDto({
    @JsonKey(name: 'isolated_concept_count') required int isolatedConceptCount,
    @JsonKey(name: 'cycle_detected') required bool cycleDetected,
    @JsonKey(name: 'unsupported_claims_count')
    required int unsupportedClaimsCount,
    @JsonKey(name: 'logical_cohesion_score')
    required double logicalCohesionScore,
    @JsonKey(name: 'detected_hollow_terms')
    @Default([])
    List<String> detectedHollowTerms,
  }) = _AntiFluffAuditDto;

  factory AntiFluffAuditDto.fromJson(Map<String, dynamic> json) =>
      _$AntiFluffAuditDtoFromJson(json);
}

@Freezed(equal: false)
abstract class PrescriptiveRemediationDto with _$PrescriptiveRemediationDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory PrescriptiveRemediationDto({
    @JsonKey(name: 'target_node_id') required String targetNodeId,
    @JsonKey(name: 'required_action') required String requiredAction,
    @JsonKey(name: 'unlocks_node_ids') @Default([]) List<String> unlocksNodeIds,
    @JsonKey(name: 'potential_score_impact')
    required double potentialScoreImpact,
  }) = _PrescriptiveRemediationDto;

  factory PrescriptiveRemediationDto.fromJson(Map<String, dynamic> json) =>
      _$PrescriptiveRemediationDtoFromJson(json);
}

@Freezed(equal: false)
abstract class FairScoringBreakdownDto with _$FairScoringBreakdownDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory FairScoringBreakdownDto({
    @JsonKey(name: 'independent_error_count')
    required int independentErrorCount,
    @JsonKey(name: 'cascading_fault_count') required int cascadingFaultCount,
    @JsonKey(name: 'raw_penalty_points') required double rawPenaltyPoints,
    @JsonKey(name: 'deduplicated_penalty_points')
    required double deduplicatedPenaltyPoints,
    @JsonKey(name: 'dampened_savings_points')
    required double dampenedSavingsPoints,
  }) = _FairScoringBreakdownDto;

  factory FairScoringBreakdownDto.fromJson(Map<String, dynamic> json) =>
      _$FairScoringBreakdownDtoFromJson(json);
}
