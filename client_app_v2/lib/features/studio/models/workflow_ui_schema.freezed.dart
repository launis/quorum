// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_ui_schema.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WorkflowUiSchema {

@JsonKey(name: 'expected_inputs') List<ExpectedInput> get expectedInputs;
/// Create a copy of WorkflowUiSchema
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowUiSchemaCopyWith<WorkflowUiSchema> get copyWith => _$WorkflowUiSchemaCopyWithImpl<WorkflowUiSchema>(this as WorkflowUiSchema, _$identity);

  /// Serializes this WorkflowUiSchema to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'WorkflowUiSchema(expectedInputs: $expectedInputs)';
}


}

/// @nodoc
abstract mixin class $WorkflowUiSchemaCopyWith<$Res>  {
  factory $WorkflowUiSchemaCopyWith(WorkflowUiSchema value, $Res Function(WorkflowUiSchema) _then) = _$WorkflowUiSchemaCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'expected_inputs') List<ExpectedInput> expectedInputs
});




}
/// @nodoc
class _$WorkflowUiSchemaCopyWithImpl<$Res>
    implements $WorkflowUiSchemaCopyWith<$Res> {
  _$WorkflowUiSchemaCopyWithImpl(this._self, this._then);

  final WorkflowUiSchema _self;
  final $Res Function(WorkflowUiSchema) _then;

/// Create a copy of WorkflowUiSchema
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? expectedInputs = null,}) {
  return _then(_self.copyWith(
expectedInputs: null == expectedInputs ? _self.expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<ExpectedInput>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowUiSchema].
extension WorkflowUiSchemaPatterns on WorkflowUiSchema {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowUiSchema value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowUiSchema() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowUiSchema value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowUiSchema():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowUiSchema value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowUiSchema() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'expected_inputs')  List<ExpectedInput> expectedInputs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowUiSchema() when $default != null:
return $default(_that.expectedInputs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'expected_inputs')  List<ExpectedInput> expectedInputs)  $default,) {final _that = this;
switch (_that) {
case _WorkflowUiSchema():
return $default(_that.expectedInputs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'expected_inputs')  List<ExpectedInput> expectedInputs)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowUiSchema() when $default != null:
return $default(_that.expectedInputs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _WorkflowUiSchema implements WorkflowUiSchema {
  const _WorkflowUiSchema({@JsonKey(name: 'expected_inputs') final  List<ExpectedInput> expectedInputs = const []}): _expectedInputs = expectedInputs;
  factory _WorkflowUiSchema.fromJson(Map<String, dynamic> json) => _$WorkflowUiSchemaFromJson(json);

 final  List<ExpectedInput> _expectedInputs;
@override@JsonKey(name: 'expected_inputs') List<ExpectedInput> get expectedInputs {
  if (_expectedInputs is EqualUnmodifiableListView) return _expectedInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_expectedInputs);
}


/// Create a copy of WorkflowUiSchema
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowUiSchemaCopyWith<_WorkflowUiSchema> get copyWith => __$WorkflowUiSchemaCopyWithImpl<_WorkflowUiSchema>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowUiSchemaToJson(this, );
}



@override
String toString() {
  return 'WorkflowUiSchema(expectedInputs: $expectedInputs)';
}


}

/// @nodoc
abstract mixin class _$WorkflowUiSchemaCopyWith<$Res> implements $WorkflowUiSchemaCopyWith<$Res> {
  factory _$WorkflowUiSchemaCopyWith(_WorkflowUiSchema value, $Res Function(_WorkflowUiSchema) _then) = __$WorkflowUiSchemaCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'expected_inputs') List<ExpectedInput> expectedInputs
});




}
/// @nodoc
class __$WorkflowUiSchemaCopyWithImpl<$Res>
    implements _$WorkflowUiSchemaCopyWith<$Res> {
  __$WorkflowUiSchemaCopyWithImpl(this._self, this._then);

  final _WorkflowUiSchema _self;
  final $Res Function(_WorkflowUiSchema) _then;

/// Create a copy of WorkflowUiSchema
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? expectedInputs = null,}) {
  return _then(_WorkflowUiSchema(
expectedInputs: null == expectedInputs ? _self._expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<ExpectedInput>,
  ));
}


}

// dart format on
