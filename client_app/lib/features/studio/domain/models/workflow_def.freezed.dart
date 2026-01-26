// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_def.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WorkflowDef implements DiagnosticableTreeMixin {

 String get id; String get name; String get description; List<WorkflowStepDef> get steps;
/// Create a copy of WorkflowDef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowDefCopyWith<WorkflowDef> get copyWith => _$WorkflowDefCopyWithImpl<WorkflowDef>(this as WorkflowDef, _$identity);

  /// Serializes this WorkflowDef to a JSON map.
  Map<String, dynamic> toJson();

@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'WorkflowDef'))
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('description', description))..add(DiagnosticsProperty('steps', steps));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.steps, steps));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(steps));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'WorkflowDef(id: $id, name: $name, description: $description, steps: $steps)';
}


}

/// @nodoc
abstract mixin class $WorkflowDefCopyWith<$Res>  {
  factory $WorkflowDefCopyWith(WorkflowDef value, $Res Function(WorkflowDef) _then) = _$WorkflowDefCopyWithImpl;
@useResult
$Res call({
 String id, String name, String description, List<WorkflowStepDef> steps
});




}
/// @nodoc
class _$WorkflowDefCopyWithImpl<$Res>
    implements $WorkflowDefCopyWith<$Res> {
  _$WorkflowDefCopyWithImpl(this._self, this._then);

  final WorkflowDef _self;
  final $Res Function(WorkflowDef) _then;

/// Create a copy of WorkflowDef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = null,Object? steps = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<WorkflowStepDef>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowDef].
extension WorkflowDefPatterns on WorkflowDef {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowDef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowDef() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowDef value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowDef():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowDef value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowDef() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String description,  List<WorkflowStepDef> steps)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowDef() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.steps);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String description,  List<WorkflowStepDef> steps)  $default,) {final _that = this;
switch (_that) {
case _WorkflowDef():
return $default(_that.id,_that.name,_that.description,_that.steps);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String description,  List<WorkflowStepDef> steps)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowDef() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.steps);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _WorkflowDef with DiagnosticableTreeMixin implements WorkflowDef {
  const _WorkflowDef({required this.id, required this.name, required this.description, final  List<WorkflowStepDef> steps = const []}): _steps = steps;
  factory _WorkflowDef.fromJson(Map<String, dynamic> json) => _$WorkflowDefFromJson(json);

@override final  String id;
@override final  String name;
@override final  String description;
 final  List<WorkflowStepDef> _steps;
@override@JsonKey() List<WorkflowStepDef> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}


/// Create a copy of WorkflowDef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowDefCopyWith<_WorkflowDef> get copyWith => __$WorkflowDefCopyWithImpl<_WorkflowDef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowDefToJson(this, );
}
@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'WorkflowDef'))
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('description', description))..add(DiagnosticsProperty('steps', steps));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._steps, _steps));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(_steps));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'WorkflowDef(id: $id, name: $name, description: $description, steps: $steps)';
}


}

/// @nodoc
abstract mixin class _$WorkflowDefCopyWith<$Res> implements $WorkflowDefCopyWith<$Res> {
  factory _$WorkflowDefCopyWith(_WorkflowDef value, $Res Function(_WorkflowDef) _then) = __$WorkflowDefCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String description, List<WorkflowStepDef> steps
});




}
/// @nodoc
class __$WorkflowDefCopyWithImpl<$Res>
    implements _$WorkflowDefCopyWith<$Res> {
  __$WorkflowDefCopyWithImpl(this._self, this._then);

  final _WorkflowDef _self;
  final $Res Function(_WorkflowDef) _then;

/// Create a copy of WorkflowDef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = null,Object? steps = null,}) {
  return _then(_WorkflowDef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<WorkflowStepDef>,
  ));
}


}


/// @nodoc
mixin _$WorkflowStepDef implements DiagnosticableTreeMixin {

 String get id; String get name;@JsonKey(name: 'task_key') String get taskKey; Map<String, dynamic> get config;
/// Create a copy of WorkflowStepDef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowStepDefCopyWith<WorkflowStepDef> get copyWith => _$WorkflowStepDefCopyWithImpl<WorkflowStepDef>(this as WorkflowStepDef, _$identity);

  /// Serializes this WorkflowStepDef to a JSON map.
  Map<String, dynamic> toJson();

@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'WorkflowStepDef'))
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('taskKey', taskKey))..add(DiagnosticsProperty('config', config));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowStepDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other.config, config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,taskKey,const DeepCollectionEquality().hash(config));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'WorkflowStepDef(id: $id, name: $name, taskKey: $taskKey, config: $config)';
}


}

