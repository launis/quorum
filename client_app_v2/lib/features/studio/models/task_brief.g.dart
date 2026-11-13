// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'task_brief.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TaskBrief _$TaskBriefFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_TaskBrief',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'organization_id',
        'label',
        'description',
        'instruction_text',
        'source_url',
      ],
    );
    final val = _TaskBrief(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      organizationId: $checkedConvert(
        'organization_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      instructionText: $checkedConvert('instruction_text', (v) => v as String?),
      sourceUrl: $checkedConvert('source_url', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'instructionText': 'instruction_text',
    'sourceUrl': 'source_url',
  },
);

Map<String, dynamic> _$TaskBriefToJson(_TaskBrief instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'organization_id': const StrictOpaqueIdConverter().toJson(
        instance.organizationId,
      ),
      'label': instance.label.toJson(),
      'description': instance.description.toJson(),
      'instruction_text': instance.instructionText,
      'source_url': instance.sourceUrl,
    };
