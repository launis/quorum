// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_data_v2_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReportDataDto {

@JsonKey(name: 'execution_id') String get executionId;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'scoring_strategy') String? get scoringStrategy;@JsonKey(name: 'user_name') String? get userName;@JsonKey(name: 'scoring_engine_name') String? get scoringEngineName;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'local_time_str') String? get localTimeStr;@JsonKey(name: 'custom_preface_md') String? get customPrefaceMd;@JsonKey(name: 'profile_id') String get profileId;@JsonKey(name: 'profile_name') I18nText? get profileName;@JsonKey(name: 'available_profiles') Map<String, I18nText> get availableProfiles;@JsonKey(name: 'global_score') double? get globalScore;@JsonKey(name: 'has_warning') bool get hasWarning;@JsonKey(name: 'global_metrics') ExecutionMetricsDTO? get globalMetrics;@JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? get globalSynthesis;@JsonKey(name: 'results') List<AtomResultDTO> get results;@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> get hydratedReferences;@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto>? get evaluativeMatrices;@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto>? get informationalMatrices;@JsonKey(name: 'content_blocks') List<Map<String, dynamic>>? get contentBlocks;@JsonKey(name: 'visible_metadata') List<String> get visibleMetadata; List<ReportLayoutDto> get layouts;@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'org_name') String? get orgName;@JsonKey(name: 'cost_estimate') double? get costEstimate;@JsonKey(name: 'total_tokens') int? get totalTokens;@JsonKey(name: 'prompt_tokens') int? get promptTokens;@JsonKey(name: 'completion_tokens') int? get completionTokens;@JsonKey(name: 'reasoning_tokens') int? get reasoningTokens;@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> get mcpToolAudit;@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>>? get groupedExtensions;@JsonKey(name: 'penalties_applied') List<String> get penaltiesApplied;
/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportDataDtoCopyWith<ReportDataDto> get copyWith => _$ReportDataDtoCopyWithImpl<ReportDataDto>(this as ReportDataDto, _$identity);

  /// Serializes this ReportDataDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportDataDto(executionId: $executionId, workflowId: $workflowId, scoringStrategy: $scoringStrategy, userName: $userName, scoringEngineName: $scoringEngineName, strictnessLevel: $strictnessLevel, localTimeStr: $localTimeStr, customPrefaceMd: $customPrefaceMd, profileId: $profileId, profileName: $profileName, availableProfiles: $availableProfiles, globalScore: $globalScore, hasWarning: $hasWarning, globalMetrics: $globalMetrics, globalSynthesis: $globalSynthesis, results: $results, hydratedReferences: $hydratedReferences, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices, contentBlocks: $contentBlocks, visibleMetadata: $visibleMetadata, layouts: $layouts, matrixVisibleColumns: $matrixVisibleColumns, createdAt: $createdAt, orgName: $orgName, costEstimate: $costEstimate, totalTokens: $totalTokens, promptTokens: $promptTokens, completionTokens: $completionTokens, reasoningTokens: $reasoningTokens, mcpToolAudit: $mcpToolAudit, groupedExtensions: $groupedExtensions, penaltiesApplied: $penaltiesApplied)';
}


}

/// @nodoc
abstract mixin class $ReportDataDtoCopyWith<$Res>  {
  factory $ReportDataDtoCopyWith(ReportDataDto value, $Res Function(ReportDataDto) _then) = _$ReportDataDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'scoring_strategy') String? scoringStrategy,@JsonKey(name: 'user_name') String? userName,@JsonKey(name: 'scoring_engine_name') String? scoringEngineName,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'local_time_str') String? localTimeStr,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd,@JsonKey(name: 'profile_id') String profileId,@JsonKey(name: 'profile_name') I18nText? profileName,@JsonKey(name: 'available_profiles') Map<String, I18nText> availableProfiles,@JsonKey(name: 'global_score') double? globalScore,@JsonKey(name: 'has_warning') bool hasWarning,@JsonKey(name: 'global_metrics') ExecutionMetricsDTO? globalMetrics,@JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? globalSynthesis,@JsonKey(name: 'results') List<AtomResultDTO> results,@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> hydratedReferences,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto>? evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto>? informationalMatrices,@JsonKey(name: 'content_blocks') List<Map<String, dynamic>>? contentBlocks,@JsonKey(name: 'visible_metadata') List<String> visibleMetadata, List<ReportLayoutDto> layouts,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'org_name') String? orgName,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'total_tokens') int? totalTokens,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens,@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> mcpToolAudit,@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>>? groupedExtensions,@JsonKey(name: 'penalties_applied') List<String> penaltiesApplied
});


