// ignore_for_file: invalid_annotation_target
import 'package:flutter/foundation.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_def.freezed.dart';
part 'workflow_def.g.dart';

@freezed
abstract class WorkflowDef with _$WorkflowDef {
  const factory WorkflowDef({
    required String id,
    required String name,
    required String description,
    @Default([]) List<WorkflowStepDef> steps,
  }) = _WorkflowDef;

  factory WorkflowDef.fromJson(Map<String, dynamic> json) => _$WorkflowDefFromJson(json);
}

@freezed
abstract class WorkflowStepDef with _$WorkflowStepDef {
  const factory WorkflowStepDef({
    required String id,
    @Default('') String name,
    @JsonKey(name: 'task_key') required String taskKey,
    @Default({}) Map<String, dynamic> config,
  }) = _WorkflowStepDef;

  factory WorkflowStepDef.fromJson(Map<String, dynamic> json) => _$WorkflowStepDefFromJson(json);
}
