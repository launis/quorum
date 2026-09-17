// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_metadata.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionMetadata {

@JsonKey(name: 'matrix_sampling_strategy') int? get matrixSamplingStrategy;@JsonKey(name: 'workflow_version') int get workflowVersion;@JsonKey(name: 'global_context_vars') Map<String, dynamic>? get globalContextVars;@JsonKey(name: 'provider_override') LLMProvider? get providerOverride;@JsonKey(name: 'model_registry_id') String? get modelRegistryId;
/// Create a copy of ExecutionMetadata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionMetadataCopyWith<ExecutionMetadata> get copyWith => _$ExecutionMetadataCopyWithImpl<ExecutionMetadata>(this as ExecutionMetadata, _$identity);

  /// Serializes this ExecutionMetadata to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionMetadata(matrixSamplingStrategy: $matrixSamplingStrategy, workflowVersion: $workflowVersion, globalContextVars: $globalContextVars, providerOverride: $providerOverride, modelRegistryId: $modelRegistryId)';
}


}

/// @nodoc
abstract mixin class $ExecutionMetadataCopyWith<$Res>  {
  factory $ExecutionMetadataCopyWith(ExecutionMetadata value, $Res Function(ExecutionMetadata) _then) = _$ExecutionMetadataCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy,@JsonKey(name: 'workflow_version') int workflowVersion,@JsonKey(name: 'global_context_vars') Map<String, dynamic>? globalContextVars,@JsonKey(name: 'provider_override') LLMProvider? providerOverride,@JsonKey(name: 'model_registry_id') String? modelRegistryId
});




}
/// @nodoc
class _$ExecutionMetadataCopyWithImpl<$Res>
    implements $ExecutionMetadataCopyWith<$Res> {
  _$ExecutionMetadataCopyWithImpl(this._self, this._then);

  final ExecutionMetadata _self;
  final $Res Function(ExecutionMetadata) _then;

/// Create a copy of ExecutionMetadata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? matrixSamplingStrategy = freezed,Object? workflowVersion = null,Object? globalContextVars = freezed,Object? providerOverride = freezed,Object? modelRegistryId = freezed,}) {
  return _then(_self.copyWith(
matrixSamplingStrategy: freezed == matrixSamplingStrategy ? _self.matrixSamplingStrategy : matrixSamplingStrategy // ignore: cast_nullable_to_non_nullable
as int?,workflowVersion: null == workflowVersion ? _self.workflowVersion : workflowVersion // ignore: cast_nullable_to_non_nullable
as int,globalContextVars: freezed == globalContextVars ? _self.globalContextVars : globalContextVars // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,providerOverride: freezed == providerOverride ? _self.providerOverride : providerOverride // ignore: cast_nullable_to_non_nullable
as LLMProvider?,modelRegistryId: freezed == modelRegistryId ? _self.modelRegistryId : modelRegistryId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionMetadata].
extension ExecutionMetadataPatterns on ExecutionMetadata {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionMetadata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionMetadata() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionMetadata value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionMetadata():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionMetadata value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionMetadata() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'matrix_sampling_strategy')  int? matrixSamplingStrategy, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'global_context_vars')  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'provider_override')  LLMProvider? providerOverride, @JsonKey(name: 'model_registry_id')  String? modelRegistryId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionMetadata() when $default != null:
return $default(_that.matrixSamplingStrategy,_that.workflowVersion,_that.globalContextVars,_that.providerOverride,_that.modelRegistryId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'matrix_sampling_strategy')  int? matrixSamplingStrategy, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'global_context_vars')  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'provider_override')  LLMProvider? providerOverride, @JsonKey(name: 'model_registry_id')  String? modelRegistryId)  $default,) {final _that = this;
switch (_that) {
case _ExecutionMetadata():
return $default(_that.matrixSamplingStrategy,_that.workflowVersion,_that.globalContextVars,_that.providerOverride,_that.modelRegistryId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'matrix_sampling_strategy')  int? matrixSamplingStrategy, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'global_context_vars')  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'provider_override')  LLMProvider? providerOverride, @JsonKey(name: 'model_registry_id')  String? modelRegistryId)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionMetadata() when $default != null:
return $default(_that.matrixSamplingStrategy,_that.workflowVersion,_that.globalContextVars,_that.providerOverride,_that.modelRegistryId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionMetadata extends ExecutionMetadata {
  const _ExecutionMetadata({@JsonKey(name: 'matrix_sampling_strategy') this.matrixSamplingStrategy, @JsonKey(name: 'workflow_version') this.workflowVersion = 1, @JsonKey(name: 'global_context_vars') final  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'provider_override') this.providerOverride, @JsonKey(name: 'model_registry_id') this.modelRegistryId}): _globalContextVars = globalContextVars,super._();
  factory _ExecutionMetadata.fromJson(Map<String, dynamic> json) => _$ExecutionMetadataFromJson(json);

@override@JsonKey(name: 'matrix_sampling_strategy') final  int? matrixSamplingStrategy;
@override@JsonKey(name: 'workflow_version') final  int workflowVersion;
 final  Map<String, dynamic>? _globalContextVars;
@override@JsonKey(name: 'global_context_vars') Map<String, dynamic>? get globalContextVars {
  final value = _globalContextVars;
  if (value == null) return null;
  if (_globalContextVars is EqualUnmodifiableMapView) return _globalContextVars;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'provider_override') final  LLMProvider? providerOverride;
@override@JsonKey(name: 'model_registry_id') final  String? modelRegistryId;

/// Create a copy of ExecutionMetadata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionMetadataCopyWith<_ExecutionMetadata> get copyWith => __$ExecutionMetadataCopyWithImpl<_ExecutionMetadata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionMetadataToJson(this, );
}



