// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'generic_status_response_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$GenericStatusResponseDto {

 String get status; String get message;
/// Create a copy of GenericStatusResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GenericStatusResponseDtoCopyWith<GenericStatusResponseDto> get copyWith => _$GenericStatusResponseDtoCopyWithImpl<GenericStatusResponseDto>(this as GenericStatusResponseDto, _$identity);

  /// Serializes this GenericStatusResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'GenericStatusResponseDto(status: $status, message: $message)';
}


}

/// @nodoc
abstract mixin class $GenericStatusResponseDtoCopyWith<$Res>  {
  factory $GenericStatusResponseDtoCopyWith(GenericStatusResponseDto value, $Res Function(GenericStatusResponseDto) _then) = _$GenericStatusResponseDtoCopyWithImpl;
@useResult
$Res call({
 String status, String message
});




}
/// @nodoc
class _$GenericStatusResponseDtoCopyWithImpl<$Res>
    implements $GenericStatusResponseDtoCopyWith<$Res> {
  _$GenericStatusResponseDtoCopyWithImpl(this._self, this._then);

  final GenericStatusResponseDto _self;
  final $Res Function(GenericStatusResponseDto) _then;

/// Create a copy of GenericStatusResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? status = null,Object? message = null,}) {
  return _then(_self.copyWith(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [GenericStatusResponseDto].
extension GenericStatusResponseDtoPatterns on GenericStatusResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GenericStatusResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GenericStatusResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GenericStatusResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _GenericStatusResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GenericStatusResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _GenericStatusResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String status,  String message)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GenericStatusResponseDto() when $default != null:
return $default(_that.status,_that.message);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String status,  String message)  $default,) {final _that = this;
switch (_that) {
case _GenericStatusResponseDto():
return $default(_that.status,_that.message);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String status,  String message)?  $default,) {final _that = this;
switch (_that) {
case _GenericStatusResponseDto() when $default != null:
return $default(_that.status,_that.message);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _GenericStatusResponseDto extends GenericStatusResponseDto {
  const _GenericStatusResponseDto({this.status = 'ok', required this.message}): super._();
  factory _GenericStatusResponseDto.fromJson(Map<String, dynamic> json) => _$GenericStatusResponseDtoFromJson(json);

@override@JsonKey() final  String status;
@override final  String message;

/// Create a copy of GenericStatusResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GenericStatusResponseDtoCopyWith<_GenericStatusResponseDto> get copyWith => __$GenericStatusResponseDtoCopyWithImpl<_GenericStatusResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GenericStatusResponseDtoToJson(this, );
}



@override
String toString() {
  return 'GenericStatusResponseDto(status: $status, message: $message)';
}


}

/// @nodoc
abstract mixin class _$GenericStatusResponseDtoCopyWith<$Res> implements $GenericStatusResponseDtoCopyWith<$Res> {
  factory _$GenericStatusResponseDtoCopyWith(_GenericStatusResponseDto value, $Res Function(_GenericStatusResponseDto) _then) = __$GenericStatusResponseDtoCopyWithImpl;
@override @useResult
$Res call({
 String status, String message
});




}
/// @nodoc
class __$GenericStatusResponseDtoCopyWithImpl<$Res>
    implements _$GenericStatusResponseDtoCopyWith<$Res> {
  __$GenericStatusResponseDtoCopyWithImpl(this._self, this._then);

  final _GenericStatusResponseDto _self;
  final $Res Function(_GenericStatusResponseDto) _then;

/// Create a copy of GenericStatusResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? status = null,Object? message = null,}) {
  return _then(_GenericStatusResponseDto(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
