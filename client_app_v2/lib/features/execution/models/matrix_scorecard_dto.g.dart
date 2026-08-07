// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'matrix_scorecard_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReasoningStepDto _$ReasoningStepDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ReasoningStepDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'step_1_identify_premise',
            'step_2_scan_source',
            'step_3_evaluate_anti_patterns',
            'step_4_final_conclusion',
          ],
        );
        final val = _ReasoningStepDto(
          step1IdentifyPremise: $checkedConvert(
            'step_1_identify_premise',
            (v) => v as String,
          ),
          step2ScanSource: $checkedConvert(
            'step_2_scan_source',
            (v) => v as String,
          ),
          step3EvaluateAntiPatterns: $checkedConvert(
            'step_3_evaluate_anti_patterns',
            (v) => v as String,
          ),
          step4FinalConclusion: $checkedConvert(
            'step_4_final_conclusion',
            (v) => v as String,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'step1IdentifyPremise': 'step_1_identify_premise',
        'step2ScanSource': 'step_2_scan_source',
        'step3EvaluateAntiPatterns': 'step_3_evaluate_anti_patterns',
        'step4FinalConclusion': 'step_4_final_conclusion',
      },
    );

Map<String, dynamic> _$ReasoningStepDtoToJson(_ReasoningStepDto instance) =>
    <String, dynamic>{
      'step_1_identify_premise': instance.step1IdentifyPremise,
      'step_2_scan_source': instance.step2ScanSource,
      'step_3_evaluate_anti_patterns': instance.step3EvaluateAntiPatterns,
      'step_4_final_conclusion': instance.step4FinalConclusion,
    };

_QuoteEvidenceDto _$QuoteEvidenceDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_QuoteEvidenceDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'quote',
        'verified_source_ids',
        'unverified_aliases',
        'is_verified',
      ],
    );
    final val = _QuoteEvidenceDto(
      quote: $checkedConvert('quote', (v) => v as String),
      verifiedSourceIds: $checkedConvert(
        'verified_source_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      unverifiedAliases: $checkedConvert(
        'unverified_aliases',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      isVerified: $checkedConvert('is_verified', (v) => v as bool? ?? false),
    );
    return val;
  },
  fieldKeyMap: const {
    'verifiedSourceIds': 'verified_source_ids',
    'unverifiedAliases': 'unverified_aliases',
    'isVerified': 'is_verified',
  },
);

Map<String, dynamic> _$QuoteEvidenceDtoToJson(_QuoteEvidenceDto instance) =>
    <String, dynamic>{
      'quote': instance.quote,
      'verified_source_ids': instance.verifiedSourceIds,
      'unverified_aliases': instance.unverifiedAliases,
      'is_verified': instance.isVerified,
    };

_HumanOverrideDto _$HumanOverrideDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_HumanOverrideDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'new_status',
            'reason',
            'evidence_quotes',
            'overridden_by',
            'overridden_at',
          ],
        );
        final val = _HumanOverrideDto(
          newStatus: $checkedConvert('new_status', (v) => v as String),
          reason: $checkedConvert('reason', (v) => v as String),
          evidenceQuotes: $checkedConvert(
            'evidence_quotes',
            (v) => (v as List<dynamic>)
                .map(
                  (e) => QuoteEvidenceDto.fromJson(e as Map<String, dynamic>),
                )
                .toList(),
          ),
          overriddenBy: $checkedConvert('overridden_by', (v) => v as String),
          overriddenAt: $checkedConvert(
            'overridden_at',
            (v) => DateTime.parse(v as String),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'newStatus': 'new_status',
        'evidenceQuotes': 'evidence_quotes',
        'overriddenBy': 'overridden_by',
        'overriddenAt': 'overridden_at',
      },
    );

Map<String, dynamic> _$HumanOverrideDtoToJson(
  _HumanOverrideDto instance,
) => <String, dynamic>{
  'new_status': instance.newStatus,
  'reason': instance.reason,
  'evidence_quotes': instance.evidenceQuotes.map((e) => e.toJson()).toList(),
  'overridden_by': instance.overriddenBy,
  'overridden_at': instance.overriddenAt.toIso8601String(),
};

