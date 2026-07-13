// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'hydrated_atom_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$HydratedAtomDTO {

@JsonKey(name: 'sdui_component') SDUIComponentType get sduiComponent;@JsonKey(name: 'resolved_claim') String get resolvedClaim;@JsonKey(name: 'source_quote') String? get sourceQuote;
/// Create a copy of HydratedAtomDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$HydratedAtomDTOCopyWith<HydratedAtomDTO> get copyWith => _$HydratedAtomDTOCopyWithImpl<HydratedAtomDTO>(this as HydratedAtomDTO, _$identity);

  /// Serializes this HydratedAtomDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is HydratedAtomDTO&&(identical(other.sduiComponent, sduiComponent) || other.sduiComponent == sduiComponent)&&(identical(other.resolvedClaim, resolvedClaim) || other.resolvedClaim == resolvedClaim)&&(identical(other.sourceQuote, sourceQuote) || other.sourceQuote == sourceQuote));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,sduiComponent,resolvedClaim,sourceQuote);

@override
String toString() {
  return 'HydratedAtomDTO(sduiComponent: $sduiComponent, resolvedClaim: $resolvedClaim, sourceQuote: $sourceQuote)';
}


}

/// @nodoc
abstract mixin class $HydratedAtomDTOCopyWith<$Res>  {
  factory $HydratedAtomDTOCopyWith(HydratedAtomDTO value, $Res Function(HydratedAtomDTO) _then) = _$HydratedAtomDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'sdui_component') SDUIComponentType sduiComponent,@JsonKey(name: 'resolved_claim') String resolvedClaim,@JsonKey(name: 'source_quote') String? sourceQuote
});




}
/// @nodoc
class _$HydratedAtomDTOCopyWithImpl<$Res>
    implements $HydratedAtomDTOCopyWith<$Res> {
  _$HydratedAtomDTOCopyWithImpl(this._self, this._then);

  final HydratedAtomDTO _self;
  final $Res Function(HydratedAtomDTO) _then;

/// Create a copy of HydratedAtomDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sduiComponent = null,Object? resolvedClaim = null,Object? sourceQuote = freezed,}) {
  return _then(_self.copyWith(
sduiComponent: null == sduiComponent ? _self.sduiComponent : sduiComponent // ignore: cast_nullable_to_non_nullable
as SDUIComponentType,resolvedClaim: null == resolvedClaim ? _self.resolvedClaim : resolvedClaim // ignore: cast_nullable_to_non_nullable
as String,sourceQuote: freezed == sourceQuote ? _self.sourceQuote : sourceQuote // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [HydratedAtomDTO].
extension HydratedAtomDTOPatterns on HydratedAtomDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _HydratedAtomDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _HydratedAtomDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _HydratedAtomDTO value)  $default,){
final _that = this;
switch (_that) {
case _HydratedAtomDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _HydratedAtomDTO value)?  $default,){
final _that = this;
switch (_that) {
case _HydratedAtomDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'sdui_component')  SDUIComponentType sduiComponent, @JsonKey(name: 'resolved_claim')  String resolvedClaim, @JsonKey(name: 'source_quote')  String? sourceQuote)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _HydratedAtomDTO() when $default != null:
return $default(_that.sduiComponent,_that.resolvedClaim,_that.sourceQuote);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'sdui_component')  SDUIComponentType sduiComponent, @JsonKey(name: 'resolved_claim')  String resolvedClaim, @JsonKey(name: 'source_quote')  String? sourceQuote)  $default,) {final _that = this;
switch (_that) {
case _HydratedAtomDTO():
return $default(_that.sduiComponent,_that.resolvedClaim,_that.sourceQuote);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'sdui_component')  SDUIComponentType sduiComponent, @JsonKey(name: 'resolved_claim')  String resolvedClaim, @JsonKey(name: 'source_quote')  String? sourceQuote)?  $default,) {final _that = this;
switch (_that) {
case _HydratedAtomDTO() when $default != null:
return $default(_that.sduiComponent,_that.resolvedClaim,_that.sourceQuote);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _HydratedAtomDTO implements HydratedAtomDTO {
  const _HydratedAtomDTO({@JsonKey(name: 'sdui_component') required this.sduiComponent, @JsonKey(name: 'resolved_claim') required this.resolvedClaim, @JsonKey(name: 'source_quote') this.sourceQuote});
  factory _HydratedAtomDTO.fromJson(Map<String, dynamic> json) => _$HydratedAtomDTOFromJson(json);

@override@JsonKey(name: 'sdui_component') final  SDUIComponentType sduiComponent;
@override@JsonKey(name: 'resolved_claim') final  String resolvedClaim;
@override@JsonKey(name: 'source_quote') final  String? sourceQuote;

/// Create a copy of HydratedAtomDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$HydratedAtomDTOCopyWith<_HydratedAtomDTO> get copyWith => __$HydratedAtomDTOCopyWithImpl<_HydratedAtomDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$HydratedAtomDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _HydratedAtomDTO&&(identical(other.sduiComponent, sduiComponent) || other.sduiComponent == sduiComponent)&&(identical(other.resolvedClaim, resolvedClaim) || other.resolvedClaim == resolvedClaim)&&(identical(other.sourceQuote, sourceQuote) || other.sourceQuote == sourceQuote));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,sduiComponent,resolvedClaim,sourceQuote);

@override
String toString() {
  return 'HydratedAtomDTO(sduiComponent: $sduiComponent, resolvedClaim: $resolvedClaim, sourceQuote: $sourceQuote)';
}


}

/// @nodoc
abstract mixin class _$HydratedAtomDTOCopyWith<$Res> implements $HydratedAtomDTOCopyWith<$Res> {
  factory _$HydratedAtomDTOCopyWith(_HydratedAtomDTO value, $Res Function(_HydratedAtomDTO) _then) = __$HydratedAtomDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'sdui_component') SDUIComponentType sduiComponent,@JsonKey(name: 'resolved_claim') String resolvedClaim,@JsonKey(name: 'source_quote') String? sourceQuote
});




}
/// @nodoc
class __$HydratedAtomDTOCopyWithImpl<$Res>
    implements _$HydratedAtomDTOCopyWith<$Res> {
  __$HydratedAtomDTOCopyWithImpl(this._self, this._then);

  final _HydratedAtomDTO _self;
  final $Res Function(_HydratedAtomDTO) _then;

/// Create a copy of HydratedAtomDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sduiComponent = null,Object? resolvedClaim = null,Object? sourceQuote = freezed,}) {
  return _then(_HydratedAtomDTO(
sduiComponent: null == sduiComponent ? _self.sduiComponent : sduiComponent // ignore: cast_nullable_to_non_nullable
as SDUIComponentType,resolvedClaim: null == resolvedClaim ? _self.resolvedClaim : resolvedClaim // ignore: cast_nullable_to_non_nullable
as String,sourceQuote: freezed == sourceQuote ? _self.sourceQuote : sourceQuote // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
