// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'studio_controller.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$StudioState {

 AsyncValue<List<WorkflowDef>> get workflows; AsyncValue<WorkflowDef?> get activeWorkflow; AsyncValue<List<StudioComponentDef>> get components; AsyncValue<List<StudioComponentDef>> get availableMatrices; AsyncValue<List<OntologyDimension>> get ontologyDimensions; String? get selectedMatrixId;
/// Create a copy of StudioState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StudioStateCopyWith<StudioState> get copyWith => _$StudioStateCopyWithImpl<StudioState>(this as StudioState, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StudioState&&(identical(other.workflows, workflows) || other.workflows == workflows)&&(identical(other.activeWorkflow, activeWorkflow) || other.activeWorkflow == activeWorkflow)&&(identical(other.components, components) || other.components == components)&&(identical(other.availableMatrices, availableMatrices) || other.availableMatrices == availableMatrices)&&(identical(other.ontologyDimensions, ontologyDimensions) || other.ontologyDimensions == ontologyDimensions)&&(identical(other.selectedMatrixId, selectedMatrixId) || other.selectedMatrixId == selectedMatrixId));
}


@override
int get hashCode => Object.hash(runtimeType,workflows,activeWorkflow,components,availableMatrices,ontologyDimensions,selectedMatrixId);

@override
String toString() {
  return 'StudioState(workflows: $workflows, activeWorkflow: $activeWorkflow, components: $components, availableMatrices: $availableMatrices, ontologyDimensions: $ontologyDimensions, selectedMatrixId: $selectedMatrixId)';
}


}

