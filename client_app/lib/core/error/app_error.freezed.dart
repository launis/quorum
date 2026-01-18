// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_error.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$AppError {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AppError);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AppError()';
}


}

/// @nodoc
class $AppErrorCopyWith<$Res>  {
$AppErrorCopyWith(AppError _, $Res Function(AppError) __);
}


/// Adds pattern-matching-related methods to [AppError].
extension AppErrorPatterns on AppError {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( _Unknown value)?  unknown,TResult Function( _Network value)?  network,TResult Function( _Server value)?  server,TResult Function( _Unauthorized value)?  unauthorized,TResult Function( _NotFound value)?  notFound,TResult Function( _Validation value)?  validation,TResult Function( _ValidationMissing value)?  validationMissing,TResult Function( _Cancelled value)?  cancelled,TResult Function( _Api value)?  api,required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Unknown() when unknown != null:
return unknown(_that);case _Network() when network != null:
return network(_that);case _Server() when server != null:
return server(_that);case _Unauthorized() when unauthorized != null:
return unauthorized(_that);case _NotFound() when notFound != null:
return notFound(_that);case _Validation() when validation != null:
return validation(_that);case _ValidationMissing() when validationMissing != null:
return validationMissing(_that);case _Cancelled() when cancelled != null:
return cancelled(_that);case _Api() when api != null:
return api(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( _Unknown value)  unknown,required TResult Function( _Network value)  network,required TResult Function( _Server value)  server,required TResult Function( _Unauthorized value)  unauthorized,required TResult Function( _NotFound value)  notFound,required TResult Function( _Validation value)  validation,required TResult Function( _ValidationMissing value)  validationMissing,required TResult Function( _Cancelled value)  cancelled,required TResult Function( _Api value)  api,}){
final _that = this;
switch (_that) {
case _Unknown():
return unknown(_that);case _Network():
return network(_that);case _Server():
return server(_that);case _Unauthorized():
return unauthorized(_that);case _NotFound():
return notFound(_that);case _Validation():
return validation(_that);case _ValidationMissing():
return validationMissing(_that);case _Cancelled():
return cancelled(_that);case _Api():
return api(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( _Unknown value)?  unknown,TResult? Function( _Network value)?  network,TResult? Function( _Server value)?  server,TResult? Function( _Unauthorized value)?  unauthorized,TResult? Function( _NotFound value)?  notFound,TResult? Function( _Validation value)?  validation,TResult? Function( _ValidationMissing value)?  validationMissing,TResult? Function( _Cancelled value)?  cancelled,TResult? Function( _Api value)?  api,}){
final _that = this;
switch (_that) {
case _Unknown() when unknown != null:
return unknown(_that);case _Network() when network != null:
return network(_that);case _Server() when server != null:
return server(_that);case _Unauthorized() when unauthorized != null:
return unauthorized(_that);case _NotFound() when notFound != null:
return notFound(_that);case _Validation() when validation != null:
return validation(_that);case _ValidationMissing() when validationMissing != null:
return validationMissing(_that);case _Cancelled() when cancelled != null:
return cancelled(_that);case _Api() when api != null:
return api(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( Object? error,  StackTrace? stackTrace)?  unknown,TResult Function( Object? error)?  network,TResult Function( String? message,  int? code)?  server,TResult Function()?  unauthorized,TResult Function( String message)?  notFound,TResult Function( ValidationErrorReason reason)?  validation,TResult Function( List<String> fields)?  validationMissing,TResult Function()?  cancelled,TResult Function( String errorCode,  String detail,  int status,  String? instance)?  api,required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Unknown() when unknown != null:
return unknown(_that.error,_that.stackTrace);case _Network() when network != null:
return network(_that.error);case _Server() when server != null:
return server(_that.message,_that.code);case _Unauthorized() when unauthorized != null:
return unauthorized();case _NotFound() when notFound != null:
return notFound(_that.message);case _Validation() when validation != null:
return validation(_that.reason);case _ValidationMissing() when validationMissing != null:
return validationMissing(_that.fields);case _Cancelled() when cancelled != null:
return cancelled();case _Api() when api != null:
return api(_that.errorCode,_that.detail,_that.status,_that.instance);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( Object? error,  StackTrace? stackTrace)  unknown,required TResult Function( Object? error)  network,required TResult Function( String? message,  int? code)  server,required TResult Function()  unauthorized,required TResult Function( String message)  notFound,required TResult Function( ValidationErrorReason reason)  validation,required TResult Function( List<String> fields)  validationMissing,required TResult Function()  cancelled,required TResult Function( String errorCode,  String detail,  int status,  String? instance)  api,}) {final _that = this;
switch (_that) {
case _Unknown():
return unknown(_that.error,_that.stackTrace);case _Network():
return network(_that.error);case _Server():
return server(_that.message,_that.code);case _Unauthorized():
return unauthorized();case _NotFound():
return notFound(_that.message);case _Validation():
return validation(_that.reason);case _ValidationMissing():
return validationMissing(_that.fields);case _Cancelled():
return cancelled();case _Api():
return api(_that.errorCode,_that.detail,_that.status,_that.instance);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( Object? error,  StackTrace? stackTrace)?  unknown,TResult? Function( Object? error)?  network,TResult? Function( String? message,  int? code)?  server,TResult? Function()?  unauthorized,TResult? Function( String message)?  notFound,TResult? Function( ValidationErrorReason reason)?  validation,TResult? Function( List<String> fields)?  validationMissing,TResult? Function()?  cancelled,TResult? Function( String errorCode,  String detail,  int status,  String? instance)?  api,}) {final _that = this;
switch (_that) {
case _Unknown() when unknown != null:
return unknown(_that.error,_that.stackTrace);case _Network() when network != null:
return network(_that.error);case _Server() when server != null:
return server(_that.message,_that.code);case _Unauthorized() when unauthorized != null:
return unauthorized();case _NotFound() when notFound != null:
return notFound(_that.message);case _Validation() when validation != null:
return validation(_that.reason);case _ValidationMissing() when validationMissing != null:
return validationMissing(_that.fields);case _Cancelled() when cancelled != null:
return cancelled();case _Api() when api != null:
return api(_that.errorCode,_that.detail,_that.status,_that.instance);case _:
  return null;

}
}

}

/// @nodoc


class _Unknown implements AppError {
  const _Unknown([this.error, this.stackTrace]);
  

 final  Object? error;
 final  StackTrace? stackTrace;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UnknownCopyWith<_Unknown> get copyWith => __$UnknownCopyWithImpl<_Unknown>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Unknown&&const DeepCollectionEquality().equals(other.error, error)&&(identical(other.stackTrace, stackTrace) || other.stackTrace == stackTrace));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(error),stackTrace);

