//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_step.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowStep {
  /// Returns a new [WorkflowStep] instance.
  WorkflowStep({

     this.id,

     this.slug,

    required  this.name,

     this.description,

    required  this.taskKey,

     this.inputs,

     this.config,

     this.isMissingRegistry = false,
  });

      /// Unique step identifier, e.g., 'safety_check'
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



      /// Human-readable name of the step
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



      /// Registry Task Name (matches @register_task name)
  @JsonKey(
    
    name: r'task_key',
    required: true,
    
  )


  final String taskKey;



      /// Maps task inputs to state values. Example: {'text': '$inputs.history_text'}
  @JsonKey(
    
    name: r'inputs',
    required: false,
    
  )


  final Map<String, String>? inputs;



      /// Optional static config for the task
  @JsonKey(
    
    name: r'config',
    required: false,
    
  )


  final Map<String, Object>? config;



      /// UI Helper: True if this step references a task_key not in the backend registry.
  @JsonKey(
    defaultValue: false,
    name: r'is_missing_registry',
    required: false,
    
  )


  final bool? isMissingRegistry;





    @override
    bool operator ==(Object other) => identical(this, other) || other is WorkflowStep &&
      other.id == id &&
      other.slug == slug &&
      other.name == name &&
      other.description == description &&
      other.taskKey == taskKey &&
      other.inputs == inputs &&
      other.config == config &&
      other.isMissingRegistry == isMissingRegistry;

    @override
    int get hashCode =>
        id.hashCode +
        (slug == null ? 0 : slug.hashCode) +
        name.hashCode +
        (description == null ? 0 : description.hashCode) +
        taskKey.hashCode +
        inputs.hashCode +
        config.hashCode +
        isMissingRegistry.hashCode;

  factory WorkflowStep.fromJson(Map<String, dynamic> json) => _$WorkflowStepFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowStepToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

