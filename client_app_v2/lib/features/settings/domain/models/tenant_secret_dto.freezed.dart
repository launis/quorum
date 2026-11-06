// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'tenant_secret_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Organization {

@StrictOpaqueIdConverter() String get id; String? get slug; String get name;@JsonKey(name: 'created_at') DateTime? get createdAt;@JsonKey(name: 'is_active') bool get isActive; String get tier;@JsonKey(name: 'contact_email') String? get contactEmail;@JsonKey(name: 'billing_id') String? get billingId;@JsonKey(name: 'subscription_status') SubscriptionStatus get subscriptionStatus;@JsonKey(name: 'quota_limit') double get quotaLimit;@JsonKey(name: 'tpm_limit') int get tpmLimit;@JsonKey(name: 'rpm_limit') int get rpmLimit;@JsonKey(name: 'allowed_email_domains') List<String> get allowedEmailDomains;
/// Create a copy of Organization
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OrganizationCopyWith<Organization> get copyWith => _$OrganizationCopyWithImpl<Organization>(this as Organization, _$identity);

  /// Serializes this Organization to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'Organization(id: $id, slug: $slug, name: $name, createdAt: $createdAt, isActive: $isActive, tier: $tier, contactEmail: $contactEmail, billingId: $billingId, subscriptionStatus: $subscriptionStatus, quotaLimit: $quotaLimit, tpmLimit: $tpmLimit, rpmLimit: $rpmLimit, allowedEmailDomains: $allowedEmailDomains)';
}


}

/// @nodoc
abstract mixin class $OrganizationCopyWith<$Res>  {
  factory $OrganizationCopyWith(Organization value, $Res Function(Organization) _then) = _$OrganizationCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String? slug, String name,@JsonKey(name: 'created_at') DateTime? createdAt,@JsonKey(name: 'is_active') bool isActive, String tier,@JsonKey(name: 'contact_email') String? contactEmail,@JsonKey(name: 'billing_id') String? billingId,@JsonKey(name: 'subscription_status') SubscriptionStatus subscriptionStatus,@JsonKey(name: 'quota_limit') double quotaLimit,@JsonKey(name: 'tpm_limit') int tpmLimit,@JsonKey(name: 'rpm_limit') int rpmLimit,@JsonKey(name: 'allowed_email_domains') List<String> allowedEmailDomains
});




}
/// @nodoc
class _$OrganizationCopyWithImpl<$Res>
    implements $OrganizationCopyWith<$Res> {
  _$OrganizationCopyWithImpl(this._self, this._then);

  final Organization _self;
  final $Res Function(Organization) _then;

/// Create a copy of Organization
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = freezed,Object? name = null,Object? createdAt = freezed,Object? isActive = null,Object? tier = null,Object? contactEmail = freezed,Object? billingId = freezed,Object? subscriptionStatus = null,Object? quotaLimit = null,Object? tpmLimit = null,Object? rpmLimit = null,Object? allowedEmailDomains = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime?,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,tier: null == tier ? _self.tier : tier // ignore: cast_nullable_to_non_nullable
as String,contactEmail: freezed == contactEmail ? _self.contactEmail : contactEmail // ignore: cast_nullable_to_non_nullable
as String?,billingId: freezed == billingId ? _self.billingId : billingId // ignore: cast_nullable_to_non_nullable
as String?,subscriptionStatus: null == subscriptionStatus ? _self.subscriptionStatus : subscriptionStatus // ignore: cast_nullable_to_non_nullable
as SubscriptionStatus,quotaLimit: null == quotaLimit ? _self.quotaLimit : quotaLimit // ignore: cast_nullable_to_non_nullable
as double,tpmLimit: null == tpmLimit ? _self.tpmLimit : tpmLimit // ignore: cast_nullable_to_non_nullable
as int,rpmLimit: null == rpmLimit ? _self.rpmLimit : rpmLimit // ignore: cast_nullable_to_non_nullable
as int,allowedEmailDomains: null == allowedEmailDomains ? _self.allowedEmailDomains : allowedEmailDomains // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [Organization].
extension OrganizationPatterns on Organization {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Organization value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Organization() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Organization value)  $default,){
final _that = this;
switch (_that) {
case _Organization():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Organization value)?  $default,){
final _that = this;
switch (_that) {
case _Organization() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String? slug,  String name, @JsonKey(name: 'created_at')  DateTime? createdAt, @JsonKey(name: 'is_active')  bool isActive,  String tier, @JsonKey(name: 'contact_email')  String? contactEmail, @JsonKey(name: 'billing_id')  String? billingId, @JsonKey(name: 'subscription_status')  SubscriptionStatus subscriptionStatus, @JsonKey(name: 'quota_limit')  double quotaLimit, @JsonKey(name: 'tpm_limit')  int tpmLimit, @JsonKey(name: 'rpm_limit')  int rpmLimit, @JsonKey(name: 'allowed_email_domains')  List<String> allowedEmailDomains)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Organization() when $default != null:
return $default(_that.id,_that.slug,_that.name,_that.createdAt,_that.isActive,_that.tier,_that.contactEmail,_that.billingId,_that.subscriptionStatus,_that.quotaLimit,_that.tpmLimit,_that.rpmLimit,_that.allowedEmailDomains);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String? slug,  String name, @JsonKey(name: 'created_at')  DateTime? createdAt, @JsonKey(name: 'is_active')  bool isActive,  String tier, @JsonKey(name: 'contact_email')  String? contactEmail, @JsonKey(name: 'billing_id')  String? billingId, @JsonKey(name: 'subscription_status')  SubscriptionStatus subscriptionStatus, @JsonKey(name: 'quota_limit')  double quotaLimit, @JsonKey(name: 'tpm_limit')  int tpmLimit, @JsonKey(name: 'rpm_limit')  int rpmLimit, @JsonKey(name: 'allowed_email_domains')  List<String> allowedEmailDomains)  $default,) {final _that = this;
switch (_that) {
case _Organization():
return $default(_that.id,_that.slug,_that.name,_that.createdAt,_that.isActive,_that.tier,_that.contactEmail,_that.billingId,_that.subscriptionStatus,_that.quotaLimit,_that.tpmLimit,_that.rpmLimit,_that.allowedEmailDomains);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String? slug,  String name, @JsonKey(name: 'created_at')  DateTime? createdAt, @JsonKey(name: 'is_active')  bool isActive,  String tier, @JsonKey(name: 'contact_email')  String? contactEmail, @JsonKey(name: 'billing_id')  String? billingId, @JsonKey(name: 'subscription_status')  SubscriptionStatus subscriptionStatus, @JsonKey(name: 'quota_limit')  double quotaLimit, @JsonKey(name: 'tpm_limit')  int tpmLimit, @JsonKey(name: 'rpm_limit')  int rpmLimit, @JsonKey(name: 'allowed_email_domains')  List<String> allowedEmailDomains)?  $default,) {final _that = this;
switch (_that) {
case _Organization() when $default != null:
return $default(_that.id,_that.slug,_that.name,_that.createdAt,_that.isActive,_that.tier,_that.contactEmail,_that.billingId,_that.subscriptionStatus,_that.quotaLimit,_that.tpmLimit,_that.rpmLimit,_that.allowedEmailDomains);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _Organization extends Organization {
  const _Organization({@StrictOpaqueIdConverter() required this.id, this.slug, required this.name, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'is_active') this.isActive = true, this.tier = 'standard', @JsonKey(name: 'contact_email') this.contactEmail, @JsonKey(name: 'billing_id') this.billingId, @JsonKey(name: 'subscription_status') this.subscriptionStatus = SubscriptionStatus.active, @JsonKey(name: 'quota_limit') this.quotaLimit = 0.0, @JsonKey(name: 'tpm_limit') this.tpmLimit = 100000, @JsonKey(name: 'rpm_limit') this.rpmLimit = 60, @JsonKey(name: 'allowed_email_domains') final  List<String> allowedEmailDomains = const []}): _allowedEmailDomains = allowedEmailDomains,super._();
  factory _Organization.fromJson(Map<String, dynamic> json) => _$OrganizationFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String? slug;
@override final  String name;
@override@JsonKey(name: 'created_at') final  DateTime? createdAt;
@override@JsonKey(name: 'is_active') final  bool isActive;
@override@JsonKey() final  String tier;
@override@JsonKey(name: 'contact_email') final  String? contactEmail;
@override@JsonKey(name: 'billing_id') final  String? billingId;
@override@JsonKey(name: 'subscription_status') final  SubscriptionStatus subscriptionStatus;
@override@JsonKey(name: 'quota_limit') final  double quotaLimit;
@override@JsonKey(name: 'tpm_limit') final  int tpmLimit;
@override@JsonKey(name: 'rpm_limit') final  int rpmLimit;
 final  List<String> _allowedEmailDomains;
@override@JsonKey(name: 'allowed_email_domains') List<String> get allowedEmailDomains {
  if (_allowedEmailDomains is EqualUnmodifiableListView) return _allowedEmailDomains;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedEmailDomains);
}


/// Create a copy of Organization
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OrganizationCopyWith<_Organization> get copyWith => __$OrganizationCopyWithImpl<_Organization>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OrganizationToJson(this, );
}



@override
String toString() {
  return 'Organization(id: $id, slug: $slug, name: $name, createdAt: $createdAt, isActive: $isActive, tier: $tier, contactEmail: $contactEmail, billingId: $billingId, subscriptionStatus: $subscriptionStatus, quotaLimit: $quotaLimit, tpmLimit: $tpmLimit, rpmLimit: $rpmLimit, allowedEmailDomains: $allowedEmailDomains)';
}


}