$I18nTextCopyWith<$Res>? get profileName;$ExecutionMetricsDTOCopyWith<$Res>? get globalMetrics;$GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis;

}
/// @nodoc
class _$ReportDataDtoCopyWithImpl<$Res>
    implements $ReportDataDtoCopyWith<$Res> {
  _$ReportDataDtoCopyWithImpl(this._self, this._then);

  final ReportDataDto _self;
  final $Res Function(ReportDataDto) _then;

/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executionId = null,Object? workflowId = null,Object? scoringStrategy = freezed,Object? userName = freezed,Object? scoringEngineName = freezed,Object? strictnessLevel = freezed,Object? localTimeStr = freezed,Object? customPrefaceMd = freezed,Object? profileId = null,Object? profileName = freezed,Object? availableProfiles = null,Object? globalScore = freezed,Object? hasWarning = null,Object? globalMetrics = freezed,Object? globalSynthesis = freezed,Object? results = null,Object? hydratedReferences = null,Object? evaluativeMatrices = freezed,Object? informationalMatrices = freezed,Object? contentBlocks = freezed,Object? visibleMetadata = null,Object? layouts = null,Object? matrixVisibleColumns = null,Object? createdAt = freezed,Object? orgName = freezed,Object? costEstimate = freezed,Object? totalTokens = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? reasoningTokens = freezed,Object? mcpToolAudit = null,Object? groupedExtensions = freezed,Object? penaltiesApplied = null,}) {
  return _then(_self.copyWith(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as String?,userName: freezed == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String?,scoringEngineName: freezed == scoringEngineName ? _self.scoringEngineName : scoringEngineName // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,localTimeStr: freezed == localTimeStr ? _self.localTimeStr : localTimeStr // ignore: cast_nullable_to_non_nullable
as String?,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,profileName: freezed == profileName ? _self.profileName : profileName // ignore: cast_nullable_to_non_nullable
as I18nText?,availableProfiles: null == availableProfiles ? _self.availableProfiles : availableProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,hasWarning: null == hasWarning ? _self.hasWarning : hasWarning // ignore: cast_nullable_to_non_nullable
as bool,globalMetrics: freezed == globalMetrics ? _self.globalMetrics : globalMetrics // ignore: cast_nullable_to_non_nullable
as ExecutionMetricsDTO?,globalSynthesis: freezed == globalSynthesis ? _self.globalSynthesis : globalSynthesis // ignore: cast_nullable_to_non_nullable
as GlobalSynthesisDTO?,results: null == results ? _self.results : results // ignore: cast_nullable_to_non_nullable
as List<AtomResultDTO>,hydratedReferences: null == hydratedReferences ? _self.hydratedReferences : hydratedReferences // ignore: cast_nullable_to_non_nullable
as Map<String, HydratedAtomDTO>,evaluativeMatrices: freezed == evaluativeMatrices ? _self.evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>?,informationalMatrices: freezed == informationalMatrices ? _self.informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>?,contentBlocks: freezed == contentBlocks ? _self.contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>?,visibleMetadata: null == visibleMetadata ? _self.visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<ReportLayoutDto>,matrixVisibleColumns: null == matrixVisibleColumns ? _self.matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,orgName: freezed == orgName ? _self.orgName : orgName // ignore: cast_nullable_to_non_nullable
as String?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,totalTokens: freezed == totalTokens ? _self.totalTokens : totalTokens // ignore: cast_nullable_to_non_nullable
as int?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,mcpToolAudit: null == mcpToolAudit ? _self.mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<McpAuditTraceDto>,groupedExtensions: freezed == groupedExtensions ? _self.groupedExtensions : groupedExtensions // ignore: cast_nullable_to_non_nullable
as Map<String, List<dynamic>>?,penaltiesApplied: null == penaltiesApplied ? _self.penaltiesApplied : penaltiesApplied // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}
/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get profileName {
    if (_self.profileName == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.profileName!, (value) {
    return _then(_self.copyWith(profileName: value));
  });
}/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetricsDTOCopyWith<$Res>? get globalMetrics {
    if (_self.globalMetrics == null) {
    return null;
  }

  return $ExecutionMetricsDTOCopyWith<$Res>(_self.globalMetrics!, (value) {
    return _then(_self.copyWith(globalMetrics: value));
  });
}/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis {
    if (_self.globalSynthesis == null) {
    return null;
  }

  return $GlobalSynthesisDTOCopyWith<$Res>(_self.globalSynthesis!, (value) {
    return _then(_self.copyWith(globalSynthesis: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportDataDto].
extension ReportDataDtoPatterns on ReportDataDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportDataDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportDataDto value)  $default,){
final _that = this;
switch (_that) {
case _ReportDataDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportDataDto value)?  $default,){
final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'scoring_strategy')  String? scoringStrategy, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'scoring_engine_name')  String? scoringEngineName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'local_time_str')  String? localTimeStr, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'global_metrics')  ExecutionMetricsDTO? globalMetrics, @JsonKey(name: 'global_synthesis')  GlobalSynthesisDTO? globalSynthesis, @JsonKey(name: 'results')  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references')  Map<String, HydratedAtomDTO> hydratedReferences, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto>? evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto>? informationalMatrices, @JsonKey(name: 'content_blocks')  List<Map<String, dynamic>>? contentBlocks, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata,  List<ReportLayoutDto> layouts, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<McpAuditTraceDto> mcpToolAudit, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>>? groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
return $default(_that.executionId,_that.workflowId,_that.scoringStrategy,_that.userName,_that.scoringEngineName,_that.strictnessLevel,_that.localTimeStr,_that.customPrefaceMd,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.hasWarning,_that.globalMetrics,_that.globalSynthesis,_that.results,_that.hydratedReferences,_that.evaluativeMatrices,_that.informationalMatrices,_that.contentBlocks,_that.visibleMetadata,_that.layouts,_that.matrixVisibleColumns,_that.createdAt,_that.orgName,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.groupedExtensions,_that.penaltiesApplied);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'scoring_strategy')  String? scoringStrategy, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'scoring_engine_name')  String? scoringEngineName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'local_time_str')  String? localTimeStr, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'global_metrics')  ExecutionMetricsDTO? globalMetrics, @JsonKey(name: 'global_synthesis')  GlobalSynthesisDTO? globalSynthesis, @JsonKey(name: 'results')  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references')  Map<String, HydratedAtomDTO> hydratedReferences, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto>? evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto>? informationalMatrices, @JsonKey(name: 'content_blocks')  List<Map<String, dynamic>>? contentBlocks, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata,  List<ReportLayoutDto> layouts, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<McpAuditTraceDto> mcpToolAudit, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>>? groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied)  $default,) {final _that = this;
switch (_that) {
case _ReportDataDto():
return $default(_that.executionId,_that.workflowId,_that.scoringStrategy,_that.userName,_that.scoringEngineName,_that.strictnessLevel,_that.localTimeStr,_that.customPrefaceMd,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.hasWarning,_that.globalMetrics,_that.globalSynthesis,_that.results,_that.hydratedReferences,_that.evaluativeMatrices,_that.informationalMatrices,_that.contentBlocks,_that.visibleMetadata,_that.layouts,_that.matrixVisibleColumns,_that.createdAt,_that.orgName,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.groupedExtensions,_that.penaltiesApplied);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'scoring_strategy')  String? scoringStrategy, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'scoring_engine_name')  String? scoringEngineName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'local_time_str')  String? localTimeStr, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'global_metrics')  ExecutionMetricsDTO? globalMetrics, @JsonKey(name: 'global_synthesis')  GlobalSynthesisDTO? globalSynthesis, @JsonKey(name: 'results')  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references')  Map<String, HydratedAtomDTO> hydratedReferences, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto>? evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto>? informationalMatrices, @JsonKey(name: 'content_blocks')  List<Map<String, dynamic>>? contentBlocks, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata,  List<ReportLayoutDto> layouts, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<McpAuditTraceDto> mcpToolAudit, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>>? groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied)?  $default,) {final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
return $default(_that.executionId,_that.workflowId,_that.scoringStrategy,_that.userName,_that.scoringEngineName,_that.strictnessLevel,_that.localTimeStr,_that.customPrefaceMd,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.hasWarning,_that.globalMetrics,_that.globalSynthesis,_that.results,_that.hydratedReferences,_that.evaluativeMatrices,_that.informationalMatrices,_that.contentBlocks,_that.visibleMetadata,_that.layouts,_that.matrixVisibleColumns,_that.createdAt,_that.orgName,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.groupedExtensions,_that.penaltiesApplied);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportDataDto implements ReportDataDto {
  const _ReportDataDto({@JsonKey(name: 'execution_id') required this.executionId, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'user_name') this.userName, @JsonKey(name: 'scoring_engine_name') this.scoringEngineName, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'local_time_str') this.localTimeStr, @JsonKey(name: 'custom_preface_md') this.customPrefaceMd, @JsonKey(name: 'profile_id') required this.profileId, @JsonKey(name: 'profile_name') this.profileName, @JsonKey(name: 'available_profiles') final  Map<String, I18nText> availableProfiles = const {}, @JsonKey(name: 'global_score') this.globalScore, @JsonKey(name: 'has_warning') this.hasWarning = false, @JsonKey(name: 'global_metrics') this.globalMetrics, @JsonKey(name: 'global_synthesis') this.globalSynthesis, @JsonKey(name: 'results') final  List<AtomResultDTO> results = const [], @JsonKey(name: 'hydrated_references') final  Map<String, HydratedAtomDTO> hydratedReferences = const {}, @JsonKey(name: 'evaluative_matrices') final  List<MatrixScorecardRowDto>? evaluativeMatrices, @JsonKey(name: 'informational_matrices') final  List<MatrixScorecardRowDto>? informationalMatrices, @JsonKey(name: 'content_blocks') final  List<Map<String, dynamic>>? contentBlocks, @JsonKey(name: 'visible_metadata') final  List<String> visibleMetadata = const [], final  List<ReportLayoutDto> layouts = const [], @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const [], @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'org_name') this.orgName, @JsonKey(name: 'cost_estimate') this.costEstimate, @JsonKey(name: 'total_tokens') this.totalTokens, @JsonKey(name: 'prompt_tokens') this.promptTokens, @JsonKey(name: 'completion_tokens') this.completionTokens, @JsonKey(name: 'reasoning_tokens') this.reasoningTokens, @JsonKey(name: 'mcp_tool_audit') final  List<McpAuditTraceDto> mcpToolAudit = const [], @JsonKey(name: 'grouped_extensions') final  Map<String, List<dynamic>>? groupedExtensions, @JsonKey(name: 'penalties_applied') final  List<String> penaltiesApplied = const []}): _availableProfiles = availableProfiles,_results = results,_hydratedReferences = hydratedReferences,_evaluativeMatrices = evaluativeMatrices,_informationalMatrices = informationalMatrices,_contentBlocks = contentBlocks,_visibleMetadata = visibleMetadata,_layouts = layouts,_matrixVisibleColumns = matrixVisibleColumns,_mcpToolAudit = mcpToolAudit,_groupedExtensions = groupedExtensions,_penaltiesApplied = penaltiesApplied;
  factory _ReportDataDto.fromJson(Map<String, dynamic> json) => _$ReportDataDtoFromJson(json);

