// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_record.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionRecord {

 String get id;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(fromJson: _statusFromJson) String get status;@JsonKey(name: 'active_profile_id') String? get activeProfileId;@JsonKey(name: 'output_profile_id') String? get outputProfileId;@JsonKey(name: 'raw_inputs') Map<String, dynamic>? get rawInputs;@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? get traceVersion;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'duration_ms') int? get durationMs;@JsonKey(name: 'cost_estimate') double? get costEstimate;@JsonKey(name: 'cumulative_synthesis_tokens') int? get cumulativeSynthesisTokens;@JsonKey(name: 'cumulative_synthesis_cost') double? get cumulativeSynthesisCost;@JsonKey(name: 'models_used') Map<String, int>? get modelsUsed;@JsonKey(name: 'metadata') ExecutionMetadata? get metadata;@JsonKey(name: 'error') String? get error;@JsonKey(name: 'is_resumable') bool? get isResumable;@JsonKey(name: 'frozen_context') Map<String, dynamic>? get frozenContext;@JsonKey(name: 'frozen_context_storage_path') String? get frozenContextStoragePath;@JsonKey(name: 'context_variables') Map<String, dynamic>? get contextVariables;@JsonKey(name: 'context_variables_storage_path') String? get contextVariablesStoragePath;@JsonKey(name: 'execution_trace_storage_path') String? get executionTraceStoragePath;@JsonKey(name: 'pdf_report_path') String? get pdfReportPath;@JsonKey(name: 'source_identity_manifest') Map<String, String>? get sourceIdentityManifest;@JsonKey(name: 'step_states') Map<String, dynamic>? get stepStates;@JsonKey(name: 'profile_syntheses') Map<String, dynamic>? get profileSyntheses;@JsonKey(name: 'results') Map<String, dynamic>? get results;@JsonKey(name: 'progress') int? get progress;@JsonKey(name: 'status_message') String? get statusMessage;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'updated_at') String? get updatedAt;@JsonKey(name: 'completed_at') String? get completedAt;@JsonKey(name: 'created_by') String? get createdBy;@JsonKey(name: 'organization_id') String? get organizationId;/// The strictly typed DTO containing the presentation flat data.
/// Replaces the legacy `results` Map.
@JsonKey(name: 'report_data') ReportDataDto? get reportData;
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionRecordCopyWith<ExecutionRecord> get copyWith => _$ExecutionRecordCopyWithImpl<ExecutionRecord>(this as ExecutionRecord, _$identity);

  /// Serializes this ExecutionRecord to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, targetLocale: $targetLocale, status: $status, activeProfileId: $activeProfileId, outputProfileId: $outputProfileId, rawInputs: $rawInputs, traceVersion: $traceVersion, strictnessLevel: $strictnessLevel, durationMs: $durationMs, costEstimate: $costEstimate, cumulativeSynthesisTokens: $cumulativeSynthesisTokens, cumulativeSynthesisCost: $cumulativeSynthesisCost, modelsUsed: $modelsUsed, metadata: $metadata, error: $error, isResumable: $isResumable, frozenContext: $frozenContext, frozenContextStoragePath: $frozenContextStoragePath, contextVariables: $contextVariables, contextVariablesStoragePath: $contextVariablesStoragePath, executionTraceStoragePath: $executionTraceStoragePath, pdfReportPath: $pdfReportPath, sourceIdentityManifest: $sourceIdentityManifest, stepStates: $stepStates, profileSyntheses: $profileSyntheses, results: $results, progress: $progress, statusMessage: $statusMessage, createdAt: $createdAt, updatedAt: $updatedAt, completedAt: $completedAt, createdBy: $createdBy, organizationId: $organizationId, reportData: $reportData)';
}


}