_ScorecardAtomDto _$ScorecardAtomDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ScorecardAtomDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'atom_id',
            'level',
            'level_name',
            'claim_label',
            'extracted_facts',
            'exact_quotes',
            'internal_logic_en',
            'status',
            'semantic_reasoning',
            'contextual_override',
            'structural_location',
            'human_override',
            'chart_display_label',
            'visual_intent',
          ],
        );
        final val = _ScorecardAtomDto(
          atomId: $checkedConvert('atom_id', (v) => v as String),
          level: $checkedConvert('level', (v) => (v as num).toInt()),
          levelName: $checkedConvert('level_name', (v) => v as String),
          claimLabel: $checkedConvert('claim_label', (v) => v as String),
          extractedFacts: $checkedConvert(
            'extracted_facts',
            (v) => Map<String, String?>.from(v as Map),
          ),
          exactQuotes: $checkedConvert(
            'exact_quotes',
            (v) => (v as List<dynamic>)
                .map(
                  (e) => QuoteEvidenceDto.fromJson(e as Map<String, dynamic>),
                )
                .toList(),
          ),
          internalLogicEn: $checkedConvert(
            'internal_logic_en',
            (v) => ReasoningStepDto.fromJson(v as Map<String, dynamic>),
          ),
          status: $checkedConvert(
            'status',
            (v) => $enumDecodeNullable(_$AtomEvaluationStatusEnumMap, v),
          ),
          semanticReasoning: $checkedConvert(
            'semantic_reasoning',
            (v) => v as String,
          ),
          contextualOverride: $checkedConvert(
            'contextual_override',
            (v) => v as bool,
          ),
          structuralLocation: $checkedConvert(
            'structural_location',
            (v) => v as String?,
          ),
          humanOverride: $checkedConvert(
            'human_override',
            (v) => v == null
                ? null
                : HumanOverrideDto.fromJson(v as Map<String, dynamic>),
          ),
          chartDisplayLabel: $checkedConvert(
            'chart_display_label',
            (v) => v as String,
          ),
          visualIntent: $checkedConvert(
            'visual_intent',
            (v) => $enumDecode(_$VisualIntentEnumMap, v),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'atomId': 'atom_id',
        'levelName': 'level_name',
        'claimLabel': 'claim_label',
        'extractedFacts': 'extracted_facts',
        'exactQuotes': 'exact_quotes',
        'internalLogicEn': 'internal_logic_en',
        'semanticReasoning': 'semantic_reasoning',
        'contextualOverride': 'contextual_override',
        'structuralLocation': 'structural_location',
        'humanOverride': 'human_override',
        'chartDisplayLabel': 'chart_display_label',
        'visualIntent': 'visual_intent',
      },
    );

Map<String, dynamic> _$ScorecardAtomDtoToJson(_ScorecardAtomDto instance) =>
    <String, dynamic>{
      'atom_id': instance.atomId,
      'level': instance.level,
      'level_name': instance.levelName,
      'claim_label': instance.claimLabel,
      'extracted_facts': instance.extractedFacts,
      'exact_quotes': instance.exactQuotes.map((e) => e.toJson()).toList(),
      'internal_logic_en': instance.internalLogicEn.toJson(),
      'status': _$AtomEvaluationStatusEnumMap[instance.status],
      'semantic_reasoning': instance.semanticReasoning,
      'contextual_override': instance.contextualOverride,
      'structural_location': instance.structuralLocation,
      'human_override': instance.humanOverride?.toJson(),
      'chart_display_label': instance.chartDisplayLabel,
      'visual_intent': _$VisualIntentEnumMap[instance.visualIntent]!,
    };

const _$AtomEvaluationStatusEnumMap = {
  AtomEvaluationStatus.pass: 'PASS',
  AtomEvaluationStatus.fail: 'FAIL',
  AtomEvaluationStatus.contested: 'CONTESTED',
  AtomEvaluationStatus.dlq: 'DLQ',
};

const _$VisualIntentEnumMap = {
  VisualIntent.success: 'success',
  VisualIntent.warning: 'warning',
  VisualIntent.error: 'error',
  VisualIntent.criticalOverride: 'critical_override',
  VisualIntent.info: 'info',
  VisualIntent.neutral: 'NEUTRAL',
};

