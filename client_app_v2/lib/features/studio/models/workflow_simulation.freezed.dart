// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_simulation.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WorkflowSimulationResponse {

 bool get valid; List<String> get errors;@JsonKey(name: 'step_status') Map<String, String> get stepStatus;@JsonKey(name: 'execution_order') List<String> get executionOrder; Map<String, dynamic> get trace;
/// Create a copy of WorkflowSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowSimulationResponseCopyWith<WorkflowSimulationResponse> get copyWith => _$WorkflowSimulationResponseCopyWithImpl<WorkflowSimulationResponse>(this as WorkflowSimulationResponse, _$identity);

  /// Serializes this WorkflowSimulationResponse to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'WorkflowSimulationResponse(valid: $valid, errors: $errors, stepStatus: $stepStatus, executionOrder: $executionOrder, trace: $trace)';
}


}

/// @nodoc
abstract mixin class $WorkflowSimulationResponseCopyWith<$Res>  {
  factory $WorkflowSimulationResponseCopyWith(WorkflowSimulationResponse value, $Res Function(WorkflowSimulationResponse) _then) = _$WorkflowSimulationResponseCopyWithImpl;
@useResult
$Res call({
 bool valid, List<String> errors,@JsonKey(name: 'step_status') Map<String, String> stepStatus,@JsonKey(name: 'execution_order') List<String> executionOrder, Map<String, dynamic> trace
});




}
/// @nodoc
class _$WorkflowSimulationResponseCopyWithImpl<$Res>
    implements $WorkflowSimulationResponseCopyWith<$Res> {
  _$WorkflowSimulationResponseCopyWithImpl(this._self, this._then);

  final WorkflowSimulationResponse _self;
  final $Res Function(WorkflowSimulationResponse) _then;

/// Create a copy of WorkflowSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? valid = null,Object? errors = null,Object? stepStatus = null,Object? executionOrder = null,Object? trace = null,}) {
  return _then(_self.copyWith(
valid: null == valid ? _self.valid : valid // ignore: cast_nullable_to_non_nullable
as bool,errors: null == errors ? _self.errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>,stepStatus: null == stepStatus ? _self.stepStatus : stepStatus // ignore: cast_nullable_to_non_nullable
as Map<String, String>,executionOrder: null == executionOrder ? _self.executionOrder : executionOrder // ignore: cast_nullable_to_non_nullable
as List<String>,trace: null == trace ? _self.trace : trace // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowSimulationResponse].
extension WorkflowSimulationResponsePatterns on WorkflowSimulationResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowSimulationResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowSimulationResponse value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowSimulationResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowSimulationResponse value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool valid,  List<String> errors, @JsonKey(name: 'step_status')  Map<String, String> stepStatus, @JsonKey(name: 'execution_order')  List<String> executionOrder,  Map<String, dynamic> trace)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowSimulationResponse() when $default != null:
return $default(_that.valid,_that.errors,_that.stepStatus,_that.executionOrder,_that.trace);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool valid,  List<String> errors, @JsonKey(name: 'step_status')  Map<String, String> stepStatus, @JsonKey(name: 'execution_order')  List<String> executionOrder,  Map<String, dynamic> trace)  $default,) {final _that = this;
switch (_that) {
case _WorkflowSimulationResponse():
return $default(_that.valid,_that.errors,_that.stepStatus,_that.executionOrder,_that.trace);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool valid,  List<String> errors, @JsonKey(name: 'step_status')  Map<String, String> stepStatus, @JsonKey(name: 'execution_order')  List<String> executionOrder,  Map<String, dynamic> trace)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowSimulationResponse() when $default != null:
return $default(_that.valid,_that.errors,_that.stepStatus,_that.executionOrder,_that.trace);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _WorkflowSimulationResponse implements WorkflowSimulationResponse {
  const _WorkflowSimulationResponse({this.valid = true, final  List<String> errors = const [], @JsonKey(name: 'step_status') final  Map<String, String> stepStatus = const {}, @JsonKey(name: 'execution_order') final  List<String> executionOrder = const [], final  Map<String, dynamic> trace = const {}}): _errors = errors,_stepStatus = stepStatus,_executionOrder = executionOrder,_trace = trace;
  factory _WorkflowSimulationResponse.fromJson(Map<String, dynamic> json) => _$WorkflowSimulationResponseFromJson(json);

@override@JsonKey() final  bool valid;
 final  List<String> _errors;
@override@JsonKey() List<String> get errors {
  if (_errors is EqualUnmodifiableListView) return _errors;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_errors);
}

 final  Map<String, String> _stepStatus;
@override@JsonKey(name: 'step_status') Map<String, String> get stepStatus {
  if (_stepStatus is EqualUnmodifiableMapView) return _stepStatus;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_stepStatus);
}

 final  List<String> _executionOrder;
@override@JsonKey(name: 'execution_order') List<String> get executionOrder {
  if (_executionOrder is EqualUnmodifiableListView) return _executionOrder;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_executionOrder);
}

 final  Map<String, dynamic> _trace;
@override@JsonKey() Map<String, dynamic> get trace {
  if (_trace is EqualUnmodifiableMapView) return _trace;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_trace);
}


/// Create a copy of WorkflowSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowSimulationResponseCopyWith<_WorkflowSimulationResponse> get copyWith => __$WorkflowSimulationResponseCopyWithImpl<_WorkflowSimulationResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowSimulationResponseToJson(this, );
}



@override
String toString() {
  return 'WorkflowSimulationResponse(valid: $valid, errors: $errors, stepStatus: $stepStatus, executionOrder: $executionOrder, trace: $trace)';
}


}

/// @nodoc
abstract mixin class _$WorkflowSimulationResponseCopyWith<$Res> implements $WorkflowSimulationResponseCopyWith<$Res> {
  factory _$WorkflowSimulationResponseCopyWith(_WorkflowSimulationResponse value, $Res Function(_WorkflowSimulationResponse) _then) = __$WorkflowSimulationResponseCopyWithImpl;
@override @useResult
$Res call({
 bool valid, List<String> errors,@JsonKey(name: 'step_status') Map<String, String> stepStatus,@JsonKey(name: 'execution_order') List<String> executionOrder, Map<String, dynamic> trace
});




}
/// @nodoc
class __$WorkflowSimulationResponseCopyWithImpl<$Res>
    implements _$WorkflowSimulationResponseCopyWith<$Res> {
  __$WorkflowSimulationResponseCopyWithImpl(this._self, this._then);

  final _WorkflowSimulationResponse _self;
  final $Res Function(_WorkflowSimulationResponse) _then;

/// Create a copy of WorkflowSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? valid = null,Object? errors = null,Object? stepStatus = null,Object? executionOrder = null,Object? trace = null,}) {
  return _then(_WorkflowSimulationResponse(
valid: null == valid ? _self.valid : valid // ignore: cast_nullable_to_non_nullable
as bool,errors: null == errors ? _self._errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>,stepStatus: null == stepStatus ? _self._stepStatus : stepStatus // ignore: cast_nullable_to_non_nullable
as Map<String, String>,executionOrder: null == executionOrder ? _self._executionOrder : executionOrder // ignore: cast_nullable_to_non_nullable
as List<String>,trace: null == trace ? _self._trace : trace // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
