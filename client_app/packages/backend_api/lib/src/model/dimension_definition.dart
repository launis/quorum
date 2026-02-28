//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'dimension_definition.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class DimensionDefinition {
  /// Returns a new [DimensionDefinition] instance.
  DimensionDefinition({
    this.id,

    this.slug,

    required this.label,

    this.description,

    this.isSystem = false,
  });

  /// Unique dimension ID (e.g. 'analyysi').
  @JsonKey(name: r'id', required: false)
  final String? id;

  @JsonKey(name: r'slug', required: false)
  final String? slug;

  /// Human readable default label.
  @JsonKey(name: r'label', required: true)
  final String label;

  @JsonKey(name: r'description', required: false)
  final String? description;

  /// If true, is a core system dimension.
  @JsonKey(defaultValue: false, name: r'is_system', required: false)
  final bool? isSystem;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DimensionDefinition &&
          other.id == id &&
          other.slug == slug &&
          other.label == label &&
          other.description == description &&
          other.isSystem == isSystem;

  @override
  int get hashCode =>
      id.hashCode +
      (slug == null ? 0 : slug.hashCode) +
      label.hashCode +
      (description == null ? 0 : description.hashCode) +
      isSystem.hashCode;

  factory DimensionDefinition.fromJson(Map<String, dynamic> json) =>
      _$DimensionDefinitionFromJson(json);

  Map<String, dynamic> toJson() => _$DimensionDefinitionToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
