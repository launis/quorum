// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'global_synthesis_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$GlobalSynthesisDTO {

@JsonKey(name: 'executive_summary') String? get executiveSummary;@JsonKey(name: 'urgency_level') int? get urgencyLevel;
/// Create a copy of GlobalSynthesisDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GlobalSynthesisDTOCopyWith<GlobalSynthesisDTO> get copyWith => _$GlobalSynthesisDTOCopyWithImpl<GlobalSynthesisDTO>(this as GlobalSynthesisDTO, _$identity);

  /// Serializes this GlobalSynthesisDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is GlobalSynthesisDTO&&(identical(other.executiveSummary, executiveSummary) || other.executiveSummary == executiveSummary)&&(identical(other.urgencyLevel, urgencyLevel) || other.urgencyLevel == urgencyLevel));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,executiveSummary,urgencyLevel);

@override
String toString() {
  return 'GlobalSynthesisDTO(executiveSummary: $executiveSummary, urgencyLevel: $urgencyLevel)';
}


}

/// @nodoc
abstract mixin class $GlobalSynthesisDTOCopyWith<$Res>  {
  factory $GlobalSynthesisDTOCopyWith(GlobalSynthesisDTO value, $Res Function(GlobalSynthesisDTO) _then) = _$GlobalSynthesisDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'executive_summary') String? executiveSummary,@JsonKey(name: 'urgency_level') int? urgencyLevel
});




}
/// @nodoc
class _$GlobalSynthesisDTOCopyWithImpl<$Res>
    implements $GlobalSynthesisDTOCopyWith<$Res> {
  _$GlobalSynthesisDTOCopyWithImpl(this._self, this._then);

  final GlobalSynthesisDTO _self;
  final $Res Function(GlobalSynthesisDTO) _then;

/// Create a copy of GlobalSynthesisDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executiveSummary = freezed,Object? urgencyLevel = freezed,}) {
  return _then(_self.copyWith(
executiveSummary: freezed == executiveSummary ? _self.executiveSummary : executiveSummary // ignore: cast_nullable_to_non_nullable
as String?,urgencyLevel: freezed == urgencyLevel ? _self.urgencyLevel : urgencyLevel // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [GlobalSynthesisDTO].
extension GlobalSynthesisDTOPatterns on GlobalSynthesisDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GlobalSynthesisDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GlobalSynthesisDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GlobalSynthesisDTO value)  $default,){
final _that = this;
switch (_that) {
case _GlobalSynthesisDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GlobalSynthesisDTO value)?  $default,){
final _that = this;
switch (_that) {
case _GlobalSynthesisDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'executive_summary')  String? executiveSummary, @JsonKey(name: 'urgency_level')  int? urgencyLevel)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GlobalSynthesisDTO() when $default != null:
return $default(_that.executiveSummary,_that.urgencyLevel);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'executive_summary')  String? executiveSummary, @JsonKey(name: 'urgency_level')  int? urgencyLevel)  $default,) {final _that = this;
switch (_that) {
case _GlobalSynthesisDTO():
return $default(_that.executiveSummary,_that.urgencyLevel);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'executive_summary')  String? executiveSummary, @JsonKey(name: 'urgency_level')  int? urgencyLevel)?  $default,) {final _that = this;
switch (_that) {
case _GlobalSynthesisDTO() when $default != null:
return $default(_that.executiveSummary,_that.urgencyLevel);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _GlobalSynthesisDTO implements GlobalSynthesisDTO {
  const _GlobalSynthesisDTO({@JsonKey(name: 'executive_summary') this.executiveSummary, @JsonKey(name: 'urgency_level') this.urgencyLevel});
  factory _GlobalSynthesisDTO.fromJson(Map<String, dynamic> json) => _$GlobalSynthesisDTOFromJson(json);

@override@JsonKey(name: 'executive_summary') final  String? executiveSummary;
@override@JsonKey(name: 'urgency_level') final  int? urgencyLevel;

/// Create a copy of GlobalSynthesisDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GlobalSynthesisDTOCopyWith<_GlobalSynthesisDTO> get copyWith => __$GlobalSynthesisDTOCopyWithImpl<_GlobalSynthesisDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GlobalSynthesisDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _GlobalSynthesisDTO&&(identical(other.executiveSummary, executiveSummary) || other.executiveSummary == executiveSummary)&&(identical(other.urgencyLevel, urgencyLevel) || other.urgencyLevel == urgencyLevel));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,executiveSummary,urgencyLevel);

@override
String toString() {
  return 'GlobalSynthesisDTO(executiveSummary: $executiveSummary, urgencyLevel: $urgencyLevel)';
}


}

/// @nodoc
abstract mixin class _$GlobalSynthesisDTOCopyWith<$Res> implements $GlobalSynthesisDTOCopyWith<$Res> {
  factory _$GlobalSynthesisDTOCopyWith(_GlobalSynthesisDTO value, $Res Function(_GlobalSynthesisDTO) _then) = __$GlobalSynthesisDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'executive_summary') String? executiveSummary,@JsonKey(name: 'urgency_level') int? urgencyLevel
});




}
/// @nodoc
class __$GlobalSynthesisDTOCopyWithImpl<$Res>
    implements _$GlobalSynthesisDTOCopyWith<$Res> {
  __$GlobalSynthesisDTOCopyWithImpl(this._self, this._then);

  final _GlobalSynthesisDTO _self;
  final $Res Function(_GlobalSynthesisDTO) _then;

/// Create a copy of GlobalSynthesisDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executiveSummary = freezed,Object? urgencyLevel = freezed,}) {
  return _then(_GlobalSynthesisDTO(
executiveSummary: freezed == executiveSummary ? _self.executiveSummary : executiveSummary // ignore: cast_nullable_to_non_nullable
as String?,urgencyLevel: freezed == urgencyLevel ? _self.urgencyLevel : urgencyLevel // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
