// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'json_schema.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_JsonSchema _$JsonSchemaFromJson(Map<String, dynamic> json) => _JsonSchema(
  type: json['type'] as String?,
  title: json['title'] as String?,
  description: json['description'] as String?,
  properties: (json['properties'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, JsonSchema.fromJson(e as Map<String, dynamic>)),
  ),
  items:
      json['items'] == null
          ? null
          : JsonSchema.fromJson(json['items'] as Map<String, dynamic>),
  required:
      (json['required'] as List<dynamic>?)?.map((e) => e as String).toList(),
  enumValues: json['enum'] as List<dynamic>?,
  minLength: (json['minLength'] as num?)?.toInt(),
  maxLength: (json['maxLength'] as num?)?.toInt(),
  minimum: (json['minimum'] as num?)?.toDouble(),
  maximum: (json['maximum'] as num?)?.toDouble(),
  uiWidget: json['x-ui-widget'] as String?,
  uiGroup: json['x-ui-group'] as String?,
);

Map<String, dynamic> _$JsonSchemaToJson(_JsonSchema instance) =>
    <String, dynamic>{
      'type': instance.type,
      'title': instance.title,
      'description': instance.description,
      'properties': instance.properties,
      'items': instance.items,
      'required': instance.required,
      'enum': instance.enumValues,
      'minLength': instance.minLength,
      'maxLength': instance.maxLength,
      'minimum': instance.minimum,
      'maximum': instance.maximum,
      'x-ui-widget': instance.uiWidget,
      'x-ui-group': instance.uiGroup,
    };
