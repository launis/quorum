// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_file.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionFile {

 String get name; String? get path; List<int>? get bytes;
/// Create a copy of ExecutionFile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionFileCopyWith<ExecutionFile> get copyWith => _$ExecutionFileCopyWithImpl<ExecutionFile>(this as ExecutionFile, _$identity);

  /// Serializes this ExecutionFile to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionFile&&(identical(other.name, name) || other.name == name)&&(identical(other.path, path) || other.path == path)&&const DeepCollectionEquality().equals(other.bytes, bytes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,path,const DeepCollectionEquality().hash(bytes));

@override
String toString() {
  return 'ExecutionFile(name: $name, path: $path, bytes: $bytes)';
}


}

/// @nodoc
abstract mixin class $ExecutionFileCopyWith<$Res>  {
  factory $ExecutionFileCopyWith(ExecutionFile value, $Res Function(ExecutionFile) _then) = _$ExecutionFileCopyWithImpl;
@useResult
$Res call({
 String name, String? path, List<int>? bytes
});




}
/// @nodoc
class _$ExecutionFileCopyWithImpl<$Res>
    implements $ExecutionFileCopyWith<$Res> {
  _$ExecutionFileCopyWithImpl(this._self, this._then);

  final ExecutionFile _self;
  final $Res Function(ExecutionFile) _then;

/// Create a copy of ExecutionFile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? path = freezed,Object? bytes = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,path: freezed == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String?,bytes: freezed == bytes ? _self.bytes : bytes // ignore: cast_nullable_to_non_nullable
as List<int>?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionFile].
extension ExecutionFilePatterns on ExecutionFile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionFile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionFile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionFile value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionFile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionFile value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionFile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String? path,  List<int>? bytes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionFile() when $default != null:
return $default(_that.name,_that.path,_that.bytes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String? path,  List<int>? bytes)  $default,) {final _that = this;
switch (_that) {
case _ExecutionFile():
return $default(_that.name,_that.path,_that.bytes);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String? path,  List<int>? bytes)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionFile() when $default != null:
return $default(_that.name,_that.path,_that.bytes);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ExecutionFile implements ExecutionFile {
  const _ExecutionFile({required this.name, this.path, final  List<int>? bytes}): _bytes = bytes;
  factory _ExecutionFile.fromJson(Map<String, dynamic> json) => _$ExecutionFileFromJson(json);

@override final  String name;
@override final  String? path;
 final  List<int>? _bytes;
@override List<int>? get bytes {
  final value = _bytes;
  if (value == null) return null;
  if (_bytes is EqualUnmodifiableListView) return _bytes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of ExecutionFile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionFileCopyWith<_ExecutionFile> get copyWith => __$ExecutionFileCopyWithImpl<_ExecutionFile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionFileToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ExecutionFile&&(identical(other.name, name) || other.name == name)&&(identical(other.path, path) || other.path == path)&&const DeepCollectionEquality().equals(other._bytes, _bytes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,path,const DeepCollectionEquality().hash(_bytes));

@override
String toString() {
  return 'ExecutionFile(name: $name, path: $path, bytes: $bytes)';
}


}

/// @nodoc
abstract mixin class _$ExecutionFileCopyWith<$Res> implements $ExecutionFileCopyWith<$Res> {
  factory _$ExecutionFileCopyWith(_ExecutionFile value, $Res Function(_ExecutionFile) _then) = __$ExecutionFileCopyWithImpl;
@override @useResult
$Res call({
 String name, String? path, List<int>? bytes
});




}
/// @nodoc
class __$ExecutionFileCopyWithImpl<$Res>
    implements _$ExecutionFileCopyWith<$Res> {
  __$ExecutionFileCopyWithImpl(this._self, this._then);

  final _ExecutionFile _self;
  final $Res Function(_ExecutionFile) _then;

/// Create a copy of ExecutionFile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? path = freezed,Object? bytes = freezed,}) {
  return _then(_ExecutionFile(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,path: freezed == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String?,bytes: freezed == bytes ? _self._bytes : bytes // ignore: cast_nullable_to_non_nullable
as List<int>?,
  ));
}


}

// dart format on
