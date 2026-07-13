// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_metrics_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionMetricsDTO {

@JsonKey(name: 'total_atoms') int get totalAtoms; int get evaluated;@JsonKey(name: 'short_circuited_na') int get shortCircuitedNa;@JsonKey(name: 'duration_ms') int get durationMs;
/// Create a copy of ExecutionMetricsDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionMetricsDTOCopyWith<ExecutionMetricsDTO> get copyWith => _$ExecutionMetricsDTOCopyWithImpl<ExecutionMetricsDTO>(this as ExecutionMetricsDTO, _$identity);

  /// Serializes this ExecutionMetricsDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionMetricsDTO&&(identical(other.totalAtoms, totalAtoms) || other.totalAtoms == totalAtoms)&&(identical(other.evaluated, evaluated) || other.evaluated == evaluated)&&(identical(other.shortCircuitedNa, shortCircuitedNa) || other.shortCircuitedNa == shortCircuitedNa)&&(identical(other.durationMs, durationMs) || other.durationMs == durationMs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalAtoms,evaluated,shortCircuitedNa,durationMs);

@override
String toString() {
  return 'ExecutionMetricsDTO(totalAtoms: $totalAtoms, evaluated: $evaluated, shortCircuitedNa: $shortCircuitedNa, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class $ExecutionMetricsDTOCopyWith<$Res>  {
  factory $ExecutionMetricsDTOCopyWith(ExecutionMetricsDTO value, $Res Function(ExecutionMetricsDTO) _then) = _$ExecutionMetricsDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'total_atoms') int totalAtoms, int evaluated,@JsonKey(name: 'short_circuited_na') int shortCircuitedNa,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class _$ExecutionMetricsDTOCopyWithImpl<$Res>
    implements $ExecutionMetricsDTOCopyWith<$Res> {
  _$ExecutionMetricsDTOCopyWithImpl(this._self, this._then);

  final ExecutionMetricsDTO _self;
  final $Res Function(ExecutionMetricsDTO) _then;

/// Create a copy of ExecutionMetricsDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totalAtoms = null,Object? evaluated = null,Object? shortCircuitedNa = null,Object? durationMs = null,}) {
  return _then(_self.copyWith(
totalAtoms: null == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int,evaluated: null == evaluated ? _self.evaluated : evaluated // ignore: cast_nullable_to_non_nullable
as int,shortCircuitedNa: null == shortCircuitedNa ? _self.shortCircuitedNa : shortCircuitedNa // ignore: cast_nullable_to_non_nullable
as int,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionMetricsDTO].
extension ExecutionMetricsDTOPatterns on ExecutionMetricsDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionMetricsDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionMetricsDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionMetricsDTO value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionMetricsDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionMetricsDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionMetricsDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_atoms')  int totalAtoms,  int evaluated, @JsonKey(name: 'short_circuited_na')  int shortCircuitedNa, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionMetricsDTO() when $default != null:
return $default(_that.totalAtoms,_that.evaluated,_that.shortCircuitedNa,_that.durationMs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_atoms')  int totalAtoms,  int evaluated, @JsonKey(name: 'short_circuited_na')  int shortCircuitedNa, @JsonKey(name: 'duration_ms')  int durationMs)  $default,) {final _that = this;
switch (_that) {
case _ExecutionMetricsDTO():
return $default(_that.totalAtoms,_that.evaluated,_that.shortCircuitedNa,_that.durationMs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'total_atoms')  int totalAtoms,  int evaluated, @JsonKey(name: 'short_circuited_na')  int shortCircuitedNa, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionMetricsDTO() when $default != null:
return $default(_that.totalAtoms,_that.evaluated,_that.shortCircuitedNa,_that.durationMs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionMetricsDTO implements ExecutionMetricsDTO {
  const _ExecutionMetricsDTO({@JsonKey(name: 'total_atoms') required this.totalAtoms, required this.evaluated, @JsonKey(name: 'short_circuited_na') required this.shortCircuitedNa, @JsonKey(name: 'duration_ms') this.durationMs = 0});
  factory _ExecutionMetricsDTO.fromJson(Map<String, dynamic> json) => _$ExecutionMetricsDTOFromJson(json);

@override@JsonKey(name: 'total_atoms') final  int totalAtoms;
@override final  int evaluated;
@override@JsonKey(name: 'short_circuited_na') final  int shortCircuitedNa;
@override@JsonKey(name: 'duration_ms') final  int durationMs;

/// Create a copy of ExecutionMetricsDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionMetricsDTOCopyWith<_ExecutionMetricsDTO> get copyWith => __$ExecutionMetricsDTOCopyWithImpl<_ExecutionMetricsDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionMetricsDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ExecutionMetricsDTO&&(identical(other.totalAtoms, totalAtoms) || other.totalAtoms == totalAtoms)&&(identical(other.evaluated, evaluated) || other.evaluated == evaluated)&&(identical(other.shortCircuitedNa, shortCircuitedNa) || other.shortCircuitedNa == shortCircuitedNa)&&(identical(other.durationMs, durationMs) || other.durationMs == durationMs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalAtoms,evaluated,shortCircuitedNa,durationMs);

@override
String toString() {
  return 'ExecutionMetricsDTO(totalAtoms: $totalAtoms, evaluated: $evaluated, shortCircuitedNa: $shortCircuitedNa, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class _$ExecutionMetricsDTOCopyWith<$Res> implements $ExecutionMetricsDTOCopyWith<$Res> {
  factory _$ExecutionMetricsDTOCopyWith(_ExecutionMetricsDTO value, $Res Function(_ExecutionMetricsDTO) _then) = __$ExecutionMetricsDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'total_atoms') int totalAtoms, int evaluated,@JsonKey(name: 'short_circuited_na') int shortCircuitedNa,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class __$ExecutionMetricsDTOCopyWithImpl<$Res>
    implements _$ExecutionMetricsDTOCopyWith<$Res> {
  __$ExecutionMetricsDTOCopyWithImpl(this._self, this._then);

  final _ExecutionMetricsDTO _self;
  final $Res Function(_ExecutionMetricsDTO) _then;

/// Create a copy of ExecutionMetricsDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totalAtoms = null,Object? evaluated = null,Object? shortCircuitedNa = null,Object? durationMs = null,}) {
  return _then(_ExecutionMetricsDTO(
totalAtoms: null == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int,evaluated: null == evaluated ? _self.evaluated : evaluated // ignore: cast_nullable_to_non_nullable
as int,shortCircuitedNa: null == shortCircuitedNa ? _self.shortCircuitedNa : shortCircuitedNa // ignore: cast_nullable_to_non_nullable
as int,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
