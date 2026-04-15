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

@JsonKey(name: 'block_id') String get blockId;@JsonKey(name: 'label_fi') String get labelFi;@JsonKey(name: 'label_en') String get labelEn; double get score;@JsonKey(name: 'scale_max') double? get scaleMax;@JsonKey(name: 'normalized_score') double? get normalizedScore;@JsonKey(name: 'true_atoms') int? get trueAtoms;@JsonKey(name: 'total_atoms') int? get totalAtoms; String get justification;@JsonKey(name: 'missing_context') String get missingContext;@JsonKey(name: 'level_breakdown') Map<String, Map<String, int>>? get levelBreakdown;@JsonKey(name: 'is_evaluative') bool get isEvaluative;
/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixScorecardRowDtoCopyWith<MatrixScorecardRowDto> get copyWith => _$MatrixScorecardRowDtoCopyWithImpl<MatrixScorecardRowDto>(this as MatrixScorecardRowDto, _$identity);

  /// Serializes this MatrixScorecardRowDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixScorecardRowDto(blockId: $blockId, labelFi: $labelFi, labelEn: $labelEn, score: $score, scaleMax: $scaleMax, normalizedScore: $normalizedScore, trueAtoms: $trueAtoms, totalAtoms: $totalAtoms, justification: $justification, missingContext: $missingContext, levelBreakdown: $levelBreakdown, isEvaluative: $isEvaluative)';
}


}

/// @nodoc
abstract mixin class $MatrixScorecardRowDtoCopyWith<$Res>  {
  factory $MatrixScorecardRowDtoCopyWith(MatrixScorecardRowDto value, $Res Function(MatrixScorecardRowDto) _then) = _$MatrixScorecardRowDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'block_id') String blockId,@JsonKey(name: 'label_fi') String labelFi,@JsonKey(name: 'label_en') String labelEn, double score,@JsonKey(name: 'scale_max') double? scaleMax,@JsonKey(name: 'normalized_score') double? normalizedScore,@JsonKey(name: 'true_atoms') int? trueAtoms,@JsonKey(name: 'total_atoms') int? totalAtoms, String justification,@JsonKey(name: 'missing_context') String missingContext,@JsonKey(name: 'level_breakdown') Map<String, Map<String, int>>? levelBreakdown,@JsonKey(name: 'is_evaluative') bool isEvaluative
});




}
/// @nodoc
class _$MatrixScorecardRowDtoCopyWithImpl<$Res>
    implements $MatrixScorecardRowDtoCopyWith<$Res> {
  _$MatrixScorecardRowDtoCopyWithImpl(this._self, this._then);

  final MatrixScorecardRowDto _self;
  final $Res Function(MatrixScorecardRowDto) _then;

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? blockId = null,Object? labelFi = null,Object? labelEn = null,Object? score = null,Object? scaleMax = freezed,Object? normalizedScore = freezed,Object? trueAtoms = freezed,Object? totalAtoms = freezed,Object? justification = null,Object? missingContext = null,Object? levelBreakdown = freezed,Object? isEvaluative = null,}) {
  return _then(_self.copyWith(
blockId: null == blockId ? _self.blockId : blockId // ignore: cast_nullable_to_non_nullable
as String,labelFi: null == labelFi ? _self.labelFi : labelFi // ignore: cast_nullable_to_non_nullable
as String,labelEn: null == labelEn ? _self.labelEn : labelEn // ignore: cast_nullable_to_non_nullable
as String,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as double?,normalizedScore: freezed == normalizedScore ? _self.normalizedScore : normalizedScore // ignore: cast_nullable_to_non_nullable
as double?,trueAtoms: freezed == trueAtoms ? _self.trueAtoms : trueAtoms // ignore: cast_nullable_to_non_nullable
as int?,totalAtoms: freezed == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int?,justification: null == justification ? _self.justification : justification // ignore: cast_nullable_to_non_nullable
as String,missingContext: null == missingContext ? _self.missingContext : missingContext // ignore: cast_nullable_to_non_nullable
as String,levelBreakdown: freezed == levelBreakdown ? _self.levelBreakdown : levelBreakdown // ignore: cast_nullable_to_non_nullable
as Map<String, Map<String, int>>?,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,
  ));
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'block_id')  String blockId, @JsonKey(name: 'label_fi')  String labelFi, @JsonKey(name: 'label_en')  String labelEn,  double score, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms,  String justification, @JsonKey(name: 'missing_context')  String missingContext, @JsonKey(name: 'level_breakdown')  Map<String, Map<String, int>>? levelBreakdown, @JsonKey(name: 'is_evaluative')  bool isEvaluative)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
return $default(_that.blockId,_that.labelFi,_that.labelEn,_that.score,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.justification,_that.missingContext,_that.levelBreakdown,_that.isEvaluative);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'block_id')  String blockId, @JsonKey(name: 'label_fi')  String labelFi, @JsonKey(name: 'label_en')  String labelEn,  double score, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms,  String justification, @JsonKey(name: 'missing_context')  String missingContext, @JsonKey(name: 'level_breakdown')  Map<String, Map<String, int>>? levelBreakdown, @JsonKey(name: 'is_evaluative')  bool isEvaluative)  $default,) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto():
return $default(_that.blockId,_that.labelFi,_that.labelEn,_that.score,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.justification,_that.missingContext,_that.levelBreakdown,_that.isEvaluative);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'block_id')  String blockId, @JsonKey(name: 'label_fi')  String labelFi, @JsonKey(name: 'label_en')  String labelEn,  double score, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms,  String justification, @JsonKey(name: 'missing_context')  String missingContext, @JsonKey(name: 'level_breakdown')  Map<String, Map<String, int>>? levelBreakdown, @JsonKey(name: 'is_evaluative')  bool isEvaluative)?  $default,) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
return $default(_that.blockId,_that.labelFi,_that.labelEn,_that.score,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.justification,_that.missingContext,_that.levelBreakdown,_that.isEvaluative);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixScorecardRowDto implements MatrixScorecardRowDto {
  const _MatrixScorecardRowDto({@JsonKey(name: 'block_id') required this.blockId, @JsonKey(name: 'label_fi') required this.labelFi, @JsonKey(name: 'label_en') required this.labelEn, required this.score, @JsonKey(name: 'scale_max') this.scaleMax, @JsonKey(name: 'normalized_score') this.normalizedScore, @JsonKey(name: 'true_atoms') this.trueAtoms, @JsonKey(name: 'total_atoms') this.totalAtoms, this.justification = '', @JsonKey(name: 'missing_context') this.missingContext = '', @JsonKey(name: 'level_breakdown') final  Map<String, Map<String, int>>? levelBreakdown, @JsonKey(name: 'is_evaluative') this.isEvaluative = true}): _levelBreakdown = levelBreakdown;
  factory _MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) => _$MatrixScorecardRowDtoFromJson(json);

