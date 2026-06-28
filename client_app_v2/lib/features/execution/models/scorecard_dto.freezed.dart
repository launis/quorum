// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'scorecard_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ScorecardResponseDto {

@JsonKey(name: 'execution_id') String get executionId;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'global_average') double? get globalAverage;@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> get evaluativeMatrices;@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> get informationalMatrices;
/// Create a copy of ScorecardResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScorecardResponseDtoCopyWith<ScorecardResponseDto> get copyWith => _$ScorecardResponseDtoCopyWithImpl<ScorecardResponseDto>(this as ScorecardResponseDto, _$identity);

  /// Serializes this ScorecardResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ScorecardResponseDto(executionId: $executionId, workflowId: $workflowId, globalAverage: $globalAverage, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices)';
}


}

/// @nodoc
abstract mixin class $ScorecardResponseDtoCopyWith<$Res>  {
  factory $ScorecardResponseDtoCopyWith(ScorecardResponseDto value, $Res Function(ScorecardResponseDto) _then) = _$ScorecardResponseDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'global_average') double? globalAverage,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> informationalMatrices
});




}
/// @nodoc
class _$ScorecardResponseDtoCopyWithImpl<$Res>
    implements $ScorecardResponseDtoCopyWith<$Res> {
  _$ScorecardResponseDtoCopyWithImpl(this._self, this._then);

  final ScorecardResponseDto _self;
  final $Res Function(ScorecardResponseDto) _then;

/// Create a copy of ScorecardResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executionId = null,Object? workflowId = null,Object? globalAverage = freezed,Object? evaluativeMatrices = null,Object? informationalMatrices = null,}) {
  return _then(_self.copyWith(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,globalAverage: freezed == globalAverage ? _self.globalAverage : globalAverage // ignore: cast_nullable_to_non_nullable
as double?,evaluativeMatrices: null == evaluativeMatrices ? _self.evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,informationalMatrices: null == informationalMatrices ? _self.informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [ScorecardResponseDto].
extension ScorecardResponseDtoPatterns on ScorecardResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScorecardResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScorecardResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScorecardResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _ScorecardResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScorecardResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _ScorecardResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'global_average')  double? globalAverage, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScorecardResponseDto() when $default != null:
return $default(_that.executionId,_that.workflowId,_that.globalAverage,_that.evaluativeMatrices,_that.informationalMatrices);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'global_average')  double? globalAverage, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices)  $default,) {final _that = this;
switch (_that) {
case _ScorecardResponseDto():
return $default(_that.executionId,_that.workflowId,_that.globalAverage,_that.evaluativeMatrices,_that.informationalMatrices);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'global_average')  double? globalAverage, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices)?  $default,) {final _that = this;
switch (_that) {
case _ScorecardResponseDto() when $default != null:
return $default(_that.executionId,_that.workflowId,_that.globalAverage,_that.evaluativeMatrices,_that.informationalMatrices);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ScorecardResponseDto implements ScorecardResponseDto {
  const _ScorecardResponseDto({@JsonKey(name: 'execution_id') required this.executionId, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'global_average') this.globalAverage, @JsonKey(name: 'evaluative_matrices') final  List<MatrixScorecardRowDto> evaluativeMatrices = const [], @JsonKey(name: 'informational_matrices') final  List<MatrixScorecardRowDto> informationalMatrices = const []}): _evaluativeMatrices = evaluativeMatrices,_informationalMatrices = informationalMatrices;
  factory _ScorecardResponseDto.fromJson(Map<String, dynamic> json) => _$ScorecardResponseDtoFromJson(json);

@override@JsonKey(name: 'execution_id') final  String executionId;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'global_average') final  double? globalAverage;
 final  List<MatrixScorecardRowDto> _evaluativeMatrices;
@override@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> get evaluativeMatrices {
  if (_evaluativeMatrices is EqualUnmodifiableListView) return _evaluativeMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_evaluativeMatrices);
}

 final  List<MatrixScorecardRowDto> _informationalMatrices;
@override@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> get informationalMatrices {
  if (_informationalMatrices is EqualUnmodifiableListView) return _informationalMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_informationalMatrices);
}


/// Create a copy of ScorecardResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScorecardResponseDtoCopyWith<_ScorecardResponseDto> get copyWith => __$ScorecardResponseDtoCopyWithImpl<_ScorecardResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ScorecardResponseDtoToJson(this, );
}



@override
String toString() {
  return 'ScorecardResponseDto(executionId: $executionId, workflowId: $workflowId, globalAverage: $globalAverage, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices)';
}


}

/// @nodoc
abstract mixin class _$ScorecardResponseDtoCopyWith<$Res> implements $ScorecardResponseDtoCopyWith<$Res> {
  factory _$ScorecardResponseDtoCopyWith(_ScorecardResponseDto value, $Res Function(_ScorecardResponseDto) _then) = __$ScorecardResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'global_average') double? globalAverage,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> informationalMatrices
});




}
/// @nodoc
class __$ScorecardResponseDtoCopyWithImpl<$Res>
    implements _$ScorecardResponseDtoCopyWith<$Res> {
  __$ScorecardResponseDtoCopyWithImpl(this._self, this._then);

  final _ScorecardResponseDto _self;
  final $Res Function(_ScorecardResponseDto) _then;

/// Create a copy of ScorecardResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executionId = null,Object? workflowId = null,Object? globalAverage = freezed,Object? evaluativeMatrices = null,Object? informationalMatrices = null,}) {
  return _then(_ScorecardResponseDto(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,globalAverage: freezed == globalAverage ? _self.globalAverage : globalAverage // ignore: cast_nullable_to_non_nullable
as double?,evaluativeMatrices: null == evaluativeMatrices ? _self._evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,informationalMatrices: null == informationalMatrices ? _self._informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}


}


/// @nodoc
mixin _$MatrixScorecardRowDto {

@JsonKey(name: 'block_id') String get blockId; String get name;@JsonKey(name: 'label_i18n') I18nText get labelI18n; String? get description; double? get score;@JsonKey(name: 'scale_min') double? get scaleMin;@JsonKey(name: 'scale_max') double? get scaleMax;@JsonKey(name: 'normalized_score') double? get normalizedScore;@JsonKey(name: 'true_atoms') int? get trueAtoms;@JsonKey(name: 'total_atoms') int? get totalAtoms;@JsonKey(name: 'row_explanation') String get rowExplanation;@JsonKey(name: 'cited_source_id') String? get citedSourceId;@JsonKey(name: 'cited_text_quote') String? get citedTextQuote;@JsonKey(name: 'cited_web_citation') String? get citedWebCitation;@JsonKey(name: 'evidence_type') EvidenceType? get evidenceType;@JsonKey(name: 'tda_state') TDAState? get tdaState;// Epic 6: XAI Output Extensions
 String? get coaching; double? get confidence; String? get falsification;@JsonKey(name: 'missing_context') String? get missingContext;@JsonKey(name: 'risk_flag') bool? get riskFlag;@JsonKey(name: 'remediation_steps') String? get remediationSteps;@JsonKey(name: 'emotional_sentiment') String? get emotionalSentiment;@JsonKey(name: 'theory_link') String? get theoryLink;@JsonKey(name: 'level_breakdown') Map<String, String>? get levelBreakdown;@JsonKey(name: 'level_names') Map<String, String>? get levelNames;@JsonKey(name: 'ui_boundary_labels') Map<String, String>? get uiBoundaryLabels;@JsonKey(name: 'ui_plot_ratio') double? get uiPlotRatio;@JsonKey(name: 'is_evaluative') bool get isEvaluative;@JsonKey(name: 'contextual_override') bool? get contextualOverride;@JsonKey(name: 'semantic_reasoning') String? get semanticReasoning;// Epic 88: Unified Forensic Traceability
@JsonKey(name: 'quotes_list') List<String>? get quotesList;@JsonKey(name: 'row_forensics') RowForensicsDto? get forensics;@JsonKey(name: 'used_evidence_ids') List<String> get usedEvidenceIds;
/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixScorecardRowDtoCopyWith<MatrixScorecardRowDto> get copyWith => _$MatrixScorecardRowDtoCopyWithImpl<MatrixScorecardRowDto>(this as MatrixScorecardRowDto, _$identity);

  /// Serializes this MatrixScorecardRowDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixScorecardRowDto(blockId: $blockId, name: $name, labelI18n: $labelI18n, description: $description, score: $score, scaleMin: $scaleMin, scaleMax: $scaleMax, normalizedScore: $normalizedScore, trueAtoms: $trueAtoms, totalAtoms: $totalAtoms, rowExplanation: $rowExplanation, citedSourceId: $citedSourceId, citedTextQuote: $citedTextQuote, citedWebCitation: $citedWebCitation, evidenceType: $evidenceType, tdaState: $tdaState, coaching: $coaching, confidence: $confidence, falsification: $falsification, missingContext: $missingContext, riskFlag: $riskFlag, remediationSteps: $remediationSteps, emotionalSentiment: $emotionalSentiment, theoryLink: $theoryLink, levelBreakdown: $levelBreakdown, levelNames: $levelNames, uiBoundaryLabels: $uiBoundaryLabels, uiPlotRatio: $uiPlotRatio, isEvaluative: $isEvaluative, contextualOverride: $contextualOverride, semanticReasoning: $semanticReasoning, quotesList: $quotesList, forensics: $forensics, usedEvidenceIds: $usedEvidenceIds)';
}


}

