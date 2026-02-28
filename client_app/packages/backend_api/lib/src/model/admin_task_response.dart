//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'admin_task_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AdminTaskResponse {
  /// Returns a new [AdminTaskResponse] instance.
  AdminTaskResponse({
    required this.status,

    required this.jobId,

    required this.task,

    this.message,
  });

  @JsonKey(name: r'status', required: true)
  final AdminTaskResponseStatusEnum status;

  @JsonKey(name: r'job_id', required: true)
  final String jobId;

  @JsonKey(name: r'task', required: true)
  final String task;

  @JsonKey(name: r'message', required: false)
  final String? message;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AdminTaskResponse &&
          other.status == status &&
          other.jobId == jobId &&
          other.task == task &&
          other.message == message;

  @override
  int get hashCode =>
      status.hashCode +
      jobId.hashCode +
      task.hashCode +
      (message == null ? 0 : message.hashCode);

  factory AdminTaskResponse.fromJson(Map<String, dynamic> json) =>
      _$AdminTaskResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AdminTaskResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}

enum AdminTaskResponseStatusEnum {
  @JsonValue(r'started')
  started(r'started'),
  @JsonValue(r'starting')
  starting(r'starting'),
  @JsonValue(r'failed')
  failed(r'failed');

  const AdminTaskResponseStatusEnum(this.value);

  final String value;

  @override
  String toString() => value;
}
