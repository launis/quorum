//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'builder_workflow_delete_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BuilderWorkflowDeleteResponse {
  /// Returns a new [BuilderWorkflowDeleteResponse] instance.
  BuilderWorkflowDeleteResponse({
    required this.status,

    required this.deletedSteps,
  });

  @JsonKey(name: r'status', required: true)
  final String status;

  @JsonKey(name: r'deleted_steps', required: true)
  final List<String> deletedSteps;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BuilderWorkflowDeleteResponse &&
          other.status == status &&
          other.deletedSteps == deletedSteps;

  @override
  int get hashCode => status.hashCode + deletedSteps.hashCode;

  factory BuilderWorkflowDeleteResponse.fromJson(Map<String, dynamic> json) =>
      _$BuilderWorkflowDeleteResponseFromJson(json);

  Map<String, dynamic> toJson() => _$BuilderWorkflowDeleteResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
