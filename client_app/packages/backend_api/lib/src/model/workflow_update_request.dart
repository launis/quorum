//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_update_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowUpdateRequest {
  /// Returns a new [WorkflowUpdateRequest] instance.
  WorkflowUpdateRequest({
    this.name,

    this.description = '',

    this.steps,

    this.uiSchema,

    this.defaultModelMapping,

    this.isPublic,

    this.status,

    this.version,

    this.scoringLogic,
  });

  @JsonKey(name: r'name', required: false)
  final String? name;

  /// New description.
  @JsonKey(defaultValue: '', name: r'description', required: false)
  final String? description;

  @JsonKey(name: r'steps', required: false)
  final List<String>? steps;

  @JsonKey(name: r'ui_schema', required: false)
  final Map<String, Object>? uiSchema;

  @JsonKey(name: r'default_model_mapping', required: false)
  final Map<String, String>? defaultModelMapping;

  @JsonKey(name: r'is_public', required: false)
  final bool? isPublic;

  @JsonKey(name: r'status', required: false)
  final String? status;

  @JsonKey(name: r'version', required: false)
  final int? version;

  @JsonKey(name: r'scoring_logic', required: false)
  final List<Map<String, Object>>? scoringLogic;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WorkflowUpdateRequest &&
          other.name == name &&
          other.description == description &&
          other.steps == steps &&
          other.uiSchema == uiSchema &&
          other.defaultModelMapping == defaultModelMapping &&
          other.isPublic == isPublic &&
          other.status == status &&
          other.version == version &&
          other.scoringLogic == scoringLogic;

  @override
  int get hashCode =>
      (name == null ? 0 : name.hashCode) +
      description.hashCode +
      (steps == null ? 0 : steps.hashCode) +
      (uiSchema == null ? 0 : uiSchema.hashCode) +
      (defaultModelMapping == null ? 0 : defaultModelMapping.hashCode) +
      (isPublic == null ? 0 : isPublic.hashCode) +
      (status == null ? 0 : status.hashCode) +
      (version == null ? 0 : version.hashCode) +
      (scoringLogic == null ? 0 : scoringLogic.hashCode);

  factory WorkflowUpdateRequest.fromJson(Map<String, dynamic> json) =>
      _$WorkflowUpdateRequestFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowUpdateRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
