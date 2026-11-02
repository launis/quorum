// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$User {

@StrictOpaqueIdConverter()@JsonKey(name: 'id') String get id;@JsonKey(name: 'slug') String? get slug;// Phase 2, Step 2: Synchronize firebase_uid and deleted_at with backend User SSOT
@JsonKey(name: 'firebase_uid') String? get firebaseUid;@JsonKey(name: 'email') String get email;@JsonKey(name: 'role') UserRole get role;@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'name') String? get name;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'language') String? get language;@JsonKey(name: 'theme_mode') String? get themeMode;@JsonKey(name: 'last_login_at') DateTime? get lastLoginAt;@JsonKey(name: 'execution_count') int? get executionCount;@JsonKey(name: 'is_active') bool? get isActive;@JsonKey(name: 'created_by') String? get createdBy;@JsonKey(name: 'deleted_at') DateTime? get deletedAt;
/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserCopyWith<User> get copyWith => _$UserCopyWithImpl<User>(this as User, _$identity);

  /// Serializes this User to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'User(id: $id, slug: $slug, firebaseUid: $firebaseUid, email: $email, role: $role, organizationId: $organizationId, name: $name, createdAt: $createdAt, language: $language, themeMode: $themeMode, lastLoginAt: $lastLoginAt, executionCount: $executionCount, isActive: $isActive, createdBy: $createdBy, deletedAt: $deletedAt)';
}


}

/// @nodoc
abstract mixin class $UserCopyWith<$Res>  {
  factory $UserCopyWith(User value, $Res Function(User) _then) = _$UserCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter()@JsonKey(name: 'id') String id,@JsonKey(name: 'slug') String? slug,@JsonKey(name: 'firebase_uid') String? firebaseUid,@JsonKey(name: 'email') String email,@JsonKey(name: 'role') UserRole role,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'name') String? name,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'language') String? language,@JsonKey(name: 'theme_mode') String? themeMode,@JsonKey(name: 'last_login_at') DateTime? lastLoginAt,@JsonKey(name: 'execution_count') int? executionCount,@JsonKey(name: 'is_active') bool? isActive,@JsonKey(name: 'created_by') String? createdBy,@JsonKey(name: 'deleted_at') DateTime? deletedAt
});




}
/// @nodoc
class _$UserCopyWithImpl<$Res>
    implements $UserCopyWith<$Res> {
  _$UserCopyWithImpl(this._self, this._then);

  final User _self;
  final $Res Function(User) _then;

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = freezed,Object? firebaseUid = freezed,Object? email = null,Object? role = null,Object? organizationId = freezed,Object? name = freezed,Object? createdAt = freezed,Object? language = freezed,Object? themeMode = freezed,Object? lastLoginAt = freezed,Object? executionCount = freezed,Object? isActive = freezed,Object? createdBy = freezed,Object? deletedAt = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,firebaseUid: freezed == firebaseUid ? _self.firebaseUid : firebaseUid // ignore: cast_nullable_to_non_nullable
as String?,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,themeMode: freezed == themeMode ? _self.themeMode : themeMode // ignore: cast_nullable_to_non_nullable
as String?,lastLoginAt: freezed == lastLoginAt ? _self.lastLoginAt : lastLoginAt // ignore: cast_nullable_to_non_nullable
as DateTime?,executionCount: freezed == executionCount ? _self.executionCount : executionCount // ignore: cast_nullable_to_non_nullable
as int?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,deletedAt: freezed == deletedAt ? _self.deletedAt : deletedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}

}


/// Adds pattern-matching-related methods to [User].
extension UserPatterns on User {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _User value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _User() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _User value)  $default,){
final _that = this;
switch (_that) {
case _User():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _User value)?  $default,){
final _that = this;
switch (_that) {
case _User() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()@JsonKey(name: 'id')  String id, @JsonKey(name: 'slug')  String? slug, @JsonKey(name: 'firebase_uid')  String? firebaseUid, @JsonKey(name: 'email')  String email, @JsonKey(name: 'role')  UserRole role, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'name')  String? name, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'language')  String? language, @JsonKey(name: 'theme_mode')  String? themeMode, @JsonKey(name: 'last_login_at')  DateTime? lastLoginAt, @JsonKey(name: 'execution_count')  int? executionCount, @JsonKey(name: 'is_active')  bool? isActive, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'deleted_at')  DateTime? deletedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _User() when $default != null:
return $default(_that.id,_that.slug,_that.firebaseUid,_that.email,_that.role,_that.organizationId,_that.name,_that.createdAt,_that.language,_that.themeMode,_that.lastLoginAt,_that.executionCount,_that.isActive,_that.createdBy,_that.deletedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()@JsonKey(name: 'id')  String id, @JsonKey(name: 'slug')  String? slug, @JsonKey(name: 'firebase_uid')  String? firebaseUid, @JsonKey(name: 'email')  String email, @JsonKey(name: 'role')  UserRole role, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'name')  String? name, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'language')  String? language, @JsonKey(name: 'theme_mode')  String? themeMode, @JsonKey(name: 'last_login_at')  DateTime? lastLoginAt, @JsonKey(name: 'execution_count')  int? executionCount, @JsonKey(name: 'is_active')  bool? isActive, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'deleted_at')  DateTime? deletedAt)  $default,) {final _that = this;
switch (_that) {
case _User():
return $default(_that.id,_that.slug,_that.firebaseUid,_that.email,_that.role,_that.organizationId,_that.name,_that.createdAt,_that.language,_that.themeMode,_that.lastLoginAt,_that.executionCount,_that.isActive,_that.createdBy,_that.deletedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()@JsonKey(name: 'id')  String id, @JsonKey(name: 'slug')  String? slug, @JsonKey(name: 'firebase_uid')  String? firebaseUid, @JsonKey(name: 'email')  String email, @JsonKey(name: 'role')  UserRole role, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'name')  String? name, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'language')  String? language, @JsonKey(name: 'theme_mode')  String? themeMode, @JsonKey(name: 'last_login_at')  DateTime? lastLoginAt, @JsonKey(name: 'execution_count')  int? executionCount, @JsonKey(name: 'is_active')  bool? isActive, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'deleted_at')  DateTime? deletedAt)?  $default,) {final _that = this;
switch (_that) {
case _User() when $default != null:
return $default(_that.id,_that.slug,_that.firebaseUid,_that.email,_that.role,_that.organizationId,_that.name,_that.createdAt,_that.language,_that.themeMode,_that.lastLoginAt,_that.executionCount,_that.isActive,_that.createdBy,_that.deletedAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _User extends User {
  const _User({@StrictOpaqueIdConverter()@JsonKey(name: 'id') required this.id, @JsonKey(name: 'slug') this.slug, @JsonKey(name: 'firebase_uid') this.firebaseUid, @JsonKey(name: 'email') required this.email, @JsonKey(name: 'role') required this.role, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'name') this.name, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'language') this.language, @JsonKey(name: 'theme_mode') this.themeMode, @JsonKey(name: 'last_login_at') this.lastLoginAt, @JsonKey(name: 'execution_count') this.executionCount, @JsonKey(name: 'is_active') this.isActive, @JsonKey(name: 'created_by') this.createdBy, @JsonKey(name: 'deleted_at') this.deletedAt}): super._();
  factory _User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

@override@StrictOpaqueIdConverter()@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'slug') final  String? slug;
// Phase 2, Step 2: Synchronize firebase_uid and deleted_at with backend User SSOT
@override@JsonKey(name: 'firebase_uid') final  String? firebaseUid;
@override@JsonKey(name: 'email') final  String email;
@override@JsonKey(name: 'role') final  UserRole role;
@override@JsonKey(name: 'organization_id') final  String? organizationId;
@override@JsonKey(name: 'name') final  String? name;
@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'language') final  String? language;
@override@JsonKey(name: 'theme_mode') final  String? themeMode;
@override@JsonKey(name: 'last_login_at') final  DateTime? lastLoginAt;
@override@JsonKey(name: 'execution_count') final  int? executionCount;
@override@JsonKey(name: 'is_active') final  bool? isActive;
@override@JsonKey(name: 'created_by') final  String? createdBy;
@override@JsonKey(name: 'deleted_at') final  DateTime? deletedAt;

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserCopyWith<_User> get copyWith => __$UserCopyWithImpl<_User>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserToJson(this, );
}



