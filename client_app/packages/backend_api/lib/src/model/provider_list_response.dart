//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'provider_list_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ProviderListResponse {
  /// Returns a new [ProviderListResponse] instance.
  ProviderListResponse({
    required this.strategies,

    required this.apiKeysSet,

    this.availableModels,
  });

  /// Map of strategy keys to model names.
  @JsonKey(name: r'strategies', required: true)
  final Map<String, String> strategies;

  /// Status of API keys (mask/bool).
  @JsonKey(name: r'api_keys_set', required: true)
  final Map<String, bool> apiKeysSet;

  /// Map of provider to list of available model IDs.
  @JsonKey(name: r'available_models', required: false)
  final Map<String, List<String>>? availableModels;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProviderListResponse &&
          other.strategies == strategies &&
          other.apiKeysSet == apiKeysSet &&
          other.availableModels == availableModels;

  @override
  int get hashCode =>
      strategies.hashCode + apiKeysSet.hashCode + availableModels.hashCode;

  factory ProviderListResponse.fromJson(Map<String, dynamic> json) =>
      _$ProviderListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ProviderListResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