/// @nodoc
abstract mixin class $WorkflowStepDefCopyWith<$Res>  {
  factory $WorkflowStepDefCopyWith(WorkflowStepDef value, $Res Function(WorkflowStepDef) _then) = _$WorkflowStepDefCopyWithImpl;
@useResult
$Res call({
 String id, String name,@JsonKey(name: 'task_key') String taskKey, Map<String, dynamic> config
});




}
/// @nodoc
class _$WorkflowStepDefCopyWithImpl<$Res>
    implements $WorkflowStepDefCopyWith<$Res> {
  _$WorkflowStepDefCopyWithImpl(this._self, this._then);

  final WorkflowStepDef _self;
  final $Res Function(WorkflowStepDef) _then;

/// Create a copy of WorkflowStepDef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? taskKey = null,Object? config = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,taskKey: null == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String,config: null == config ? _self.config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowStepDef].
extension WorkflowStepDefPatterns on WorkflowStepDef {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowStepDef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowStepDef() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowStepDef value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowStepDef():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowStepDef value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowStepDef() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name, @JsonKey(name: 'task_key')  String taskKey,  Map<String, dynamic> config)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowStepDef() when $default != null:
return $default(_that.id,_that.name,_that.taskKey,_that.config);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name, @JsonKey(name: 'task_key')  String taskKey,  Map<String, dynamic> config)  $default,) {final _that = this;
switch (_that) {
case _WorkflowStepDef():
return $default(_that.id,_that.name,_that.taskKey,_that.config);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name, @JsonKey(name: 'task_key')  String taskKey,  Map<String, dynamic> config)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowStepDef() when $default != null:
return $default(_that.id,_that.name,_that.taskKey,_that.config);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _WorkflowStepDef with DiagnosticableTreeMixin implements WorkflowStepDef {
  const _WorkflowStepDef({required this.id, this.name = '', @JsonKey(name: 'task_key') required this.taskKey, final  Map<String, dynamic> config = const {}}): _config = config;
  factory _WorkflowStepDef.fromJson(Map<String, dynamic> json) => _$WorkflowStepDefFromJson(json);

@override final  String id;
@override@JsonKey() final  String name;
@override@JsonKey(name: 'task_key') final  String taskKey;
 final  Map<String, dynamic> _config;
@override@JsonKey() Map<String, dynamic> get config {
  if (_config is EqualUnmodifiableMapView) return _config;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_config);
}


/// Create a copy of WorkflowStepDef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowStepDefCopyWith<_WorkflowStepDef> get copyWith => __$WorkflowStepDefCopyWithImpl<_WorkflowStepDef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowStepDefToJson(this, );
}
@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'WorkflowStepDef'))
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('taskKey', taskKey))..add(DiagnosticsProperty('config', config));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowStepDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other._config, _config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,taskKey,const DeepCollectionEquality().hash(_config));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'WorkflowStepDef(id: $id, name: $name, taskKey: $taskKey, config: $config)';
}


}

/// @nodoc
abstract mixin class _$WorkflowStepDefCopyWith<$Res> implements $WorkflowStepDefCopyWith<$Res> {
  factory _$WorkflowStepDefCopyWith(_WorkflowStepDef value, $Res Function(_WorkflowStepDef) _then) = __$WorkflowStepDefCopyWithImpl;
@override @useResult
$Res call({
 String id, String name,@JsonKey(name: 'task_key') String taskKey, Map<String, dynamic> config
});




}
/// @nodoc
class __$WorkflowStepDefCopyWithImpl<$Res>
    implements _$WorkflowStepDefCopyWith<$Res> {
  __$WorkflowStepDefCopyWithImpl(this._self, this._then);

  final _WorkflowStepDef _self;
  final $Res Function(_WorkflowStepDef) _then;

/// Create a copy of WorkflowStepDef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? taskKey = null,Object? config = null,}) {
  return _then(_WorkflowStepDef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,taskKey: null == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String,config: null == config ? _self._config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