@override@JsonKey(name: 'execution_id') final  String executionId;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'scoring_strategy') final  String? scoringStrategy;
@override@JsonKey(name: 'user_name') final  String? userName;
@override@JsonKey(name: 'scoring_engine_name') final  String? scoringEngineName;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'local_time_str') final  String? localTimeStr;
@override@JsonKey(name: 'custom_preface_md') final  String? customPrefaceMd;
@override@JsonKey(name: 'profile_id') final  String profileId;
@override@JsonKey(name: 'profile_name') final  I18nText? profileName;
 final  Map<String, I18nText> _availableProfiles;
@override@JsonKey(name: 'available_profiles') Map<String, I18nText> get availableProfiles {
  if (_availableProfiles is EqualUnmodifiableMapView) return _availableProfiles;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_availableProfiles);
}

@override@JsonKey(name: 'global_score') final  double? globalScore;
@override@JsonKey(name: 'has_warning') final  bool hasWarning;
@override@JsonKey(name: 'global_metrics') final  ExecutionMetricsDTO? globalMetrics;
@override@JsonKey(name: 'global_synthesis') final  GlobalSynthesisDTO? globalSynthesis;
 final  List<AtomResultDTO> _results;
@override@JsonKey(name: 'results') List<AtomResultDTO> get results {
  if (_results is EqualUnmodifiableListView) return _results;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_results);
}

 final  Map<String, HydratedAtomDTO> _hydratedReferences;
