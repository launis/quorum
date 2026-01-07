// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'wizard_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$WizardStateModel {

 int get currentStep; String get selectedWorkflowId; Map<String, dynamic> get inputs; bool get isSubmitting; String? get error;
/// Create a copy of WizardStateModel
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WizardStateModelCopyWith<WizardStateModel> get copyWith => _$WizardStateModelCopyWithImpl<WizardStateModel>(this as WizardStateModel, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WizardStateModel&&(identical(other.currentStep, currentStep) || other.currentStep == currentStep)&&(identical(other.selectedWorkflowId, selectedWorkflowId) || other.selectedWorkflowId == selectedWorkflowId)&&const DeepCollectionEquality().equals(other.inputs, inputs)&&(identical(other.isSubmitting, isSubmitting) || other.isSubmitting == isSubmitting)&&(identical(other.error, error) || other.error == error));
}


@override
int get hashCode => Object.hash(runtimeType,currentStep,selectedWorkflowId,const DeepCollectionEquality().hash(inputs),isSubmitting,error);

@override
String toString() {
  return 'WizardStateModel(currentStep: $currentStep, selectedWorkflowId: $selectedWorkflowId, inputs: $inputs, isSubmitting: $isSubmitting, error: $error)';
}


}

/// @nodoc
abstract mixin class $WizardStateModelCopyWith<$Res>  {
  factory $WizardStateModelCopyWith(WizardStateModel value, $Res Function(WizardStateModel) _then) = _$WizardStateModelCopyWithImpl;
@useResult
$Res call({
 int currentStep, String selectedWorkflowId, Map<String, dynamic> inputs, bool isSubmitting, String? error
});




}
/// @nodoc
class _$WizardStateModelCopyWithImpl<$Res>
    implements $WizardStateModelCopyWith<$Res> {
  _$WizardStateModelCopyWithImpl(this._self, this._then);

  final WizardStateModel _self;
  final $Res Function(WizardStateModel) _then;

/// Create a copy of WizardStateModel
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? currentStep = null,Object? selectedWorkflowId = null,Object? inputs = null,Object? isSubmitting = null,Object? error = freezed,}) {
  return _then(_self.copyWith(
currentStep: null == currentStep ? _self.currentStep : currentStep // ignore: cast_nullable_to_non_nullable
as int,selectedWorkflowId: null == selectedWorkflowId ? _self.selectedWorkflowId : selectedWorkflowId // ignore: cast_nullable_to_non_nullable
as String,inputs: null == inputs ? _self.inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,isSubmitting: null == isSubmitting ? _self.isSubmitting : isSubmitting // ignore: cast_nullable_to_non_nullable
as bool,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [WizardStateModel].
extension WizardStateModelPatterns on WizardStateModel {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WizardStateModel value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WizardStateModel() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WizardStateModel value)  $default,){
final _that = this;
switch (_that) {
case _WizardStateModel():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WizardStateModel value)?  $default,){
final _that = this;
switch (_that) {
case _WizardStateModel() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int currentStep,  String selectedWorkflowId,  Map<String, dynamic> inputs,  bool isSubmitting,  String? error)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WizardStateModel() when $default != null:
return $default(_that.currentStep,_that.selectedWorkflowId,_that.inputs,_that.isSubmitting,_that.error);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int currentStep,  String selectedWorkflowId,  Map<String, dynamic> inputs,  bool isSubmitting,  String? error)  $default,) {final _that = this;
switch (_that) {
case _WizardStateModel():
return $default(_that.currentStep,_that.selectedWorkflowId,_that.inputs,_that.isSubmitting,_that.error);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int currentStep,  String selectedWorkflowId,  Map<String, dynamic> inputs,  bool isSubmitting,  String? error)?  $default,) {final _that = this;
switch (_that) {
case _WizardStateModel() when $default != null:
return $default(_that.currentStep,_that.selectedWorkflowId,_that.inputs,_that.isSubmitting,_that.error);case _:
  return null;

}
}

}

/// @nodoc


class _WizardStateModel implements WizardStateModel {
  const _WizardStateModel({this.currentStep = 0, this.selectedWorkflowId = 'audit_workflow_v1', final  Map<String, dynamic> inputs = const {}, this.isSubmitting = false, this.error}): _inputs = inputs;
  

@override@JsonKey() final  int currentStep;
@override@JsonKey() final  String selectedWorkflowId;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey() final  bool isSubmitting;
@override final  String? error;

/// Create a copy of WizardStateModel
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WizardStateModelCopyWith<_WizardStateModel> get copyWith => __$WizardStateModelCopyWithImpl<_WizardStateModel>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WizardStateModel&&(identical(other.currentStep, currentStep) || other.currentStep == currentStep)&&(identical(other.selectedWorkflowId, selectedWorkflowId) || other.selectedWorkflowId == selectedWorkflowId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.isSubmitting, isSubmitting) || other.isSubmitting == isSubmitting)&&(identical(other.error, error) || other.error == error));
}


@override
int get hashCode => Object.hash(runtimeType,currentStep,selectedWorkflowId,const DeepCollectionEquality().hash(_inputs),isSubmitting,error);

@override
String toString() {
  return 'WizardStateModel(currentStep: $currentStep, selectedWorkflowId: $selectedWorkflowId, inputs: $inputs, isSubmitting: $isSubmitting, error: $error)';
}


}

/// @nodoc
abstract mixin class _$WizardStateModelCopyWith<$Res> implements $WizardStateModelCopyWith<$Res> {
  factory _$WizardStateModelCopyWith(_WizardStateModel value, $Res Function(_WizardStateModel) _then) = __$WizardStateModelCopyWithImpl;
@override @useResult
$Res call({
 int currentStep, String selectedWorkflowId, Map<String, dynamic> inputs, bool isSubmitting, String? error
});




}
/// @nodoc
class __$WizardStateModelCopyWithImpl<$Res>
    implements _$WizardStateModelCopyWith<$Res> {
  __$WizardStateModelCopyWithImpl(this._self, this._then);

  final _WizardStateModel _self;
  final $Res Function(_WizardStateModel) _then;

/// Create a copy of WizardStateModel
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? currentStep = null,Object? selectedWorkflowId = null,Object? inputs = null,Object? isSubmitting = null,Object? error = freezed,}) {
  return _then(_WizardStateModel(
currentStep: null == currentStep ? _self.currentStep : currentStep // ignore: cast_nullable_to_non_nullable
as int,selectedWorkflowId: null == selectedWorkflowId ? _self.selectedWorkflowId : selectedWorkflowId // ignore: cast_nullable_to_non_nullable
as String,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,isSubmitting: null == isSubmitting ? _self.isSubmitting : isSubmitting // ignore: cast_nullable_to_non_nullable
as bool,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
