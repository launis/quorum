//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/problem_detail.dart';
import 'package:backend_api/src/model/percent.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'task_status_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class TaskStatusResponse {
  /// Returns a new [TaskStatusResponse] instance.
  TaskStatusResponse({
    required this.status,

    this.stage,

    this.percent,

    this.error,
  });

  @JsonKey(name: r'status', required: true)
  final String status;

  @JsonKey(name: r'stage', required: false)
  final String? stage;

  @JsonKey(name: r'percent', required: false)
  final Percent? percent;

  @JsonKey(name: r'error', required: false)
  final ProblemDetail? error;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TaskStatusResponse &&
          other.status == status &&
          other.stage == stage &&
          other.percent == percent &&
          other.error == error;

  @override
  int get hashCode =>
      status.hashCode +
      (stage == null ? 0 : stage.hashCode) +
      percent.hashCode +
      (error == null ? 0 : error.hashCode);

  factory TaskStatusResponse.fromJson(Map<String, dynamic> json) =>
      _$TaskStatusResponseFromJson(json);

  Map<String, dynamic> toJson() => _$TaskStatusResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
