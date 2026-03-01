// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'guided_reflection.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$GuidedReflectionDTO {

/// Tavoite ja strateginen suunnittelu
@JsonKey(name: 'q1_goal') String? get q1Goal;/// Tekoälyn ohjaus ja kriittinen iterointi
@JsonKey(name: 'q2_falsification') String? get q2Falsification;/// Oma panos ja luovuus
@JsonKey(name: 'q3_synthesis') String? get q3Synthesis;/// Laadunvarmistus ja metakognitio
@JsonKey(name: 'q4_argumentation') String? get q4Argumentation;
/// Create a copy of GuidedReflectionDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GuidedReflectionDTOCopyWith<GuidedReflectionDTO> get copyWith => _$GuidedReflectionDTOCopyWithImpl<GuidedReflectionDTO>(this as GuidedReflectionDTO, _$identity);

  /// Serializes this GuidedReflectionDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is GuidedReflectionDTO&&(identical(other.q1Goal, q1Goal) || other.q1Goal == q1Goal)&&(identical(other.q2Falsification, q2Falsification) || other.q2Falsification == q2Falsification)&&(identical(other.q3Synthesis, q3Synthesis) || other.q3Synthesis == q3Synthesis)&&(identical(other.q4Argumentation, q4Argumentation) || other.q4Argumentation == q4Argumentation));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,q1Goal,q2Falsification,q3Synthesis,q4Argumentation);

@override
String toString() {
  return 'GuidedReflectionDTO(q1Goal: $q1Goal, q2Falsification: $q2Falsification, q3Synthesis: $q3Synthesis, q4Argumentation: $q4Argumentation)';
}


}

