// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'output_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MatrixSynthesisGroup _$MatrixSynthesisGroupFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_MatrixSynthesisGroup',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'title',
        'target_blocks',
        'synthesis_directive',
        'view_type',
      ],
    );
    final val = _MatrixSynthesisGroup(
      id: $checkedConvert('id', (v) => v as String),
      title: $checkedConvert(
        'title',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      targetBlocks: $checkedConvert(
        'target_blocks',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
      synthesisDirective: $checkedConvert(
        'synthesis_directive',
        (v) => v as String?,
      ),
      viewType: $checkedConvert(
        'view_type',
        (v) =>
            $enumDecodeNullable(_$PresetViewEnumMap, v) ?? PresetView.metrics1d,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'targetBlocks': 'target_blocks',
    'synthesisDirective': 'synthesis_directive',
    'viewType': 'view_type',
  },
);

Map<String, dynamic> _$MatrixSynthesisGroupToJson(
  _MatrixSynthesisGroup instance,
) => <String, dynamic>{
  'id': instance.id,
  'title': instance.title.toJson(),
  'target_blocks': instance.targetBlocks,
  'synthesis_directive': instance.synthesisDirective,
  'view_type': _$PresetViewEnumMap[instance.viewType]!,
};

const _$PresetViewEnumMap = {
  PresetView.metrics1d: '1d_metrics',
  PresetView.compare2d: '2d_compare',
  PresetView.matrix3d: '3d_matrix',
  PresetView.textOnly: 'text_only',
  PresetView.defaultView: 'default',
  PresetView.matrixSummary: 'matrix_summary',
};

_SynthesisConfigDTO _$SynthesisConfigDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_SynthesisConfigDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'system_prompt',
            'synthesis_block_id',
            'row_explanations_block_id',
            'length_constraint',
            'preamble_text',
            'tone_instruction',
            'max_quotes_per_matrix',
            'max_unmet_criteria',
          ],
        );
        final val = _SynthesisConfigDTO(
          systemPrompt: $checkedConvert('system_prompt', (v) => v as String?),
          synthesisBlockId: $checkedConvert(
            'synthesis_block_id',
            (v) => v as String?,
          ),
          rowExplanationsBlockId: $checkedConvert(
            'row_explanations_block_id',
            (v) => v as String?,
          ),
          lengthConstraint: $checkedConvert(
            'length_constraint',
            (v) => (v as num?)?.toInt(),
          ),
          preambleText: $checkedConvert(
            'preamble_text',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          toneInstruction: $checkedConvert(
            'tone_instruction',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          maxQuotesPerMatrix: $checkedConvert(
            'max_quotes_per_matrix',
            (v) => (v as num?)?.toInt(),
          ),
          maxUnmetCriteria: $checkedConvert(
            'max_unmet_criteria',
            (v) => (v as num?)?.toInt(),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemPrompt': 'system_prompt',
        'synthesisBlockId': 'synthesis_block_id',
        'rowExplanationsBlockId': 'row_explanations_block_id',
        'lengthConstraint': 'length_constraint',
        'preambleText': 'preamble_text',
        'toneInstruction': 'tone_instruction',
        'maxQuotesPerMatrix': 'max_quotes_per_matrix',
        'maxUnmetCriteria': 'max_unmet_criteria',
      },
    );

Map<String, dynamic> _$SynthesisConfigDTOToJson(_SynthesisConfigDTO instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'synthesis_block_id': instance.synthesisBlockId,
      'row_explanations_block_id': instance.rowExplanationsBlockId,
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'tone_instruction': instance.toneInstruction?.toJson(),
      'max_quotes_per_matrix': instance.maxQuotesPerMatrix,
      'max_unmet_criteria': instance.maxUnmetCriteria,
    };

_OutputProfile _$OutputProfileFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_OutputProfile',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'workflow_id',
        'organization_id',
        'name',
        'description',
        'user_role_label',
        'custom_preface',
        'visible_metadata',
        'matrix_visible_columns',
        'visible_block_extensions',
        'visible_workflow_extensions',
        'max_extension_items',
        'display_scale',
        'custom_scale_min',
        'custom_scale_max',
        'strictness_level',
        'scoring_strategy',
        'tone_instruction',
        'language',
        'matrix_synthesis_groups',
        'content_blocks',
        'target_block_order',
        'show_sources_summary_box',
        'sources_display_mode',
        'synthesis',
        'performativity_detector_step_id',
      ],
    );
    final val = _OutputProfile(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String? ?? ''),
      workflowId: $checkedConvert(
        'workflow_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      name: $checkedConvert(
        'name',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      userRoleLabel: $checkedConvert(
        'user_role_label',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      customPreface: $checkedConvert(
        'custom_preface',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      visibleMetadata: $checkedConvert(
        'visible_metadata',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const [
              'date',
              'organization',
              'user',
              'scoring_engine',
              'strictness',
            ],
      ),
      matrixVisibleColumns: $checkedConvert(
        'matrix_visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const [
              'label',
              'distribution',
              'row_explanation',
              'quotes',
              'normalized_score',
              'score',
            ],
      ),
      visibleBlockExtensions: $checkedConvert(
        'visible_block_extensions',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => $enumDecode(_$XaiExtensionTypeEnumMap, e))
                .toList() ??
            const [],
      ),
      visibleWorkflowExtensions: $checkedConvert(
        'visible_workflow_extensions',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => $enumDecode(_$XaiExtensionTypeEnumMap, e))
                .toList() ??
            const [],
      ),
      maxExtensionItems: $checkedConvert(
        'max_extension_items',
        (v) => (v as num?)?.toInt() ?? 3,
      ),
      displayScale: $checkedConvert(
        'display_scale',
        (v) =>
            $enumDecodeNullable(_$DisplayScaleEnumMap, v) ??
            DisplayScale.original,
      ),
      customScaleMin: $checkedConvert(
        'custom_scale_min',
        (v) => (v as num?)?.toDouble(),
      ),
      customScaleMax: $checkedConvert(
        'custom_scale_max',
        (v) => (v as num?)?.toDouble(),
      ),
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt(),
      ),
      scoringStrategy: $checkedConvert(
        'scoring_strategy',
        (v) => $enumDecodeNullable(_$ScoringStrategyEnumMap, v),
      ),
      toneInstruction: $checkedConvert(
        'tone_instruction',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      language: $checkedConvert('language', (v) => v as String?),
      matrixSynthesisGroups: $checkedConvert(
        'matrix_synthesis_groups',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixSynthesisGroup.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      contentBlocks: $checkedConvert(
        'content_blocks',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      targetBlockOrder: $checkedConvert(
        'target_block_order',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => $enumDecode(_$TargetBlockTypeEnumMap, e))
                .toList() ??
            const [
              TargetBlockType.metadataBlock,
              TargetBlockType.executiveSummaryBlock,
              TargetBlockType.matrixGraphsBlock,
              TargetBlockType.groupedExtensionsBlock,
              TargetBlockType.penaltiesBlock,
              TargetBlockType.matrixSummaryTableBlock,
              TargetBlockType.varianceValidationBlock,
              TargetBlockType.authenticityEvaluationBlock,
              TargetBlockType.printableSourcesBlock,
              TargetBlockType.globalScoreBlock,
              TargetBlockType.auditTrailBlock,
            ],
      ),
      showSourcesSummaryBox: $checkedConvert(
        'show_sources_summary_box',
        (v) => v as bool? ?? true,
      ),
      sourcesDisplayMode: $checkedConvert(
        'sources_display_mode',
        (v) =>
            $enumDecodeNullable(_$SourcesDisplayModeEnumMap, v) ??
            SourcesDisplayMode.verifiedEvidence,
      ),
      synthesis: $checkedConvert(
        'synthesis',
        (v) => v == null
            ? null
            : SynthesisConfigDTO.fromJson(v as Map<String, dynamic>),
      ),
      performativityDetectorStepId: $checkedConvert(
        'performativity_detector_step_id',
        (v) => v as String?,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'organizationId': 'organization_id',
    'userRoleLabel': 'user_role_label',
    'customPreface': 'custom_preface',
    'visibleMetadata': 'visible_metadata',
    'matrixVisibleColumns': 'matrix_visible_columns',
    'visibleBlockExtensions': 'visible_block_extensions',
    'visibleWorkflowExtensions': 'visible_workflow_extensions',
    'maxExtensionItems': 'max_extension_items',
    'displayScale': 'display_scale',
    'customScaleMin': 'custom_scale_min',
    'customScaleMax': 'custom_scale_max',
    'strictnessLevel': 'strictness_level',
    'scoringStrategy': 'scoring_strategy',
    'toneInstruction': 'tone_instruction',
    'matrixSynthesisGroups': 'matrix_synthesis_groups',
    'contentBlocks': 'content_blocks',
    'targetBlockOrder': 'target_block_order',
    'showSourcesSummaryBox': 'show_sources_summary_box',
    'sourcesDisplayMode': 'sources_display_mode',
    'performativityDetectorStepId': 'performativity_detector_step_id',
  },
);

Map<String, dynamic> _$OutputProfileToJson(
  _OutputProfile instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'workflow_id': const StrictOpaqueIdConverter().toJson(instance.workflowId),
  'organization_id': instance.organizationId,
  'name': instance.name.toJson(),
  'description': instance.description?.toJson(),
  'user_role_label': instance.userRoleLabel?.toJson(),
  'custom_preface': instance.customPreface?.toJson(),
  'visible_metadata': instance.visibleMetadata,
  'matrix_visible_columns': instance.matrixVisibleColumns,
  'visible_block_extensions': instance.visibleBlockExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'visible_workflow_extensions': instance.visibleWorkflowExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'max_extension_items': instance.maxExtensionItems,
  'display_scale': _$DisplayScaleEnumMap[instance.displayScale]!,
  'custom_scale_min': instance.customScaleMin,
  'custom_scale_max': instance.customScaleMax,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
  'tone_instruction': instance.toneInstruction?.toJson(),
  'language': instance.language,
  'matrix_synthesis_groups': instance.matrixSynthesisGroups
      .map((e) => e.toJson())
      .toList(),
  'content_blocks': instance.contentBlocks.map((e) => e.toJson()).toList(),
  'target_block_order': instance.targetBlockOrder
      .map((e) => _$TargetBlockTypeEnumMap[e]!)
      .toList(),
  'show_sources_summary_box': instance.showSourcesSummaryBox,
  'sources_display_mode':
      _$SourcesDisplayModeEnumMap[instance.sourcesDisplayMode]!,
  'synthesis': instance.synthesis?.toJson(),
  'performativity_detector_step_id': instance.performativityDetectorStepId,
};

const _$XaiExtensionTypeEnumMap = {
  XaiExtensionType.citation: 'citation',
  XaiExtensionType.justification: 'justification',
  XaiExtensionType.falsification: 'falsification',
  XaiExtensionType.theoryLink: 'theory_link',
  XaiExtensionType.riskFlag: 'risk_flag',
  XaiExtensionType.coaching: 'coaching',
  XaiExtensionType.missingContext: 'missing_context',
  XaiExtensionType.remediationSteps: 'remediation_steps',
  XaiExtensionType.emotionalSentiment: 'emotional_sentiment',
  XaiExtensionType.confidence: 'confidence',
  XaiExtensionType.sourceId: 'source_id',
  XaiExtensionType.contextualOverride: 'contextual_override',
  XaiExtensionType.varianceValidation: 'variance_validation',
  XaiExtensionType.authenticityEvaluation: 'authenticity_evaluation',
};

const _$DisplayScaleEnumMap = {
  DisplayScale.original: 'original',
  DisplayScale.custom: 'custom',
  DisplayScale.normalized100: 'normalized_100',
};

const _$ScoringStrategyEnumMap = {
  ScoringStrategy.waterfall: 'WATERFALL',
  ScoringStrategy.average: 'AVERAGE',
  ScoringStrategy.weightedAverage: 'WEIGHTED_AVERAGE',
  ScoringStrategy.pureMath: 'PURE_MATH',
};

const _$TargetBlockTypeEnumMap = {
  TargetBlockType.globalScoreBlock: 'global_score_block',
  TargetBlockType.penaltiesBlock: 'penalties_block',
  TargetBlockType.auditTrailBlock: 'audit_trail_block',
  TargetBlockType.jargonRatioBlock: 'jargon_ratio_block',
  TargetBlockType.printableSourcesBlock: 'printable_sources_block',
  TargetBlockType.groupedExtensionsBlock: 'grouped_extensions_block',
  TargetBlockType.executiveSummaryBlock: 'executive_summary_block',
  TargetBlockType.metadataBlock: 'metadata_block',
  TargetBlockType.synthesisTextBlock: 'synthesis_text_block',
  TargetBlockType.matrixGraphsBlock: 'matrix_graphs_block',
  TargetBlockType.matrixSummaryTableBlock: 'matrix_summary_table_block',
  TargetBlockType.varianceValidationBlock: 'variance_validation_block',
  TargetBlockType.authenticityEvaluationBlock: 'authenticity_evaluation_block',
};

const _$SourcesDisplayModeEnumMap = {
  SourcesDisplayMode.verifiedEvidence: 'verified_evidence',
  SourcesDisplayMode.simpleBibliography: 'simple_bibliography',
};
