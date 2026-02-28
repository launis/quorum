//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'knowledge_job_status_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class KnowledgeJobStatusResponse {
  /// Returns a new [KnowledgeJobStatusResponse] instance.
  KnowledgeJobStatusResponse({
    required this.jobId,

    required this.status,

    required this.progress,

    required this.stage,

    this.result,

    this.error,

    this.errorCode,
  });

  @JsonKey(name: r'job_id', required: true)
  final String jobId;

  @JsonKey(name: r'status', required: true)
  final String status;

  @JsonKey(name: r'progress', required: true)
  final int progress;

  @JsonKey(name: r'stage', required: true)
  final String stage;

  @JsonKey(name: r'result', required: false)
  final dynamic? result;

  @JsonKey(name: r'error', required: false)
  final String? error;

  @JsonKey(name: r'error_code', required: false)
  final String? errorCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is KnowledgeJobStatusResponse &&
          other.jobId == jobId &&
          other.status == status &&
          other.progress == progress &&
          other.stage == stage &&
          other.result == result &&
          other.error == error &&
          other.errorCode == errorCode;

  @override
  int get hashCode =>
      jobId.hashCode +
      status.hashCode +
      progress.hashCode +
      stage.hashCode +
      (result == null ? 0 : result.hashCode) +
      (error == null ? 0 : error.hashCode) +
      (errorCode == null ? 0 : errorCode.hashCode);

  factory KnowledgeJobStatusResponse.fromJson(Map<String, dynamic> json) =>
      _$KnowledgeJobStatusResponseFromJson(json);

  Map<String, dynamic> toJson() => _$KnowledgeJobStatusResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