@override@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> get hydratedReferences {
  if (_hydratedReferences is EqualUnmodifiableMapView) return _hydratedReferences;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_hydratedReferences);
}

 final  List<MatrixScorecardRowDto>? _evaluativeMatrices;
@override@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto>? get evaluativeMatrices {
  final value = _evaluativeMatrices;
  if (value == null) return null;
  if (_evaluativeMatrices is EqualUnmodifiableListView) return _evaluativeMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  List<MatrixScorecardRowDto>? _informationalMatrices;
@override@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto>? get informationalMatrices {
  final value = _informationalMatrices;
  if (value == null) return null;
  if (_informationalMatrices is EqualUnmodifiableListView) return _informationalMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  List<Map<String, dynamic>>? _contentBlocks;
@override@JsonKey(name: 'content_blocks') List<Map<String, dynamic>>? get contentBlocks {
  final value = _contentBlocks;
  if (value == null) return null;
  if (_contentBlocks is EqualUnmodifiableListView) return _contentBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  List<String> _visibleMetadata;
@override@JsonKey(name: 'visible_metadata') List<String> get visibleMetadata {
  if (_visibleMetadata is EqualUnmodifiableListView) return _visibleMetadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleMetadata);
}

 final  List<ReportLayoutDto> _layouts;
@override@JsonKey() List<ReportLayoutDto> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}

 final  List<String> _matrixVisibleColumns;
@override@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
}

