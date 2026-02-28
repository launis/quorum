//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'schema_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SchemaResponse {
  /// Returns a new [SchemaResponse] instance.
  SchemaResponse({required this.modelName, required this.schemaDef});

  @JsonKey(name: r'model_name', required: true)
  final String modelName;

  @JsonKey(name: r'schema_def', required: true)
  final Map<String, Object> schemaDef;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SchemaResponse &&
          other.modelName == modelName &&
          other.schemaDef == schemaDef;

  @override
  int get hashCode => modelName.hashCode + schemaDef.hashCode;

  factory SchemaResponse.fromJson(Map<String, dynamic> json) =>
      _$SchemaResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SchemaResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