/// @nodoc
abstract mixin class $ExecutionRecordCopyWith<$Res>  {
  factory $ExecutionRecordCopyWith(ExecutionRecord value, $Res Function(ExecutionRecord) _then) = _$ExecutionRecordCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'active_profile_id') String? activeProfileId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'raw_inputs') Map<String, dynamic>? rawInputs,@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? traceVersion,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'duration_ms') int? durationMs,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'cumulative_synthesis_tokens') int? cumulativeSynthesisTokens,@JsonKey(name: 'cumulative_synthesis_cost') double? cumulativeSynthesisCost,@JsonKey(name: 'models_used') Map<String, int>? modelsUsed,@JsonKey(name: 'metadata') ExecutionMetadata? metadata,@JsonKey(name: 'error') String? error,@JsonKey(name: 'is_resumable') bool? isResumable,@JsonKey(name: 'frozen_context') Map<String, dynamic>? frozenContext,@JsonKey(name: 'frozen_context_storage_path') String? frozenContextStoragePath,@JsonKey(name: 'context_variables') Map<String, dynamic>? contextVariables,@JsonKey(name: 'context_variables_storage_path') String? contextVariablesStoragePath,@JsonKey(name: 'execution_trace_storage_path') String? executionTraceStoragePath,@JsonKey(name: 'pdf_report_path') String? pdfReportPath,@JsonKey(name: 'source_identity_manifest') Map<String, String>? sourceIdentityManifest,@JsonKey(name: 'step_states') Map<String, dynamic>? stepStates,@JsonKey(name: 'profile_syntheses') Map<String, dynamic>? profileSyntheses,@JsonKey(name: 'results') Map<String, dynamic>? results,@JsonKey(name: 'progress') int? progress,@JsonKey(name: 'status_message') String? statusMessage,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'updated_at') String? updatedAt,@JsonKey(name: 'completed_at') String? completedAt,@JsonKey(name: 'created_by') String? createdBy,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'report_data') ReportDataDto? reportData
});


