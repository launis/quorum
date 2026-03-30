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
        'show_text',
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
      showText: $checkedConvert('show_text', (v) => v as bool? ?? true),
    );
    return val;
  },
  fieldKeyMap: const {
    'presetView': 'preset_view',
    'targetBlocks': 'target_blocks',
    'showText': 'show_text',
  },
);

Map<String, dynamic> _$OutputLayoutBlockToJson(_OutputLayoutBlock instance) =>
    <String, dynamic>{
      'preset_view': instance.presetView,
      'title': instance.title?.toJson(),
      'description': instance.description?.toJson(),
      'steps': instance.steps,
      'target_blocks': instance.targetBlocks,
      'show_text': instance.showText,
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
            'display_scale',
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
            (v) => I18nText.fromJson(v as Map<String, dynamic>),
          ),
          displayScale: $checkedConvert(
            'display_scale',
            (v) => v as String? ?? 'original',
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
  'description': instance.description.toJson(),
  'display_scale': instance.displayScale,
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
};

_EmbeddedOutputProfile _$EmbeddedOutputProfileFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_EmbeddedOutputProfile',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['name', 'display_scale', 'layouts']);
    final val = _EmbeddedOutputProfile(
      name: $checkedConvert(
        'name',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      displayScale: $checkedConvert(
        'display_scale',
        (v) => v as String? ?? 'original',
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
  fieldKeyMap: const {'displayScale': 'display_scale'},
);

Map<String, dynamic> _$EmbeddedOutputProfileToJson(
  _EmbeddedOutputProfile instance,
) => <String, dynamic>{
  'name': instance.name.toJson(),
  'display_scale': instance.displayScale,
  'layouts': instance.layouts.map((e) => e.toJson()).toList(),
};
