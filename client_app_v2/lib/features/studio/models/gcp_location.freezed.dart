// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'gcp_location.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$GcpLocation {

 String get id; String get label; String get description;
/// Create a copy of GcpLocation
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GcpLocationCopyWith<GcpLocation> get copyWith => _$GcpLocationCopyWithImpl<GcpLocation>(this as GcpLocation, _$identity);

  /// Serializes this GcpLocation to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'GcpLocation(id: $id, label: $label, description: $description)';
}


}

/// @nodoc
abstract mixin class $GcpLocationCopyWith<$Res>  {
  factory $GcpLocationCopyWith(GcpLocation value, $Res Function(GcpLocation) _then) = _$GcpLocationCopyWithImpl;
@useResult
$Res call({
 String id, String label, String description
});




}
/// @nodoc
class _$GcpLocationCopyWithImpl<$Res>
    implements $GcpLocationCopyWith<$Res> {
  _$GcpLocationCopyWithImpl(this._self, this._then);

  final GcpLocation _self;
  final $Res Function(GcpLocation) _then;

/// Create a copy of GcpLocation
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? label = null,Object? description = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [GcpLocation].
extension GcpLocationPatterns on GcpLocation {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GcpLocation value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GcpLocation() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GcpLocation value)  $default,){
final _that = this;
switch (_that) {
case _GcpLocation():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GcpLocation value)?  $default,){
final _that = this;
switch (_that) {
case _GcpLocation() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String label,  String description)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GcpLocation() when $default != null:
return $default(_that.id,_that.label,_that.description);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String label,  String description)  $default,) {final _that = this;
switch (_that) {
case _GcpLocation():
return $default(_that.id,_that.label,_that.description);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String label,  String description)?  $default,) {final _that = this;
switch (_that) {
case _GcpLocation() when $default != null:
return $default(_that.id,_that.label,_that.description);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _GcpLocation extends GcpLocation {
  const _GcpLocation({required this.id, required this.label, required this.description}): super._();
  factory _GcpLocation.fromJson(Map<String, dynamic> json) => _$GcpLocationFromJson(json);

@override final  String id;
@override final  String label;
@override final  String description;

/// Create a copy of GcpLocation
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GcpLocationCopyWith<_GcpLocation> get copyWith => __$GcpLocationCopyWithImpl<_GcpLocation>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GcpLocationToJson(this, );
}



@override
String toString() {
  return 'GcpLocation(id: $id, label: $label, description: $description)';
}


}

/// @nodoc
abstract mixin class _$GcpLocationCopyWith<$Res> implements $GcpLocationCopyWith<$Res> {
  factory _$GcpLocationCopyWith(_GcpLocation value, $Res Function(_GcpLocation) _then) = __$GcpLocationCopyWithImpl;
@override @useResult
$Res call({
 String id, String label, String description
});




}
/// @nodoc
class __$GcpLocationCopyWithImpl<$Res>
    implements _$GcpLocationCopyWith<$Res> {
  __$GcpLocationCopyWithImpl(this._self, this._then);

  final _GcpLocation _self;
  final $Res Function(_GcpLocation) _then;

/// Create a copy of GcpLocation
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? label = null,Object? description = null,}) {
  return _then(_GcpLocation(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