@override
String toString() {
  return 'User(id: $id, slug: $slug, firebaseUid: $firebaseUid, email: $email, role: $role, organizationId: $organizationId, name: $name, createdAt: $createdAt, language: $language, themeMode: $themeMode, lastLoginAt: $lastLoginAt, executionCount: $executionCount, isActive: $isActive, createdBy: $createdBy, deletedAt: $deletedAt)';
}


}

/// @nodoc
abstract mixin class _$UserCopyWith<$Res> implements $UserCopyWith<$Res> {
  factory _$UserCopyWith(_User value, $Res Function(_User) _then) = __$UserCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter()@JsonKey(name: 'id') String id,@JsonKey(name: 'slug') String? slug,@JsonKey(name: 'firebase_uid') String? firebaseUid,@JsonKey(name: 'email') String email,@JsonKey(name: 'role') UserRole role,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'name') String? name,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'language') String? language,@JsonKey(name: 'theme_mode') String? themeMode,@JsonKey(name: 'last_login_at') DateTime? lastLoginAt,@JsonKey(name: 'execution_count') int? executionCount,@JsonKey(name: 'is_active') bool? isActive,@JsonKey(name: 'created_by') String? createdBy,@JsonKey(name: 'deleted_at') DateTime? deletedAt
});




}
/// @nodoc
class __$UserCopyWithImpl<$Res>
    implements _$UserCopyWith<$Res> {
  __$UserCopyWithImpl(this._self, this._then);

  final _User _self;
  final $Res Function(_User) _then;

/// Create a copy of User
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = freezed,Object? firebaseUid = freezed,Object? email = null,Object? role = null,Object? organizationId = freezed,Object? name = freezed,Object? createdAt = freezed,Object? language = freezed,Object? themeMode = freezed,Object? lastLoginAt = freezed,Object? executionCount = freezed,Object? isActive = freezed,Object? createdBy = freezed,Object? deletedAt = freezed,}) {
  return _then(_User(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,firebaseUid: freezed == firebaseUid ? _self.firebaseUid : firebaseUid // ignore: cast_nullable_to_non_nullable
as String?,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,themeMode: freezed == themeMode ? _self.themeMode : themeMode // ignore: cast_nullable_to_non_nullable
as String?,lastLoginAt: freezed == lastLoginAt ? _self.lastLoginAt : lastLoginAt // ignore: cast_nullable_to_non_nullable
as DateTime?,executionCount: freezed == executionCount ? _self.executionCount : executionCount // ignore: cast_nullable_to_non_nullable
as int?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,deletedAt: freezed == deletedAt ? _self.deletedAt : deletedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}


}


/// @nodoc
mixin _$TokenExchangeRequestDto {

@JsonKey(name: 'firebase_token', includeIfNull: false) String? get firebaseToken;@JsonKey(name: 'target_user_id', includeIfNull: false) String? get targetUserId;@JsonKey(name: 'service_auth_secret', includeIfNull: false) String? get serviceAuthSecret;
/// Create a copy of TokenExchangeRequestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TokenExchangeRequestDtoCopyWith<TokenExchangeRequestDto> get copyWith => _$TokenExchangeRequestDtoCopyWithImpl<TokenExchangeRequestDto>(this as TokenExchangeRequestDto, _$identity);

  /// Serializes this TokenExchangeRequestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TokenExchangeRequestDto(firebaseToken: $firebaseToken, targetUserId: $targetUserId, serviceAuthSecret: $serviceAuthSecret)';
}


}

