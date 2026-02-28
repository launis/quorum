//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'model_registry_update_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ModelRegistryUpdateResponse {
  /// Returns a new [ModelRegistryUpdateResponse] instance.
  ModelRegistryUpdateResponse({required this.status, required this.registry});

  @JsonKey(name: r'status', required: true)
  final String status;

  @JsonKey(name: r'registry', required: true)
  final Map<String, Map<String, String>> registry;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ModelRegistryUpdateResponse &&
          other.status == status &&
          other.registry == registry;

  @override
  int get hashCode => status.hashCode + registry.hashCode;

  factory ModelRegistryUpdateResponse.fromJson(Map<String, dynamic> json) =>
      _$ModelRegistryUpdateResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ModelRegistryUpdateResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
