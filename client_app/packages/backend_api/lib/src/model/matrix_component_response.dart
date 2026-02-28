//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/matrix_content_dto.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'matrix_component_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class MatrixComponentResponse {
  /// Returns a new [MatrixComponentResponse] instance.
  MatrixComponentResponse({
    this.id,

    this.slug,

    this.name,

    this.description,

    this.citation,

    this.citationFull,

    this.module,

    this.componentClass,

    this.className,

    this.registeredAt,

    required this.type,

    required this.content,
  });

  @JsonKey(name: r'id', required: false)
  final String? id;

  @JsonKey(name: r'slug', required: false)
  final String? slug;

  @JsonKey(name: r'name', required: false)
  final String? name;

  @JsonKey(name: r'description', required: false)
  final String? description;

  @JsonKey(name: r'citation', required: false)
  final String? citation;

  @JsonKey(name: r'citation_full', required: false)
  final String? citationFull;

  @JsonKey(name: r'module', required: false)
  final String? module;

  @JsonKey(name: r'component_class', required: false)
  final String? componentClass;

  @JsonKey(name: r'class_name', required: false)
  final String? className;

  @JsonKey(name: r'registered_at', required: false)
  final String? registeredAt;

  @JsonKey(name: r'type', required: true)
  final MatrixComponentResponseTypeEnum type;

  @JsonKey(name: r'content', required: true)
  final MatrixContentDTO content;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MatrixComponentResponse &&
          other.id == id &&
          other.slug == slug &&
          other.name == name &&
          other.description == description &&
          other.citation == citation &&
          other.citationFull == citationFull &&
          other.module == module &&
          other.componentClass == componentClass &&
          other.className == className &&
          other.registeredAt == registeredAt &&
          other.type == type &&
          other.content == content;

  @override
  int get hashCode =>
      id.hashCode +
      (slug == null ? 0 : slug.hashCode) +
      (name == null ? 0 : name.hashCode) +
      (description == null ? 0 : description.hashCode) +
      (citation == null ? 0 : citation.hashCode) +
      (citationFull == null ? 0 : citationFull.hashCode) +
      (module == null ? 0 : module.hashCode) +
      (componentClass == null ? 0 : componentClass.hashCode) +
      (className == null ? 0 : className.hashCode) +
      (registeredAt == null ? 0 : registeredAt.hashCode) +
      type.hashCode +
      content.hashCode;

  factory MatrixComponentResponse.fromJson(Map<String, dynamic> json) =>
      _$MatrixComponentResponseFromJson(json);

  Map<String, dynamic> toJson() => _$MatrixComponentResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}

enum MatrixComponentResponseTypeEnum {
  @JsonValue(r'evaluation_matrix')
  evaluationMatrix(r'evaluation_matrix');

  const MatrixComponentResponseTypeEnum(this.value);

  final String value;

  @override
  String toString() => value;
}
