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

 String get id; String get name; String get description; List<WorkflowStepDef> get steps;@JsonKey(name: 'scoring_logic') List<ScoringLogic> get scoringLogic;@JsonKey(name: 'ui_schema') Map<String, dynamic> get uiSchema;
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
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('description', description))..add(DiagnosticsProperty('steps', steps))..add(DiagnosticsProperty('scoringLogic', scoringLogic))..add(DiagnosticsProperty('uiSchema', uiSchema));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.steps, steps)&&const DeepCollectionEquality().equals(other.scoringLogic, scoringLogic)&&const DeepCollectionEquality().equals(other.uiSchema, uiSchema));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(steps),const DeepCollectionEquality().hash(scoringLogic),const DeepCollectionEquality().hash(uiSchema));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'WorkflowDef(id: $id, name: $name, description: $description, steps: $steps, scoringLogic: $scoringLogic, uiSchema: $uiSchema)';
}


}

/// @nodoc
abstract mixin class $WorkflowDefCopyWith<$Res>  {
  factory $WorkflowDefCopyWith(WorkflowDef value, $Res Function(WorkflowDef) _then) = _$WorkflowDefCopyWithImpl;
@useResult
$Res call({
 String id, String name, String description, List<WorkflowStepDef> steps,@JsonKey(name: 'scoring_logic') List<ScoringLogic> scoringLogic,@JsonKey(name: 'ui_schema') Map<String, dynamic> uiSchema
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = null,Object? steps = null,Object? scoringLogic = null,Object? uiSchema = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<WorkflowStepDef>,scoringLogic: null == scoringLogic ? _self.scoringLogic : scoringLogic // ignore: cast_nullable_to_non_nullable
as List<ScoringLogic>,uiSchema: null == uiSchema ? _self.uiSchema : uiSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String description,  List<WorkflowStepDef> steps, @JsonKey(name: 'scoring_logic')  List<ScoringLogic> scoringLogic, @JsonKey(name: 'ui_schema')  Map<String, dynamic> uiSchema)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowDef() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.steps,_that.scoringLogic,_that.uiSchema);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String description,  List<WorkflowStepDef> steps, @JsonKey(name: 'scoring_logic')  List<ScoringLogic> scoringLogic, @JsonKey(name: 'ui_schema')  Map<String, dynamic> uiSchema)  $default,) {final _that = this;
switch (_that) {
case _WorkflowDef():
return $default(_that.id,_that.name,_that.description,_that.steps,_that.scoringLogic,_that.uiSchema);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String description,  List<WorkflowStepDef> steps, @JsonKey(name: 'scoring_logic')  List<ScoringLogic> scoringLogic, @JsonKey(name: 'ui_schema')  Map<String, dynamic> uiSchema)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowDef() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.steps,_that.scoringLogic,_that.uiSchema);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _WorkflowDef with DiagnosticableTreeMixin implements WorkflowDef {
  const _WorkflowDef({required this.id, required this.name, required this.description, final  List<WorkflowStepDef> steps = const [], @JsonKey(name: 'scoring_logic') final  List<ScoringLogic> scoringLogic = const [], @JsonKey(name: 'ui_schema') final  Map<String, dynamic> uiSchema = const {}}): _steps = steps,_scoringLogic = scoringLogic,_uiSchema = uiSchema;
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

 final  List<ScoringLogic> _scoringLogic;
@override@JsonKey(name: 'scoring_logic') List<ScoringLogic> get scoringLogic {
  if (_scoringLogic is EqualUnmodifiableListView) return _scoringLogic;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_scoringLogic);
}

 final  Map<String, dynamic> _uiSchema;
@override@JsonKey(name: 'ui_schema') Map<String, dynamic> get uiSchema {
  if (_uiSchema is EqualUnmodifiableMapView) return _uiSchema;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_uiSchema);
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
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('description', description))..add(DiagnosticsProperty('steps', steps))..add(DiagnosticsProperty('scoringLogic', scoringLogic))..add(DiagnosticsProperty('uiSchema', uiSchema));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._steps, _steps)&&const DeepCollectionEquality().equals(other._scoringLogic, _scoringLogic)&&const DeepCollectionEquality().equals(other._uiSchema, _uiSchema));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(_steps),const DeepCollectionEquality().hash(_scoringLogic),const DeepCollectionEquality().hash(_uiSchema));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'WorkflowDef(id: $id, name: $name, description: $description, steps: $steps, scoringLogic: $scoringLogic, uiSchema: $uiSchema)';
}


}