@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'org_name') final  String? orgName;
@override@JsonKey(name: 'cost_estimate') final  double? costEstimate;
@override@JsonKey(name: 'total_tokens') final  int? totalTokens;
@override@JsonKey(name: 'prompt_tokens') final  int? promptTokens;
@override@JsonKey(name: 'completion_tokens') final  int? completionTokens;
@override@JsonKey(name: 'reasoning_tokens') final  int? reasoningTokens;
 final  List<McpAuditTraceDto> _mcpToolAudit;
@override@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> get mcpToolAudit {
  if (_mcpToolAudit is EqualUnmodifiableListView) return _mcpToolAudit;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mcpToolAudit);
}

 final  Map<String, List<dynamic>>? _groupedExtensions;
@override@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>>? get groupedExtensions {
  final value = _groupedExtensions;
  if (value == null) return null;
  if (_groupedExtensions is EqualUnmodifiableMapView) return _groupedExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  List<String> _penaltiesApplied;
@override@JsonKey(name: 'penalties_applied') List<String> get penaltiesApplied {
  if (_penaltiesApplied is EqualUnmodifiableListView) return _penaltiesApplied;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_penaltiesApplied);
}


/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportDataDtoCopyWith<_ReportDataDto> get copyWith => __$ReportDataDtoCopyWithImpl<_ReportDataDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportDataDtoToJson(this, );
}



