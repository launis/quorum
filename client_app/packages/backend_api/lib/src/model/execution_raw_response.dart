//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'execution_raw_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ExecutionRawResponse {
  /// Returns a new [ExecutionRawResponse] instance.
  ExecutionRawResponse({

    required  this.id,

    required  this.workflowId,

    required  this.status,

    required  this.startedAt,

    required  this.completedAt,

     this.durationSeconds,

     this.inputs = const {},

     this.results = const {},

     this.state = const {},

    required  this.userId,

     this.agentOutputs = const {},

     this.hookOutputs = const {},

     this.xaiReport,
  });

  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



  @JsonKey(
    
    name: r'workflow_id',
    required: true,
    includeIfNull: true,
  )


  final String? workflowId;



  @JsonKey(
    
    name: r'status',
    required: true,
    includeIfNull: true,
  )


  final String? status;



  @JsonKey(
    
    name: r'started_at',
    required: true,
    includeIfNull: true,
  )


  final DateTime? startedAt;



  @JsonKey(
    
    name: r'completed_at',
    required: true,
    includeIfNull: true,
  )


  final DateTime? completedAt;



  @JsonKey(
    
    name: r'duration_seconds',
    required: false,
    
  )


  final num? durationSeconds;



  @JsonKey(
    defaultValue: {},
    name: r'inputs',
    required: false,
    
  )


  final Map<String, Object>? inputs;



  @JsonKey(
    defaultValue: {},
    name: r'results',
    required: false,
    
  )


  final Map<String, Object>? results;



  @JsonKey(
    defaultValue: {},
    name: r'state',
    required: false,
    
  )


  final Map<String, Object>? state;



  @JsonKey(
    
    name: r'user_id',
    required: true,
    includeIfNull: true,
  )


  final String? userId;



  @JsonKey(
    defaultValue: {},
    name: r'agent_outputs',
    required: false,
    
  )


  final Map<String, Object>? agentOutputs;



  @JsonKey(
    defaultValue: {},
    name: r'hook_outputs',
    required: false,
    
  )


  final Map<String, Object>? hookOutputs;



  @JsonKey(
    
    name: r'xai_report',
    required: false,
    
  )


  final String? xaiReport;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ExecutionRawResponse &&
      other.id == id &&
      other.workflowId == workflowId &&
      other.status == status &&
      other.startedAt == startedAt &&
      other.completedAt == completedAt &&
      other.durationSeconds == durationSeconds &&
      other.inputs == inputs &&
      other.results == results &&
      other.state == state &&
      other.userId == userId &&
      other.agentOutputs == agentOutputs &&
      other.hookOutputs == hookOutputs &&
      other.xaiReport == xaiReport;

    @override
    int get hashCode =>
        id.hashCode +
        (workflowId == null ? 0 : workflowId.hashCode) +
        (status == null ? 0 : status.hashCode) +
        (startedAt == null ? 0 : startedAt.hashCode) +
        (completedAt == null ? 0 : completedAt.hashCode) +
        (durationSeconds == null ? 0 : durationSeconds.hashCode) +
        inputs.hashCode +
        results.hashCode +
        state.hashCode +
        (userId == null ? 0 : userId.hashCode) +
        agentOutputs.hashCode +
        hookOutputs.hashCode +
        (xaiReport == null ? 0 : xaiReport.hashCode);

  factory ExecutionRawResponse.fromJson(Map<String, dynamic> json) => _$ExecutionRawResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ExecutionRawResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

