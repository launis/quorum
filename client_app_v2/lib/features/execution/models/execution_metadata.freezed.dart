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

@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'profile_id') String? get profileId;@JsonKey(name: 'matrix_sampling_strategy') int get matrixSamplingStrategy;@JsonKey(name: 'workflow_version') int get workflowVersion;@JsonKey(name: 'user_id') String? get userId;@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'global_context_vars') Map<String, dynamic>? get globalContextVars;@JsonKey(name: 'execution_summary') Map<String, dynamic>? get executionSummary;@JsonKey(name: 'step_metrics') Map<String, dynamic>? get stepMetrics;@JsonKey(name: 'dag_cost_usd') double? get dagCostUsd;@JsonKey(name: 'prompt_tokens') int? get promptTokens;@JsonKey(name: 'completion_tokens') int? get completionTokens;@JsonKey(name: 'cached_tokens') int? get cachedTokens;@JsonKey(name: 'reasoning_tokens') int? get reasoningTokens;
/// Create a copy of ExecutionMetadata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionMetadataCopyWith<ExecutionMetadata> get copyWith => _$ExecutionMetadataCopyWithImpl<ExecutionMetadata>(this as ExecutionMetadata, _$identity);

  /// Serializes this ExecutionMetadata to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionMetadata(targetLocale: $targetLocale, profileId: $profileId, matrixSamplingStrategy: $matrixSamplingStrategy, workflowVersion: $workflowVersion, userId: $userId, organizationId: $organizationId, globalContextVars: $globalContextVars, executionSummary: $executionSummary, stepMetrics: $stepMetrics, dagCostUsd: $dagCostUsd, promptTokens: $promptTokens, completionTokens: $completionTokens, cachedTokens: $cachedTokens, reasoningTokens: $reasoningTokens)';
}


}

