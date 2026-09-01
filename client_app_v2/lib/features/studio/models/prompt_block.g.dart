// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prompt_block.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TheoryGrounding _$TheoryGroundingFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_TheoryGrounding',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['source_url', 'citation_reference'],
        );
        final val = _TheoryGrounding(
          sourceUrl: $checkedConvert('source_url', (v) => v as String),
          citationReference: $checkedConvert(
            'citation_reference',
            (v) => v as String?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'sourceUrl': 'source_url',
        'citationReference': 'citation_reference',
      },
    );

Map<String, dynamic> _$TheoryGroundingToJson(_TheoryGrounding instance) =>
    <String, dynamic>{
      'source_url': instance.sourceUrl,
      'citation_reference': instance.citationReference,
    };

_AcceptanceCriterion _$AcceptanceCriterionFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_AcceptanceCriterion',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['instruction', 'requires_contextual_override'],
        );
        final val = _AcceptanceCriterion(
          instruction: $checkedConvert('instruction', (v) => v as String),
          requiresContextualOverride: $checkedConvert(
            'requires_contextual_override',
            (v) => v as bool? ?? false,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'requiresContextualOverride': 'requires_contextual_override',
      },
    );

Map<String, dynamic> _$AcceptanceCriterionToJson(
  _AcceptanceCriterion instance,
) => <String, dynamic>{
  'instruction': instance.instruction,
  'requires_contextual_override': instance.requiresContextualOverride,
};

_AntiPattern _$AntiPatternFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_AntiPattern',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['pattern', 'allows_contextual_excuse'],
    );
    final val = _AntiPattern(
      pattern: $checkedConvert('pattern', (v) => v as String),
      allowsContextualExcuse: $checkedConvert(
        'allows_contextual_excuse',
        (v) => v as bool? ?? false,
      ),
    );
    return val;
  },
  fieldKeyMap: const {'allowsContextualExcuse': 'allows_contextual_excuse'},
);

Map<String, dynamic> _$AntiPatternToJson(_AntiPattern instance) =>
    <String, dynamic>{
      'pattern': instance.pattern,
      'allows_contextual_excuse': instance.allowsContextualExcuse,
    };

_CausalEdgeDTO _$CausalEdgeDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_CausalEdgeDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'edge_reasoning',
            'tda_id',
            'source_id',
            'expected_status',
          ],
        );
        final val = _CausalEdgeDTO(
          edgeReasoning: $checkedConvert('edge_reasoning', (v) => v as String),
          tdaId: $checkedConvert('tda_id', (v) => v as String),
          sourceId: $checkedConvert('source_id', (v) => v as String),
          expectedStatus: $checkedConvert(
            'expected_status',
            (v) =>
                $enumDecodeNullable(_$ExecutionStatusEnumMap, v) ??
                ExecutionStatus.passed,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'edgeReasoning': 'edge_reasoning',
        'tdaId': 'tda_id',
        'sourceId': 'source_id',
        'expectedStatus': 'expected_status',
      },
    );

