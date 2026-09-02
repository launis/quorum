// ignore_for_file: invalid_annotation_target
import 'dart:convert';

import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

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
    @JsonKey(name: 'target_locale') required String targetLocale,
    @JsonKey(fromJson: _statusFromJson) required String status,
    @JsonKey(name: 'active_profile_id') String? activeProfileId,
    @JsonKey(name: 'output_profile_id') String? outputProfileId,
    @JsonKey(name: 'raw_inputs') Map<String, dynamic>? rawInputs,
    @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)
    String? traceVersion,
    @JsonKey(name: 'strictness_level') int? strictnessLevel,
    @JsonKey(name: 'duration_ms') int? durationMs,
    @JsonKey(name: 'cost_estimate') double? costEstimate,
    @JsonKey(name: 'prompt_tokens') @Default(0) int promptTokens,
    @JsonKey(name: 'completion_tokens') @Default(0) int completionTokens,
    @JsonKey(name: 'cached_tokens') @Default(0) int cachedTokens,
    @JsonKey(name: 'reasoning_tokens') @Default(0) int reasoningTokens,
    @JsonKey(name: 'dag_cost_usd') @Default(0.0) double dagCostUsd,
    @JsonKey(name: 'cumulative_synthesis_tokens')
    int? cumulativeSynthesisTokens,
    @JsonKey(name: 'cumulative_synthesis_cost') double? cumulativeSynthesisCost,
    @JsonKey(name: 'models_used') List<String>? modelsUsed,
    @JsonKey(name: 'metadata') ExecutionMetadata? metadata,
    @JsonKey(name: 'error') String? error,
    @JsonKey(name: 'is_resumable') bool? isResumable,
    @JsonKey(name: 'frozen_context') Map<String, dynamic>? frozenContext,
    @JsonKey(name: 'frozen_context_storage_path')
    String? frozenContextStoragePath,
    @JsonKey(name: 'context_variables') Map<String, dynamic>? contextVariables,
    @JsonKey(name: 'context_variables_storage_path')
    String? contextVariablesStoragePath,
    @JsonKey(name: 'execution_trace')
    List<Map<String, dynamic>>? executionTrace,
    @JsonKey(name: 'execution_trace_storage_path')
    String? executionTraceStoragePath,
    @JsonKey(name: 'pdf_report_path') String? pdfReportPath,
    @JsonKey(name: 'source_identity_manifest')
    Map<String, String>? sourceIdentityManifest,
    @JsonKey(name: 'steps') @Default([]) List<ExecutionStep> steps,
    @JsonKey(name: 'step_states') Map<String, dynamic>? stepStates,
    @JsonKey(name: 'profile_syntheses') Map<String, dynamic>? profileSyntheses,
    @JsonKey(name: 'results') Map<String, dynamic>? results,
    @JsonKey(name: 'progress') int? progress,
    @JsonKey(name: 'status_message') String? statusMessage,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'updated_at') String? updatedAt,
    @JsonKey(name: 'completed_at') String? completedAt,
    @JsonKey(name: 'created_by') String? createdBy,
    @JsonKey(name: 'organization_id') String? organizationId,

    /// The strictly typed DTO containing the presentation flat data.
    /// Replaces the legacy `results` Map.
    @JsonKey(name: 'report_data') ReportDataDto? reportData,
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
