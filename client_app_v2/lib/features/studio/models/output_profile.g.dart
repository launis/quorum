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
        'synthesis',
        'synthesis_md',
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
      synthesisMd: $checkedConvert('synthesis_md', (v) => v as String?),
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
    'synthesisMd': 'synthesis_md',
    'strictnessLevel': 'strictness_level',
    'scoringStrategy': 'scoring_strategy',
  },
);

Map<String, dynamic> _$OutputLayoutBlockToJson(_OutputLayoutBlock instance) =>
    <String, dynamic>{
      'preset_view': _$PresetViewEnumMap[instance.presetView]!,
      'title': instance.title?.toJson(),
      'description': instance.description?.toJson(),
      'steps': instance.steps,
      'target_blocks': instance.targetBlocks,
      'text_delivery_mode': instance.textDeliveryMode,
      'synthesis': instance.synthesis?.toJson(),
      'synthesis_md': instance.synthesisMd,
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
  ScoringStrategy.dampening: 'DAMPENING',
  ScoringStrategy.average: 'AVERAGE',
  ScoringStrategy.weightedAverage: 'WEIGHTED_AVERAGE',
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
            'row_explanation_prompt',
            'length_constraint',
            'preamble_text',
            'historical_context_mode',
            'enable_pii_masking',
            'allowed_exports',
            'omit_empty_sections',
            'allowed_mcp_tools',
            'matrix_visible_columns',
          ],
        );
        final val = _SynthesisConfigDTO(
          systemPrompt: $checkedConvert('system_prompt', (v) => v as String?),
          rowExplanationPrompt: $checkedConvert(
            'row_explanation_prompt',
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
        );
        return val;
      },
      fieldKeyMap: const {
        'systemPrompt': 'system_prompt',
        'rowExplanationPrompt': 'row_explanation_prompt',
        'lengthConstraint': 'length_constraint',
        'preambleText': 'preamble_text',
        'historicalContextMode': 'historical_context_mode',
        'enablePiiMasking': 'enable_pii_masking',
        'allowedExports': 'allowed_exports',
        'omitEmptySections': 'omit_empty_sections',
        'allowedMcpTools': 'allowed_mcp_tools',
        'matrixVisibleColumns': 'matrix_visible_columns',
      },
    );

Map<String, dynamic> _$SynthesisConfigDTOToJson(_SynthesisConfigDTO instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'row_explanation_prompt': instance.rowExplanationPrompt,
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'historical_context_mode': instance.historicalContextMode,
      'enable_pii_masking': instance.enablePiiMasking,
      'allowed_exports': instance.allowedExports,
      'omit_empty_sections': instance.omitEmptySections,
      'allowed_mcp_tools': instance.allowedMcpTools,
      'matrix_visible_columns': instance.matrixVisibleColumns,
    };

_OutputProfile _$OutputProfileFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
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
            'visible_metadata',
            'visible_extensions',
            'max_extension_items',
            'display_scale',
            'synthesis',
            'include_diagnostic_scorecard',
            'strictness_level',
            'scoring_strategy',
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
          organizationId: $checkedConvert(
            'organization_id',
            (v) => v as String?,
          ),
          name: $checkedConvert(
            'name',
            (v) => I18nText.fromJson(v as Map<String, dynamic>),
          ),
          description: $checkedConvert(
            'description',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          visibleMetadata: $checkedConvert(
            'visible_metadata',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const ['date', 'organization'],
          ),
          visibleExtensions: $checkedConvert(
            'visible_extensions',
            (v) => (v as List<dynamic>)
                .map((e) => $enumDecode(_$XaiExtensionTypeEnumMap, e))
                .toList(),
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
          layouts: $checkedConvert(
            'layouts',
            (v) =>
                (v as List<dynamic>?)
                    ?.map(
                      (e) =>
                          OutputLayoutBlock.fromJson(e as Map<String, dynamic>),
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
        'visibleMetadata': 'visible_metadata',
        'visibleExtensions': 'visible_extensions',
        'maxExtensionItems': 'max_extension_items',
        'displayScale': 'display_scale',
        'includeDiagnosticScorecard': 'include_diagnostic_scorecard',
        'strictnessLevel': 'strictness_level',
        'scoringStrategy': 'scoring_strategy',
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
  'visible_metadata': instance.visibleMetadata,
  'visible_extensions': instance.visibleExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'max_extension_items': instance.maxExtensionItems,
  'display_scale': instance.displayScale,
  'synthesis': instance.synthesis?.toJson(),
  'include_diagnostic_scorecard': instance.includeDiagnosticScorecard,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
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
        'visible_metadata',
        'visible_extensions',
        'max_extension_items',
        'display_scale',
        'synthesis',
        'include_diagnostic_scorecard',
        'strictness_level',
        'scoring_strategy',
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
      visibleMetadata: $checkedConvert(
        'visible_metadata',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const ['date', 'organization'],
      ),
      visibleExtensions: $checkedConvert(
        'visible_extensions',
        (v) => (v as List<dynamic>)
            .map((e) => $enumDecode(_$XaiExtensionTypeEnumMap, e))
            .toList(),
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
    'visibleMetadata': 'visible_metadata',
    'visibleExtensions': 'visible_extensions',
    'maxExtensionItems': 'max_extension_items',
    'displayScale': 'display_scale',
    'includeDiagnosticScorecard': 'include_diagnostic_scorecard',
    'strictnessLevel': 'strictness_level',
    'scoringStrategy': 'scoring_strategy',
  },
);

Map<String, dynamic> _$EmbeddedOutputProfileToJson(
  _EmbeddedOutputProfile instance,
) => <String, dynamic>{
  'name': instance.name.toJson(),
  'description': instance.description?.toJson(),
  'visible_metadata': instance.visibleMetadata,
  'visible_extensions': instance.visibleExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'max_extension_items': instance.maxExtensionItems,
  'display_scale': instance.displayScale,
  'synthesis': instance.synthesis?.toJson(),
  'include_diagnostic_scorecard': instance.includeDiagnosticScorecard,
  'strictness_level': instance.strictnessLevel,
  'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
};
