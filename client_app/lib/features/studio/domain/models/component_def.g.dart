// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'component_def.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_OntologyDimension _$OntologyDimensionFromJson(Map<String, dynamic> json) =>
    _OntologyDimension(
      id: json['id'] as String,
      name: json['label'] as String,
      description: json['description'] as String,
      isSystem: json['is_system'] as bool? ?? false,
    );

Map<String, dynamic> _$OntologyDimensionToJson(_OntologyDimension instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.name,
      'description': instance.description,
      'is_system': instance.isSystem,
    };

_MatrixCriterion _$MatrixCriterionFromJson(Map<String, dynamic> json) =>
    _MatrixCriterion(
      dimensionId: json['id'] as String,
      label: json['label'] as String? ?? '',
      prompt: json['instruction'] as String? ?? '',
      anchors:
          (json['anchors'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as String),
          ) ??
          const {},
      weight: (json['weight'] as num?)?.toDouble() ?? 1.0,
    );

Map<String, dynamic> _$MatrixCriterionToJson(_MatrixCriterion instance) =>
    <String, dynamic>{
      'id': instance.dimensionId,
      'label': instance.label,
      'instruction': instance.prompt,
      'anchors': instance.anchors,
      'weight': instance.weight,
    };

_MatrixDef _$MatrixDefFromJson(Map<String, dynamic> json) => _MatrixDef(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String,
  scale: Map<String, int>.from(json['scale'] as Map),
  roleDescription: json['role_description'] as String?,
  criteria:
      (json['criteria'] as List<dynamic>?)
          ?.map((e) => MatrixCriterion.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$MatrixDefToJson(_MatrixDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'scale': instance.scale,
      'role_description': instance.roleDescription,
      'criteria': instance.criteria,
    };

_StudioComponentDef _$StudioComponentDefFromJson(Map<String, dynamic> json) =>
    _StudioComponentDef(
      id: json['id'] as String,
      slug: json['slug'] as String?,
      name: json['name'] as String?,
      type: json['type'] as String,
      description: json['description'] as String?,
      citation: json['citation'] as String?,
      content: json['content'],
    );

Map<String, dynamic> _$StudioComponentDefToJson(_StudioComponentDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'slug': instance.slug,
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'citation': instance.citation,
      'content': instance.content,
    };
