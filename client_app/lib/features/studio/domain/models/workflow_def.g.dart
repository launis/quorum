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
  scoringLogic:
      (json['scoring_logic'] as List<dynamic>?)
          ?.map((e) => ScoringLogic.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  uiSchema: json['ui_schema'] as Map<String, dynamic>? ?? const {},
);

Map<String, dynamic> _$WorkflowDefToJson(_WorkflowDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'steps': instance.steps,
      'scoring_logic': instance.scoringLogic,
      'ui_schema': instance.uiSchema,
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

_ComponentScoringRule _$ComponentScoringRuleFromJson(
  Map<String, dynamic> json,
) => _ComponentScoringRule(
  componentId: json['component_id'] as String,
  weight: (json['weight'] as num?)?.toDouble() ?? 1.0,
  metricKey: json['metric_key'] as String,
);

Map<String, dynamic> _$ComponentScoringRuleToJson(
  _ComponentScoringRule instance,
) => <String, dynamic>{
  'component_id': instance.componentId,
  'weight': instance.weight,
  'metric_key': instance.metricKey,
};

_ScoringLogic _$ScoringLogicFromJson(Map<String, dynamic> json) =>
    _ScoringLogic(
      label: json['label'] as String,
      rules:
          (json['rules'] as List<dynamic>?)
              ?.map(
                (e) => ComponentScoringRule.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const [],
    );

Map<String, dynamic> _$ScoringLogicToJson(_ScoringLogic instance) =>
    <String, dynamic>{'label': instance.label, 'rules': instance.rules};

_ComponentDef _$ComponentDefFromJson(Map<String, dynamic> json) =>
    _ComponentDef(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      description: json['description'] as String?,
      content: json['content'],
      citation: json['citation'] as String?,
    );

Map<String, dynamic> _$ComponentDefToJson(_ComponentDef instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'content': instance.content,
      'citation': instance.citation,
    };
