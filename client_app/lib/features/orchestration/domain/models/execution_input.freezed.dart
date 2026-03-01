// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_input.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionInput {

/// The UUID of the workflow definition to instantiate.
@JsonKey(name: 'workflow_id') String get workflowId;/// Key-value pairs representing the initial input state (e.g. source text).
 Map<String, dynamic> get inputs;/// File attachments to be uploaded via Multipart request.
/// Not serialized to JSON as the repository handles FormData construction manually.
@JsonKey(includeToJson: false) Map<String, ExecutionFile> get files;/// Optional structured guided reflection form data
@JsonKey(name: 'guided_reflection') GuidedReflectionDTO? get guidedReflection;
/// Create a copy of ExecutionInput
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionInputCopyWith<ExecutionInput> get copyWith => _$ExecutionInputCopyWithImpl<ExecutionInput>(this as ExecutionInput, _$identity);

  /// Serializes this ExecutionInput to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionInput&&(identical(other.workflowId, workflowId) || other.workflowId == workflowId)&&const DeepCollectionEquality().equals(other.inputs, inputs)&&const DeepCollectionEquality().equals(other.files, files)&&(identical(other.guidedReflection, guidedReflection) || other.guidedReflection == guidedReflection));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,workflowId,const DeepCollectionEquality().hash(inputs),const DeepCollectionEquality().hash(files),guidedReflection);

@override
String toString() {
  return 'ExecutionInput(workflowId: $workflowId, inputs: $inputs, files: $files, guidedReflection: $guidedReflection)';
}


}

/// @nodoc
abstract mixin class $ExecutionInputCopyWith<$Res>  {
  factory $ExecutionInputCopyWith(ExecutionInput value, $Res Function(ExecutionInput) _then) = _$ExecutionInputCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId, Map<String, dynamic> inputs,@JsonKey(includeToJson: false) Map<String, ExecutionFile> files,@JsonKey(name: 'guided_reflection') GuidedReflectionDTO? guidedReflection
});