_McpAuditTraceDto _$McpAuditTraceDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_McpAuditTraceDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'tool_id',
        'step_name',
        'claim_text',
        'query',
        'knowledge_gap',
        'search_rationale',
        'reasoning',
        'response_summary',
        'source_urls',
        'impacted_axis_names',
        'timestamp',
        'duration_ms',
      ],
    );
    final val = _McpAuditTraceDto(
      id: $checkedConvert('id', (v) => v as String?),
      toolId: $checkedConvert('tool_id', (v) => v as String),
      stepName: $checkedConvert('step_name', (v) => v as String),
      claimText: $checkedConvert('claim_text', (v) => v as String?),
      query: $checkedConvert('query', (v) => v as String),
      knowledgeGap: $checkedConvert('knowledge_gap', (v) => v as String? ?? ''),
      searchRationale: $checkedConvert(
        'search_rationale',
        (v) => v as String? ?? '',
      ),
      reasoning: $checkedConvert('reasoning', (v) => v as String? ?? ''),
      responseSummary: $checkedConvert(
        'response_summary',
        (v) => v as String? ?? '',
      ),
      sourceUrls: $checkedConvert(
        'source_urls',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      impactedAxisNames: $checkedConvert(
        'impacted_axis_names',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      timestamp: $checkedConvert('timestamp', (v) => v as String?),
      durationMs: $checkedConvert(
        'duration_ms',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'toolId': 'tool_id',
    'stepName': 'step_name',
    'claimText': 'claim_text',
    'knowledgeGap': 'knowledge_gap',
    'searchRationale': 'search_rationale',
    'responseSummary': 'response_summary',
    'sourceUrls': 'source_urls',
    'impactedAxisNames': 'impacted_axis_names',
    'durationMs': 'duration_ms',
  },
);

Map<String, dynamic> _$McpAuditTraceDtoToJson(_McpAuditTraceDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'tool_id': instance.toolId,
      'step_name': instance.stepName,
      'claim_text': instance.claimText,
      'query': instance.query,
      'knowledge_gap': instance.knowledgeGap,
      'search_rationale': instance.searchRationale,
      'reasoning': instance.reasoning,
      'response_summary': instance.responseSummary,
      'source_urls': instance.sourceUrls,
      'impacted_axis_names': instance.impactedAxisNames,
      'timestamp': instance.timestamp,
      'duration_ms': instance.durationMs,
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
        'label_i18n',
        'description',
        'score',
        'score_display_label',
        'scale_min',
        'scale_max',
        'normalized_score',
        'true_atoms',
        'total_atoms',
        'row_explanation',
        'cited_source_id',
        'cited_text_quote',
        'cited_web_citation',
        'evidence_type',
        'tda_state',
        'confidence',
        'inner_sdui_blocks',
        'level_breakdown',
        'level_names',
        'ui_boundary_labels',
        'ui_plot_ratio',
        'is_evaluative',
        'contextual_override',
        'semantic_reasoning',
        'evaluated_atoms',
        'clustered_row_sources',
        'used_evidence_ids',
      ],
    );
    final val = _MatrixScorecardRowDto(
      blockId: $checkedConvert('block_id', (v) => v as String),
      name: $checkedConvert('name', (v) => v as String),
      labelI18n: $checkedConvert(
        'label_i18n',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert('description', (v) => v as String?),
      score: $checkedConvert('score', (v) => (v as num?)?.toDouble()),
      scoreDisplayLabel: $checkedConvert(
        'score_display_label',
        (v) => v as String?,
      ),
      scaleMin: $checkedConvert('scale_min', (v) => (v as num?)?.toDouble()),
      scaleMax: $checkedConvert('scale_max', (v) => (v as num?)?.toDouble()),
      normalizedScore: $checkedConvert(
        'normalized_score',
        (v) => (v as num?)?.toDouble(),
      ),
      trueAtoms: $checkedConvert('true_atoms', (v) => (v as num?)?.toInt()),
      totalAtoms: $checkedConvert('total_atoms', (v) => (v as num?)?.toInt()),
      rowExplanation: $checkedConvert(
        'row_explanation',
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
      tdaState: $checkedConvert(
        'tda_state',
        (v) => v == null ? null : TDAState.fromJson(v as Map<String, dynamic>),
      ),
      confidence: $checkedConvert('confidence', (v) => (v as num?)?.toDouble()),
      innerSduiBlocks: $checkedConvert(
        'inner_sdui_blocks',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
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
      contextualOverride: $checkedConvert(
        'contextual_override',
        (v) => v as bool?,
      ),
      semanticReasoning: $checkedConvert(
        'semantic_reasoning',
        (v) => v as String?,
      ),
      evaluatedAtoms: $checkedConvert(
        'evaluated_atoms',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => ScorecardAtomDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      clusteredRowSources: $checkedConvert(
        'clustered_row_sources',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => McpAuditTraceDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      usedEvidenceIds: $checkedConvert(
        'used_evidence_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'blockId': 'block_id',
    'labelI18n': 'label_i18n',
    'scoreDisplayLabel': 'score_display_label',
    'scaleMin': 'scale_min',
    'scaleMax': 'scale_max',
    'normalizedScore': 'normalized_score',
    'trueAtoms': 'true_atoms',
    'totalAtoms': 'total_atoms',
    'rowExplanation': 'row_explanation',
    'citedSourceId': 'cited_source_id',
    'citedTextQuote': 'cited_text_quote',
    'citedWebCitation': 'cited_web_citation',
    'evidenceType': 'evidence_type',
    'tdaState': 'tda_state',
    'innerSduiBlocks': 'inner_sdui_blocks',
    'levelBreakdown': 'level_breakdown',
    'levelNames': 'level_names',
    'uiBoundaryLabels': 'ui_boundary_labels',
    'uiPlotRatio': 'ui_plot_ratio',
    'isEvaluative': 'is_evaluative',
    'contextualOverride': 'contextual_override',
    'semanticReasoning': 'semantic_reasoning',
    'evaluatedAtoms': 'evaluated_atoms',
    'clusteredRowSources': 'clustered_row_sources',
    'usedEvidenceIds': 'used_evidence_ids',
  },
);

Map<String, dynamic> _$MatrixScorecardRowDtoToJson(
  _MatrixScorecardRowDto instance,
) => <String, dynamic>{
  'block_id': instance.blockId,
  'name': instance.name,
  'label_i18n': instance.labelI18n.toJson(),
  'description': instance.description,
  'score': instance.score,
  'score_display_label': instance.scoreDisplayLabel,
  'scale_min': instance.scaleMin,
  'scale_max': instance.scaleMax,
  'normalized_score': instance.normalizedScore,
  'true_atoms': instance.trueAtoms,
  'total_atoms': instance.totalAtoms,
  'row_explanation': instance.rowExplanation,
  'cited_source_id': instance.citedSourceId,
  'cited_text_quote': instance.citedTextQuote,
  'cited_web_citation': instance.citedWebCitation,
  'evidence_type': _$EvidenceTypeEnumMap[instance.evidenceType],
  'tda_state': instance.tdaState?.toJson(),
  'confidence': instance.confidence,
  'inner_sdui_blocks': instance.innerSduiBlocks.map((e) => e.toJson()).toList(),
  'level_breakdown': instance.levelBreakdown,
  'level_names': instance.levelNames,
  'ui_boundary_labels': instance.uiBoundaryLabels,
  'ui_plot_ratio': instance.uiPlotRatio,
  'is_evaluative': instance.isEvaluative,
  'contextual_override': instance.contextualOverride,
  'semantic_reasoning': instance.semanticReasoning,
  'evaluated_atoms': instance.evaluatedAtoms.map((e) => e.toJson()).toList(),
  'clustered_row_sources': instance.clusteredRowSources
      .map((e) => e.toJson())
      .toList(),
  'used_evidence_ids': instance.usedEvidenceIds,
};

const _$EvidenceTypeEnumMap = {
  EvidenceType.explicitQuote: 'EXPLICIT_QUOTE',
  EvidenceType.impliedIntent: 'IMPLIED_INTENT',
  EvidenceType.noEvidence: 'NO_EVIDENCE',
};