/// @nodoc
abstract mixin class _$WorkflowDefCopyWith<$Res> implements $WorkflowDefCopyWith<$Res> {
  factory _$WorkflowDefCopyWith(_WorkflowDef value, $Res Function(_WorkflowDef) _then) = __$WorkflowDefCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String description, List<WorkflowStepDef> steps,@JsonKey(name: 'scoring_logic') List<ScoringLogic> scoringLogic,@JsonKey(name: 'ui_schema') Map<String, dynamic> uiSchema
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = null,Object? steps = null,Object? scoringLogic = null,Object? uiSchema = null,}) {
  return _then(_WorkflowDef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<WorkflowStepDef>,scoringLogic: null == scoringLogic ? _self._scoringLogic : scoringLogic // ignore: cast_nullable_to_non_nullable
as List<ScoringLogic>,uiSchema: null == uiSchema ? _self._uiSchema : uiSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
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


/// @nodoc
mixin _$ComponentScoringRule implements DiagnosticableTreeMixin {

@JsonKey(name: 'component_id') String get componentId; double get weight;@JsonKey(name: 'metric_key') String get metricKey;
/// Create a copy of ComponentScoringRule
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ComponentScoringRuleCopyWith<ComponentScoringRule> get copyWith => _$ComponentScoringRuleCopyWithImpl<ComponentScoringRule>(this as ComponentScoringRule, _$identity);

  /// Serializes this ComponentScoringRule to a JSON map.
  Map<String, dynamic> toJson();

@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ComponentScoringRule'))
    ..add(DiagnosticsProperty('componentId', componentId))..add(DiagnosticsProperty('weight', weight))..add(DiagnosticsProperty('metricKey', metricKey));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ComponentScoringRule&&(identical(other.componentId, componentId) || other.componentId == componentId)&&(identical(other.weight, weight) || other.weight == weight)&&(identical(other.metricKey, metricKey) || other.metricKey == metricKey));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,componentId,weight,metricKey);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ComponentScoringRule(componentId: $componentId, weight: $weight, metricKey: $metricKey)';
}


}