$ExecutionMetadataCopyWith<$Res>? get metadata;$ReportDataDtoCopyWith<$Res>? get reportData;

}
/// @nodoc
class _$ExecutionRecordCopyWithImpl<$Res>
    implements $ExecutionRecordCopyWith<$Res> {
  _$ExecutionRecordCopyWithImpl(this._self, this._then);

  final ExecutionRecord _self;
  final $Res Function(ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? workflowId = null,Object? targetLocale = null,Object? status = null,Object? activeProfileId = freezed,Object? outputProfileId = freezed,Object? rawInputs = freezed,Object? traceVersion = freezed,Object? strictnessLevel = freezed,Object? durationMs = freezed,Object? costEstimate = freezed,Object? cumulativeSynthesisTokens = freezed,Object? cumulativeSynthesisCost = freezed,Object? modelsUsed = freezed,Object? metadata = freezed,Object? error = freezed,Object? isResumable = freezed,Object? frozenContext = freezed,Object? frozenContextStoragePath = freezed,Object? contextVariables = freezed,Object? contextVariablesStoragePath = freezed,Object? executionTraceStoragePath = freezed,Object? pdfReportPath = freezed,Object? sourceIdentityManifest = freezed,Object? stepStates = freezed,Object? profileSyntheses = freezed,Object? results = freezed,Object? progress = freezed,Object? statusMessage = freezed,Object? createdAt = freezed,Object? updatedAt = freezed,Object? completedAt = freezed,Object? createdBy = freezed,Object? organizationId = freezed,Object? reportData = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,activeProfileId: freezed == activeProfileId ? _self.activeProfileId : activeProfileId // ignore: cast_nullable_to_non_nullable
as String?,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,rawInputs: freezed == rawInputs ? _self.rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,traceVersion: freezed == traceVersion ? _self.traceVersion : traceVersion // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,durationMs: freezed == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,cumulativeSynthesisTokens: freezed == cumulativeSynthesisTokens ? _self.cumulativeSynthesisTokens : cumulativeSynthesisTokens // ignore: cast_nullable_to_non_nullable
as int?,cumulativeSynthesisCost: freezed == cumulativeSynthesisCost ? _self.cumulativeSynthesisCost : cumulativeSynthesisCost // ignore: cast_nullable_to_non_nullable
as double?,modelsUsed: freezed == modelsUsed ? _self.modelsUsed : modelsUsed // ignore: cast_nullable_to_non_nullable
as Map<String, int>?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as ExecutionMetadata?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isResumable: freezed == isResumable ? _self.isResumable : isResumable // ignore: cast_nullable_to_non_nullable
as bool?,frozenContext: freezed == frozenContext ? _self.frozenContext : frozenContext // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,frozenContextStoragePath: freezed == frozenContextStoragePath ? _self.frozenContextStoragePath : frozenContextStoragePath // ignore: cast_nullable_to_non_nullable
as String?,contextVariables: freezed == contextVariables ? _self.contextVariables : contextVariables // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,contextVariablesStoragePath: freezed == contextVariablesStoragePath ? _self.contextVariablesStoragePath : contextVariablesStoragePath // ignore: cast_nullable_to_non_nullable
as String?,executionTraceStoragePath: freezed == executionTraceStoragePath ? _self.executionTraceStoragePath : executionTraceStoragePath // ignore: cast_nullable_to_non_nullable
as String?,pdfReportPath: freezed == pdfReportPath ? _self.pdfReportPath : pdfReportPath // ignore: cast_nullable_to_non_nullable
as String?,sourceIdentityManifest: freezed == sourceIdentityManifest ? _self.sourceIdentityManifest : sourceIdentityManifest // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,stepStates: freezed == stepStates ? _self.stepStates : stepStates // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,profileSyntheses: freezed == profileSyntheses ? _self.profileSyntheses : profileSyntheses // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,results: freezed == results ? _self.results : results // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,progress: freezed == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int?,statusMessage: freezed == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: freezed == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,reportData: freezed == reportData ? _self.reportData : reportData // ignore: cast_nullable_to_non_nullable
as ReportDataDto?,
  ));
}
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetadataCopyWith<$Res>? get metadata {
    if (_self.metadata == null) {
    return null;
  }

  return $ExecutionMetadataCopyWith<$Res>(_self.metadata!, (value) {
    return _then(_self.copyWith(metadata: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportDataDtoCopyWith<$Res>? get reportData {
    if (_self.reportData == null) {
    return null;
  }

  return $ReportDataDtoCopyWith<$Res>(_self.reportData!, (value) {
    return _then(_self.copyWith(reportData: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionRecord].
extension ExecutionRecordPatterns on ExecutionRecord {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionRecord value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionRecord value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionRecord():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionRecord value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'active_profile_id')  String? activeProfileId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'raw_inputs')  Map<String, dynamic>? rawInputs, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'cumulative_synthesis_tokens')  int? cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost')  double? cumulativeSynthesisCost, @JsonKey(name: 'models_used')  Map<String, int>? modelsUsed, @JsonKey(name: 'metadata')  ExecutionMetadata? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  Map<String, dynamic>? frozenContext, @JsonKey(name: 'frozen_context_storage_path')  String? frozenContextStoragePath, @JsonKey(name: 'context_variables')  Map<String, dynamic>? contextVariables, @JsonKey(name: 'context_variables_storage_path')  String? contextVariablesStoragePath, @JsonKey(name: 'execution_trace_storage_path')  String? executionTraceStoragePath, @JsonKey(name: 'pdf_report_path')  String? pdfReportPath, @JsonKey(name: 'source_identity_manifest')  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'step_states')  Map<String, dynamic>? stepStates, @JsonKey(name: 'profile_syntheses')  Map<String, dynamic>? profileSyntheses, @JsonKey(name: 'results')  Map<String, dynamic>? results, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'report_data')  ReportDataDto? reportData)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.targetLocale,_that.status,_that.activeProfileId,_that.outputProfileId,_that.rawInputs,_that.traceVersion,_that.strictnessLevel,_that.durationMs,_that.costEstimate,_that.cumulativeSynthesisTokens,_that.cumulativeSynthesisCost,_that.modelsUsed,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.frozenContextStoragePath,_that.contextVariables,_that.contextVariablesStoragePath,_that.executionTraceStoragePath,_that.pdfReportPath,_that.sourceIdentityManifest,_that.stepStates,_that.profileSyntheses,_that.results,_that.progress,_that.statusMessage,_that.createdAt,_that.updatedAt,_that.completedAt,_that.createdBy,_that.organizationId,_that.reportData);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'active_profile_id')  String? activeProfileId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'raw_inputs')  Map<String, dynamic>? rawInputs, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'cumulative_synthesis_tokens')  int? cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost')  double? cumulativeSynthesisCost, @JsonKey(name: 'models_used')  Map<String, int>? modelsUsed, @JsonKey(name: 'metadata')  ExecutionMetadata? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  Map<String, dynamic>? frozenContext, @JsonKey(name: 'frozen_context_storage_path')  String? frozenContextStoragePath, @JsonKey(name: 'context_variables')  Map<String, dynamic>? contextVariables, @JsonKey(name: 'context_variables_storage_path')  String? contextVariablesStoragePath, @JsonKey(name: 'execution_trace_storage_path')  String? executionTraceStoragePath, @JsonKey(name: 'pdf_report_path')  String? pdfReportPath, @JsonKey(name: 'source_identity_manifest')  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'step_states')  Map<String, dynamic>? stepStates, @JsonKey(name: 'profile_syntheses')  Map<String, dynamic>? profileSyntheses, @JsonKey(name: 'results')  Map<String, dynamic>? results, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'report_data')  ReportDataDto? reportData)  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord():
return $default(_that.id,_that.workflowId,_that.targetLocale,_that.status,_that.activeProfileId,_that.outputProfileId,_that.rawInputs,_that.traceVersion,_that.strictnessLevel,_that.durationMs,_that.costEstimate,_that.cumulativeSynthesisTokens,_that.cumulativeSynthesisCost,_that.modelsUsed,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.frozenContextStoragePath,_that.contextVariables,_that.contextVariablesStoragePath,_that.executionTraceStoragePath,_that.pdfReportPath,_that.sourceIdentityManifest,_that.stepStates,_that.profileSyntheses,_that.results,_that.progress,_that.statusMessage,_that.createdAt,_that.updatedAt,_that.completedAt,_that.createdBy,_that.organizationId,_that.reportData);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'active_profile_id')  String? activeProfileId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'raw_inputs')  Map<String, dynamic>? rawInputs, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'cumulative_synthesis_tokens')  int? cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost')  double? cumulativeSynthesisCost, @JsonKey(name: 'models_used')  Map<String, int>? modelsUsed, @JsonKey(name: 'metadata')  ExecutionMetadata? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  Map<String, dynamic>? frozenContext, @JsonKey(name: 'frozen_context_storage_path')  String? frozenContextStoragePath, @JsonKey(name: 'context_variables')  Map<String, dynamic>? contextVariables, @JsonKey(name: 'context_variables_storage_path')  String? contextVariablesStoragePath, @JsonKey(name: 'execution_trace_storage_path')  String? executionTraceStoragePath, @JsonKey(name: 'pdf_report_path')  String? pdfReportPath, @JsonKey(name: 'source_identity_manifest')  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'step_states')  Map<String, dynamic>? stepStates, @JsonKey(name: 'profile_syntheses')  Map<String, dynamic>? profileSyntheses, @JsonKey(name: 'results')  Map<String, dynamic>? results, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'report_data')  ReportDataDto? reportData)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.targetLocale,_that.status,_that.activeProfileId,_that.outputProfileId,_that.rawInputs,_that.traceVersion,_that.strictnessLevel,_that.durationMs,_that.costEstimate,_that.cumulativeSynthesisTokens,_that.cumulativeSynthesisCost,_that.modelsUsed,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.frozenContextStoragePath,_that.contextVariables,_that.contextVariablesStoragePath,_that.executionTraceStoragePath,_that.pdfReportPath,_that.sourceIdentityManifest,_that.stepStates,_that.profileSyntheses,_that.results,_that.progress,_that.statusMessage,_that.createdAt,_that.updatedAt,_that.completedAt,_that.createdBy,_that.organizationId,_that.reportData);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionRecord extends ExecutionRecord {
  const _ExecutionRecord({required this.id, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'target_locale') required this.targetLocale, @JsonKey(fromJson: _statusFromJson) required this.status, @JsonKey(name: 'active_profile_id') this.activeProfileId, @JsonKey(name: 'output_profile_id') this.outputProfileId, @JsonKey(name: 'raw_inputs') final  Map<String, dynamic>? rawInputs, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) this.traceVersion, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'duration_ms') this.durationMs, @JsonKey(name: 'cost_estimate') this.costEstimate, @JsonKey(name: 'cumulative_synthesis_tokens') this.cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost') this.cumulativeSynthesisCost, @JsonKey(name: 'models_used') final  Map<String, int>? modelsUsed, @JsonKey(name: 'metadata') this.metadata, @JsonKey(name: 'error') this.error, @JsonKey(name: 'is_resumable') this.isResumable, @JsonKey(name: 'frozen_context') final  Map<String, dynamic>? frozenContext, @JsonKey(name: 'frozen_context_storage_path') this.frozenContextStoragePath, @JsonKey(name: 'context_variables') final  Map<String, dynamic>? contextVariables, @JsonKey(name: 'context_variables_storage_path') this.contextVariablesStoragePath, @JsonKey(name: 'execution_trace_storage_path') this.executionTraceStoragePath, @JsonKey(name: 'pdf_report_path') this.pdfReportPath, @JsonKey(name: 'source_identity_manifest') final  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'step_states') final  Map<String, dynamic>? stepStates, @JsonKey(name: 'profile_syntheses') final  Map<String, dynamic>? profileSyntheses, @JsonKey(name: 'results') final  Map<String, dynamic>? results, @JsonKey(name: 'progress') this.progress, @JsonKey(name: 'status_message') this.statusMessage, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'updated_at') this.updatedAt, @JsonKey(name: 'completed_at') this.completedAt, @JsonKey(name: 'created_by') this.createdBy, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'report_data') this.reportData}): _rawInputs = rawInputs,_modelsUsed = modelsUsed,_frozenContext = frozenContext,_contextVariables = contextVariables,_sourceIdentityManifest = sourceIdentityManifest,_stepStates = stepStates,_profileSyntheses = profileSyntheses,_results = results,super._();
  factory _ExecutionRecord.fromJson(Map<String, dynamic> json) => _$ExecutionRecordFromJson(json);

