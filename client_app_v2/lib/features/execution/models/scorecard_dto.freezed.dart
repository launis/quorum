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

// dart format on
