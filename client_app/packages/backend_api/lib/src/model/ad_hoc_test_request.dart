//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'ad_hoc_test_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AdHocTestRequest {
  /// Returns a new [AdHocTestRequest] instance.
  AdHocTestRequest({
    required this.provider,

    this.apiKey,

    required this.systemInstruction,

    required this.userPrompt,

    this.modelParams,
  });

  /// Provider identifier.
  @JsonKey(name: r'provider', required: true)
  final String provider;

  @JsonKey(name: r'api_key', required: false)
  final String? apiKey;

  /// System prompt.
  @JsonKey(name: r'system_instruction', required: true)
  final String systemInstruction;

  /// User prompt.
  @JsonKey(name: r'user_prompt', required: true)
  final String userPrompt;

  /// Model parameters override.
  @JsonKey(name: r'model_params', required: false)
  final Map<String, Object>? modelParams;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AdHocTestRequest &&
          other.provider == provider &&
          other.apiKey == apiKey &&
          other.systemInstruction == systemInstruction &&
          other.userPrompt == userPrompt &&
          other.modelParams == modelParams;

  @override
  int get hashCode =>
      provider.hashCode +
      (apiKey == null ? 0 : apiKey.hashCode) +
      systemInstruction.hashCode +
      userPrompt.hashCode +
      modelParams.hashCode;

  factory AdHocTestRequest.fromJson(Map<String, dynamic> json) =>
      _$AdHocTestRequestFromJson(json);

  Map<String, dynamic> toJson() => _$AdHocTestRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