@override
String toString() {
  return 'ReportDataDto(executionId: $executionId, workflowId: $workflowId, scoringStrategy: $scoringStrategy, userName: $userName, scoringEngineName: $scoringEngineName, strictnessLevel: $strictnessLevel, localTimeStr: $localTimeStr, customPrefaceMd: $customPrefaceMd, profileId: $profileId, profileName: $profileName, availableProfiles: $availableProfiles, globalScore: $globalScore, hasWarning: $hasWarning, globalMetrics: $globalMetrics, globalSynthesis: $globalSynthesis, results: $results, hydratedReferences: $hydratedReferences, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices, contentBlocks: $contentBlocks, visibleMetadata: $visibleMetadata, layouts: $layouts, matrixVisibleColumns: $matrixVisibleColumns, createdAt: $createdAt, orgName: $orgName, costEstimate: $costEstimate, totalTokens: $totalTokens, promptTokens: $promptTokens, completionTokens: $completionTokens, reasoningTokens: $reasoningTokens, mcpToolAudit: $mcpToolAudit, groupedExtensions: $groupedExtensions, penaltiesApplied: $penaltiesApplied)';
}


}

/// @nodoc
abstract mixin class _$ReportDataDtoCopyWith<$Res> implements $ReportDataDtoCopyWith<$Res> {
  factory _$ReportDataDtoCopyWith(_ReportDataDto value, $Res Function(_ReportDataDto) _then) = __$ReportDataDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'scoring_strategy') String? scoringStrategy,@JsonKey(name: 'user_name') String? userName,@JsonKey(name: 'scoring_engine_name') String? scoringEngineName,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'local_time_str') String? localTimeStr,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd,@JsonKey(name: 'profile_id') String profileId,@JsonKey(name: 'profile_name') I18nText? profileName,@JsonKey(name: 'available_profiles') Map<String, I18nText> availableProfiles,@JsonKey(name: 'global_score') double? globalScore,@JsonKey(name: 'has_warning') bool hasWarning,@JsonKey(name: 'global_metrics') ExecutionMetricsDTO? globalMetrics,@JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? globalSynthesis,@JsonKey(name: 'results') List<AtomResultDTO> results,@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> hydratedReferences,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto>? evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto>? informationalMatrices,@JsonKey(name: 'content_blocks') List<Map<String, dynamic>>? contentBlocks,@JsonKey(name: 'visible_metadata') List<String> visibleMetadata, List<ReportLayoutDto> layouts,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'org_name') String? orgName,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'total_tokens') int? totalTokens,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens,@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> mcpToolAudit,@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>>? groupedExtensions,@JsonKey(name: 'penalties_applied') List<String> penaltiesApplied
});


