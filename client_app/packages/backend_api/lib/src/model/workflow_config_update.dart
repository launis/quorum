//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_config_update.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowConfigUpdate {
  /// Returns a new [WorkflowConfigUpdate] instance.
  WorkflowConfigUpdate({
    this.steps,

    this.sequence,

    this.description,

    this.defaultModelMapping,
  });

  @JsonKey(name: r'steps', required: false)
  final List<Map<String, Object>>? steps;

  @JsonKey(name: r'sequence', required: false)
  final List<String>? sequence;

  @JsonKey(name: r'description', required: false)
  final String? description;

  @JsonKey(name: r'default_model_mapping', required: false)
  final Map<String, String>? defaultModelMapping;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WorkflowConfigUpdate &&
          other.steps == steps &&
          other.sequence == sequence &&
          other.description == description &&
          other.defaultModelMapping == defaultModelMapping;

  @override
  int get hashCode =>
      (steps == null ? 0 : steps.hashCode) +
      (sequence == null ? 0 : sequence.hashCode) +
      (description == null ? 0 : description.hashCode) +
      (defaultModelMapping == null ? 0 : defaultModelMapping.hashCode);

  factory WorkflowConfigUpdate.fromJson(Map<String, dynamic> json) =>
      _$WorkflowConfigUpdateFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowConfigUpdateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
