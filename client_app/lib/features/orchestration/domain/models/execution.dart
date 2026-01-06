import 'package:json_annotation/json_annotation.dart';

part 'execution.g.dart';

/// **Execution Status Enum**
///
/// Represents the lifecycle state of a workflow execution.
enum ExecutionStatus {
  pending,
  started,
  running,
  completed,
  failed,
  rejected,
  interrupted,
  unknown,
}

/// **Execution Domain Model**
///
/// Represents a single instance of a Workflow being run.
/// This is the primary data structure for tracking asynchronous jobs in the system.
///
/// **Business Context**:
/// An [Execution] links a [User] to a [Workflow] and stores both the initial [inputs]
/// and the final [result]. It acts as the audit trail for "who did what and when".
///
/// **Serialization**:
/// Uses [JsonSerializable] to map from the backend JSON schema.
/// `explicitToJson: true` ensures nested objects are correctly serialized.
@JsonSerializable(explicitToJson: true)
class Execution {
  /// The unique UUID of the execution record.
  @JsonKey(name: 'execution_id')
  final String? executionId;

  /// The UUID of the Workflow definition that strictly defines the steps logic.
  @JsonKey(name: 'workflow_id')
  final String? workflowId;

  /// Current status string (e.g. 'completed', 'failed').
  /// Ideally mapped to [ExecutionStatus] in the UI layer or via custom converters.
  final String? status;

  /// The input parameters provided at start time.
  /// Used for re-running or auditing the execution context.
  @JsonKey(defaultValue: {})
  final Map<String, dynamic> inputs;

  /// ISO 8601 Timestamp of when the execution started.
  @JsonKey(name: 'start_time')
  final String? startTime;

  /// ISO 8601 Timestamp of when the execution finished (if applicable).
  @JsonKey(name: 'end_time')
  final String? endTime;

  /// The Organization ID this execution belongs to.
  /// Used for multi-tenant isolation and strict data scoping.
  @JsonKey(name: 'organization_id')
  final String? organizationId;

  // Constructor
  Execution({
    this.executionId,
    this.workflowId,
    this.status,
    this.inputs = const {},
    this.startTime,
    this.endTime,
    this.organizationId,
  });

  /// Creates an [Execution] instance from a JSON map.
  factory Execution.fromJson(Map<String, dynamic> json) =>
      _$ExecutionFromJson(json);

  /// Converts this [Execution] instance to a JSON map.
  Map<String, dynamic> toJson() => _$ExecutionToJson(this);
}
