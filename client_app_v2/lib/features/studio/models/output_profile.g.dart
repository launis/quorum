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
      ],
    );
    final val = _OutputLayoutBlock(
      presetView: $checkedConvert(
        'preset_view',
        (v) => v as String? ?? 'default',
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
    );
    return val;
  },
  fieldKeyMap: const {
    'presetView': 'preset_view',
    'targetBlocks': 'target_blocks',
    'textDeliveryMode': 'text_delivery_mode',
    'synthesisMd': 'synthesis_md',
  },
);

Map<String, dynamic> _$OutputLayoutBlockToJson(_OutputLayoutBlock instance) =>
    <String, dynamic>{
      'preset_view': instance.presetView,
      'title': instance.title?.toJson(),
      'description': instance.description?.toJson(),
      'steps': instance.steps,
      'target_blocks': instance.targetBlocks,
      'text_delivery_mode': instance.textDeliveryMode,
      'synthesis': instance.synthesis?.toJson(),
      'synthesis_md': instance.synthesisMd,
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
            'include_historical_summary',
            'enable_pii_masking',
            'allowed_exports',
            'omit_empty_sections',
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
          includeHistoricalSummary: $checkedConvert(
            'include_historical_summary',
            (v) => v as bool? ?? false,
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
        );
        return val;
      },
      fieldKeyMap: const {
        'systemPrompt': 'system_prompt',
        'lengthConstraint': 'length_constraint',
        'preambleText': 'preamble_text',
        'includeHistoricalSummary': 'include_historical_summary',
        'enablePiiMasking': 'enable_pii_masking',
        'allowedExports': 'allowed_exports',
        'omitEmptySections': 'omit_empty_sections',
      },
    );

Map<String, dynamic> _$SynthesisConfigDTOToJson(_SynthesisConfigDTO instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'include_historical_summary': instance.includeHistoricalSummary,
      'enable_pii_masking': instance.enablePiiMasking,
      'allowed_exports': instance.allowedExports,
      'omit_empty_sections': instance.omitEmptySections,
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
            'name',
            'description',
            'visible_metadata',
            'visible_extensions',
            'max_extension_items',
            'display_scale',
            'synthesis',
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
        'visibleMetadata': 'visible_metadata',
        'visibleExtensions': 'visible_extensions',
        'maxExtensionItems': 'max_extension_items',
        'displayScale': 'display_scale',
      },
    );

Map<String, dynamic> _$OutputProfileToJson(
  _OutputProfile instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'slug': instance.slug,
  'workflow_id': const StrictOpaqueIdConverter().toJson(instance.workflowId),
  'name': instance.name.toJson(),
  'description': instance.description?.toJson(),
  'visible_metadata': instance.visibleMetadata,
  'visible_extensions': instance.visibleExtensions
      .map((e) => _$XaiExtensionTypeEnumMap[e]!)
      .toList(),
  'max_extension_items': instance.maxExtensionItems,
  'display_scale': instance.displayScale,
  'synthesis': instance.synthesis?.toJson(),
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
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
};
