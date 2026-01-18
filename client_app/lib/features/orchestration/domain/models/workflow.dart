import 'package:client_app/features/orchestration/domain/models/workflow_step.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow.freezed.dart';
part 'workflow.g.dart';

@freezed
sealed class Workflow with _$Workflow {
  const factory Workflow({
    required String id,
    required String name,
    @Default('') String description,
    @Default([]) List<WorkflowStep> steps,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'is_public') @Default(false) bool isPublic,
    @JsonKey(name: 'ui_schema') Map<String, dynamic>? uiSchema,
  }) = _Workflow;

  factory Workflow.fromJson(Map<String, dynamic> json) =>
      _$WorkflowFromJson(json);
}


