// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_inputs.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WorkflowInputs {

@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'user_id') String? get userId;@JsonKey(name: 'simulation_mode') bool get simulationMode; String get language;@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> get dynamicInputs;
/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<WorkflowInputs> get copyWith => _$WorkflowInputsCopyWithImpl<WorkflowInputs>(this as WorkflowInputs, _$identity);

  /// Serializes this WorkflowInputs to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'WorkflowInputs(organizationId: $organizationId, userId: $userId, simulationMode: $simulationMode, language: $language, dynamicInputs: $dynamicInputs)';
}


}

/// @nodoc
abstract mixin class $WorkflowInputsCopyWith<$Res>  {
  factory $WorkflowInputsCopyWith(WorkflowInputs value, $Res Function(WorkflowInputs) _then) = _$WorkflowInputsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'simulation_mode') bool simulationMode, String language,@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> dynamicInputs
});




}
/// @nodoc
class _$WorkflowInputsCopyWithImpl<$Res>
    implements $WorkflowInputsCopyWith<$Res> {
  _$WorkflowInputsCopyWithImpl(this._self, this._then);

  final WorkflowInputs _self;
  final $Res Function(WorkflowInputs) _then;

/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? organizationId = freezed,Object? userId = freezed,Object? simulationMode = null,Object? language = null,Object? dynamicInputs = null,}) {
  return _then(_self.copyWith(
organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,simulationMode: null == simulationMode ? _self.simulationMode : simulationMode // ignore: cast_nullable_to_non_nullable
as bool,language: null == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String,dynamicInputs: null == dynamicInputs ? _self.dynamicInputs : dynamicInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowInputs].
extension WorkflowInputsPatterns on WorkflowInputs {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowInputs value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowInputs value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowInputs():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowInputs value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'simulation_mode')  bool simulationMode,  String language, @JsonKey(name: 'dynamic_inputs')  Map<String, dynamic> dynamicInputs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
return $default(_that.organizationId,_that.userId,_that.simulationMode,_that.language,_that.dynamicInputs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'simulation_mode')  bool simulationMode,  String language, @JsonKey(name: 'dynamic_inputs')  Map<String, dynamic> dynamicInputs)  $default,) {final _that = this;
switch (_that) {
case _WorkflowInputs():
return $default(_that.organizationId,_that.userId,_that.simulationMode,_that.language,_that.dynamicInputs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'simulation_mode')  bool simulationMode,  String language, @JsonKey(name: 'dynamic_inputs')  Map<String, dynamic> dynamicInputs)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
return $default(_that.organizationId,_that.userId,_that.simulationMode,_that.language,_that.dynamicInputs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _WorkflowInputs extends WorkflowInputs {
  const _WorkflowInputs({@JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, @JsonKey(name: 'simulation_mode') this.simulationMode = false, this.language = 'en', @JsonKey(name: 'dynamic_inputs') final  Map<String, dynamic> dynamicInputs = const {}}): _dynamicInputs = dynamicInputs,super._();
  factory _WorkflowInputs.fromJson(Map<String, dynamic> json) => _$WorkflowInputsFromJson(json);

@override@JsonKey(name: 'organization_id') final  String? organizationId;
@override@JsonKey(name: 'user_id') final  String? userId;
@override@JsonKey(name: 'simulation_mode') final  bool simulationMode;
@override@JsonKey() final  String language;
 final  Map<String, dynamic> _dynamicInputs;
@override@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> get dynamicInputs {
  if (_dynamicInputs is EqualUnmodifiableMapView) return _dynamicInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_dynamicInputs);
}


/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowInputsCopyWith<_WorkflowInputs> get copyWith => __$WorkflowInputsCopyWithImpl<_WorkflowInputs>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowInputsToJson(this, );
}



@override
String toString() {
  return 'WorkflowInputs(organizationId: $organizationId, userId: $userId, simulationMode: $simulationMode, language: $language, dynamicInputs: $dynamicInputs)';
}


}

/// @nodoc
abstract mixin class _$WorkflowInputsCopyWith<$Res> implements $WorkflowInputsCopyWith<$Res> {
  factory _$WorkflowInputsCopyWith(_WorkflowInputs value, $Res Function(_WorkflowInputs) _then) = __$WorkflowInputsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'simulation_mode') bool simulationMode, String language,@JsonKey(name: 'dynamic_inputs') Map<String, dynamic> dynamicInputs
});




}
/// @nodoc
class __$WorkflowInputsCopyWithImpl<$Res>
    implements _$WorkflowInputsCopyWith<$Res> {
  __$WorkflowInputsCopyWithImpl(this._self, this._then);

  final _WorkflowInputs _self;
  final $Res Function(_WorkflowInputs) _then;

/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? organizationId = freezed,Object? userId = freezed,Object? simulationMode = null,Object? language = null,Object? dynamicInputs = null,}) {
  return _then(_WorkflowInputs(
organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,simulationMode: null == simulationMode ? _self.simulationMode : simulationMode // ignore: cast_nullable_to_non_nullable
as bool,language: null == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String,dynamicInputs: null == dynamicInputs ? _self._dynamicInputs : dynamicInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
