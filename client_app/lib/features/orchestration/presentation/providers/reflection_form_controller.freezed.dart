// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'reflection_form_controller.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReflectionFormState {

 ReflectionInputMode get inputMode; String get q1Goal; String get q2Falsification; String get q3Synthesis; String get q4Argumentation; String get freeText;
/// Create a copy of ReflectionFormState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReflectionFormStateCopyWith<ReflectionFormState> get copyWith => _$ReflectionFormStateCopyWithImpl<ReflectionFormState>(this as ReflectionFormState, _$identity);

  /// Serializes this ReflectionFormState to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReflectionFormState&&(identical(other.inputMode, inputMode) || other.inputMode == inputMode)&&(identical(other.q1Goal, q1Goal) || other.q1Goal == q1Goal)&&(identical(other.q2Falsification, q2Falsification) || other.q2Falsification == q2Falsification)&&(identical(other.q3Synthesis, q3Synthesis) || other.q3Synthesis == q3Synthesis)&&(identical(other.q4Argumentation, q4Argumentation) || other.q4Argumentation == q4Argumentation)&&(identical(other.freeText, freeText) || other.freeText == freeText));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,inputMode,q1Goal,q2Falsification,q3Synthesis,q4Argumentation,freeText);

@override
String toString() {
  return 'ReflectionFormState(inputMode: $inputMode, q1Goal: $q1Goal, q2Falsification: $q2Falsification, q3Synthesis: $q3Synthesis, q4Argumentation: $q4Argumentation, freeText: $freeText)';
}


}