/// @nodoc
abstract mixin class $ComponentScoringRuleCopyWith<$Res>  {
  factory $ComponentScoringRuleCopyWith(ComponentScoringRule value, $Res Function(ComponentScoringRule) _then) = _$ComponentScoringRuleCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'component_id') String componentId, double weight,@JsonKey(name: 'metric_key') String metricKey
});




}
/// @nodoc
class _$ComponentScoringRuleCopyWithImpl<$Res>
    implements $ComponentScoringRuleCopyWith<$Res> {
  _$ComponentScoringRuleCopyWithImpl(this._self, this._then);

  final ComponentScoringRule _self;
  final $Res Function(ComponentScoringRule) _then;

/// Create a copy of ComponentScoringRule
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? componentId = null,Object? weight = null,Object? metricKey = null,}) {
  return _then(_self.copyWith(
componentId: null == componentId ? _self.componentId : componentId // ignore: cast_nullable_to_non_nullable
as String,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,metricKey: null == metricKey ? _self.metricKey : metricKey // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ComponentScoringRule].
extension ComponentScoringRulePatterns on ComponentScoringRule {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ComponentScoringRule value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ComponentScoringRule() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ComponentScoringRule value)  $default,){
final _that = this;
switch (_that) {
case _ComponentScoringRule():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ComponentScoringRule value)?  $default,){
final _that = this;
switch (_that) {
case _ComponentScoringRule() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'component_id')  String componentId,  double weight, @JsonKey(name: 'metric_key')  String metricKey)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ComponentScoringRule() when $default != null:
return $default(_that.componentId,_that.weight,_that.metricKey);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'component_id')  String componentId,  double weight, @JsonKey(name: 'metric_key')  String metricKey)  $default,) {final _that = this;
switch (_that) {
case _ComponentScoringRule():
return $default(_that.componentId,_that.weight,_that.metricKey);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'component_id')  String componentId,  double weight, @JsonKey(name: 'metric_key')  String metricKey)?  $default,) {final _that = this;
switch (_that) {
case _ComponentScoringRule() when $default != null:
return $default(_that.componentId,_that.weight,_that.metricKey);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ComponentScoringRule with DiagnosticableTreeMixin implements ComponentScoringRule {
  const _ComponentScoringRule({@JsonKey(name: 'component_id') required this.componentId, this.weight = 1.0, @JsonKey(name: 'metric_key') required this.metricKey});
  factory _ComponentScoringRule.fromJson(Map<String, dynamic> json) => _$ComponentScoringRuleFromJson(json);

@override@JsonKey(name: 'component_id') final  String componentId;
@override@JsonKey() final  double weight;
@override@JsonKey(name: 'metric_key') final  String metricKey;

/// Create a copy of ComponentScoringRule
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ComponentScoringRuleCopyWith<_ComponentScoringRule> get copyWith => __$ComponentScoringRuleCopyWithImpl<_ComponentScoringRule>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ComponentScoringRuleToJson(this, );
}
@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ComponentScoringRule'))
    ..add(DiagnosticsProperty('componentId', componentId))..add(DiagnosticsProperty('weight', weight))..add(DiagnosticsProperty('metricKey', metricKey));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ComponentScoringRule&&(identical(other.componentId, componentId) || other.componentId == componentId)&&(identical(other.weight, weight) || other.weight == weight)&&(identical(other.metricKey, metricKey) || other.metricKey == metricKey));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,componentId,weight,metricKey);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ComponentScoringRule(componentId: $componentId, weight: $weight, metricKey: $metricKey)';
}


}

/// @nodoc
abstract mixin class _$ComponentScoringRuleCopyWith<$Res> implements $ComponentScoringRuleCopyWith<$Res> {
  factory _$ComponentScoringRuleCopyWith(_ComponentScoringRule value, $Res Function(_ComponentScoringRule) _then) = __$ComponentScoringRuleCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'component_id') String componentId, double weight,@JsonKey(name: 'metric_key') String metricKey
});




}
/// @nodoc
class __$ComponentScoringRuleCopyWithImpl<$Res>
    implements _$ComponentScoringRuleCopyWith<$Res> {
  __$ComponentScoringRuleCopyWithImpl(this._self, this._then);

  final _ComponentScoringRule _self;
  final $Res Function(_ComponentScoringRule) _then;

/// Create a copy of ComponentScoringRule
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? componentId = null,Object? weight = null,Object? metricKey = null,}) {
  return _then(_ComponentScoringRule(
componentId: null == componentId ? _self.componentId : componentId // ignore: cast_nullable_to_non_nullable
as String,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,metricKey: null == metricKey ? _self.metricKey : metricKey // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ScoringLogic implements DiagnosticableTreeMixin {

 String get label; List<ComponentScoringRule> get rules;
/// Create a copy of ScoringLogic
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScoringLogicCopyWith<ScoringLogic> get copyWith => _$ScoringLogicCopyWithImpl<ScoringLogic>(this as ScoringLogic, _$identity);

  /// Serializes this ScoringLogic to a JSON map.
  Map<String, dynamic> toJson();

@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ScoringLogic'))
    ..add(DiagnosticsProperty('label', label))..add(DiagnosticsProperty('rules', rules));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ScoringLogic&&(identical(other.label, label) || other.label == label)&&const DeepCollectionEquality().equals(other.rules, rules));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,label,const DeepCollectionEquality().hash(rules));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ScoringLogic(label: $label, rules: $rules)';
}


}

