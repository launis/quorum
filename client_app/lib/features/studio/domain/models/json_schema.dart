import 'package:freezed_annotation/freezed_annotation.dart';

part 'json_schema.freezed.dart';
part 'json_schema.g.dart';

// ignore_for_file: invalid_annotation_target
// Force Rebuild

@freezed
abstract class JsonSchema with _$JsonSchema {
  const factory JsonSchema({
    String? type,
    String? title,
    String? description,
    
    // Recursive definition for object properties
    Map<String, JsonSchema>? properties,
    
    // For arrays
    JsonSchema? items,

    List<String>? required,
    
    // Mapped from 'enum' in JSON Schema
    @JsonKey(name: 'enum') List<dynamic>? enumValues,
    
    int? minLength,
    int? maxLength,
    double? minimum,
    double? maximum,
    
    // UI Hints
    @JsonKey(name: 'x-ui-widget') String? uiWidget,
    @JsonKey(name: 'x-ui-group') String? uiGroup,
  }) = _JsonSchema;

  factory JsonSchema.fromJson(Map<String, dynamic> json) => 
      _$JsonSchemaFromJson(json);
}
