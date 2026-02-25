//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/steps.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_config_definition.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowConfigDefinition {
  /// Returns a new [WorkflowConfigDefinition] instance.
  WorkflowConfigDefinition({

     this.id,

     this.slug,

    required  this.name,

     this.description,

     this.sequence = const [],

     this.steps,

     this.uiSchema,

     this.defaultModelMapping,
  });

      /// Workflow UUID
  @JsonKey(
    
    name: r'id',
    required: false,
    
  )


  final String? id;



  @JsonKey(
    
    name: r'slug',
    required: false,
    
  )


  final String? slug;



      /// Workflow Name
  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



  @JsonKey(
    
    name: r'description',
    required: false,
    
  )


  final String? description;



      /// Ordered list of Step IDs
  @JsonKey(
    defaultValue: [],
    name: r'sequence',
    required: false,
    
  )


  final List<String>? sequence;



  @JsonKey(
    
    name: r'steps',
    required: false,
    
  )


  final Steps? steps;



  @JsonKey(
    
    name: r'ui_schema',
    required: false,
    
  )


  final Map<String, Object>? uiSchema;



  @JsonKey(
    
    name: r'default_model_mapping',
    required: false,
    
  )


  final Map<String, String>? defaultModelMapping;





    @override
    bool operator ==(Object other) => identical(this, other) || other is WorkflowConfigDefinition &&
      other.id == id &&
      other.slug == slug &&
      other.name == name &&
      other.description == description &&
      other.sequence == sequence &&
      other.steps == steps &&
      other.uiSchema == uiSchema &&
      other.defaultModelMapping == defaultModelMapping;

    @override
    int get hashCode =>
        id.hashCode +
        (slug == null ? 0 : slug.hashCode) +
        name.hashCode +
        (description == null ? 0 : description.hashCode) +
        sequence.hashCode +
        steps.hashCode +
        (uiSchema == null ? 0 : uiSchema.hashCode) +
        (defaultModelMapping == null ? 0 : defaultModelMapping.hashCode);

  factory WorkflowConfigDefinition.fromJson(Map<String, dynamic> json) => _$WorkflowConfigDefinitionFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowConfigDefinitionToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