@override final  String id;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(fromJson: _statusFromJson) final  String status;
@override@JsonKey(name: 'active_profile_id') final  String? activeProfileId;
@override@JsonKey(name: 'output_profile_id') final  String? outputProfileId;
 final  Map<String, dynamic>? _rawInputs;
@override@JsonKey(name: 'raw_inputs') Map<String, dynamic>? get rawInputs {
  final value = _rawInputs;
  if (value == null) return null;
  if (_rawInputs is EqualUnmodifiableMapView) return _rawInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) final  String? traceVersion;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'duration_ms') final  int? durationMs;
@override@JsonKey(name: 'cost_estimate') final  double? costEstimate;
@override@JsonKey(name: 'cumulative_synthesis_tokens') final  int? cumulativeSynthesisTokens;
@override@JsonKey(name: 'cumulative_synthesis_cost') final  double? cumulativeSynthesisCost;
 final  Map<String, int>? _modelsUsed;
@override@JsonKey(name: 'models_used') Map<String, int>? get modelsUsed {
  final value = _modelsUsed;
  if (value == null) return null;
  if (_modelsUsed is EqualUnmodifiableMapView) return _modelsUsed;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'metadata') final  ExecutionMetadata? metadata;
@override@JsonKey(name: 'error') final  String? error;
@override@JsonKey(name: 'is_resumable') final  bool? isResumable;
 final  Map<String, dynamic>? _frozenContext;
