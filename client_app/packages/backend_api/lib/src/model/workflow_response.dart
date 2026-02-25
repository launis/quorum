//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/workflow_step.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'workflow_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WorkflowResponse {
  /// Returns a new [WorkflowResponse] instance.
  WorkflowResponse({

    required  this.id,

    required  this.name,

     this.description = '',

    required  this.steps,

     this.defaultModelMapping = const {},

     this.uiSchema = const {},

     this.isPublic = false,

     this.status = 'draft',

     this.version = 1,

     this.scoringLogic = const [],

     this.createdAt,

     this.updatedAt,

    required  this.organizationId,
  });

  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



  @JsonKey(
    defaultValue: '',
    name: r'description',
    required: false,
    
  )


  final String? description;



  @JsonKey(
    
    name: r'steps',
    required: true,
    
  )


  final List<WorkflowStep> steps;



  @JsonKey(
    defaultValue: {},
    name: r'default_model_mapping',
    required: false,
    
  )


  final Map<String, String>? defaultModelMapping;



  @JsonKey(
    defaultValue: {},
    name: r'ui_schema',
    required: false,
    
  )


  final Map<String, Object>? uiSchema;



  @JsonKey(
    defaultValue: false,
    name: r'is_public',
    required: false,
    
  )


  final bool? isPublic;



  @JsonKey(
    defaultValue: 'draft',
    name: r'status',
    required: false,
    
  )


  final String? status;



  @JsonKey(
    defaultValue: 1,
    name: r'version',
    required: false,
    
  )


  final int? version;



  @JsonKey(
    defaultValue: [],
    name: r'scoring_logic',
    required: false,
    
  )


  final List<Map<String, Object>>? scoringLogic;



  @JsonKey(
    
    name: r'created_at',
    required: false,
    
  )


  final dynamic? createdAt;



  @JsonKey(
    
    name: r'updated_at',
    required: false,
    
  )


  final dynamic? updatedAt;



  @JsonKey(
    
    name: r'organization_id',
    required: true,
    
  )


  final String organizationId;





    @override
    bool operator ==(Object other) => identical(this, other) || other is WorkflowResponse &&
      other.id == id &&
      other.name == name &&
      other.description == description &&
      other.steps == steps &&
      other.defaultModelMapping == defaultModelMapping &&
      other.uiSchema == uiSchema &&
      other.isPublic == isPublic &&
      other.status == status &&
      other.version == version &&
      other.scoringLogic == scoringLogic &&
      other.createdAt == createdAt &&
      other.updatedAt == updatedAt &&
      other.organizationId == organizationId;

    @override
    int get hashCode =>
        id.hashCode +
        name.hashCode +
        description.hashCode +
        steps.hashCode +
        defaultModelMapping.hashCode +
        uiSchema.hashCode +
        isPublic.hashCode +
        status.hashCode +
        version.hashCode +
        scoringLogic.hashCode +
        (createdAt == null ? 0 : createdAt.hashCode) +
        (updatedAt == null ? 0 : updatedAt.hashCode) +
        organizationId.hashCode;

  factory WorkflowResponse.fromJson(Map<String, dynamic> json) => _$WorkflowResponseFromJson(json);

  Map<String, dynamic> toJson() => _$WorkflowResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