Map<String, dynamic> _$CausalEdgeDTOToJson(_CausalEdgeDTO instance) =>
    <String, dynamic>{
      'edge_reasoning': instance.edgeReasoning,
      'tda_id': instance.tdaId,
      'source_id': instance.sourceId,
      'expected_status': _$ExecutionStatusEnumMap[instance.expectedStatus]!,
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

_TDAAssertion _$TDAAssertionFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_TDAAssertion',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'tda_id',
        'concept_description',
        'acceptance_criteria',
        'anti_patterns',
        'contrastive_example',
        'syntactic_anchors',
        'enforce_pre_flight',
        'depends_on',
        'inverse_evidence',
        'aggregation_mode',
        'evaluation_track',
        'facts_to_find',
        'logical_expression',
        'high_entropy',
        'anchor_target',
        'bounding_box_scope',
        'extraction_rule',
      ],
    );
    final val = _TDAAssertion(
      tdaId: $checkedConvert('tda_id', (v) => v as String),
      conceptDescription: $checkedConvert(
        'concept_description',
        (v) => v as String,
      ),
      acceptanceCriteria: $checkedConvert(
        'acceptance_criteria',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      AcceptanceCriterion.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      antiPatterns: $checkedConvert(
        'anti_patterns',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => AntiPattern.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      contrastiveExample: $checkedConvert(
        'contrastive_example',
        (v) => v as String?,
      ),
      syntacticAnchors: $checkedConvert(
        'syntactic_anchors',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      enforcePreFlight: $checkedConvert(
        'enforce_pre_flight',
        (v) => v as bool? ?? false,
      ),
      dependsOn: $checkedConvert(
        'depends_on',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => CausalEdgeDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      inverseEvidence: $checkedConvert('inverse_evidence', (v) => v as bool),
      aggregationMode: $checkedConvert(
        'aggregation_mode',
        (v) => $enumDecode(_$AggregationModeEnumMap, v),
      ),
      evaluationTrack: $checkedConvert(
        'evaluation_track',
        (v) =>
            $enumDecodeNullable(_$EvaluationTrackEnumMap, v) ??
            EvaluationTrack.cognitiveJudgement,
      ),
      factsToFind: $checkedConvert(
        'facts_to_find',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      logicalExpression: $checkedConvert(
        'logical_expression',
        (v) => v as String?,
      ),
      highEntropy: $checkedConvert('high_entropy', (v) => v as bool? ?? false),
      anchorTarget: $checkedConvert('anchor_target', (v) => v as String?),
      boundingBoxScope: $checkedConvert(
        'bounding_box_scope',
        (v) => v as String? ?? 'paragraph',
      ),
      extractionRule: $checkedConvert('extraction_rule', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'tdaId': 'tda_id',
    'conceptDescription': 'concept_description',
    'acceptanceCriteria': 'acceptance_criteria',
    'antiPatterns': 'anti_patterns',
    'contrastiveExample': 'contrastive_example',
    'syntacticAnchors': 'syntactic_anchors',
    'enforcePreFlight': 'enforce_pre_flight',
    'dependsOn': 'depends_on',
    'inverseEvidence': 'inverse_evidence',
    'aggregationMode': 'aggregation_mode',
    'evaluationTrack': 'evaluation_track',
    'factsToFind': 'facts_to_find',
    'logicalExpression': 'logical_expression',
    'highEntropy': 'high_entropy',
    'anchorTarget': 'anchor_target',
    'boundingBoxScope': 'bounding_box_scope',
    'extractionRule': 'extraction_rule',
  },
);

Map<String, dynamic> _$TDAAssertionToJson(_TDAAssertion instance) =>
    <String, dynamic>{
      'tda_id': instance.tdaId,
      'concept_description': instance.conceptDescription,
      'acceptance_criteria': instance.acceptanceCriteria
          .map((e) => e.toJson())
          .toList(),
      'anti_patterns': instance.antiPatterns.map((e) => e.toJson()).toList(),
      'contrastive_example': instance.contrastiveExample,
      'syntactic_anchors': instance.syntacticAnchors,
      'enforce_pre_flight': instance.enforcePreFlight,
      'depends_on': instance.dependsOn.map((e) => e.toJson()).toList(),
      'inverse_evidence': instance.inverseEvidence,
      'aggregation_mode': _$AggregationModeEnumMap[instance.aggregationMode]!,
      'evaluation_track': _$EvaluationTrackEnumMap[instance.evaluationTrack]!,
      'facts_to_find': instance.factsToFind,
      'logical_expression': instance.logicalExpression,
      'high_entropy': instance.highEntropy,
      'anchor_target': instance.anchorTarget,
      'bounding_box_scope': instance.boundingBoxScope,
      'extraction_rule': instance.extractionRule,
    };

const _$AggregationModeEnumMap = {
  AggregationMode.exists: 'EXISTS',
  AggregationMode.allMustComply: 'ALL_MUST_COMPLY',
};

const _$EvaluationTrackEnumMap = {
  EvaluationTrack.extractiveSensor: 'EXTRACTIVE_SENSOR',
  EvaluationTrack.cognitiveJudgement: 'COGNITIVE_JUDGEMENT',
};

_MatrixClaim _$MatrixClaimFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_MatrixClaim', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['label', 'tda_assertions']);
      final val = _MatrixClaim(
        label: $checkedConvert(
          'label',
          (v) => I18nText.fromJson(v as Map<String, dynamic>),
        ),
        tdaAssertions: $checkedConvert(
          'tda_assertions',
          (v) =>
              (v as List<dynamic>?)
                  ?.map((e) => TDAAssertion.fromJson(e as Map<String, dynamic>))
                  .toList() ??
              const [],
        ),
      );
      return val;
    }, fieldKeyMap: const {'tdaAssertions': 'tda_assertions'});

Map<String, dynamic> _$MatrixClaimToJson(_MatrixClaim instance) =>
    <String, dynamic>{
      'label': instance.label.toJson(),
      'tda_assertions': instance.tdaAssertions.map((e) => e.toJson()).toList(),
    };

_MatrixRow _$MatrixRowFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_MatrixRow', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['label', 'ai_description']);
      final val = _MatrixRow(
        label: $checkedConvert(
          'label',
          (v) => I18nText.fromJson(v as Map<String, dynamic>),
        ),
        aiDescription: $checkedConvert('ai_description', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'aiDescription': 'ai_description'});

Map<String, dynamic> _$MatrixRowToJson(_MatrixRow instance) =>
    <String, dynamic>{
      'label': instance.label.toJson(),
      'ai_description': instance.aiDescription,
    };

_MatrixScale _$MatrixScaleFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_MatrixScale', json, ($checkedConvert) {
      $checkKeys(
        json,
        allowedKeys: const ['score', 'name', 'ai_label', 'claims'],
      );
      final val = _MatrixScale(
        score: $checkedConvert('score', (v) => (v as num).toInt()),
        name: $checkedConvert(
          'name',
          (v) =>
              v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
        ),
        aiLabel: $checkedConvert('ai_label', (v) => v as String),
        claims: $checkedConvert(
          'claims',
          (v) => (v as List<dynamic>)
              .map((e) => MatrixClaim.fromJson(e as Map<String, dynamic>))
              .toList(),
        ),
      );
      return val;
    }, fieldKeyMap: const {'aiLabel': 'ai_label'});

Map<String, dynamic> _$MatrixScaleToJson(_MatrixScale instance) =>
    <String, dynamic>{
      'score': instance.score,
      'name': instance.name?.toJson(),
      'ai_label': instance.aiLabel,
      'claims': instance.claims.map((e) => e.toJson()).toList(),
    };

MatrixPromptBlock _$MatrixPromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'MatrixPromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'ai_description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'allow_contextual_override',
        'is_lightweight_protocol',
        'scales',
        'rows',
        'columns',
        'computed_min',
        'computed_max',
        'category_id',
      ],
    );
    final val = MatrixPromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      aiDescription: $checkedConvert('ai_description', (v) => v as String?),
      isEvaluative: $checkedConvert('is_evaluative', (v) => v as bool? ?? true),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.floatType,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      allowContextualOverride: $checkedConvert(
        'allow_contextual_override',
        (v) => v as bool? ?? false,
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      scales: $checkedConvert(
        'scales',
        (v) => (v as List<dynamic>)
            .map((e) => MatrixScale.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      rows: $checkedConvert(
        'rows',
        (v) => (v as List<dynamic>?)
            ?.map((e) => MatrixRow.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      columns: $checkedConvert(
        'columns',
        (v) => (v as List<dynamic>?)
            ?.map((e) => I18nText.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      computedMin: $checkedConvert('computed_min', (v) => (v as num?)?.toInt()),
      computedMax: $checkedConvert('computed_max', (v) => (v as num?)?.toInt()),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'aiDescription': 'ai_description',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'allowContextualOverride': 'allow_contextual_override',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'computedMin': 'computed_min',
    'computedMax': 'computed_max',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$MatrixPromptBlockToJson(MatrixPromptBlock instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'organization_id': instance.organizationId,
      'label': instance.label.toJson(),
      'description': instance.description.toJson(),
      'ai_description': instance.aiDescription,
      'is_evaluative': instance.isEvaluative,
      'type': _$BlockDataTypeEnumMap[instance.type]!,
      'allow_decimals': instance.allowDecimals,
      'output_extensions': instance.outputExtensions,
      'theory_grounding': instance.theoryGrounding?.toJson(),
      'allow_contextual_override': instance.allowContextualOverride,
      'is_lightweight_protocol': instance.isLightweightProtocol,
      'scales': instance.scales.map((e) => e.toJson()).toList(),
      'rows': instance.rows?.map((e) => e.toJson()).toList(),
      'columns': instance.columns?.map((e) => e.toJson()).toList(),
      'computed_min': instance.computedMin,
      'computed_max': instance.computedMax,
      'category_id': instance.$type,
    };

const _$BlockDataTypeEnumMap = {
  BlockDataType.floatType: 'float',
  BlockDataType.intType: 'int',
  BlockDataType.stringType: 'string',
  BlockDataType.instruction: 'instruction',
  BlockDataType.panel: 'panel',
  BlockDataType.compliance: 'compliance',
  BlockDataType.question: 'question',
  BlockDataType.criteria: 'criteria',
};

SystemRulePromptBlock _$SystemRulePromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SystemRulePromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'instruction_text',
        'category_id',
      ],
    );
    final val = SystemRulePromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      isEvaluative: $checkedConvert(
        'is_evaluative',
        (v) => v as bool? ?? false,
      ),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.instruction,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      instructionText: $checkedConvert('instruction_text', (v) => v as String?),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'instructionText': 'instruction_text',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$SystemRulePromptBlockToJson(
  SystemRulePromptBlock instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'organization_id': instance.organizationId,
  'label': instance.label.toJson(),
  'description': instance.description.toJson(),
  'is_evaluative': instance.isEvaluative,
  'type': _$BlockDataTypeEnumMap[instance.type]!,
  'allow_decimals': instance.allowDecimals,
  'output_extensions': instance.outputExtensions,
  'theory_grounding': instance.theoryGrounding?.toJson(),
  'is_lightweight_protocol': instance.isLightweightProtocol,
  'instruction_text': instance.instructionText,
  'category_id': instance.$type,
};

ExecutionPersonaPromptBlock _$ExecutionPersonaPromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ExecutionPersonaPromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'role_enforcement',
        'tone_directives',
        'category_id',
      ],
    );
    final val = ExecutionPersonaPromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      isEvaluative: $checkedConvert(
        'is_evaluative',
        (v) => v as bool? ?? false,
      ),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.instruction,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      roleEnforcement: $checkedConvert('role_enforcement', (v) => v as String?),
      toneDirectives: $checkedConvert(
        'tone_directives',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'roleEnforcement': 'role_enforcement',
    'toneDirectives': 'tone_directives',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$ExecutionPersonaPromptBlockToJson(
  ExecutionPersonaPromptBlock instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'organization_id': instance.organizationId,
  'label': instance.label.toJson(),
  'description': instance.description.toJson(),
  'is_evaluative': instance.isEvaluative,
  'type': _$BlockDataTypeEnumMap[instance.type]!,
  'allow_decimals': instance.allowDecimals,
  'output_extensions': instance.outputExtensions,
  'theory_grounding': instance.theoryGrounding?.toJson(),
  'is_lightweight_protocol': instance.isLightweightProtocol,
  'role_enforcement': instance.roleEnforcement,
  'tone_directives': instance.toneDirectives,
  'category_id': instance.$type,
};

AgentRolePromptBlock _$AgentRolePromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'AgentRolePromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'role_enforcement',
        'tone_directives',
        'category_id',
      ],
    );
    final val = AgentRolePromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      isEvaluative: $checkedConvert(
        'is_evaluative',
        (v) => v as bool? ?? false,
      ),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.instruction,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      roleEnforcement: $checkedConvert('role_enforcement', (v) => v as String?),
      toneDirectives: $checkedConvert(
        'tone_directives',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'roleEnforcement': 'role_enforcement',
    'toneDirectives': 'tone_directives',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$AgentRolePromptBlockToJson(
  AgentRolePromptBlock instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'organization_id': instance.organizationId,
  'label': instance.label.toJson(),
  'description': instance.description.toJson(),
  'is_evaluative': instance.isEvaluative,
  'type': _$BlockDataTypeEnumMap[instance.type]!,
  'allow_decimals': instance.allowDecimals,
  'output_extensions': instance.outputExtensions,
  'theory_grounding': instance.theoryGrounding?.toJson(),
  'is_lightweight_protocol': instance.isLightweightProtocol,
  'role_enforcement': instance.roleEnforcement,
  'tone_directives': instance.toneDirectives,
  'category_id': instance.$type,
};

ProtocolPromptBlock _$ProtocolPromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ProtocolPromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'protocol_instructions',
        'category_id',
      ],
    );
    final val = ProtocolPromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      isEvaluative: $checkedConvert(
        'is_evaluative',
        (v) => v as bool? ?? false,
      ),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.instruction,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      protocolInstructions: $checkedConvert(
        'protocol_instructions',
        (v) => v as String?,
      ),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'protocolInstructions': 'protocol_instructions',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$ProtocolPromptBlockToJson(
  ProtocolPromptBlock instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'organization_id': instance.organizationId,
  'label': instance.label.toJson(),
  'description': instance.description.toJson(),
  'is_evaluative': instance.isEvaluative,
  'type': _$BlockDataTypeEnumMap[instance.type]!,
  'allow_decimals': instance.allowDecimals,
  'output_extensions': instance.outputExtensions,
  'theory_grounding': instance.theoryGrounding?.toJson(),
  'is_lightweight_protocol': instance.isLightweightProtocol,
  'protocol_instructions': instance.protocolInstructions,
  'category_id': instance.$type,
};

RuntimeVariablesPromptBlock _$RuntimeVariablesPromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'RuntimeVariablesPromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'instruction_text',
        'category_id',
      ],
    );
    final val = RuntimeVariablesPromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      isEvaluative: $checkedConvert(
        'is_evaluative',
        (v) => v as bool? ?? false,
      ),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.instruction,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      instructionText: $checkedConvert('instruction_text', (v) => v as String?),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'instructionText': 'instruction_text',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$RuntimeVariablesPromptBlockToJson(
  RuntimeVariablesPromptBlock instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'organization_id': instance.organizationId,
  'label': instance.label.toJson(),
  'description': instance.description.toJson(),
  'is_evaluative': instance.isEvaluative,
  'type': _$BlockDataTypeEnumMap[instance.type]!,
  'allow_decimals': instance.allowDecimals,
  'output_extensions': instance.outputExtensions,
  'theory_grounding': instance.theoryGrounding?.toJson(),
  'is_lightweight_protocol': instance.isLightweightProtocol,
  'instruction_text': instance.instructionText,
  'category_id': instance.$type,
};

