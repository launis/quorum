// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_step.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WorkflowStep _$WorkflowStepFromJson(Map<String, dynamic> json) =>
    _WorkflowStep(
      id: json['id'] as String,
      slug: json['slug'] as String?,
      name: json['name'] as String? ?? 'Unnamed Step',
      taskKey: json['task_key'] as String,
      inputs:
          (json['inputs'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as String),
          ) ??
          const {},
      config: json['config'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$WorkflowStepToJson(_WorkflowStep instance) =>
    <String, dynamic>{
      'id': instance.id,
      'slug': instance.slug,
      'name': instance.name,
      'task_key': instance.taskKey,
      'inputs': instance.inputs,
      'config': instance.config,
    };
