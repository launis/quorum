// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_create_request_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionCreateRequestDto {

@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'raw_inputs') Map<String, dynamic> get rawInputs;@JsonKey(name: 'profile_id') String? get profileId;@JsonKey(name: 'matrix_sampling_strategy') int? get matrixSamplingStrategy;
/// Create a copy of ExecutionCreateRequestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionCreateRequestDtoCopyWith<ExecutionCreateRequestDto> get copyWith => _$ExecutionCreateRequestDtoCopyWithImpl<ExecutionCreateRequestDto>(this as ExecutionCreateRequestDto, _$identity);

  /// Serializes this ExecutionCreateRequestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionCreateRequestDto(workflowId: $workflowId, targetLocale: $targetLocale, rawInputs: $rawInputs, profileId: $profileId, matrixSamplingStrategy: $matrixSamplingStrategy)';
}


}

/// @nodoc
abstract mixin class $ExecutionCreateRequestDtoCopyWith<$Res>  {
  factory $ExecutionCreateRequestDtoCopyWith(ExecutionCreateRequestDto value, $Res Function(ExecutionCreateRequestDto) _then) = _$ExecutionCreateRequestDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'raw_inputs') Map<String, dynamic> rawInputs,@JsonKey(name: 'profile_id') String? profileId,@JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy
});




}
/// @nodoc
class _$ExecutionCreateRequestDtoCopyWithImpl<$Res>
    implements $ExecutionCreateRequestDtoCopyWith<$Res> {
  _$ExecutionCreateRequestDtoCopyWithImpl(this._self, this._then);

  final ExecutionCreateRequestDto _self;
  final $Res Function(ExecutionCreateRequestDto) _then;

/// Create a copy of ExecutionCreateRequestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? workflowId = null,Object? targetLocale = null,Object? rawInputs = null,Object? profileId = freezed,Object? matrixSamplingStrategy = freezed,}) {
  return _then(_self.copyWith(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,rawInputs: null == rawInputs ? _self.rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,profileId: freezed == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String?,matrixSamplingStrategy: freezed == matrixSamplingStrategy ? _self.matrixSamplingStrategy : matrixSamplingStrategy // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionCreateRequestDto].
extension ExecutionCreateRequestDtoPatterns on ExecutionCreateRequestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionCreateRequestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionCreateRequestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionCreateRequestDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionCreateRequestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionCreateRequestDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionCreateRequestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'raw_inputs')  Map<String, dynamic> rawInputs, @JsonKey(name: 'profile_id')  String? profileId, @JsonKey(name: 'matrix_sampling_strategy')  int? matrixSamplingStrategy)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionCreateRequestDto() when $default != null:
return $default(_that.workflowId,_that.targetLocale,_that.rawInputs,_that.profileId,_that.matrixSamplingStrategy);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'raw_inputs')  Map<String, dynamic> rawInputs, @JsonKey(name: 'profile_id')  String? profileId, @JsonKey(name: 'matrix_sampling_strategy')  int? matrixSamplingStrategy)  $default,) {final _that = this;
switch (_that) {
case _ExecutionCreateRequestDto():
return $default(_that.workflowId,_that.targetLocale,_that.rawInputs,_that.profileId,_that.matrixSamplingStrategy);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'raw_inputs')  Map<String, dynamic> rawInputs, @JsonKey(name: 'profile_id')  String? profileId, @JsonKey(name: 'matrix_sampling_strategy')  int? matrixSamplingStrategy)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionCreateRequestDto() when $default != null:
return $default(_that.workflowId,_that.targetLocale,_that.rawInputs,_that.profileId,_that.matrixSamplingStrategy);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionCreateRequestDto extends ExecutionCreateRequestDto {
  const _ExecutionCreateRequestDto({@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'target_locale') required this.targetLocale, @JsonKey(name: 'raw_inputs') final  Map<String, dynamic> rawInputs = const {}, @JsonKey(name: 'profile_id') this.profileId, @JsonKey(name: 'matrix_sampling_strategy') this.matrixSamplingStrategy}): _rawInputs = rawInputs,super._();
  factory _ExecutionCreateRequestDto.fromJson(Map<String, dynamic> json) => _$ExecutionCreateRequestDtoFromJson(json);

@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
 final  Map<String, dynamic> _rawInputs;
@override@JsonKey(name: 'raw_inputs') Map<String, dynamic> get rawInputs {
  if (_rawInputs is EqualUnmodifiableMapView) return _rawInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_rawInputs);
}

@override@JsonKey(name: 'profile_id') final  String? profileId;
@override@JsonKey(name: 'matrix_sampling_strategy') final  int? matrixSamplingStrategy;

/// Create a copy of ExecutionCreateRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionCreateRequestDtoCopyWith<_ExecutionCreateRequestDto> get copyWith => __$ExecutionCreateRequestDtoCopyWithImpl<_ExecutionCreateRequestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionCreateRequestDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionCreateRequestDto(workflowId: $workflowId, targetLocale: $targetLocale, rawInputs: $rawInputs, profileId: $profileId, matrixSamplingStrategy: $matrixSamplingStrategy)';
}


}

/// @nodoc
abstract mixin class _$ExecutionCreateRequestDtoCopyWith<$Res> implements $ExecutionCreateRequestDtoCopyWith<$Res> {
  factory _$ExecutionCreateRequestDtoCopyWith(_ExecutionCreateRequestDto value, $Res Function(_ExecutionCreateRequestDto) _then) = __$ExecutionCreateRequestDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'raw_inputs') Map<String, dynamic> rawInputs,@JsonKey(name: 'profile_id') String? profileId,@JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy
});




}
/// @nodoc
class __$ExecutionCreateRequestDtoCopyWithImpl<$Res>
    implements _$ExecutionCreateRequestDtoCopyWith<$Res> {
  __$ExecutionCreateRequestDtoCopyWithImpl(this._self, this._then);

  final _ExecutionCreateRequestDto _self;
  final $Res Function(_ExecutionCreateRequestDto) _then;

/// Create a copy of ExecutionCreateRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? workflowId = null,Object? targetLocale = null,Object? rawInputs = null,Object? profileId = freezed,Object? matrixSamplingStrategy = freezed,}) {
  return _then(_ExecutionCreateRequestDto(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,rawInputs: null == rawInputs ? _self._rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,profileId: freezed == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String?,matrixSamplingStrategy: freezed == matrixSamplingStrategy ? _self.matrixSamplingStrategy : matrixSamplingStrategy // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
