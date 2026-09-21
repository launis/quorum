// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'llm_platform.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LlmPlatform {

 String get id; String get label;@JsonKey(name: 'has_regions') bool get hasRegions;
/// Create a copy of LlmPlatform
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LlmPlatformCopyWith<LlmPlatform> get copyWith => _$LlmPlatformCopyWithImpl<LlmPlatform>(this as LlmPlatform, _$identity);

  /// Serializes this LlmPlatform to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'LlmPlatform(id: $id, label: $label, hasRegions: $hasRegions)';
}


}

/// @nodoc
abstract mixin class $LlmPlatformCopyWith<$Res>  {
  factory $LlmPlatformCopyWith(LlmPlatform value, $Res Function(LlmPlatform) _then) = _$LlmPlatformCopyWithImpl;
@useResult
$Res call({
 String id, String label,@JsonKey(name: 'has_regions') bool hasRegions
});




}
/// @nodoc
class _$LlmPlatformCopyWithImpl<$Res>
    implements $LlmPlatformCopyWith<$Res> {
  _$LlmPlatformCopyWithImpl(this._self, this._then);

  final LlmPlatform _self;
  final $Res Function(LlmPlatform) _then;

/// Create a copy of LlmPlatform
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? label = null,Object? hasRegions = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,hasRegions: null == hasRegions ? _self.hasRegions : hasRegions // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [LlmPlatform].
extension LlmPlatformPatterns on LlmPlatform {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LlmPlatform value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LlmPlatform() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LlmPlatform value)  $default,){
final _that = this;
switch (_that) {
case _LlmPlatform():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LlmPlatform value)?  $default,){
final _that = this;
switch (_that) {
case _LlmPlatform() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String label, @JsonKey(name: 'has_regions')  bool hasRegions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LlmPlatform() when $default != null:
return $default(_that.id,_that.label,_that.hasRegions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String label, @JsonKey(name: 'has_regions')  bool hasRegions)  $default,) {final _that = this;
switch (_that) {
case _LlmPlatform():
return $default(_that.id,_that.label,_that.hasRegions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String label, @JsonKey(name: 'has_regions')  bool hasRegions)?  $default,) {final _that = this;
switch (_that) {
case _LlmPlatform() when $default != null:
return $default(_that.id,_that.label,_that.hasRegions);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _LlmPlatform implements LlmPlatform {
  const _LlmPlatform({required this.id, required this.label, @JsonKey(name: 'has_regions') required this.hasRegions});
  factory _LlmPlatform.fromJson(Map<String, dynamic> json) => _$LlmPlatformFromJson(json);

@override final  String id;
@override final  String label;
@override@JsonKey(name: 'has_regions') final  bool hasRegions;

/// Create a copy of LlmPlatform
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LlmPlatformCopyWith<_LlmPlatform> get copyWith => __$LlmPlatformCopyWithImpl<_LlmPlatform>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LlmPlatformToJson(this, );
}



@override
String toString() {
  return 'LlmPlatform(id: $id, label: $label, hasRegions: $hasRegions)';
}


}

/// @nodoc
abstract mixin class _$LlmPlatformCopyWith<$Res> implements $LlmPlatformCopyWith<$Res> {
  factory _$LlmPlatformCopyWith(_LlmPlatform value, $Res Function(_LlmPlatform) _then) = __$LlmPlatformCopyWithImpl;
@override @useResult
$Res call({
 String id, String label,@JsonKey(name: 'has_regions') bool hasRegions
});




}
/// @nodoc
class __$LlmPlatformCopyWithImpl<$Res>
    implements _$LlmPlatformCopyWith<$Res> {
  __$LlmPlatformCopyWithImpl(this._self, this._then);

  final _LlmPlatform _self;
  final $Res Function(_LlmPlatform) _then;

/// Create a copy of LlmPlatform
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? label = null,Object? hasRegions = null,}) {
  return _then(_LlmPlatform(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,hasRegions: null == hasRegions ? _self.hasRegions : hasRegions // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
