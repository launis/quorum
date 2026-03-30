// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'blueprint_config.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$BlueprintConfig {

@JsonKey(name: 'preset_view') String get presetView;
/// Create a copy of BlueprintConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$BlueprintConfigCopyWith<BlueprintConfig> get copyWith => _$BlueprintConfigCopyWithImpl<BlueprintConfig>(this as BlueprintConfig, _$identity);

  /// Serializes this BlueprintConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is BlueprintConfig&&(identical(other.presetView, presetView) || other.presetView == presetView));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,presetView);

@override
String toString() {
  return 'BlueprintConfig(presetView: $presetView)';
}


}

/// @nodoc
abstract mixin class $BlueprintConfigCopyWith<$Res>  {
  factory $BlueprintConfigCopyWith(BlueprintConfig value, $Res Function(BlueprintConfig) _then) = _$BlueprintConfigCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'preset_view') String presetView
});




}
/// @nodoc
class _$BlueprintConfigCopyWithImpl<$Res>
    implements $BlueprintConfigCopyWith<$Res> {
  _$BlueprintConfigCopyWithImpl(this._self, this._then);

  final BlueprintConfig _self;
  final $Res Function(BlueprintConfig) _then;

/// Create a copy of BlueprintConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [BlueprintConfig].
extension BlueprintConfigPatterns on BlueprintConfig {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _BlueprintConfig value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _BlueprintConfig() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _BlueprintConfig value)  $default,){
final _that = this;
switch (_that) {
case _BlueprintConfig():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _BlueprintConfig value)?  $default,){
final _that = this;
switch (_that) {
case _BlueprintConfig() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  String presetView)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _BlueprintConfig() when $default != null:
return $default(_that.presetView);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  String presetView)  $default,) {final _that = this;
switch (_that) {
case _BlueprintConfig():
return $default(_that.presetView);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'preset_view')  String presetView)?  $default,) {final _that = this;
switch (_that) {
case _BlueprintConfig() when $default != null:
return $default(_that.presetView);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _BlueprintConfig implements BlueprintConfig {
  const _BlueprintConfig({@JsonKey(name: 'preset_view') this.presetView = '1d_metrics'});
  factory _BlueprintConfig.fromJson(Map<String, dynamic> json) => _$BlueprintConfigFromJson(json);

@override@JsonKey(name: 'preset_view') final  String presetView;

/// Create a copy of BlueprintConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$BlueprintConfigCopyWith<_BlueprintConfig> get copyWith => __$BlueprintConfigCopyWithImpl<_BlueprintConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$BlueprintConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _BlueprintConfig&&(identical(other.presetView, presetView) || other.presetView == presetView));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,presetView);

@override
String toString() {
  return 'BlueprintConfig(presetView: $presetView)';
}


}

/// @nodoc
abstract mixin class _$BlueprintConfigCopyWith<$Res> implements $BlueprintConfigCopyWith<$Res> {
  factory _$BlueprintConfigCopyWith(_BlueprintConfig value, $Res Function(_BlueprintConfig) _then) = __$BlueprintConfigCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'preset_view') String presetView
});




}
/// @nodoc
class __$BlueprintConfigCopyWithImpl<$Res>
    implements _$BlueprintConfigCopyWith<$Res> {
  __$BlueprintConfigCopyWithImpl(this._self, this._then);

  final _BlueprintConfig _self;
  final $Res Function(_BlueprintConfig) _then;

/// Create a copy of BlueprintConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,}) {
  return _then(_BlueprintConfig(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
