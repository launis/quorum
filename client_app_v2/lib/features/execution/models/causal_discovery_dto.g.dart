// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'causal_discovery_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CausalNodeDto _$CausalNodeDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_CausalNodeDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'node_id',
        'claim',
        'source_quote',
        'paragraph_ref',
        'status',
        'blame_parent_ids',
        'dependent_child_ids',
        'tda_score',
        'tda_level_key',
        'source_input_key',
      ],
    );
    final val = _CausalNodeDto(
      nodeId: $checkedConvert('node_id', (v) => v as String),
      claim: $checkedConvert('claim', (v) => v as String),
      sourceQuote: $checkedConvert('source_quote', (v) => v as String?),
      paragraphRef: $checkedConvert('paragraph_ref', (v) => v as String?),
      status: $checkedConvert(
        'status',
        (v) => $enumDecode(_$ExecutionStatusEnumMap, v),
      ),
      blameParentIds: $checkedConvert(
        'blame_parent_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      dependentChildIds: $checkedConvert(
        'dependent_child_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      tdaScore: $checkedConvert('tda_score', (v) => (v as num?)?.toDouble()),
      tdaLevelKey: $checkedConvert('tda_level_key', (v) => v as String?),
      sourceInputKey: $checkedConvert(
        'source_input_key',
        (v) => v as String? ?? null,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'nodeId': 'node_id',
    'sourceQuote': 'source_quote',
    'paragraphRef': 'paragraph_ref',
    'blameParentIds': 'blame_parent_ids',
    'dependentChildIds': 'dependent_child_ids',
    'tdaScore': 'tda_score',
    'tdaLevelKey': 'tda_level_key',
    'sourceInputKey': 'source_input_key',
  },
);

Map<String, dynamic> _$CausalNodeDtoToJson(_CausalNodeDto instance) =>
    <String, dynamic>{
      'node_id': instance.nodeId,
      'claim': instance.claim,
      'source_quote': instance.sourceQuote,
      'paragraph_ref': instance.paragraphRef,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
      'blame_parent_ids': instance.blameParentIds,
      'dependent_child_ids': instance.dependentChildIds,
      'tda_score': instance.tdaScore,
      'tda_level_key': instance.tdaLevelKey,
      'source_input_key': instance.sourceInputKey,
    };

const _$ExecutionStatusEnumMap = {
  ExecutionStatus.passed: 'PASSED',
  ExecutionStatus.failed: 'FAILED',
  ExecutionStatus.nA: 'N_A',
  ExecutionStatus.systemError: 'SYSTEM_ERROR',
  ExecutionStatus.blocked: 'BLOCKED',
  ExecutionStatus.pending: 'PENDING',
  ExecutionStatus.running: 'RUNNING',
  ExecutionStatus.queued: 'QUEUED',
};

_CausalEdgeDto _$CausalEdgeDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_CausalEdgeDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['source_id', 'target_id', 'reasoning'],
        );
        final val = _CausalEdgeDto(
          sourceId: $checkedConvert('source_id', (v) => v as String),
          targetId: $checkedConvert('target_id', (v) => v as String),
          reasoning: $checkedConvert('reasoning', (v) => v as String),
        );
        return val;
      },
      fieldKeyMap: const {'sourceId': 'source_id', 'targetId': 'target_id'},
    );

Map<String, dynamic> _$CausalEdgeDtoToJson(_CausalEdgeDto instance) =>
    <String, dynamic>{
      'source_id': instance.sourceId,
      'target_id': instance.targetId,
      'reasoning': instance.reasoning,
    };

_CausalRootCauseDiagnosisDto _$CausalRootCauseDiagnosisDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_CausalRootCauseDiagnosisDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'failing_node_id',
        'root_cause_parent_id',
        'paragraph_ref',
        'explanation',
        'penalty_points',
        'root_cause_type',
      ],
    );
    final val = _CausalRootCauseDiagnosisDto(
      failingNodeId: $checkedConvert('failing_node_id', (v) => v as String),
      rootCauseParentId: $checkedConvert(
        'root_cause_parent_id',
        (v) => v as String,
      ),
      paragraphRef: $checkedConvert('paragraph_ref', (v) => v as String),
      explanation: $checkedConvert('explanation', (v) => v as String),
      penaltyPoints: $checkedConvert(
        'penalty_points',
        (v) => (v as num).toDouble(),
      ),
      rootCauseType: $checkedConvert(
        'root_cause_type',
        (v) =>
            $enumDecodeNullable(_$CausalRootCauseTypeEnumMap, v) ??
            CausalRootCauseType.nodeFailure,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'failingNodeId': 'failing_node_id',
    'rootCauseParentId': 'root_cause_parent_id',
    'paragraphRef': 'paragraph_ref',
    'penaltyPoints': 'penalty_points',
    'rootCauseType': 'root_cause_type',
  },
);

Map<String, dynamic> _$CausalRootCauseDiagnosisDtoToJson(
  _CausalRootCauseDiagnosisDto instance,
) => <String, dynamic>{
  'failing_node_id': instance.failingNodeId,
  'root_cause_parent_id': instance.rootCauseParentId,
  'paragraph_ref': instance.paragraphRef,
  'explanation': instance.explanation,
  'penalty_points': instance.penaltyPoints,
  'root_cause_type': _$CausalRootCauseTypeEnumMap[instance.rootCauseType]!,
};

