//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'registry_component_item.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class RegistryComponentItem {
  /// Returns a new [RegistryComponentItem] instance.
  RegistryComponentItem({
    this.id,

    this.slug,

    required this.name,

    required this.type,

    this.description,

    this.content,

    this.citation,
  });

  /// Component ID
  @JsonKey(name: r'id', required: false)
  final String? id;

  @JsonKey(name: r'slug', required: false)
  final String? slug;

  /// Meaningful Label
  @JsonKey(name: r'name', required: true)
  final String name;

  /// Type category
  @JsonKey(name: r'type', required: true)
  final String type;

  @JsonKey(name: r'description', required: false)
  final String? description;

  @JsonKey(name: r'content', required: false)
  final Object? content;

  @JsonKey(name: r'citation', required: false)
  final String? citation;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RegistryComponentItem &&
          other.id == id &&
          other.slug == slug &&
          other.name == name &&
          other.type == type &&
          other.description == description &&
          other.content == content &&
          other.citation == citation;

  @override
  int get hashCode =>
      id.hashCode +
      (slug == null ? 0 : slug.hashCode) +
      name.hashCode +
      type.hashCode +
      (description == null ? 0 : description.hashCode) +
      (content == null ? 0 : content.hashCode) +
      (citation == null ? 0 : citation.hashCode);

  factory RegistryComponentItem.fromJson(Map<String, dynamic> json) =>
      _$RegistryComponentItemFromJson(json);

  Map<String, dynamic> toJson() => _$RegistryComponentItemToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