@override@JsonKey(name: 'block_id') final  String blockId;
@override@JsonKey(name: 'label_fi') final  String labelFi;
@override@JsonKey(name: 'label_en') final  String labelEn;
@override final  double score;
@override@JsonKey(name: 'scale_max') final  double? scaleMax;
@override@JsonKey(name: 'normalized_score') final  double? normalizedScore;
@override@JsonKey(name: 'true_atoms') final  int? trueAtoms;
@override@JsonKey(name: 'total_atoms') final  int? totalAtoms;
@override@JsonKey() final  String justification;
@override@JsonKey(name: 'missing_context') final  String missingContext;
 final  Map<String, Map<String, int>>? _levelBreakdown;
@override@JsonKey(name: 'level_breakdown') Map<String, Map<String, int>>? get levelBreakdown {
  final value = _levelBreakdown;
  if (value == null) return null;
  if (_levelBreakdown is EqualUnmodifiableMapView) return _levelBreakdown;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'is_evaluative') final  bool isEvaluative;

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
  return 'MatrixScorecardRowDto(blockId: $blockId, labelFi: $labelFi, labelEn: $labelEn, score: $score, scaleMax: $scaleMax, normalizedScore: $normalizedScore, trueAtoms: $trueAtoms, totalAtoms: $totalAtoms, justification: $justification, missingContext: $missingContext, levelBreakdown: $levelBreakdown, isEvaluative: $isEvaluative)';
}


}

/// @nodoc
abstract mixin class _$MatrixScorecardRowDtoCopyWith<$Res> implements $MatrixScorecardRowDtoCopyWith<$Res> {
  factory _$MatrixScorecardRowDtoCopyWith(_MatrixScorecardRowDto value, $Res Function(_MatrixScorecardRowDto) _then) = __$MatrixScorecardRowDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'block_id') String blockId,@JsonKey(name: 'label_fi') String labelFi,@JsonKey(name: 'label_en') String labelEn, double score,@JsonKey(name: 'scale_max') double? scaleMax,@JsonKey(name: 'normalized_score') double? normalizedScore,@JsonKey(name: 'true_atoms') int? trueAtoms,@JsonKey(name: 'total_atoms') int? totalAtoms, String justification,@JsonKey(name: 'missing_context') String missingContext,@JsonKey(name: 'level_breakdown') Map<String, Map<String, int>>? levelBreakdown,@JsonKey(name: 'is_evaluative') bool isEvaluative
});




}
/// @nodoc
class __$MatrixScorecardRowDtoCopyWithImpl<$Res>
    implements _$MatrixScorecardRowDtoCopyWith<$Res> {
  __$MatrixScorecardRowDtoCopyWithImpl(this._self, this._then);

  final _MatrixScorecardRowDto _self;
  final $Res Function(_MatrixScorecardRowDto) _then;

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? blockId = null,Object? labelFi = null,Object? labelEn = null,Object? score = null,Object? scaleMax = freezed,Object? normalizedScore = freezed,Object? trueAtoms = freezed,Object? totalAtoms = freezed,Object? justification = null,Object? missingContext = null,Object? levelBreakdown = freezed,Object? isEvaluative = null,}) {
  return _then(_MatrixScorecardRowDto(
blockId: null == blockId ? _self.blockId : blockId // ignore: cast_nullable_to_non_nullable
as String,labelFi: null == labelFi ? _self.labelFi : labelFi // ignore: cast_nullable_to_non_nullable
as String,labelEn: null == labelEn ? _self.labelEn : labelEn // ignore: cast_nullable_to_non_nullable
as String,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as double?,normalizedScore: freezed == normalizedScore ? _self.normalizedScore : normalizedScore // ignore: cast_nullable_to_non_nullable
as double?,trueAtoms: freezed == trueAtoms ? _self.trueAtoms : trueAtoms // ignore: cast_nullable_to_non_nullable
as int?,totalAtoms: freezed == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int?,justification: null == justification ? _self.justification : justification // ignore: cast_nullable_to_non_nullable
as String,missingContext: null == missingContext ? _self.missingContext : missingContext // ignore: cast_nullable_to_non_nullable
as String,levelBreakdown: freezed == levelBreakdown ? _self._levelBreakdown : levelBreakdown // ignore: cast_nullable_to_non_nullable
as Map<String, Map<String, int>>?,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
