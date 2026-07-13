// ignore_for_file: invalid_annotation_target
import 'package:client_app/core/utils/safe_isolate.dart';
import 'dart:convert';

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';

part 'execution_record.freezed.dart';
part 'execution_record.g.dart';

String _statusFromJson(String status) => status.toUpperCase();
String? _traceVersionFromJson(dynamic value) => value?.toString();

/// Represents the status and metadata of an execution.
/// Follows The De-Generator Mandate: Replaces the old dynamic 'results' map
/// with strict typed fields and an explicit reference to the [ReportDataDTO].
@Freezed(equal: false)
abstract class ExecutionRecord with _$ExecutionRecord {
  const ExecutionRecord._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionRecord({
    required String id,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(fromJson: _statusFromJson) required String status,
    @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)
    String? traceVersion,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,

    /// The strictly typed DTO containing the presentation flat data.
    /// Replaces the legacy `results` Map.
    @JsonKey(name: 'report_data') ReportDataDTO? reportData,

    /// Phase 2 V2 Payload implementation
    @JsonKey(name: 'report_data_v2') ReportDataDto? reportDataV2,
  }) = _ExecutionRecord;

  /// Instantiates a strictly typed [ExecutionRecord] from raw JSON.
  factory ExecutionRecord.fromJson(Map<String, dynamic> json) =>
      _$ExecutionRecordFromJson(json);

  /// Parses raw JSON string to ExecutionRecord in a background isolate
  /// to prevent Main Thread Jank when handling large payloads.
  static Future<ExecutionRecord> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ExecutionRecord.fromJson(decoded);
    });
  }
}
