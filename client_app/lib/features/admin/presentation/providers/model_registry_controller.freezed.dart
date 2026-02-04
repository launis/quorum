// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'model_registry_controller.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ModelRegistryState {

 AsyncValue<List<LLMProviderConfig>> get providers; AsyncValue<Map<String, List<String>>> get availableOptions; String? get selectedProviderId; AsyncValue<AdHocTestResult?> get testResult; bool get isSaving;
/// Create a copy of ModelRegistryState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ModelRegistryStateCopyWith<ModelRegistryState> get copyWith => _$ModelRegistryStateCopyWithImpl<ModelRegistryState>(this as ModelRegistryState, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ModelRegistryState&&(identical(other.providers, providers) || other.providers == providers)&&(identical(other.availableOptions, availableOptions) || other.availableOptions == availableOptions)&&(identical(other.selectedProviderId, selectedProviderId) || other.selectedProviderId == selectedProviderId)&&(identical(other.testResult, testResult) || other.testResult == testResult)&&(identical(other.isSaving, isSaving) || other.isSaving == isSaving));
}


@override
int get hashCode => Object.hash(runtimeType,providers,availableOptions,selectedProviderId,testResult,isSaving);

@override
String toString() {
  return 'ModelRegistryState(providers: $providers, availableOptions: $availableOptions, selectedProviderId: $selectedProviderId, testResult: $testResult, isSaving: $isSaving)';
}


}

