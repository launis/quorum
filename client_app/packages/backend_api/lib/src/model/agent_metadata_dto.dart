//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'agent_metadata_dto.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AgentMetadataDTO {
  /// Returns a new [AgentMetadataDTO] instance.
  AgentMetadataDTO({

    required  this.name,

    required  this.description,

    required  this.inputs,

     this.outputs,
  });

      /// Agent class name.
  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



      /// Agent docstring/description.
  @JsonKey(
    
    name: r'description',
    required: true,
    
  )


  final String description;



      /// List of required input keys.
  @JsonKey(
    
    name: r'inputs',
    required: true,
    
  )


  final List<String> inputs;



      /// List of produced output keys.
  @JsonKey(
    
    name: r'outputs',
    required: false,
    
  )


  final List<String>? outputs;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AgentMetadataDTO &&
      other.name == name &&
      other.description == description &&
      other.inputs == inputs &&
      other.outputs == outputs;

    @override
    int get hashCode =>
        name.hashCode +
        description.hashCode +
        inputs.hashCode +
        outputs.hashCode;

  factory AgentMetadataDTO.fromJson(Map<String, dynamic> json) => _$AgentMetadataDTOFromJson(json);

  Map<String, dynamic> toJson() => _$AgentMetadataDTOToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

