//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'playground_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PlaygroundRequest {
  /// Returns a new [PlaygroundRequest] instance.
  PlaygroundRequest({
    required this.systemInstruction,

    required this.userMessage,

    this.variables,

    this.modelParams,
  });

  /// System prompt template.
  @JsonKey(name: r'system_instruction', required: true)
  final String systemInstruction;

  /// User message.
  @JsonKey(name: r'user_message', required: true)
  final String userMessage;

  /// Variables to inject into system prompt.
  @JsonKey(name: r'variables', required: false)
  final Map<String, String>? variables;

  /// Optional LLM parameters.
  @JsonKey(name: r'model_params', required: false)
  final Map<String, Object>? modelParams;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PlaygroundRequest &&
          other.systemInstruction == systemInstruction &&
          other.userMessage == userMessage &&
          other.variables == variables &&
          other.modelParams == modelParams;

  @override
  int get hashCode =>
      systemInstruction.hashCode +
      userMessage.hashCode +
      variables.hashCode +
      modelParams.hashCode;

  factory PlaygroundRequest.fromJson(Map<String, dynamic> json) =>
      _$PlaygroundRequestFromJson(json);

  Map<String, dynamic> toJson() => _$PlaygroundRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
