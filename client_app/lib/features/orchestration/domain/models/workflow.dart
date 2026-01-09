import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow.freezed.dart';
part 'workflow.g.dart';

@freezed
sealed class Workflow with _$Workflow {
  const factory Workflow({
    required String id,
    required String name,
    @Default('') String description,
    @Default([]) List<String> steps,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'is_public') @Default(false) bool isPublic,
  }) = _Workflow;

  factory Workflow.fromJson(Map<String, dynamic> json) =>
      _$WorkflowFromJson(json);
}
