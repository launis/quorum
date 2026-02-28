//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'body_run_agent_agents_agent_name_run_post.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class BodyRunAgentAgentsAgentNameRunPost {
  /// Returns a new [BodyRunAgentAgentsAgentNameRunPost] instance.
  BodyRunAgentAgentsAgentNameRunPost({
    required this.inputs,

    this.systemInstruction,

    this.model,
  });

  /// Key-value pairs representing the input state for the agent.
  @JsonKey(name: r'inputs', required: true)
  final Map<String, Object> inputs;

  @JsonKey(name: r'system_instruction', required: false)
  final String? systemInstruction;

  @JsonKey(name: r'model', required: false)
  final String? model;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BodyRunAgentAgentsAgentNameRunPost &&
          other.inputs == inputs &&
          other.systemInstruction == systemInstruction &&
          other.model == model;

  @override
  int get hashCode =>
      inputs.hashCode +
      (systemInstruction == null ? 0 : systemInstruction.hashCode) +
      (model == null ? 0 : model.hashCode);

  factory BodyRunAgentAgentsAgentNameRunPost.fromJson(
    Map<String, dynamic> json,
  ) => _$BodyRunAgentAgentsAgentNameRunPostFromJson(json);

  Map<String, dynamic> toJson() =>
      _$BodyRunAgentAgentsAgentNameRunPostToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