/// @nodoc
abstract mixin class $TokenExchangeRequestDtoCopyWith<$Res>  {
  factory $TokenExchangeRequestDtoCopyWith(TokenExchangeRequestDto value, $Res Function(TokenExchangeRequestDto) _then) = _$TokenExchangeRequestDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'firebase_token', includeIfNull: false) String? firebaseToken,@JsonKey(name: 'target_user_id', includeIfNull: false) String? targetUserId,@JsonKey(name: 'service_auth_secret', includeIfNull: false) String? serviceAuthSecret
});




}
/// @nodoc
class _$TokenExchangeRequestDtoCopyWithImpl<$Res>
    implements $TokenExchangeRequestDtoCopyWith<$Res> {
  _$TokenExchangeRequestDtoCopyWithImpl(this._self, this._then);

  final TokenExchangeRequestDto _self;
  final $Res Function(TokenExchangeRequestDto) _then;

/// Create a copy of TokenExchangeRequestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? firebaseToken = freezed,Object? targetUserId = freezed,Object? serviceAuthSecret = freezed,}) {
  return _then(_self.copyWith(
firebaseToken: freezed == firebaseToken ? _self.firebaseToken : firebaseToken // ignore: cast_nullable_to_non_nullable
as String?,targetUserId: freezed == targetUserId ? _self.targetUserId : targetUserId // ignore: cast_nullable_to_non_nullable
as String?,serviceAuthSecret: freezed == serviceAuthSecret ? _self.serviceAuthSecret : serviceAuthSecret // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [TokenExchangeRequestDto].
extension TokenExchangeRequestDtoPatterns on TokenExchangeRequestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TokenExchangeRequestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TokenExchangeRequestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TokenExchangeRequestDto value)  $default,){
final _that = this;
switch (_that) {
case _TokenExchangeRequestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TokenExchangeRequestDto value)?  $default,){
final _that = this;
switch (_that) {
case _TokenExchangeRequestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'firebase_token', includeIfNull: false)  String? firebaseToken, @JsonKey(name: 'target_user_id', includeIfNull: false)  String? targetUserId, @JsonKey(name: 'service_auth_secret', includeIfNull: false)  String? serviceAuthSecret)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TokenExchangeRequestDto() when $default != null:
return $default(_that.firebaseToken,_that.targetUserId,_that.serviceAuthSecret);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'firebase_token', includeIfNull: false)  String? firebaseToken, @JsonKey(name: 'target_user_id', includeIfNull: false)  String? targetUserId, @JsonKey(name: 'service_auth_secret', includeIfNull: false)  String? serviceAuthSecret)  $default,) {final _that = this;
switch (_that) {
case _TokenExchangeRequestDto():
return $default(_that.firebaseToken,_that.targetUserId,_that.serviceAuthSecret);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'firebase_token', includeIfNull: false)  String? firebaseToken, @JsonKey(name: 'target_user_id', includeIfNull: false)  String? targetUserId, @JsonKey(name: 'service_auth_secret', includeIfNull: false)  String? serviceAuthSecret)?  $default,) {final _that = this;
switch (_that) {
case _TokenExchangeRequestDto() when $default != null:
return $default(_that.firebaseToken,_that.targetUserId,_that.serviceAuthSecret);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _TokenExchangeRequestDto extends TokenExchangeRequestDto {
  const _TokenExchangeRequestDto({@JsonKey(name: 'firebase_token', includeIfNull: false) this.firebaseToken, @JsonKey(name: 'target_user_id', includeIfNull: false) this.targetUserId, @JsonKey(name: 'service_auth_secret', includeIfNull: false) this.serviceAuthSecret}): super._();
  factory _TokenExchangeRequestDto.fromJson(Map<String, dynamic> json) => _$TokenExchangeRequestDtoFromJson(json);

@override@JsonKey(name: 'firebase_token', includeIfNull: false) final  String? firebaseToken;
@override@JsonKey(name: 'target_user_id', includeIfNull: false) final  String? targetUserId;
@override@JsonKey(name: 'service_auth_secret', includeIfNull: false) final  String? serviceAuthSecret;

/// Create a copy of TokenExchangeRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TokenExchangeRequestDtoCopyWith<_TokenExchangeRequestDto> get copyWith => __$TokenExchangeRequestDtoCopyWithImpl<_TokenExchangeRequestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TokenExchangeRequestDtoToJson(this, );
}



@override
String toString() {
  return 'TokenExchangeRequestDto(firebaseToken: $firebaseToken, targetUserId: $targetUserId, serviceAuthSecret: $serviceAuthSecret)';
}


}

/// @nodoc
abstract mixin class _$TokenExchangeRequestDtoCopyWith<$Res> implements $TokenExchangeRequestDtoCopyWith<$Res> {
  factory _$TokenExchangeRequestDtoCopyWith(_TokenExchangeRequestDto value, $Res Function(_TokenExchangeRequestDto) _then) = __$TokenExchangeRequestDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'firebase_token', includeIfNull: false) String? firebaseToken,@JsonKey(name: 'target_user_id', includeIfNull: false) String? targetUserId,@JsonKey(name: 'service_auth_secret', includeIfNull: false) String? serviceAuthSecret
});




}
/// @nodoc
class __$TokenExchangeRequestDtoCopyWithImpl<$Res>
    implements _$TokenExchangeRequestDtoCopyWith<$Res> {
  __$TokenExchangeRequestDtoCopyWithImpl(this._self, this._then);

  final _TokenExchangeRequestDto _self;
  final $Res Function(_TokenExchangeRequestDto) _then;

/// Create a copy of TokenExchangeRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? firebaseToken = freezed,Object? targetUserId = freezed,Object? serviceAuthSecret = freezed,}) {
  return _then(_TokenExchangeRequestDto(
firebaseToken: freezed == firebaseToken ? _self.firebaseToken : firebaseToken // ignore: cast_nullable_to_non_nullable
as String?,targetUserId: freezed == targetUserId ? _self.targetUserId : targetUserId // ignore: cast_nullable_to_non_nullable
as String?,serviceAuthSecret: freezed == serviceAuthSecret ? _self.serviceAuthSecret : serviceAuthSecret // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$TokenExchangeResponseDto {

@JsonKey(name: 'access_token') String get accessToken;@JsonKey(name: 'token_type') String get tokenType;@JsonKey(name: 'expires_in_seconds') int get expiresInSeconds;@JsonKey(name: 'user') User get user;
/// Create a copy of TokenExchangeResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TokenExchangeResponseDtoCopyWith<TokenExchangeResponseDto> get copyWith => _$TokenExchangeResponseDtoCopyWithImpl<TokenExchangeResponseDto>(this as TokenExchangeResponseDto, _$identity);

  /// Serializes this TokenExchangeResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TokenExchangeResponseDto(accessToken: $accessToken, tokenType: $tokenType, expiresInSeconds: $expiresInSeconds, user: $user)';
}


}

/// @nodoc
abstract mixin class $TokenExchangeResponseDtoCopyWith<$Res>  {
  factory $TokenExchangeResponseDtoCopyWith(TokenExchangeResponseDto value, $Res Function(TokenExchangeResponseDto) _then) = _$TokenExchangeResponseDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'token_type') String tokenType,@JsonKey(name: 'expires_in_seconds') int expiresInSeconds,@JsonKey(name: 'user') User user
});