/// @nodoc
abstract mixin class $ReflectionFormStateCopyWith<$Res>  {
  factory $ReflectionFormStateCopyWith(ReflectionFormState value, $Res Function(ReflectionFormState) _then) = _$ReflectionFormStateCopyWithImpl;
@useResult
$Res call({
 ReflectionInputMode inputMode, String q1Goal, String q2Falsification, String q3Synthesis, String q4Argumentation, String freeText
});




}
/// @nodoc
class _$ReflectionFormStateCopyWithImpl<$Res>
    implements $ReflectionFormStateCopyWith<$Res> {
  _$ReflectionFormStateCopyWithImpl(this._self, this._then);

  final ReflectionFormState _self;
  final $Res Function(ReflectionFormState) _then;

/// Create a copy of ReflectionFormState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? inputMode = null,Object? q1Goal = null,Object? q2Falsification = null,Object? q3Synthesis = null,Object? q4Argumentation = null,Object? freeText = null,}) {
  return _then(_self.copyWith(
inputMode: null == inputMode ? _self.inputMode : inputMode // ignore: cast_nullable_to_non_nullable
as ReflectionInputMode,q1Goal: null == q1Goal ? _self.q1Goal : q1Goal // ignore: cast_nullable_to_non_nullable
as String,q2Falsification: null == q2Falsification ? _self.q2Falsification : q2Falsification // ignore: cast_nullable_to_non_nullable
as String,q3Synthesis: null == q3Synthesis ? _self.q3Synthesis : q3Synthesis // ignore: cast_nullable_to_non_nullable
as String,q4Argumentation: null == q4Argumentation ? _self.q4Argumentation : q4Argumentation // ignore: cast_nullable_to_non_nullable
as String,freeText: null == freeText ? _self.freeText : freeText // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ReflectionFormState].
extension ReflectionFormStatePatterns on ReflectionFormState {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReflectionFormState value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReflectionFormState() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReflectionFormState value)  $default,){
final _that = this;
switch (_that) {
case _ReflectionFormState():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReflectionFormState value)?  $default,){
final _that = this;
switch (_that) {
case _ReflectionFormState() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( ReflectionInputMode inputMode,  String q1Goal,  String q2Falsification,  String q3Synthesis,  String q4Argumentation,  String freeText)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReflectionFormState() when $default != null:
return $default(_that.inputMode,_that.q1Goal,_that.q2Falsification,_that.q3Synthesis,_that.q4Argumentation,_that.freeText);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( ReflectionInputMode inputMode,  String q1Goal,  String q2Falsification,  String q3Synthesis,  String q4Argumentation,  String freeText)  $default,) {final _that = this;
switch (_that) {
case _ReflectionFormState():
return $default(_that.inputMode,_that.q1Goal,_that.q2Falsification,_that.q3Synthesis,_that.q4Argumentation,_that.freeText);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( ReflectionInputMode inputMode,  String q1Goal,  String q2Falsification,  String q3Synthesis,  String q4Argumentation,  String freeText)?  $default,) {final _that = this;
switch (_that) {
case _ReflectionFormState() when $default != null:
return $default(_that.inputMode,_that.q1Goal,_that.q2Falsification,_that.q3Synthesis,_that.q4Argumentation,_that.freeText);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReflectionFormState implements ReflectionFormState {
  const _ReflectionFormState({this.inputMode = ReflectionInputMode.guided, this.q1Goal = '', this.q2Falsification = '', this.q3Synthesis = '', this.q4Argumentation = '', this.freeText = ''});
  factory _ReflectionFormState.fromJson(Map<String, dynamic> json) => _$ReflectionFormStateFromJson(json);

@override@JsonKey() final  ReflectionInputMode inputMode;
@override@JsonKey() final  String q1Goal;
@override@JsonKey() final  String q2Falsification;
@override@JsonKey() final  String q3Synthesis;
@override@JsonKey() final  String q4Argumentation;
@override@JsonKey() final  String freeText;

/// Create a copy of ReflectionFormState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReflectionFormStateCopyWith<_ReflectionFormState> get copyWith => __$ReflectionFormStateCopyWithImpl<_ReflectionFormState>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReflectionFormStateToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReflectionFormState&&(identical(other.inputMode, inputMode) || other.inputMode == inputMode)&&(identical(other.q1Goal, q1Goal) || other.q1Goal == q1Goal)&&(identical(other.q2Falsification, q2Falsification) || other.q2Falsification == q2Falsification)&&(identical(other.q3Synthesis, q3Synthesis) || other.q3Synthesis == q3Synthesis)&&(identical(other.q4Argumentation, q4Argumentation) || other.q4Argumentation == q4Argumentation)&&(identical(other.freeText, freeText) || other.freeText == freeText));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,inputMode,q1Goal,q2Falsification,q3Synthesis,q4Argumentation,freeText);

@override
String toString() {
  return 'ReflectionFormState(inputMode: $inputMode, q1Goal: $q1Goal, q2Falsification: $q2Falsification, q3Synthesis: $q3Synthesis, q4Argumentation: $q4Argumentation, freeText: $freeText)';
}


}

/// @nodoc
abstract mixin class _$ReflectionFormStateCopyWith<$Res> implements $ReflectionFormStateCopyWith<$Res> {
  factory _$ReflectionFormStateCopyWith(_ReflectionFormState value, $Res Function(_ReflectionFormState) _then) = __$ReflectionFormStateCopyWithImpl;
@override @useResult
$Res call({
 ReflectionInputMode inputMode, String q1Goal, String q2Falsification, String q3Synthesis, String q4Argumentation, String freeText
});




}
/// @nodoc
class __$ReflectionFormStateCopyWithImpl<$Res>
    implements _$ReflectionFormStateCopyWith<$Res> {
  __$ReflectionFormStateCopyWithImpl(this._self, this._then);

  final _ReflectionFormState _self;
  final $Res Function(_ReflectionFormState) _then;

/// Create a copy of ReflectionFormState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? inputMode = null,Object? q1Goal = null,Object? q2Falsification = null,Object? q3Synthesis = null,Object? q4Argumentation = null,Object? freeText = null,}) {
  return _then(_ReflectionFormState(
inputMode: null == inputMode ? _self.inputMode : inputMode // ignore: cast_nullable_to_non_nullable
as ReflectionInputMode,q1Goal: null == q1Goal ? _self.q1Goal : q1Goal // ignore: cast_nullable_to_non_nullable
as String,q2Falsification: null == q2Falsification ? _self.q2Falsification : q2Falsification // ignore: cast_nullable_to_non_nullable
as String,q3Synthesis: null == q3Synthesis ? _self.q3Synthesis : q3Synthesis // ignore: cast_nullable_to_non_nullable
as String,q4Argumentation: null == q4Argumentation ? _self.q4Argumentation : q4Argumentation // ignore: cast_nullable_to_non_nullable
as String,freeText: null == freeText ? _self.freeText : freeText // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
