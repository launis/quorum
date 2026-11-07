import 'dart:convert';

import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/features/execution/models/execution_summary_snapshot.dart';
import 'package:client_app/features/execution/models/frozen_context_snapshot.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_record.freezed.dart';
part 'execution_record.g.dart';

String _statusFromJson(String status) => status.toUpperCase();

/// Typed execution-level context variables matching backend `ContextVariablesDTO`.
/// Phase 5, Step 5.1: Replace `Map<String, Object?>` contextVariables with closed Freezed DTO.
@freezed
abstract class ContextVariablesDto with _$ContextVariablesDto {
  const ContextVariablesDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ContextVariablesDto({
    @JsonKey(name: 'global_atom_blackboard') String? globalAtomBlackboard,
    @JsonKey(name: 'matrix_reducer_output') String? matrixReducerOutput,
    @JsonKey(name: 'report_context') String? reportContext,
    @JsonKey(name: 'step_detector') String? stepDetector,
    @JsonKey(name: 'evaluated_matrices') String? evaluatedMatrices,
    @Default(<String, String>{}) Map<String, String> variables,
  }) = _ContextVariablesDto;

  /// Instantiates a strictly typed [ContextVariablesDto] from raw JSON.
  factory ContextVariablesDto.fromJson(Map<String, dynamic> json) =>
      _$ContextVariablesDtoFromJson(json);
}

/// Typed execution trace entry on `ExecutionRecord.executionTrace`.
@freezed
abstract class ExecutionTraceItemDto with _$ExecutionTraceItemDto {
  const ExecutionTraceItemDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionTraceItemDto({
    String? event,
    @JsonKey(name: 'step_id') String? stepId,
    String? status,
    @JsonKey(name: 'duration_ms') int? durationMs,
    String? detail,
  }) = _ExecutionTraceItemDto;

  /// Instantiates a strictly typed [ExecutionTraceItemDto] from raw JSON.
  factory ExecutionTraceItemDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionTraceItemDtoFromJson(json);
}

/// Typed cached profile synthesis summary entry on `ExecutionRecord.profileSyntheses`.
@freezed
abstract class ProfileSynthesisEntryDto with _$ProfileSynthesisEntryDto {
  const ProfileSynthesisEntryDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ProfileSynthesisEntryDto({
    @Default(false) bool cached,
    @JsonKey(name: 'variance_explanation') String? varianceExplanation,
    @JsonKey(name: 'authenticity_explanation') String? authenticityExplanation,
    @JsonKey(name: 'cited_sources')
    @Default(<String>[])
    List<String> citedSources,
    @JsonKey(name: 'user_role') String? userRole,
    @JsonKey(name: 'user_role_justification') String? userRoleJustification,
    @JsonKey(name: 'created_at') String? createdAt,
  }) = _ProfileSynthesisEntryDto;

  /// Instantiates a strictly typed [ProfileSynthesisEntryDto] from raw JSON.
  factory ProfileSynthesisEntryDto.fromJson(Map<String, dynamic> json) =>
      _$ProfileSynthesisEntryDtoFromJson(json);
}

/// Represents the status and metadata of an execution.
@Freezed(equal: false)
abstract class ExecutionRecord with _$ExecutionRecord {
  const ExecutionRecord._();

  // Phase 5, Step 5.1: Replace Map<String, Object?> fields with typed Freezed step state and synthesis models.
  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionRecord({
    required String id,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'target_locale') required String targetLocale,
    @JsonKey(fromJson: _statusFromJson) required String status,
    @JsonKey(name: 'workflow_version') @Default(1) int workflowVersion,
    @JsonKey(name: 'state_version') @Default(1) int stateVersion,
    @JsonKey(name: 'active_profile_id') String? activeProfileId,
    @JsonKey(name: 'output_profile_id') String? outputProfileId,
    @JsonKey(name: 'raw_inputs') WorkflowInputs? rawInputs,
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
    @JsonKey(name: 'models_used') Map<String, int>? modelsUsed,
    @JsonKey(name: 'execution_summary')
    ExecutionSummarySnapshot? executionSummary,
    @JsonKey(name: 'metadata') ExecutionMetadata? metadata,
    @JsonKey(name: 'error') String? error,
    @JsonKey(name: 'is_resumable') bool? isResumable,
    @JsonKey(name: 'frozen_context') FrozenContextSnapshot? frozenContext,
    @JsonKey(name: 'frozen_context_storage_path')
    String? frozenContextStoragePath,
    @JsonKey(name: 'context_variables') ContextVariablesDto? contextVariables,
    @JsonKey(name: 'context_variables_storage_path')
    String? contextVariablesStoragePath,
    @JsonKey(name: 'execution_trace')
    List<ExecutionTraceItemDto>? executionTrace,
    @JsonKey(name: 'execution_trace_storage_path')
    String? executionTraceStoragePath,
    @JsonKey(name: 'pdf_report_path') String? pdfReportPath,
    @JsonKey(name: 'source_identity_manifest')
    Map<String, String>? sourceIdentityManifest,
    @JsonKey(name: 'steps') @Default([]) List<ExecutionStep> steps,
    @JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates,
    @JsonKey(name: 'profile_syntheses')
    Map<String, ProfileSynthesisEntryDto>? profileSyntheses,
    @JsonKey(name: 'progress') int? progress,
    @JsonKey(name: 'status_message') String? statusMessage,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'updated_at') String? updatedAt,
    @JsonKey(name: 'completed_at') String? completedAt,
    @JsonKey(name: 'created_by') String? createdBy,
    @JsonKey(name: 'organization_id') String? organizationId,
  }) = _ExecutionRecord;

  /// Instantiates a strictly typed [ExecutionRecord] from raw JSON.
  factory ExecutionRecord.fromJson(Map<String, dynamic> json) =>
      _$ExecutionRecordFromJson(json);

  /// Parses raw JSON string to ExecutionRecord in a background isolate
  /// to prevent Main Thread Jank when handling large payloads.
  static Future<ExecutionRecord> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final Object? decoded = jsonDecode(rawJson);
      if (decoded is! Map) {
        throw TypeError();
      }
      return ExecutionRecord.fromJson(Map.from(decoded));
    });
  }
}