$UserCopyWith<$Res> get user;

}
/// @nodoc
class _$TokenExchangeResponseDtoCopyWithImpl<$Res>
    implements $TokenExchangeResponseDtoCopyWith<$Res> {
  _$TokenExchangeResponseDtoCopyWithImpl(this._self, this._then);

  final TokenExchangeResponseDto _self;
  final $Res Function(TokenExchangeResponseDto) _then;

/// Create a copy of TokenExchangeResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? accessToken = null,Object? tokenType = null,Object? expiresInSeconds = null,Object? user = null,}) {
  return _then(_self.copyWith(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: null == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String,expiresInSeconds: null == expiresInSeconds ? _self.expiresInSeconds : expiresInSeconds // ignore: cast_nullable_to_non_nullable
as int,user: null == user ? _self.user : user // ignore: cast_nullable_to_non_nullable
as User,
  ));
}
/// Create a copy of TokenExchangeResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$UserCopyWith<$Res> get user {
  
  return $UserCopyWith<$Res>(_self.user, (value) {
    return _then(_self.copyWith(user: value));
  });
}
}


/// Adds pattern-matching-related methods to [TokenExchangeResponseDto].
extension TokenExchangeResponseDtoPatterns on TokenExchangeResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TokenExchangeResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TokenExchangeResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TokenExchangeResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _TokenExchangeResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TokenExchangeResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _TokenExchangeResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'token_type')  String tokenType, @JsonKey(name: 'expires_in_seconds')  int expiresInSeconds, @JsonKey(name: 'user')  User user)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TokenExchangeResponseDto() when $default != null:
return $default(_that.accessToken,_that.tokenType,_that.expiresInSeconds,_that.user);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'token_type')  String tokenType, @JsonKey(name: 'expires_in_seconds')  int expiresInSeconds, @JsonKey(name: 'user')  User user)  $default,) {final _that = this;
switch (_that) {
case _TokenExchangeResponseDto():
return $default(_that.accessToken,_that.tokenType,_that.expiresInSeconds,_that.user);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'token_type')  String tokenType, @JsonKey(name: 'expires_in_seconds')  int expiresInSeconds, @JsonKey(name: 'user')  User user)?  $default,) {final _that = this;
switch (_that) {
case _TokenExchangeResponseDto() when $default != null:
return $default(_that.accessToken,_that.tokenType,_that.expiresInSeconds,_that.user);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _TokenExchangeResponseDto extends TokenExchangeResponseDto {
  const _TokenExchangeResponseDto({@JsonKey(name: 'access_token') required this.accessToken, @JsonKey(name: 'token_type') this.tokenType = 'bearer', @JsonKey(name: 'expires_in_seconds') required this.expiresInSeconds, @JsonKey(name: 'user') required this.user}): super._();
  factory _TokenExchangeResponseDto.fromJson(Map<String, dynamic> json) => _$TokenExchangeResponseDtoFromJson(json);

@override@JsonKey(name: 'access_token') final  String accessToken;
@override@JsonKey(name: 'token_type') final  String tokenType;
@override@JsonKey(name: 'expires_in_seconds') final  int expiresInSeconds;
@override@JsonKey(name: 'user') final  User user;

/// Create a copy of TokenExchangeResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TokenExchangeResponseDtoCopyWith<_TokenExchangeResponseDto> get copyWith => __$TokenExchangeResponseDtoCopyWithImpl<_TokenExchangeResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TokenExchangeResponseDtoToJson(this, );
}



@override
String toString() {
  return 'TokenExchangeResponseDto(accessToken: $accessToken, tokenType: $tokenType, expiresInSeconds: $expiresInSeconds, user: $user)';
}


}

/// @nodoc
abstract mixin class _$TokenExchangeResponseDtoCopyWith<$Res> implements $TokenExchangeResponseDtoCopyWith<$Res> {
  factory _$TokenExchangeResponseDtoCopyWith(_TokenExchangeResponseDto value, $Res Function(_TokenExchangeResponseDto) _then) = __$TokenExchangeResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'token_type') String tokenType,@JsonKey(name: 'expires_in_seconds') int expiresInSeconds,@JsonKey(name: 'user') User user
});


@override $UserCopyWith<$Res> get user;

}
/// @nodoc
class __$TokenExchangeResponseDtoCopyWithImpl<$Res>
    implements _$TokenExchangeResponseDtoCopyWith<$Res> {
  __$TokenExchangeResponseDtoCopyWithImpl(this._self, this._then);

  final _TokenExchangeResponseDto _self;
  final $Res Function(_TokenExchangeResponseDto) _then;

/// Create a copy of TokenExchangeResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? accessToken = null,Object? tokenType = null,Object? expiresInSeconds = null,Object? user = null,}) {
  return _then(_TokenExchangeResponseDto(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: null == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String,expiresInSeconds: null == expiresInSeconds ? _self.expiresInSeconds : expiresInSeconds // ignore: cast_nullable_to_non_nullable
as int,user: null == user ? _self.user : user // ignore: cast_nullable_to_non_nullable
as User,
  ));
}

/// Create a copy of TokenExchangeResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$UserCopyWith<$Res> get user {
  
  return $UserCopyWith<$Res>(_self.user, (value) {
    return _then(_self.copyWith(user: value));
  });
}
}