@override
String toString() {
  return 'AppError.unknown(error: $error, stackTrace: $stackTrace)';
}


}

/// @nodoc
abstract mixin class _$UnknownCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$UnknownCopyWith(_Unknown value, $Res Function(_Unknown) _then) = __$UnknownCopyWithImpl;
@useResult
$Res call({
 Object? error, StackTrace? stackTrace
});




}
/// @nodoc
class __$UnknownCopyWithImpl<$Res>
    implements _$UnknownCopyWith<$Res> {
  __$UnknownCopyWithImpl(this._self, this._then);

  final _Unknown _self;
  final $Res Function(_Unknown) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = freezed,Object? stackTrace = freezed,}) {
  return _then(_Unknown(
freezed == error ? _self.error : error ,freezed == stackTrace ? _self.stackTrace : stackTrace // ignore: cast_nullable_to_non_nullable
as StackTrace?,
  ));
}


}

/// @nodoc


class _Network implements AppError {
  const _Network([this.error]);
  

 final  Object? error;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NetworkCopyWith<_Network> get copyWith => __$NetworkCopyWithImpl<_Network>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Network&&const DeepCollectionEquality().equals(other.error, error));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(error));

@override
String toString() {
  return 'AppError.network(error: $error)';
}


}

/// @nodoc
abstract mixin class _$NetworkCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$NetworkCopyWith(_Network value, $Res Function(_Network) _then) = __$NetworkCopyWithImpl;
@useResult
$Res call({
 Object? error
});




}
/// @nodoc
class __$NetworkCopyWithImpl<$Res>
    implements _$NetworkCopyWith<$Res> {
  __$NetworkCopyWithImpl(this._self, this._then);

  final _Network _self;
  final $Res Function(_Network) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = freezed,}) {
  return _then(_Network(
freezed == error ? _self.error : error ,
  ));
}


}

/// @nodoc


class _Server implements AppError {
  const _Server(this.message, [this.code]);
  

 final  String? message;
 final  int? code;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ServerCopyWith<_Server> get copyWith => __$ServerCopyWithImpl<_Server>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Server&&(identical(other.message, message) || other.message == message)&&(identical(other.code, code) || other.code == code));
}


@override
int get hashCode => Object.hash(runtimeType,message,code);

@override
String toString() {
  return 'AppError.server(message: $message, code: $code)';
}


}

/// @nodoc
abstract mixin class _$ServerCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$ServerCopyWith(_Server value, $Res Function(_Server) _then) = __$ServerCopyWithImpl;
@useResult
$Res call({
 String? message, int? code
});




}
/// @nodoc
class __$ServerCopyWithImpl<$Res>
    implements _$ServerCopyWith<$Res> {
  __$ServerCopyWithImpl(this._self, this._then);

  final _Server _self;
  final $Res Function(_Server) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = freezed,Object? code = freezed,}) {
  return _then(_Server(
freezed == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String?,freezed == code ? _self.code : code // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

/// @nodoc


class _Unauthorized implements AppError {
  const _Unauthorized();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Unauthorized);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AppError.unauthorized()';
}


}




/// @nodoc


class _NotFound implements AppError {
  const _NotFound(this.message);
  

 final  String message;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NotFoundCopyWith<_NotFound> get copyWith => __$NotFoundCopyWithImpl<_NotFound>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _NotFound&&(identical(other.message, message) || other.message == message));
}