/// @nodoc
abstract mixin class $ScoringLogicCopyWith<$Res>  {
  factory $ScoringLogicCopyWith(ScoringLogic value, $Res Function(ScoringLogic) _then) = _$ScoringLogicCopyWithImpl;
@useResult
$Res call({
 String label, List<ComponentScoringRule> rules
});




}
/// @nodoc
class _$ScoringLogicCopyWithImpl<$Res>
    implements $ScoringLogicCopyWith<$Res> {
  _$ScoringLogicCopyWithImpl(this._self, this._then);

  final ScoringLogic _self;
  final $Res Function(ScoringLogic) _then;

/// Create a copy of ScoringLogic
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? label = null,Object? rules = null,}) {
  return _then(_self.copyWith(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,rules: null == rules ? _self.rules : rules // ignore: cast_nullable_to_non_nullable
as List<ComponentScoringRule>,
  ));
}

}


/// Adds pattern-matching-related methods to [ScoringLogic].
extension ScoringLogicPatterns on ScoringLogic {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScoringLogic value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScoringLogic() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScoringLogic value)  $default,){
final _that = this;
switch (_that) {
case _ScoringLogic():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScoringLogic value)?  $default,){
final _that = this;
switch (_that) {
case _ScoringLogic() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String label,  List<ComponentScoringRule> rules)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScoringLogic() when $default != null:
return $default(_that.label,_that.rules);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String label,  List<ComponentScoringRule> rules)  $default,) {final _that = this;
switch (_that) {
case _ScoringLogic():
return $default(_that.label,_that.rules);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String label,  List<ComponentScoringRule> rules)?  $default,) {final _that = this;
switch (_that) {
case _ScoringLogic() when $default != null:
return $default(_that.label,_that.rules);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ScoringLogic with DiagnosticableTreeMixin implements ScoringLogic {
  const _ScoringLogic({required this.label, final  List<ComponentScoringRule> rules = const []}): _rules = rules;
  factory _ScoringLogic.fromJson(Map<String, dynamic> json) => _$ScoringLogicFromJson(json);

@override final  String label;
 final  List<ComponentScoringRule> _rules;
@override@JsonKey() List<ComponentScoringRule> get rules {
  if (_rules is EqualUnmodifiableListView) return _rules;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_rules);
}


/// Create a copy of ScoringLogic
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScoringLogicCopyWith<_ScoringLogic> get copyWith => __$ScoringLogicCopyWithImpl<_ScoringLogic>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ScoringLogicToJson(this, );
}
@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ScoringLogic'))
    ..add(DiagnosticsProperty('label', label))..add(DiagnosticsProperty('rules', rules));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ScoringLogic&&(identical(other.label, label) || other.label == label)&&const DeepCollectionEquality().equals(other._rules, _rules));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,label,const DeepCollectionEquality().hash(_rules));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ScoringLogic(label: $label, rules: $rules)';
}


}

/// @nodoc
abstract mixin class _$ScoringLogicCopyWith<$Res> implements $ScoringLogicCopyWith<$Res> {
  factory _$ScoringLogicCopyWith(_ScoringLogic value, $Res Function(_ScoringLogic) _then) = __$ScoringLogicCopyWithImpl;
@override @useResult
$Res call({
 String label, List<ComponentScoringRule> rules
});




}
/// @nodoc
class __$ScoringLogicCopyWithImpl<$Res>
    implements _$ScoringLogicCopyWith<$Res> {
  __$ScoringLogicCopyWithImpl(this._self, this._then);

  final _ScoringLogic _self;
  final $Res Function(_ScoringLogic) _then;

/// Create a copy of ScoringLogic
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? label = null,Object? rules = null,}) {
  return _then(_ScoringLogic(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,rules: null == rules ? _self._rules : rules // ignore: cast_nullable_to_non_nullable
as List<ComponentScoringRule>,
  ));
}


}


/// @nodoc
mixin _$ComponentDef implements DiagnosticableTreeMixin {

 String get id; String get name; String get type; String? get description; dynamic get content; String? get citation;
/// Create a copy of ComponentDef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ComponentDefCopyWith<ComponentDef> get copyWith => _$ComponentDefCopyWithImpl<ComponentDef>(this as ComponentDef, _$identity);

  /// Serializes this ComponentDef to a JSON map.
  Map<String, dynamic> toJson();

@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ComponentDef'))
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('type', type))..add(DiagnosticsProperty('description', description))..add(DiagnosticsProperty('content', content))..add(DiagnosticsProperty('citation', citation));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ComponentDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.content, content)&&(identical(other.citation, citation) || other.citation == citation));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,type,description,const DeepCollectionEquality().hash(content),citation);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ComponentDef(id: $id, name: $name, type: $type, description: $description, content: $content, citation: $citation)';
}


}

