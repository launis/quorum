// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_step.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionStep {

 String get id; String get label; String get status;@JsonKey(name: 'last_error') String? get lastError;@JsonKey(name: 'message_code') String? get messageCode;@JsonKey(name: 'model_strategy') String? get modelStrategy;@JsonKey(name: 'physical_model') String? get physicalModel;@JsonKey(name: 'system_fingerprint') String? get systemFingerprint;@JsonKey(name: 'prompt_tokens') int get promptTokens;@JsonKey(name: 'completion_tokens') int get completionTokens;@JsonKey(name: 'cached_tokens') int get cachedTokens;@JsonKey(name: 'reasoning_tokens') int get reasoningTokens;@JsonKey(name: 'cost_usd') double get costUsd;@JsonKey(name: 'duration_ms') int get durationMs;@JsonKey(name: 'chunk_count') int get chunkCount;@JsonKey(name: 'scorecard_atoms') Map<String, dynamic> get scorecardAtoms;
/// Create a copy of ExecutionStep
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionStepCopyWith<ExecutionStep> get copyWith => _$ExecutionStepCopyWithImpl<ExecutionStep>(this as ExecutionStep, _$identity);

  /// Serializes this ExecutionStep to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionStep(id: $id, label: $label, status: $status, lastError: $lastError, messageCode: $messageCode, modelStrategy: $modelStrategy, physicalModel: $physicalModel, systemFingerprint: $systemFingerprint, promptTokens: $promptTokens, completionTokens: $completionTokens, cachedTokens: $cachedTokens, reasoningTokens: $reasoningTokens, costUsd: $costUsd, durationMs: $durationMs, chunkCount: $chunkCount, scorecardAtoms: $scorecardAtoms)';
}


}