@override $I18nTextCopyWith<$Res>? get profileName;@override $ExecutionMetricsDTOCopyWith<$Res>? get globalMetrics;@override $GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis;

}
/// @nodoc
class __$ReportDataDtoCopyWithImpl<$Res>
    implements _$ReportDataDtoCopyWith<$Res> {
  __$ReportDataDtoCopyWithImpl(this._self, this._then);

  final _ReportDataDto _self;
  final $Res Function(_ReportDataDto) _then;

/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executionId = null,Object? workflowId = null,Object? scoringStrategy = freezed,Object? userName = freezed,Object? scoringEngineName = freezed,Object? strictnessLevel = freezed,Object? localTimeStr = freezed,Object? customPrefaceMd = freezed,Object? profileId = null,Object? profileName = freezed,Object? availableProfiles = null,Object? globalScore = freezed,Object? hasWarning = null,Object? globalMetrics = freezed,Object? globalSynthesis = freezed,Object? results = null,Object? hydratedReferences = null,Object? evaluativeMatrices = freezed,Object? informationalMatrices = freezed,Object? contentBlocks = freezed,Object? visibleMetadata = null,Object? layouts = null,Object? matrixVisibleColumns = null,Object? createdAt = freezed,Object? orgName = freezed,Object? costEstimate = freezed,Object? totalTokens = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? reasoningTokens = freezed,Object? mcpToolAudit = null,Object? groupedExtensions = freezed,Object? penaltiesApplied = null,}) {
  return _then(_ReportDataDto(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as String?,userName: freezed == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String?,scoringEngineName: freezed == scoringEngineName ? _self.scoringEngineName : scoringEngineName // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,localTimeStr: freezed == localTimeStr ? _self.localTimeStr : localTimeStr // ignore: cast_nullable_to_non_nullable
as String?,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,profileName: freezed == profileName ? _self.profileName : profileName // ignore: cast_nullable_to_non_nullable
as I18nText?,availableProfiles: null == availableProfiles ? _self._availableProfiles : availableProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,hasWarning: null == hasWarning ? _self.hasWarning : hasWarning // ignore: cast_nullable_to_non_nullable
as bool,globalMetrics: freezed == globalMetrics ? _self.globalMetrics : globalMetrics // ignore: cast_nullable_to_non_nullable
as ExecutionMetricsDTO?,globalSynthesis: freezed == globalSynthesis ? _self.globalSynthesis : globalSynthesis // ignore: cast_nullable_to_non_nullable
as GlobalSynthesisDTO?,results: null == results ? _self._results : results // ignore: cast_nullable_to_non_nullable
as List<AtomResultDTO>,hydratedReferences: null == hydratedReferences ? _self._hydratedReferences : hydratedReferences // ignore: cast_nullable_to_non_nullable
as Map<String, HydratedAtomDTO>,evaluativeMatrices: freezed == evaluativeMatrices ? _self._evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>?,informationalMatrices: freezed == informationalMatrices ? _self._informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>?,contentBlocks: freezed == contentBlocks ? _self._contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>?,visibleMetadata: null == visibleMetadata ? _self._visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<ReportLayoutDto>,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,orgName: freezed == orgName ? _self.orgName : orgName // ignore: cast_nullable_to_non_nullable
as String?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,totalTokens: freezed == totalTokens ? _self.totalTokens : totalTokens // ignore: cast_nullable_to_non_nullable
as int?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,mcpToolAudit: null == mcpToolAudit ? _self._mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<McpAuditTraceDto>,groupedExtensions: freezed == groupedExtensions ? _self._groupedExtensions : groupedExtensions // ignore: cast_nullable_to_non_nullable
as Map<String, List<dynamic>>?,penaltiesApplied: null == penaltiesApplied ? _self._penaltiesApplied : penaltiesApplied // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get profileName {
    if (_self.profileName == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.profileName!, (value) {
    return _then(_self.copyWith(profileName: value));
  });
}/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetricsDTOCopyWith<$Res>? get globalMetrics {
    if (_self.globalMetrics == null) {
    return null;
  }

  return $ExecutionMetricsDTOCopyWith<$Res>(_self.globalMetrics!, (value) {
    return _then(_self.copyWith(globalMetrics: value));
  });
}/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis {
    if (_self.globalSynthesis == null) {
    return null;
  }

  return $GlobalSynthesisDTOCopyWith<$Res>(_self.globalSynthesis!, (value) {
    return _then(_self.copyWith(globalSynthesis: value));
  });
}
}

// dart format on
