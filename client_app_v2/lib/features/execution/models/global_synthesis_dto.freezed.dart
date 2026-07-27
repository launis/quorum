// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'global_synthesis_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$GlobalSynthesisDto {

@JsonKey(name: 'executive_summary') String? get executiveSummary;@JsonKey(name: 'urgency_level') int? get urgencyLevel;@JsonKey(name: 'user_role') String? get userRole;@JsonKey(name: 'user_role_justification') String? get userRoleJustification;
/// Create a copy of GlobalSynthesisDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GlobalSynthesisDtoCopyWith<GlobalSynthesisDto> get copyWith => _$GlobalSynthesisDtoCopyWithImpl<GlobalSynthesisDto>(this as GlobalSynthesisDto, _$identity);

  /// Serializes this GlobalSynthesisDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is GlobalSynthesisDto&&(identical(other.executiveSummary, executiveSummary) || other.executiveSummary == executiveSummary)&&(identical(other.urgencyLevel, urgencyLevel) || other.urgencyLevel == urgencyLevel)&&(identical(other.userRole, userRole) || other.userRole == userRole)&&(identical(other.userRoleJustification, userRoleJustification) || other.userRoleJustification == userRoleJustification));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,executiveSummary,urgencyLevel,userRole,userRoleJustification);

@override
String toString() {
  return 'GlobalSynthesisDto(executiveSummary: $executiveSummary, urgencyLevel: $urgencyLevel, userRole: $userRole, userRoleJustification: $userRoleJustification)';
}


}