@override@JsonKey(name: 'frozen_context') Map<String, dynamic>? get frozenContext {
  final value = _frozenContext;
  if (value == null) return null;
  if (_frozenContext is EqualUnmodifiableMapView) return _frozenContext;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'frozen_context_storage_path') final  String? frozenContextStoragePath;
 final  Map<String, dynamic>? _contextVariables;
@override@JsonKey(name: 'context_variables') Map<String, dynamic>? get contextVariables {
  final value = _contextVariables;
  if (value == null) return null;
  if (_contextVariables is EqualUnmodifiableMapView) return _contextVariables;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'context_variables_storage_path') final  String? contextVariablesStoragePath;
@override@JsonKey(name: 'execution_trace_storage_path') final  String? executionTraceStoragePath;
@override@JsonKey(name: 'pdf_report_path') final  String? pdfReportPath;
 final  Map<String, String>? _sourceIdentityManifest;
@override@JsonKey(name: 'source_identity_manifest') Map<String, String>? get sourceIdentityManifest {
  final value = _sourceIdentityManifest;
  if (value == null) return null;
  if (_sourceIdentityManifest is EqualUnmodifiableMapView) return _sourceIdentityManifest;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepStates;
@override@JsonKey(name: 'step_states') Map<String, dynamic>? get stepStates {
  final value = _stepStates;
  if (value == null) return null;
  if (_stepStates is EqualUnmodifiableMapView) return _stepStates;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _profileSyntheses;
@override@JsonKey(name: 'profile_syntheses') Map<String, dynamic>? get profileSyntheses {
  final value = _profileSyntheses;
  if (value == null) return null;
  if (_profileSyntheses is EqualUnmodifiableMapView) return _profileSyntheses;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _results;
@override@JsonKey(name: 'results') Map<String, dynamic>? get results {
  final value = _results;
  if (value == null) return null;
  if (_results is EqualUnmodifiableMapView) return _results;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'progress') final  int? progress;
@override@JsonKey(name: 'status_message') final  String? statusMessage;
@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'updated_at') final  String? updatedAt;
@override@JsonKey(name: 'completed_at') final  String? completedAt;
@override@JsonKey(name: 'created_by') final  String? createdBy;
@override@JsonKey(name: 'organization_id') final  String? organizationId;
/// The strictly typed DTO containing the presentation flat data.
/// Replaces the legacy `results` Map.
@override@JsonKey(name: 'report_data') final  ReportDataDto? reportData;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionRecordCopyWith<_ExecutionRecord> get copyWith => __$ExecutionRecordCopyWithImpl<_ExecutionRecord>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionRecordToJson(this, );
}



@override
String toString() {
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, targetLocale: $targetLocale, status: $status, activeProfileId: $activeProfileId, outputProfileId: $outputProfileId, rawInputs: $rawInputs, traceVersion: $traceVersion, strictnessLevel: $strictnessLevel, durationMs: $durationMs, costEstimate: $costEstimate, cumulativeSynthesisTokens: $cumulativeSynthesisTokens, cumulativeSynthesisCost: $cumulativeSynthesisCost, modelsUsed: $modelsUsed, metadata: $metadata, error: $error, isResumable: $isResumable, frozenContext: $frozenContext, frozenContextStoragePath: $frozenContextStoragePath, contextVariables: $contextVariables, contextVariablesStoragePath: $contextVariablesStoragePath, executionTraceStoragePath: $executionTraceStoragePath, pdfReportPath: $pdfReportPath, sourceIdentityManifest: $sourceIdentityManifest, stepStates: $stepStates, profileSyntheses: $profileSyntheses, results: $results, progress: $progress, statusMessage: $statusMessage, createdAt: $createdAt, updatedAt: $updatedAt, completedAt: $completedAt, createdBy: $createdBy, organizationId: $organizationId, reportData: $reportData)';
}


}