$GuidedReflectionDTOCopyWith<$Res>? get guidedReflection;

}
/// @nodoc
class _$ExecutionInputCopyWithImpl<$Res>
    implements $ExecutionInputCopyWith<$Res> {
  _$ExecutionInputCopyWithImpl(this._self, this._then);

  final ExecutionInput _self;
  final $Res Function(ExecutionInput) _then;

/// Create a copy of ExecutionInput
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? workflowId = null,Object? inputs = null,Object? files = null,Object? guidedReflection = freezed,}) {
  return _then(_self.copyWith(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,inputs: null == inputs ? _self.inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,files: null == files ? _self.files : files // ignore: cast_nullable_to_non_nullable
as Map<String, ExecutionFile>,guidedReflection: freezed == guidedReflection ? _self.guidedReflection : guidedReflection // ignore: cast_nullable_to_non_nullable
as GuidedReflectionDTO?,
  ));
}
/// Create a copy of ExecutionInput
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GuidedReflectionDTOCopyWith<$Res>? get guidedReflection {
    if (_self.guidedReflection == null) {
    return null;
  }

  return $GuidedReflectionDTOCopyWith<$Res>(_self.guidedReflection!, (value) {
    return _then(_self.copyWith(guidedReflection: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionInput].
extension ExecutionInputPatterns on ExecutionInput {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionInput value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionInput() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionInput value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionInput():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionInput value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionInput() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId,  Map<String, dynamic> inputs, @JsonKey(includeToJson: false)  Map<String, ExecutionFile> files, @JsonKey(name: 'guided_reflection')  GuidedReflectionDTO? guidedReflection)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionInput() when $default != null:
return $default(_that.workflowId,_that.inputs,_that.files,_that.guidedReflection);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId,  Map<String, dynamic> inputs, @JsonKey(includeToJson: false)  Map<String, ExecutionFile> files, @JsonKey(name: 'guided_reflection')  GuidedReflectionDTO? guidedReflection)  $default,) {final _that = this;
switch (_that) {
case _ExecutionInput():
return $default(_that.workflowId,_that.inputs,_that.files,_that.guidedReflection);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'workflow_id')  String workflowId,  Map<String, dynamic> inputs, @JsonKey(includeToJson: false)  Map<String, ExecutionFile> files, @JsonKey(name: 'guided_reflection')  GuidedReflectionDTO? guidedReflection)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionInput() when $default != null:
return $default(_that.workflowId,_that.inputs,_that.files,_that.guidedReflection);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ExecutionInput implements ExecutionInput {
  const _ExecutionInput({@JsonKey(name: 'workflow_id') required this.workflowId, final  Map<String, dynamic> inputs = const {}, @JsonKey(includeToJson: false) final  Map<String, ExecutionFile> files = const {}, @JsonKey(name: 'guided_reflection') this.guidedReflection}): _inputs = inputs,_files = files;
  factory _ExecutionInput.fromJson(Map<String, dynamic> json) => _$ExecutionInputFromJson(json);

/// The UUID of the workflow definition to instantiate.
@override@JsonKey(name: 'workflow_id') final  String workflowId;
/// Key-value pairs representing the initial input state (e.g. source text).
 final  Map<String, dynamic> _inputs;
/// Key-value pairs representing the initial input state (e.g. source text).
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

/// File attachments to be uploaded via Multipart request.
/// Not serialized to JSON as the repository handles FormData construction manually.
 final  Map<String, ExecutionFile> _files;
/// File attachments to be uploaded via Multipart request.
/// Not serialized to JSON as the repository handles FormData construction manually.
@override@JsonKey(includeToJson: false) Map<String, ExecutionFile> get files {
  if (_files is EqualUnmodifiableMapView) return _files;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_files);
}

/// Optional structured guided reflection form data
@override@JsonKey(name: 'guided_reflection') final  GuidedReflectionDTO? guidedReflection;

/// Create a copy of ExecutionInput
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionInputCopyWith<_ExecutionInput> get copyWith => __$ExecutionInputCopyWithImpl<_ExecutionInput>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionInputToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ExecutionInput&&(identical(other.workflowId, workflowId) || other.workflowId == workflowId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&const DeepCollectionEquality().equals(other._files, _files)&&(identical(other.guidedReflection, guidedReflection) || other.guidedReflection == guidedReflection));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,workflowId,const DeepCollectionEquality().hash(_inputs),const DeepCollectionEquality().hash(_files),guidedReflection);

@override
String toString() {
  return 'ExecutionInput(workflowId: $workflowId, inputs: $inputs, files: $files, guidedReflection: $guidedReflection)';
}


}

/// @nodoc
abstract mixin class _$ExecutionInputCopyWith<$Res> implements $ExecutionInputCopyWith<$Res> {
  factory _$ExecutionInputCopyWith(_ExecutionInput value, $Res Function(_ExecutionInput) _then) = __$ExecutionInputCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId, Map<String, dynamic> inputs,@JsonKey(includeToJson: false) Map<String, ExecutionFile> files,@JsonKey(name: 'guided_reflection') GuidedReflectionDTO? guidedReflection
});


@override $GuidedReflectionDTOCopyWith<$Res>? get guidedReflection;

}
/// @nodoc
class __$ExecutionInputCopyWithImpl<$Res>
    implements _$ExecutionInputCopyWith<$Res> {
  __$ExecutionInputCopyWithImpl(this._self, this._then);

  final _ExecutionInput _self;
  final $Res Function(_ExecutionInput) _then;

/// Create a copy of ExecutionInput
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? workflowId = null,Object? inputs = null,Object? files = null,Object? guidedReflection = freezed,}) {
  return _then(_ExecutionInput(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,files: null == files ? _self._files : files // ignore: cast_nullable_to_non_nullable
as Map<String, ExecutionFile>,guidedReflection: freezed == guidedReflection ? _self.guidedReflection : guidedReflection // ignore: cast_nullable_to_non_nullable
as GuidedReflectionDTO?,
  ));
}

/// Create a copy of ExecutionInput
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GuidedReflectionDTOCopyWith<$Res>? get guidedReflection {
    if (_self.guidedReflection == null) {
    return null;
  }

  return $GuidedReflectionDTOCopyWith<$Res>(_self.guidedReflection!, (value) {
    return _then(_self.copyWith(guidedReflection: value));
  });
}
}

// dart format on