/// @nodoc
abstract mixin class _$OrganizationCopyWith<$Res> implements $OrganizationCopyWith<$Res> {
  factory _$OrganizationCopyWith(_Organization value, $Res Function(_Organization) _then) = __$OrganizationCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String? slug, String name,@JsonKey(name: 'created_at') DateTime? createdAt,@JsonKey(name: 'is_active') bool isActive, String tier,@JsonKey(name: 'contact_email') String? contactEmail,@JsonKey(name: 'billing_id') String? billingId,@JsonKey(name: 'subscription_status') SubscriptionStatus subscriptionStatus,@JsonKey(name: 'quota_limit') double quotaLimit,@JsonKey(name: 'tpm_limit') int tpmLimit,@JsonKey(name: 'rpm_limit') int rpmLimit,@JsonKey(name: 'allowed_email_domains') List<String> allowedEmailDomains
});




}
/// @nodoc
class __$OrganizationCopyWithImpl<$Res>
    implements _$OrganizationCopyWith<$Res> {
  __$OrganizationCopyWithImpl(this._self, this._then);

  final _Organization _self;
  final $Res Function(_Organization) _then;

/// Create a copy of Organization
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = freezed,Object? name = null,Object? createdAt = freezed,Object? isActive = null,Object? tier = null,Object? contactEmail = freezed,Object? billingId = freezed,Object? subscriptionStatus = null,Object? quotaLimit = null,Object? tpmLimit = null,Object? rpmLimit = null,Object? allowedEmailDomains = null,}) {
  return _then(_Organization(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime?,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,tier: null == tier ? _self.tier : tier // ignore: cast_nullable_to_non_nullable
as String,contactEmail: freezed == contactEmail ? _self.contactEmail : contactEmail // ignore: cast_nullable_to_non_nullable
as String?,billingId: freezed == billingId ? _self.billingId : billingId // ignore: cast_nullable_to_non_nullable
as String?,subscriptionStatus: null == subscriptionStatus ? _self.subscriptionStatus : subscriptionStatus // ignore: cast_nullable_to_non_nullable
as SubscriptionStatus,quotaLimit: null == quotaLimit ? _self.quotaLimit : quotaLimit // ignore: cast_nullable_to_non_nullable
as double,tpmLimit: null == tpmLimit ? _self.tpmLimit : tpmLimit // ignore: cast_nullable_to_non_nullable
as int,rpmLimit: null == rpmLimit ? _self.rpmLimit : rpmLimit // ignore: cast_nullable_to_non_nullable
as int,allowedEmailDomains: null == allowedEmailDomains ? _self._allowedEmailDomains : allowedEmailDomains // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}


/// @nodoc
mixin _$OrganizationUpdateDto {

 String? get name; String? get tier;@JsonKey(name: 'is_active') bool? get isActive;@JsonKey(name: 'contact_email') String? get contactEmail;@JsonKey(name: 'billing_id') String? get billingId;@JsonKey(name: 'subscription_status') SubscriptionStatus? get subscriptionStatus;@JsonKey(name: 'quota_limit') double? get quotaLimit;@JsonKey(name: 'tpm_limit') int? get tpmLimit;@JsonKey(name: 'rpm_limit') int? get rpmLimit;@JsonKey(name: 'allowed_email_domains') List<String>? get allowedEmailDomains;
/// Create a copy of OrganizationUpdateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OrganizationUpdateDtoCopyWith<OrganizationUpdateDto> get copyWith => _$OrganizationUpdateDtoCopyWithImpl<OrganizationUpdateDto>(this as OrganizationUpdateDto, _$identity);

  /// Serializes this OrganizationUpdateDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OrganizationUpdateDto(name: $name, tier: $tier, isActive: $isActive, contactEmail: $contactEmail, billingId: $billingId, subscriptionStatus: $subscriptionStatus, quotaLimit: $quotaLimit, tpmLimit: $tpmLimit, rpmLimit: $rpmLimit, allowedEmailDomains: $allowedEmailDomains)';
}


}

/// @nodoc
abstract mixin class $OrganizationUpdateDtoCopyWith<$Res>  {
  factory $OrganizationUpdateDtoCopyWith(OrganizationUpdateDto value, $Res Function(OrganizationUpdateDto) _then) = _$OrganizationUpdateDtoCopyWithImpl;
@useResult
$Res call({
 String? name, String? tier,@JsonKey(name: 'is_active') bool? isActive,@JsonKey(name: 'contact_email') String? contactEmail,@JsonKey(name: 'billing_id') String? billingId,@JsonKey(name: 'subscription_status') SubscriptionStatus? subscriptionStatus,@JsonKey(name: 'quota_limit') double? quotaLimit,@JsonKey(name: 'tpm_limit') int? tpmLimit,@JsonKey(name: 'rpm_limit') int? rpmLimit,@JsonKey(name: 'allowed_email_domains') List<String>? allowedEmailDomains
});




}
/// @nodoc
class _$OrganizationUpdateDtoCopyWithImpl<$Res>
    implements $OrganizationUpdateDtoCopyWith<$Res> {
  _$OrganizationUpdateDtoCopyWithImpl(this._self, this._then);

  final OrganizationUpdateDto _self;
  final $Res Function(OrganizationUpdateDto) _then;

/// Create a copy of OrganizationUpdateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = freezed,Object? tier = freezed,Object? isActive = freezed,Object? contactEmail = freezed,Object? billingId = freezed,Object? subscriptionStatus = freezed,Object? quotaLimit = freezed,Object? tpmLimit = freezed,Object? rpmLimit = freezed,Object? allowedEmailDomains = freezed,}) {
  return _then(_self.copyWith(
name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,tier: freezed == tier ? _self.tier : tier // ignore: cast_nullable_to_non_nullable
as String?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,contactEmail: freezed == contactEmail ? _self.contactEmail : contactEmail // ignore: cast_nullable_to_non_nullable
as String?,billingId: freezed == billingId ? _self.billingId : billingId // ignore: cast_nullable_to_non_nullable
as String?,subscriptionStatus: freezed == subscriptionStatus ? _self.subscriptionStatus : subscriptionStatus // ignore: cast_nullable_to_non_nullable
as SubscriptionStatus?,quotaLimit: freezed == quotaLimit ? _self.quotaLimit : quotaLimit // ignore: cast_nullable_to_non_nullable
as double?,tpmLimit: freezed == tpmLimit ? _self.tpmLimit : tpmLimit // ignore: cast_nullable_to_non_nullable
as int?,rpmLimit: freezed == rpmLimit ? _self.rpmLimit : rpmLimit // ignore: cast_nullable_to_non_nullable
as int?,allowedEmailDomains: freezed == allowedEmailDomains ? _self.allowedEmailDomains : allowedEmailDomains // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}

}


/// Adds pattern-matching-related methods to [OrganizationUpdateDto].
extension OrganizationUpdateDtoPatterns on OrganizationUpdateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OrganizationUpdateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OrganizationUpdateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OrganizationUpdateDto value)  $default,){
final _that = this;
switch (_that) {
case _OrganizationUpdateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OrganizationUpdateDto value)?  $default,){
final _that = this;
switch (_that) {
case _OrganizationUpdateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? name,  String? tier, @JsonKey(name: 'is_active')  bool? isActive, @JsonKey(name: 'contact_email')  String? contactEmail, @JsonKey(name: 'billing_id')  String? billingId, @JsonKey(name: 'subscription_status')  SubscriptionStatus? subscriptionStatus, @JsonKey(name: 'quota_limit')  double? quotaLimit, @JsonKey(name: 'tpm_limit')  int? tpmLimit, @JsonKey(name: 'rpm_limit')  int? rpmLimit, @JsonKey(name: 'allowed_email_domains')  List<String>? allowedEmailDomains)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OrganizationUpdateDto() when $default != null:
return $default(_that.name,_that.tier,_that.isActive,_that.contactEmail,_that.billingId,_that.subscriptionStatus,_that.quotaLimit,_that.tpmLimit,_that.rpmLimit,_that.allowedEmailDomains);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? name,  String? tier, @JsonKey(name: 'is_active')  bool? isActive, @JsonKey(name: 'contact_email')  String? contactEmail, @JsonKey(name: 'billing_id')  String? billingId, @JsonKey(name: 'subscription_status')  SubscriptionStatus? subscriptionStatus, @JsonKey(name: 'quota_limit')  double? quotaLimit, @JsonKey(name: 'tpm_limit')  int? tpmLimit, @JsonKey(name: 'rpm_limit')  int? rpmLimit, @JsonKey(name: 'allowed_email_domains')  List<String>? allowedEmailDomains)  $default,) {final _that = this;
switch (_that) {
case _OrganizationUpdateDto():
return $default(_that.name,_that.tier,_that.isActive,_that.contactEmail,_that.billingId,_that.subscriptionStatus,_that.quotaLimit,_that.tpmLimit,_that.rpmLimit,_that.allowedEmailDomains);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? name,  String? tier, @JsonKey(name: 'is_active')  bool? isActive, @JsonKey(name: 'contact_email')  String? contactEmail, @JsonKey(name: 'billing_id')  String? billingId, @JsonKey(name: 'subscription_status')  SubscriptionStatus? subscriptionStatus, @JsonKey(name: 'quota_limit')  double? quotaLimit, @JsonKey(name: 'tpm_limit')  int? tpmLimit, @JsonKey(name: 'rpm_limit')  int? rpmLimit, @JsonKey(name: 'allowed_email_domains')  List<String>? allowedEmailDomains)?  $default,) {final _that = this;
switch (_that) {
case _OrganizationUpdateDto() when $default != null:
return $default(_that.name,_that.tier,_that.isActive,_that.contactEmail,_that.billingId,_that.subscriptionStatus,_that.quotaLimit,_that.tpmLimit,_that.rpmLimit,_that.allowedEmailDomains);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, includeIfNull: false)
class _OrganizationUpdateDto extends OrganizationUpdateDto {
  const _OrganizationUpdateDto({this.name, this.tier, @JsonKey(name: 'is_active') this.isActive, @JsonKey(name: 'contact_email') this.contactEmail, @JsonKey(name: 'billing_id') this.billingId, @JsonKey(name: 'subscription_status') this.subscriptionStatus, @JsonKey(name: 'quota_limit') this.quotaLimit, @JsonKey(name: 'tpm_limit') this.tpmLimit, @JsonKey(name: 'rpm_limit') this.rpmLimit, @JsonKey(name: 'allowed_email_domains') final  List<String>? allowedEmailDomains}): _allowedEmailDomains = allowedEmailDomains,super._();
  factory _OrganizationUpdateDto.fromJson(Map<String, dynamic> json) => _$OrganizationUpdateDtoFromJson(json);

@override final  String? name;
@override final  String? tier;
@override@JsonKey(name: 'is_active') final  bool? isActive;
@override@JsonKey(name: 'contact_email') final  String? contactEmail;
@override@JsonKey(name: 'billing_id') final  String? billingId;
@override@JsonKey(name: 'subscription_status') final  SubscriptionStatus? subscriptionStatus;
@override@JsonKey(name: 'quota_limit') final  double? quotaLimit;
@override@JsonKey(name: 'tpm_limit') final  int? tpmLimit;
@override@JsonKey(name: 'rpm_limit') final  int? rpmLimit;
 final  List<String>? _allowedEmailDomains;
@override@JsonKey(name: 'allowed_email_domains') List<String>? get allowedEmailDomains {
  final value = _allowedEmailDomains;
  if (value == null) return null;
  if (_allowedEmailDomains is EqualUnmodifiableListView) return _allowedEmailDomains;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of OrganizationUpdateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OrganizationUpdateDtoCopyWith<_OrganizationUpdateDto> get copyWith => __$OrganizationUpdateDtoCopyWithImpl<_OrganizationUpdateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OrganizationUpdateDtoToJson(this, );
}



@override
String toString() {
  return 'OrganizationUpdateDto(name: $name, tier: $tier, isActive: $isActive, contactEmail: $contactEmail, billingId: $billingId, subscriptionStatus: $subscriptionStatus, quotaLimit: $quotaLimit, tpmLimit: $tpmLimit, rpmLimit: $rpmLimit, allowedEmailDomains: $allowedEmailDomains)';
}


}

/// @nodoc
abstract mixin class _$OrganizationUpdateDtoCopyWith<$Res> implements $OrganizationUpdateDtoCopyWith<$Res> {
  factory _$OrganizationUpdateDtoCopyWith(_OrganizationUpdateDto value, $Res Function(_OrganizationUpdateDto) _then) = __$OrganizationUpdateDtoCopyWithImpl;
@override @useResult
$Res call({
 String? name, String? tier,@JsonKey(name: 'is_active') bool? isActive,@JsonKey(name: 'contact_email') String? contactEmail,@JsonKey(name: 'billing_id') String? billingId,@JsonKey(name: 'subscription_status') SubscriptionStatus? subscriptionStatus,@JsonKey(name: 'quota_limit') double? quotaLimit,@JsonKey(name: 'tpm_limit') int? tpmLimit,@JsonKey(name: 'rpm_limit') int? rpmLimit,@JsonKey(name: 'allowed_email_domains') List<String>? allowedEmailDomains
});




}
/// @nodoc
class __$OrganizationUpdateDtoCopyWithImpl<$Res>
    implements _$OrganizationUpdateDtoCopyWith<$Res> {
  __$OrganizationUpdateDtoCopyWithImpl(this._self, this._then);

  final _OrganizationUpdateDto _self;
  final $Res Function(_OrganizationUpdateDto) _then;

/// Create a copy of OrganizationUpdateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = freezed,Object? tier = freezed,Object? isActive = freezed,Object? contactEmail = freezed,Object? billingId = freezed,Object? subscriptionStatus = freezed,Object? quotaLimit = freezed,Object? tpmLimit = freezed,Object? rpmLimit = freezed,Object? allowedEmailDomains = freezed,}) {
  return _then(_OrganizationUpdateDto(
name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,tier: freezed == tier ? _self.tier : tier // ignore: cast_nullable_to_non_nullable
as String?,isActive: freezed == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool?,contactEmail: freezed == contactEmail ? _self.contactEmail : contactEmail // ignore: cast_nullable_to_non_nullable
as String?,billingId: freezed == billingId ? _self.billingId : billingId // ignore: cast_nullable_to_non_nullable
as String?,subscriptionStatus: freezed == subscriptionStatus ? _self.subscriptionStatus : subscriptionStatus // ignore: cast_nullable_to_non_nullable
as SubscriptionStatus?,quotaLimit: freezed == quotaLimit ? _self.quotaLimit : quotaLimit // ignore: cast_nullable_to_non_nullable
as double?,tpmLimit: freezed == tpmLimit ? _self.tpmLimit : tpmLimit // ignore: cast_nullable_to_non_nullable
as int?,rpmLimit: freezed == rpmLimit ? _self.rpmLimit : rpmLimit // ignore: cast_nullable_to_non_nullable
as int?,allowedEmailDomains: freezed == allowedEmailDomains ? _self._allowedEmailDomains : allowedEmailDomains // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}


}


/// @nodoc
mixin _$OrganizationDeleteResponse {

 String get status;@StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id') String get deletedId;
/// Create a copy of OrganizationDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OrganizationDeleteResponseCopyWith<OrganizationDeleteResponse> get copyWith => _$OrganizationDeleteResponseCopyWithImpl<OrganizationDeleteResponse>(this as OrganizationDeleteResponse, _$identity);

  /// Serializes this OrganizationDeleteResponse to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OrganizationDeleteResponse(status: $status, deletedId: $deletedId)';
}


}

/// @nodoc
abstract mixin class $OrganizationDeleteResponseCopyWith<$Res>  {
  factory $OrganizationDeleteResponseCopyWith(OrganizationDeleteResponse value, $Res Function(OrganizationDeleteResponse) _then) = _$OrganizationDeleteResponseCopyWithImpl;
@useResult
$Res call({
 String status,@StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id') String deletedId
});




}
/// @nodoc
class _$OrganizationDeleteResponseCopyWithImpl<$Res>
    implements $OrganizationDeleteResponseCopyWith<$Res> {
  _$OrganizationDeleteResponseCopyWithImpl(this._self, this._then);

  final OrganizationDeleteResponse _self;
  final $Res Function(OrganizationDeleteResponse) _then;

/// Create a copy of OrganizationDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? status = null,Object? deletedId = null,}) {
  return _then(_self.copyWith(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,deletedId: null == deletedId ? _self.deletedId : deletedId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [OrganizationDeleteResponse].
extension OrganizationDeleteResponsePatterns on OrganizationDeleteResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OrganizationDeleteResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OrganizationDeleteResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OrganizationDeleteResponse value)  $default,){
final _that = this;
switch (_that) {
case _OrganizationDeleteResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OrganizationDeleteResponse value)?  $default,){
final _that = this;
switch (_that) {
case _OrganizationDeleteResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String status, @StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id')  String deletedId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OrganizationDeleteResponse() when $default != null:
return $default(_that.status,_that.deletedId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String status, @StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id')  String deletedId)  $default,) {final _that = this;
switch (_that) {
case _OrganizationDeleteResponse():
return $default(_that.status,_that.deletedId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String status, @StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id')  String deletedId)?  $default,) {final _that = this;
switch (_that) {
case _OrganizationDeleteResponse() when $default != null:
return $default(_that.status,_that.deletedId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _OrganizationDeleteResponse extends OrganizationDeleteResponse {
  const _OrganizationDeleteResponse({required this.status, @StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id') required this.deletedId}): super._();
  factory _OrganizationDeleteResponse.fromJson(Map<String, dynamic> json) => _$OrganizationDeleteResponseFromJson(json);

@override final  String status;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id') final  String deletedId;

/// Create a copy of OrganizationDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OrganizationDeleteResponseCopyWith<_OrganizationDeleteResponse> get copyWith => __$OrganizationDeleteResponseCopyWithImpl<_OrganizationDeleteResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OrganizationDeleteResponseToJson(this, );
}



@override
String toString() {
  return 'OrganizationDeleteResponse(status: $status, deletedId: $deletedId)';
}


}

/// @nodoc
abstract mixin class _$OrganizationDeleteResponseCopyWith<$Res> implements $OrganizationDeleteResponseCopyWith<$Res> {
  factory _$OrganizationDeleteResponseCopyWith(_OrganizationDeleteResponse value, $Res Function(_OrganizationDeleteResponse) _then) = __$OrganizationDeleteResponseCopyWithImpl;
@override @useResult
$Res call({
 String status,@StrictOpaqueIdConverter()@JsonKey(name: 'deleted_id') String deletedId
});




}
/// @nodoc
class __$OrganizationDeleteResponseCopyWithImpl<$Res>
    implements _$OrganizationDeleteResponseCopyWith<$Res> {
  __$OrganizationDeleteResponseCopyWithImpl(this._self, this._then);

  final _OrganizationDeleteResponse _self;
  final $Res Function(_OrganizationDeleteResponse) _then;

/// Create a copy of OrganizationDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? status = null,Object? deletedId = null,}) {
  return _then(_OrganizationDeleteResponse(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,deletedId: null == deletedId ? _self.deletedId : deletedId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$UserDeleteResponse {

 String get status;@StrictOpaqueIdConverter() String get id;
/// Create a copy of UserDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserDeleteResponseCopyWith<UserDeleteResponse> get copyWith => _$UserDeleteResponseCopyWithImpl<UserDeleteResponse>(this as UserDeleteResponse, _$identity);

  /// Serializes this UserDeleteResponse to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'UserDeleteResponse(status: $status, id: $id)';
}


}

/// @nodoc
abstract mixin class $UserDeleteResponseCopyWith<$Res>  {
  factory $UserDeleteResponseCopyWith(UserDeleteResponse value, $Res Function(UserDeleteResponse) _then) = _$UserDeleteResponseCopyWithImpl;
@useResult
$Res call({
 String status,@StrictOpaqueIdConverter() String id
});




}
/// @nodoc
class _$UserDeleteResponseCopyWithImpl<$Res>
    implements $UserDeleteResponseCopyWith<$Res> {
  _$UserDeleteResponseCopyWithImpl(this._self, this._then);

  final UserDeleteResponse _self;
  final $Res Function(UserDeleteResponse) _then;

/// Create a copy of UserDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? status = null,Object? id = null,}) {
  return _then(_self.copyWith(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [UserDeleteResponse].
extension UserDeleteResponsePatterns on UserDeleteResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserDeleteResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserDeleteResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserDeleteResponse value)  $default,){
final _that = this;
switch (_that) {
case _UserDeleteResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserDeleteResponse value)?  $default,){
final _that = this;
switch (_that) {
case _UserDeleteResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String status, @StrictOpaqueIdConverter()  String id)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserDeleteResponse() when $default != null:
return $default(_that.status,_that.id);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String status, @StrictOpaqueIdConverter()  String id)  $default,) {final _that = this;
switch (_that) {
case _UserDeleteResponse():
return $default(_that.status,_that.id);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String status, @StrictOpaqueIdConverter()  String id)?  $default,) {final _that = this;
switch (_that) {
case _UserDeleteResponse() when $default != null:
return $default(_that.status,_that.id);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _UserDeleteResponse extends UserDeleteResponse {
  const _UserDeleteResponse({required this.status, @StrictOpaqueIdConverter() required this.id}): super._();
  factory _UserDeleteResponse.fromJson(Map<String, dynamic> json) => _$UserDeleteResponseFromJson(json);

@override final  String status;
@override@StrictOpaqueIdConverter() final  String id;

/// Create a copy of UserDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserDeleteResponseCopyWith<_UserDeleteResponse> get copyWith => __$UserDeleteResponseCopyWithImpl<_UserDeleteResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserDeleteResponseToJson(this, );
}



@override
String toString() {
  return 'UserDeleteResponse(status: $status, id: $id)';
}


}

/// @nodoc
abstract mixin class _$UserDeleteResponseCopyWith<$Res> implements $UserDeleteResponseCopyWith<$Res> {
  factory _$UserDeleteResponseCopyWith(_UserDeleteResponse value, $Res Function(_UserDeleteResponse) _then) = __$UserDeleteResponseCopyWithImpl;
@override @useResult
$Res call({
 String status,@StrictOpaqueIdConverter() String id
});




}
/// @nodoc
class __$UserDeleteResponseCopyWithImpl<$Res>
    implements _$UserDeleteResponseCopyWith<$Res> {
  __$UserDeleteResponseCopyWithImpl(this._self, this._then);

  final _UserDeleteResponse _self;
  final $Res Function(_UserDeleteResponse) _then;

/// Create a copy of UserDeleteResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? status = null,Object? id = null,}) {
  return _then(_UserDeleteResponse(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$InvitationCreateDto {

 String get email; UserRole get role;@JsonKey(name: 'expires_in_hours') int get expiresInHours;
/// Create a copy of InvitationCreateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InvitationCreateDtoCopyWith<InvitationCreateDto> get copyWith => _$InvitationCreateDtoCopyWithImpl<InvitationCreateDto>(this as InvitationCreateDto, _$identity);

  /// Serializes this InvitationCreateDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'InvitationCreateDto(email: $email, role: $role, expiresInHours: $expiresInHours)';
}


}

/// @nodoc
abstract mixin class $InvitationCreateDtoCopyWith<$Res>  {
  factory $InvitationCreateDtoCopyWith(InvitationCreateDto value, $Res Function(InvitationCreateDto) _then) = _$InvitationCreateDtoCopyWithImpl;
@useResult
$Res call({
 String email, UserRole role,@JsonKey(name: 'expires_in_hours') int expiresInHours
});




}
/// @nodoc
class _$InvitationCreateDtoCopyWithImpl<$Res>
    implements $InvitationCreateDtoCopyWith<$Res> {
  _$InvitationCreateDtoCopyWithImpl(this._self, this._then);

  final InvitationCreateDto _self;
  final $Res Function(InvitationCreateDto) _then;

/// Create a copy of InvitationCreateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? email = null,Object? role = null,Object? expiresInHours = null,}) {
  return _then(_self.copyWith(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,expiresInHours: null == expiresInHours ? _self.expiresInHours : expiresInHours // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [InvitationCreateDto].
extension InvitationCreateDtoPatterns on InvitationCreateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InvitationCreateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InvitationCreateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InvitationCreateDto value)  $default,){
final _that = this;
switch (_that) {
case _InvitationCreateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InvitationCreateDto value)?  $default,){
final _that = this;
switch (_that) {
case _InvitationCreateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String email,  UserRole role, @JsonKey(name: 'expires_in_hours')  int expiresInHours)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InvitationCreateDto() when $default != null:
return $default(_that.email,_that.role,_that.expiresInHours);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String email,  UserRole role, @JsonKey(name: 'expires_in_hours')  int expiresInHours)  $default,) {final _that = this;
switch (_that) {
case _InvitationCreateDto():
return $default(_that.email,_that.role,_that.expiresInHours);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String email,  UserRole role, @JsonKey(name: 'expires_in_hours')  int expiresInHours)?  $default,) {final _that = this;
switch (_that) {
case _InvitationCreateDto() when $default != null:
return $default(_that.email,_that.role,_that.expiresInHours);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _InvitationCreateDto extends InvitationCreateDto {
  const _InvitationCreateDto({required this.email, this.role = UserRole.member, @JsonKey(name: 'expires_in_hours') this.expiresInHours = 168}): super._();
  factory _InvitationCreateDto.fromJson(Map<String, dynamic> json) => _$InvitationCreateDtoFromJson(json);

@override final  String email;
@override@JsonKey() final  UserRole role;
@override@JsonKey(name: 'expires_in_hours') final  int expiresInHours;

/// Create a copy of InvitationCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InvitationCreateDtoCopyWith<_InvitationCreateDto> get copyWith => __$InvitationCreateDtoCopyWithImpl<_InvitationCreateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InvitationCreateDtoToJson(this, );
}



@override
String toString() {
  return 'InvitationCreateDto(email: $email, role: $role, expiresInHours: $expiresInHours)';
}


}

/// @nodoc
abstract mixin class _$InvitationCreateDtoCopyWith<$Res> implements $InvitationCreateDtoCopyWith<$Res> {
  factory _$InvitationCreateDtoCopyWith(_InvitationCreateDto value, $Res Function(_InvitationCreateDto) _then) = __$InvitationCreateDtoCopyWithImpl;
@override @useResult
$Res call({
 String email, UserRole role,@JsonKey(name: 'expires_in_hours') int expiresInHours
});




}
/// @nodoc
class __$InvitationCreateDtoCopyWithImpl<$Res>
    implements _$InvitationCreateDtoCopyWith<$Res> {
  __$InvitationCreateDtoCopyWithImpl(this._self, this._then);

  final _InvitationCreateDto _self;
  final $Res Function(_InvitationCreateDto) _then;

/// Create a copy of InvitationCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? email = null,Object? role = null,Object? expiresInHours = null,}) {
  return _then(_InvitationCreateDto(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,expiresInHours: null == expiresInHours ? _self.expiresInHours : expiresInHours // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$InvitationResponseDto {

@StrictOpaqueIdConverter() String get id;@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String get organizationId; String get email; UserRole get role; InvitationStatus get status;@JsonKey(name: 'email_delivery_status') EmailDeliveryStatus get emailDeliveryStatus;@StrictOpaqueIdConverter()@JsonKey(name: 'invited_by') String get invitedBy;@JsonKey(name: 'expires_at') DateTime get expiresAt;@JsonKey(name: 'created_at') DateTime get createdAt;
/// Create a copy of InvitationResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InvitationResponseDtoCopyWith<InvitationResponseDto> get copyWith => _$InvitationResponseDtoCopyWithImpl<InvitationResponseDto>(this as InvitationResponseDto, _$identity);

  /// Serializes this InvitationResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'InvitationResponseDto(id: $id, organizationId: $organizationId, email: $email, role: $role, status: $status, emailDeliveryStatus: $emailDeliveryStatus, invitedBy: $invitedBy, expiresAt: $expiresAt, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $InvitationResponseDtoCopyWith<$Res>  {
  factory $InvitationResponseDtoCopyWith(InvitationResponseDto value, $Res Function(InvitationResponseDto) _then) = _$InvitationResponseDtoCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId, String email, UserRole role, InvitationStatus status,@JsonKey(name: 'email_delivery_status') EmailDeliveryStatus emailDeliveryStatus,@StrictOpaqueIdConverter()@JsonKey(name: 'invited_by') String invitedBy,@JsonKey(name: 'expires_at') DateTime expiresAt,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class _$InvitationResponseDtoCopyWithImpl<$Res>
    implements $InvitationResponseDtoCopyWith<$Res> {
  _$InvitationResponseDtoCopyWithImpl(this._self, this._then);

  final InvitationResponseDto _self;
  final $Res Function(InvitationResponseDto) _then;

/// Create a copy of InvitationResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? organizationId = null,Object? email = null,Object? role = null,Object? status = null,Object? emailDeliveryStatus = null,Object? invitedBy = null,Object? expiresAt = null,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as InvitationStatus,emailDeliveryStatus: null == emailDeliveryStatus ? _self.emailDeliveryStatus : emailDeliveryStatus // ignore: cast_nullable_to_non_nullable
as EmailDeliveryStatus,invitedBy: null == invitedBy ? _self.invitedBy : invitedBy // ignore: cast_nullable_to_non_nullable
as String,expiresAt: null == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [InvitationResponseDto].
extension InvitationResponseDtoPatterns on InvitationResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InvitationResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InvitationResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InvitationResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _InvitationResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InvitationResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _InvitationResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  String email,  UserRole role,  InvitationStatus status, @JsonKey(name: 'email_delivery_status')  EmailDeliveryStatus emailDeliveryStatus, @StrictOpaqueIdConverter()@JsonKey(name: 'invited_by')  String invitedBy, @JsonKey(name: 'expires_at')  DateTime expiresAt, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InvitationResponseDto() when $default != null:
return $default(_that.id,_that.organizationId,_that.email,_that.role,_that.status,_that.emailDeliveryStatus,_that.invitedBy,_that.expiresAt,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  String email,  UserRole role,  InvitationStatus status, @JsonKey(name: 'email_delivery_status')  EmailDeliveryStatus emailDeliveryStatus, @StrictOpaqueIdConverter()@JsonKey(name: 'invited_by')  String invitedBy, @JsonKey(name: 'expires_at')  DateTime expiresAt, @JsonKey(name: 'created_at')  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _InvitationResponseDto():
return $default(_that.id,_that.organizationId,_that.email,_that.role,_that.status,_that.emailDeliveryStatus,_that.invitedBy,_that.expiresAt,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  String email,  UserRole role,  InvitationStatus status, @JsonKey(name: 'email_delivery_status')  EmailDeliveryStatus emailDeliveryStatus, @StrictOpaqueIdConverter()@JsonKey(name: 'invited_by')  String invitedBy, @JsonKey(name: 'expires_at')  DateTime expiresAt, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _InvitationResponseDto() when $default != null:
return $default(_that.id,_that.organizationId,_that.email,_that.role,_that.status,_that.emailDeliveryStatus,_that.invitedBy,_that.expiresAt,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _InvitationResponseDto extends InvitationResponseDto {
  const _InvitationResponseDto({@StrictOpaqueIdConverter() required this.id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') required this.organizationId, required this.email, required this.role, required this.status, @JsonKey(name: 'email_delivery_status') this.emailDeliveryStatus = EmailDeliveryStatus.pending, @StrictOpaqueIdConverter()@JsonKey(name: 'invited_by') required this.invitedBy, @JsonKey(name: 'expires_at') required this.expiresAt, @JsonKey(name: 'created_at') required this.createdAt}): super._();
  factory _InvitationResponseDto.fromJson(Map<String, dynamic> json) => _$InvitationResponseDtoFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') final  String organizationId;
@override final  String email;
@override final  UserRole role;
@override final  InvitationStatus status;
@override@JsonKey(name: 'email_delivery_status') final  EmailDeliveryStatus emailDeliveryStatus;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'invited_by') final  String invitedBy;
@override@JsonKey(name: 'expires_at') final  DateTime expiresAt;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;

/// Create a copy of InvitationResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InvitationResponseDtoCopyWith<_InvitationResponseDto> get copyWith => __$InvitationResponseDtoCopyWithImpl<_InvitationResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InvitationResponseDtoToJson(this, );
}



@override
String toString() {
  return 'InvitationResponseDto(id: $id, organizationId: $organizationId, email: $email, role: $role, status: $status, emailDeliveryStatus: $emailDeliveryStatus, invitedBy: $invitedBy, expiresAt: $expiresAt, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$InvitationResponseDtoCopyWith<$Res> implements $InvitationResponseDtoCopyWith<$Res> {
  factory _$InvitationResponseDtoCopyWith(_InvitationResponseDto value, $Res Function(_InvitationResponseDto) _then) = __$InvitationResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId, String email, UserRole role, InvitationStatus status,@JsonKey(name: 'email_delivery_status') EmailDeliveryStatus emailDeliveryStatus,@StrictOpaqueIdConverter()@JsonKey(name: 'invited_by') String invitedBy,@JsonKey(name: 'expires_at') DateTime expiresAt,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class __$InvitationResponseDtoCopyWithImpl<$Res>
    implements _$InvitationResponseDtoCopyWith<$Res> {
  __$InvitationResponseDtoCopyWithImpl(this._self, this._then);

  final _InvitationResponseDto _self;
  final $Res Function(_InvitationResponseDto) _then;

/// Create a copy of InvitationResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? organizationId = null,Object? email = null,Object? role = null,Object? status = null,Object? emailDeliveryStatus = null,Object? invitedBy = null,Object? expiresAt = null,Object? createdAt = null,}) {
  return _then(_InvitationResponseDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as UserRole,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as InvitationStatus,emailDeliveryStatus: null == emailDeliveryStatus ? _self.emailDeliveryStatus : emailDeliveryStatus // ignore: cast_nullable_to_non_nullable
as EmailDeliveryStatus,invitedBy: null == invitedBy ? _self.invitedBy : invitedBy // ignore: cast_nullable_to_non_nullable
as String,expiresAt: null == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$InvitationBatchCreateDto {

 List<InvitationCreateDto> get recipients;
/// Create a copy of InvitationBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InvitationBatchCreateDtoCopyWith<InvitationBatchCreateDto> get copyWith => _$InvitationBatchCreateDtoCopyWithImpl<InvitationBatchCreateDto>(this as InvitationBatchCreateDto, _$identity);

  /// Serializes this InvitationBatchCreateDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'InvitationBatchCreateDto(recipients: $recipients)';
}


}

/// @nodoc
abstract mixin class $InvitationBatchCreateDtoCopyWith<$Res>  {
  factory $InvitationBatchCreateDtoCopyWith(InvitationBatchCreateDto value, $Res Function(InvitationBatchCreateDto) _then) = _$InvitationBatchCreateDtoCopyWithImpl;
@useResult
$Res call({
 List<InvitationCreateDto> recipients
});




}
/// @nodoc
class _$InvitationBatchCreateDtoCopyWithImpl<$Res>
    implements $InvitationBatchCreateDtoCopyWith<$Res> {
  _$InvitationBatchCreateDtoCopyWithImpl(this._self, this._then);

  final InvitationBatchCreateDto _self;
  final $Res Function(InvitationBatchCreateDto) _then;

/// Create a copy of InvitationBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipients = null,}) {
  return _then(_self.copyWith(
recipients: null == recipients ? _self.recipients : recipients // ignore: cast_nullable_to_non_nullable
as List<InvitationCreateDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [InvitationBatchCreateDto].
extension InvitationBatchCreateDtoPatterns on InvitationBatchCreateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InvitationBatchCreateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InvitationBatchCreateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InvitationBatchCreateDto value)  $default,){
final _that = this;
switch (_that) {
case _InvitationBatchCreateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InvitationBatchCreateDto value)?  $default,){
final _that = this;
switch (_that) {
case _InvitationBatchCreateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<InvitationCreateDto> recipients)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InvitationBatchCreateDto() when $default != null:
return $default(_that.recipients);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<InvitationCreateDto> recipients)  $default,) {final _that = this;
switch (_that) {
case _InvitationBatchCreateDto():
return $default(_that.recipients);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<InvitationCreateDto> recipients)?  $default,) {final _that = this;
switch (_that) {
case _InvitationBatchCreateDto() when $default != null:
return $default(_that.recipients);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _InvitationBatchCreateDto extends InvitationBatchCreateDto {
  const _InvitationBatchCreateDto({required final  List<InvitationCreateDto> recipients}): _recipients = recipients,super._();
  factory _InvitationBatchCreateDto.fromJson(Map<String, dynamic> json) => _$InvitationBatchCreateDtoFromJson(json);

 final  List<InvitationCreateDto> _recipients;
@override List<InvitationCreateDto> get recipients {
  if (_recipients is EqualUnmodifiableListView) return _recipients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recipients);
}


/// Create a copy of InvitationBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InvitationBatchCreateDtoCopyWith<_InvitationBatchCreateDto> get copyWith => __$InvitationBatchCreateDtoCopyWithImpl<_InvitationBatchCreateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InvitationBatchCreateDtoToJson(this, );
}



@override
String toString() {
  return 'InvitationBatchCreateDto(recipients: $recipients)';
}


}

/// @nodoc
abstract mixin class _$InvitationBatchCreateDtoCopyWith<$Res> implements $InvitationBatchCreateDtoCopyWith<$Res> {
  factory _$InvitationBatchCreateDtoCopyWith(_InvitationBatchCreateDto value, $Res Function(_InvitationBatchCreateDto) _then) = __$InvitationBatchCreateDtoCopyWithImpl;
@override @useResult
$Res call({
 List<InvitationCreateDto> recipients
});




}
/// @nodoc
class __$InvitationBatchCreateDtoCopyWithImpl<$Res>
    implements _$InvitationBatchCreateDtoCopyWith<$Res> {
  __$InvitationBatchCreateDtoCopyWithImpl(this._self, this._then);

  final _InvitationBatchCreateDto _self;
  final $Res Function(_InvitationBatchCreateDto) _then;

/// Create a copy of InvitationBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipients = null,}) {
  return _then(_InvitationBatchCreateDto(
recipients: null == recipients ? _self._recipients : recipients // ignore: cast_nullable_to_non_nullable
as List<InvitationCreateDto>,
  ));
}


}


/// @nodoc
mixin _$InvitationBatchResponseDto {

@JsonKey(name: 'created_count') int get createdCount; List<InvitationResponseDto> get invitations;
/// Create a copy of InvitationBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InvitationBatchResponseDtoCopyWith<InvitationBatchResponseDto> get copyWith => _$InvitationBatchResponseDtoCopyWithImpl<InvitationBatchResponseDto>(this as InvitationBatchResponseDto, _$identity);

  /// Serializes this InvitationBatchResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'InvitationBatchResponseDto(createdCount: $createdCount, invitations: $invitations)';
}


}

/// @nodoc
abstract mixin class $InvitationBatchResponseDtoCopyWith<$Res>  {
  factory $InvitationBatchResponseDtoCopyWith(InvitationBatchResponseDto value, $Res Function(InvitationBatchResponseDto) _then) = _$InvitationBatchResponseDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'created_count') int createdCount, List<InvitationResponseDto> invitations
});




}
/// @nodoc
class _$InvitationBatchResponseDtoCopyWithImpl<$Res>
    implements $InvitationBatchResponseDtoCopyWith<$Res> {
  _$InvitationBatchResponseDtoCopyWithImpl(this._self, this._then);

  final InvitationBatchResponseDto _self;
  final $Res Function(InvitationBatchResponseDto) _then;

/// Create a copy of InvitationBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? createdCount = null,Object? invitations = null,}) {
  return _then(_self.copyWith(
createdCount: null == createdCount ? _self.createdCount : createdCount // ignore: cast_nullable_to_non_nullable
as int,invitations: null == invitations ? _self.invitations : invitations // ignore: cast_nullable_to_non_nullable
as List<InvitationResponseDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [InvitationBatchResponseDto].
extension InvitationBatchResponseDtoPatterns on InvitationBatchResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InvitationBatchResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InvitationBatchResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InvitationBatchResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _InvitationBatchResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InvitationBatchResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _InvitationBatchResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'created_count')  int createdCount,  List<InvitationResponseDto> invitations)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InvitationBatchResponseDto() when $default != null:
return $default(_that.createdCount,_that.invitations);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'created_count')  int createdCount,  List<InvitationResponseDto> invitations)  $default,) {final _that = this;
switch (_that) {
case _InvitationBatchResponseDto():
return $default(_that.createdCount,_that.invitations);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'created_count')  int createdCount,  List<InvitationResponseDto> invitations)?  $default,) {final _that = this;
switch (_that) {
case _InvitationBatchResponseDto() when $default != null:
return $default(_that.createdCount,_that.invitations);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _InvitationBatchResponseDto extends InvitationBatchResponseDto {
  const _InvitationBatchResponseDto({@JsonKey(name: 'created_count') required this.createdCount, required final  List<InvitationResponseDto> invitations}): _invitations = invitations,super._();
  factory _InvitationBatchResponseDto.fromJson(Map<String, dynamic> json) => _$InvitationBatchResponseDtoFromJson(json);

@override@JsonKey(name: 'created_count') final  int createdCount;
 final  List<InvitationResponseDto> _invitations;
@override List<InvitationResponseDto> get invitations {
  if (_invitations is EqualUnmodifiableListView) return _invitations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_invitations);
}


/// Create a copy of InvitationBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InvitationBatchResponseDtoCopyWith<_InvitationBatchResponseDto> get copyWith => __$InvitationBatchResponseDtoCopyWithImpl<_InvitationBatchResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InvitationBatchResponseDtoToJson(this, );
}



@override
String toString() {
  return 'InvitationBatchResponseDto(createdCount: $createdCount, invitations: $invitations)';
}


}

/// @nodoc
abstract mixin class _$InvitationBatchResponseDtoCopyWith<$Res> implements $InvitationBatchResponseDtoCopyWith<$Res> {
  factory _$InvitationBatchResponseDtoCopyWith(_InvitationBatchResponseDto value, $Res Function(_InvitationBatchResponseDto) _then) = __$InvitationBatchResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'created_count') int createdCount, List<InvitationResponseDto> invitations
});




}
/// @nodoc
class __$InvitationBatchResponseDtoCopyWithImpl<$Res>
    implements _$InvitationBatchResponseDtoCopyWith<$Res> {
  __$InvitationBatchResponseDtoCopyWithImpl(this._self, this._then);

  final _InvitationBatchResponseDto _self;
  final $Res Function(_InvitationBatchResponseDto) _then;

/// Create a copy of InvitationBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? createdCount = null,Object? invitations = null,}) {
  return _then(_InvitationBatchResponseDto(
createdCount: null == createdCount ? _self.createdCount : createdCount // ignore: cast_nullable_to_non_nullable
as int,invitations: null == invitations ? _self._invitations : invitations // ignore: cast_nullable_to_non_nullable
as List<InvitationResponseDto>,
  ));
}


}


/// @nodoc
mixin _$TenantSecretCreateDto {

 SecretScope get scope;@JsonKey(name: 'target_identifier') String get targetIdentifier;@JsonKey(name: 'plaintext_secret') String get plaintextSecret;// Phase 3, Step 3: Add required storageMode with zero default value (REQ-012)
@JsonKey(name: 'storage_mode') SecretStorageMode get storageMode;
/// Create a copy of TenantSecretCreateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TenantSecretCreateDtoCopyWith<TenantSecretCreateDto> get copyWith => _$TenantSecretCreateDtoCopyWithImpl<TenantSecretCreateDto>(this as TenantSecretCreateDto, _$identity);

  /// Serializes this TenantSecretCreateDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TenantSecretCreateDto(scope: $scope, targetIdentifier: $targetIdentifier, plaintextSecret: $plaintextSecret, storageMode: $storageMode)';
}


}

/// @nodoc
abstract mixin class $TenantSecretCreateDtoCopyWith<$Res>  {
  factory $TenantSecretCreateDtoCopyWith(TenantSecretCreateDto value, $Res Function(TenantSecretCreateDto) _then) = _$TenantSecretCreateDtoCopyWithImpl;
@useResult
$Res call({
 SecretScope scope,@JsonKey(name: 'target_identifier') String targetIdentifier,@JsonKey(name: 'plaintext_secret') String plaintextSecret,@JsonKey(name: 'storage_mode') SecretStorageMode storageMode
});




}
/// @nodoc
class _$TenantSecretCreateDtoCopyWithImpl<$Res>
    implements $TenantSecretCreateDtoCopyWith<$Res> {
  _$TenantSecretCreateDtoCopyWithImpl(this._self, this._then);

  final TenantSecretCreateDto _self;
  final $Res Function(TenantSecretCreateDto) _then;

/// Create a copy of TenantSecretCreateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? scope = null,Object? targetIdentifier = null,Object? plaintextSecret = null,Object? storageMode = null,}) {
  return _then(_self.copyWith(
scope: null == scope ? _self.scope : scope // ignore: cast_nullable_to_non_nullable
as SecretScope,targetIdentifier: null == targetIdentifier ? _self.targetIdentifier : targetIdentifier // ignore: cast_nullable_to_non_nullable
as String,plaintextSecret: null == plaintextSecret ? _self.plaintextSecret : plaintextSecret // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as SecretStorageMode,
  ));
}

}


/// Adds pattern-matching-related methods to [TenantSecretCreateDto].
extension TenantSecretCreateDtoPatterns on TenantSecretCreateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TenantSecretCreateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TenantSecretCreateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TenantSecretCreateDto value)  $default,){
final _that = this;
switch (_that) {
case _TenantSecretCreateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TenantSecretCreateDto value)?  $default,){
final _that = this;
switch (_that) {
case _TenantSecretCreateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( SecretScope scope, @JsonKey(name: 'target_identifier')  String targetIdentifier, @JsonKey(name: 'plaintext_secret')  String plaintextSecret, @JsonKey(name: 'storage_mode')  SecretStorageMode storageMode)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TenantSecretCreateDto() when $default != null:
return $default(_that.scope,_that.targetIdentifier,_that.plaintextSecret,_that.storageMode);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( SecretScope scope, @JsonKey(name: 'target_identifier')  String targetIdentifier, @JsonKey(name: 'plaintext_secret')  String plaintextSecret, @JsonKey(name: 'storage_mode')  SecretStorageMode storageMode)  $default,) {final _that = this;
switch (_that) {
case _TenantSecretCreateDto():
return $default(_that.scope,_that.targetIdentifier,_that.plaintextSecret,_that.storageMode);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( SecretScope scope, @JsonKey(name: 'target_identifier')  String targetIdentifier, @JsonKey(name: 'plaintext_secret')  String plaintextSecret, @JsonKey(name: 'storage_mode')  SecretStorageMode storageMode)?  $default,) {final _that = this;
switch (_that) {
case _TenantSecretCreateDto() when $default != null:
return $default(_that.scope,_that.targetIdentifier,_that.plaintextSecret,_that.storageMode);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _TenantSecretCreateDto extends TenantSecretCreateDto {
  const _TenantSecretCreateDto({required this.scope, @JsonKey(name: 'target_identifier') required this.targetIdentifier, @JsonKey(name: 'plaintext_secret') required this.plaintextSecret, @JsonKey(name: 'storage_mode') required this.storageMode}): super._();
  factory _TenantSecretCreateDto.fromJson(Map<String, dynamic> json) => _$TenantSecretCreateDtoFromJson(json);

@override final  SecretScope scope;
@override@JsonKey(name: 'target_identifier') final  String targetIdentifier;
@override@JsonKey(name: 'plaintext_secret') final  String plaintextSecret;
// Phase 3, Step 3: Add required storageMode with zero default value (REQ-012)
@override@JsonKey(name: 'storage_mode') final  SecretStorageMode storageMode;

/// Create a copy of TenantSecretCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TenantSecretCreateDtoCopyWith<_TenantSecretCreateDto> get copyWith => __$TenantSecretCreateDtoCopyWithImpl<_TenantSecretCreateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TenantSecretCreateDtoToJson(this, );
}



@override
String toString() {
  return 'TenantSecretCreateDto(scope: $scope, targetIdentifier: $targetIdentifier, plaintextSecret: $plaintextSecret, storageMode: $storageMode)';
}


}

/// @nodoc
abstract mixin class _$TenantSecretCreateDtoCopyWith<$Res> implements $TenantSecretCreateDtoCopyWith<$Res> {
  factory _$TenantSecretCreateDtoCopyWith(_TenantSecretCreateDto value, $Res Function(_TenantSecretCreateDto) _then) = __$TenantSecretCreateDtoCopyWithImpl;
@override @useResult
$Res call({
 SecretScope scope,@JsonKey(name: 'target_identifier') String targetIdentifier,@JsonKey(name: 'plaintext_secret') String plaintextSecret,@JsonKey(name: 'storage_mode') SecretStorageMode storageMode
});




}
/// @nodoc
class __$TenantSecretCreateDtoCopyWithImpl<$Res>
    implements _$TenantSecretCreateDtoCopyWith<$Res> {
  __$TenantSecretCreateDtoCopyWithImpl(this._self, this._then);

  final _TenantSecretCreateDto _self;
  final $Res Function(_TenantSecretCreateDto) _then;

/// Create a copy of TenantSecretCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? scope = null,Object? targetIdentifier = null,Object? plaintextSecret = null,Object? storageMode = null,}) {
  return _then(_TenantSecretCreateDto(
scope: null == scope ? _self.scope : scope // ignore: cast_nullable_to_non_nullable
as SecretScope,targetIdentifier: null == targetIdentifier ? _self.targetIdentifier : targetIdentifier // ignore: cast_nullable_to_non_nullable
as String,plaintextSecret: null == plaintextSecret ? _self.plaintextSecret : plaintextSecret // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as SecretStorageMode,
  ));
}


}


/// @nodoc
mixin _$TenantSecretResponseDto {

@StrictOpaqueIdConverter() String get id;@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String get organizationId; SecretScope get scope;@JsonKey(name: 'target_identifier') String get targetIdentifier;@JsonKey(name: 'storage_mode') SecretStorageMode get storageMode; bool get configured;@JsonKey(name: 'masked_hint') String get maskedHint;@JsonKey(name: 'kek_version') String get kekVersion;@JsonKey(name: 'updated_at') DateTime get updatedAt;
/// Create a copy of TenantSecretResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TenantSecretResponseDtoCopyWith<TenantSecretResponseDto> get copyWith => _$TenantSecretResponseDtoCopyWithImpl<TenantSecretResponseDto>(this as TenantSecretResponseDto, _$identity);

  /// Serializes this TenantSecretResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TenantSecretResponseDto(id: $id, organizationId: $organizationId, scope: $scope, targetIdentifier: $targetIdentifier, storageMode: $storageMode, configured: $configured, maskedHint: $maskedHint, kekVersion: $kekVersion, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class $TenantSecretResponseDtoCopyWith<$Res>  {
  factory $TenantSecretResponseDtoCopyWith(TenantSecretResponseDto value, $Res Function(TenantSecretResponseDto) _then) = _$TenantSecretResponseDtoCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId, SecretScope scope,@JsonKey(name: 'target_identifier') String targetIdentifier,@JsonKey(name: 'storage_mode') SecretStorageMode storageMode, bool configured,@JsonKey(name: 'masked_hint') String maskedHint,@JsonKey(name: 'kek_version') String kekVersion,@JsonKey(name: 'updated_at') DateTime updatedAt
});




}
/// @nodoc
class _$TenantSecretResponseDtoCopyWithImpl<$Res>
    implements $TenantSecretResponseDtoCopyWith<$Res> {
  _$TenantSecretResponseDtoCopyWithImpl(this._self, this._then);

  final TenantSecretResponseDto _self;
  final $Res Function(TenantSecretResponseDto) _then;

/// Create a copy of TenantSecretResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? organizationId = null,Object? scope = null,Object? targetIdentifier = null,Object? storageMode = null,Object? configured = null,Object? maskedHint = null,Object? kekVersion = null,Object? updatedAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,scope: null == scope ? _self.scope : scope // ignore: cast_nullable_to_non_nullable
as SecretScope,targetIdentifier: null == targetIdentifier ? _self.targetIdentifier : targetIdentifier // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as SecretStorageMode,configured: null == configured ? _self.configured : configured // ignore: cast_nullable_to_non_nullable
as bool,maskedHint: null == maskedHint ? _self.maskedHint : maskedHint // ignore: cast_nullable_to_non_nullable
as String,kekVersion: null == kekVersion ? _self.kekVersion : kekVersion // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [TenantSecretResponseDto].
extension TenantSecretResponseDtoPatterns on TenantSecretResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TenantSecretResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TenantSecretResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TenantSecretResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _TenantSecretResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TenantSecretResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _TenantSecretResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  SecretScope scope, @JsonKey(name: 'target_identifier')  String targetIdentifier, @JsonKey(name: 'storage_mode')  SecretStorageMode storageMode,  bool configured, @JsonKey(name: 'masked_hint')  String maskedHint, @JsonKey(name: 'kek_version')  String kekVersion, @JsonKey(name: 'updated_at')  DateTime updatedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TenantSecretResponseDto() when $default != null:
return $default(_that.id,_that.organizationId,_that.scope,_that.targetIdentifier,_that.storageMode,_that.configured,_that.maskedHint,_that.kekVersion,_that.updatedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  SecretScope scope, @JsonKey(name: 'target_identifier')  String targetIdentifier, @JsonKey(name: 'storage_mode')  SecretStorageMode storageMode,  bool configured, @JsonKey(name: 'masked_hint')  String maskedHint, @JsonKey(name: 'kek_version')  String kekVersion, @JsonKey(name: 'updated_at')  DateTime updatedAt)  $default,) {final _that = this;
switch (_that) {
case _TenantSecretResponseDto():
return $default(_that.id,_that.organizationId,_that.scope,_that.targetIdentifier,_that.storageMode,_that.configured,_that.maskedHint,_that.kekVersion,_that.updatedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  SecretScope scope, @JsonKey(name: 'target_identifier')  String targetIdentifier, @JsonKey(name: 'storage_mode')  SecretStorageMode storageMode,  bool configured, @JsonKey(name: 'masked_hint')  String maskedHint, @JsonKey(name: 'kek_version')  String kekVersion, @JsonKey(name: 'updated_at')  DateTime updatedAt)?  $default,) {final _that = this;
switch (_that) {
case _TenantSecretResponseDto() when $default != null:
return $default(_that.id,_that.organizationId,_that.scope,_that.targetIdentifier,_that.storageMode,_that.configured,_that.maskedHint,_that.kekVersion,_that.updatedAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _TenantSecretResponseDto extends TenantSecretResponseDto {
  const _TenantSecretResponseDto({@StrictOpaqueIdConverter() required this.id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') required this.organizationId, required this.scope, @JsonKey(name: 'target_identifier') required this.targetIdentifier, @JsonKey(name: 'storage_mode') required this.storageMode, this.configured = true, @JsonKey(name: 'masked_hint') required this.maskedHint, @JsonKey(name: 'kek_version') required this.kekVersion, @JsonKey(name: 'updated_at') required this.updatedAt}): super._();
  factory _TenantSecretResponseDto.fromJson(Map<String, dynamic> json) => _$TenantSecretResponseDtoFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') final  String organizationId;
@override final  SecretScope scope;
@override@JsonKey(name: 'target_identifier') final  String targetIdentifier;
@override@JsonKey(name: 'storage_mode') final  SecretStorageMode storageMode;
@override@JsonKey() final  bool configured;
@override@JsonKey(name: 'masked_hint') final  String maskedHint;
@override@JsonKey(name: 'kek_version') final  String kekVersion;
@override@JsonKey(name: 'updated_at') final  DateTime updatedAt;

/// Create a copy of TenantSecretResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TenantSecretResponseDtoCopyWith<_TenantSecretResponseDto> get copyWith => __$TenantSecretResponseDtoCopyWithImpl<_TenantSecretResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TenantSecretResponseDtoToJson(this, );
}



@override
String toString() {
  return 'TenantSecretResponseDto(id: $id, organizationId: $organizationId, scope: $scope, targetIdentifier: $targetIdentifier, storageMode: $storageMode, configured: $configured, maskedHint: $maskedHint, kekVersion: $kekVersion, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class _$TenantSecretResponseDtoCopyWith<$Res> implements $TenantSecretResponseDtoCopyWith<$Res> {
  factory _$TenantSecretResponseDtoCopyWith(_TenantSecretResponseDto value, $Res Function(_TenantSecretResponseDto) _then) = __$TenantSecretResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId, SecretScope scope,@JsonKey(name: 'target_identifier') String targetIdentifier,@JsonKey(name: 'storage_mode') SecretStorageMode storageMode, bool configured,@JsonKey(name: 'masked_hint') String maskedHint,@JsonKey(name: 'kek_version') String kekVersion,@JsonKey(name: 'updated_at') DateTime updatedAt
});




}
/// @nodoc
class __$TenantSecretResponseDtoCopyWithImpl<$Res>
    implements _$TenantSecretResponseDtoCopyWith<$Res> {
  __$TenantSecretResponseDtoCopyWithImpl(this._self, this._then);

  final _TenantSecretResponseDto _self;
  final $Res Function(_TenantSecretResponseDto) _then;

/// Create a copy of TenantSecretResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? organizationId = null,Object? scope = null,Object? targetIdentifier = null,Object? storageMode = null,Object? configured = null,Object? maskedHint = null,Object? kekVersion = null,Object? updatedAt = null,}) {
  return _then(_TenantSecretResponseDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,scope: null == scope ? _self.scope : scope // ignore: cast_nullable_to_non_nullable
as SecretScope,targetIdentifier: null == targetIdentifier ? _self.targetIdentifier : targetIdentifier // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as SecretStorageMode,configured: null == configured ? _self.configured : configured // ignore: cast_nullable_to_non_nullable
as bool,maskedHint: null == maskedHint ? _self.maskedHint : maskedHint // ignore: cast_nullable_to_non_nullable
as String,kekVersion: null == kekVersion ? _self.kekVersion : kekVersion // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$ExecutionAssignmentCreateDto {

@JsonKey(name: 'assigned_email') String get assignedEmail;@JsonKey(name: 'invited_role') UserRole get invitedRole;@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'output_profile_id') String? get outputProfileId;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'locked_inputs') WorkflowInputs get lockedInputs;@JsonKey(name: 'assignee_input_keys') List<String> get assigneeInputKeys;@JsonKey(name: 'result_visibility') AssignmentResultVisibility get resultVisibility;@JsonKey(name: 'hard_deadline_at') DateTime get hardDeadlineAt;@JsonKey(name: 'relative_duration_seconds') int? get relativeDurationSeconds;
/// Create a copy of ExecutionAssignmentCreateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentCreateDtoCopyWith<ExecutionAssignmentCreateDto> get copyWith => _$ExecutionAssignmentCreateDtoCopyWithImpl<ExecutionAssignmentCreateDto>(this as ExecutionAssignmentCreateDto, _$identity);

  /// Serializes this ExecutionAssignmentCreateDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentCreateDto(assignedEmail: $assignedEmail, invitedRole: $invitedRole, workflowId: $workflowId, outputProfileId: $outputProfileId, targetLocale: $targetLocale, lockedInputs: $lockedInputs, assigneeInputKeys: $assigneeInputKeys, resultVisibility: $resultVisibility, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentCreateDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentCreateDtoCopyWith(ExecutionAssignmentCreateDto value, $Res Function(ExecutionAssignmentCreateDto) _then) = _$ExecutionAssignmentCreateDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'assigned_email') String assignedEmail,@JsonKey(name: 'invited_role') UserRole invitedRole,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'locked_inputs') WorkflowInputs lockedInputs,@JsonKey(name: 'assignee_input_keys') List<String> assigneeInputKeys,@JsonKey(name: 'result_visibility') AssignmentResultVisibility resultVisibility,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds
});


$WorkflowInputsCopyWith<$Res> get lockedInputs;

}
/// @nodoc
class _$ExecutionAssignmentCreateDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentCreateDtoCopyWith<$Res> {
  _$ExecutionAssignmentCreateDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentCreateDto _self;
  final $Res Function(ExecutionAssignmentCreateDto) _then;

/// Create a copy of ExecutionAssignmentCreateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? assignedEmail = null,Object? invitedRole = null,Object? workflowId = null,Object? outputProfileId = freezed,Object? targetLocale = null,Object? lockedInputs = null,Object? assigneeInputKeys = null,Object? resultVisibility = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,}) {
  return _then(_self.copyWith(
assignedEmail: null == assignedEmail ? _self.assignedEmail : assignedEmail // ignore: cast_nullable_to_non_nullable
as String,invitedRole: null == invitedRole ? _self.invitedRole : invitedRole // ignore: cast_nullable_to_non_nullable
as UserRole,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,lockedInputs: null == lockedInputs ? _self.lockedInputs : lockedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,assigneeInputKeys: null == assigneeInputKeys ? _self.assigneeInputKeys : assigneeInputKeys // ignore: cast_nullable_to_non_nullable
as List<String>,resultVisibility: null == resultVisibility ? _self.resultVisibility : resultVisibility // ignore: cast_nullable_to_non_nullable
as AssignmentResultVisibility,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}
/// Create a copy of ExecutionAssignmentCreateDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get lockedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.lockedInputs, (value) {
    return _then(_self.copyWith(lockedInputs: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionAssignmentCreateDto].
extension ExecutionAssignmentCreateDtoPatterns on ExecutionAssignmentCreateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentCreateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentCreateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentCreateDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentCreateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentCreateDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentCreateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'assigned_email')  String assignedEmail, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentCreateDto() when $default != null:
return $default(_that.assignedEmail,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'assigned_email')  String assignedEmail, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentCreateDto():
return $default(_that.assignedEmail,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'assigned_email')  String assignedEmail, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentCreateDto() when $default != null:
return $default(_that.assignedEmail,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, includeIfNull: false)
class _ExecutionAssignmentCreateDto extends ExecutionAssignmentCreateDto {
  const _ExecutionAssignmentCreateDto({@JsonKey(name: 'assigned_email') required this.assignedEmail, @JsonKey(name: 'invited_role') this.invitedRole = UserRole.member, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'output_profile_id') this.outputProfileId, @JsonKey(name: 'target_locale') this.targetLocale = 'fi', @JsonKey(name: 'locked_inputs') required this.lockedInputs, @JsonKey(name: 'assignee_input_keys') final  List<String> assigneeInputKeys = const [], @JsonKey(name: 'result_visibility') this.resultVisibility = AssignmentResultVisibility.confirmationOnly, @JsonKey(name: 'hard_deadline_at') required this.hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds') this.relativeDurationSeconds}): _assigneeInputKeys = assigneeInputKeys,super._();
  factory _ExecutionAssignmentCreateDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentCreateDtoFromJson(json);

@override@JsonKey(name: 'assigned_email') final  String assignedEmail;
@override@JsonKey(name: 'invited_role') final  UserRole invitedRole;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'output_profile_id') final  String? outputProfileId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(name: 'locked_inputs') final  WorkflowInputs lockedInputs;
 final  List<String> _assigneeInputKeys;
@override@JsonKey(name: 'assignee_input_keys') List<String> get assigneeInputKeys {
  if (_assigneeInputKeys is EqualUnmodifiableListView) return _assigneeInputKeys;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_assigneeInputKeys);
}

@override@JsonKey(name: 'result_visibility') final  AssignmentResultVisibility resultVisibility;
@override@JsonKey(name: 'hard_deadline_at') final  DateTime hardDeadlineAt;
@override@JsonKey(name: 'relative_duration_seconds') final  int? relativeDurationSeconds;

/// Create a copy of ExecutionAssignmentCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentCreateDtoCopyWith<_ExecutionAssignmentCreateDto> get copyWith => __$ExecutionAssignmentCreateDtoCopyWithImpl<_ExecutionAssignmentCreateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentCreateDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentCreateDto(assignedEmail: $assignedEmail, invitedRole: $invitedRole, workflowId: $workflowId, outputProfileId: $outputProfileId, targetLocale: $targetLocale, lockedInputs: $lockedInputs, assigneeInputKeys: $assigneeInputKeys, resultVisibility: $resultVisibility, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentCreateDtoCopyWith<$Res> implements $ExecutionAssignmentCreateDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentCreateDtoCopyWith(_ExecutionAssignmentCreateDto value, $Res Function(_ExecutionAssignmentCreateDto) _then) = __$ExecutionAssignmentCreateDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'assigned_email') String assignedEmail,@JsonKey(name: 'invited_role') UserRole invitedRole,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'locked_inputs') WorkflowInputs lockedInputs,@JsonKey(name: 'assignee_input_keys') List<String> assigneeInputKeys,@JsonKey(name: 'result_visibility') AssignmentResultVisibility resultVisibility,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds
});


@override $WorkflowInputsCopyWith<$Res> get lockedInputs;

}
/// @nodoc
class __$ExecutionAssignmentCreateDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentCreateDtoCopyWith<$Res> {
  __$ExecutionAssignmentCreateDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentCreateDto _self;
  final $Res Function(_ExecutionAssignmentCreateDto) _then;

/// Create a copy of ExecutionAssignmentCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? assignedEmail = null,Object? invitedRole = null,Object? workflowId = null,Object? outputProfileId = freezed,Object? targetLocale = null,Object? lockedInputs = null,Object? assigneeInputKeys = null,Object? resultVisibility = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,}) {
  return _then(_ExecutionAssignmentCreateDto(
assignedEmail: null == assignedEmail ? _self.assignedEmail : assignedEmail // ignore: cast_nullable_to_non_nullable
as String,invitedRole: null == invitedRole ? _self.invitedRole : invitedRole // ignore: cast_nullable_to_non_nullable
as UserRole,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,lockedInputs: null == lockedInputs ? _self.lockedInputs : lockedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,assigneeInputKeys: null == assigneeInputKeys ? _self._assigneeInputKeys : assigneeInputKeys // ignore: cast_nullable_to_non_nullable
as List<String>,resultVisibility: null == resultVisibility ? _self.resultVisibility : resultVisibility // ignore: cast_nullable_to_non_nullable
as AssignmentResultVisibility,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

/// Create a copy of ExecutionAssignmentCreateDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get lockedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.lockedInputs, (value) {
    return _then(_self.copyWith(lockedInputs: value));
  });
}
}


/// @nodoc
mixin _$ExecutionAssignmentRecipientDto {

 String get email; String? get name;@JsonKey(name: 'target_locale') String? get targetLocale;
/// Create a copy of ExecutionAssignmentRecipientDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentRecipientDtoCopyWith<ExecutionAssignmentRecipientDto> get copyWith => _$ExecutionAssignmentRecipientDtoCopyWithImpl<ExecutionAssignmentRecipientDto>(this as ExecutionAssignmentRecipientDto, _$identity);

  /// Serializes this ExecutionAssignmentRecipientDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentRecipientDto(email: $email, name: $name, targetLocale: $targetLocale)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentRecipientDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentRecipientDtoCopyWith(ExecutionAssignmentRecipientDto value, $Res Function(ExecutionAssignmentRecipientDto) _then) = _$ExecutionAssignmentRecipientDtoCopyWithImpl;
@useResult
$Res call({
 String email, String? name,@JsonKey(name: 'target_locale') String? targetLocale
});




}
/// @nodoc
class _$ExecutionAssignmentRecipientDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentRecipientDtoCopyWith<$Res> {
  _$ExecutionAssignmentRecipientDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentRecipientDto _self;
  final $Res Function(ExecutionAssignmentRecipientDto) _then;

/// Create a copy of ExecutionAssignmentRecipientDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? email = null,Object? name = freezed,Object? targetLocale = freezed,}) {
  return _then(_self.copyWith(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: freezed == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionAssignmentRecipientDto].
extension ExecutionAssignmentRecipientDtoPatterns on ExecutionAssignmentRecipientDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentRecipientDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentRecipientDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentRecipientDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentRecipientDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentRecipientDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentRecipientDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String email,  String? name, @JsonKey(name: 'target_locale')  String? targetLocale)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentRecipientDto() when $default != null:
return $default(_that.email,_that.name,_that.targetLocale);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String email,  String? name, @JsonKey(name: 'target_locale')  String? targetLocale)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentRecipientDto():
return $default(_that.email,_that.name,_that.targetLocale);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String email,  String? name, @JsonKey(name: 'target_locale')  String? targetLocale)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentRecipientDto() when $default != null:
return $default(_that.email,_that.name,_that.targetLocale);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, includeIfNull: false)
class _ExecutionAssignmentRecipientDto extends ExecutionAssignmentRecipientDto {
  const _ExecutionAssignmentRecipientDto({required this.email, this.name, @JsonKey(name: 'target_locale') this.targetLocale}): super._();
  factory _ExecutionAssignmentRecipientDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentRecipientDtoFromJson(json);

@override final  String email;
@override final  String? name;
@override@JsonKey(name: 'target_locale') final  String? targetLocale;

/// Create a copy of ExecutionAssignmentRecipientDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentRecipientDtoCopyWith<_ExecutionAssignmentRecipientDto> get copyWith => __$ExecutionAssignmentRecipientDtoCopyWithImpl<_ExecutionAssignmentRecipientDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentRecipientDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentRecipientDto(email: $email, name: $name, targetLocale: $targetLocale)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentRecipientDtoCopyWith<$Res> implements $ExecutionAssignmentRecipientDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentRecipientDtoCopyWith(_ExecutionAssignmentRecipientDto value, $Res Function(_ExecutionAssignmentRecipientDto) _then) = __$ExecutionAssignmentRecipientDtoCopyWithImpl;
@override @useResult
$Res call({
 String email, String? name,@JsonKey(name: 'target_locale') String? targetLocale
});




}
/// @nodoc
class __$ExecutionAssignmentRecipientDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentRecipientDtoCopyWith<$Res> {
  __$ExecutionAssignmentRecipientDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentRecipientDto _self;
  final $Res Function(_ExecutionAssignmentRecipientDto) _then;

/// Create a copy of ExecutionAssignmentRecipientDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? email = null,Object? name = freezed,Object? targetLocale = freezed,}) {
  return _then(_ExecutionAssignmentRecipientDto(
email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: freezed == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ExecutionAssignmentBatchCreateDto {

 List<ExecutionAssignmentRecipientDto> get recipients;@JsonKey(name: 'invited_role') UserRole get invitedRole;@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'output_profile_id') String? get outputProfileId;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'locked_inputs') WorkflowInputs get lockedInputs;@JsonKey(name: 'assignee_input_keys') List<String> get assigneeInputKeys;@JsonKey(name: 'result_visibility') AssignmentResultVisibility get resultVisibility;@JsonKey(name: 'hard_deadline_at') DateTime get hardDeadlineAt;@JsonKey(name: 'relative_duration_seconds') int? get relativeDurationSeconds;
/// Create a copy of ExecutionAssignmentBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentBatchCreateDtoCopyWith<ExecutionAssignmentBatchCreateDto> get copyWith => _$ExecutionAssignmentBatchCreateDtoCopyWithImpl<ExecutionAssignmentBatchCreateDto>(this as ExecutionAssignmentBatchCreateDto, _$identity);

  /// Serializes this ExecutionAssignmentBatchCreateDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentBatchCreateDto(recipients: $recipients, invitedRole: $invitedRole, workflowId: $workflowId, outputProfileId: $outputProfileId, targetLocale: $targetLocale, lockedInputs: $lockedInputs, assigneeInputKeys: $assigneeInputKeys, resultVisibility: $resultVisibility, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentBatchCreateDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentBatchCreateDtoCopyWith(ExecutionAssignmentBatchCreateDto value, $Res Function(ExecutionAssignmentBatchCreateDto) _then) = _$ExecutionAssignmentBatchCreateDtoCopyWithImpl;
@useResult
$Res call({
 List<ExecutionAssignmentRecipientDto> recipients,@JsonKey(name: 'invited_role') UserRole invitedRole,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'locked_inputs') WorkflowInputs lockedInputs,@JsonKey(name: 'assignee_input_keys') List<String> assigneeInputKeys,@JsonKey(name: 'result_visibility') AssignmentResultVisibility resultVisibility,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds
});


$WorkflowInputsCopyWith<$Res> get lockedInputs;

}
/// @nodoc
class _$ExecutionAssignmentBatchCreateDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentBatchCreateDtoCopyWith<$Res> {
  _$ExecutionAssignmentBatchCreateDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentBatchCreateDto _self;
  final $Res Function(ExecutionAssignmentBatchCreateDto) _then;

/// Create a copy of ExecutionAssignmentBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipients = null,Object? invitedRole = null,Object? workflowId = null,Object? outputProfileId = freezed,Object? targetLocale = null,Object? lockedInputs = null,Object? assigneeInputKeys = null,Object? resultVisibility = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,}) {
  return _then(_self.copyWith(
recipients: null == recipients ? _self.recipients : recipients // ignore: cast_nullable_to_non_nullable
as List<ExecutionAssignmentRecipientDto>,invitedRole: null == invitedRole ? _self.invitedRole : invitedRole // ignore: cast_nullable_to_non_nullable
as UserRole,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,lockedInputs: null == lockedInputs ? _self.lockedInputs : lockedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,assigneeInputKeys: null == assigneeInputKeys ? _self.assigneeInputKeys : assigneeInputKeys // ignore: cast_nullable_to_non_nullable
as List<String>,resultVisibility: null == resultVisibility ? _self.resultVisibility : resultVisibility // ignore: cast_nullable_to_non_nullable
as AssignmentResultVisibility,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}
/// Create a copy of ExecutionAssignmentBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get lockedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.lockedInputs, (value) {
    return _then(_self.copyWith(lockedInputs: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionAssignmentBatchCreateDto].
extension ExecutionAssignmentBatchCreateDtoPatterns on ExecutionAssignmentBatchCreateDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentBatchCreateDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchCreateDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentBatchCreateDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchCreateDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentBatchCreateDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchCreateDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<ExecutionAssignmentRecipientDto> recipients, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchCreateDto() when $default != null:
return $default(_that.recipients,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<ExecutionAssignmentRecipientDto> recipients, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchCreateDto():
return $default(_that.recipients,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<ExecutionAssignmentRecipientDto> recipients, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchCreateDto() when $default != null:
return $default(_that.recipients,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, includeIfNull: false)
class _ExecutionAssignmentBatchCreateDto extends ExecutionAssignmentBatchCreateDto {
  const _ExecutionAssignmentBatchCreateDto({required final  List<ExecutionAssignmentRecipientDto> recipients, @JsonKey(name: 'invited_role') this.invitedRole = UserRole.member, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'output_profile_id') this.outputProfileId, @JsonKey(name: 'target_locale') this.targetLocale = 'fi', @JsonKey(name: 'locked_inputs') required this.lockedInputs, @JsonKey(name: 'assignee_input_keys') final  List<String> assigneeInputKeys = const [], @JsonKey(name: 'result_visibility') this.resultVisibility = AssignmentResultVisibility.confirmationOnly, @JsonKey(name: 'hard_deadline_at') required this.hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds') this.relativeDurationSeconds}): _recipients = recipients,_assigneeInputKeys = assigneeInputKeys,super._();
  factory _ExecutionAssignmentBatchCreateDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentBatchCreateDtoFromJson(json);

 final  List<ExecutionAssignmentRecipientDto> _recipients;
@override List<ExecutionAssignmentRecipientDto> get recipients {
  if (_recipients is EqualUnmodifiableListView) return _recipients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recipients);
}

@override@JsonKey(name: 'invited_role') final  UserRole invitedRole;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'output_profile_id') final  String? outputProfileId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(name: 'locked_inputs') final  WorkflowInputs lockedInputs;
 final  List<String> _assigneeInputKeys;
@override@JsonKey(name: 'assignee_input_keys') List<String> get assigneeInputKeys {
  if (_assigneeInputKeys is EqualUnmodifiableListView) return _assigneeInputKeys;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_assigneeInputKeys);
}

@override@JsonKey(name: 'result_visibility') final  AssignmentResultVisibility resultVisibility;
@override@JsonKey(name: 'hard_deadline_at') final  DateTime hardDeadlineAt;
@override@JsonKey(name: 'relative_duration_seconds') final  int? relativeDurationSeconds;

/// Create a copy of ExecutionAssignmentBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentBatchCreateDtoCopyWith<_ExecutionAssignmentBatchCreateDto> get copyWith => __$ExecutionAssignmentBatchCreateDtoCopyWithImpl<_ExecutionAssignmentBatchCreateDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentBatchCreateDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentBatchCreateDto(recipients: $recipients, invitedRole: $invitedRole, workflowId: $workflowId, outputProfileId: $outputProfileId, targetLocale: $targetLocale, lockedInputs: $lockedInputs, assigneeInputKeys: $assigneeInputKeys, resultVisibility: $resultVisibility, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentBatchCreateDtoCopyWith<$Res> implements $ExecutionAssignmentBatchCreateDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentBatchCreateDtoCopyWith(_ExecutionAssignmentBatchCreateDto value, $Res Function(_ExecutionAssignmentBatchCreateDto) _then) = __$ExecutionAssignmentBatchCreateDtoCopyWithImpl;
@override @useResult
$Res call({
 List<ExecutionAssignmentRecipientDto> recipients,@JsonKey(name: 'invited_role') UserRole invitedRole,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'locked_inputs') WorkflowInputs lockedInputs,@JsonKey(name: 'assignee_input_keys') List<String> assigneeInputKeys,@JsonKey(name: 'result_visibility') AssignmentResultVisibility resultVisibility,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds
});


@override $WorkflowInputsCopyWith<$Res> get lockedInputs;

}
/// @nodoc
class __$ExecutionAssignmentBatchCreateDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentBatchCreateDtoCopyWith<$Res> {
  __$ExecutionAssignmentBatchCreateDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentBatchCreateDto _self;
  final $Res Function(_ExecutionAssignmentBatchCreateDto) _then;

/// Create a copy of ExecutionAssignmentBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipients = null,Object? invitedRole = null,Object? workflowId = null,Object? outputProfileId = freezed,Object? targetLocale = null,Object? lockedInputs = null,Object? assigneeInputKeys = null,Object? resultVisibility = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,}) {
  return _then(_ExecutionAssignmentBatchCreateDto(
recipients: null == recipients ? _self._recipients : recipients // ignore: cast_nullable_to_non_nullable
as List<ExecutionAssignmentRecipientDto>,invitedRole: null == invitedRole ? _self.invitedRole : invitedRole // ignore: cast_nullable_to_non_nullable
as UserRole,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,lockedInputs: null == lockedInputs ? _self.lockedInputs : lockedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,assigneeInputKeys: null == assigneeInputKeys ? _self._assigneeInputKeys : assigneeInputKeys // ignore: cast_nullable_to_non_nullable
as List<String>,resultVisibility: null == resultVisibility ? _self.resultVisibility : resultVisibility // ignore: cast_nullable_to_non_nullable
as AssignmentResultVisibility,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

/// Create a copy of ExecutionAssignmentBatchCreateDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get lockedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.lockedInputs, (value) {
    return _then(_self.copyWith(lockedInputs: value));
  });
}
}


/// @nodoc
mixin _$ExecutionAssignmentResponseDto {

@StrictOpaqueIdConverter() String get id;@JsonKey(name: 'batch_id') String? get batchId;@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String get organizationId;@JsonKey(name: 'assigned_email') String get assignedEmail;@JsonKey(name: 'assigned_user_id') String? get assignedUserId;@JsonKey(name: 'invited_role') UserRole get invitedRole;@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'output_profile_id') String? get outputProfileId;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'locked_inputs') WorkflowInputs get lockedInputs;@JsonKey(name: 'assignee_input_keys') List<String> get assigneeInputKeys;@JsonKey(name: 'draft_inputs') WorkflowInputs get draftInputs; AssignmentStatus get status;@JsonKey(name: 'email_delivery_status') EmailDeliveryStatus get emailDeliveryStatus;@JsonKey(name: 'result_visibility') AssignmentResultVisibility get resultVisibility;@JsonKey(name: 'hard_deadline_at') DateTime get hardDeadlineAt;@JsonKey(name: 'relative_duration_seconds') int? get relativeDurationSeconds;@JsonKey(name: 'activated_at') DateTime? get activatedAt;@JsonKey(name: 'submitted_at') DateTime? get submittedAt;@JsonKey(name: 'execution_id') String? get executionId;@StrictOpaqueIdConverter()@JsonKey(name: 'created_by') String get createdBy;@JsonKey(name: 'created_at') DateTime get createdAt;
/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentResponseDtoCopyWith<ExecutionAssignmentResponseDto> get copyWith => _$ExecutionAssignmentResponseDtoCopyWithImpl<ExecutionAssignmentResponseDto>(this as ExecutionAssignmentResponseDto, _$identity);

  /// Serializes this ExecutionAssignmentResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentResponseDto(id: $id, batchId: $batchId, organizationId: $organizationId, assignedEmail: $assignedEmail, assignedUserId: $assignedUserId, invitedRole: $invitedRole, workflowId: $workflowId, outputProfileId: $outputProfileId, targetLocale: $targetLocale, lockedInputs: $lockedInputs, assigneeInputKeys: $assigneeInputKeys, draftInputs: $draftInputs, status: $status, emailDeliveryStatus: $emailDeliveryStatus, resultVisibility: $resultVisibility, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds, activatedAt: $activatedAt, submittedAt: $submittedAt, executionId: $executionId, createdBy: $createdBy, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentResponseDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentResponseDtoCopyWith(ExecutionAssignmentResponseDto value, $Res Function(ExecutionAssignmentResponseDto) _then) = _$ExecutionAssignmentResponseDtoCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id,@JsonKey(name: 'batch_id') String? batchId,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId,@JsonKey(name: 'assigned_email') String assignedEmail,@JsonKey(name: 'assigned_user_id') String? assignedUserId,@JsonKey(name: 'invited_role') UserRole invitedRole,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'locked_inputs') WorkflowInputs lockedInputs,@JsonKey(name: 'assignee_input_keys') List<String> assigneeInputKeys,@JsonKey(name: 'draft_inputs') WorkflowInputs draftInputs, AssignmentStatus status,@JsonKey(name: 'email_delivery_status') EmailDeliveryStatus emailDeliveryStatus,@JsonKey(name: 'result_visibility') AssignmentResultVisibility resultVisibility,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds,@JsonKey(name: 'activated_at') DateTime? activatedAt,@JsonKey(name: 'submitted_at') DateTime? submittedAt,@JsonKey(name: 'execution_id') String? executionId,@StrictOpaqueIdConverter()@JsonKey(name: 'created_by') String createdBy,@JsonKey(name: 'created_at') DateTime createdAt
});


$WorkflowInputsCopyWith<$Res> get lockedInputs;$WorkflowInputsCopyWith<$Res> get draftInputs;

}
/// @nodoc
class _$ExecutionAssignmentResponseDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentResponseDtoCopyWith<$Res> {
  _$ExecutionAssignmentResponseDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentResponseDto _self;
  final $Res Function(ExecutionAssignmentResponseDto) _then;

/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? batchId = freezed,Object? organizationId = null,Object? assignedEmail = null,Object? assignedUserId = freezed,Object? invitedRole = null,Object? workflowId = null,Object? outputProfileId = freezed,Object? targetLocale = null,Object? lockedInputs = null,Object? assigneeInputKeys = null,Object? draftInputs = null,Object? status = null,Object? emailDeliveryStatus = null,Object? resultVisibility = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,Object? activatedAt = freezed,Object? submittedAt = freezed,Object? executionId = freezed,Object? createdBy = null,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,batchId: freezed == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String?,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,assignedEmail: null == assignedEmail ? _self.assignedEmail : assignedEmail // ignore: cast_nullable_to_non_nullable
as String,assignedUserId: freezed == assignedUserId ? _self.assignedUserId : assignedUserId // ignore: cast_nullable_to_non_nullable
as String?,invitedRole: null == invitedRole ? _self.invitedRole : invitedRole // ignore: cast_nullable_to_non_nullable
as UserRole,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,lockedInputs: null == lockedInputs ? _self.lockedInputs : lockedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,assigneeInputKeys: null == assigneeInputKeys ? _self.assigneeInputKeys : assigneeInputKeys // ignore: cast_nullable_to_non_nullable
as List<String>,draftInputs: null == draftInputs ? _self.draftInputs : draftInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as AssignmentStatus,emailDeliveryStatus: null == emailDeliveryStatus ? _self.emailDeliveryStatus : emailDeliveryStatus // ignore: cast_nullable_to_non_nullable
as EmailDeliveryStatus,resultVisibility: null == resultVisibility ? _self.resultVisibility : resultVisibility // ignore: cast_nullable_to_non_nullable
as AssignmentResultVisibility,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,activatedAt: freezed == activatedAt ? _self.activatedAt : activatedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,submittedAt: freezed == submittedAt ? _self.submittedAt : submittedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,executionId: freezed == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String?,createdBy: null == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}
/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get lockedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.lockedInputs, (value) {
    return _then(_self.copyWith(lockedInputs: value));
  });
}/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get draftInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.draftInputs, (value) {
    return _then(_self.copyWith(draftInputs: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionAssignmentResponseDto].
extension ExecutionAssignmentResponseDtoPatterns on ExecutionAssignmentResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @JsonKey(name: 'batch_id')  String? batchId, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'assigned_email')  String assignedEmail, @JsonKey(name: 'assigned_user_id')  String? assignedUserId, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'draft_inputs')  WorkflowInputs draftInputs,  AssignmentStatus status, @JsonKey(name: 'email_delivery_status')  EmailDeliveryStatus emailDeliveryStatus, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds, @JsonKey(name: 'activated_at')  DateTime? activatedAt, @JsonKey(name: 'submitted_at')  DateTime? submittedAt, @JsonKey(name: 'execution_id')  String? executionId, @StrictOpaqueIdConverter()@JsonKey(name: 'created_by')  String createdBy, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentResponseDto() when $default != null:
return $default(_that.id,_that.batchId,_that.organizationId,_that.assignedEmail,_that.assignedUserId,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.draftInputs,_that.status,_that.emailDeliveryStatus,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds,_that.activatedAt,_that.submittedAt,_that.executionId,_that.createdBy,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @JsonKey(name: 'batch_id')  String? batchId, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'assigned_email')  String assignedEmail, @JsonKey(name: 'assigned_user_id')  String? assignedUserId, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'draft_inputs')  WorkflowInputs draftInputs,  AssignmentStatus status, @JsonKey(name: 'email_delivery_status')  EmailDeliveryStatus emailDeliveryStatus, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds, @JsonKey(name: 'activated_at')  DateTime? activatedAt, @JsonKey(name: 'submitted_at')  DateTime? submittedAt, @JsonKey(name: 'execution_id')  String? executionId, @StrictOpaqueIdConverter()@JsonKey(name: 'created_by')  String createdBy, @JsonKey(name: 'created_at')  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentResponseDto():
return $default(_that.id,_that.batchId,_that.organizationId,_that.assignedEmail,_that.assignedUserId,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.draftInputs,_that.status,_that.emailDeliveryStatus,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds,_that.activatedAt,_that.submittedAt,_that.executionId,_that.createdBy,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id, @JsonKey(name: 'batch_id')  String? batchId, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'assigned_email')  String assignedEmail, @JsonKey(name: 'assigned_user_id')  String? assignedUserId, @JsonKey(name: 'invited_role')  UserRole invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'locked_inputs')  WorkflowInputs lockedInputs, @JsonKey(name: 'assignee_input_keys')  List<String> assigneeInputKeys, @JsonKey(name: 'draft_inputs')  WorkflowInputs draftInputs,  AssignmentStatus status, @JsonKey(name: 'email_delivery_status')  EmailDeliveryStatus emailDeliveryStatus, @JsonKey(name: 'result_visibility')  AssignmentResultVisibility resultVisibility, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds, @JsonKey(name: 'activated_at')  DateTime? activatedAt, @JsonKey(name: 'submitted_at')  DateTime? submittedAt, @JsonKey(name: 'execution_id')  String? executionId, @StrictOpaqueIdConverter()@JsonKey(name: 'created_by')  String createdBy, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentResponseDto() when $default != null:
return $default(_that.id,_that.batchId,_that.organizationId,_that.assignedEmail,_that.assignedUserId,_that.invitedRole,_that.workflowId,_that.outputProfileId,_that.targetLocale,_that.lockedInputs,_that.assigneeInputKeys,_that.draftInputs,_that.status,_that.emailDeliveryStatus,_that.resultVisibility,_that.hardDeadlineAt,_that.relativeDurationSeconds,_that.activatedAt,_that.submittedAt,_that.executionId,_that.createdBy,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionAssignmentResponseDto extends ExecutionAssignmentResponseDto {
  const _ExecutionAssignmentResponseDto({@StrictOpaqueIdConverter() required this.id, @JsonKey(name: 'batch_id') this.batchId, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') required this.organizationId, @JsonKey(name: 'assigned_email') required this.assignedEmail, @JsonKey(name: 'assigned_user_id') this.assignedUserId, @JsonKey(name: 'invited_role') required this.invitedRole, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'output_profile_id') this.outputProfileId, @JsonKey(name: 'target_locale') required this.targetLocale, @JsonKey(name: 'locked_inputs') required this.lockedInputs, @JsonKey(name: 'assignee_input_keys') required final  List<String> assigneeInputKeys, @JsonKey(name: 'draft_inputs') required this.draftInputs, required this.status, @JsonKey(name: 'email_delivery_status') this.emailDeliveryStatus = EmailDeliveryStatus.pending, @JsonKey(name: 'result_visibility') required this.resultVisibility, @JsonKey(name: 'hard_deadline_at') required this.hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds') this.relativeDurationSeconds, @JsonKey(name: 'activated_at') this.activatedAt, @JsonKey(name: 'submitted_at') this.submittedAt, @JsonKey(name: 'execution_id') this.executionId, @StrictOpaqueIdConverter()@JsonKey(name: 'created_by') required this.createdBy, @JsonKey(name: 'created_at') required this.createdAt}): _assigneeInputKeys = assigneeInputKeys,super._();
  factory _ExecutionAssignmentResponseDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentResponseDtoFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@JsonKey(name: 'batch_id') final  String? batchId;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') final  String organizationId;
@override@JsonKey(name: 'assigned_email') final  String assignedEmail;
@override@JsonKey(name: 'assigned_user_id') final  String? assignedUserId;
@override@JsonKey(name: 'invited_role') final  UserRole invitedRole;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'output_profile_id') final  String? outputProfileId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(name: 'locked_inputs') final  WorkflowInputs lockedInputs;
 final  List<String> _assigneeInputKeys;
@override@JsonKey(name: 'assignee_input_keys') List<String> get assigneeInputKeys {
  if (_assigneeInputKeys is EqualUnmodifiableListView) return _assigneeInputKeys;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_assigneeInputKeys);
}

@override@JsonKey(name: 'draft_inputs') final  WorkflowInputs draftInputs;
@override final  AssignmentStatus status;
@override@JsonKey(name: 'email_delivery_status') final  EmailDeliveryStatus emailDeliveryStatus;
@override@JsonKey(name: 'result_visibility') final  AssignmentResultVisibility resultVisibility;
@override@JsonKey(name: 'hard_deadline_at') final  DateTime hardDeadlineAt;
@override@JsonKey(name: 'relative_duration_seconds') final  int? relativeDurationSeconds;
@override@JsonKey(name: 'activated_at') final  DateTime? activatedAt;
@override@JsonKey(name: 'submitted_at') final  DateTime? submittedAt;
@override@JsonKey(name: 'execution_id') final  String? executionId;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'created_by') final  String createdBy;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;

