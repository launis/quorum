// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'output_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SduiParagraphBlock _$SduiParagraphBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiParagraphBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['text', 'citations', 'exact_quotes', 'block_type'],
    );
    final val = SduiParagraphBlock(
      text: $checkedConvert('text', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiParagraphBlockToJson(SduiParagraphBlock instance) =>
    <String, dynamic>{
      'text': instance.text,
      'citations': instance.citations,
      'exact_quotes': instance.exactQuotes,
      'block_type': instance.$type,
    };

SduiBulletListBlock _$SduiBulletListBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiBulletListBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['items', 'block_type']);
      final val = SduiBulletListBlock(
        items: $checkedConvert(
          'items',
          (v) => (v as List<dynamic>)
              .map(
                (e) =>
                    SduiBulletListItemDTO.fromJson(e as Map<String, dynamic>),
              )
              .toList(),
        ),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiBulletListBlockToJson(
  SduiBulletListBlock instance,
) => <String, dynamic>{
  'items': instance.items.map((e) => e.toJson()).toList(),
  'block_type': instance.$type,
};

SduiAlertBoxBlock _$SduiAlertBoxBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiAlertBoxBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'text',
        'severity',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiAlertBoxBlock(
      text: $checkedConvert('text', (v) => v as String),
      severity: $checkedConvert('severity', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiAlertBoxBlockToJson(SduiAlertBoxBlock instance) =>
    <String, dynamic>{
      'text': instance.text,
      'severity': instance.severity,
      'citations': instance.citations,
      'exact_quotes': instance.exactQuotes,
      'block_type': instance.$type,
    };

SduiHeroInsightBlock _$SduiHeroInsightBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiHeroInsightBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['text', 'citations', 'exact_quotes', 'block_type'],
    );
    final val = SduiHeroInsightBlock(
      text: $checkedConvert('text', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiHeroInsightBlockToJson(
  SduiHeroInsightBlock instance,
) => <String, dynamic>{
  'text': instance.text,
  'citations': instance.citations,
  'exact_quotes': instance.exactQuotes,
  'block_type': instance.$type,
};

SduiMarkdownBlock _$SduiMarkdownBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiMarkdownBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['text', 'block_type']);
      final val = SduiMarkdownBlock(
        text: $checkedConvert('text', (v) => v as String),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiMarkdownBlockToJson(SduiMarkdownBlock instance) =>
    <String, dynamic>{'text': instance.text, 'block_type': instance.$type};

_SduiBulletListItemDTO _$SduiBulletListItemDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SduiBulletListItemDTO', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['text', 'citations', 'exact_quotes']);
  final val = _SduiBulletListItemDTO(
    text: $checkedConvert('text', (v) => v as String),
    citations: $checkedConvert(
      'citations',
      (v) =>
          (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
          const [],
    ),
    exactQuotes: $checkedConvert(
      'exact_quotes',
      (v) =>
          (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
    ),
  );
  return val;
}, fieldKeyMap: const {'exactQuotes': 'exact_quotes'});

Map<String, dynamic> _$SduiBulletListItemDTOToJson(
  _SduiBulletListItemDTO instance,
) => <String, dynamic>{
  'text': instance.text,
  'citations': instance.citations,
  'exact_quotes': instance.exactQuotes,
};

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
        'synthesis',
        'synthesis_blocks',
        'strictness_level',
        'scoring_strategy',
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
        (v) => v as String? ?? 'full',
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
    );
    return val;
  },
  fieldKeyMap: const {
    'presetView': 'preset_view',
    'targetBlocks': 'target_blocks',
    'textDeliveryMode': 'text_delivery_mode',
    'synthesisBlocks': 'synthesis_blocks',
    'strictnessLevel': 'strictness_level',
    'scoringStrategy': 'scoring_strategy',
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
  'text_delivery_mode': instance.textDeliveryMode,
  'synthesis': instance.synthesis?.toJson(),
  'synthesis_blocks': instance.synthesisBlocks.map((e) => e.toJson()).toList(),
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
};

const _$PresetViewEnumMap = {
  PresetView.metrics1d: '1d_metrics',
  PresetView.compare2d: '2d_compare',
  PresetView.complex3d: '3d_complex',
  PresetView.matrix3d: '3d_matrix',
  PresetView.textOnly: 'text_only',
  PresetView.defaultView: 'default',
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
            'matrix_visible_columns',
            'model_strategy',
            'tone_instruction',
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
            (v) => v as String? ?? 'DISABLED',
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
          matrixVisibleColumns: $checkedConvert(
            'matrix_visible_columns',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const ['label', 'score', 'distribution', 'row_explanation'],
          ),
          modelStrategy: $checkedConvert('model_strategy', (v) => v as String?),
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
        'lengthConstraint': 'length_constraint',
        'preambleText': 'preamble_text',
        'historicalContextMode': 'historical_context_mode',
        'enablePiiMasking': 'enable_pii_masking',
        'allowedExports': 'allowed_exports',
        'omitEmptySections': 'omit_empty_sections',
        'allowedMcpTools': 'allowed_mcp_tools',
        'matrixVisibleColumns': 'matrix_visible_columns',
        'modelStrategy': 'model_strategy',
        'toneInstruction': 'tone_instruction',
      },
    );

Map<String, dynamic> _$SynthesisConfigDTOToJson(_SynthesisConfigDTO instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'historical_context_mode': instance.historicalContextMode,
      'enable_pii_masking': instance.enablePiiMasking,
      'allowed_exports': instance.allowedExports,
      'omit_empty_sections': instance.omitEmptySections,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'matrix_visible_columns': instance.matrixVisibleColumns,
      'model_strategy': instance.modelStrategy,
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
        'custom_preface',
        'visible_metadata',
        'visible_block_extensions',
        'visible_workflow_extensions',
        'max_extension_items',
        'display_scale',
        'synthesis',
        'include_diagnostic_scorecard',
        'strictness_level',
        'scoring_strategy',
        'tone_instruction',
        'language',
        'formatting_directives',
        'layouts',
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
      synthesis: $checkedConvert(
        'synthesis',
        (v) => v == null
            ? null
            : SynthesisConfigDTO.fromJson(v as Map<String, dynamic>),
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
      formattingDirectives: $checkedConvert(
        'formatting_directives',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
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
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'organizationId': 'organization_id',
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
    'formattingDirectives': 'formatting_directives',
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
  'synthesis': instance.synthesis?.toJson(),
  'include_diagnostic_scorecard': instance.includeDiagnosticScorecard,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
  'tone_instruction': instance.toneInstruction?.toJson(),
  'language': instance.language,
  'formatting_directives': instance.formattingDirectives,
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
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

_EmbeddedOutputProfile _$EmbeddedOutputProfileFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_EmbeddedOutputProfile',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'name',
        'description',
        'custom_preface',
        'visible_metadata',
        'visible_block_extensions',
        'visible_workflow_extensions',
        'max_extension_items',
        'display_scale',
        'synthesis',
        'include_diagnostic_scorecard',
        'strictness_level',
        'scoring_strategy',
        'tone_instruction',
        'language',
        'formatting_directives',
        'layouts',
      ],
    );
    final val = _EmbeddedOutputProfile(
      name: $checkedConvert(
        'name',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
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
      synthesis: $checkedConvert(
        'synthesis',
        (v) => v == null
            ? null
            : SynthesisConfigDTO.fromJson(v as Map<String, dynamic>),
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
      formattingDirectives: $checkedConvert(
        'formatting_directives',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
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
    );
    return val;
  },
  fieldKeyMap: const {
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
    'formattingDirectives': 'formatting_directives',
  },
);

Map<String, dynamic> _$EmbeddedOutputProfileToJson(
  _EmbeddedOutputProfile instance,
) => <String, dynamic>{
  'name': instance.name.toJson(),
  'description': instance.description?.toJson(),
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
  'synthesis': instance.synthesis?.toJson(),
  'include_diagnostic_scorecard': instance.includeDiagnosticScorecard,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
  'tone_instruction': instance.toneInstruction?.toJson(),
  'language': instance.language,
  'formatting_directives': instance.formattingDirectives,
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
};
