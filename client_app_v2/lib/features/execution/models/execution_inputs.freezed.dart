// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_inputs.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionInputs {

@JsonKey(name: 'raw_inputs') Map<String, dynamic> get rawInputs;@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> get dynamicInputs;@JsonKey(name: 'user_role') String? get userRole;@JsonKey(name: 'target_locale') String? get targetLocale;
/// Create a copy of ExecutionInputs
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionInputsCopyWith<ExecutionInputs> get copyWith => _$ExecutionInputsCopyWithImpl<ExecutionInputs>(this as ExecutionInputs, _$identity);

  /// Serializes this ExecutionInputs to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionInputs(rawInputs: $rawInputs, dynamicInputs: $dynamicInputs, userRole: $userRole, targetLocale: $targetLocale)';
}


}

/// @nodoc
abstract mixin class $ExecutionInputsCopyWith<$Res>  {
  factory $ExecutionInputsCopyWith(ExecutionInputs value, $Res Function(ExecutionInputs) _then) = _$ExecutionInputsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'raw_inputs') Map<String, dynamic> rawInputs,@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> dynamicInputs,@JsonKey(name: 'user_role') String? userRole,@JsonKey(name: 'target_locale') String? targetLocale
});




}
/// @nodoc
class _$ExecutionInputsCopyWithImpl<$Res>
    implements $ExecutionInputsCopyWith<$Res> {
  _$ExecutionInputsCopyWithImpl(this._self, this._then);

  final ExecutionInputs _self;
  final $Res Function(ExecutionInputs) _then;

/// Create a copy of ExecutionInputs
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? rawInputs = null,Object? dynamicInputs = null,Object? userRole = freezed,Object? targetLocale = freezed,}) {
  return _then(_self.copyWith(
rawInputs: null == rawInputs ? _self.rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,dynamicInputs: null == dynamicInputs ? _self.dynamicInputs : dynamicInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,userRole: freezed == userRole ? _self.userRole : userRole // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: freezed == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionInputs].
extension ExecutionInputsPatterns on ExecutionInputs {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionInputs value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionInputs() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionInputs value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionInputs():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionInputs value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionInputs() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'raw_inputs')  Map<String, dynamic> rawInputs, @JsonKey(name: 'dynamic_inputs')  Map<String, dynamic> dynamicInputs, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'target_locale')  String? targetLocale)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionInputs() when $default != null:
return $default(_that.rawInputs,_that.dynamicInputs,_that.userRole,_that.targetLocale);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'raw_inputs')  Map<String, dynamic> rawInputs, @JsonKey(name: 'dynamic_inputs')  Map<String, dynamic> dynamicInputs, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'target_locale')  String? targetLocale)  $default,) {final _that = this;
switch (_that) {
case _ExecutionInputs():
return $default(_that.rawInputs,_that.dynamicInputs,_that.userRole,_that.targetLocale);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'raw_inputs')  Map<String, dynamic> rawInputs, @JsonKey(name: 'dynamic_inputs')  Map<String, dynamic> dynamicInputs, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'target_locale')  String? targetLocale)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionInputs() when $default != null:
return $default(_that.rawInputs,_that.dynamicInputs,_that.userRole,_that.targetLocale);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionInputs extends ExecutionInputs {
  const _ExecutionInputs({@JsonKey(name: 'raw_inputs') final  Map<String, dynamic> rawInputs = const {}, @JsonKey(name: 'dynamic_inputs') final  Map<String, dynamic> dynamicInputs = const {}, @JsonKey(name: 'user_role') this.userRole, @JsonKey(name: 'target_locale') this.targetLocale}): _rawInputs = rawInputs,_dynamicInputs = dynamicInputs,super._();
  factory _ExecutionInputs.fromJson(Map<String, dynamic> json) => _$ExecutionInputsFromJson(json);

 final  Map<String, dynamic> _rawInputs;
@override@JsonKey(name: 'raw_inputs') Map<String, dynamic> get rawInputs {
  if (_rawInputs is EqualUnmodifiableMapView) return _rawInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_rawInputs);
}

 final  Map<String, dynamic> _dynamicInputs;
@override@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> get dynamicInputs {
  if (_dynamicInputs is EqualUnmodifiableMapView) return _dynamicInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_dynamicInputs);
}

@override@JsonKey(name: 'user_role') final  String? userRole;
@override@JsonKey(name: 'target_locale') final  String? targetLocale;

/// Create a copy of ExecutionInputs
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionInputsCopyWith<_ExecutionInputs> get copyWith => __$ExecutionInputsCopyWithImpl<_ExecutionInputs>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionInputsToJson(this, );
}



@override
String toString() {
  return 'ExecutionInputs(rawInputs: $rawInputs, dynamicInputs: $dynamicInputs, userRole: $userRole, targetLocale: $targetLocale)';
}


}

/// @nodoc
abstract mixin class _$ExecutionInputsCopyWith<$Res> implements $ExecutionInputsCopyWith<$Res> {
  factory _$ExecutionInputsCopyWith(_ExecutionInputs value, $Res Function(_ExecutionInputs) _then) = __$ExecutionInputsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'raw_inputs') Map<String, dynamic> rawInputs,@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> dynamicInputs,@JsonKey(name: 'user_role') String? userRole,@JsonKey(name: 'target_locale') String? targetLocale
});




}
/// @nodoc
class __$ExecutionInputsCopyWithImpl<$Res>
    implements _$ExecutionInputsCopyWith<$Res> {
  __$ExecutionInputsCopyWithImpl(this._self, this._then);

  final _ExecutionInputs _self;
  final $Res Function(_ExecutionInputs) _then;

/// Create a copy of ExecutionInputs
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? rawInputs = null,Object? dynamicInputs = null,Object? userRole = freezed,Object? targetLocale = freezed,}) {
  return _then(_ExecutionInputs(
rawInputs: null == rawInputs ? _self._rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,dynamicInputs: null == dynamicInputs ? _self._dynamicInputs : dynamicInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,userRole: freezed == userRole ? _self.userRole : userRole // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: freezed == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