/// @nodoc
abstract mixin class $MatrixScorecardRowDtoCopyWith<$Res>  {
  factory $MatrixScorecardRowDtoCopyWith(MatrixScorecardRowDto value, $Res Function(MatrixScorecardRowDto) _then) = _$MatrixScorecardRowDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'block_id') String blockId, String name,@JsonKey(name: 'label_i18n') I18nText labelI18n, String? description, double? score,@JsonKey(name: 'scale_min') double? scaleMin,@JsonKey(name: 'scale_max') double? scaleMax,@JsonKey(name: 'normalized_score') double? normalizedScore,@JsonKey(name: 'true_atoms') int? trueAtoms,@JsonKey(name: 'total_atoms') int? totalAtoms,@JsonKey(name: 'row_explanation') String rowExplanation,@JsonKey(name: 'cited_source_id') String? citedSourceId,@JsonKey(name: 'cited_text_quote') String? citedTextQuote,@JsonKey(name: 'cited_web_citation') String? citedWebCitation,@JsonKey(name: 'evidence_type') EvidenceType? evidenceType,@JsonKey(name: 'tda_state') TDAState? tdaState, String? coaching, double? confidence, String? falsification,@JsonKey(name: 'missing_context') String? missingContext,@JsonKey(name: 'risk_flag') bool? riskFlag,@JsonKey(name: 'remediation_steps') String? remediationSteps,@JsonKey(name: 'emotional_sentiment') String? emotionalSentiment,@JsonKey(name: 'theory_link') String? theoryLink,@JsonKey(name: 'level_breakdown') Map<String, String>? levelBreakdown,@JsonKey(name: 'level_names') Map<String, String>? levelNames,@JsonKey(name: 'ui_boundary_labels') Map<String, String>? uiBoundaryLabels,@JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,@JsonKey(name: 'is_evaluative') bool isEvaluative,@JsonKey(name: 'contextual_override') bool? contextualOverride,@JsonKey(name: 'semantic_reasoning') String? semanticReasoning,@JsonKey(name: 'quotes_list') List<String>? quotesList,@JsonKey(name: 'row_forensics') RowForensicsDto? forensics,@JsonKey(name: 'used_evidence_ids') List<String> usedEvidenceIds
});


