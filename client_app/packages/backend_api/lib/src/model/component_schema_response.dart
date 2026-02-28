//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'component_schema_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ComponentSchemaResponse {
  /// Returns a new [ComponentSchemaResponse] instance.
  ComponentSchemaResponse({required this.schema});

  @JsonKey(name: r'schema', required: true)
  final Map<String, Object> schema;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ComponentSchemaResponse && other.schema == schema;

  @override
  int get hashCode => schema.hashCode;

  factory ComponentSchemaResponse.fromJson(Map<String, dynamic> json) =>
      _$ComponentSchemaResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ComponentSchemaResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
