//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_config_create.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowConfigCreate {
  /// Returns a new [WorkflowConfigCreate] instance.
  WorkflowConfigCreate({
    this.id,

    this.slug,

    required this.name,

    this.sequence = const [],

    this.description,

    this.defaultModelMapping,
  });

  /// New Workflow UUID
  @JsonKey(name: r'id', required: false)
  final String? id;

  @JsonKey(name: r'slug', required: false)
  final String? slug;

  /// Workflow Name
  @JsonKey(name: r'name', required: true)
  final String name;

  /// List of Step IDs
  @JsonKey(defaultValue: [], name: r'sequence', required: false)
  final List<String>? sequence;

  @JsonKey(name: r'description', required: false)
  final String? description;

  @JsonKey(name: r'default_model_mapping', required: false)
  final Map<String, String>? defaultModelMapping;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WorkflowConfigCreate &&
          other.id == id &&
          other.slug == slug &&
          other.name == name &&
          other.sequence == sequence &&
          other.description == description &&
          other.defaultModelMapping == defaultModelMapping;

  @override
  int get hashCode =>
      id.hashCode +
      (slug == null ? 0 : slug.hashCode) +
      name.hashCode +
      sequence.hashCode +
      (description == null ? 0 : description.hashCode) +
      (defaultModelMapping == null ? 0 : defaultModelMapping.hashCode);

  factory WorkflowConfigCreate.fromJson(Map<String, dynamic> json) =>
      _$WorkflowConfigCreateFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowConfigCreateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
