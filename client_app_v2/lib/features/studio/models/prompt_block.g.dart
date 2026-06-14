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
            (v) => v as String,
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
        'inverse_evidence',
        'aggregation_mode',
        'evaluation_track',
        'facts_to_find',
        'logical_expression',
        'allow_contextual_override',
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
      allowContextualOverride: $checkedConvert(
        'allow_contextual_override',
        (v) => v as bool? ?? false,
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
    'inverseEvidence': 'inverse_evidence',
    'aggregationMode': 'aggregation_mode',
    'evaluationTrack': 'evaluation_track',
    'factsToFind': 'facts_to_find',
    'logicalExpression': 'logical_expression',
    'allowContextualOverride': 'allow_contextual_override',
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
      'inverse_evidence': instance.inverseEvidence,
      'aggregation_mode': _$AggregationModeEnumMap[instance.aggregationMode]!,
      'evaluation_track': _$EvaluationTrackEnumMap[instance.evaluationTrack]!,
      'facts_to_find': instance.factsToFind,
      'logical_expression': instance.logicalExpression,
      'allow_contextual_override': instance.allowContextualOverride,
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

_MatrixClaim _$MatrixClaimFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_MatrixClaim',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['label', 'ai_description', 'tda_assertions'],
    );
    final val = _MatrixClaim(
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      aiDescription: $checkedConvert('ai_description', (v) => v as String),
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
  },
  fieldKeyMap: const {
    'aiDescription': 'ai_description',
    'tdaAssertions': 'tda_assertions',
  },
);

Map<String, dynamic> _$MatrixClaimToJson(_MatrixClaim instance) =>
    <String, dynamic>{
      'label': instance.label.toJson(),
      'ai_description': instance.aiDescription,
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

_PromptBlock _$PromptBlockFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_PromptBlock',
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
        'category_id',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'is_lightweight_protocol',
        'scale_min',
        'scale_max',
        'computed_min',
        'computed_max',
        'scales',
        'rows',
        'columns',
      ],
    );
    final val = _PromptBlock(
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
      categoryId: $checkedConvert(
        'category_id',
        (v) => v as String? ?? 'system',
      ),
      isEvaluative: $checkedConvert('is_evaluative', (v) => v as bool? ?? true),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.stringType,
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
      scaleMin: $checkedConvert('scale_min', (v) => (v as num?)?.toInt()),
      scaleMax: $checkedConvert('scale_max', (v) => (v as num?)?.toInt()),
      computedMin: $checkedConvert('computed_min', (v) => (v as num?)?.toInt()),
      computedMax: $checkedConvert('computed_max', (v) => (v as num?)?.toInt()),
      scales: $checkedConvert(
        'scales',
        (v) => (v as List<dynamic>?)
            ?.map((e) => MatrixScale.fromJson(e as Map<String, dynamic>))
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
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'aiDescription': 'ai_description',
    'categoryId': 'category_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'isLightweightProtocol': 'is_lightweight_protocol',
    'scaleMin': 'scale_min',
    'scaleMax': 'scale_max',
    'computedMin': 'computed_min',
    'computedMax': 'computed_max',
  },
);

Map<String, dynamic> _$PromptBlockToJson(_PromptBlock instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'organization_id': instance.organizationId,
      'label': instance.label.toJson(),
      'description': instance.description.toJson(),
      'ai_description': instance.aiDescription,
      'category_id': instance.categoryId,
      'is_evaluative': instance.isEvaluative,
      'type': _$BlockDataTypeEnumMap[instance.type]!,
      'allow_decimals': instance.allowDecimals,
      'output_extensions': instance.outputExtensions,
      'theory_grounding': instance.theoryGrounding?.toJson(),
      'is_lightweight_protocol': instance.isLightweightProtocol,
      'scale_min': instance.scaleMin,
      'scale_max': instance.scaleMax,
      'scales': instance.scales?.map((e) => e.toJson()).toList(),
      'rows': instance.rows?.map((e) => e.toJson()).toList(),
      'columns': instance.columns?.map((e) => e.toJson()).toList(),
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