/// @nodoc
abstract mixin class $GlobalSynthesisDtoCopyWith<$Res>  {
  factory $GlobalSynthesisDtoCopyWith(GlobalSynthesisDto value, $Res Function(GlobalSynthesisDto) _then) = _$GlobalSynthesisDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'executive_summary') String? executiveSummary,@JsonKey(name: 'urgency_level') int? urgencyLevel,@JsonKey(name: 'user_role') String? userRole,@JsonKey(name: 'user_role_justification') String? userRoleJustification
});




}
/// @nodoc
class _$GlobalSynthesisDtoCopyWithImpl<$Res>
    implements $GlobalSynthesisDtoCopyWith<$Res> {
  _$GlobalSynthesisDtoCopyWithImpl(this._self, this._then);

  final GlobalSynthesisDto _self;
  final $Res Function(GlobalSynthesisDto) _then;

/// Create a copy of GlobalSynthesisDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executiveSummary = freezed,Object? urgencyLevel = freezed,Object? userRole = freezed,Object? userRoleJustification = freezed,}) {
  return _then(_self.copyWith(
executiveSummary: freezed == executiveSummary ? _self.executiveSummary : executiveSummary // ignore: cast_nullable_to_non_nullable
as String?,urgencyLevel: freezed == urgencyLevel ? _self.urgencyLevel : urgencyLevel // ignore: cast_nullable_to_non_nullable
as int?,userRole: freezed == userRole ? _self.userRole : userRole // ignore: cast_nullable_to_non_nullable
as String?,userRoleJustification: freezed == userRoleJustification ? _self.userRoleJustification : userRoleJustification // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [GlobalSynthesisDto].
extension GlobalSynthesisDtoPatterns on GlobalSynthesisDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GlobalSynthesisDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GlobalSynthesisDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GlobalSynthesisDto value)  $default,){
final _that = this;
switch (_that) {
case _GlobalSynthesisDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GlobalSynthesisDto value)?  $default,){
final _that = this;
switch (_that) {
case _GlobalSynthesisDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'executive_summary')  String? executiveSummary, @JsonKey(name: 'urgency_level')  int? urgencyLevel, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'user_role_justification')  String? userRoleJustification)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GlobalSynthesisDto() when $default != null:
return $default(_that.executiveSummary,_that.urgencyLevel,_that.userRole,_that.userRoleJustification);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'executive_summary')  String? executiveSummary, @JsonKey(name: 'urgency_level')  int? urgencyLevel, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'user_role_justification')  String? userRoleJustification)  $default,) {final _that = this;
switch (_that) {
case _GlobalSynthesisDto():
return $default(_that.executiveSummary,_that.urgencyLevel,_that.userRole,_that.userRoleJustification);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'executive_summary')  String? executiveSummary, @JsonKey(name: 'urgency_level')  int? urgencyLevel, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'user_role_justification')  String? userRoleJustification)?  $default,) {final _that = this;
switch (_that) {
case _GlobalSynthesisDto() when $default != null:
return $default(_that.executiveSummary,_that.urgencyLevel,_that.userRole,_that.userRoleJustification);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _GlobalSynthesisDto implements GlobalSynthesisDto {
  const _GlobalSynthesisDto({@JsonKey(name: 'executive_summary') this.executiveSummary, @JsonKey(name: 'urgency_level') this.urgencyLevel, @JsonKey(name: 'user_role') this.userRole, @JsonKey(name: 'user_role_justification') this.userRoleJustification});
  factory _GlobalSynthesisDto.fromJson(Map<String, dynamic> json) => _$GlobalSynthesisDtoFromJson(json);

@override@JsonKey(name: 'executive_summary') final  String? executiveSummary;
@override@JsonKey(name: 'urgency_level') final  int? urgencyLevel;
@override@JsonKey(name: 'user_role') final  String? userRole;
@override@JsonKey(name: 'user_role_justification') final  String? userRoleJustification;

/// Create a copy of GlobalSynthesisDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GlobalSynthesisDtoCopyWith<_GlobalSynthesisDto> get copyWith => __$GlobalSynthesisDtoCopyWithImpl<_GlobalSynthesisDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GlobalSynthesisDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _GlobalSynthesisDto&&(identical(other.executiveSummary, executiveSummary) || other.executiveSummary == executiveSummary)&&(identical(other.urgencyLevel, urgencyLevel) || other.urgencyLevel == urgencyLevel)&&(identical(other.userRole, userRole) || other.userRole == userRole)&&(identical(other.userRoleJustification, userRoleJustification) || other.userRoleJustification == userRoleJustification));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,executiveSummary,urgencyLevel,userRole,userRoleJustification);

@override
String toString() {
  return 'GlobalSynthesisDto(executiveSummary: $executiveSummary, urgencyLevel: $urgencyLevel, userRole: $userRole, userRoleJustification: $userRoleJustification)';
}


}

/// @nodoc
abstract mixin class _$GlobalSynthesisDtoCopyWith<$Res> implements $GlobalSynthesisDtoCopyWith<$Res> {
  factory _$GlobalSynthesisDtoCopyWith(_GlobalSynthesisDto value, $Res Function(_GlobalSynthesisDto) _then) = __$GlobalSynthesisDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'executive_summary') String? executiveSummary,@JsonKey(name: 'urgency_level') int? urgencyLevel,@JsonKey(name: 'user_role') String? userRole,@JsonKey(name: 'user_role_justification') String? userRoleJustification
});




}
/// @nodoc
class __$GlobalSynthesisDtoCopyWithImpl<$Res>
    implements _$GlobalSynthesisDtoCopyWith<$Res> {
  __$GlobalSynthesisDtoCopyWithImpl(this._self, this._then);

  final _GlobalSynthesisDto _self;
  final $Res Function(_GlobalSynthesisDto) _then;

/// Create a copy of GlobalSynthesisDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executiveSummary = freezed,Object? urgencyLevel = freezed,Object? userRole = freezed,Object? userRoleJustification = freezed,}) {
  return _then(_GlobalSynthesisDto(
executiveSummary: freezed == executiveSummary ? _self.executiveSummary : executiveSummary // ignore: cast_nullable_to_non_nullable
as String?,urgencyLevel: freezed == urgencyLevel ? _self.urgencyLevel : urgencyLevel // ignore: cast_nullable_to_non_nullable
as int?,userRole: freezed == userRole ? _self.userRole : userRole // ignore: cast_nullable_to_non_nullable
as String?,userRoleJustification: freezed == userRoleJustification ? _self.userRoleJustification : userRoleJustification // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