/// @nodoc
abstract mixin class $ModelRegistryStateCopyWith<$Res>  {
  factory $ModelRegistryStateCopyWith(ModelRegistryState value, $Res Function(ModelRegistryState) _then) = _$ModelRegistryStateCopyWithImpl;
@useResult
$Res call({
 AsyncValue<List<LLMProviderConfig>> providers, AsyncValue<Map<String, List<String>>> availableOptions, String? selectedProviderId, AsyncValue<AdHocTestResult?> testResult, bool isSaving
});




}
/// @nodoc
class _$ModelRegistryStateCopyWithImpl<$Res>
    implements $ModelRegistryStateCopyWith<$Res> {
  _$ModelRegistryStateCopyWithImpl(this._self, this._then);

  final ModelRegistryState _self;
  final $Res Function(ModelRegistryState) _then;

/// Create a copy of ModelRegistryState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? providers = null,Object? availableOptions = null,Object? selectedProviderId = freezed,Object? testResult = null,Object? isSaving = null,}) {
  return _then(_self.copyWith(
providers: null == providers ? _self.providers : providers // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<LLMProviderConfig>>,availableOptions: null == availableOptions ? _self.availableOptions : availableOptions // ignore: cast_nullable_to_non_nullable
as AsyncValue<Map<String, List<String>>>,selectedProviderId: freezed == selectedProviderId ? _self.selectedProviderId : selectedProviderId // ignore: cast_nullable_to_non_nullable
as String?,testResult: null == testResult ? _self.testResult : testResult // ignore: cast_nullable_to_non_nullable
as AsyncValue<AdHocTestResult?>,isSaving: null == isSaving ? _self.isSaving : isSaving // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [ModelRegistryState].
extension ModelRegistryStatePatterns on ModelRegistryState {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ModelRegistryState value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ModelRegistryState() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ModelRegistryState value)  $default,){
final _that = this;
switch (_that) {
case _ModelRegistryState():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ModelRegistryState value)?  $default,){
final _that = this;
switch (_that) {
case _ModelRegistryState() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( AsyncValue<List<LLMProviderConfig>> providers,  AsyncValue<Map<String, List<String>>> availableOptions,  String? selectedProviderId,  AsyncValue<AdHocTestResult?> testResult,  bool isSaving)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ModelRegistryState() when $default != null:
return $default(_that.providers,_that.availableOptions,_that.selectedProviderId,_that.testResult,_that.isSaving);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( AsyncValue<List<LLMProviderConfig>> providers,  AsyncValue<Map<String, List<String>>> availableOptions,  String? selectedProviderId,  AsyncValue<AdHocTestResult?> testResult,  bool isSaving)  $default,) {final _that = this;
switch (_that) {
case _ModelRegistryState():
return $default(_that.providers,_that.availableOptions,_that.selectedProviderId,_that.testResult,_that.isSaving);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( AsyncValue<List<LLMProviderConfig>> providers,  AsyncValue<Map<String, List<String>>> availableOptions,  String? selectedProviderId,  AsyncValue<AdHocTestResult?> testResult,  bool isSaving)?  $default,) {final _that = this;
switch (_that) {
case _ModelRegistryState() when $default != null:
return $default(_that.providers,_that.availableOptions,_that.selectedProviderId,_that.testResult,_that.isSaving);case _:
  return null;

}
}

}

/// @nodoc


class _ModelRegistryState implements ModelRegistryState {
  const _ModelRegistryState({this.providers = const AsyncValue.loading(), this.availableOptions = const AsyncValue.loading(), this.selectedProviderId, this.testResult = const AsyncValue.data(null), this.isSaving = false});
  

@override@JsonKey() final  AsyncValue<List<LLMProviderConfig>> providers;
@override@JsonKey() final  AsyncValue<Map<String, List<String>>> availableOptions;
@override final  String? selectedProviderId;
@override@JsonKey() final  AsyncValue<AdHocTestResult?> testResult;
@override@JsonKey() final  bool isSaving;

/// Create a copy of ModelRegistryState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ModelRegistryStateCopyWith<_ModelRegistryState> get copyWith => __$ModelRegistryStateCopyWithImpl<_ModelRegistryState>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ModelRegistryState&&(identical(other.providers, providers) || other.providers == providers)&&(identical(other.availableOptions, availableOptions) || other.availableOptions == availableOptions)&&(identical(other.selectedProviderId, selectedProviderId) || other.selectedProviderId == selectedProviderId)&&(identical(other.testResult, testResult) || other.testResult == testResult)&&(identical(other.isSaving, isSaving) || other.isSaving == isSaving));
}


@override
int get hashCode => Object.hash(runtimeType,providers,availableOptions,selectedProviderId,testResult,isSaving);

@override
String toString() {
  return 'ModelRegistryState(providers: $providers, availableOptions: $availableOptions, selectedProviderId: $selectedProviderId, testResult: $testResult, isSaving: $isSaving)';
}


}

/// @nodoc
abstract mixin class _$ModelRegistryStateCopyWith<$Res> implements $ModelRegistryStateCopyWith<$Res> {
  factory _$ModelRegistryStateCopyWith(_ModelRegistryState value, $Res Function(_ModelRegistryState) _then) = __$ModelRegistryStateCopyWithImpl;
@override @useResult
$Res call({
 AsyncValue<List<LLMProviderConfig>> providers, AsyncValue<Map<String, List<String>>> availableOptions, String? selectedProviderId, AsyncValue<AdHocTestResult?> testResult, bool isSaving
});




}
/// @nodoc
class __$ModelRegistryStateCopyWithImpl<$Res>
    implements _$ModelRegistryStateCopyWith<$Res> {
  __$ModelRegistryStateCopyWithImpl(this._self, this._then);

  final _ModelRegistryState _self;
  final $Res Function(_ModelRegistryState) _then;

/// Create a copy of ModelRegistryState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? providers = null,Object? availableOptions = null,Object? selectedProviderId = freezed,Object? testResult = null,Object? isSaving = null,}) {
  return _then(_ModelRegistryState(
providers: null == providers ? _self.providers : providers // ignore: cast_nullable_to_non_nullable
as AsyncValue<List<LLMProviderConfig>>,availableOptions: null == availableOptions ? _self.availableOptions : availableOptions // ignore: cast_nullable_to_non_nullable
as AsyncValue<Map<String, List<String>>>,selectedProviderId: freezed == selectedProviderId ? _self.selectedProviderId : selectedProviderId // ignore: cast_nullable_to_non_nullable
as String?,testResult: null == testResult ? _self.testResult : testResult // ignore: cast_nullable_to_non_nullable
as AsyncValue<AdHocTestResult?>,isSaving: null == isSaving ? _self.isSaving : isSaving // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
