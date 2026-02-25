//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'execution_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ExecutionResponse {
  /// Returns a new [ExecutionResponse] instance.
  ExecutionResponse({

    required  this.id,

    required  this.workflowId,

    required  this.status,

    required  this.startedAt,

     this.completedAt,

     this.results = const {},

     this.inputs = const {},

    required  this.userId,

     this.organizationId,

     this.workflowName,

     this.startTime,
  });

  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



  @JsonKey(
    
    name: r'workflow_id',
    required: true,
    
  )


  final String workflowId;



  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'started_at',
    required: true,
    
  )


  final DateTime startedAt;



  @JsonKey(
    
    name: r'completed_at',
    required: false,
    
  )


  final DateTime? completedAt;



  @JsonKey(
    defaultValue: {},
    name: r'results',
    required: false,
    
  )


  final Map<String, Object>? results;



  @JsonKey(
    defaultValue: {},
    name: r'inputs',
    required: false,
    
  )


  final Map<String, Object>? inputs;



  @JsonKey(
    
    name: r'user_id',
    required: true,
    
  )


  final String userId;



  @JsonKey(
    
    name: r'organization_id',
    required: false,
    
  )


  final String? organizationId;



  @JsonKey(
    
    name: r'workflow_name',
    required: false,
    
  )


  final String? workflowName;



  @JsonKey(
    
    name: r'start_time',
    required: false,
    
  )


  final DateTime? startTime;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ExecutionResponse &&
      other.id == id &&
      other.workflowId == workflowId &&
      other.status == status &&
      other.startedAt == startedAt &&
      other.completedAt == completedAt &&
      other.results == results &&
      other.inputs == inputs &&
      other.userId == userId &&
      other.organizationId == organizationId &&
      other.workflowName == workflowName &&
      other.startTime == startTime;

    @override
    int get hashCode =>
        id.hashCode +
        workflowId.hashCode +
        status.hashCode +
        startedAt.hashCode +
        (completedAt == null ? 0 : completedAt.hashCode) +
        results.hashCode +
        inputs.hashCode +
        userId.hashCode +
        (organizationId == null ? 0 : organizationId.hashCode) +
        (workflowName == null ? 0 : workflowName.hashCode) +
        (startTime == null ? 0 : startTime.hashCode);

  factory ExecutionResponse.fromJson(Map<String, dynamic> json) => _$ExecutionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ExecutionResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