TaskDefinitionPromptBlock _$TaskDefinitionPromptBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'TaskDefinitionPromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'instruction_text',
        'category_id',
      ],
    );
    final val = TaskDefinitionPromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      isEvaluative: $checkedConvert(
        'is_evaluative',
        (v) => v as bool? ?? false,
      ),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.instruction,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      isLightweightProtocol: $checkedConvert(
        'is_lightweight_protocol',
        (v) => v as bool? ?? false,
      ),
      instructionText: $checkedConvert('instruction_text', (v) => v as String?),
      $type: $checkedConvert('category_id', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'instructionText': 'instruction_text',
    r'$type': 'category_id',
  },
);

Map<String, dynamic> _$TaskDefinitionPromptBlockToJson(
  TaskDefinitionPromptBlock instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'organization_id': instance.organizationId,
  'label': instance.label.toJson(),
  'description': instance.description.toJson(),
  'is_evaluative': instance.isEvaluative,
  'type': _$BlockDataTypeEnumMap[instance.type]!,
  'allow_decimals': instance.allowDecimals,
  'output_extensions': instance.outputExtensions,
  'theory_grounding': instance.theoryGrounding?.toJson(),
  'is_lightweight_protocol': instance.isLightweightProtocol,
  'instruction_text': instance.instructionText,
  'category_id': instance.$type,
};