/// @nodoc
abstract mixin class _$ExecutionRecordCopyWith<$Res> implements $ExecutionRecordCopyWith<$Res> {
  factory _$ExecutionRecordCopyWith(_ExecutionRecord value, $Res Function(_ExecutionRecord) _then) = __$ExecutionRecordCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'active_profile_id') String? activeProfileId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'raw_inputs') Map<String, dynamic>? rawInputs,@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? traceVersion,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'duration_ms') int? durationMs,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'cumulative_synthesis_tokens') int? cumulativeSynthesisTokens,@JsonKey(name: 'cumulative_synthesis_cost') double? cumulativeSynthesisCost,@JsonKey(name: 'models_used') Map<String, int>? modelsUsed,@JsonKey(name: 'metadata') ExecutionMetadata? metadata,@JsonKey(name: 'error') String? error,@JsonKey(name: 'is_resumable') bool? isResumable,@JsonKey(name: 'frozen_context') Map<String, dynamic>? frozenContext,@JsonKey(name: 'frozen_context_storage_path') String? frozenContextStoragePath,@JsonKey(name: 'context_variables') Map<String, dynamic>? contextVariables,@JsonKey(name: 'context_variables_storage_path') String? contextVariablesStoragePath,@JsonKey(name: 'execution_trace_storage_path') String? executionTraceStoragePath,@JsonKey(name: 'pdf_report_path') String? pdfReportPath,@JsonKey(name: 'source_identity_manifest') Map<String, String>? sourceIdentityManifest,@JsonKey(name: 'step_states') Map<String, dynamic>? stepStates,@JsonKey(name: 'profile_syntheses') Map<String, dynamic>? profileSyntheses,@JsonKey(name: 'results') Map<String, dynamic>? results,@JsonKey(name: 'progress') int? progress,@JsonKey(name: 'status_message') String? statusMessage,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'updated_at') String? updatedAt,@JsonKey(name: 'completed_at') String? completedAt,@JsonKey(name: 'created_by') String? createdBy,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'report_data') ReportDataDto? reportData
});


