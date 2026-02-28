//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'step_dto.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class StepDTO {
  /// Returns a new [StepDTO] instance.
  StepDTO({
    required this.id,

    this.name,

    required this.taskKey,

    this.description,

    this.config,

    this.inputs = const {},
  });

  @JsonKey(name: r'id', required: true)
  final String id;

  @JsonKey(name: r'name', required: false)
  final String? name;

  @JsonKey(name: r'task_key', required: true)
  final String taskKey;

  @JsonKey(name: r'description', required: false)
  final String? description;

  @JsonKey(name: r'config', required: false)
  final Map<String, Object>? config;

  @JsonKey(defaultValue: {}, name: r'inputs', required: false)
  final Map<String, String>? inputs;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is StepDTO &&
          other.id == id &&
          other.name == name &&
          other.taskKey == taskKey &&
          other.description == description &&
          other.config == config &&
          other.inputs == inputs;

  @override
  int get hashCode =>
      id.hashCode +
      (name == null ? 0 : name.hashCode) +
      taskKey.hashCode +
      (description == null ? 0 : description.hashCode) +
      (config == null ? 0 : config.hashCode) +
      inputs.hashCode;

  factory StepDTO.fromJson(Map<String, dynamic> json) =>
      _$StepDTOFromJson(json);

  Map<String, dynamic> toJson() => _$StepDTOToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
