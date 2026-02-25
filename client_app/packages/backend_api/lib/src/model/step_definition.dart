//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'step_definition.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class StepDefinition {
  /// Returns a new [StepDefinition] instance.
  StepDefinition({

     this.id,

     this.slug,

    required  this.name,

     this.description,

     this.taskKey = 'analyst',

     this.config = const {},

     this.inputs = const {},

     this.isMissingRegistry = false,
  });

      /// Unique step identifier
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



      /// Human-readable name
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



      /// Task Key (DB source)
  @JsonKey(
    defaultValue: 'analyst',
    name: r'task_key',
    required: false,
    
  )


  final String? taskKey;



      /// Configuration (DB source)
  @JsonKey(
    defaultValue: {},
    name: r'config',
    required: false,
    
  )


  final Map<String, Object>? config;



      /// Default Input Mapping
  @JsonKey(
    defaultValue: {},
    name: r'inputs',
    required: false,
    
  )


  final Map<String, String>? inputs;



      /// Missing registry marker
  @JsonKey(
    defaultValue: false,
    name: r'is_missing_registry',
    required: false,
    
  )


  final bool? isMissingRegistry;





    @override
    bool operator ==(Object other) => identical(this, other) || other is StepDefinition &&
      other.id == id &&
      other.slug == slug &&
      other.name == name &&
      other.description == description &&
      other.taskKey == taskKey &&
      other.config == config &&
      other.inputs == inputs &&
      other.isMissingRegistry == isMissingRegistry;

    @override
    int get hashCode =>
        id.hashCode +
        (slug == null ? 0 : slug.hashCode) +
        name.hashCode +
        (description == null ? 0 : description.hashCode) +
        taskKey.hashCode +
        config.hashCode +
        inputs.hashCode +
        isMissingRegistry.hashCode;

  factory StepDefinition.fromJson(Map<String, dynamic> json) => _$StepDefinitionFromJson(json);

  Map<String, dynamic> toJson() => _$StepDefinitionToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

