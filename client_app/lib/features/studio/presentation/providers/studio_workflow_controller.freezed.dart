// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'studio_workflow_controller.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$WorkflowEditorState {

 JsonSchema? get schema; Map<String, dynamic>? get data; bool get isSaving; String? get lastError;
/// Create a copy of WorkflowEditorState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowEditorStateCopyWith<WorkflowEditorState> get copyWith => _$WorkflowEditorStateCopyWithImpl<WorkflowEditorState>(this as WorkflowEditorState, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowEditorState&&(identical(other.schema, schema) || other.schema == schema)&&const DeepCollectionEquality().equals(other.data, data)&&(identical(other.isSaving, isSaving) || other.isSaving == isSaving)&&(identical(other.lastError, lastError) || other.lastError == lastError));
}


@override
int get hashCode => Object.hash(runtimeType,schema,const DeepCollectionEquality().hash(data),isSaving,lastError);

@override
String toString() {
  return 'WorkflowEditorState(schema: $schema, data: $data, isSaving: $isSaving, lastError: $lastError)';
}


}

/// @nodoc
abstract mixin class $WorkflowEditorStateCopyWith<$Res>  {
  factory $WorkflowEditorStateCopyWith(WorkflowEditorState value, $Res Function(WorkflowEditorState) _then) = _$WorkflowEditorStateCopyWithImpl;
@useResult
$Res call({
 JsonSchema? schema, Map<String, dynamic>? data, bool isSaving, String? lastError
});


$JsonSchemaCopyWith<$Res>? get schema;

}
/// @nodoc
class _$WorkflowEditorStateCopyWithImpl<$Res>
    implements $WorkflowEditorStateCopyWith<$Res> {
  _$WorkflowEditorStateCopyWithImpl(this._self, this._then);

  final WorkflowEditorState _self;
  final $Res Function(WorkflowEditorState) _then;

/// Create a copy of WorkflowEditorState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? schema = freezed,Object? data = freezed,Object? isSaving = null,Object? lastError = freezed,}) {
  return _then(_self.copyWith(
schema: freezed == schema ? _self.schema : schema // ignore: cast_nullable_to_non_nullable
as JsonSchema?,data: freezed == data ? _self.data : data // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,isSaving: null == isSaving ? _self.isSaving : isSaving // ignore: cast_nullable_to_non_nullable
as bool,lastError: freezed == lastError ? _self.lastError : lastError // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of WorkflowEditorState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$JsonSchemaCopyWith<$Res>? get schema {
    if (_self.schema == null) {
    return null;
  }

  return $JsonSchemaCopyWith<$Res>(_self.schema!, (value) {
    return _then(_self.copyWith(schema: value));
  });
}
}


/// Adds pattern-matching-related methods to [WorkflowEditorState].
extension WorkflowEditorStatePatterns on WorkflowEditorState {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowEditorState value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowEditorState() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowEditorState value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowEditorState():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowEditorState value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowEditorState() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( JsonSchema? schema,  Map<String, dynamic>? data,  bool isSaving,  String? lastError)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowEditorState() when $default != null:
return $default(_that.schema,_that.data,_that.isSaving,_that.lastError);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( JsonSchema? schema,  Map<String, dynamic>? data,  bool isSaving,  String? lastError)  $default,) {final _that = this;
switch (_that) {
case _WorkflowEditorState():
return $default(_that.schema,_that.data,_that.isSaving,_that.lastError);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( JsonSchema? schema,  Map<String, dynamic>? data,  bool isSaving,  String? lastError)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowEditorState() when $default != null:
return $default(_that.schema,_that.data,_that.isSaving,_that.lastError);case _:
  return null;

}
}

}

/// @nodoc


class _WorkflowEditorState implements WorkflowEditorState {
  const _WorkflowEditorState({this.schema, final  Map<String, dynamic>? data, this.isSaving = false, this.lastError}): _data = data;
  

@override final  JsonSchema? schema;
 final  Map<String, dynamic>? _data;
@override Map<String, dynamic>? get data {
  final value = _data;
  if (value == null) return null;
  if (_data is EqualUnmodifiableMapView) return _data;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey() final  bool isSaving;
@override final  String? lastError;

/// Create a copy of WorkflowEditorState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowEditorStateCopyWith<_WorkflowEditorState> get copyWith => __$WorkflowEditorStateCopyWithImpl<_WorkflowEditorState>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowEditorState&&(identical(other.schema, schema) || other.schema == schema)&&const DeepCollectionEquality().equals(other._data, _data)&&(identical(other.isSaving, isSaving) || other.isSaving == isSaving)&&(identical(other.lastError, lastError) || other.lastError == lastError));
}


@override
int get hashCode => Object.hash(runtimeType,schema,const DeepCollectionEquality().hash(_data),isSaving,lastError);

@override
String toString() {
  return 'WorkflowEditorState(schema: $schema, data: $data, isSaving: $isSaving, lastError: $lastError)';
}


}

/// @nodoc
abstract mixin class _$WorkflowEditorStateCopyWith<$Res> implements $WorkflowEditorStateCopyWith<$Res> {
  factory _$WorkflowEditorStateCopyWith(_WorkflowEditorState value, $Res Function(_WorkflowEditorState) _then) = __$WorkflowEditorStateCopyWithImpl;
@override @useResult
$Res call({
 JsonSchema? schema, Map<String, dynamic>? data, bool isSaving, String? lastError
});


@override $JsonSchemaCopyWith<$Res>? get schema;

}
/// @nodoc
class __$WorkflowEditorStateCopyWithImpl<$Res>
    implements _$WorkflowEditorStateCopyWith<$Res> {
  __$WorkflowEditorStateCopyWithImpl(this._self, this._then);

  final _WorkflowEditorState _self;
  final $Res Function(_WorkflowEditorState) _then;

/// Create a copy of WorkflowEditorState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? schema = freezed,Object? data = freezed,Object? isSaving = null,Object? lastError = freezed,}) {
  return _then(_WorkflowEditorState(
schema: freezed == schema ? _self.schema : schema // ignore: cast_nullable_to_non_nullable
as JsonSchema?,data: freezed == data ? _self._data : data // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,isSaving: null == isSaving ? _self.isSaving : isSaving // ignore: cast_nullable_to_non_nullable
as bool,lastError: freezed == lastError ? _self.lastError : lastError // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of WorkflowEditorState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$JsonSchemaCopyWith<$Res>? get schema {
    if (_self.schema == null) {
    return null;
  }

  return $JsonSchemaCopyWith<$Res>(_self.schema!, (value) {
    return _then(_self.copyWith(schema: value));
  });
}
}

// dart format on