/// @nodoc
abstract mixin class $ExecutionStepCopyWith<$Res>  {
  factory $ExecutionStepCopyWith(ExecutionStep value, $Res Function(ExecutionStep) _then) = _$ExecutionStepCopyWithImpl;
@useResult
$Res call({
 String id, String label, String status,@JsonKey(name: 'last_error') String? lastError,@JsonKey(name: 'message_code') String? messageCode,@JsonKey(name: 'model_strategy') String? modelStrategy,@JsonKey(name: 'physical_model') String? physicalModel,@JsonKey(name: 'system_fingerprint') String? systemFingerprint,@JsonKey(name: 'prompt_tokens') int promptTokens,@JsonKey(name: 'completion_tokens') int completionTokens,@JsonKey(name: 'cached_tokens') int cachedTokens,@JsonKey(name: 'reasoning_tokens') int reasoningTokens,@JsonKey(name: 'cost_usd') double costUsd,@JsonKey(name: 'duration_ms') int durationMs,@JsonKey(name: 'chunk_count') int chunkCount,@JsonKey(name: 'scorecard_atoms') Map<String, dynamic> scorecardAtoms
});




}
/// @nodoc
class _$ExecutionStepCopyWithImpl<$Res>
    implements $ExecutionStepCopyWith<$Res> {
  _$ExecutionStepCopyWithImpl(this._self, this._then);

  final ExecutionStep _self;
  final $Res Function(ExecutionStep) _then;

/// Create a copy of ExecutionStep
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? label = null,Object? status = null,Object? lastError = freezed,Object? messageCode = freezed,Object? modelStrategy = freezed,Object? physicalModel = freezed,Object? systemFingerprint = freezed,Object? promptTokens = null,Object? completionTokens = null,Object? cachedTokens = null,Object? reasoningTokens = null,Object? costUsd = null,Object? durationMs = null,Object? chunkCount = null,Object? scorecardAtoms = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,lastError: freezed == lastError ? _self.lastError : lastError // ignore: cast_nullable_to_non_nullable
as String?,messageCode: freezed == messageCode ? _self.messageCode : messageCode // ignore: cast_nullable_to_non_nullable
as String?,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,physicalModel: freezed == physicalModel ? _self.physicalModel : physicalModel // ignore: cast_nullable_to_non_nullable
as String?,systemFingerprint: freezed == systemFingerprint ? _self.systemFingerprint : systemFingerprint // ignore: cast_nullable_to_non_nullable
as String?,promptTokens: null == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int,completionTokens: null == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int,cachedTokens: null == cachedTokens ? _self.cachedTokens : cachedTokens // ignore: cast_nullable_to_non_nullable
as int,reasoningTokens: null == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int,costUsd: null == costUsd ? _self.costUsd : costUsd // ignore: cast_nullable_to_non_nullable
as double,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,chunkCount: null == chunkCount ? _self.chunkCount : chunkCount // ignore: cast_nullable_to_non_nullable
as int,scorecardAtoms: null == scorecardAtoms ? _self.scorecardAtoms : scorecardAtoms // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionStep].
extension ExecutionStepPatterns on ExecutionStep {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionStep value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionStep() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionStep value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionStep():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionStep value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionStep() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String label,  String status, @JsonKey(name: 'last_error')  String? lastError, @JsonKey(name: 'message_code')  String? messageCode, @JsonKey(name: 'model_strategy')  String? modelStrategy, @JsonKey(name: 'physical_model')  String? physicalModel, @JsonKey(name: 'system_fingerprint')  String? systemFingerprint, @JsonKey(name: 'prompt_tokens')  int promptTokens, @JsonKey(name: 'completion_tokens')  int completionTokens, @JsonKey(name: 'cached_tokens')  int cachedTokens, @JsonKey(name: 'reasoning_tokens')  int reasoningTokens, @JsonKey(name: 'cost_usd')  double costUsd, @JsonKey(name: 'duration_ms')  int durationMs, @JsonKey(name: 'chunk_count')  int chunkCount, @JsonKey(name: 'scorecard_atoms')  Map<String, dynamic> scorecardAtoms)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionStep() when $default != null:
return $default(_that.id,_that.label,_that.status,_that.lastError,_that.messageCode,_that.modelStrategy,_that.physicalModel,_that.systemFingerprint,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens,_that.costUsd,_that.durationMs,_that.chunkCount,_that.scorecardAtoms);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String label,  String status, @JsonKey(name: 'last_error')  String? lastError, @JsonKey(name: 'message_code')  String? messageCode, @JsonKey(name: 'model_strategy')  String? modelStrategy, @JsonKey(name: 'physical_model')  String? physicalModel, @JsonKey(name: 'system_fingerprint')  String? systemFingerprint, @JsonKey(name: 'prompt_tokens')  int promptTokens, @JsonKey(name: 'completion_tokens')  int completionTokens, @JsonKey(name: 'cached_tokens')  int cachedTokens, @JsonKey(name: 'reasoning_tokens')  int reasoningTokens, @JsonKey(name: 'cost_usd')  double costUsd, @JsonKey(name: 'duration_ms')  int durationMs, @JsonKey(name: 'chunk_count')  int chunkCount, @JsonKey(name: 'scorecard_atoms')  Map<String, dynamic> scorecardAtoms)  $default,) {final _that = this;
switch (_that) {
case _ExecutionStep():
return $default(_that.id,_that.label,_that.status,_that.lastError,_that.messageCode,_that.modelStrategy,_that.physicalModel,_that.systemFingerprint,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens,_that.costUsd,_that.durationMs,_that.chunkCount,_that.scorecardAtoms);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String label,  String status, @JsonKey(name: 'last_error')  String? lastError, @JsonKey(name: 'message_code')  String? messageCode, @JsonKey(name: 'model_strategy')  String? modelStrategy, @JsonKey(name: 'physical_model')  String? physicalModel, @JsonKey(name: 'system_fingerprint')  String? systemFingerprint, @JsonKey(name: 'prompt_tokens')  int promptTokens, @JsonKey(name: 'completion_tokens')  int completionTokens, @JsonKey(name: 'cached_tokens')  int cachedTokens, @JsonKey(name: 'reasoning_tokens')  int reasoningTokens, @JsonKey(name: 'cost_usd')  double costUsd, @JsonKey(name: 'duration_ms')  int durationMs, @JsonKey(name: 'chunk_count')  int chunkCount, @JsonKey(name: 'scorecard_atoms')  Map<String, dynamic> scorecardAtoms)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionStep() when $default != null:
return $default(_that.id,_that.label,_that.status,_that.lastError,_that.messageCode,_that.modelStrategy,_that.physicalModel,_that.systemFingerprint,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens,_that.costUsd,_that.durationMs,_that.chunkCount,_that.scorecardAtoms);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionStep extends ExecutionStep {
  const _ExecutionStep({required this.id, required this.label, required this.status, @JsonKey(name: 'last_error') this.lastError, @JsonKey(name: 'message_code') this.messageCode, @JsonKey(name: 'model_strategy') this.modelStrategy, @JsonKey(name: 'physical_model') this.physicalModel, @JsonKey(name: 'system_fingerprint') this.systemFingerprint, @JsonKey(name: 'prompt_tokens') this.promptTokens = 0, @JsonKey(name: 'completion_tokens') this.completionTokens = 0, @JsonKey(name: 'cached_tokens') this.cachedTokens = 0, @JsonKey(name: 'reasoning_tokens') this.reasoningTokens = 0, @JsonKey(name: 'cost_usd') this.costUsd = 0.0, @JsonKey(name: 'duration_ms') this.durationMs = 0, @JsonKey(name: 'chunk_count') this.chunkCount = 1, @JsonKey(name: 'scorecard_atoms') final  Map<String, dynamic> scorecardAtoms = const {}}): _scorecardAtoms = scorecardAtoms,super._();
  factory _ExecutionStep.fromJson(Map<String, dynamic> json) => _$ExecutionStepFromJson(json);

@override final  String id;
@override final  String label;
@override final  String status;
@override@JsonKey(name: 'last_error') final  String? lastError;
@override@JsonKey(name: 'message_code') final  String? messageCode;
@override@JsonKey(name: 'model_strategy') final  String? modelStrategy;
@override@JsonKey(name: 'physical_model') final  String? physicalModel;
@override@JsonKey(name: 'system_fingerprint') final  String? systemFingerprint;
@override@JsonKey(name: 'prompt_tokens') final  int promptTokens;
@override@JsonKey(name: 'completion_tokens') final  int completionTokens;
@override@JsonKey(name: 'cached_tokens') final  int cachedTokens;
@override@JsonKey(name: 'reasoning_tokens') final  int reasoningTokens;
@override@JsonKey(name: 'cost_usd') final  double costUsd;
@override@JsonKey(name: 'duration_ms') final  int durationMs;
@override@JsonKey(name: 'chunk_count') final  int chunkCount;
 final  Map<String, dynamic> _scorecardAtoms;
@override@JsonKey(name: 'scorecard_atoms') Map<String, dynamic> get scorecardAtoms {
  if (_scorecardAtoms is EqualUnmodifiableMapView) return _scorecardAtoms;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_scorecardAtoms);
}


/// Create a copy of ExecutionStep
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionStepCopyWith<_ExecutionStep> get copyWith => __$ExecutionStepCopyWithImpl<_ExecutionStep>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionStepToJson(this, );
}



