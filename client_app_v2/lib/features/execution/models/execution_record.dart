import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/features/execution/models/report_data_dto.dart';

/// Represents the status and metadata of an execution.
/// Follows The De-Generator Mandate: Replaces the old dynamic 'results' map
/// with strict typed fields and an explicit reference to the [ReportDataDTO].
class ExecutionRecord {
  final String id;
  final String workflowId;
  final String status;
  final String? traceVersion;

  /// The strictly typed DTO containing the presentation flat data.
  /// Replaces the legacy `results` Map.
  final ReportDataDTO? reportData;

  const ExecutionRecord({
    required this.id,
    required this.workflowId,
    required this.status,
    this.traceVersion,
    this.reportData,
  });

  /// Instantiates a strictly typed [ExecutionRecord] from raw JSON.
  factory ExecutionRecord.fromJson(Map<String, dynamic> json) {
    return ExecutionRecord(
      id: json['id'] as String,
      workflowId: json['workflow_id'] as String,
      status: (json['status'] as String).toUpperCase(),
      traceVersion: json['trace_version']?.toString(),
      reportData: json['report_data'] != null
          ? ReportDataDTO.fromJson(
              json['report_data'] is Map
                  ? json['report_data'] as Map<String, dynamic>
                  : <String, dynamic>{},
            )
          : null,
    );
  }

  /// Parses raw JSON string to ExecutionRecord in a background isolate
  /// to prevent Main Thread Jank when handling large payloads.
  static Future<ExecutionRecord> parseInBackground(String rawJson) async {
    return Isolate.run(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ExecutionRecord.fromJson(decoded);
    });
  }

  /// Creates a copy of this record, allowing non-destructive mutation
  /// (e.g., when merging a Heavy Fetch ReportDataDTO into an SSE Delta state).
  ExecutionRecord copyWith({
    String? status,
    String? traceVersion,
    ReportDataDTO? reportData,
  }) {
    return ExecutionRecord(
      id: id,
      workflowId: workflowId,
      status: status ?? this.status,
      traceVersion: traceVersion ?? this.traceVersion,
      reportData: reportData ?? this.reportData,
    );
  }
}
