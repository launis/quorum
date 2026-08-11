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
        'synthesis',
        'synthesis_blocks',
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
            $enumDecodeNullable(
              _$PresetViewEnumMap,
              v,
              unknownValue: PresetView.defaultView,
            ) ??
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
            $enumDecodeNullable(
              _$TextDeliveryModeEnumMap,
              v,
              unknownValue: TextDeliveryMode.full,
            ) ??
            TextDeliveryMode.full,
      ),
      isSynthesisEnabled: $checkedConvert(
        'is_synthesis_enabled',
        (v) => v as bool? ?? true,
      ),
      synthesis: $checkedConvert(
        'synthesis',
        (v) => v == null
            ? null
            : SynthesisConfigDTO.fromJson(v as Map<String, dynamic>),
      ),
      synthesisBlocks: $checkedConvert(
        'synthesis_blocks',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
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
    'synthesisBlocks': 'synthesis_blocks',
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
  'synthesis': instance.synthesis?.toJson(),
  'synthesis_blocks': instance.synthesisBlocks.map((e) => e.toJson()).toList(),
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
            'length_constraint',
            'preamble_text',
            'historical_context_mode',
            'enable_pii_masking',
            'allowed_exports',
            'omit_empty_sections',
            'allowed_mcp_tools',
            'model_strategy',
            'tone_instruction',
            'synthesis_block_id',
            'row_explanations_block_id',
          ],
        );
        final val = _SynthesisConfigDTO(
          systemPrompt: $checkedConvert('system_prompt', (v) => v as String?),
          lengthConstraint: $checkedConvert(
            'length_constraint',
            (v) => (v as num?)?.toInt(),
          ),
          preambleText: $checkedConvert(
            'preamble_text',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          historicalContextMode: $checkedConvert(
            'historical_context_mode',
            (v) =>
                $enumDecodeNullable(
                  _$HistoricalContextModeEnumMap,
                  v,
                  unknownValue: HistoricalContextMode.disabled,
                ) ??
                HistoricalContextMode.disabled,
          ),
          enablePiiMasking: $checkedConvert(
            'enable_pii_masking',
            (v) => v as bool? ?? false,
          ),
          allowedExports: $checkedConvert(
            'allowed_exports',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const ['pdf', 'raw_json'],
          ),
          omitEmptySections: $checkedConvert(
            'omit_empty_sections',
            (v) => v as bool? ?? true,
          ),
          allowedMcpTools: $checkedConvert(
            'allowed_mcp_tools',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const [],
          ),
          modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
          toneInstruction: $checkedConvert(
            'tone_instruction',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          synthesisBlockId: $checkedConvert(
            'synthesis_block_id',
            (v) => v as String?,
          ),
          rowExplanationsBlockId: $checkedConvert(
            'row_explanations_block_id',
            (v) => v as String?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemPrompt': 'system_prompt',
        'lengthConstraint': 'length_constraint',
        'preambleText': 'preamble_text',
        'historicalContextMode': 'historical_context_mode',
        'enablePiiMasking': 'enable_pii_masking',
        'allowedExports': 'allowed_exports',
        'omitEmptySections': 'omit_empty_sections',
        'allowedMcpTools': 'allowed_mcp_tools',
        'modelStrategy': 'model_strategy',
        'toneInstruction': 'tone_instruction',
        'synthesisBlockId': 'synthesis_block_id',
        'rowExplanationsBlockId': 'row_explanations_block_id',
      },
    );

Map<String, dynamic> _$SynthesisConfigDTOToJson(_SynthesisConfigDTO instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'historical_context_mode':
          _$HistoricalContextModeEnumMap[instance.historicalContextMode]!,
      'enable_pii_masking': instance.enablePiiMasking,
      'allowed_exports': instance.allowedExports,
      'omit_empty_sections': instance.omitEmptySections,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'model_strategy': instance.modelStrategy,
      'tone_instruction': instance.toneInstruction?.toJson(),
      'synthesis_block_id': instance.synthesisBlockId,
      'row_explanations_block_id': instance.rowExplanationsBlockId,
    };

const _$HistoricalContextModeEnumMap = {
  HistoricalContextMode.disabled: 'DISABLED',
  HistoricalContextMode.slidingWindow3: 'SLIDING_WINDOW_3',
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
        'include_diagnostic_scorecard',
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
        (v) => (v as num?)?.toInt(),
      ),
      displayScale: $checkedConvert(
        'display_scale',
        (v) => v as String? ?? 'original',
      ),
      includeDiagnosticScorecard: $checkedConvert(
        'include_diagnostic_scorecard',
        (v) => v as bool? ?? false,
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
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const [
              'metadata_block',
              'executive_summary_block',
              'synthesis_text_block',
              'matrix_graphs_block',
              'grouped_extensions_block',
              'penalties_block',
              'matrix_summary_table_block',
              'variance_validation_block',
              'authenticity_evaluation_block',
              'printable_sources_block',
              'global_score_block',
              'audit_trail_block',
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
    'includeDiagnosticScorecard': 'include_diagnostic_scorecard',
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
  'display_scale': instance.displayScale,
  'include_diagnostic_scorecard': instance.includeDiagnosticScorecard,
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
  'target_block_order': instance.targetBlockOrder,
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