/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentResponseDtoCopyWith<_ExecutionAssignmentResponseDto> get copyWith => __$ExecutionAssignmentResponseDtoCopyWithImpl<_ExecutionAssignmentResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentResponseDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentResponseDto(id: $id, batchId: $batchId, organizationId: $organizationId, assignedEmail: $assignedEmail, assignedUserId: $assignedUserId, invitedRole: $invitedRole, workflowId: $workflowId, outputProfileId: $outputProfileId, targetLocale: $targetLocale, lockedInputs: $lockedInputs, assigneeInputKeys: $assigneeInputKeys, draftInputs: $draftInputs, status: $status, emailDeliveryStatus: $emailDeliveryStatus, resultVisibility: $resultVisibility, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds, activatedAt: $activatedAt, submittedAt: $submittedAt, executionId: $executionId, createdBy: $createdBy, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentResponseDtoCopyWith<$Res> implements $ExecutionAssignmentResponseDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentResponseDtoCopyWith(_ExecutionAssignmentResponseDto value, $Res Function(_ExecutionAssignmentResponseDto) _then) = __$ExecutionAssignmentResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id,@JsonKey(name: 'batch_id') String? batchId,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId,@JsonKey(name: 'assigned_email') String assignedEmail,@JsonKey(name: 'assigned_user_id') String? assignedUserId,@JsonKey(name: 'invited_role') UserRole invitedRole,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'locked_inputs') WorkflowInputs lockedInputs,@JsonKey(name: 'assignee_input_keys') List<String> assigneeInputKeys,@JsonKey(name: 'draft_inputs') WorkflowInputs draftInputs, AssignmentStatus status,@JsonKey(name: 'email_delivery_status') EmailDeliveryStatus emailDeliveryStatus,@JsonKey(name: 'result_visibility') AssignmentResultVisibility resultVisibility,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds,@JsonKey(name: 'activated_at') DateTime? activatedAt,@JsonKey(name: 'submitted_at') DateTime? submittedAt,@JsonKey(name: 'execution_id') String? executionId,@StrictOpaqueIdConverter()@JsonKey(name: 'created_by') String createdBy,@JsonKey(name: 'created_at') DateTime createdAt
});