/// @nodoc
mixin _$LogoutRequestDto {

@JsonKey(name: 'revoke_all_sessions') bool get revokeAllSessions;
/// Create a copy of LogoutRequestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LogoutRequestDtoCopyWith<LogoutRequestDto> get copyWith => _$LogoutRequestDtoCopyWithImpl<LogoutRequestDto>(this as LogoutRequestDto, _$identity);

  /// Serializes this LogoutRequestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'LogoutRequestDto(revokeAllSessions: $revokeAllSessions)';
}


}

/// @nodoc
abstract mixin class $LogoutRequestDtoCopyWith<$Res>  {
  factory $LogoutRequestDtoCopyWith(LogoutRequestDto value, $Res Function(LogoutRequestDto) _then) = _$LogoutRequestDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'revoke_all_sessions') bool revokeAllSessions
});




}
/// @nodoc
class _$LogoutRequestDtoCopyWithImpl<$Res>
    implements $LogoutRequestDtoCopyWith<$Res> {
  _$LogoutRequestDtoCopyWithImpl(this._self, this._then);

  final LogoutRequestDto _self;
  final $Res Function(LogoutRequestDto) _then;

/// Create a copy of LogoutRequestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? revokeAllSessions = null,}) {
  return _then(_self.copyWith(
revokeAllSessions: null == revokeAllSessions ? _self.revokeAllSessions : revokeAllSessions // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [LogoutRequestDto].
extension LogoutRequestDtoPatterns on LogoutRequestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LogoutRequestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LogoutRequestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LogoutRequestDto value)  $default,){
final _that = this;
switch (_that) {
case _LogoutRequestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LogoutRequestDto value)?  $default,){
final _that = this;
switch (_that) {
case _LogoutRequestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'revoke_all_sessions')  bool revokeAllSessions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LogoutRequestDto() when $default != null:
return $default(_that.revokeAllSessions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'revoke_all_sessions')  bool revokeAllSessions)  $default,) {final _that = this;
switch (_that) {
case _LogoutRequestDto():
return $default(_that.revokeAllSessions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'revoke_all_sessions')  bool revokeAllSessions)?  $default,) {final _that = this;
switch (_that) {
case _LogoutRequestDto() when $default != null:
return $default(_that.revokeAllSessions);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _LogoutRequestDto extends LogoutRequestDto {
  const _LogoutRequestDto({@JsonKey(name: 'revoke_all_sessions') this.revokeAllSessions = false}): super._();
  factory _LogoutRequestDto.fromJson(Map<String, dynamic> json) => _$LogoutRequestDtoFromJson(json);

@override@JsonKey(name: 'revoke_all_sessions') final  bool revokeAllSessions;

/// Create a copy of LogoutRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LogoutRequestDtoCopyWith<_LogoutRequestDto> get copyWith => __$LogoutRequestDtoCopyWithImpl<_LogoutRequestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LogoutRequestDtoToJson(this, );
}



@override
String toString() {
  return 'LogoutRequestDto(revokeAllSessions: $revokeAllSessions)';
}


}

/// @nodoc
abstract mixin class _$LogoutRequestDtoCopyWith<$Res> implements $LogoutRequestDtoCopyWith<$Res> {
  factory _$LogoutRequestDtoCopyWith(_LogoutRequestDto value, $Res Function(_LogoutRequestDto) _then) = __$LogoutRequestDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'revoke_all_sessions') bool revokeAllSessions
});




}
/// @nodoc
class __$LogoutRequestDtoCopyWithImpl<$Res>
    implements _$LogoutRequestDtoCopyWith<$Res> {
  __$LogoutRequestDtoCopyWithImpl(this._self, this._then);

  final _LogoutRequestDto _self;
  final $Res Function(_LogoutRequestDto) _then;

/// Create a copy of LogoutRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? revokeAllSessions = null,}) {
  return _then(_LogoutRequestDto(
revokeAllSessions: null == revokeAllSessions ? _self.revokeAllSessions : revokeAllSessions // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$LogoutResponseDto {

// Phase 2, Step 2: Synchronize default logout status with backend LogoutResponseDTO
@JsonKey(name: 'status') String get status;@JsonKey(name: 'revoked_jti') String get revokedJti;@JsonKey(name: 'all_sessions_revoked') bool get allSessionsRevoked;
/// Create a copy of LogoutResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LogoutResponseDtoCopyWith<LogoutResponseDto> get copyWith => _$LogoutResponseDtoCopyWithImpl<LogoutResponseDto>(this as LogoutResponseDto, _$identity);

  /// Serializes this LogoutResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'LogoutResponseDto(status: $status, revokedJti: $revokedJti, allSessionsRevoked: $allSessionsRevoked)';
}


}

/// @nodoc
abstract mixin class $LogoutResponseDtoCopyWith<$Res>  {
  factory $LogoutResponseDtoCopyWith(LogoutResponseDto value, $Res Function(LogoutResponseDto) _then) = _$LogoutResponseDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'status') String status,@JsonKey(name: 'revoked_jti') String revokedJti,@JsonKey(name: 'all_sessions_revoked') bool allSessionsRevoked
});




}
/// @nodoc
class _$LogoutResponseDtoCopyWithImpl<$Res>
    implements $LogoutResponseDtoCopyWith<$Res> {
  _$LogoutResponseDtoCopyWithImpl(this._self, this._then);

  final LogoutResponseDto _self;
  final $Res Function(LogoutResponseDto) _then;

/// Create a copy of LogoutResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? status = null,Object? revokedJti = null,Object? allSessionsRevoked = null,}) {
  return _then(_self.copyWith(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,revokedJti: null == revokedJti ? _self.revokedJti : revokedJti // ignore: cast_nullable_to_non_nullable
as String,allSessionsRevoked: null == allSessionsRevoked ? _self.allSessionsRevoked : allSessionsRevoked // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [LogoutResponseDto].
extension LogoutResponseDtoPatterns on LogoutResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LogoutResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LogoutResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LogoutResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _LogoutResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LogoutResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _LogoutResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'status')  String status, @JsonKey(name: 'revoked_jti')  String revokedJti, @JsonKey(name: 'all_sessions_revoked')  bool allSessionsRevoked)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LogoutResponseDto() when $default != null:
return $default(_that.status,_that.revokedJti,_that.allSessionsRevoked);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'status')  String status, @JsonKey(name: 'revoked_jti')  String revokedJti, @JsonKey(name: 'all_sessions_revoked')  bool allSessionsRevoked)  $default,) {final _that = this;
switch (_that) {
case _LogoutResponseDto():
return $default(_that.status,_that.revokedJti,_that.allSessionsRevoked);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'status')  String status, @JsonKey(name: 'revoked_jti')  String revokedJti, @JsonKey(name: 'all_sessions_revoked')  bool allSessionsRevoked)?  $default,) {final _that = this;
switch (_that) {
case _LogoutResponseDto() when $default != null:
return $default(_that.status,_that.revokedJti,_that.allSessionsRevoked);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _LogoutResponseDto extends LogoutResponseDto {
  const _LogoutResponseDto({@JsonKey(name: 'status') this.status = 'logged_out', @JsonKey(name: 'revoked_jti') required this.revokedJti, @JsonKey(name: 'all_sessions_revoked') required this.allSessionsRevoked}): super._();
  factory _LogoutResponseDto.fromJson(Map<String, dynamic> json) => _$LogoutResponseDtoFromJson(json);

// Phase 2, Step 2: Synchronize default logout status with backend LogoutResponseDTO
@override@JsonKey(name: 'status') final  String status;
@override@JsonKey(name: 'revoked_jti') final  String revokedJti;
@override@JsonKey(name: 'all_sessions_revoked') final  bool allSessionsRevoked;

/// Create a copy of LogoutResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LogoutResponseDtoCopyWith<_LogoutResponseDto> get copyWith => __$LogoutResponseDtoCopyWithImpl<_LogoutResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LogoutResponseDtoToJson(this, );
}



@override
String toString() {
  return 'LogoutResponseDto(status: $status, revokedJti: $revokedJti, allSessionsRevoked: $allSessionsRevoked)';
}


}

/// @nodoc
abstract mixin class _$LogoutResponseDtoCopyWith<$Res> implements $LogoutResponseDtoCopyWith<$Res> {
  factory _$LogoutResponseDtoCopyWith(_LogoutResponseDto value, $Res Function(_LogoutResponseDto) _then) = __$LogoutResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'status') String status,@JsonKey(name: 'revoked_jti') String revokedJti,@JsonKey(name: 'all_sessions_revoked') bool allSessionsRevoked
});




}
/// @nodoc
class __$LogoutResponseDtoCopyWithImpl<$Res>
    implements _$LogoutResponseDtoCopyWith<$Res> {
  __$LogoutResponseDtoCopyWithImpl(this._self, this._then);

  final _LogoutResponseDto _self;
  final $Res Function(_LogoutResponseDto) _then;

/// Create a copy of LogoutResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? status = null,Object? revokedJti = null,Object? allSessionsRevoked = null,}) {
  return _then(_LogoutResponseDto(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,revokedJti: null == revokedJti ? _self.revokedJti : revokedJti // ignore: cast_nullable_to_non_nullable
as String,allSessionsRevoked: null == allSessionsRevoked ? _self.allSessionsRevoked : allSessionsRevoked // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$UserCreate {

@JsonKey(name: 'email') String get email;@JsonKey(name: 'name', includeIfNull: false) String? get name;@JsonKey(name: 'role') UserRole get role;@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String get organizationId;@JsonKey(name: 'is_active') bool get isActive;@JsonKey(name: 'language', includeIfNull: false) String? get language;@JsonKey(name: 'theme_mode', includeIfNull: false) String? get themeMode;@JsonKey(name: 'created_by', includeIfNull: false) String? get createdBy;@JsonKey(name: 'password', includeIfNull: false) String? get password;
/// Create a copy of UserCreate
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserCreateCopyWith<UserCreate> get copyWith => _$UserCreateCopyWithImpl<UserCreate>(this as UserCreate, _$identity);

  /// Serializes this UserCreate to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'UserCreate(email: $email, name: $name, role: $role, organizationId: $organizationId, isActive: $isActive, language: $language, themeMode: $themeMode, createdBy: $createdBy, password: $password)';
}


}

/// @nodoc
abstract mixin class $UserCreateCopyWith<$Res>  {
  factory $UserCreateCopyWith(UserCreate value, $Res Function(UserCreate) _then) = _$UserCreateCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'email') String email,@JsonKey(name: 'name', includeIfNull: false) String? name,@JsonKey(name: 'role') UserRole role,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'language', includeIfNull: false) String? language,@JsonKey(name: 'theme_mode', includeIfNull: false) String? themeMode,@JsonKey(name: 'created_by', includeIfNull: false) String? createdBy,@JsonKey(name: 'password', includeIfNull: false) String? password
});




}
/// @nodoc
class _$UserCreateCopyWithImpl<$Res>
    implements $UserCreateCopyWith<$Res> {
  _$UserCreateCopyWithImpl(this._self, this._then);

  final UserCreate _self;
  final $Res Function(UserCreate) _then;

/// Create a copy of UserCreate
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? email = null,Object? name = freezed,Object? role = null,Object? organizationId = null,Object? isActive = null,Object? language = freezed,Object? themeMode = freezed,Object? createdBy = freezed,Object? password = freezed,}) {
  return _then(_self.copyWith(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,themeMode: freezed == themeMode ? _self.themeMode : themeMode // ignore: cast_nullable_to_non_nullable
as String?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,password: freezed == password ? _self.password : password // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserCreate].
extension UserCreatePatterns on UserCreate {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserCreate value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserCreate() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserCreate value)  $default,){
final _that = this;
switch (_that) {
case _UserCreate():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserCreate value)?  $default,){
final _that = this;
switch (_that) {
case _UserCreate() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'email')  String email, @JsonKey(name: 'name', includeIfNull: false)  String? name, @JsonKey(name: 'role')  UserRole role, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'language', includeIfNull: false)  String? language, @JsonKey(name: 'theme_mode', includeIfNull: false)  String? themeMode, @JsonKey(name: 'created_by', includeIfNull: false)  String? createdBy, @JsonKey(name: 'password', includeIfNull: false)  String? password)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserCreate() when $default != null:
return $default(_that.email,_that.name,_that.role,_that.organizationId,_that.isActive,_that.language,_that.themeMode,_that.createdBy,_that.password);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'email')  String email, @JsonKey(name: 'name', includeIfNull: false)  String? name, @JsonKey(name: 'role')  UserRole role, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'language', includeIfNull: false)  String? language, @JsonKey(name: 'theme_mode', includeIfNull: false)  String? themeMode, @JsonKey(name: 'created_by', includeIfNull: false)  String? createdBy, @JsonKey(name: 'password', includeIfNull: false)  String? password)  $default,) {final _that = this;
switch (_that) {
case _UserCreate():
return $default(_that.email,_that.name,_that.role,_that.organizationId,_that.isActive,_that.language,_that.themeMode,_that.createdBy,_that.password);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'email')  String email, @JsonKey(name: 'name', includeIfNull: false)  String? name, @JsonKey(name: 'role')  UserRole role, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'language', includeIfNull: false)  String? language, @JsonKey(name: 'theme_mode', includeIfNull: false)  String? themeMode, @JsonKey(name: 'created_by', includeIfNull: false)  String? createdBy, @JsonKey(name: 'password', includeIfNull: false)  String? password)?  $default,) {final _that = this;
switch (_that) {
case _UserCreate() when $default != null:
return $default(_that.email,_that.name,_that.role,_that.organizationId,_that.isActive,_that.language,_that.themeMode,_that.createdBy,_that.password);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _UserCreate extends UserCreate {
  const _UserCreate({@JsonKey(name: 'email') required this.email, @JsonKey(name: 'name', includeIfNull: false) this.name, @JsonKey(name: 'role') this.role = UserRole.member, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') required this.organizationId, @JsonKey(name: 'is_active') this.isActive = true, @JsonKey(name: 'language', includeIfNull: false) this.language, @JsonKey(name: 'theme_mode', includeIfNull: false) this.themeMode, @JsonKey(name: 'created_by', includeIfNull: false) this.createdBy, @JsonKey(name: 'password', includeIfNull: false) this.password}): super._();
  factory _UserCreate.fromJson(Map<String, dynamic> json) => _$UserCreateFromJson(json);

@override@JsonKey(name: 'email') final  String email;
@override@JsonKey(name: 'name', includeIfNull: false) final  String? name;
@override@JsonKey(name: 'role') final  UserRole role;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') final  String organizationId;
@override@JsonKey(name: 'is_active') final  bool isActive;
@override@JsonKey(name: 'language', includeIfNull: false) final  String? language;
@override@JsonKey(name: 'theme_mode', includeIfNull: false) final  String? themeMode;
@override@JsonKey(name: 'created_by', includeIfNull: false) final  String? createdBy;
@override@JsonKey(name: 'password', includeIfNull: false) final  String? password;

/// Create a copy of UserCreate
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserCreateCopyWith<_UserCreate> get copyWith => __$UserCreateCopyWithImpl<_UserCreate>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserCreateToJson(this, );
}



@override
String toString() {
  return 'UserCreate(email: $email, name: $name, role: $role, organizationId: $organizationId, isActive: $isActive, language: $language, themeMode: $themeMode, createdBy: $createdBy, password: $password)';
}


}

/// @nodoc
abstract mixin class _$UserCreateCopyWith<$Res> implements $UserCreateCopyWith<$Res> {
  factory _$UserCreateCopyWith(_UserCreate value, $Res Function(_UserCreate) _then) = __$UserCreateCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'email') String email,@JsonKey(name: 'name', includeIfNull: false) String? name,@JsonKey(name: 'role') UserRole role,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'language', includeIfNull: false) String? language,@JsonKey(name: 'theme_mode', includeIfNull: false) String? themeMode,@JsonKey(name: 'created_by', includeIfNull: false) String? createdBy,@JsonKey(name: 'password', includeIfNull: false) String? password
});




}
/// @nodoc
class __$UserCreateCopyWithImpl<$Res>
    implements _$UserCreateCopyWith<$Res> {
  __$UserCreateCopyWithImpl(this._self, this._then);

  final _UserCreate _self;
  final $Res Function(_UserCreate) _then;

/// Create a copy of UserCreate
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? email = null,Object? name = freezed,Object? role = null,Object? organizationId = null,Object? isActive = null,Object? language = freezed,Object? themeMode = freezed,Object? createdBy = freezed,Object? password = freezed,}) {
  return _then(_UserCreate(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,themeMode: freezed == themeMode ? _self.themeMode : themeMode // ignore: cast_nullable_to_non_nullable
as String?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,password: freezed == password ? _self.password : password // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserUpdate {

@JsonKey(name: 'name', includeIfNull: false) String? get name;@JsonKey(name: 'role', includeIfNull: false) UserRole? get role;@JsonKey(name: 'organization_id', includeIfNull: false) String? get organizationId;@JsonKey(name: 'is_active', includeIfNull: false) bool? get isActive;@JsonKey(name: 'language', includeIfNull: false) String? get language;@JsonKey(name: 'theme_mode', includeIfNull: false) String? get themeMode;@JsonKey(name: 'password', includeIfNull: false) String? get password;
/// Create a copy of UserUpdate
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserUpdateCopyWith<UserUpdate> get copyWith => _$UserUpdateCopyWithImpl<UserUpdate>(this as UserUpdate, _$identity);

  /// Serializes this UserUpdate to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'UserUpdate(name: $name, role: $role, organizationId: $organizationId, isActive: $isActive, language: $language, themeMode: $themeMode, password: $password)';
}


}

/// @nodoc
abstract mixin class $UserUpdateCopyWith<$Res>  {
  factory $UserUpdateCopyWith(UserUpdate value, $Res Function(UserUpdate) _then) = _$UserUpdateCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'name', includeIfNull: false) String? name,@JsonKey(name: 'role', includeIfNull: false) UserRole? role,@JsonKey(name: 'organization_id', includeIfNull: false) String? organizationId,@JsonKey(name: 'is_active', includeIfNull: false) bool? isActive,@JsonKey(name: 'language', includeIfNull: false) String? language,@JsonKey(name: 'theme_mode', includeIfNull: false) String? themeMode,@JsonKey(name: 'password', includeIfNull: false) String? password
});




}
/// @nodoc
class _$UserUpdateCopyWithImpl<$Res>
    implements $UserUpdateCopyWith<$Res> {
  _$UserUpdateCopyWithImpl(this._self, this._then);

  final UserUpdate _self;
  final $Res Function(UserUpdate) _then;

/// Create a copy of UserUpdate
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = freezed,Object? role = freezed,Object? organizationId = freezed,Object? isActive = freezed,Object? language = freezed,Object? themeMode = freezed,Object? password = freezed,}) {
  return _then(_self.copyWith(
name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,role: freezed == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,themeMode: freezed == themeMode ? _self.themeMode : themeMode // ignore: cast_nullable_to_non_nullable
as String?,password: freezed == password ? _self.password : password // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserUpdate].
extension UserUpdatePatterns on UserUpdate {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserUpdate value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserUpdate() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserUpdate value)  $default,){
final _that = this;
switch (_that) {
case _UserUpdate():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserUpdate value)?  $default,){
final _that = this;
switch (_that) {
case _UserUpdate() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'name', includeIfNull: false)  String? name, @JsonKey(name: 'role', includeIfNull: false)  UserRole? role, @JsonKey(name: 'organization_id', includeIfNull: false)  String? organizationId, @JsonKey(name: 'is_active', includeIfNull: false)  bool? isActive, @JsonKey(name: 'language', includeIfNull: false)  String? language, @JsonKey(name: 'theme_mode', includeIfNull: false)  String? themeMode, @JsonKey(name: 'password', includeIfNull: false)  String? password)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserUpdate() when $default != null:
return $default(_that.name,_that.role,_that.organizationId,_that.isActive,_that.language,_that.themeMode,_that.password);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'name', includeIfNull: false)  String? name, @JsonKey(name: 'role', includeIfNull: false)  UserRole? role, @JsonKey(name: 'organization_id', includeIfNull: false)  String? organizationId, @JsonKey(name: 'is_active', includeIfNull: false)  bool? isActive, @JsonKey(name: 'language', includeIfNull: false)  String? language, @JsonKey(name: 'theme_mode', includeIfNull: false)  String? themeMode, @JsonKey(name: 'password', includeIfNull: false)  String? password)  $default,) {final _that = this;
switch (_that) {
case _UserUpdate():
return $default(_that.name,_that.role,_that.organizationId,_that.isActive,_that.language,_that.themeMode,_that.password);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'name', includeIfNull: false)  String? name, @JsonKey(name: 'role', includeIfNull: false)  UserRole? role, @JsonKey(name: 'organization_id', includeIfNull: false)  String? organizationId, @JsonKey(name: 'is_active', includeIfNull: false)  bool? isActive, @JsonKey(name: 'language', includeIfNull: false)  String? language, @JsonKey(name: 'theme_mode', includeIfNull: false)  String? themeMode, @JsonKey(name: 'password', includeIfNull: false)  String? password)?  $default,) {final _that = this;
switch (_that) {
case _UserUpdate() when $default != null:
return $default(_that.name,_that.role,_that.organizationId,_that.isActive,_that.language,_that.themeMode,_that.password);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _UserUpdate extends UserUpdate {
  const _UserUpdate({@JsonKey(name: 'name', includeIfNull: false) this.name, @JsonKey(name: 'role', includeIfNull: false) this.role, @JsonKey(name: 'organization_id', includeIfNull: false) this.organizationId, @JsonKey(name: 'is_active', includeIfNull: false) this.isActive, @JsonKey(name: 'language', includeIfNull: false) this.language, @JsonKey(name: 'theme_mode', includeIfNull: false) this.themeMode, @JsonKey(name: 'password', includeIfNull: false) this.password}): super._();
  factory _UserUpdate.fromJson(Map<String, dynamic> json) => _$UserUpdateFromJson(json);

@override@JsonKey(name: 'name', includeIfNull: false) final  String? name;
@override@JsonKey(name: 'role', includeIfNull: false) final  UserRole? role;
@override@JsonKey(name: 'organization_id', includeIfNull: false) final  String? organizationId;
@override@JsonKey(name: 'is_active', includeIfNull: false) final  bool? isActive;
@override@JsonKey(name: 'language', includeIfNull: false) final  String? language;
@override@JsonKey(name: 'theme_mode', includeIfNull: false) final  String? themeMode;
@override@JsonKey(name: 'password', includeIfNull: false) final  String? password;

/// Create a copy of UserUpdate
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserUpdateCopyWith<_UserUpdate> get copyWith => __$UserUpdateCopyWithImpl<_UserUpdate>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserUpdateToJson(this, );
}



@override
String toString() {
  return 'UserUpdate(name: $name, role: $role, organizationId: $organizationId, isActive: $isActive, language: $language, themeMode: $themeMode, password: $password)';
}


}

/// @nodoc
abstract mixin class _$UserUpdateCopyWith<$Res> implements $UserUpdateCopyWith<$Res> {
  factory _$UserUpdateCopyWith(_UserUpdate value, $Res Function(_UserUpdate) _then) = __$UserUpdateCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'name', includeIfNull: false) String? name,@JsonKey(name: 'role', includeIfNull: false) UserRole? role,@JsonKey(name: 'organization_id', includeIfNull: false) String? organizationId,@JsonKey(name: 'is_active', includeIfNull: false) bool? isActive,@JsonKey(name: 'language', includeIfNull: false) String? language,@JsonKey(name: 'theme_mode', includeIfNull: false) String? themeMode,@JsonKey(name: 'password', includeIfNull: false) String? password
});




}
/// @nodoc
class __$UserUpdateCopyWithImpl<$Res>
    implements _$UserUpdateCopyWith<$Res> {
  __$UserUpdateCopyWithImpl(this._self, this._then);

  final _UserUpdate _self;
  final $Res Function(_UserUpdate) _then;

/// Create a copy of UserUpdate
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = freezed,Object? role = freezed,Object? organizationId = freezed,Object? isActive = freezed,Object? language = freezed,Object? themeMode = freezed,Object? password = freezed,}) {
  return _then(_UserUpdate(
name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,role: freezed == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,themeMode: freezed == themeMode ? _self.themeMode : themeMode // ignore: cast_nullable_to_non_nullable
as String?,password: freezed == password ? _self.password : password // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