/// @nodoc
abstract mixin class $GuidedReflectionDTOCopyWith<$Res>  {
  factory $GuidedReflectionDTOCopyWith(GuidedReflectionDTO value, $Res Function(GuidedReflectionDTO) _then) = _$GuidedReflectionDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'q1_goal') String? q1Goal,@JsonKey(name: 'q2_falsification') String? q2Falsification,@JsonKey(name: 'q3_synthesis') String? q3Synthesis,@JsonKey(name: 'q4_argumentation') String? q4Argumentation
});




}
/// @nodoc
class _$GuidedReflectionDTOCopyWithImpl<$Res>
    implements $GuidedReflectionDTOCopyWith<$Res> {
  _$GuidedReflectionDTOCopyWithImpl(this._self, this._then);

  final GuidedReflectionDTO _self;
  final $Res Function(GuidedReflectionDTO) _then;

/// Create a copy of GuidedReflectionDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? q1Goal = freezed,Object? q2Falsification = freezed,Object? q3Synthesis = freezed,Object? q4Argumentation = freezed,}) {
  return _then(_self.copyWith(
q1Goal: freezed == q1Goal ? _self.q1Goal : q1Goal // ignore: cast_nullable_to_non_nullable
as String?,q2Falsification: freezed == q2Falsification ? _self.q2Falsification : q2Falsification // ignore: cast_nullable_to_non_nullable
as String?,q3Synthesis: freezed == q3Synthesis ? _self.q3Synthesis : q3Synthesis // ignore: cast_nullable_to_non_nullable
as String?,q4Argumentation: freezed == q4Argumentation ? _self.q4Argumentation : q4Argumentation // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [GuidedReflectionDTO].
extension GuidedReflectionDTOPatterns on GuidedReflectionDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GuidedReflectionDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GuidedReflectionDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GuidedReflectionDTO value)  $default,){
final _that = this;
switch (_that) {
case _GuidedReflectionDTO():
return $default(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GuidedReflectionDTO value)?  $default,){
final _that = this;
switch (_that) {
case _GuidedReflectionDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'q1_goal')  String? q1Goal, @JsonKey(name: 'q2_falsification')  String? q2Falsification, @JsonKey(name: 'q3_synthesis')  String? q3Synthesis, @JsonKey(name: 'q4_argumentation')  String? q4Argumentation)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GuidedReflectionDTO() when $default != null:
return $default(_that.q1Goal,_that.q2Falsification,_that.q3Synthesis,_that.q4Argumentation);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'q1_goal')  String? q1Goal, @JsonKey(name: 'q2_falsification')  String? q2Falsification, @JsonKey(name: 'q3_synthesis')  String? q3Synthesis, @JsonKey(name: 'q4_argumentation')  String? q4Argumentation)  $default,) {final _that = this;
switch (_that) {
case _GuidedReflectionDTO():
return $default(_that.q1Goal,_that.q2Falsification,_that.q3Synthesis,_that.q4Argumentation);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'q1_goal')  String? q1Goal, @JsonKey(name: 'q2_falsification')  String? q2Falsification, @JsonKey(name: 'q3_synthesis')  String? q3Synthesis, @JsonKey(name: 'q4_argumentation')  String? q4Argumentation)?  $default,) {final _that = this;
switch (_that) {
case _GuidedReflectionDTO() when $default != null:
return $default(_that.q1Goal,_that.q2Falsification,_that.q3Synthesis,_that.q4Argumentation);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _GuidedReflectionDTO implements GuidedReflectionDTO {
  const _GuidedReflectionDTO({@JsonKey(name: 'q1_goal') this.q1Goal, @JsonKey(name: 'q2_falsification') this.q2Falsification, @JsonKey(name: 'q3_synthesis') this.q3Synthesis, @JsonKey(name: 'q4_argumentation') this.q4Argumentation});
  factory _GuidedReflectionDTO.fromJson(Map<String, dynamic> json) => _$GuidedReflectionDTOFromJson(json);

/// Tavoite ja strateginen suunnittelu
@override@JsonKey(name: 'q1_goal') final  String? q1Goal;
/// Tekoälyn ohjaus ja kriittinen iterointi
@override@JsonKey(name: 'q2_falsification') final  String? q2Falsification;
/// Oma panos ja luovuus
@override@JsonKey(name: 'q3_synthesis') final  String? q3Synthesis;
/// Laadunvarmistus ja metakognitio
@override@JsonKey(name: 'q4_argumentation') final  String? q4Argumentation;

/// Create a copy of GuidedReflectionDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GuidedReflectionDTOCopyWith<_GuidedReflectionDTO> get copyWith => __$GuidedReflectionDTOCopyWithImpl<_GuidedReflectionDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GuidedReflectionDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _GuidedReflectionDTO&&(identical(other.q1Goal, q1Goal) || other.q1Goal == q1Goal)&&(identical(other.q2Falsification, q2Falsification) || other.q2Falsification == q2Falsification)&&(identical(other.q3Synthesis, q3Synthesis) || other.q3Synthesis == q3Synthesis)&&(identical(other.q4Argumentation, q4Argumentation) || other.q4Argumentation == q4Argumentation));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,q1Goal,q2Falsification,q3Synthesis,q4Argumentation);

@override
String toString() {
  return 'GuidedReflectionDTO(q1Goal: $q1Goal, q2Falsification: $q2Falsification, q3Synthesis: $q3Synthesis, q4Argumentation: $q4Argumentation)';
}


}

/// @nodoc
abstract mixin class _$GuidedReflectionDTOCopyWith<$Res> implements $GuidedReflectionDTOCopyWith<$Res> {
  factory _$GuidedReflectionDTOCopyWith(_GuidedReflectionDTO value, $Res Function(_GuidedReflectionDTO) _then) = __$GuidedReflectionDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'q1_goal') String? q1Goal,@JsonKey(name: 'q2_falsification') String? q2Falsification,@JsonKey(name: 'q3_synthesis') String? q3Synthesis,@JsonKey(name: 'q4_argumentation') String? q4Argumentation
});




}
/// @nodoc
class __$GuidedReflectionDTOCopyWithImpl<$Res>
    implements _$GuidedReflectionDTOCopyWith<$Res> {
  __$GuidedReflectionDTOCopyWithImpl(this._self, this._then);

  final _GuidedReflectionDTO _self;
  final $Res Function(_GuidedReflectionDTO) _then;

/// Create a copy of GuidedReflectionDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? q1Goal = freezed,Object? q2Falsification = freezed,Object? q3Synthesis = freezed,Object? q4Argumentation = freezed,}) {
  return _then(_GuidedReflectionDTO(
q1Goal: freezed == q1Goal ? _self.q1Goal : q1Goal // ignore: cast_nullable_to_non_nullable
as String?,q2Falsification: freezed == q2Falsification ? _self.q2Falsification : q2Falsification // ignore: cast_nullable_to_non_nullable
as String?,q3Synthesis: freezed == q3Synthesis ? _self.q3Synthesis : q3Synthesis // ignore: cast_nullable_to_non_nullable
as String?,q4Argumentation: freezed == q4Argumentation ? _self.q4Argumentation : q4Argumentation // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