@override $WorkflowInputsCopyWith<$Res> get lockedInputs;@override $WorkflowInputsCopyWith<$Res> get draftInputs;

}
/// @nodoc
class __$ExecutionAssignmentResponseDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentResponseDtoCopyWith<$Res> {
  __$ExecutionAssignmentResponseDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentResponseDto _self;
  final $Res Function(_ExecutionAssignmentResponseDto) _then;

/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? batchId = freezed,Object? organizationId = null,Object? assignedEmail = null,Object? assignedUserId = freezed,Object? invitedRole = null,Object? workflowId = null,Object? outputProfileId = freezed,Object? targetLocale = null,Object? lockedInputs = null,Object? assigneeInputKeys = null,Object? draftInputs = null,Object? status = null,Object? emailDeliveryStatus = null,Object? resultVisibility = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,Object? activatedAt = freezed,Object? submittedAt = freezed,Object? executionId = freezed,Object? createdBy = null,Object? createdAt = null,}) {
  return _then(_ExecutionAssignmentResponseDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,batchId: freezed == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String?,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,assignedEmail: null == assignedEmail ? _self.assignedEmail : assignedEmail // ignore: cast_nullable_to_non_nullable
as String,assignedUserId: freezed == assignedUserId ? _self.assignedUserId : assignedUserId // ignore: cast_nullable_to_non_nullable
as String?,invitedRole: null == invitedRole ? _self.invitedRole : invitedRole // ignore: cast_nullable_to_non_nullable
as UserRole,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,lockedInputs: null == lockedInputs ? _self.lockedInputs : lockedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,assigneeInputKeys: null == assigneeInputKeys ? _self._assigneeInputKeys : assigneeInputKeys // ignore: cast_nullable_to_non_nullable
as List<String>,draftInputs: null == draftInputs ? _self.draftInputs : draftInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as AssignmentStatus,emailDeliveryStatus: null == emailDeliveryStatus ? _self.emailDeliveryStatus : emailDeliveryStatus // ignore: cast_nullable_to_non_nullable
as EmailDeliveryStatus,resultVisibility: null == resultVisibility ? _self.resultVisibility : resultVisibility // ignore: cast_nullable_to_non_nullable
as AssignmentResultVisibility,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,activatedAt: freezed == activatedAt ? _self.activatedAt : activatedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,submittedAt: freezed == submittedAt ? _self.submittedAt : submittedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,executionId: freezed == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String?,createdBy: null == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get lockedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.lockedInputs, (value) {
    return _then(_self.copyWith(lockedInputs: value));
  });
}/// Create a copy of ExecutionAssignmentResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get draftInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.draftInputs, (value) {
    return _then(_self.copyWith(draftInputs: value));
  });
}
}


