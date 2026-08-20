// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'output_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_OutputLayoutBlock _$OutputLayoutBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_OutputLayoutBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'preset_view',
        'title',
        'description',
        'steps',
        'target_blocks',
        'text_delivery_mode',
        'is_synthesis_enabled',
        'strictness_level',
        'scoring_strategy',
        'matrix_column_labels',
        'matrix_visible_columns',
      ],
    );
    final val = _OutputLayoutBlock(
      presetView: $checkedConvert(
        'preset_view',
        (v) =>
            $enumDecodeNullable(_$PresetViewEnumMap, v) ??
            PresetView.defaultView,
      ),
      title: $checkedConvert(
        'title',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      steps: $checkedConvert(
        'steps',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      targetBlocks: $checkedConvert(
        'target_blocks',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      textDeliveryMode: $checkedConvert(
        'text_delivery_mode',
        (v) =>
            $enumDecodeNullable(_$TextDeliveryModeEnumMap, v) ??
            TextDeliveryMode.full,
      ),
      isSynthesisEnabled: $checkedConvert(
        'is_synthesis_enabled',
        (v) => v as bool? ?? true,
      ),
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt(),
      ),
      scoringStrategy: $checkedConvert(
        'scoring_strategy',
        (v) => $enumDecodeNullable(_$ScoringStrategyEnumMap, v),
      ),
      matrixColumnLabels: $checkedConvert(
        'matrix_column_labels',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
      matrixVisibleColumns: $checkedConvert(
        'matrix_visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'presetView': 'preset_view',
    'targetBlocks': 'target_blocks',
    'textDeliveryMode': 'text_delivery_mode',
    'isSynthesisEnabled': 'is_synthesis_enabled',
    'strictnessLevel': 'strictness_level',
    'scoringStrategy': 'scoring_strategy',
    'matrixColumnLabels': 'matrix_column_labels',
    'matrixVisibleColumns': 'matrix_visible_columns',
  },
);

Map<String, dynamic> _$OutputLayoutBlockToJson(
  _OutputLayoutBlock instance,
) => <String, dynamic>{
  'preset_view': _$PresetViewEnumMap[instance.presetView]!,
  'title': instance.title?.toJson(),
  'description': instance.description?.toJson(),
  'steps': instance.steps,
  'target_blocks': instance.targetBlocks,
  'text_delivery_mode': _$TextDeliveryModeEnumMap[instance.textDeliveryMode]!,
  'is_synthesis_enabled': instance.isSynthesisEnabled,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
  'matrix_column_labels': instance.matrixColumnLabels.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'matrix_visible_columns': instance.matrixVisibleColumns,
};

const _$PresetViewEnumMap = {
  PresetView.metrics1d: '1d_metrics',
  PresetView.compare2d: '2d_compare',
  PresetView.matrix3d: '3d_matrix',
  PresetView.textOnly: 'text_only',
  PresetView.defaultView: 'default',
  PresetView.matrixSummary: 'matrix_summary',
};

const _$TextDeliveryModeEnumMap = {
  TextDeliveryMode.full: 'full',
  TextDeliveryMode.titlesOnly: 'titles_only',
  TextDeliveryMode.none: 'none',
};

const _$ScoringStrategyEnumMap = {
  ScoringStrategy.waterfall: 'WATERFALL',
  ScoringStrategy.average: 'AVERAGE',
  ScoringStrategy.weightedAverage: 'WEIGHTED_AVERAGE',
  ScoringStrategy.pureMath: 'PURE_MATH',
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
        'visible_block_extensions',
        'visible_workflow_extensions',
        'max_extension_items',
        'display_scale',
        'strictness_level',
        'scoring_strategy',
        'tone_instruction',
        'language',
        'user_role_mappings',
        'extension_labels',
        'metric_mappings',
        'layouts',
        'content_blocks',
        'target_block_order',
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
            const ['date', 'organization'],
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
      userRoleMappings: $checkedConvert(
        'user_role_mappings',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
      extensionLabels: $checkedConvert(
        'extension_labels',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
      metricMappings: $checkedConvert(
        'metric_mappings',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
      layouts: $checkedConvert(
        'layouts',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => OutputLayoutBlock.fromJson(e as Map<String, dynamic>),
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
    'visibleBlockExtensions': 'visible_block_extensions',
    'visibleWorkflowExtensions': 'visible_workflow_extensions',
    'maxExtensionItems': 'max_extension_items',
    'displayScale': 'display_scale',
    'strictnessLevel': 'strictness_level',
    'scoringStrategy': 'scoring_strategy',
    'toneInstruction': 'tone_instruction',
    'userRoleMappings': 'user_role_mappings',
    'extensionLabels': 'extension_labels',
    'metricMappings': 'metric_mappings',
    'contentBlocks': 'content_blocks',
    'targetBlockOrder': 'target_block_order',
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
  'visible_block_extensions': instance.visibleBlockExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'visible_workflow_extensions': instance.visibleWorkflowExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'max_extension_items': instance.maxExtensionItems,
  'display_scale': _$DisplayScaleEnumMap[instance.displayScale]!,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
  'tone_instruction': instance.toneInstruction?.toJson(),
  'language': instance.language,
  'user_role_mappings': instance.userRoleMappings.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'extension_labels': instance.extensionLabels.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'metric_mappings': instance.metricMappings.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
  'content_blocks': instance.contentBlocks.map((e) => e.toJson()).toList(),
  'target_block_order': instance.targetBlockOrder
      .map((e) => _$TargetBlockTypeEnumMap[e]!)
      .toList(),
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