@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'AppError.notFound(message: $message)';
}


}

/// @nodoc
abstract mixin class _$NotFoundCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$NotFoundCopyWith(_NotFound value, $Res Function(_NotFound) _then) = __$NotFoundCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class __$NotFoundCopyWithImpl<$Res>
    implements _$NotFoundCopyWith<$Res> {
  __$NotFoundCopyWithImpl(this._self, this._then);

  final _NotFound _self;
  final $Res Function(_NotFound) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(_NotFound(
null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class _Validation implements AppError {
  const _Validation(this.reason);
  

 final  ValidationErrorReason reason;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ValidationCopyWith<_Validation> get copyWith => __$ValidationCopyWithImpl<_Validation>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Validation&&(identical(other.reason, reason) || other.reason == reason));
}


@override
int get hashCode => Object.hash(runtimeType,reason);

@override
String toString() {
  return 'AppError.validation(reason: $reason)';
}


}

/// @nodoc
abstract mixin class _$ValidationCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$ValidationCopyWith(_Validation value, $Res Function(_Validation) _then) = __$ValidationCopyWithImpl;
@useResult
$Res call({
 ValidationErrorReason reason
});




}
/// @nodoc
class __$ValidationCopyWithImpl<$Res>
    implements _$ValidationCopyWith<$Res> {
  __$ValidationCopyWithImpl(this._self, this._then);

  final _Validation _self;
  final $Res Function(_Validation) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? reason = null,}) {
  return _then(_Validation(
null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as ValidationErrorReason,
  ));
}


}

/// @nodoc


class _ValidationMissing implements AppError {
  const _ValidationMissing(final  List<String> fields): _fields = fields;
  

 final  List<String> _fields;
 List<String> get fields {
  if (_fields is EqualUnmodifiableListView) return _fields;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_fields);
}


/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ValidationMissingCopyWith<_ValidationMissing> get copyWith => __$ValidationMissingCopyWithImpl<_ValidationMissing>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ValidationMissing&&const DeepCollectionEquality().equals(other._fields, _fields));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_fields));

@override
String toString() {
  return 'AppError.validationMissing(fields: $fields)';
}


}

/// @nodoc
abstract mixin class _$ValidationMissingCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$ValidationMissingCopyWith(_ValidationMissing value, $Res Function(_ValidationMissing) _then) = __$ValidationMissingCopyWithImpl;
@useResult
$Res call({
 List<String> fields
});




}
/// @nodoc
class __$ValidationMissingCopyWithImpl<$Res>
    implements _$ValidationMissingCopyWith<$Res> {
  __$ValidationMissingCopyWithImpl(this._self, this._then);

  final _ValidationMissing _self;
  final $Res Function(_ValidationMissing) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? fields = null,}) {
  return _then(_ValidationMissing(
null == fields ? _self._fields : fields // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc


class _Cancelled implements AppError {
  const _Cancelled();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Cancelled);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AppError.cancelled()';
}


}




/// @nodoc


class _Api implements AppError {
  const _Api({required this.errorCode, required this.detail, required this.status, this.instance});
  

 final  String errorCode;
 final  String detail;
 final  int status;
 final  String? instance;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ApiCopyWith<_Api> get copyWith => __$ApiCopyWithImpl<_Api>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Api&&(identical(other.errorCode, errorCode) || other.errorCode == errorCode)&&(identical(other.detail, detail) || other.detail == detail)&&(identical(other.status, status) || other.status == status)&&(identical(other.instance, instance) || other.instance == instance));
}


@override
int get hashCode => Object.hash(runtimeType,errorCode,detail,status,instance);

@override
String toString() {
  return 'AppError.api(errorCode: $errorCode, detail: $detail, status: $status, instance: $instance)';
}


}

/// @nodoc
abstract mixin class _$ApiCopyWith<$Res> implements $AppErrorCopyWith<$Res> {
  factory _$ApiCopyWith(_Api value, $Res Function(_Api) _then) = __$ApiCopyWithImpl;
@useResult
$Res call({
 String errorCode, String detail, int status, String? instance
});




}
/// @nodoc
class __$ApiCopyWithImpl<$Res>
    implements _$ApiCopyWith<$Res> {
  __$ApiCopyWithImpl(this._self, this._then);

  final _Api _self;
  final $Res Function(_Api) _then;

/// Create a copy of AppError
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? errorCode = null,Object? detail = null,Object? status = null,Object? instance = freezed,}) {
  return _then(_Api(
errorCode: null == errorCode ? _self.errorCode : errorCode // ignore: cast_nullable_to_non_nullable
as String,detail: null == detail ? _self.detail : detail // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as int,instance: freezed == instance ? _self.instance : instance // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
