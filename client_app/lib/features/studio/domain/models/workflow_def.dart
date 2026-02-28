// ignore_for_file: invalid_annotation_target
import 'package:flutter/foundation.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_def.freezed.dart';
part 'workflow_def.g.dart';

@freezed
abstract class WorkflowDef with _$WorkflowDef {
  const factory WorkflowDef({
    required String id,
    String? slug,
    required String name,
    required String description,
    @Default([]) List<WorkflowStepDef> steps,
    @Default([])
    @JsonKey(name: 'scoring_logic')
    List<ScoringLogic> scoringLogic,
    @Default({}) @JsonKey(name: 'ui_schema') Map<String, dynamic> uiSchema,
  }) = _WorkflowDef;

  factory WorkflowDef.fromJson(Map<String, dynamic> json) =>
      _$WorkflowDefFromJson(json);
}

@freezed
abstract class WorkflowStepDef with _$WorkflowStepDef {
  const factory WorkflowStepDef({
    required String id,
    String? slug,
    @Default('') String name,
    @JsonKey(name: 'task_key') required String taskKey,
    @Default({}) Map<String, dynamic> config,
  }) = _WorkflowStepDef;

  factory WorkflowStepDef.fromJson(Map<String, dynamic> json) =>
      _$WorkflowStepDefFromJson(json);
}

@freezed
abstract class ComponentScoringRule with _$ComponentScoringRule {
  const factory ComponentScoringRule({
    @JsonKey(name: 'component_id') required String componentId,
    @Default(1.0) double weight,
    @JsonKey(name: 'metric_key') required String metricKey,
  }) = _ComponentScoringRule;

  factory ComponentScoringRule.fromJson(Map<String, dynamic> json) =>
      _$ComponentScoringRuleFromJson(json);
}

@freezed
abstract class ScoringLogic with _$ScoringLogic {
  const factory ScoringLogic({
    required String label,
    @Default([]) List<ComponentScoringRule> rules,
  }) = _ScoringLogic;

  factory ScoringLogic.fromJson(Map<String, dynamic> json) =>
      _$ScoringLogicFromJson(json);
}

@freezed
abstract class ComponentDef with _$ComponentDef {
  const factory ComponentDef({
    required String id,
    String? slug,
    required String name,
    required String type,
    String? description,
    dynamic content,
    String? citation,
  }) = _ComponentDef;

  factory ComponentDef.fromJson(Map<String, dynamic> json) =>
      _$ComponentDefFromJson(json);
}