/// @nodoc
abstract mixin class $StudioStateCopyWith<$Res>  {
  factory $StudioStateCopyWith(StudioState value, $Res Function(StudioState) _then) = _$StudioStateCopyWithImpl;
@useResult
$Res call({
 AsyncValue<List<WorkflowDef>> workflows, AsyncValue<WorkflowDef?> activeWorkflow, AsyncValue<List<StudioComponentDef>> components, AsyncValue<List<StudioComponentDef>> availableMatrices, AsyncValue<List<OntologyDimension>> ontologyDimensions, String? selectedMatrixId
});




}
/// @nodoc
class _$StudioStateCopyWithImpl<$Res>
    implements $StudioStateCopyWith<$Res> {
  _$StudioStateCopyWithImpl(this._self, this._then);

  final StudioState _self;
  final $Res Function(StudioState) _then;

/// Create a copy of StudioState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? workflows = null,Object? activeWorkflow = null,Object? components = null,Object? availableMatrices = null,Object? ontologyDimensions = null,Object? selectedMatrixId = freezed,}) {
  return _then(_self.copyWith(
workflows: null == workflows ? _self.workflows : workflows // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<WorkflowDef>>,activeWorkflow: null == activeWorkflow ? _self.activeWorkflow : activeWorkflow // ignore: cast_nullable_to_non_nullable
as AsyncValue<WorkflowDef?>,components: null == components ? _self.components : components // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<StudioComponentDef>>,availableMatrices: null == availableMatrices ? _self.availableMatrices : availableMatrices // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<StudioComponentDef>>,ontologyDimensions: null == ontologyDimensions ? _self.ontologyDimensions : ontologyDimensions // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<OntologyDimension>>,selectedMatrixId: freezed == selectedMatrixId ? _self.selectedMatrixId : selectedMatrixId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [StudioState].
extension StudioStatePatterns on StudioState {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StudioState value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StudioState() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StudioState value)  $default,){
final _that = this;
switch (_that) {
case _StudioState():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StudioState value)?  $default,){
final _that = this;
switch (_that) {
case _StudioState() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( AsyncValue<List<WorkflowDef>> workflows,  AsyncValue<WorkflowDef?> activeWorkflow,  AsyncValue<List<StudioComponentDef>> components,  AsyncValue<List<StudioComponentDef>> availableMatrices,  AsyncValue<List<OntologyDimension>> ontologyDimensions,  String? selectedMatrixId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StudioState() when $default != null:
return $default(_that.workflows,_that.activeWorkflow,_that.components,_that.availableMatrices,_that.ontologyDimensions,_that.selectedMatrixId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( AsyncValue<List<WorkflowDef>> workflows,  AsyncValue<WorkflowDef?> activeWorkflow,  AsyncValue<List<StudioComponentDef>> components,  AsyncValue<List<StudioComponentDef>> availableMatrices,  AsyncValue<List<OntologyDimension>> ontologyDimensions,  String? selectedMatrixId)  $default,) {final _that = this;
switch (_that) {
case _StudioState():
return $default(_that.workflows,_that.activeWorkflow,_that.components,_that.availableMatrices,_that.ontologyDimensions,_that.selectedMatrixId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( AsyncValue<List<WorkflowDef>> workflows,  AsyncValue<WorkflowDef?> activeWorkflow,  AsyncValue<List<StudioComponentDef>> components,  AsyncValue<List<StudioComponentDef>> availableMatrices,  AsyncValue<List<OntologyDimension>> ontologyDimensions,  String? selectedMatrixId)?  $default,) {final _that = this;
switch (_that) {
case _StudioState() when $default != null:
return $default(_that.workflows,_that.activeWorkflow,_that.components,_that.availableMatrices,_that.ontologyDimensions,_that.selectedMatrixId);case _:
  return null;

}
}

}

/// @nodoc


class _StudioState implements StudioState {
  const _StudioState({this.workflows = const AsyncValue.data(<WorkflowDef>[]), this.activeWorkflow = const AsyncValue.data(null), this.components = const AsyncValue.data(<StudioComponentDef>[]), this.availableMatrices = const AsyncValue.data(<StudioComponentDef>[]), this.ontologyDimensions = const AsyncValue.data([]), this.selectedMatrixId});
  

@override@JsonKey() final  AsyncValue<List<WorkflowDef>> workflows;
@override@JsonKey() final  AsyncValue<WorkflowDef?> activeWorkflow;
@override@JsonKey() final  AsyncValue<List<StudioComponentDef>> components;
@override@JsonKey() final  AsyncValue<List<StudioComponentDef>> availableMatrices;
@override@JsonKey() final  AsyncValue<List<OntologyDimension>> ontologyDimensions;
@override final  String? selectedMatrixId;

/// Create a copy of StudioState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StudioStateCopyWith<_StudioState> get copyWith => __$StudioStateCopyWithImpl<_StudioState>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _StudioState&&(identical(other.workflows, workflows) || other.workflows == workflows)&&(identical(other.activeWorkflow, activeWorkflow) || other.activeWorkflow == activeWorkflow)&&(identical(other.components, components) || other.components == components)&&(identical(other.availableMatrices, availableMatrices) || other.availableMatrices == availableMatrices)&&(identical(other.ontologyDimensions, ontologyDimensions) || other.ontologyDimensions == ontologyDimensions)&&(identical(other.selectedMatrixId, selectedMatrixId) || other.selectedMatrixId == selectedMatrixId));
}


@override
int get hashCode => Object.hash(runtimeType,workflows,activeWorkflow,components,availableMatrices,ontologyDimensions,selectedMatrixId);

@override
String toString() {
  return 'StudioState(workflows: $workflows, activeWorkflow: $activeWorkflow, components: $components, availableMatrices: $availableMatrices, ontologyDimensions: $ontologyDimensions, selectedMatrixId: $selectedMatrixId)';
}


}

/// @nodoc
abstract mixin class _$StudioStateCopyWith<$Res> implements $StudioStateCopyWith<$Res> {
  factory _$StudioStateCopyWith(_StudioState value, $Res Function(_StudioState) _then) = __$StudioStateCopyWithImpl;
@override @useResult
$Res call({
 AsyncValue<List<WorkflowDef>> workflows, AsyncValue<WorkflowDef?> activeWorkflow, AsyncValue<List<StudioComponentDef>> components, AsyncValue<List<StudioComponentDef>> availableMatrices, AsyncValue<List<OntologyDimension>> ontologyDimensions, String? selectedMatrixId
});




}
/// @nodoc
class __$StudioStateCopyWithImpl<$Res>
    implements _$StudioStateCopyWith<$Res> {
  __$StudioStateCopyWithImpl(this._self, this._then);

  final _StudioState _self;
  final $Res Function(_StudioState) _then;

/// Create a copy of StudioState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? workflows = null,Object? activeWorkflow = null,Object? components = null,Object? availableMatrices = null,Object? ontologyDimensions = null,Object? selectedMatrixId = freezed,}) {
  return _then(_StudioState(
workflows: null == workflows ? _self.workflows : workflows // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<WorkflowDef>>,activeWorkflow: null == activeWorkflow ? _self.activeWorkflow : activeWorkflow // ignore: cast_nullable_to_non_nullable
as AsyncValue<WorkflowDef?>,components: null == components ? _self.components : components // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<StudioComponentDef>>,availableMatrices: null == availableMatrices ? _self.availableMatrices : availableMatrices // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<StudioComponentDef>>,ontologyDimensions: null == ontologyDimensions ? _self.ontologyDimensions : ontologyDimensions // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<OntologyDimension>>,selectedMatrixId: freezed == selectedMatrixId ? _self.selectedMatrixId : selectedMatrixId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
