// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_def.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WorkflowDef _$WorkflowDefFromJson(Map<String, dynamic> json) => _WorkflowDef(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String,
  steps:
      (json['steps'] as List<dynamic>?)
          ?.map((e) => WorkflowStepDef.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$WorkflowDefToJson(_WorkflowDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'steps': instance.steps,
    };

_WorkflowStepDef _$WorkflowStepDefFromJson(Map<String, dynamic> json) =>
    _WorkflowStepDef(
      id: json['id'] as String,
      name: json['name'] as String? ?? '',
      taskKey: json['task_key'] as String,
      config: json['config'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$WorkflowStepDefToJson(_WorkflowStepDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'task_key': instance.taskKey,
      'config': instance.config,
    };
