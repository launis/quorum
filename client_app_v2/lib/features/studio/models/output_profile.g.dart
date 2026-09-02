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
      allowedKeys: const ['id', 'title', 'target_blocks', 'view_type'],
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
      viewType: $checkedConvert(
        'view_type',
        (v) =>
            $enumDecodeNullable(_$PresetViewEnumMap, v) ?? PresetView.metrics1d,
      ),
    );
    return val;
  },
  fieldKeyMap: const {'targetBlocks': 'target_blocks', 'viewType': 'view_type'},
);

Map<String, dynamic> _$MatrixSynthesisGroupToJson(
  _MatrixSynthesisGroup instance,
) => <String, dynamic>{
  'id': instance.id,
  'title': instance.title.toJson(),
  'target_blocks': instance.targetBlocks,
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
        'synthesis_length_constraint',
        'max_quotes_per_matrix',
        'max_unmet_criteria',
        'tone_instruction',
        'executive_summary_directive',
        'matrix_1d_synthesis_directive',
        'matrix_2d_synthesis_directive',
        'matrix_3d_synthesis_directive',
        'matrix_text_synthesis_directive',
        'row_explanation_directive',
        'xai_synthesis_directive',
        'variance_synthesis_directive',
        'language',
        'matrix_synthesis_groups',
        'content_blocks',
        'target_block_order',
        'show_sources_summary_box',
        'sources_display_mode',
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
      synthesisLengthConstraint: $checkedConvert(
        'synthesis_length_constraint',
        (v) => (v as num?)?.toInt(),
      ),
      maxQuotesPerMatrix: $checkedConvert(
        'max_quotes_per_matrix',
        (v) => (v as num?)?.toInt(),
      ),
      maxUnmetCriteria: $checkedConvert(
        'max_unmet_criteria',
        (v) => (v as num?)?.toInt(),
      ),
      toneInstruction: $checkedConvert(
        'tone_instruction',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      executiveSummaryDirective: $checkedConvert(
        'executive_summary_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      matrix1dSynthesisDirective: $checkedConvert(
        'matrix_1d_synthesis_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      matrix2dSynthesisDirective: $checkedConvert(
        'matrix_2d_synthesis_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      matrix3dSynthesisDirective: $checkedConvert(
        'matrix_3d_synthesis_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      matrixTextSynthesisDirective: $checkedConvert(
        'matrix_text_synthesis_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      rowExplanationDirective: $checkedConvert(
        'row_explanation_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      xaiSynthesisDirective: $checkedConvert(
        'xai_synthesis_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      varianceSynthesisDirective: $checkedConvert(
        'variance_synthesis_directive',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      language: $checkedConvert(
        'language',
        (v) => $enumDecodeNullable(_$SystemLocaleEnumMap, v),
      ),
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
              TargetBlockType.synthesisTextBlock,
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
    'synthesisLengthConstraint': 'synthesis_length_constraint',
    'maxQuotesPerMatrix': 'max_quotes_per_matrix',
    'maxUnmetCriteria': 'max_unmet_criteria',
    'toneInstruction': 'tone_instruction',
    'executiveSummaryDirective': 'executive_summary_directive',
    'matrix1dSynthesisDirective': 'matrix_1d_synthesis_directive',
    'matrix2dSynthesisDirective': 'matrix_2d_synthesis_directive',
    'matrix3dSynthesisDirective': 'matrix_3d_synthesis_directive',
    'matrixTextSynthesisDirective': 'matrix_text_synthesis_directive',
    'rowExplanationDirective': 'row_explanation_directive',
    'xaiSynthesisDirective': 'xai_synthesis_directive',
    'varianceSynthesisDirective': 'variance_synthesis_directive',
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
  'synthesis_length_constraint': instance.synthesisLengthConstraint,
  'max_quotes_per_matrix': instance.maxQuotesPerMatrix,
  'max_unmet_criteria': instance.maxUnmetCriteria,
  'tone_instruction': instance.toneInstruction?.toJson(),
  'executive_summary_directive': instance.executiveSummaryDirective?.toJson(),
  'matrix_1d_synthesis_directive': instance.matrix1dSynthesisDirective
      ?.toJson(),
  'matrix_2d_synthesis_directive': instance.matrix2dSynthesisDirective
      ?.toJson(),
  'matrix_3d_synthesis_directive': instance.matrix3dSynthesisDirective
      ?.toJson(),
  'matrix_text_synthesis_directive': instance.matrixTextSynthesisDirective
      ?.toJson(),
  'row_explanation_directive': instance.rowExplanationDirective?.toJson(),
  'xai_synthesis_directive': instance.xaiSynthesisDirective?.toJson(),
  'variance_synthesis_directive': instance.varianceSynthesisDirective?.toJson(),
  'language': _$SystemLocaleEnumMap[instance.language],
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

const _$SystemLocaleEnumMap = {SystemLocale.en: 'en', SystemLocale.fi: 'fi'};

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
