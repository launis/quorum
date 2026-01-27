// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'component_def.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_StudioComponentDef _$StudioComponentDefFromJson(Map<String, dynamic> json) =>
    _StudioComponentDef(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      description: json['description'] as String?,
      content: json['content'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$StudioComponentDefToJson(_StudioComponentDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'content': instance.content,
    };