$I18nTextCopyWith<$Res> get labelI18n;$TDAStateCopyWith<$Res>? get tdaState;$RowForensicsDtoCopyWith<$Res>? get forensics;

}
/// @nodoc
class _$MatrixScorecardRowDtoCopyWithImpl<$Res>
    implements $MatrixScorecardRowDtoCopyWith<$Res> {
  _$MatrixScorecardRowDtoCopyWithImpl(this._self, this._then);

  final MatrixScorecardRowDto _self;
  final $Res Function(MatrixScorecardRowDto) _then;

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? blockId = null,Object? name = null,Object? labelI18n = null,Object? description = freezed,Object? score = freezed,Object? scaleMin = freezed,Object? scaleMax = freezed,Object? normalizedScore = freezed,Object? trueAtoms = freezed,Object? totalAtoms = freezed,Object? rowExplanation = null,Object? citedSourceId = freezed,Object? citedTextQuote = freezed,Object? citedWebCitation = freezed,Object? evidenceType = freezed,Object? tdaState = freezed,Object? coaching = freezed,Object? confidence = freezed,Object? falsification = freezed,Object? missingContext = freezed,Object? riskFlag = freezed,Object? remediationSteps = freezed,Object? emotionalSentiment = freezed,Object? theoryLink = freezed,Object? levelBreakdown = freezed,Object? levelNames = freezed,Object? uiBoundaryLabels = freezed,Object? uiPlotRatio = freezed,Object? isEvaluative = null,Object? contextualOverride = freezed,Object? semanticReasoning = freezed,Object? quotesList = freezed,Object? forensics = freezed,Object? usedEvidenceIds = null,}) {
  return _then(_self.copyWith(
blockId: null == blockId ? _self.blockId : blockId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,labelI18n: null == labelI18n ? _self.labelI18n : labelI18n // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,score: freezed == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double?,scaleMin: freezed == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as double?,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as double?,normalizedScore: freezed == normalizedScore ? _self.normalizedScore : normalizedScore // ignore: cast_nullable_to_non_nullable
as double?,trueAtoms: freezed == trueAtoms ? _self.trueAtoms : trueAtoms // ignore: cast_nullable_to_non_nullable
as int?,totalAtoms: freezed == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int?,rowExplanation: null == rowExplanation ? _self.rowExplanation : rowExplanation // ignore: cast_nullable_to_non_nullable
as String,citedSourceId: freezed == citedSourceId ? _self.citedSourceId : citedSourceId // ignore: cast_nullable_to_non_nullable
as String?,citedTextQuote: freezed == citedTextQuote ? _self.citedTextQuote : citedTextQuote // ignore: cast_nullable_to_non_nullable
as String?,citedWebCitation: freezed == citedWebCitation ? _self.citedWebCitation : citedWebCitation // ignore: cast_nullable_to_non_nullable
as String?,evidenceType: freezed == evidenceType ? _self.evidenceType : evidenceType // ignore: cast_nullable_to_non_nullable
as EvidenceType?,tdaState: freezed == tdaState ? _self.tdaState : tdaState // ignore: cast_nullable_to_non_nullable
as TDAState?,coaching: freezed == coaching ? _self.coaching : coaching // ignore: cast_nullable_to_non_nullable
as String?,confidence: freezed == confidence ? _self.confidence : confidence // ignore: cast_nullable_to_non_nullable
as double?,falsification: freezed == falsification ? _self.falsification : falsification // ignore: cast_nullable_to_non_nullable
as String?,missingContext: freezed == missingContext ? _self.missingContext : missingContext // ignore: cast_nullable_to_non_nullable
as String?,riskFlag: freezed == riskFlag ? _self.riskFlag : riskFlag // ignore: cast_nullable_to_non_nullable
as bool?,remediationSteps: freezed == remediationSteps ? _self.remediationSteps : remediationSteps // ignore: cast_nullable_to_non_nullable
as String?,emotionalSentiment: freezed == emotionalSentiment ? _self.emotionalSentiment : emotionalSentiment // ignore: cast_nullable_to_non_nullable
as String?,theoryLink: freezed == theoryLink ? _self.theoryLink : theoryLink // ignore: cast_nullable_to_non_nullable
as String?,levelBreakdown: freezed == levelBreakdown ? _self.levelBreakdown : levelBreakdown // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,levelNames: freezed == levelNames ? _self.levelNames : levelNames // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiBoundaryLabels: freezed == uiBoundaryLabels ? _self.uiBoundaryLabels : uiBoundaryLabels // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiPlotRatio: freezed == uiPlotRatio ? _self.uiPlotRatio : uiPlotRatio // ignore: cast_nullable_to_non_nullable
as double?,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,contextualOverride: freezed == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool?,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,quotesList: freezed == quotesList ? _self.quotesList : quotesList // ignore: cast_nullable_to_non_nullable
as List<String>?,forensics: freezed == forensics ? _self.forensics : forensics // ignore: cast_nullable_to_non_nullable
as RowForensicsDto?,usedEvidenceIds: null == usedEvidenceIds ? _self.usedEvidenceIds : usedEvidenceIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}
/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get labelI18n {
  
  return $I18nTextCopyWith<$Res>(_self.labelI18n, (value) {
    return _then(_self.copyWith(labelI18n: value));
  });
}/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TDAStateCopyWith<$Res>? get tdaState {
    if (_self.tdaState == null) {
    return null;
  }

  return $TDAStateCopyWith<$Res>(_self.tdaState!, (value) {
    return _then(_self.copyWith(tdaState: value));
  });
}/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RowForensicsDtoCopyWith<$Res>? get forensics {
    if (_self.forensics == null) {
    return null;
  }

  return $RowForensicsDtoCopyWith<$Res>(_self.forensics!, (value) {
    return _then(_self.copyWith(forensics: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixScorecardRowDto].
extension MatrixScorecardRowDtoPatterns on MatrixScorecardRowDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixScorecardRowDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixScorecardRowDto value)  $default,){
final _that = this;
switch (_that) {
case _MatrixScorecardRowDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixScorecardRowDto value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'block_id')  String blockId,  String name, @JsonKey(name: 'label_i18n')  I18nText labelI18n,  String? description,  double? score, @JsonKey(name: 'scale_min')  double? scaleMin, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms, @JsonKey(name: 'row_explanation')  String rowExplanation, @JsonKey(name: 'cited_source_id')  String? citedSourceId, @JsonKey(name: 'cited_text_quote')  String? citedTextQuote, @JsonKey(name: 'cited_web_citation')  String? citedWebCitation, @JsonKey(name: 'evidence_type')  EvidenceType? evidenceType, @JsonKey(name: 'tda_state')  TDAState? tdaState,  String? coaching,  double? confidence,  String? falsification, @JsonKey(name: 'missing_context')  String? missingContext, @JsonKey(name: 'risk_flag')  bool? riskFlag, @JsonKey(name: 'remediation_steps')  String? remediationSteps, @JsonKey(name: 'emotional_sentiment')  String? emotionalSentiment, @JsonKey(name: 'theory_link')  String? theoryLink, @JsonKey(name: 'level_breakdown')  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names')  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels')  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio')  double? uiPlotRatio, @JsonKey(name: 'is_evaluative')  bool isEvaluative, @JsonKey(name: 'contextual_override')  bool? contextualOverride, @JsonKey(name: 'semantic_reasoning')  String? semanticReasoning, @JsonKey(name: 'quotes_list')  List<String>? quotesList, @JsonKey(name: 'row_forensics')  RowForensicsDto? forensics, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
return $default(_that.blockId,_that.name,_that.labelI18n,_that.description,_that.score,_that.scaleMin,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.rowExplanation,_that.citedSourceId,_that.citedTextQuote,_that.citedWebCitation,_that.evidenceType,_that.tdaState,_that.coaching,_that.confidence,_that.falsification,_that.missingContext,_that.riskFlag,_that.remediationSteps,_that.emotionalSentiment,_that.theoryLink,_that.levelBreakdown,_that.levelNames,_that.uiBoundaryLabels,_that.uiPlotRatio,_that.isEvaluative,_that.contextualOverride,_that.semanticReasoning,_that.quotesList,_that.forensics,_that.usedEvidenceIds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'block_id')  String blockId,  String name, @JsonKey(name: 'label_i18n')  I18nText labelI18n,  String? description,  double? score, @JsonKey(name: 'scale_min')  double? scaleMin, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms, @JsonKey(name: 'row_explanation')  String rowExplanation, @JsonKey(name: 'cited_source_id')  String? citedSourceId, @JsonKey(name: 'cited_text_quote')  String? citedTextQuote, @JsonKey(name: 'cited_web_citation')  String? citedWebCitation, @JsonKey(name: 'evidence_type')  EvidenceType? evidenceType, @JsonKey(name: 'tda_state')  TDAState? tdaState,  String? coaching,  double? confidence,  String? falsification, @JsonKey(name: 'missing_context')  String? missingContext, @JsonKey(name: 'risk_flag')  bool? riskFlag, @JsonKey(name: 'remediation_steps')  String? remediationSteps, @JsonKey(name: 'emotional_sentiment')  String? emotionalSentiment, @JsonKey(name: 'theory_link')  String? theoryLink, @JsonKey(name: 'level_breakdown')  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names')  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels')  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio')  double? uiPlotRatio, @JsonKey(name: 'is_evaluative')  bool isEvaluative, @JsonKey(name: 'contextual_override')  bool? contextualOverride, @JsonKey(name: 'semantic_reasoning')  String? semanticReasoning, @JsonKey(name: 'quotes_list')  List<String>? quotesList, @JsonKey(name: 'row_forensics')  RowForensicsDto? forensics, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)  $default,) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto():
return $default(_that.blockId,_that.name,_that.labelI18n,_that.description,_that.score,_that.scaleMin,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.rowExplanation,_that.citedSourceId,_that.citedTextQuote,_that.citedWebCitation,_that.evidenceType,_that.tdaState,_that.coaching,_that.confidence,_that.falsification,_that.missingContext,_that.riskFlag,_that.remediationSteps,_that.emotionalSentiment,_that.theoryLink,_that.levelBreakdown,_that.levelNames,_that.uiBoundaryLabels,_that.uiPlotRatio,_that.isEvaluative,_that.contextualOverride,_that.semanticReasoning,_that.quotesList,_that.forensics,_that.usedEvidenceIds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'block_id')  String blockId,  String name, @JsonKey(name: 'label_i18n')  I18nText labelI18n,  String? description,  double? score, @JsonKey(name: 'scale_min')  double? scaleMin, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms, @JsonKey(name: 'row_explanation')  String rowExplanation, @JsonKey(name: 'cited_source_id')  String? citedSourceId, @JsonKey(name: 'cited_text_quote')  String? citedTextQuote, @JsonKey(name: 'cited_web_citation')  String? citedWebCitation, @JsonKey(name: 'evidence_type')  EvidenceType? evidenceType, @JsonKey(name: 'tda_state')  TDAState? tdaState,  String? coaching,  double? confidence,  String? falsification, @JsonKey(name: 'missing_context')  String? missingContext, @JsonKey(name: 'risk_flag')  bool? riskFlag, @JsonKey(name: 'remediation_steps')  String? remediationSteps, @JsonKey(name: 'emotional_sentiment')  String? emotionalSentiment, @JsonKey(name: 'theory_link')  String? theoryLink, @JsonKey(name: 'level_breakdown')  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names')  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels')  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio')  double? uiPlotRatio, @JsonKey(name: 'is_evaluative')  bool isEvaluative, @JsonKey(name: 'contextual_override')  bool? contextualOverride, @JsonKey(name: 'semantic_reasoning')  String? semanticReasoning, @JsonKey(name: 'quotes_list')  List<String>? quotesList, @JsonKey(name: 'row_forensics')  RowForensicsDto? forensics, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)?  $default,) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
return $default(_that.blockId,_that.name,_that.labelI18n,_that.description,_that.score,_that.scaleMin,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.rowExplanation,_that.citedSourceId,_that.citedTextQuote,_that.citedWebCitation,_that.evidenceType,_that.tdaState,_that.coaching,_that.confidence,_that.falsification,_that.missingContext,_that.riskFlag,_that.remediationSteps,_that.emotionalSentiment,_that.theoryLink,_that.levelBreakdown,_that.levelNames,_that.uiBoundaryLabels,_that.uiPlotRatio,_that.isEvaluative,_that.contextualOverride,_that.semanticReasoning,_that.quotesList,_that.forensics,_that.usedEvidenceIds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixScorecardRowDto extends MatrixScorecardRowDto {
  const _MatrixScorecardRowDto({@JsonKey(name: 'block_id') required this.blockId, required this.name, @JsonKey(name: 'label_i18n') required this.labelI18n, this.description, this.score, @JsonKey(name: 'scale_min') this.scaleMin, @JsonKey(name: 'scale_max') this.scaleMax, @JsonKey(name: 'normalized_score') this.normalizedScore, @JsonKey(name: 'true_atoms') this.trueAtoms, @JsonKey(name: 'total_atoms') this.totalAtoms, @JsonKey(name: 'row_explanation') this.rowExplanation = '', @JsonKey(name: 'cited_source_id') this.citedSourceId, @JsonKey(name: 'cited_text_quote') this.citedTextQuote, @JsonKey(name: 'cited_web_citation') this.citedWebCitation, @JsonKey(name: 'evidence_type') this.evidenceType, @JsonKey(name: 'tda_state') this.tdaState, this.coaching, this.confidence, this.falsification, @JsonKey(name: 'missing_context') this.missingContext, @JsonKey(name: 'risk_flag') this.riskFlag, @JsonKey(name: 'remediation_steps') this.remediationSteps, @JsonKey(name: 'emotional_sentiment') this.emotionalSentiment, @JsonKey(name: 'theory_link') this.theoryLink, @JsonKey(name: 'level_breakdown') final  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names') final  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels') final  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio') this.uiPlotRatio, @JsonKey(name: 'is_evaluative') this.isEvaluative = true, @JsonKey(name: 'contextual_override') this.contextualOverride, @JsonKey(name: 'semantic_reasoning') this.semanticReasoning, @JsonKey(name: 'quotes_list') final  List<String>? quotesList, @JsonKey(name: 'row_forensics') this.forensics, @JsonKey(name: 'used_evidence_ids') final  List<String> usedEvidenceIds = const []}): _levelBreakdown = levelBreakdown,_levelNames = levelNames,_uiBoundaryLabels = uiBoundaryLabels,_quotesList = quotesList,_usedEvidenceIds = usedEvidenceIds,super._();
  factory _MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) => _$MatrixScorecardRowDtoFromJson(json);

@override@JsonKey(name: 'block_id') final  String blockId;
@override final  String name;
@override@JsonKey(name: 'label_i18n') final  I18nText labelI18n;
@override final  String? description;
@override final  double? score;
@override@JsonKey(name: 'scale_min') final  double? scaleMin;
@override@JsonKey(name: 'scale_max') final  double? scaleMax;
@override@JsonKey(name: 'normalized_score') final  double? normalizedScore;
@override@JsonKey(name: 'true_atoms') final  int? trueAtoms;
@override@JsonKey(name: 'total_atoms') final  int? totalAtoms;
@override@JsonKey(name: 'row_explanation') final  String rowExplanation;
@override@JsonKey(name: 'cited_source_id') final  String? citedSourceId;
@override@JsonKey(name: 'cited_text_quote') final  String? citedTextQuote;
@override@JsonKey(name: 'cited_web_citation') final  String? citedWebCitation;
@override@JsonKey(name: 'evidence_type') final  EvidenceType? evidenceType;
@override@JsonKey(name: 'tda_state') final  TDAState? tdaState;
// Epic 6: XAI Output Extensions
@override final  String? coaching;
@override final  double? confidence;
@override final  String? falsification;
@override@JsonKey(name: 'missing_context') final  String? missingContext;
@override@JsonKey(name: 'risk_flag') final  bool? riskFlag;
@override@JsonKey(name: 'remediation_steps') final  String? remediationSteps;
@override@JsonKey(name: 'emotional_sentiment') final  String? emotionalSentiment;
@override@JsonKey(name: 'theory_link') final  String? theoryLink;
 final  Map<String, String>? _levelBreakdown;
@override@JsonKey(name: 'level_breakdown') Map<String, String>? get levelBreakdown {
  final value = _levelBreakdown;
  if (value == null) return null;
  if (_levelBreakdown is EqualUnmodifiableMapView) return _levelBreakdown;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, String>? _levelNames;
@override@JsonKey(name: 'level_names') Map<String, String>? get levelNames {
  final value = _levelNames;
  if (value == null) return null;
  if (_levelNames is EqualUnmodifiableMapView) return _levelNames;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, String>? _uiBoundaryLabels;
@override@JsonKey(name: 'ui_boundary_labels') Map<String, String>? get uiBoundaryLabels {
  final value = _uiBoundaryLabels;
  if (value == null) return null;
  if (_uiBoundaryLabels is EqualUnmodifiableMapView) return _uiBoundaryLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'ui_plot_ratio') final  double? uiPlotRatio;
@override@JsonKey(name: 'is_evaluative') final  bool isEvaluative;
@override@JsonKey(name: 'contextual_override') final  bool? contextualOverride;
@override@JsonKey(name: 'semantic_reasoning') final  String? semanticReasoning;
// Epic 88: Unified Forensic Traceability
 final  List<String>? _quotesList;
// Epic 88: Unified Forensic Traceability
@override@JsonKey(name: 'quotes_list') List<String>? get quotesList {
  final value = _quotesList;
  if (value == null) return null;
  if (_quotesList is EqualUnmodifiableListView) return _quotesList;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey(name: 'row_forensics') final  RowForensicsDto? forensics;
 final  List<String> _usedEvidenceIds;
@override@JsonKey(name: 'used_evidence_ids') List<String> get usedEvidenceIds {
  if (_usedEvidenceIds is EqualUnmodifiableListView) return _usedEvidenceIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_usedEvidenceIds);
}


/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixScorecardRowDtoCopyWith<_MatrixScorecardRowDto> get copyWith => __$MatrixScorecardRowDtoCopyWithImpl<_MatrixScorecardRowDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixScorecardRowDtoToJson(this, );
}



@override
String toString() {
  return 'MatrixScorecardRowDto(blockId: $blockId, name: $name, labelI18n: $labelI18n, description: $description, score: $score, scaleMin: $scaleMin, scaleMax: $scaleMax, normalizedScore: $normalizedScore, trueAtoms: $trueAtoms, totalAtoms: $totalAtoms, rowExplanation: $rowExplanation, citedSourceId: $citedSourceId, citedTextQuote: $citedTextQuote, citedWebCitation: $citedWebCitation, evidenceType: $evidenceType, tdaState: $tdaState, coaching: $coaching, confidence: $confidence, falsification: $falsification, missingContext: $missingContext, riskFlag: $riskFlag, remediationSteps: $remediationSteps, emotionalSentiment: $emotionalSentiment, theoryLink: $theoryLink, levelBreakdown: $levelBreakdown, levelNames: $levelNames, uiBoundaryLabels: $uiBoundaryLabels, uiPlotRatio: $uiPlotRatio, isEvaluative: $isEvaluative, contextualOverride: $contextualOverride, semanticReasoning: $semanticReasoning, quotesList: $quotesList, forensics: $forensics, usedEvidenceIds: $usedEvidenceIds)';
}


}

/// @nodoc
abstract mixin class _$MatrixScorecardRowDtoCopyWith<$Res> implements $MatrixScorecardRowDtoCopyWith<$Res> {
  factory _$MatrixScorecardRowDtoCopyWith(_MatrixScorecardRowDto value, $Res Function(_MatrixScorecardRowDto) _then) = __$MatrixScorecardRowDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'block_id') String blockId, String name,@JsonKey(name: 'label_i18n') I18nText labelI18n, String? description, double? score,@JsonKey(name: 'scale_min') double? scaleMin,@JsonKey(name: 'scale_max') double? scaleMax,@JsonKey(name: 'normalized_score') double? normalizedScore,@JsonKey(name: 'true_atoms') int? trueAtoms,@JsonKey(name: 'total_atoms') int? totalAtoms,@JsonKey(name: 'row_explanation') String rowExplanation,@JsonKey(name: 'cited_source_id') String? citedSourceId,@JsonKey(name: 'cited_text_quote') String? citedTextQuote,@JsonKey(name: 'cited_web_citation') String? citedWebCitation,@JsonKey(name: 'evidence_type') EvidenceType? evidenceType,@JsonKey(name: 'tda_state') TDAState? tdaState, String? coaching, double? confidence, String? falsification,@JsonKey(name: 'missing_context') String? missingContext,@JsonKey(name: 'risk_flag') bool? riskFlag,@JsonKey(name: 'remediation_steps') String? remediationSteps,@JsonKey(name: 'emotional_sentiment') String? emotionalSentiment,@JsonKey(name: 'theory_link') String? theoryLink,@JsonKey(name: 'level_breakdown') Map<String, String>? levelBreakdown,@JsonKey(name: 'level_names') Map<String, String>? levelNames,@JsonKey(name: 'ui_boundary_labels') Map<String, String>? uiBoundaryLabels,@JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,@JsonKey(name: 'is_evaluative') bool isEvaluative,@JsonKey(name: 'contextual_override') bool? contextualOverride,@JsonKey(name: 'semantic_reasoning') String? semanticReasoning,@JsonKey(name: 'quotes_list') List<String>? quotesList,@JsonKey(name: 'row_forensics') RowForensicsDto? forensics,@JsonKey(name: 'used_evidence_ids') List<String> usedEvidenceIds
});


@override $I18nTextCopyWith<$Res> get labelI18n;@override $TDAStateCopyWith<$Res>? get tdaState;@override $RowForensicsDtoCopyWith<$Res>? get forensics;

}
/// @nodoc
class __$MatrixScorecardRowDtoCopyWithImpl<$Res>
    implements _$MatrixScorecardRowDtoCopyWith<$Res> {
  __$MatrixScorecardRowDtoCopyWithImpl(this._self, this._then);

  final _MatrixScorecardRowDto _self;
  final $Res Function(_MatrixScorecardRowDto) _then;

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? blockId = null,Object? name = null,Object? labelI18n = null,Object? description = freezed,Object? score = freezed,Object? scaleMin = freezed,Object? scaleMax = freezed,Object? normalizedScore = freezed,Object? trueAtoms = freezed,Object? totalAtoms = freezed,Object? rowExplanation = null,Object? citedSourceId = freezed,Object? citedTextQuote = freezed,Object? citedWebCitation = freezed,Object? evidenceType = freezed,Object? tdaState = freezed,Object? coaching = freezed,Object? confidence = freezed,Object? falsification = freezed,Object? missingContext = freezed,Object? riskFlag = freezed,Object? remediationSteps = freezed,Object? emotionalSentiment = freezed,Object? theoryLink = freezed,Object? levelBreakdown = freezed,Object? levelNames = freezed,Object? uiBoundaryLabels = freezed,Object? uiPlotRatio = freezed,Object? isEvaluative = null,Object? contextualOverride = freezed,Object? semanticReasoning = freezed,Object? quotesList = freezed,Object? forensics = freezed,Object? usedEvidenceIds = null,}) {
  return _then(_MatrixScorecardRowDto(
blockId: null == blockId ? _self.blockId : blockId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,labelI18n: null == labelI18n ? _self.labelI18n : labelI18n // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,score: freezed == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double?,scaleMin: freezed == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as double?,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as double?,normalizedScore: freezed == normalizedScore ? _self.normalizedScore : normalizedScore // ignore: cast_nullable_to_non_nullable
as double?,trueAtoms: freezed == trueAtoms ? _self.trueAtoms : trueAtoms // ignore: cast_nullable_to_non_nullable
as int?,totalAtoms: freezed == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int?,rowExplanation: null == rowExplanation ? _self.rowExplanation : rowExplanation // ignore: cast_nullable_to_non_nullable
as String,citedSourceId: freezed == citedSourceId ? _self.citedSourceId : citedSourceId // ignore: cast_nullable_to_non_nullable
as String?,citedTextQuote: freezed == citedTextQuote ? _self.citedTextQuote : citedTextQuote // ignore: cast_nullable_to_non_nullable
as String?,citedWebCitation: freezed == citedWebCitation ? _self.citedWebCitation : citedWebCitation // ignore: cast_nullable_to_non_nullable
as String?,evidenceType: freezed == evidenceType ? _self.evidenceType : evidenceType // ignore: cast_nullable_to_non_nullable
as EvidenceType?,tdaState: freezed == tdaState ? _self.tdaState : tdaState // ignore: cast_nullable_to_non_nullable
as TDAState?,coaching: freezed == coaching ? _self.coaching : coaching // ignore: cast_nullable_to_non_nullable
as String?,confidence: freezed == confidence ? _self.confidence : confidence // ignore: cast_nullable_to_non_nullable
as double?,falsification: freezed == falsification ? _self.falsification : falsification // ignore: cast_nullable_to_non_nullable
as String?,missingContext: freezed == missingContext ? _self.missingContext : missingContext // ignore: cast_nullable_to_non_nullable
as String?,riskFlag: freezed == riskFlag ? _self.riskFlag : riskFlag // ignore: cast_nullable_to_non_nullable
as bool?,remediationSteps: freezed == remediationSteps ? _self.remediationSteps : remediationSteps // ignore: cast_nullable_to_non_nullable
as String?,emotionalSentiment: freezed == emotionalSentiment ? _self.emotionalSentiment : emotionalSentiment // ignore: cast_nullable_to_non_nullable
as String?,theoryLink: freezed == theoryLink ? _self.theoryLink : theoryLink // ignore: cast_nullable_to_non_nullable
as String?,levelBreakdown: freezed == levelBreakdown ? _self._levelBreakdown : levelBreakdown // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,levelNames: freezed == levelNames ? _self._levelNames : levelNames // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiBoundaryLabels: freezed == uiBoundaryLabels ? _self._uiBoundaryLabels : uiBoundaryLabels // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiPlotRatio: freezed == uiPlotRatio ? _self.uiPlotRatio : uiPlotRatio // ignore: cast_nullable_to_non_nullable
as double?,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,contextualOverride: freezed == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool?,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,quotesList: freezed == quotesList ? _self._quotesList : quotesList // ignore: cast_nullable_to_non_nullable
as List<String>?,forensics: freezed == forensics ? _self.forensics : forensics // ignore: cast_nullable_to_non_nullable
as RowForensicsDto?,usedEvidenceIds: null == usedEvidenceIds ? _self._usedEvidenceIds : usedEvidenceIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get labelI18n {
  
  return $I18nTextCopyWith<$Res>(_self.labelI18n, (value) {
    return _then(_self.copyWith(labelI18n: value));
  });
}/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TDAStateCopyWith<$Res>? get tdaState {
    if (_self.tdaState == null) {
    return null;
  }

  return $TDAStateCopyWith<$Res>(_self.tdaState!, (value) {
    return _then(_self.copyWith(tdaState: value));
  });
}/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RowForensicsDtoCopyWith<$Res>? get forensics {
    if (_self.forensics == null) {
    return null;
  }

  return $RowForensicsDtoCopyWith<$Res>(_self.forensics!, (value) {
    return _then(_self.copyWith(forensics: value));
  });
}
}


/// @nodoc
mixin _$EvidenceQuoteDto {

 String get id; String get text;@JsonKey(name: 'source_reference') String? get sourceReference;@JsonKey(name: 'user_rejected') bool get userRejected;@JsonKey(name: 'rejection_reason') String? get rejectionReason;@JsonKey(name: 'is_mcp_verified') bool get isMcpVerified;@JsonKey(name: 'used_evidence_ids') List<String> get usedEvidenceIds;
/// Create a copy of EvidenceQuoteDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EvidenceQuoteDtoCopyWith<EvidenceQuoteDto> get copyWith => _$EvidenceQuoteDtoCopyWithImpl<EvidenceQuoteDto>(this as EvidenceQuoteDto, _$identity);

  /// Serializes this EvidenceQuoteDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'EvidenceQuoteDto(id: $id, text: $text, sourceReference: $sourceReference, userRejected: $userRejected, rejectionReason: $rejectionReason, isMcpVerified: $isMcpVerified, usedEvidenceIds: $usedEvidenceIds)';
}


}

/// @nodoc
abstract mixin class $EvidenceQuoteDtoCopyWith<$Res>  {
  factory $EvidenceQuoteDtoCopyWith(EvidenceQuoteDto value, $Res Function(EvidenceQuoteDto) _then) = _$EvidenceQuoteDtoCopyWithImpl;
@useResult
$Res call({
 String id, String text,@JsonKey(name: 'source_reference') String? sourceReference,@JsonKey(name: 'user_rejected') bool userRejected,@JsonKey(name: 'rejection_reason') String? rejectionReason,@JsonKey(name: 'is_mcp_verified') bool isMcpVerified,@JsonKey(name: 'used_evidence_ids') List<String> usedEvidenceIds
});




}
/// @nodoc
class _$EvidenceQuoteDtoCopyWithImpl<$Res>
    implements $EvidenceQuoteDtoCopyWith<$Res> {
  _$EvidenceQuoteDtoCopyWithImpl(this._self, this._then);

  final EvidenceQuoteDto _self;
  final $Res Function(EvidenceQuoteDto) _then;

/// Create a copy of EvidenceQuoteDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? text = null,Object? sourceReference = freezed,Object? userRejected = null,Object? rejectionReason = freezed,Object? isMcpVerified = null,Object? usedEvidenceIds = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,sourceReference: freezed == sourceReference ? _self.sourceReference : sourceReference // ignore: cast_nullable_to_non_nullable
as String?,userRejected: null == userRejected ? _self.userRejected : userRejected // ignore: cast_nullable_to_non_nullable
as bool,rejectionReason: freezed == rejectionReason ? _self.rejectionReason : rejectionReason // ignore: cast_nullable_to_non_nullable
as String?,isMcpVerified: null == isMcpVerified ? _self.isMcpVerified : isMcpVerified // ignore: cast_nullable_to_non_nullable
as bool,usedEvidenceIds: null == usedEvidenceIds ? _self.usedEvidenceIds : usedEvidenceIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [EvidenceQuoteDto].
extension EvidenceQuoteDtoPatterns on EvidenceQuoteDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EvidenceQuoteDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EvidenceQuoteDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EvidenceQuoteDto value)  $default,){
final _that = this;
switch (_that) {
case _EvidenceQuoteDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EvidenceQuoteDto value)?  $default,){
final _that = this;
switch (_that) {
case _EvidenceQuoteDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String text, @JsonKey(name: 'source_reference')  String? sourceReference, @JsonKey(name: 'user_rejected')  bool userRejected, @JsonKey(name: 'rejection_reason')  String? rejectionReason, @JsonKey(name: 'is_mcp_verified')  bool isMcpVerified, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EvidenceQuoteDto() when $default != null:
return $default(_that.id,_that.text,_that.sourceReference,_that.userRejected,_that.rejectionReason,_that.isMcpVerified,_that.usedEvidenceIds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String text, @JsonKey(name: 'source_reference')  String? sourceReference, @JsonKey(name: 'user_rejected')  bool userRejected, @JsonKey(name: 'rejection_reason')  String? rejectionReason, @JsonKey(name: 'is_mcp_verified')  bool isMcpVerified, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)  $default,) {final _that = this;
switch (_that) {
case _EvidenceQuoteDto():
return $default(_that.id,_that.text,_that.sourceReference,_that.userRejected,_that.rejectionReason,_that.isMcpVerified,_that.usedEvidenceIds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String text, @JsonKey(name: 'source_reference')  String? sourceReference, @JsonKey(name: 'user_rejected')  bool userRejected, @JsonKey(name: 'rejection_reason')  String? rejectionReason, @JsonKey(name: 'is_mcp_verified')  bool isMcpVerified, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)?  $default,) {final _that = this;
switch (_that) {
case _EvidenceQuoteDto() when $default != null:
return $default(_that.id,_that.text,_that.sourceReference,_that.userRejected,_that.rejectionReason,_that.isMcpVerified,_that.usedEvidenceIds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _EvidenceQuoteDto implements EvidenceQuoteDto {
  const _EvidenceQuoteDto({required this.id, required this.text, @JsonKey(name: 'source_reference') this.sourceReference, @JsonKey(name: 'user_rejected') this.userRejected = false, @JsonKey(name: 'rejection_reason') this.rejectionReason, @JsonKey(name: 'is_mcp_verified') this.isMcpVerified = false, @JsonKey(name: 'used_evidence_ids') final  List<String> usedEvidenceIds = const []}): _usedEvidenceIds = usedEvidenceIds;
  factory _EvidenceQuoteDto.fromJson(Map<String, dynamic> json) => _$EvidenceQuoteDtoFromJson(json);

@override final  String id;
@override final  String text;
@override@JsonKey(name: 'source_reference') final  String? sourceReference;
@override@JsonKey(name: 'user_rejected') final  bool userRejected;
@override@JsonKey(name: 'rejection_reason') final  String? rejectionReason;
@override@JsonKey(name: 'is_mcp_verified') final  bool isMcpVerified;
 final  List<String> _usedEvidenceIds;
@override@JsonKey(name: 'used_evidence_ids') List<String> get usedEvidenceIds {
  if (_usedEvidenceIds is EqualUnmodifiableListView) return _usedEvidenceIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_usedEvidenceIds);
}


/// Create a copy of EvidenceQuoteDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EvidenceQuoteDtoCopyWith<_EvidenceQuoteDto> get copyWith => __$EvidenceQuoteDtoCopyWithImpl<_EvidenceQuoteDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EvidenceQuoteDtoToJson(this, );
}



@override
String toString() {
  return 'EvidenceQuoteDto(id: $id, text: $text, sourceReference: $sourceReference, userRejected: $userRejected, rejectionReason: $rejectionReason, isMcpVerified: $isMcpVerified, usedEvidenceIds: $usedEvidenceIds)';
}


}

/// @nodoc
abstract mixin class _$EvidenceQuoteDtoCopyWith<$Res> implements $EvidenceQuoteDtoCopyWith<$Res> {
  factory _$EvidenceQuoteDtoCopyWith(_EvidenceQuoteDto value, $Res Function(_EvidenceQuoteDto) _then) = __$EvidenceQuoteDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String text,@JsonKey(name: 'source_reference') String? sourceReference,@JsonKey(name: 'user_rejected') bool userRejected,@JsonKey(name: 'rejection_reason') String? rejectionReason,@JsonKey(name: 'is_mcp_verified') bool isMcpVerified,@JsonKey(name: 'used_evidence_ids') List<String> usedEvidenceIds
});




}
/// @nodoc
class __$EvidenceQuoteDtoCopyWithImpl<$Res>
    implements _$EvidenceQuoteDtoCopyWith<$Res> {
  __$EvidenceQuoteDtoCopyWithImpl(this._self, this._then);

  final _EvidenceQuoteDto _self;
  final $Res Function(_EvidenceQuoteDto) _then;

/// Create a copy of EvidenceQuoteDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? text = null,Object? sourceReference = freezed,Object? userRejected = null,Object? rejectionReason = freezed,Object? isMcpVerified = null,Object? usedEvidenceIds = null,}) {
  return _then(_EvidenceQuoteDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,sourceReference: freezed == sourceReference ? _self.sourceReference : sourceReference // ignore: cast_nullable_to_non_nullable
as String?,userRejected: null == userRejected ? _self.userRejected : userRejected // ignore: cast_nullable_to_non_nullable
as bool,rejectionReason: freezed == rejectionReason ? _self.rejectionReason : rejectionReason // ignore: cast_nullable_to_non_nullable
as String?,isMcpVerified: null == isMcpVerified ? _self.isMcpVerified : isMcpVerified // ignore: cast_nullable_to_non_nullable
as bool,usedEvidenceIds: null == usedEvidenceIds ? _self._usedEvidenceIds : usedEvidenceIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}


/// @nodoc
mixin _$LevelQuotesDto {

 int get level;@JsonKey(name: 'level_name') String get levelName; List<EvidenceQuoteDto> get quotes;
/// Create a copy of LevelQuotesDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LevelQuotesDtoCopyWith<LevelQuotesDto> get copyWith => _$LevelQuotesDtoCopyWithImpl<LevelQuotesDto>(this as LevelQuotesDto, _$identity);

  /// Serializes this LevelQuotesDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'LevelQuotesDto(level: $level, levelName: $levelName, quotes: $quotes)';
}


}

/// @nodoc
abstract mixin class $LevelQuotesDtoCopyWith<$Res>  {
  factory $LevelQuotesDtoCopyWith(LevelQuotesDto value, $Res Function(LevelQuotesDto) _then) = _$LevelQuotesDtoCopyWithImpl;
@useResult
$Res call({
 int level,@JsonKey(name: 'level_name') String levelName, List<EvidenceQuoteDto> quotes
});




}
/// @nodoc
class _$LevelQuotesDtoCopyWithImpl<$Res>
    implements $LevelQuotesDtoCopyWith<$Res> {
  _$LevelQuotesDtoCopyWithImpl(this._self, this._then);

  final LevelQuotesDto _self;
  final $Res Function(LevelQuotesDto) _then;

/// Create a copy of LevelQuotesDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? level = null,Object? levelName = null,Object? quotes = null,}) {
  return _then(_self.copyWith(
level: null == level ? _self.level : level // ignore: cast_nullable_to_non_nullable
as int,levelName: null == levelName ? _self.levelName : levelName // ignore: cast_nullable_to_non_nullable
as String,quotes: null == quotes ? _self.quotes : quotes // ignore: cast_nullable_to_non_nullable
as List<EvidenceQuoteDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [LevelQuotesDto].
extension LevelQuotesDtoPatterns on LevelQuotesDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LevelQuotesDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LevelQuotesDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LevelQuotesDto value)  $default,){
final _that = this;
switch (_that) {
case _LevelQuotesDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LevelQuotesDto value)?  $default,){
final _that = this;
switch (_that) {
case _LevelQuotesDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int level, @JsonKey(name: 'level_name')  String levelName,  List<EvidenceQuoteDto> quotes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LevelQuotesDto() when $default != null:
return $default(_that.level,_that.levelName,_that.quotes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int level, @JsonKey(name: 'level_name')  String levelName,  List<EvidenceQuoteDto> quotes)  $default,) {final _that = this;
switch (_that) {
case _LevelQuotesDto():
return $default(_that.level,_that.levelName,_that.quotes);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int level, @JsonKey(name: 'level_name')  String levelName,  List<EvidenceQuoteDto> quotes)?  $default,) {final _that = this;
switch (_that) {
case _LevelQuotesDto() when $default != null:
return $default(_that.level,_that.levelName,_that.quotes);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _LevelQuotesDto implements LevelQuotesDto {
  const _LevelQuotesDto({required this.level, @JsonKey(name: 'level_name') required this.levelName, final  List<EvidenceQuoteDto> quotes = const []}): _quotes = quotes;
  factory _LevelQuotesDto.fromJson(Map<String, dynamic> json) => _$LevelQuotesDtoFromJson(json);

@override final  int level;
@override@JsonKey(name: 'level_name') final  String levelName;
 final  List<EvidenceQuoteDto> _quotes;
@override@JsonKey() List<EvidenceQuoteDto> get quotes {
  if (_quotes is EqualUnmodifiableListView) return _quotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_quotes);
}


/// Create a copy of LevelQuotesDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LevelQuotesDtoCopyWith<_LevelQuotesDto> get copyWith => __$LevelQuotesDtoCopyWithImpl<_LevelQuotesDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LevelQuotesDtoToJson(this, );
}



@override
String toString() {
  return 'LevelQuotesDto(level: $level, levelName: $levelName, quotes: $quotes)';
}


}

/// @nodoc
abstract mixin class _$LevelQuotesDtoCopyWith<$Res> implements $LevelQuotesDtoCopyWith<$Res> {
  factory _$LevelQuotesDtoCopyWith(_LevelQuotesDto value, $Res Function(_LevelQuotesDto) _then) = __$LevelQuotesDtoCopyWithImpl;
@override @useResult
$Res call({
 int level,@JsonKey(name: 'level_name') String levelName, List<EvidenceQuoteDto> quotes
});




}
/// @nodoc
class __$LevelQuotesDtoCopyWithImpl<$Res>
    implements _$LevelQuotesDtoCopyWith<$Res> {
  __$LevelQuotesDtoCopyWithImpl(this._self, this._then);

  final _LevelQuotesDto _self;
  final $Res Function(_LevelQuotesDto) _then;

/// Create a copy of LevelQuotesDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? level = null,Object? levelName = null,Object? quotes = null,}) {
  return _then(_LevelQuotesDto(
level: null == level ? _self.level : level // ignore: cast_nullable_to_non_nullable
as int,levelName: null == levelName ? _self.levelName : levelName // ignore: cast_nullable_to_non_nullable
as String,quotes: null == quotes ? _self._quotes : quotes // ignore: cast_nullable_to_non_nullable
as List<EvidenceQuoteDto>,
  ));
}


}


/// @nodoc
mixin _$RowForensicsDto {

@JsonKey(name: 'level_quotes') List<LevelQuotesDto> get levelQuotes;@JsonKey(name: 'all_evidence_rejected') bool get allEvidenceRejected;
/// Create a copy of RowForensicsDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RowForensicsDtoCopyWith<RowForensicsDto> get copyWith => _$RowForensicsDtoCopyWithImpl<RowForensicsDto>(this as RowForensicsDto, _$identity);

  /// Serializes this RowForensicsDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'RowForensicsDto(levelQuotes: $levelQuotes, allEvidenceRejected: $allEvidenceRejected)';
}


}

/// @nodoc
abstract mixin class $RowForensicsDtoCopyWith<$Res>  {
  factory $RowForensicsDtoCopyWith(RowForensicsDto value, $Res Function(RowForensicsDto) _then) = _$RowForensicsDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'level_quotes') List<LevelQuotesDto> levelQuotes,@JsonKey(name: 'all_evidence_rejected') bool allEvidenceRejected
});




}
/// @nodoc
class _$RowForensicsDtoCopyWithImpl<$Res>
    implements $RowForensicsDtoCopyWith<$Res> {
  _$RowForensicsDtoCopyWithImpl(this._self, this._then);

  final RowForensicsDto _self;
  final $Res Function(RowForensicsDto) _then;

/// Create a copy of RowForensicsDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? levelQuotes = null,Object? allEvidenceRejected = null,}) {
  return _then(_self.copyWith(
levelQuotes: null == levelQuotes ? _self.levelQuotes : levelQuotes // ignore: cast_nullable_to_non_nullable
as List<LevelQuotesDto>,allEvidenceRejected: null == allEvidenceRejected ? _self.allEvidenceRejected : allEvidenceRejected // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [RowForensicsDto].
extension RowForensicsDtoPatterns on RowForensicsDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RowForensicsDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RowForensicsDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RowForensicsDto value)  $default,){
final _that = this;
switch (_that) {
case _RowForensicsDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RowForensicsDto value)?  $default,){
final _that = this;
switch (_that) {
case _RowForensicsDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'level_quotes')  List<LevelQuotesDto> levelQuotes, @JsonKey(name: 'all_evidence_rejected')  bool allEvidenceRejected)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RowForensicsDto() when $default != null:
return $default(_that.levelQuotes,_that.allEvidenceRejected);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'level_quotes')  List<LevelQuotesDto> levelQuotes, @JsonKey(name: 'all_evidence_rejected')  bool allEvidenceRejected)  $default,) {final _that = this;
switch (_that) {
case _RowForensicsDto():
return $default(_that.levelQuotes,_that.allEvidenceRejected);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'level_quotes')  List<LevelQuotesDto> levelQuotes, @JsonKey(name: 'all_evidence_rejected')  bool allEvidenceRejected)?  $default,) {final _that = this;
switch (_that) {
case _RowForensicsDto() when $default != null:
return $default(_that.levelQuotes,_that.allEvidenceRejected);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _RowForensicsDto implements RowForensicsDto {
  const _RowForensicsDto({@JsonKey(name: 'level_quotes') final  List<LevelQuotesDto> levelQuotes = const [], @JsonKey(name: 'all_evidence_rejected') this.allEvidenceRejected = false}): _levelQuotes = levelQuotes;
  factory _RowForensicsDto.fromJson(Map<String, dynamic> json) => _$RowForensicsDtoFromJson(json);

 final  List<LevelQuotesDto> _levelQuotes;
@override@JsonKey(name: 'level_quotes') List<LevelQuotesDto> get levelQuotes {
  if (_levelQuotes is EqualUnmodifiableListView) return _levelQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_levelQuotes);
}

@override@JsonKey(name: 'all_evidence_rejected') final  bool allEvidenceRejected;

/// Create a copy of RowForensicsDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RowForensicsDtoCopyWith<_RowForensicsDto> get copyWith => __$RowForensicsDtoCopyWithImpl<_RowForensicsDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RowForensicsDtoToJson(this, );
}



@override
String toString() {
  return 'RowForensicsDto(levelQuotes: $levelQuotes, allEvidenceRejected: $allEvidenceRejected)';
}


}

/// @nodoc
abstract mixin class _$RowForensicsDtoCopyWith<$Res> implements $RowForensicsDtoCopyWith<$Res> {
  factory _$RowForensicsDtoCopyWith(_RowForensicsDto value, $Res Function(_RowForensicsDto) _then) = __$RowForensicsDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'level_quotes') List<LevelQuotesDto> levelQuotes,@JsonKey(name: 'all_evidence_rejected') bool allEvidenceRejected
});




}
/// @nodoc
class __$RowForensicsDtoCopyWithImpl<$Res>
    implements _$RowForensicsDtoCopyWith<$Res> {
  __$RowForensicsDtoCopyWithImpl(this._self, this._then);

  final _RowForensicsDto _self;
  final $Res Function(_RowForensicsDto) _then;

/// Create a copy of RowForensicsDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? levelQuotes = null,Object? allEvidenceRejected = null,}) {
  return _then(_RowForensicsDto(
levelQuotes: null == levelQuotes ? _self._levelQuotes : levelQuotes // ignore: cast_nullable_to_non_nullable
as List<LevelQuotesDto>,allEvidenceRejected: null == allEvidenceRejected ? _self.allEvidenceRejected : allEvidenceRejected // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