const _$CausalRootCauseTypeEnumMap = {
  CausalRootCauseType.nodeFailure: 'node_failure',
  CausalRootCauseType.warrantGroundingFailure: 'warrant_grounding_failure',
  CausalRootCauseType.preconditionMismatch: 'precondition_mismatch',
};

_AntiFluffAuditDto _$AntiFluffAuditDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_AntiFluffAuditDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'isolated_concept_count',
            'cycle_detected',
            'unsupported_claims_count',
            'logical_cohesion_score',
            'detected_hollow_terms',
          ],
        );
        final val = _AntiFluffAuditDto(
          isolatedConceptCount: $checkedConvert(
            'isolated_concept_count',
            (v) => (v as num).toInt(),
          ),
          cycleDetected: $checkedConvert('cycle_detected', (v) => v as bool),
          unsupportedClaimsCount: $checkedConvert(
            'unsupported_claims_count',
            (v) => (v as num).toInt(),
          ),
          logicalCohesionScore: $checkedConvert(
            'logical_cohesion_score',
            (v) => (v as num).toDouble(),
          ),
          detectedHollowTerms: $checkedConvert(
            'detected_hollow_terms',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const [],
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'isolatedConceptCount': 'isolated_concept_count',
        'cycleDetected': 'cycle_detected',
        'unsupportedClaimsCount': 'unsupported_claims_count',
        'logicalCohesionScore': 'logical_cohesion_score',
        'detectedHollowTerms': 'detected_hollow_terms',
      },
    );

Map<String, dynamic> _$AntiFluffAuditDtoToJson(_AntiFluffAuditDto instance) =>
    <String, dynamic>{
      'isolated_concept_count': instance.isolatedConceptCount,
      'cycle_detected': instance.cycleDetected,
      'unsupported_claims_count': instance.unsupportedClaimsCount,
      'logical_cohesion_score': instance.logicalCohesionScore,
      'detected_hollow_terms': instance.detectedHollowTerms,
    };

_PrescriptiveRemediationDto _$PrescriptiveRemediationDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_PrescriptiveRemediationDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'target_node_id',
        'required_action',
        'unlocks_node_ids',
        'potential_score_impact',
      ],
    );
    final val = _PrescriptiveRemediationDto(
      targetNodeId: $checkedConvert('target_node_id', (v) => v as String),
      requiredAction: $checkedConvert('required_action', (v) => v as String),
      unlocksNodeIds: $checkedConvert(
        'unlocks_node_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      potentialScoreImpact: $checkedConvert(
        'potential_score_impact',
        (v) => (v as num).toDouble(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'targetNodeId': 'target_node_id',
    'requiredAction': 'required_action',
    'unlocksNodeIds': 'unlocks_node_ids',
    'potentialScoreImpact': 'potential_score_impact',
  },
);

Map<String, dynamic> _$PrescriptiveRemediationDtoToJson(
  _PrescriptiveRemediationDto instance,
) => <String, dynamic>{
  'target_node_id': instance.targetNodeId,
  'required_action': instance.requiredAction,
  'unlocks_node_ids': instance.unlocksNodeIds,
  'potential_score_impact': instance.potentialScoreImpact,
};

_FairScoringBreakdownDto _$FairScoringBreakdownDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_FairScoringBreakdownDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'independent_error_count',
        'cascading_fault_count',
        'raw_penalty_points',
        'deduplicated_penalty_points',
        'dampened_savings_points',
      ],
    );
    final val = _FairScoringBreakdownDto(
      independentErrorCount: $checkedConvert(
        'independent_error_count',
        (v) => (v as num).toInt(),
      ),
      cascadingFaultCount: $checkedConvert(
        'cascading_fault_count',
        (v) => (v as num).toInt(),
      ),
      rawPenaltyPoints: $checkedConvert(
        'raw_penalty_points',
        (v) => (v as num).toDouble(),
      ),
      deduplicatedPenaltyPoints: $checkedConvert(
        'deduplicated_penalty_points',
        (v) => (v as num).toDouble(),
      ),
      dampenedSavingsPoints: $checkedConvert(
        'dampened_savings_points',
        (v) => (v as num).toDouble(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'independentErrorCount': 'independent_error_count',
    'cascadingFaultCount': 'cascading_fault_count',
    'rawPenaltyPoints': 'raw_penalty_points',
    'deduplicatedPenaltyPoints': 'deduplicated_penalty_points',
    'dampenedSavingsPoints': 'dampened_savings_points',
  },
);

Map<String, dynamic> _$FairScoringBreakdownDtoToJson(
  _FairScoringBreakdownDto instance,
) => <String, dynamic>{
  'independent_error_count': instance.independentErrorCount,
  'cascading_fault_count': instance.cascadingFaultCount,
  'raw_penalty_points': instance.rawPenaltyPoints,
  'deduplicated_penalty_points': instance.deduplicatedPenaltyPoints,
  'dampened_savings_points': instance.dampenedSavingsPoints,
};