@override
String toString() {
  return 'ExecutionStep(id: $id, label: $label, status: $status, lastError: $lastError, messageCode: $messageCode, modelStrategy: $modelStrategy, physicalModel: $physicalModel, systemFingerprint: $systemFingerprint, promptTokens: $promptTokens, completionTokens: $completionTokens, cachedTokens: $cachedTokens, reasoningTokens: $reasoningTokens, costUsd: $costUsd, durationMs: $durationMs, chunkCount: $chunkCount, scorecardAtoms: $scorecardAtoms)';
}


}

/// @nodoc
abstract mixin class _$ExecutionStepCopyWith<$Res> implements $ExecutionStepCopyWith<$Res> {
  factory _$ExecutionStepCopyWith(_ExecutionStep value, $Res Function(_ExecutionStep) _then) = __$ExecutionStepCopyWithImpl;
@override @useResult
$Res call({
 String id, String label, String status,@JsonKey(name: 'last_error') String? lastError,@JsonKey(name: 'message_code') String? messageCode,@JsonKey(name: 'model_strategy') String? modelStrategy,@JsonKey(name: 'physical_model') String? physicalModel,@JsonKey(name: 'system_fingerprint') String? systemFingerprint,@JsonKey(name: 'prompt_tokens') int promptTokens,@JsonKey(name: 'completion_tokens') int completionTokens,@JsonKey(name: 'cached_tokens') int cachedTokens,@JsonKey(name: 'reasoning_tokens') int reasoningTokens,@JsonKey(name: 'cost_usd') double costUsd,@JsonKey(name: 'duration_ms') int durationMs,@JsonKey(name: 'chunk_count') int chunkCount,@JsonKey(name: 'scorecard_atoms') Map<String, dynamic> scorecardAtoms
});




}
/// @nodoc
class __$ExecutionStepCopyWithImpl<$Res>
    implements _$ExecutionStepCopyWith<$Res> {
  __$ExecutionStepCopyWithImpl(this._self, this._then);

  final _ExecutionStep _self;
  final $Res Function(_ExecutionStep) _then;

/// Create a copy of ExecutionStep
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? label = null,Object? status = null,Object? lastError = freezed,Object? messageCode = freezed,Object? modelStrategy = freezed,Object? physicalModel = freezed,Object? systemFingerprint = freezed,Object? promptTokens = null,Object? completionTokens = null,Object? cachedTokens = null,Object? reasoningTokens = null,Object? costUsd = null,Object? durationMs = null,Object? chunkCount = null,Object? scorecardAtoms = null,}) {
  return _then(_ExecutionStep(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,lastError: freezed == lastError ? _self.lastError : lastError // ignore: cast_nullable_to_non_nullable
as String?,messageCode: freezed == messageCode ? _self.messageCode : messageCode // ignore: cast_nullable_to_non_nullable
as String?,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,physicalModel: freezed == physicalModel ? _self.physicalModel : physicalModel // ignore: cast_nullable_to_non_nullable
as String?,systemFingerprint: freezed == systemFingerprint ? _self.systemFingerprint : systemFingerprint // ignore: cast_nullable_to_non_nullable
as String?,promptTokens: null == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int,completionTokens: null == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int,cachedTokens: null == cachedTokens ? _self.cachedTokens : cachedTokens // ignore: cast_nullable_to_non_nullable
as int,reasoningTokens: null == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int,costUsd: null == costUsd ? _self.costUsd : costUsd // ignore: cast_nullable_to_non_nullable
as double,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,chunkCount: null == chunkCount ? _self.chunkCount : chunkCount // ignore: cast_nullable_to_non_nullable
as int,scorecardAtoms: null == scorecardAtoms ? _self._scorecardAtoms : scorecardAtoms // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