@override $ExecutionMetadataCopyWith<$Res>? get metadata;@override $ReportDataDtoCopyWith<$Res>? get reportData;

}
/// @nodoc
class __$ExecutionRecordCopyWithImpl<$Res>
    implements _$ExecutionRecordCopyWith<$Res> {
  __$ExecutionRecordCopyWithImpl(this._self, this._then);

  final _ExecutionRecord _self;
  final $Res Function(_ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? workflowId = null,Object? targetLocale = null,Object? status = null,Object? activeProfileId = freezed,Object? outputProfileId = freezed,Object? rawInputs = freezed,Object? traceVersion = freezed,Object? strictnessLevel = freezed,Object? durationMs = freezed,Object? costEstimate = freezed,Object? cumulativeSynthesisTokens = freezed,Object? cumulativeSynthesisCost = freezed,Object? modelsUsed = freezed,Object? metadata = freezed,Object? error = freezed,Object? isResumable = freezed,Object? frozenContext = freezed,Object? frozenContextStoragePath = freezed,Object? contextVariables = freezed,Object? contextVariablesStoragePath = freezed,Object? executionTraceStoragePath = freezed,Object? pdfReportPath = freezed,Object? sourceIdentityManifest = freezed,Object? stepStates = freezed,Object? profileSyntheses = freezed,Object? results = freezed,Object? progress = freezed,Object? statusMessage = freezed,Object? createdAt = freezed,Object? updatedAt = freezed,Object? completedAt = freezed,Object? createdBy = freezed,Object? organizationId = freezed,Object? reportData = freezed,}) {
  return _then(_ExecutionRecord(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,activeProfileId: freezed == activeProfileId ? _self.activeProfileId : activeProfileId // ignore: cast_nullable_to_non_nullable
as String?,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,rawInputs: freezed == rawInputs ? _self._rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,traceVersion: freezed == traceVersion ? _self.traceVersion : traceVersion // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,durationMs: freezed == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,cumulativeSynthesisTokens: freezed == cumulativeSynthesisTokens ? _self.cumulativeSynthesisTokens : cumulativeSynthesisTokens // ignore: cast_nullable_to_non_nullable
as int?,cumulativeSynthesisCost: freezed == cumulativeSynthesisCost ? _self.cumulativeSynthesisCost : cumulativeSynthesisCost // ignore: cast_nullable_to_non_nullable
as double?,modelsUsed: freezed == modelsUsed ? _self._modelsUsed : modelsUsed // ignore: cast_nullable_to_non_nullable
as Map<String, int>?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as ExecutionMetadata?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isResumable: freezed == isResumable ? _self.isResumable : isResumable // ignore: cast_nullable_to_non_nullable
as bool?,frozenContext: freezed == frozenContext ? _self._frozenContext : frozenContext // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,frozenContextStoragePath: freezed == frozenContextStoragePath ? _self.frozenContextStoragePath : frozenContextStoragePath // ignore: cast_nullable_to_non_nullable
as String?,contextVariables: freezed == contextVariables ? _self._contextVariables : contextVariables // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,contextVariablesStoragePath: freezed == contextVariablesStoragePath ? _self.contextVariablesStoragePath : contextVariablesStoragePath // ignore: cast_nullable_to_non_nullable
as String?,executionTraceStoragePath: freezed == executionTraceStoragePath ? _self.executionTraceStoragePath : executionTraceStoragePath // ignore: cast_nullable_to_non_nullable
as String?,pdfReportPath: freezed == pdfReportPath ? _self.pdfReportPath : pdfReportPath // ignore: cast_nullable_to_non_nullable
as String?,sourceIdentityManifest: freezed == sourceIdentityManifest ? _self._sourceIdentityManifest : sourceIdentityManifest // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,stepStates: freezed == stepStates ? _self._stepStates : stepStates // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,profileSyntheses: freezed == profileSyntheses ? _self._profileSyntheses : profileSyntheses // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,results: freezed == results ? _self._results : results // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,progress: freezed == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int?,statusMessage: freezed == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: freezed == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,reportData: freezed == reportData ? _self.reportData : reportData // ignore: cast_nullable_to_non_nullable
as ReportDataDto?,
  ));
}

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetadataCopyWith<$Res>? get metadata {
    if (_self.metadata == null) {
    return null;
  }

  return $ExecutionMetadataCopyWith<$Res>(_self.metadata!, (value) {
    return _then(_self.copyWith(metadata: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportDataDtoCopyWith<$Res>? get reportData {
    if (_self.reportData == null) {
    return null;
  }

  return $ReportDataDtoCopyWith<$Res>(_self.reportData!, (value) {
    return _then(_self.copyWith(reportData: value));
  });
}
}

// dart format on