/// @nodoc
mixin _$ExecutionAssignmentBatchResponseDto {

@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id') String get batchId;@JsonKey(name: 'created_count') int get createdCount; List<ExecutionAssignmentResponseDto> get assignments;
/// Create a copy of ExecutionAssignmentBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentBatchResponseDtoCopyWith<ExecutionAssignmentBatchResponseDto> get copyWith => _$ExecutionAssignmentBatchResponseDtoCopyWithImpl<ExecutionAssignmentBatchResponseDto>(this as ExecutionAssignmentBatchResponseDto, _$identity);

  /// Serializes this ExecutionAssignmentBatchResponseDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentBatchResponseDto(batchId: $batchId, createdCount: $createdCount, assignments: $assignments)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentBatchResponseDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentBatchResponseDtoCopyWith(ExecutionAssignmentBatchResponseDto value, $Res Function(ExecutionAssignmentBatchResponseDto) _then) = _$ExecutionAssignmentBatchResponseDtoCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id') String batchId,@JsonKey(name: 'created_count') int createdCount, List<ExecutionAssignmentResponseDto> assignments
});




}
/// @nodoc
class _$ExecutionAssignmentBatchResponseDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentBatchResponseDtoCopyWith<$Res> {
  _$ExecutionAssignmentBatchResponseDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentBatchResponseDto _self;
  final $Res Function(ExecutionAssignmentBatchResponseDto) _then;

/// Create a copy of ExecutionAssignmentBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? batchId = null,Object? createdCount = null,Object? assignments = null,}) {
  return _then(_self.copyWith(
batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,createdCount: null == createdCount ? _self.createdCount : createdCount // ignore: cast_nullable_to_non_nullable
as int,assignments: null == assignments ? _self.assignments : assignments // ignore: cast_nullable_to_non_nullable
as List<ExecutionAssignmentResponseDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionAssignmentBatchResponseDto].
extension ExecutionAssignmentBatchResponseDtoPatterns on ExecutionAssignmentBatchResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentBatchResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentBatchResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentBatchResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id')  String batchId, @JsonKey(name: 'created_count')  int createdCount,  List<ExecutionAssignmentResponseDto> assignments)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchResponseDto() when $default != null:
return $default(_that.batchId,_that.createdCount,_that.assignments);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id')  String batchId, @JsonKey(name: 'created_count')  int createdCount,  List<ExecutionAssignmentResponseDto> assignments)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchResponseDto():
return $default(_that.batchId,_that.createdCount,_that.assignments);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id')  String batchId, @JsonKey(name: 'created_count')  int createdCount,  List<ExecutionAssignmentResponseDto> assignments)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentBatchResponseDto() when $default != null:
return $default(_that.batchId,_that.createdCount,_that.assignments);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionAssignmentBatchResponseDto extends ExecutionAssignmentBatchResponseDto {
  const _ExecutionAssignmentBatchResponseDto({@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id') required this.batchId, @JsonKey(name: 'created_count') required this.createdCount, required final  List<ExecutionAssignmentResponseDto> assignments}): _assignments = assignments,super._();
  factory _ExecutionAssignmentBatchResponseDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentBatchResponseDtoFromJson(json);

@override@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id') final  String batchId;
@override@JsonKey(name: 'created_count') final  int createdCount;
 final  List<ExecutionAssignmentResponseDto> _assignments;
@override List<ExecutionAssignmentResponseDto> get assignments {
  if (_assignments is EqualUnmodifiableListView) return _assignments;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_assignments);
}


/// Create a copy of ExecutionAssignmentBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentBatchResponseDtoCopyWith<_ExecutionAssignmentBatchResponseDto> get copyWith => __$ExecutionAssignmentBatchResponseDtoCopyWithImpl<_ExecutionAssignmentBatchResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentBatchResponseDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentBatchResponseDto(batchId: $batchId, createdCount: $createdCount, assignments: $assignments)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentBatchResponseDtoCopyWith<$Res> implements $ExecutionAssignmentBatchResponseDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentBatchResponseDtoCopyWith(_ExecutionAssignmentBatchResponseDto value, $Res Function(_ExecutionAssignmentBatchResponseDto) _then) = __$ExecutionAssignmentBatchResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter()@JsonKey(name: 'batch_id') String batchId,@JsonKey(name: 'created_count') int createdCount, List<ExecutionAssignmentResponseDto> assignments
});




}
/// @nodoc
class __$ExecutionAssignmentBatchResponseDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentBatchResponseDtoCopyWith<$Res> {
  __$ExecutionAssignmentBatchResponseDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentBatchResponseDto _self;
  final $Res Function(_ExecutionAssignmentBatchResponseDto) _then;

/// Create a copy of ExecutionAssignmentBatchResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? batchId = null,Object? createdCount = null,Object? assignments = null,}) {
  return _then(_ExecutionAssignmentBatchResponseDto(
batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,createdCount: null == createdCount ? _self.createdCount : createdCount // ignore: cast_nullable_to_non_nullable
as int,assignments: null == assignments ? _self._assignments : assignments // ignore: cast_nullable_to_non_nullable
as List<ExecutionAssignmentResponseDto>,
  ));
}


}


