//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'builder_workflow_create_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BuilderWorkflowCreateRequest {
  /// Returns a new [BuilderWorkflowCreateRequest] instance.
  BuilderWorkflowCreateRequest({
    required this.name,

    this.description = '',

    this.steps = const [],

    this.defaultModelMapping,

    this.uiSchema,

    this.isPublic = false,

    this.status = 'draft',

    this.version = 1,

    this.scoringLogic = const [],
  });

  /// Name of the new workflow.
  @JsonKey(name: r'name', required: true)
  final String name;

  /// Optional description.
  @JsonKey(defaultValue: '', name: r'description', required: false)
  final String? description;

  /// List of step IDs.
  @JsonKey(defaultValue: [], name: r'steps', required: false)
  final List<String>? steps;

  @JsonKey(name: r'default_model_mapping', required: false)
  final Map<String, String>? defaultModelMapping;

  @JsonKey(name: r'ui_schema', required: false)
  final Map<String, Object>? uiSchema;

  /// If True, visible to all tenants (System Only).
  @JsonKey(defaultValue: false, name: r'is_public', required: false)
  final bool? isPublic;

  /// Lifecycle status.
  @JsonKey(defaultValue: 'draft', name: r'status', required: false)
  final String? status;

  /// Version number.
  @JsonKey(defaultValue: 1, name: r'version', required: false)
  final int? version;

  /// Scoring configuration.
  @JsonKey(defaultValue: [], name: r'scoring_logic', required: false)
  final List<Map<String, Object>>? scoringLogic;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BuilderWorkflowCreateRequest &&
          other.name == name &&
          other.description == description &&
          other.steps == steps &&
          other.defaultModelMapping == defaultModelMapping &&
          other.uiSchema == uiSchema &&
          other.isPublic == isPublic &&
          other.status == status &&
          other.version == version &&
          other.scoringLogic == scoringLogic;

  @override
  int get hashCode =>
      name.hashCode +
      description.hashCode +
      steps.hashCode +
      (defaultModelMapping == null ? 0 : defaultModelMapping.hashCode) +
      (uiSchema == null ? 0 : uiSchema.hashCode) +
      isPublic.hashCode +
      status.hashCode +
      version.hashCode +
      scoringLogic.hashCode;

  factory BuilderWorkflowCreateRequest.fromJson(Map<String, dynamic> json) =>
      _$BuilderWorkflowCreateRequestFromJson(json);

  Map<String, dynamic> toJson() => _$BuilderWorkflowCreateRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
