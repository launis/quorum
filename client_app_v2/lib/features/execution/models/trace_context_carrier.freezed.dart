// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'trace_context_carrier.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TraceContextCarrier {

 String get traceparent; String? get tracestate;
/// Create a copy of TraceContextCarrier
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TraceContextCarrierCopyWith<TraceContextCarrier> get copyWith => _$TraceContextCarrierCopyWithImpl<TraceContextCarrier>(this as TraceContextCarrier, _$identity);

  /// Serializes this TraceContextCarrier to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TraceContextCarrier(traceparent: $traceparent, tracestate: $tracestate)';
}


}

/// @nodoc
abstract mixin class $TraceContextCarrierCopyWith<$Res>  {
  factory $TraceContextCarrierCopyWith(TraceContextCarrier value, $Res Function(TraceContextCarrier) _then) = _$TraceContextCarrierCopyWithImpl;
@useResult
$Res call({
 String traceparent, String? tracestate
});




}
/// @nodoc
class _$TraceContextCarrierCopyWithImpl<$Res>
    implements $TraceContextCarrierCopyWith<$Res> {
  _$TraceContextCarrierCopyWithImpl(this._self, this._then);

  final TraceContextCarrier _self;
  final $Res Function(TraceContextCarrier) _then;

/// Create a copy of TraceContextCarrier
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? traceparent = null,Object? tracestate = freezed,}) {
  return _then(_self.copyWith(
traceparent: null == traceparent ? _self.traceparent : traceparent // ignore: cast_nullable_to_non_nullable
as String,tracestate: freezed == tracestate ? _self.tracestate : tracestate // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [TraceContextCarrier].
extension TraceContextCarrierPatterns on TraceContextCarrier {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TraceContextCarrier value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TraceContextCarrier() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TraceContextCarrier value)  $default,){
final _that = this;
switch (_that) {
case _TraceContextCarrier():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TraceContextCarrier value)?  $default,){
final _that = this;
switch (_that) {
case _TraceContextCarrier() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String traceparent,  String? tracestate)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TraceContextCarrier() when $default != null:
return $default(_that.traceparent,_that.tracestate);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String traceparent,  String? tracestate)  $default,) {final _that = this;
switch (_that) {
case _TraceContextCarrier():
return $default(_that.traceparent,_that.tracestate);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String traceparent,  String? tracestate)?  $default,) {final _that = this;
switch (_that) {
case _TraceContextCarrier() when $default != null:
return $default(_that.traceparent,_that.tracestate);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _TraceContextCarrier extends TraceContextCarrier {
  const _TraceContextCarrier({required this.traceparent, this.tracestate}): super._();
  factory _TraceContextCarrier.fromJson(Map<String, dynamic> json) => _$TraceContextCarrierFromJson(json);

@override final  String traceparent;
@override final  String? tracestate;

/// Create a copy of TraceContextCarrier
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TraceContextCarrierCopyWith<_TraceContextCarrier> get copyWith => __$TraceContextCarrierCopyWithImpl<_TraceContextCarrier>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TraceContextCarrierToJson(this, );
}



@override
String toString() {
  return 'TraceContextCarrier(traceparent: $traceparent, tracestate: $tracestate)';
}


}

/// @nodoc
abstract mixin class _$TraceContextCarrierCopyWith<$Res> implements $TraceContextCarrierCopyWith<$Res> {
  factory _$TraceContextCarrierCopyWith(_TraceContextCarrier value, $Res Function(_TraceContextCarrier) _then) = __$TraceContextCarrierCopyWithImpl;
@override @useResult
$Res call({
 String traceparent, String? tracestate
});




}
/// @nodoc
class __$TraceContextCarrierCopyWithImpl<$Res>
    implements _$TraceContextCarrierCopyWith<$Res> {
  __$TraceContextCarrierCopyWithImpl(this._self, this._then);

  final _TraceContextCarrier _self;
  final $Res Function(_TraceContextCarrier) _then;

/// Create a copy of TraceContextCarrier
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? traceparent = null,Object? tracestate = freezed,}) {
  return _then(_TraceContextCarrier(
traceparent: null == traceparent ? _self.traceparent : traceparent // ignore: cast_nullable_to_non_nullable
as String,tracestate: freezed == tracestate ? _self.tracestate : tracestate // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