/// @nodoc
mixin _$ExecutionAssignmentPreviewDto {

@StrictOpaqueIdConverter() String get id;@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String get organizationId;@JsonKey(name: 'organization_name') String get organizationName;@JsonKey(name: 'assigned_email_masked') String get assignedEmailMasked;@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'target_locale') String get targetLocale; AssignmentStatus get status;@JsonKey(name: 'hard_deadline_at') DateTime get hardDeadlineAt;@JsonKey(name: 'relative_duration_seconds') int? get relativeDurationSeconds;
/// Create a copy of ExecutionAssignmentPreviewDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentPreviewDtoCopyWith<ExecutionAssignmentPreviewDto> get copyWith => _$ExecutionAssignmentPreviewDtoCopyWithImpl<ExecutionAssignmentPreviewDto>(this as ExecutionAssignmentPreviewDto, _$identity);

  /// Serializes this ExecutionAssignmentPreviewDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentPreviewDto(id: $id, organizationId: $organizationId, organizationName: $organizationName, assignedEmailMasked: $assignedEmailMasked, workflowId: $workflowId, targetLocale: $targetLocale, status: $status, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentPreviewDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentPreviewDtoCopyWith(ExecutionAssignmentPreviewDto value, $Res Function(ExecutionAssignmentPreviewDto) _then) = _$ExecutionAssignmentPreviewDtoCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId,@JsonKey(name: 'organization_name') String organizationName,@JsonKey(name: 'assigned_email_masked') String assignedEmailMasked,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale, AssignmentStatus status,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds
});




}
/// @nodoc
class _$ExecutionAssignmentPreviewDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentPreviewDtoCopyWith<$Res> {
  _$ExecutionAssignmentPreviewDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentPreviewDto _self;
  final $Res Function(ExecutionAssignmentPreviewDto) _then;

/// Create a copy of ExecutionAssignmentPreviewDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? organizationId = null,Object? organizationName = null,Object? assignedEmailMasked = null,Object? workflowId = null,Object? targetLocale = null,Object? status = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,organizationName: null == organizationName ? _self.organizationName : organizationName // ignore: cast_nullable_to_non_nullable
as String,assignedEmailMasked: null == assignedEmailMasked ? _self.assignedEmailMasked : assignedEmailMasked // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as AssignmentStatus,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionAssignmentPreviewDto].
extension ExecutionAssignmentPreviewDtoPatterns on ExecutionAssignmentPreviewDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentPreviewDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentPreviewDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentPreviewDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentPreviewDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentPreviewDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentPreviewDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'organization_name')  String organizationName, @JsonKey(name: 'assigned_email_masked')  String assignedEmailMasked, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale,  AssignmentStatus status, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentPreviewDto() when $default != null:
return $default(_that.id,_that.organizationId,_that.organizationName,_that.assignedEmailMasked,_that.workflowId,_that.targetLocale,_that.status,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'organization_name')  String organizationName, @JsonKey(name: 'assigned_email_masked')  String assignedEmailMasked, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale,  AssignmentStatus status, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentPreviewDto():
return $default(_that.id,_that.organizationId,_that.organizationName,_that.assignedEmailMasked,_that.workflowId,_that.targetLocale,_that.status,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId, @JsonKey(name: 'organization_name')  String organizationName, @JsonKey(name: 'assigned_email_masked')  String assignedEmailMasked, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale,  AssignmentStatus status, @JsonKey(name: 'hard_deadline_at')  DateTime hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds')  int? relativeDurationSeconds)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentPreviewDto() when $default != null:
return $default(_that.id,_that.organizationId,_that.organizationName,_that.assignedEmailMasked,_that.workflowId,_that.targetLocale,_that.status,_that.hardDeadlineAt,_that.relativeDurationSeconds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionAssignmentPreviewDto extends ExecutionAssignmentPreviewDto {
  const _ExecutionAssignmentPreviewDto({@StrictOpaqueIdConverter() required this.id, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') required this.organizationId, @JsonKey(name: 'organization_name') required this.organizationName, @JsonKey(name: 'assigned_email_masked') required this.assignedEmailMasked, @StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'target_locale') required this.targetLocale, required this.status, @JsonKey(name: 'hard_deadline_at') required this.hardDeadlineAt, @JsonKey(name: 'relative_duration_seconds') this.relativeDurationSeconds}): super._();
  factory _ExecutionAssignmentPreviewDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentPreviewDtoFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') final  String organizationId;
@override@JsonKey(name: 'organization_name') final  String organizationName;
@override@JsonKey(name: 'assigned_email_masked') final  String assignedEmailMasked;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override final  AssignmentStatus status;
@override@JsonKey(name: 'hard_deadline_at') final  DateTime hardDeadlineAt;
@override@JsonKey(name: 'relative_duration_seconds') final  int? relativeDurationSeconds;

/// Create a copy of ExecutionAssignmentPreviewDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentPreviewDtoCopyWith<_ExecutionAssignmentPreviewDto> get copyWith => __$ExecutionAssignmentPreviewDtoCopyWithImpl<_ExecutionAssignmentPreviewDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentPreviewDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentPreviewDto(id: $id, organizationId: $organizationId, organizationName: $organizationName, assignedEmailMasked: $assignedEmailMasked, workflowId: $workflowId, targetLocale: $targetLocale, status: $status, hardDeadlineAt: $hardDeadlineAt, relativeDurationSeconds: $relativeDurationSeconds)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentPreviewDtoCopyWith<$Res> implements $ExecutionAssignmentPreviewDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentPreviewDtoCopyWith(_ExecutionAssignmentPreviewDto value, $Res Function(_ExecutionAssignmentPreviewDto) _then) = __$ExecutionAssignmentPreviewDtoCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId,@JsonKey(name: 'organization_name') String organizationName,@JsonKey(name: 'assigned_email_masked') String assignedEmailMasked,@StrictOpaqueIdConverter()@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale, AssignmentStatus status,@JsonKey(name: 'hard_deadline_at') DateTime hardDeadlineAt,@JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds
});




}
/// @nodoc
class __$ExecutionAssignmentPreviewDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentPreviewDtoCopyWith<$Res> {
  __$ExecutionAssignmentPreviewDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentPreviewDto _self;
  final $Res Function(_ExecutionAssignmentPreviewDto) _then;

/// Create a copy of ExecutionAssignmentPreviewDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? organizationId = null,Object? organizationName = null,Object? assignedEmailMasked = null,Object? workflowId = null,Object? targetLocale = null,Object? status = null,Object? hardDeadlineAt = null,Object? relativeDurationSeconds = freezed,}) {
  return _then(_ExecutionAssignmentPreviewDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,organizationName: null == organizationName ? _self.organizationName : organizationName // ignore: cast_nullable_to_non_nullable
as String,assignedEmailMasked: null == assignedEmailMasked ? _self.assignedEmailMasked : assignedEmailMasked // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as AssignmentStatus,hardDeadlineAt: null == hardDeadlineAt ? _self.hardDeadlineAt : hardDeadlineAt // ignore: cast_nullable_to_non_nullable
as DateTime,relativeDurationSeconds: freezed == relativeDurationSeconds ? _self.relativeDurationSeconds : relativeDurationSeconds // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$ExecutionAssignmentOnboardingRequestDto {

@JsonKey(name: 'firebase_token') String? get firebaseToken; String? get name;
/// Create a copy of ExecutionAssignmentOnboardingRequestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentOnboardingRequestDtoCopyWith<ExecutionAssignmentOnboardingRequestDto> get copyWith => _$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl<ExecutionAssignmentOnboardingRequestDto>(this as ExecutionAssignmentOnboardingRequestDto, _$identity);

  /// Serializes this ExecutionAssignmentOnboardingRequestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentOnboardingRequestDto(firebaseToken: $firebaseToken, name: $name)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentOnboardingRequestDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentOnboardingRequestDtoCopyWith(ExecutionAssignmentOnboardingRequestDto value, $Res Function(ExecutionAssignmentOnboardingRequestDto) _then) = _$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'firebase_token') String? firebaseToken, String? name
});




}
/// @nodoc
class _$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentOnboardingRequestDtoCopyWith<$Res> {
  _$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentOnboardingRequestDto _self;
  final $Res Function(ExecutionAssignmentOnboardingRequestDto) _then;

/// Create a copy of ExecutionAssignmentOnboardingRequestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? firebaseToken = freezed,Object? name = freezed,}) {
  return _then(_self.copyWith(
firebaseToken: freezed == firebaseToken ? _self.firebaseToken : firebaseToken // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionAssignmentOnboardingRequestDto].
extension ExecutionAssignmentOnboardingRequestDtoPatterns on ExecutionAssignmentOnboardingRequestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentOnboardingRequestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentOnboardingRequestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentOnboardingRequestDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentOnboardingRequestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentOnboardingRequestDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentOnboardingRequestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'firebase_token')  String? firebaseToken,  String? name)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentOnboardingRequestDto() when $default != null:
return $default(_that.firebaseToken,_that.name);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'firebase_token')  String? firebaseToken,  String? name)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentOnboardingRequestDto():
return $default(_that.firebaseToken,_that.name);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'firebase_token')  String? firebaseToken,  String? name)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentOnboardingRequestDto() when $default != null:
return $default(_that.firebaseToken,_that.name);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, includeIfNull: false)
class _ExecutionAssignmentOnboardingRequestDto extends ExecutionAssignmentOnboardingRequestDto {
  const _ExecutionAssignmentOnboardingRequestDto({@JsonKey(name: 'firebase_token') this.firebaseToken, this.name}): super._();
  factory _ExecutionAssignmentOnboardingRequestDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentOnboardingRequestDtoFromJson(json);

@override@JsonKey(name: 'firebase_token') final  String? firebaseToken;
@override final  String? name;

/// Create a copy of ExecutionAssignmentOnboardingRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentOnboardingRequestDtoCopyWith<_ExecutionAssignmentOnboardingRequestDto> get copyWith => __$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl<_ExecutionAssignmentOnboardingRequestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentOnboardingRequestDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentOnboardingRequestDto(firebaseToken: $firebaseToken, name: $name)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentOnboardingRequestDtoCopyWith<$Res> implements $ExecutionAssignmentOnboardingRequestDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentOnboardingRequestDtoCopyWith(_ExecutionAssignmentOnboardingRequestDto value, $Res Function(_ExecutionAssignmentOnboardingRequestDto) _then) = __$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'firebase_token') String? firebaseToken, String? name
});




}
/// @nodoc
class __$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentOnboardingRequestDtoCopyWith<$Res> {
  __$ExecutionAssignmentOnboardingRequestDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentOnboardingRequestDto _self;
  final $Res Function(_ExecutionAssignmentOnboardingRequestDto) _then;

/// Create a copy of ExecutionAssignmentOnboardingRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? firebaseToken = freezed,Object? name = freezed,}) {
  return _then(_ExecutionAssignmentOnboardingRequestDto(
firebaseToken: freezed == firebaseToken ? _self.firebaseToken : firebaseToken // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ExecutionAssignmentDraftDto {

@JsonKey(name: 'draft_inputs') WorkflowInputs get draftInputs;
/// Create a copy of ExecutionAssignmentDraftDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentDraftDtoCopyWith<ExecutionAssignmentDraftDto> get copyWith => _$ExecutionAssignmentDraftDtoCopyWithImpl<ExecutionAssignmentDraftDto>(this as ExecutionAssignmentDraftDto, _$identity);

  /// Serializes this ExecutionAssignmentDraftDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentDraftDto(draftInputs: $draftInputs)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentDraftDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentDraftDtoCopyWith(ExecutionAssignmentDraftDto value, $Res Function(ExecutionAssignmentDraftDto) _then) = _$ExecutionAssignmentDraftDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'draft_inputs') WorkflowInputs draftInputs
});


$WorkflowInputsCopyWith<$Res> get draftInputs;

}
/// @nodoc
class _$ExecutionAssignmentDraftDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentDraftDtoCopyWith<$Res> {
  _$ExecutionAssignmentDraftDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentDraftDto _self;
  final $Res Function(ExecutionAssignmentDraftDto) _then;

/// Create a copy of ExecutionAssignmentDraftDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? draftInputs = null,}) {
  return _then(_self.copyWith(
draftInputs: null == draftInputs ? _self.draftInputs : draftInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,
  ));
}
/// Create a copy of ExecutionAssignmentDraftDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get draftInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.draftInputs, (value) {
    return _then(_self.copyWith(draftInputs: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionAssignmentDraftDto].
extension ExecutionAssignmentDraftDtoPatterns on ExecutionAssignmentDraftDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentDraftDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentDraftDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentDraftDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentDraftDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentDraftDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentDraftDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'draft_inputs')  WorkflowInputs draftInputs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentDraftDto() when $default != null:
return $default(_that.draftInputs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'draft_inputs')  WorkflowInputs draftInputs)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentDraftDto():
return $default(_that.draftInputs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'draft_inputs')  WorkflowInputs draftInputs)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentDraftDto() when $default != null:
return $default(_that.draftInputs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionAssignmentDraftDto extends ExecutionAssignmentDraftDto {
  const _ExecutionAssignmentDraftDto({@JsonKey(name: 'draft_inputs') required this.draftInputs}): super._();
  factory _ExecutionAssignmentDraftDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentDraftDtoFromJson(json);

@override@JsonKey(name: 'draft_inputs') final  WorkflowInputs draftInputs;

/// Create a copy of ExecutionAssignmentDraftDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentDraftDtoCopyWith<_ExecutionAssignmentDraftDto> get copyWith => __$ExecutionAssignmentDraftDtoCopyWithImpl<_ExecutionAssignmentDraftDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentDraftDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentDraftDto(draftInputs: $draftInputs)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentDraftDtoCopyWith<$Res> implements $ExecutionAssignmentDraftDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentDraftDtoCopyWith(_ExecutionAssignmentDraftDto value, $Res Function(_ExecutionAssignmentDraftDto) _then) = __$ExecutionAssignmentDraftDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'draft_inputs') WorkflowInputs draftInputs
});


