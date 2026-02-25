//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'agent_definition.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AgentDefinition {
  /// Returns a new [AgentDefinition] instance.
  AgentDefinition({

    required  this.name,

    required  this.class_,

    required  this.description,

    required  this.model,

     this.inputSchema,

     this.outputSchema,
  });

  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



  @JsonKey(
    
    name: r'class',
    required: true,
    
  )


  final String class_;



  @JsonKey(
    
    name: r'description',
    required: true,
    
  )


  final String description;



  @JsonKey(
    
    name: r'model',
    required: true,
    
  )


  final String model;



  @JsonKey(
    
    name: r'input_schema',
    required: false,
    
  )


  final Map<String, Object>? inputSchema;



  @JsonKey(
    
    name: r'output_schema',
    required: false,
    
  )


  final Map<String, Object>? outputSchema;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AgentDefinition &&
      other.name == name &&
      other.class_ == class_ &&
      other.description == description &&
      other.model == model &&
      other.inputSchema == inputSchema &&
      other.outputSchema == outputSchema;

    @override
    int get hashCode =>
        name.hashCode +
        class_.hashCode +
        description.hashCode +
        model.hashCode +
        (inputSchema == null ? 0 : inputSchema.hashCode) +
        (outputSchema == null ? 0 : outputSchema.hashCode);

  factory AgentDefinition.fromJson(Map<String, dynamic> json) => _$AgentDefinitionFromJson(json);

  Map<String, dynamic> toJson() => _$AgentDefinitionToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

