// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_exception.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$AppException {

 String get type; String get title; int get status; String get detail; String? get instance; Map<String, dynamic> get extensions;
/// Create a copy of AppException
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AppExceptionCopyWith<AppException> get copyWith => _$AppExceptionCopyWithImpl<AppException>(this as AppException, _$identity);

  /// Serializes this AppException to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AppException&&(identical(other.type, type) || other.type == type)&&(identical(other.title, title) || other.title == title)&&(identical(other.status, status) || other.status == status)&&(identical(other.detail, detail) || other.detail == detail)&&(identical(other.instance, instance) || other.instance == instance)&&const DeepCollectionEquality().equals(other.extensions, extensions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,title,status,detail,instance,const DeepCollectionEquality().hash(extensions));

@override
String toString() {
  return 'AppException(type: $type, title: $title, status: $status, detail: $detail, instance: $instance, extensions: $extensions)';
}


}

/// @nodoc
abstract mixin class $AppExceptionCopyWith<$Res>  {
  factory $AppExceptionCopyWith(AppException value, $Res Function(AppException) _then) = _$AppExceptionCopyWithImpl;
@useResult
$Res call({
 String type, String title, int status, String detail, String? instance, Map<String, dynamic> extensions
});




}
/// @nodoc
class _$AppExceptionCopyWithImpl<$Res>
    implements $AppExceptionCopyWith<$Res> {
  _$AppExceptionCopyWithImpl(this._self, this._then);

  final AppException _self;
  final $Res Function(AppException) _then;

/// Create a copy of AppException
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = null,Object? title = null,Object? status = null,Object? detail = null,Object? instance = freezed,Object? extensions = null,}) {
  return _then(_self.copyWith(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as int,detail: null == detail ? _self.detail : detail // ignore: cast_nullable_to_non_nullable
as String,instance: freezed == instance ? _self.instance : instance // ignore: cast_nullable_to_non_nullable
as String?,extensions: null == extensions ? _self.extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [AppException].
extension AppExceptionPatterns on AppException {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AppException value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AppException() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AppException value)  $default,){
final _that = this;
switch (_that) {
case _AppException():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AppException value)?  $default,){
final _that = this;
switch (_that) {
case _AppException() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String type,  String title,  int status,  String detail,  String? instance,  Map<String, dynamic> extensions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AppException() when $default != null:
return $default(_that.type,_that.title,_that.status,_that.detail,_that.instance,_that.extensions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String type,  String title,  int status,  String detail,  String? instance,  Map<String, dynamic> extensions)  $default,) {final _that = this;
switch (_that) {
case _AppException():
return $default(_that.type,_that.title,_that.status,_that.detail,_that.instance,_that.extensions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String type,  String title,  int status,  String detail,  String? instance,  Map<String, dynamic> extensions)?  $default,) {final _that = this;
switch (_that) {
case _AppException() when $default != null:
return $default(_that.type,_that.title,_that.status,_that.detail,_that.instance,_that.extensions);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AppException extends AppException {
  const _AppException({this.type = 'about:blank', this.title = 'Error', this.status = 500, this.detail = 'Unknown error', this.instance, final  Map<String, dynamic> extensions = const <String, dynamic>{}}): _extensions = extensions,super._();
  factory _AppException.fromJson(Map<String, dynamic> json) => _$AppExceptionFromJson(json);

@override@JsonKey() final  String type;
@override@JsonKey() final  String title;
@override@JsonKey() final  int status;
@override@JsonKey() final  String detail;
@override final  String? instance;
 final  Map<String, dynamic> _extensions;
@override@JsonKey() Map<String, dynamic> get extensions {
  if (_extensions is EqualUnmodifiableMapView) return _extensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_extensions);
}


/// Create a copy of AppException
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AppExceptionCopyWith<_AppException> get copyWith => __$AppExceptionCopyWithImpl<_AppException>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AppExceptionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AppException&&(identical(other.type, type) || other.type == type)&&(identical(other.title, title) || other.title == title)&&(identical(other.status, status) || other.status == status)&&(identical(other.detail, detail) || other.detail == detail)&&(identical(other.instance, instance) || other.instance == instance)&&const DeepCollectionEquality().equals(other._extensions, _extensions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,title,status,detail,instance,const DeepCollectionEquality().hash(_extensions));

@override
String toString() {
  return 'AppException(type: $type, title: $title, status: $status, detail: $detail, instance: $instance, extensions: $extensions)';
}


}

/// @nodoc
abstract mixin class _$AppExceptionCopyWith<$Res> implements $AppExceptionCopyWith<$Res> {
  factory _$AppExceptionCopyWith(_AppException value, $Res Function(_AppException) _then) = __$AppExceptionCopyWithImpl;
@override @useResult
$Res call({
 String type, String title, int status, String detail, String? instance, Map<String, dynamic> extensions
});




}
/// @nodoc
class __$AppExceptionCopyWithImpl<$Res>
    implements _$AppExceptionCopyWith<$Res> {
  __$AppExceptionCopyWithImpl(this._self, this._then);

  final _AppException _self;
  final $Res Function(_AppException) _then;

/// Create a copy of AppException
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = null,Object? title = null,Object? status = null,Object? detail = null,Object? instance = freezed,Object? extensions = null,}) {
  return _then(_AppException(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as int,detail: null == detail ? _self.detail : detail // ignore: cast_nullable_to_non_nullable
as String,instance: freezed == instance ? _self.instance : instance // ignore: cast_nullable_to_non_nullable
as String?,extensions: null == extensions ? _self._extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