@override $WorkflowInputsCopyWith<$Res> get draftInputs;

}
/// @nodoc
class __$ExecutionAssignmentDraftDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentDraftDtoCopyWith<$Res> {
  __$ExecutionAssignmentDraftDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentDraftDto _self;
  final $Res Function(_ExecutionAssignmentDraftDto) _then;

/// Create a copy of ExecutionAssignmentDraftDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? draftInputs = null,}) {
  return _then(_ExecutionAssignmentDraftDto(
draftInputs: null == draftInputs ? _self.draftInputs : draftInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,
  ));
}

/// Create a copy of ExecutionAssignmentDraftDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get draftInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.draftInputs, (value) {
    return _then(_self.copyWith(draftInputs: value));
  });
}
}


/// @nodoc
mixin _$ExecutionAssignmentSubmitDto {

@JsonKey(name: 'submitted_inputs') WorkflowInputs get submittedInputs;
/// Create a copy of ExecutionAssignmentSubmitDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionAssignmentSubmitDtoCopyWith<ExecutionAssignmentSubmitDto> get copyWith => _$ExecutionAssignmentSubmitDtoCopyWithImpl<ExecutionAssignmentSubmitDto>(this as ExecutionAssignmentSubmitDto, _$identity);

  /// Serializes this ExecutionAssignmentSubmitDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionAssignmentSubmitDto(submittedInputs: $submittedInputs)';
}


}

