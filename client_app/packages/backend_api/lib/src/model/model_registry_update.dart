//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'model_registry_update.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ModelRegistryUpdate {
  /// Returns a new [ModelRegistryUpdate] instance.
  ModelRegistryUpdate({required this.registry});

  /// The new configuration map for model strategies (e.g. {'fast': {'model_name': '...'}}).
  @JsonKey(name: r'registry', required: true)
  final Map<String, Map<String, String>> registry;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ModelRegistryUpdate && other.registry == registry;

  @override
  int get hashCode => registry.hashCode;

  factory ModelRegistryUpdate.fromJson(Map<String, dynamic> json) =>
      _$ModelRegistryUpdateFromJson(json);

  Map<String, dynamic> toJson() => _$ModelRegistryUpdateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
