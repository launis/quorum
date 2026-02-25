//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_template.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowTemplate {
  /// Returns a new [WorkflowTemplate] instance.
  WorkflowTemplate({

    required  this.name,

    required  this.description,

    required  this.steps,

    required  this.defaultModelMapping,

    required  this.uiSchema,
  });

  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



  @JsonKey(
    
    name: r'description',
    required: true,
    
  )


  final String description;



  @JsonKey(
    
    name: r'steps',
    required: true,
    
  )


  final List<String> steps;



  @JsonKey(
    
    name: r'default_model_mapping',
    required: true,
    
  )


  final Map<String, String> defaultModelMapping;



  @JsonKey(
    
    name: r'ui_schema',
    required: true,
    
  )


  final Map<String, Object> uiSchema;





    @override
    bool operator ==(Object other) => identical(this, other) || other is WorkflowTemplate &&
      other.name == name &&
      other.description == description &&
      other.steps == steps &&
      other.defaultModelMapping == defaultModelMapping &&
      other.uiSchema == uiSchema;

    @override
    int get hashCode =>
        name.hashCode +
        description.hashCode +
        steps.hashCode +
        defaultModelMapping.hashCode +
        uiSchema.hashCode;

  factory WorkflowTemplate.fromJson(Map<String, dynamic> json) => _$WorkflowTemplateFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowTemplateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

