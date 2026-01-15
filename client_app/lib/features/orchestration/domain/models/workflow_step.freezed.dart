// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_step.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WorkflowStep {

/// Unique step identifier, e.g., 'safety_check'
 String get id;/// Registry Task Name (matches @register_task name)
@JsonKey(name: 'task_key') String get taskKey;/// Maps task inputs to state values. Example: {'text': '$inputs.history_text'}
 Map<String, String> get inputs;/// Optional static config for the task
 Map<String, dynamic> get config;
/// Create a copy of WorkflowStep
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowStepCopyWith<WorkflowStep> get copyWith => _$WorkflowStepCopyWithImpl<WorkflowStep>(this as WorkflowStep, _$identity);

  /// Serializes this WorkflowStep to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowStep&&(identical(other.id, id) || other.id == id)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other.inputs, inputs)&&const DeepCollectionEquality().equals(other.config, config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,taskKey,const DeepCollectionEquality().hash(inputs),const DeepCollectionEquality().hash(config));

@override
String toString() {
  return 'WorkflowStep(id: $id, taskKey: $taskKey, inputs: $inputs, config: $config)';
}


}

/// @nodoc
abstract mixin class $WorkflowStepCopyWith<$Res>  {
  factory $WorkflowStepCopyWith(WorkflowStep value, $Res Function(WorkflowStep) _then) = _$WorkflowStepCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'task_key') String taskKey, Map<String, String> inputs, Map<String, dynamic> config
});




}
/// @nodoc
class _$WorkflowStepCopyWithImpl<$Res>
    implements $WorkflowStepCopyWith<$Res> {
  _$WorkflowStepCopyWithImpl(this._self, this._then);

  final WorkflowStep _self;
  final $Res Function(WorkflowStep) _then;

/// Create a copy of WorkflowStep
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? taskKey = null,Object? inputs = null,Object? config = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,taskKey: null == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String,inputs: null == inputs ? _self.inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,config: null == config ? _self.config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowStep].
extension WorkflowStepPatterns on WorkflowStep {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowStep value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowStep() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowStep value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowStep():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowStep value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowStep() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'task_key')  String taskKey,  Map<String, String> inputs,  Map<String, dynamic> config)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowStep() when $default != null:
return $default(_that.id,_that.taskKey,_that.inputs,_that.config);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'task_key')  String taskKey,  Map<String, String> inputs,  Map<String, dynamic> config)  $default,) {final _that = this;
switch (_that) {
case _WorkflowStep():
return $default(_that.id,_that.taskKey,_that.inputs,_that.config);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'task_key')  String taskKey,  Map<String, String> inputs,  Map<String, dynamic> config)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowStep() when $default != null:
return $default(_that.id,_that.taskKey,_that.inputs,_that.config);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _WorkflowStep implements WorkflowStep {
  const _WorkflowStep({required this.id, @JsonKey(name: 'task_key') required this.taskKey, final  Map<String, String> inputs = const {}, final  Map<String, dynamic> config = const {}}): _inputs = inputs,_config = config;
  factory _WorkflowStep.fromJson(Map<String, dynamic> json) => _$WorkflowStepFromJson(json);

/// Unique step identifier, e.g., 'safety_check'
@override final  String id;
/// Registry Task Name (matches @register_task name)
@override@JsonKey(name: 'task_key') final  String taskKey;
/// Maps task inputs to state values. Example: {'text': '$inputs.history_text'}
 final  Map<String, String> _inputs;
/// Maps task inputs to state values. Example: {'text': '$inputs.history_text'}
@override@JsonKey() Map<String, String> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

/// Optional static config for the task
 final  Map<String, dynamic> _config;
/// Optional static config for the task
@override@JsonKey() Map<String, dynamic> get config {
  if (_config is EqualUnmodifiableMapView) return _config;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_config);
}


/// Create a copy of WorkflowStep
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowStepCopyWith<_WorkflowStep> get copyWith => __$WorkflowStepCopyWithImpl<_WorkflowStep>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowStepToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowStep&&(identical(other.id, id) || other.id == id)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&const DeepCollectionEquality().equals(other._config, _config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,taskKey,const DeepCollectionEquality().hash(_inputs),const DeepCollectionEquality().hash(_config));

@override
String toString() {
  return 'WorkflowStep(id: $id, taskKey: $taskKey, inputs: $inputs, config: $config)';
}


}

/// @nodoc
abstract mixin class _$WorkflowStepCopyWith<$Res> implements $WorkflowStepCopyWith<$Res> {
  factory _$WorkflowStepCopyWith(_WorkflowStep value, $Res Function(_WorkflowStep) _then) = __$WorkflowStepCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'task_key') String taskKey, Map<String, String> inputs, Map<String, dynamic> config
});




}
/// @nodoc
class __$WorkflowStepCopyWithImpl<$Res>
    implements _$WorkflowStepCopyWith<$Res> {
  __$WorkflowStepCopyWithImpl(this._self, this._then);

  final _WorkflowStep _self;
  final $Res Function(_WorkflowStep) _then;

/// Create a copy of WorkflowStep
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? taskKey = null,Object? inputs = null,Object? config = null,}) {
  return _then(_WorkflowStep(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,taskKey: null == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,config: null == config ? _self._config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
