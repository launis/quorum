// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'step_config.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$StepConfig {

 String get id; String get name; String? get description;@JsonKey(name: 'task_key') String get taskKey;@JsonKey(name: 'config') Map<String, dynamic> get config;
/// Create a copy of StepConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepConfigCopyWith<StepConfig> get copyWith => _$StepConfigCopyWithImpl<StepConfig>(this as StepConfig, _$identity);

  /// Serializes this StepConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StepConfig&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other.config, config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,taskKey,const DeepCollectionEquality().hash(config));

@override
String toString() {
  return 'StepConfig(id: $id, name: $name, description: $description, taskKey: $taskKey, config: $config)';
}


}

/// @nodoc
abstract mixin class $StepConfigCopyWith<$Res>  {
  factory $StepConfigCopyWith(StepConfig value, $Res Function(StepConfig) _then) = _$StepConfigCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description,@JsonKey(name: 'task_key') String taskKey,@JsonKey(name: 'config') Map<String, dynamic> config
});




}
/// @nodoc
class _$StepConfigCopyWithImpl<$Res>
    implements $StepConfigCopyWith<$Res> {
  _$StepConfigCopyWithImpl(this._self, this._then);

  final StepConfig _self;
  final $Res Function(StepConfig) _then;

/// Create a copy of StepConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? taskKey = null,Object? config = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,taskKey: null == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String,config: null == config ? _self.config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [StepConfig].
extension StepConfigPatterns on StepConfig {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StepConfig value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StepConfig() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StepConfig value)  $default,){
final _that = this;
switch (_that) {
case _StepConfig():
return $default(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StepConfig value)?  $default,){
final _that = this;
switch (_that) {
case _StepConfig() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? description, @JsonKey(name: 'task_key')  String taskKey, @JsonKey(name: 'config')  Map<String, dynamic> config)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepConfig() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.taskKey,_that.config);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? description, @JsonKey(name: 'task_key')  String taskKey, @JsonKey(name: 'config')  Map<String, dynamic> config)  $default,) {final _that = this;
switch (_that) {
case _StepConfig():
return $default(_that.id,_that.name,_that.description,_that.taskKey,_that.config);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? description, @JsonKey(name: 'task_key')  String taskKey, @JsonKey(name: 'config')  Map<String, dynamic> config)?  $default,) {final _that = this;
switch (_that) {
case _StepConfig() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.taskKey,_that.config);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StepConfig implements StepConfig {
  const _StepConfig({required this.id, required this.name, this.description, @JsonKey(name: 'task_key') this.taskKey = 'analyst', @JsonKey(name: 'config') final  Map<String, dynamic> config = const {}}): _config = config;
  factory _StepConfig.fromJson(Map<String, dynamic> json) => _$StepConfigFromJson(json);

@override final  String id;
@override final  String name;
@override final  String? description;
@override@JsonKey(name: 'task_key') final  String taskKey;
 final  Map<String, dynamic> _config;
@override@JsonKey(name: 'config') Map<String, dynamic> get config {
  if (_config is EqualUnmodifiableMapView) return _config;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_config);
}


/// Create a copy of StepConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StepConfigCopyWith<_StepConfig> get copyWith => __$StepConfigCopyWithImpl<_StepConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StepConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _StepConfig&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other._config, _config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,taskKey,const DeepCollectionEquality().hash(_config));

@override
String toString() {
  return 'StepConfig(id: $id, name: $name, description: $description, taskKey: $taskKey, config: $config)';
}


}

/// @nodoc
abstract mixin class _$StepConfigCopyWith<$Res> implements $StepConfigCopyWith<$Res> {
  factory _$StepConfigCopyWith(_StepConfig value, $Res Function(_StepConfig) _then) = __$StepConfigCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description,@JsonKey(name: 'task_key') String taskKey,@JsonKey(name: 'config') Map<String, dynamic> config
});




}
/// @nodoc
class __$StepConfigCopyWithImpl<$Res>
    implements _$StepConfigCopyWith<$Res> {
  __$StepConfigCopyWithImpl(this._self, this._then);

  final _StepConfig _self;
  final $Res Function(_StepConfig) _then;

/// Create a copy of StepConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? taskKey = null,Object? config = null,}) {
  return _then(_StepConfig(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,taskKey: null == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String,config: null == config ? _self._config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
