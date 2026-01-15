// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Workflow _$WorkflowFromJson(Map<String, dynamic> json) => _Workflow(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String? ?? '',
  steps:
      (json['steps'] as List<dynamic>?)
          ?.map((e) => WorkflowStep.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  organizationId: json['organization_id'] as String?,
  isPublic: json['is_public'] as bool? ?? false,
  uiSchema: json['ui_schema'] as Map<String, dynamic>?,
);

Map<String, dynamic> _$WorkflowToJson(_Workflow instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'description': instance.description,
  'steps': instance.steps,
  'organization_id': instance.organizationId,
  'is_public': instance.isPublic,
  'ui_schema': instance.uiSchema,
};