/// @nodoc
abstract mixin class $ComponentDefCopyWith<$Res>  {
  factory $ComponentDefCopyWith(ComponentDef value, $Res Function(ComponentDef) _then) = _$ComponentDefCopyWithImpl;
@useResult
$Res call({
 String id, String name, String type, String? description, dynamic content, String? citation
});




}
/// @nodoc
class _$ComponentDefCopyWithImpl<$Res>
    implements $ComponentDefCopyWith<$Res> {
  _$ComponentDefCopyWithImpl(this._self, this._then);

  final ComponentDef _self;
  final $Res Function(ComponentDef) _then;

/// Create a copy of ComponentDef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? type = null,Object? description = freezed,Object? content = freezed,Object? citation = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,content: freezed == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as dynamic,citation: freezed == citation ? _self.citation : citation // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ComponentDef].
extension ComponentDefPatterns on ComponentDef {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ComponentDef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ComponentDef() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ComponentDef value)  $default,){
final _that = this;
switch (_that) {
case _ComponentDef():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ComponentDef value)?  $default,){
final _that = this;
switch (_that) {
case _ComponentDef() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String type,  String? description,  dynamic content,  String? citation)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ComponentDef() when $default != null:
return $default(_that.id,_that.name,_that.type,_that.description,_that.content,_that.citation);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String type,  String? description,  dynamic content,  String? citation)  $default,) {final _that = this;
switch (_that) {
case _ComponentDef():
return $default(_that.id,_that.name,_that.type,_that.description,_that.content,_that.citation);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String type,  String? description,  dynamic content,  String? citation)?  $default,) {final _that = this;
switch (_that) {
case _ComponentDef() when $default != null:
return $default(_that.id,_that.name,_that.type,_that.description,_that.content,_that.citation);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ComponentDef with DiagnosticableTreeMixin implements ComponentDef {
  const _ComponentDef({required this.id, required this.name, required this.type, this.description, this.content, this.citation});
  factory _ComponentDef.fromJson(Map<String, dynamic> json) => _$ComponentDefFromJson(json);

@override final  String id;
@override final  String name;
@override final  String type;
@override final  String? description;
@override final  dynamic content;
@override final  String? citation;

/// Create a copy of ComponentDef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ComponentDefCopyWith<_ComponentDef> get copyWith => __$ComponentDefCopyWithImpl<_ComponentDef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ComponentDefToJson(this, );
}
@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ComponentDef'))
    ..add(DiagnosticsProperty('id', id))..add(DiagnosticsProperty('name', name))..add(DiagnosticsProperty('type', type))..add(DiagnosticsProperty('description', description))..add(DiagnosticsProperty('content', content))..add(DiagnosticsProperty('citation', citation));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ComponentDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.content, content)&&(identical(other.citation, citation) || other.citation == citation));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,type,description,const DeepCollectionEquality().hash(content),citation);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ComponentDef(id: $id, name: $name, type: $type, description: $description, content: $content, citation: $citation)';
}


}

/// @nodoc
abstract mixin class _$ComponentDefCopyWith<$Res> implements $ComponentDefCopyWith<$Res> {
  factory _$ComponentDefCopyWith(_ComponentDef value, $Res Function(_ComponentDef) _then) = __$ComponentDefCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String type, String? description, dynamic content, String? citation
});




}
/// @nodoc
class __$ComponentDefCopyWithImpl<$Res>
    implements _$ComponentDefCopyWith<$Res> {
  __$ComponentDefCopyWithImpl(this._self, this._then);

  final _ComponentDef _self;
  final $Res Function(_ComponentDef) _then;

/// Create a copy of ComponentDef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? type = null,Object? description = freezed,Object? content = freezed,Object? citation = freezed,}) {
  return _then(_ComponentDef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,content: freezed == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as dynamic,citation: freezed == citation ? _self.citation : citation // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
