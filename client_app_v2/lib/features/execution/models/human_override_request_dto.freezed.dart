// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'human_override_request_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$HumanOverrideRequestDto {

@JsonKey(name: 'new_status') ExecutionStatus get newStatus; String get reason;@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> get evidenceQuotes;
/// Create a copy of HumanOverrideRequestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$HumanOverrideRequestDtoCopyWith<HumanOverrideRequestDto> get copyWith => _$HumanOverrideRequestDtoCopyWithImpl<HumanOverrideRequestDto>(this as HumanOverrideRequestDto, _$identity);

  /// Serializes this HumanOverrideRequestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'HumanOverrideRequestDto(newStatus: $newStatus, reason: $reason, evidenceQuotes: $evidenceQuotes)';
}


}

/// @nodoc
abstract mixin class $HumanOverrideRequestDtoCopyWith<$Res>  {
  factory $HumanOverrideRequestDtoCopyWith(HumanOverrideRequestDto value, $Res Function(HumanOverrideRequestDto) _then) = _$HumanOverrideRequestDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'new_status') ExecutionStatus newStatus, String reason,@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> evidenceQuotes
});




}
/// @nodoc
class _$HumanOverrideRequestDtoCopyWithImpl<$Res>
    implements $HumanOverrideRequestDtoCopyWith<$Res> {
  _$HumanOverrideRequestDtoCopyWithImpl(this._self, this._then);

  final HumanOverrideRequestDto _self;
  final $Res Function(HumanOverrideRequestDto) _then;

/// Create a copy of HumanOverrideRequestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? newStatus = null,Object? reason = null,Object? evidenceQuotes = null,}) {
  return _then(_self.copyWith(
newStatus: null == newStatus ? _self.newStatus : newStatus // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,evidenceQuotes: null == evidenceQuotes ? _self.evidenceQuotes : evidenceQuotes // ignore: cast_nullable_to_non_nullable
as List<QuoteEvidenceDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [HumanOverrideRequestDto].
extension HumanOverrideRequestDtoPatterns on HumanOverrideRequestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _HumanOverrideRequestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _HumanOverrideRequestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _HumanOverrideRequestDto value)  $default,){
final _that = this;
switch (_that) {
case _HumanOverrideRequestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _HumanOverrideRequestDto value)?  $default,){
final _that = this;
switch (_that) {
case _HumanOverrideRequestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'new_status')  ExecutionStatus newStatus,  String reason, @JsonKey(name: 'evidence_quotes')  List<QuoteEvidenceDto> evidenceQuotes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _HumanOverrideRequestDto() when $default != null:
return $default(_that.newStatus,_that.reason,_that.evidenceQuotes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'new_status')  ExecutionStatus newStatus,  String reason, @JsonKey(name: 'evidence_quotes')  List<QuoteEvidenceDto> evidenceQuotes)  $default,) {final _that = this;
switch (_that) {
case _HumanOverrideRequestDto():
return $default(_that.newStatus,_that.reason,_that.evidenceQuotes);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'new_status')  ExecutionStatus newStatus,  String reason, @JsonKey(name: 'evidence_quotes')  List<QuoteEvidenceDto> evidenceQuotes)?  $default,) {final _that = this;
switch (_that) {
case _HumanOverrideRequestDto() when $default != null:
return $default(_that.newStatus,_that.reason,_that.evidenceQuotes);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _HumanOverrideRequestDto implements HumanOverrideRequestDto {
  const _HumanOverrideRequestDto({@JsonKey(name: 'new_status') required this.newStatus, required this.reason, @JsonKey(name: 'evidence_quotes') final  List<QuoteEvidenceDto> evidenceQuotes = const []}): _evidenceQuotes = evidenceQuotes;
  factory _HumanOverrideRequestDto.fromJson(Map<String, dynamic> json) => _$HumanOverrideRequestDtoFromJson(json);

@override@JsonKey(name: 'new_status') final  ExecutionStatus newStatus;
@override final  String reason;
 final  List<QuoteEvidenceDto> _evidenceQuotes;
@override@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> get evidenceQuotes {
  if (_evidenceQuotes is EqualUnmodifiableListView) return _evidenceQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_evidenceQuotes);
}


/// Create a copy of HumanOverrideRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$HumanOverrideRequestDtoCopyWith<_HumanOverrideRequestDto> get copyWith => __$HumanOverrideRequestDtoCopyWithImpl<_HumanOverrideRequestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$HumanOverrideRequestDtoToJson(this, );
}



@override
String toString() {
  return 'HumanOverrideRequestDto(newStatus: $newStatus, reason: $reason, evidenceQuotes: $evidenceQuotes)';
}


}

/// @nodoc
abstract mixin class _$HumanOverrideRequestDtoCopyWith<$Res> implements $HumanOverrideRequestDtoCopyWith<$Res> {
  factory _$HumanOverrideRequestDtoCopyWith(_HumanOverrideRequestDto value, $Res Function(_HumanOverrideRequestDto) _then) = __$HumanOverrideRequestDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'new_status') ExecutionStatus newStatus, String reason,@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> evidenceQuotes
});




}
/// @nodoc
class __$HumanOverrideRequestDtoCopyWithImpl<$Res>
    implements _$HumanOverrideRequestDtoCopyWith<$Res> {
  __$HumanOverrideRequestDtoCopyWithImpl(this._self, this._then);

  final _HumanOverrideRequestDto _self;
  final $Res Function(_HumanOverrideRequestDto) _then;

/// Create a copy of HumanOverrideRequestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? newStatus = null,Object? reason = null,Object? evidenceQuotes = null,}) {
  return _then(_HumanOverrideRequestDto(
newStatus: null == newStatus ? _self.newStatus : newStatus // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,evidenceQuotes: null == evidenceQuotes ? _self._evidenceQuotes : evidenceQuotes // ignore: cast_nullable_to_non_nullable
as List<QuoteEvidenceDto>,
  ));
}


}

// dart format on