/// @nodoc
abstract mixin class $ExecutionAssignmentSubmitDtoCopyWith<$Res>  {
  factory $ExecutionAssignmentSubmitDtoCopyWith(ExecutionAssignmentSubmitDto value, $Res Function(ExecutionAssignmentSubmitDto) _then) = _$ExecutionAssignmentSubmitDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'submitted_inputs') WorkflowInputs submittedInputs
});


$WorkflowInputsCopyWith<$Res> get submittedInputs;

}
/// @nodoc
class _$ExecutionAssignmentSubmitDtoCopyWithImpl<$Res>
    implements $ExecutionAssignmentSubmitDtoCopyWith<$Res> {
  _$ExecutionAssignmentSubmitDtoCopyWithImpl(this._self, this._then);

  final ExecutionAssignmentSubmitDto _self;
  final $Res Function(ExecutionAssignmentSubmitDto) _then;

/// Create a copy of ExecutionAssignmentSubmitDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? submittedInputs = null,}) {
  return _then(_self.copyWith(
submittedInputs: null == submittedInputs ? _self.submittedInputs : submittedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,
  ));
}
/// Create a copy of ExecutionAssignmentSubmitDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get submittedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.submittedInputs, (value) {
    return _then(_self.copyWith(submittedInputs: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionAssignmentSubmitDto].
extension ExecutionAssignmentSubmitDtoPatterns on ExecutionAssignmentSubmitDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionAssignmentSubmitDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionAssignmentSubmitDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionAssignmentSubmitDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentSubmitDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionAssignmentSubmitDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionAssignmentSubmitDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'submitted_inputs')  WorkflowInputs submittedInputs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionAssignmentSubmitDto() when $default != null:
return $default(_that.submittedInputs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'submitted_inputs')  WorkflowInputs submittedInputs)  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentSubmitDto():
return $default(_that.submittedInputs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'submitted_inputs')  WorkflowInputs submittedInputs)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionAssignmentSubmitDto() when $default != null:
return $default(_that.submittedInputs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionAssignmentSubmitDto extends ExecutionAssignmentSubmitDto {
  const _ExecutionAssignmentSubmitDto({@JsonKey(name: 'submitted_inputs') required this.submittedInputs}): super._();
  factory _ExecutionAssignmentSubmitDto.fromJson(Map<String, dynamic> json) => _$ExecutionAssignmentSubmitDtoFromJson(json);

@override@JsonKey(name: 'submitted_inputs') final  WorkflowInputs submittedInputs;

/// Create a copy of ExecutionAssignmentSubmitDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionAssignmentSubmitDtoCopyWith<_ExecutionAssignmentSubmitDto> get copyWith => __$ExecutionAssignmentSubmitDtoCopyWithImpl<_ExecutionAssignmentSubmitDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionAssignmentSubmitDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionAssignmentSubmitDto(submittedInputs: $submittedInputs)';
}


}

/// @nodoc
abstract mixin class _$ExecutionAssignmentSubmitDtoCopyWith<$Res> implements $ExecutionAssignmentSubmitDtoCopyWith<$Res> {
  factory _$ExecutionAssignmentSubmitDtoCopyWith(_ExecutionAssignmentSubmitDto value, $Res Function(_ExecutionAssignmentSubmitDto) _then) = __$ExecutionAssignmentSubmitDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'submitted_inputs') WorkflowInputs submittedInputs
});


@override $WorkflowInputsCopyWith<$Res> get submittedInputs;

}
/// @nodoc
class __$ExecutionAssignmentSubmitDtoCopyWithImpl<$Res>
    implements _$ExecutionAssignmentSubmitDtoCopyWith<$Res> {
  __$ExecutionAssignmentSubmitDtoCopyWithImpl(this._self, this._then);

  final _ExecutionAssignmentSubmitDto _self;
  final $Res Function(_ExecutionAssignmentSubmitDto) _then;

/// Create a copy of ExecutionAssignmentSubmitDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? submittedInputs = null,}) {
  return _then(_ExecutionAssignmentSubmitDto(
submittedInputs: null == submittedInputs ? _self.submittedInputs : submittedInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs,
  ));
}

/// Create a copy of ExecutionAssignmentSubmitDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res> get submittedInputs {
  
  return $WorkflowInputsCopyWith<$Res>(_self.submittedInputs, (value) {
    return _then(_self.copyWith(submittedInputs: value));
  });
}
}

// dart format on