@override
String toString() {
  return 'ExecutionMetadata(matrixSamplingStrategy: $matrixSamplingStrategy, workflowVersion: $workflowVersion, globalContextVars: $globalContextVars, providerOverride: $providerOverride, modelRegistryId: $modelRegistryId)';
}


}

/// @nodoc
abstract mixin class _$ExecutionMetadataCopyWith<$Res> implements $ExecutionMetadataCopyWith<$Res> {
  factory _$ExecutionMetadataCopyWith(_ExecutionMetadata value, $Res Function(_ExecutionMetadata) _then) = __$ExecutionMetadataCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'matrix_sampling_strategy') int? matrixSamplingStrategy,@JsonKey(name: 'workflow_version') int workflowVersion,@JsonKey(name: 'global_context_vars') Map<String, dynamic>? globalContextVars,@JsonKey(name: 'provider_override') LLMProvider? providerOverride,@JsonKey(name: 'model_registry_id') String? modelRegistryId
});




}
/// @nodoc
class __$ExecutionMetadataCopyWithImpl<$Res>
    implements _$ExecutionMetadataCopyWith<$Res> {
  __$ExecutionMetadataCopyWithImpl(this._self, this._then);

  final _ExecutionMetadata _self;
  final $Res Function(_ExecutionMetadata) _then;

/// Create a copy of ExecutionMetadata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? matrixSamplingStrategy = freezed,Object? workflowVersion = null,Object? globalContextVars = freezed,Object? providerOverride = freezed,Object? modelRegistryId = freezed,}) {
  return _then(_ExecutionMetadata(
matrixSamplingStrategy: freezed == matrixSamplingStrategy ? _self.matrixSamplingStrategy : matrixSamplingStrategy // ignore: cast_nullable_to_non_nullable
as int?,workflowVersion: null == workflowVersion ? _self.workflowVersion : workflowVersion // ignore: cast_nullable_to_non_nullable
as int,globalContextVars: freezed == globalContextVars ? _self._globalContextVars : globalContextVars // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,providerOverride: freezed == providerOverride ? _self.providerOverride : providerOverride // ignore: cast_nullable_to_non_nullable
as LLMProvider?,modelRegistryId: freezed == modelRegistryId ? _self.modelRegistryId : modelRegistryId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
