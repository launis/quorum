// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scorecard_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ScorecardResponseDto _$ScorecardResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ScorecardResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'execution_id',
        'workflow_id',
        'global_average',
        'evaluative_matrices',
        'informational_matrices',
      ],
    );
    final val = _ScorecardResponseDto(
      executionId: $checkedConvert('execution_id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      globalAverage: $checkedConvert(
        'global_average',
        (v) => (v as num?)?.toDouble(),
      ),
      evaluativeMatrices: $checkedConvert(
        'evaluative_matrices',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      informationalMatrices: $checkedConvert(
        'informational_matrices',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'executionId': 'execution_id',
    'workflowId': 'workflow_id',
    'globalAverage': 'global_average',
    'evaluativeMatrices': 'evaluative_matrices',
    'informationalMatrices': 'informational_matrices',
  },
);

Map<String, dynamic> _$ScorecardResponseDtoToJson(
  _ScorecardResponseDto instance,
) => <String, dynamic>{
  'execution_id': instance.executionId,
  'workflow_id': instance.workflowId,
  'global_average': instance.globalAverage,
  'evaluative_matrices': instance.evaluativeMatrices
      .map((e) => e.toJson())
      .toList(),
  'informational_matrices': instance.informationalMatrices
      .map((e) => e.toJson())
      .toList(),
};

_MatrixScorecardRowDto _$MatrixScorecardRowDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_MatrixScorecardRowDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'block_id',
        'name',
        'label_fi',
        'label_en',
        'description',
        'score',
        'scale_min',
        'scale_max',
        'normalized_score',
        'true_atoms',
        'total_atoms',
        'justification',
        'cited_source_id',
        'cited_text_quote',
        'cited_web_citation',
        'evidence_type',
        'coaching',
        'confidence',
        'falsification',
        'missing_context',
        'risk_flag',
        'remediation_steps',
        'emotional_sentiment',
        'theory_link',
        'level_breakdown',
        'level_names',
        'ui_boundary_labels',
        'ui_plot_ratio',
        'is_evaluative',
      ],
    );
    final val = _MatrixScorecardRowDto(
      blockId: $checkedConvert('block_id', (v) => v as String),
      name: $checkedConvert('name', (v) => v as String),
      labelFi: $checkedConvert('label_fi', (v) => v as String),
      labelEn: $checkedConvert('label_en', (v) => v as String),
      description: $checkedConvert('description', (v) => v as String?),
      score: $checkedConvert('score', (v) => (v as num?)?.toDouble()),
      scaleMin: $checkedConvert('scale_min', (v) => (v as num?)?.toDouble()),
      scaleMax: $checkedConvert('scale_max', (v) => (v as num?)?.toDouble()),
      normalizedScore: $checkedConvert(
        'normalized_score',
        (v) => (v as num?)?.toDouble(),
      ),
      trueAtoms: $checkedConvert('true_atoms', (v) => (v as num?)?.toInt()),
      totalAtoms: $checkedConvert('total_atoms', (v) => (v as num?)?.toInt()),
      justification: $checkedConvert(
        'justification',
        (v) => v as String? ?? '',
      ),
      citedSourceId: $checkedConvert('cited_source_id', (v) => v as String?),
      citedTextQuote: $checkedConvert('cited_text_quote', (v) => v as String?),
      citedWebCitation: $checkedConvert(
        'cited_web_citation',
        (v) => v as String?,
      ),
      evidenceType: $checkedConvert(
        'evidence_type',
        (v) => $enumDecodeNullable(_$EvidenceTypeEnumMap, v),
      ),
      coaching: $checkedConvert('coaching', (v) => v as String?),
      confidence: $checkedConvert('confidence', (v) => (v as num?)?.toDouble()),
      falsification: $checkedConvert('falsification', (v) => v as String?),
      missingContext: $checkedConvert('missing_context', (v) => v as String?),
      riskFlag: $checkedConvert('risk_flag', (v) => v as bool?),
      remediationSteps: $checkedConvert(
        'remediation_steps',
        (v) => v as String?,
      ),
      emotionalSentiment: $checkedConvert(
        'emotional_sentiment',
        (v) => v as String?,
      ),
      theoryLink: $checkedConvert('theory_link', (v) => v as String?),
      levelBreakdown: $checkedConvert(
        'level_breakdown',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      levelNames: $checkedConvert(
        'level_names',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      uiBoundaryLabels: $checkedConvert(
        'ui_boundary_labels',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      uiPlotRatio: $checkedConvert(
        'ui_plot_ratio',
        (v) => (v as num?)?.toDouble(),
      ),
      isEvaluative: $checkedConvert('is_evaluative', (v) => v as bool? ?? true),
    );
    return val;
  },
  fieldKeyMap: const {
    'blockId': 'block_id',
    'labelFi': 'label_fi',
    'labelEn': 'label_en',
    'scaleMin': 'scale_min',
    'scaleMax': 'scale_max',
    'normalizedScore': 'normalized_score',
    'trueAtoms': 'true_atoms',
    'totalAtoms': 'total_atoms',
    'citedSourceId': 'cited_source_id',
    'citedTextQuote': 'cited_text_quote',
    'citedWebCitation': 'cited_web_citation',
    'evidenceType': 'evidence_type',
    'missingContext': 'missing_context',
    'riskFlag': 'risk_flag',
    'remediationSteps': 'remediation_steps',
    'emotionalSentiment': 'emotional_sentiment',
    'theoryLink': 'theory_link',
    'levelBreakdown': 'level_breakdown',
    'levelNames': 'level_names',
    'uiBoundaryLabels': 'ui_boundary_labels',
    'uiPlotRatio': 'ui_plot_ratio',
    'isEvaluative': 'is_evaluative',
  },
);

Map<String, dynamic> _$MatrixScorecardRowDtoToJson(
  _MatrixScorecardRowDto instance,
) => <String, dynamic>{
  'block_id': instance.blockId,
  'name': instance.name,
  'label_fi': instance.labelFi,
  'label_en': instance.labelEn,
  'description': instance.description,
  'score': instance.score,
  'scale_min': instance.scaleMin,
  'scale_max': instance.scaleMax,
  'normalized_score': instance.normalizedScore,
  'true_atoms': instance.trueAtoms,
  'total_atoms': instance.totalAtoms,
  'justification': instance.justification,
  'cited_source_id': instance.citedSourceId,
  'cited_text_quote': instance.citedTextQuote,
  'cited_web_citation': instance.citedWebCitation,
  'evidence_type': _$EvidenceTypeEnumMap[instance.evidenceType],
  'coaching': instance.coaching,
  'confidence': instance.confidence,
  'falsification': instance.falsification,
  'missing_context': instance.missingContext,
  'risk_flag': instance.riskFlag,
  'remediation_steps': instance.remediationSteps,
  'emotional_sentiment': instance.emotionalSentiment,
  'theory_link': instance.theoryLink,
  'level_breakdown': instance.levelBreakdown,
  'level_names': instance.levelNames,
  'ui_boundary_labels': instance.uiBoundaryLabels,
  'ui_plot_ratio': instance.uiPlotRatio,
  'is_evaluative': instance.isEvaluative,
};

const _$EvidenceTypeEnumMap = {
  EvidenceType.explicitQuote: 'EXPLICIT_QUOTE',
  EvidenceType.impliedIntent: 'IMPLIED_INTENT',
  EvidenceType.noEvidence: 'NO_EVIDENCE',
};
