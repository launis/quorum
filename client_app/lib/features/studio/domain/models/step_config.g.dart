// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_StepConfig _$StepConfigFromJson(Map<String, dynamic> json) => _StepConfig(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String?,
  taskKey: json['task_key'] as String? ?? 'analyst',
  config: json['config'] as Map<String, dynamic>? ?? const {},
);

Map<String, dynamic> _$StepConfigToJson(_StepConfig instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'task_key': instance.taskKey,
      'config': instance.config,
    };