/// @nodoc
abstract mixin class $ExecutionMetadataCopyWith<$Res>  {
  factory $ExecutionMetadataCopyWith(ExecutionMetadata value, $Res Function(ExecutionMetadata) _then) = _$ExecutionMetadataCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'profile_id') String? profileId,@JsonKey(name: 'matrix_sampling_strategy') int matrixSamplingStrategy,@JsonKey(name: 'workflow_version') int workflowVersion,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'global_context_vars') Map<String, dynamic>? globalContextVars,@JsonKey(name: 'execution_summary') Map<String, dynamic>? executionSummary,@JsonKey(name: 'step_metrics') Map<String, dynamic>? stepMetrics,@JsonKey(name: 'dag_cost_usd') double? dagCostUsd,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'cached_tokens') int? cachedTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens
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
@pragma('vm:prefer-inline') @override $Res call({Object? targetLocale = null,Object? profileId = freezed,Object? matrixSamplingStrategy = null,Object? workflowVersion = null,Object? userId = freezed,Object? organizationId = freezed,Object? globalContextVars = freezed,Object? executionSummary = freezed,Object? stepMetrics = freezed,Object? dagCostUsd = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? cachedTokens = freezed,Object? reasoningTokens = freezed,}) {
  return _then(_self.copyWith(
targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,profileId: freezed == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String?,matrixSamplingStrategy: null == matrixSamplingStrategy ? _self.matrixSamplingStrategy : matrixSamplingStrategy // ignore: cast_nullable_to_non_nullable
as int,workflowVersion: null == workflowVersion ? _self.workflowVersion : workflowVersion // ignore: cast_nullable_to_non_nullable
as int,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,globalContextVars: freezed == globalContextVars ? _self.globalContextVars : globalContextVars // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,executionSummary: freezed == executionSummary ? _self.executionSummary : executionSummary // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepMetrics: freezed == stepMetrics ? _self.stepMetrics : stepMetrics // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,dagCostUsd: freezed == dagCostUsd ? _self.dagCostUsd : dagCostUsd // ignore: cast_nullable_to_non_nullable
as double?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,cachedTokens: freezed == cachedTokens ? _self.cachedTokens : cachedTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'profile_id')  String? profileId, @JsonKey(name: 'matrix_sampling_strategy')  int matrixSamplingStrategy, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'global_context_vars')  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'execution_summary')  Map<String, dynamic>? executionSummary, @JsonKey(name: 'step_metrics')  Map<String, dynamic>? stepMetrics, @JsonKey(name: 'dag_cost_usd')  double? dagCostUsd, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'cached_tokens')  int? cachedTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionMetadata() when $default != null:
return $default(_that.targetLocale,_that.profileId,_that.matrixSamplingStrategy,_that.workflowVersion,_that.userId,_that.organizationId,_that.globalContextVars,_that.executionSummary,_that.stepMetrics,_that.dagCostUsd,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'profile_id')  String? profileId, @JsonKey(name: 'matrix_sampling_strategy')  int matrixSamplingStrategy, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'global_context_vars')  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'execution_summary')  Map<String, dynamic>? executionSummary, @JsonKey(name: 'step_metrics')  Map<String, dynamic>? stepMetrics, @JsonKey(name: 'dag_cost_usd')  double? dagCostUsd, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'cached_tokens')  int? cachedTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens)  $default,) {final _that = this;
switch (_that) {
case _ExecutionMetadata():
return $default(_that.targetLocale,_that.profileId,_that.matrixSamplingStrategy,_that.workflowVersion,_that.userId,_that.organizationId,_that.globalContextVars,_that.executionSummary,_that.stepMetrics,_that.dagCostUsd,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'profile_id')  String? profileId, @JsonKey(name: 'matrix_sampling_strategy')  int matrixSamplingStrategy, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'global_context_vars')  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'execution_summary')  Map<String, dynamic>? executionSummary, @JsonKey(name: 'step_metrics')  Map<String, dynamic>? stepMetrics, @JsonKey(name: 'dag_cost_usd')  double? dagCostUsd, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'cached_tokens')  int? cachedTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionMetadata() when $default != null:
return $default(_that.targetLocale,_that.profileId,_that.matrixSamplingStrategy,_that.workflowVersion,_that.userId,_that.organizationId,_that.globalContextVars,_that.executionSummary,_that.stepMetrics,_that.dagCostUsd,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionMetadata extends ExecutionMetadata {
  const _ExecutionMetadata({@JsonKey(name: 'target_locale') required this.targetLocale, @JsonKey(name: 'profile_id') this.profileId, @JsonKey(name: 'matrix_sampling_strategy') this.matrixSamplingStrategy = 10, @JsonKey(name: 'workflow_version') this.workflowVersion = 1, @JsonKey(name: 'user_id') this.userId, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'global_context_vars') final  Map<String, dynamic>? globalContextVars, @JsonKey(name: 'execution_summary') final  Map<String, dynamic>? executionSummary, @JsonKey(name: 'step_metrics') final  Map<String, dynamic>? stepMetrics, @JsonKey(name: 'dag_cost_usd') this.dagCostUsd, @JsonKey(name: 'prompt_tokens') this.promptTokens, @JsonKey(name: 'completion_tokens') this.completionTokens, @JsonKey(name: 'cached_tokens') this.cachedTokens, @JsonKey(name: 'reasoning_tokens') this.reasoningTokens}): _globalContextVars = globalContextVars,_executionSummary = executionSummary,_stepMetrics = stepMetrics,super._();
  factory _ExecutionMetadata.fromJson(Map<String, dynamic> json) => _$ExecutionMetadataFromJson(json);

@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(name: 'profile_id') final  String? profileId;
@override@JsonKey(name: 'matrix_sampling_strategy') final  int matrixSamplingStrategy;
@override@JsonKey(name: 'workflow_version') final  int workflowVersion;
@override@JsonKey(name: 'user_id') final  String? userId;
@override@JsonKey(name: 'organization_id') final  String? organizationId;
 final  Map<String, dynamic>? _globalContextVars;
@override@JsonKey(name: 'global_context_vars') Map<String, dynamic>? get globalContextVars {
  final value = _globalContextVars;
  if (value == null) return null;
  if (_globalContextVars is EqualUnmodifiableMapView) return _globalContextVars;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _executionSummary;
@override@JsonKey(name: 'execution_summary') Map<String, dynamic>? get executionSummary {
  final value = _executionSummary;
  if (value == null) return null;
  if (_executionSummary is EqualUnmodifiableMapView) return _executionSummary;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepMetrics;
@override@JsonKey(name: 'step_metrics') Map<String, dynamic>? get stepMetrics {
  final value = _stepMetrics;
  if (value == null) return null;
  if (_stepMetrics is EqualUnmodifiableMapView) return _stepMetrics;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'dag_cost_usd') final  double? dagCostUsd;
@override@JsonKey(name: 'prompt_tokens') final  int? promptTokens;
@override@JsonKey(name: 'completion_tokens') final  int? completionTokens;
@override@JsonKey(name: 'cached_tokens') final  int? cachedTokens;
@override@JsonKey(name: 'reasoning_tokens') final  int? reasoningTokens;

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
  return 'ExecutionMetadata(targetLocale: $targetLocale, profileId: $profileId, matrixSamplingStrategy: $matrixSamplingStrategy, workflowVersion: $workflowVersion, userId: $userId, organizationId: $organizationId, globalContextVars: $globalContextVars, executionSummary: $executionSummary, stepMetrics: $stepMetrics, dagCostUsd: $dagCostUsd, promptTokens: $promptTokens, completionTokens: $completionTokens, cachedTokens: $cachedTokens, reasoningTokens: $reasoningTokens)';
}


}

/// @nodoc
abstract mixin class _$ExecutionMetadataCopyWith<$Res> implements $ExecutionMetadataCopyWith<$Res> {
  factory _$ExecutionMetadataCopyWith(_ExecutionMetadata value, $Res Function(_ExecutionMetadata) _then) = __$ExecutionMetadataCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'profile_id') String? profileId,@JsonKey(name: 'matrix_sampling_strategy') int matrixSamplingStrategy,@JsonKey(name: 'workflow_version') int workflowVersion,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'global_context_vars') Map<String, dynamic>? globalContextVars,@JsonKey(name: 'execution_summary') Map<String, dynamic>? executionSummary,@JsonKey(name: 'step_metrics') Map<String, dynamic>? stepMetrics,@JsonKey(name: 'dag_cost_usd') double? dagCostUsd,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'cached_tokens') int? cachedTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens
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
@override @pragma('vm:prefer-inline') $Res call({Object? targetLocale = null,Object? profileId = freezed,Object? matrixSamplingStrategy = null,Object? workflowVersion = null,Object? userId = freezed,Object? organizationId = freezed,Object? globalContextVars = freezed,Object? executionSummary = freezed,Object? stepMetrics = freezed,Object? dagCostUsd = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? cachedTokens = freezed,Object? reasoningTokens = freezed,}) {
  return _then(_ExecutionMetadata(
targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,profileId: freezed == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String?,matrixSamplingStrategy: null == matrixSamplingStrategy ? _self.matrixSamplingStrategy : matrixSamplingStrategy // ignore: cast_nullable_to_non_nullable
as int,workflowVersion: null == workflowVersion ? _self.workflowVersion : workflowVersion // ignore: cast_nullable_to_non_nullable
as int,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,globalContextVars: freezed == globalContextVars ? _self._globalContextVars : globalContextVars // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,executionSummary: freezed == executionSummary ? _self._executionSummary : executionSummary // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepMetrics: freezed == stepMetrics ? _self._stepMetrics : stepMetrics // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,dagCostUsd: freezed == dagCostUsd ? _self.dagCostUsd : dagCostUsd // ignore: cast_nullable_to_non_nullable
as double?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,cachedTokens: freezed == cachedTokens ? _self.cachedTokens : cachedTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
