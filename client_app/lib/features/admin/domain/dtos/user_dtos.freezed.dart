// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user_dtos.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$UserCreateDto {

 String get email; String get password;@JsonKey(name: 'display_name') String get displayName; UserRole get role;@JsonKey(name: 'organization_id') String? get organizationId;
/// Create a copy of UserCreateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserCreateDtoCopyWith<UserCreateDto> get copyWith => _$UserCreateDtoCopyWithImpl<UserCreateDto>(this as UserCreateDto, _$identity);

  /// Serializes this UserCreateDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserCreateDto&&(identical(other.email, email) || other.email == email)&&(identical(other.password, password) || other.password == password)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.role, role) || other.role == role)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,email,password,displayName,role,organizationId);

@override
String toString() {
  return 'UserCreateDto(email: $email, password: $password, displayName: $displayName, role: $role, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class $UserCreateDtoCopyWith<$Res>  {
  factory $UserCreateDtoCopyWith(UserCreateDto value, $Res Function(UserCreateDto) _then) = _$UserCreateDtoCopyWithImpl;
@useResult
$Res call({
 String email, String password,@JsonKey(name: 'display_name') String displayName, UserRole role,@JsonKey(name: 'organization_id') String? organizationId
});




}
/// @nodoc
class _$UserCreateDtoCopyWithImpl<$Res>
    implements $UserCreateDtoCopyWith<$Res> {
  _$UserCreateDtoCopyWithImpl(this._self, this._then);

  final UserCreateDto _self;
  final $Res Function(UserCreateDto) _then;

/// Create a copy of UserCreateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? email = null,Object? password = null,Object? displayName = null,Object? role = null,Object? organizationId = freezed,}) {
  return _then(_self.copyWith(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,password: null == password ? _self.password : password // ignore: cast_nullable_to_non_nullable
as String,displayName: null == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserCreateDto].
extension UserCreateDtoPatterns on UserCreateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserCreateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserCreateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserCreateDto value)  $default,){
final _that = this;
switch (_that) {
case _UserCreateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserCreateDto value)?  $default,){
final _that = this;
switch (_that) {
case _UserCreateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String email,  String password, @JsonKey(name: 'display_name')  String displayName,  UserRole role, @JsonKey(name: 'organization_id')  String? organizationId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserCreateDto() when $default != null:
return $default(_that.email,_that.password,_that.displayName,_that.role,_that.organizationId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String email,  String password, @JsonKey(name: 'display_name')  String displayName,  UserRole role, @JsonKey(name: 'organization_id')  String? organizationId)  $default,) {final _that = this;
switch (_that) {
case _UserCreateDto():
return $default(_that.email,_that.password,_that.displayName,_that.role,_that.organizationId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String email,  String password, @JsonKey(name: 'display_name')  String displayName,  UserRole role, @JsonKey(name: 'organization_id')  String? organizationId)?  $default,) {final _that = this;
switch (_that) {
case _UserCreateDto() when $default != null:
return $default(_that.email,_that.password,_that.displayName,_that.role,_that.organizationId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(includeIfNull: false)
class _UserCreateDto implements UserCreateDto {
  const _UserCreateDto({required this.email, required this.password, @JsonKey(name: 'display_name') required this.displayName, required this.role, @JsonKey(name: 'organization_id') this.organizationId});
  factory _UserCreateDto.fromJson(Map<String, dynamic> json) => _$UserCreateDtoFromJson(json);

@override final  String email;
@override final  String password;
@override@JsonKey(name: 'display_name') final  String displayName;
@override final  UserRole role;
@override@JsonKey(name: 'organization_id') final  String? organizationId;

/// Create a copy of UserCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserCreateDtoCopyWith<_UserCreateDto> get copyWith => __$UserCreateDtoCopyWithImpl<_UserCreateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserCreateDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserCreateDto&&(identical(other.email, email) || other.email == email)&&(identical(other.password, password) || other.password == password)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.role, role) || other.role == role)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,email,password,displayName,role,organizationId);

@override
String toString() {
  return 'UserCreateDto(email: $email, password: $password, displayName: $displayName, role: $role, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class _$UserCreateDtoCopyWith<$Res> implements $UserCreateDtoCopyWith<$Res> {
  factory _$UserCreateDtoCopyWith(_UserCreateDto value, $Res Function(_UserCreateDto) _then) = __$UserCreateDtoCopyWithImpl;
@override @useResult
$Res call({
 String email, String password,@JsonKey(name: 'display_name') String displayName, UserRole role,@JsonKey(name: 'organization_id') String? organizationId
});




}
/// @nodoc
class __$UserCreateDtoCopyWithImpl<$Res>
    implements _$UserCreateDtoCopyWith<$Res> {
  __$UserCreateDtoCopyWithImpl(this._self, this._then);

  final _UserCreateDto _self;
  final $Res Function(_UserCreateDto) _then;

/// Create a copy of UserCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? email = null,Object? password = null,Object? displayName = null,Object? role = null,Object? organizationId = freezed,}) {
  return _then(_UserCreateDto(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,password: null == password ? _self.password : password // ignore: cast_nullable_to_non_nullable
as String,displayName: null == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserUpdateDto {

@JsonKey(name: 'display_name') String? get displayName; UserRole? get role;@JsonKey(name: 'is_active') bool? get isActive;
/// Create a copy of UserUpdateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserUpdateDtoCopyWith<UserUpdateDto> get copyWith => _$UserUpdateDtoCopyWithImpl<UserUpdateDto>(this as UserUpdateDto, _$identity);

  /// Serializes this UserUpdateDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserUpdateDto&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.role, role) || other.role == role)&&(identical(other.isActive, isActive) || other.isActive == isActive));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,displayName,role,isActive);

@override
String toString() {
  return 'UserUpdateDto(displayName: $displayName, role: $role, isActive: $isActive)';
}


}

/// @nodoc
abstract mixin class $UserUpdateDtoCopyWith<$Res>  {
  factory $UserUpdateDtoCopyWith(UserUpdateDto value, $Res Function(UserUpdateDto) _then) = _$UserUpdateDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'display_name') String? displayName, UserRole? role,@JsonKey(name: 'is_active') bool? isActive
});




}
/// @nodoc
class _$UserUpdateDtoCopyWithImpl<$Res>
    implements $UserUpdateDtoCopyWith<$Res> {
  _$UserUpdateDtoCopyWithImpl(this._self, this._then);

  final UserUpdateDto _self;
  final $Res Function(UserUpdateDto) _then;

/// Create a copy of UserUpdateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? displayName = freezed,Object? role = freezed,Object? isActive = freezed,}) {
  return _then(_self.copyWith(
displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,role: freezed == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserUpdateDto].
extension UserUpdateDtoPatterns on UserUpdateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserUpdateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserUpdateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserUpdateDto value)  $default,){
final _that = this;
switch (_that) {
case _UserUpdateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserUpdateDto value)?  $default,){
final _that = this;
switch (_that) {
case _UserUpdateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'display_name')  String? displayName,  UserRole? role, @JsonKey(name: 'is_active')  bool? isActive)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserUpdateDto() when $default != null:
return $default(_that.displayName,_that.role,_that.isActive);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'display_name')  String? displayName,  UserRole? role, @JsonKey(name: 'is_active')  bool? isActive)  $default,) {final _that = this;
switch (_that) {
case _UserUpdateDto():
return $default(_that.displayName,_that.role,_that.isActive);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'display_name')  String? displayName,  UserRole? role, @JsonKey(name: 'is_active')  bool? isActive)?  $default,) {final _that = this;
switch (_that) {
case _UserUpdateDto() when $default != null:
return $default(_that.displayName,_that.role,_that.isActive);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(includeIfNull: false)
class _UserUpdateDto implements UserUpdateDto {
  const _UserUpdateDto({@JsonKey(name: 'display_name') this.displayName, this.role, @JsonKey(name: 'is_active') this.isActive});
  factory _UserUpdateDto.fromJson(Map<String, dynamic> json) => _$UserUpdateDtoFromJson(json);

@override@JsonKey(name: 'display_name') final  String? displayName;
@override final  UserRole? role;
@override@JsonKey(name: 'is_active') final  bool? isActive;

/// Create a copy of UserUpdateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserUpdateDtoCopyWith<_UserUpdateDto> get copyWith => __$UserUpdateDtoCopyWithImpl<_UserUpdateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserUpdateDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserUpdateDto&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.role, role) || other.role == role)&&(identical(other.isActive, isActive) || other.isActive == isActive));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,displayName,role,isActive);

@override
String toString() {
  return 'UserUpdateDto(displayName: $displayName, role: $role, isActive: $isActive)';
}


}

/// @nodoc
abstract mixin class _$UserUpdateDtoCopyWith<$Res> implements $UserUpdateDtoCopyWith<$Res> {
  factory _$UserUpdateDtoCopyWith(_UserUpdateDto value, $Res Function(_UserUpdateDto) _then) = __$UserUpdateDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'display_name') String? displayName, UserRole? role,@JsonKey(name: 'is_active') bool? isActive
});




}
/// @nodoc
class __$UserUpdateDtoCopyWithImpl<$Res>
    implements _$UserUpdateDtoCopyWith<$Res> {
  __$UserUpdateDtoCopyWithImpl(this._self, this._then);

  final _UserUpdateDto _self;
  final $Res Function(_UserUpdateDto) _then;

/// Create a copy of UserUpdateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? displayName = freezed,Object? role = freezed,Object? isActive = freezed,}) {
  return _then(_UserUpdateDto(
displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,role: freezed == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}


}

// dart format on
