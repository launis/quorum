// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_record.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ContextVariablesDto {

@JsonKey(name: 'global_atom_blackboard') Object? get globalAtomBlackboard;@JsonKey(name: 'matrix_reducer_output') Object? get matrixReducerOutput;@JsonKey(name: 'report_context') Object? get reportContext;@JsonKey(name: 'step_detector') Object? get stepDetector;@JsonKey(name: 'evaluated_matrices') Object? get evaluatedMatrices; Map<String, ContextVariableEntry> get variables;
/// Create a copy of ContextVariablesDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ContextVariablesDtoCopyWith<ContextVariablesDto> get copyWith => _$ContextVariablesDtoCopyWithImpl<ContextVariablesDto>(this as ContextVariablesDto, _$identity);

  /// Serializes this ContextVariablesDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ContextVariablesDto(globalAtomBlackboard: $globalAtomBlackboard, matrixReducerOutput: $matrixReducerOutput, reportContext: $reportContext, stepDetector: $stepDetector, evaluatedMatrices: $evaluatedMatrices, variables: $variables)';
}


}

/// @nodoc
abstract mixin class $ContextVariablesDtoCopyWith<$Res>  {
  factory $ContextVariablesDtoCopyWith(ContextVariablesDto value, $Res Function(ContextVariablesDto) _then) = _$ContextVariablesDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'global_atom_blackboard') Object? globalAtomBlackboard,@JsonKey(name: 'matrix_reducer_output') Object? matrixReducerOutput,@JsonKey(name: 'report_context') Object? reportContext,@JsonKey(name: 'step_detector') Object? stepDetector,@JsonKey(name: 'evaluated_matrices') Object? evaluatedMatrices, Map<String, ContextVariableEntry> variables
});




}
/// @nodoc
class _$ContextVariablesDtoCopyWithImpl<$Res>
    implements $ContextVariablesDtoCopyWith<$Res> {
  _$ContextVariablesDtoCopyWithImpl(this._self, this._then);

  final ContextVariablesDto _self;
  final $Res Function(ContextVariablesDto) _then;

/// Create a copy of ContextVariablesDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? globalAtomBlackboard = freezed,Object? matrixReducerOutput = freezed,Object? reportContext = freezed,Object? stepDetector = freezed,Object? evaluatedMatrices = freezed,Object? variables = null,}) {
  return _then(_self.copyWith(
globalAtomBlackboard: freezed == globalAtomBlackboard ? _self.globalAtomBlackboard : globalAtomBlackboard ,matrixReducerOutput: freezed == matrixReducerOutput ? _self.matrixReducerOutput : matrixReducerOutput ,reportContext: freezed == reportContext ? _self.reportContext : reportContext ,stepDetector: freezed == stepDetector ? _self.stepDetector : stepDetector ,evaluatedMatrices: freezed == evaluatedMatrices ? _self.evaluatedMatrices : evaluatedMatrices ,variables: null == variables ? _self.variables : variables // ignore: cast_nullable_to_non_nullable
as Map<String, ContextVariableEntry>,
  ));
}

}


/// Adds pattern-matching-related methods to [ContextVariablesDto].
extension ContextVariablesDtoPatterns on ContextVariablesDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ContextVariablesDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ContextVariablesDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ContextVariablesDto value)  $default,){
final _that = this;
switch (_that) {
case _ContextVariablesDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ContextVariablesDto value)?  $default,){
final _that = this;
switch (_that) {
case _ContextVariablesDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'global_atom_blackboard')  Object? globalAtomBlackboard, @JsonKey(name: 'matrix_reducer_output')  Object? matrixReducerOutput, @JsonKey(name: 'report_context')  Object? reportContext, @JsonKey(name: 'step_detector')  Object? stepDetector, @JsonKey(name: 'evaluated_matrices')  Object? evaluatedMatrices,  Map<String, ContextVariableEntry> variables)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ContextVariablesDto() when $default != null:
return $default(_that.globalAtomBlackboard,_that.matrixReducerOutput,_that.reportContext,_that.stepDetector,_that.evaluatedMatrices,_that.variables);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'global_atom_blackboard')  Object? globalAtomBlackboard, @JsonKey(name: 'matrix_reducer_output')  Object? matrixReducerOutput, @JsonKey(name: 'report_context')  Object? reportContext, @JsonKey(name: 'step_detector')  Object? stepDetector, @JsonKey(name: 'evaluated_matrices')  Object? evaluatedMatrices,  Map<String, ContextVariableEntry> variables)  $default,) {final _that = this;
switch (_that) {
case _ContextVariablesDto():
return $default(_that.globalAtomBlackboard,_that.matrixReducerOutput,_that.reportContext,_that.stepDetector,_that.evaluatedMatrices,_that.variables);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'global_atom_blackboard')  Object? globalAtomBlackboard, @JsonKey(name: 'matrix_reducer_output')  Object? matrixReducerOutput, @JsonKey(name: 'report_context')  Object? reportContext, @JsonKey(name: 'step_detector')  Object? stepDetector, @JsonKey(name: 'evaluated_matrices')  Object? evaluatedMatrices,  Map<String, ContextVariableEntry> variables)?  $default,) {final _that = this;
switch (_that) {
case _ContextVariablesDto() when $default != null:
return $default(_that.globalAtomBlackboard,_that.matrixReducerOutput,_that.reportContext,_that.stepDetector,_that.evaluatedMatrices,_that.variables);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ContextVariablesDto extends ContextVariablesDto {
  const _ContextVariablesDto({@JsonKey(name: 'global_atom_blackboard') this.globalAtomBlackboard, @JsonKey(name: 'matrix_reducer_output') this.matrixReducerOutput, @JsonKey(name: 'report_context') this.reportContext, @JsonKey(name: 'step_detector') this.stepDetector, @JsonKey(name: 'evaluated_matrices') this.evaluatedMatrices, final  Map<String, ContextVariableEntry> variables = const <String, ContextVariableEntry>{}}): _variables = variables,super._();
  factory _ContextVariablesDto.fromJson(Map<String, dynamic> json) => _$ContextVariablesDtoFromJson(json);

@override@JsonKey(name: 'global_atom_blackboard') final  Object? globalAtomBlackboard;
@override@JsonKey(name: 'matrix_reducer_output') final  Object? matrixReducerOutput;
@override@JsonKey(name: 'report_context') final  Object? reportContext;
@override@JsonKey(name: 'step_detector') final  Object? stepDetector;
@override@JsonKey(name: 'evaluated_matrices') final  Object? evaluatedMatrices;
 final  Map<String, ContextVariableEntry> _variables;
@override@JsonKey() Map<String, ContextVariableEntry> get variables {
  if (_variables is EqualUnmodifiableMapView) return _variables;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_variables);
}


/// Create a copy of ContextVariablesDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ContextVariablesDtoCopyWith<_ContextVariablesDto> get copyWith => __$ContextVariablesDtoCopyWithImpl<_ContextVariablesDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ContextVariablesDtoToJson(this, );
}



@override
String toString() {
  return 'ContextVariablesDto(globalAtomBlackboard: $globalAtomBlackboard, matrixReducerOutput: $matrixReducerOutput, reportContext: $reportContext, stepDetector: $stepDetector, evaluatedMatrices: $evaluatedMatrices, variables: $variables)';
}


}

/// @nodoc
abstract mixin class _$ContextVariablesDtoCopyWith<$Res> implements $ContextVariablesDtoCopyWith<$Res> {
  factory _$ContextVariablesDtoCopyWith(_ContextVariablesDto value, $Res Function(_ContextVariablesDto) _then) = __$ContextVariablesDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'global_atom_blackboard') Object? globalAtomBlackboard,@JsonKey(name: 'matrix_reducer_output') Object? matrixReducerOutput,@JsonKey(name: 'report_context') Object? reportContext,@JsonKey(name: 'step_detector') Object? stepDetector,@JsonKey(name: 'evaluated_matrices') Object? evaluatedMatrices, Map<String, ContextVariableEntry> variables
});




}
/// @nodoc
class __$ContextVariablesDtoCopyWithImpl<$Res>
    implements _$ContextVariablesDtoCopyWith<$Res> {
  __$ContextVariablesDtoCopyWithImpl(this._self, this._then);

  final _ContextVariablesDto _self;
  final $Res Function(_ContextVariablesDto) _then;

/// Create a copy of ContextVariablesDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? globalAtomBlackboard = freezed,Object? matrixReducerOutput = freezed,Object? reportContext = freezed,Object? stepDetector = freezed,Object? evaluatedMatrices = freezed,Object? variables = null,}) {
  return _then(_ContextVariablesDto(
globalAtomBlackboard: freezed == globalAtomBlackboard ? _self.globalAtomBlackboard : globalAtomBlackboard ,matrixReducerOutput: freezed == matrixReducerOutput ? _self.matrixReducerOutput : matrixReducerOutput ,reportContext: freezed == reportContext ? _self.reportContext : reportContext ,stepDetector: freezed == stepDetector ? _self.stepDetector : stepDetector ,evaluatedMatrices: freezed == evaluatedMatrices ? _self.evaluatedMatrices : evaluatedMatrices ,variables: null == variables ? _self._variables : variables // ignore: cast_nullable_to_non_nullable
as Map<String, ContextVariableEntry>,
  ));
}


}


/// @nodoc
mixin _$ExecutionTraceItemDto {

@JsonKey(name: 'event_id') String? get eventId; int? get v; String? get timestamp;@JsonKey(name: 'step_name') String? get stepName;@JsonKey(name: 'event_type') String? get eventType; Object? get content; Object? get reasoning; Object? get metadata;@JsonKey(name: 'mcp_audit_traces') List<Object?> get mcpAuditTraces;@JsonKey(name: 'error_code') String? get errorCode;@JsonKey(name: 'error_message') String? get errorMessage;@JsonKey(name: 'redacted_hash') String? get redactedHash;
/// Create a copy of ExecutionTraceItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionTraceItemDtoCopyWith<ExecutionTraceItemDto> get copyWith => _$ExecutionTraceItemDtoCopyWithImpl<ExecutionTraceItemDto>(this as ExecutionTraceItemDto, _$identity);

  /// Serializes this ExecutionTraceItemDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionTraceItemDto(eventId: $eventId, v: $v, timestamp: $timestamp, stepName: $stepName, eventType: $eventType, content: $content, reasoning: $reasoning, metadata: $metadata, mcpAuditTraces: $mcpAuditTraces, errorCode: $errorCode, errorMessage: $errorMessage, redactedHash: $redactedHash)';
}


}

/// @nodoc
abstract mixin class $ExecutionTraceItemDtoCopyWith<$Res>  {
  factory $ExecutionTraceItemDtoCopyWith(ExecutionTraceItemDto value, $Res Function(ExecutionTraceItemDto) _then) = _$ExecutionTraceItemDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'event_id') String? eventId, int? v, String? timestamp,@JsonKey(name: 'step_name') String? stepName,@JsonKey(name: 'event_type') String? eventType, Object? content, Object? reasoning, Object? metadata,@JsonKey(name: 'mcp_audit_traces') List<Object?> mcpAuditTraces,@JsonKey(name: 'error_code') String? errorCode,@JsonKey(name: 'error_message') String? errorMessage,@JsonKey(name: 'redacted_hash') String? redactedHash
});




}
/// @nodoc
class _$ExecutionTraceItemDtoCopyWithImpl<$Res>
    implements $ExecutionTraceItemDtoCopyWith<$Res> {
  _$ExecutionTraceItemDtoCopyWithImpl(this._self, this._then);

  final ExecutionTraceItemDto _self;
  final $Res Function(ExecutionTraceItemDto) _then;

/// Create a copy of ExecutionTraceItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? eventId = freezed,Object? v = freezed,Object? timestamp = freezed,Object? stepName = freezed,Object? eventType = freezed,Object? content = freezed,Object? reasoning = freezed,Object? metadata = freezed,Object? mcpAuditTraces = null,Object? errorCode = freezed,Object? errorMessage = freezed,Object? redactedHash = freezed,}) {
  return _then(_self.copyWith(
eventId: freezed == eventId ? _self.eventId : eventId // ignore: cast_nullable_to_non_nullable
as String?,v: freezed == v ? _self.v : v // ignore: cast_nullable_to_non_nullable
as int?,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,stepName: freezed == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String?,eventType: freezed == eventType ? _self.eventType : eventType // ignore: cast_nullable_to_non_nullable
as String?,content: freezed == content ? _self.content : content ,reasoning: freezed == reasoning ? _self.reasoning : reasoning ,metadata: freezed == metadata ? _self.metadata : metadata ,mcpAuditTraces: null == mcpAuditTraces ? _self.mcpAuditTraces : mcpAuditTraces // ignore: cast_nullable_to_non_nullable
as List<Object?>,errorCode: freezed == errorCode ? _self.errorCode : errorCode // ignore: cast_nullable_to_non_nullable
as String?,errorMessage: freezed == errorMessage ? _self.errorMessage : errorMessage // ignore: cast_nullable_to_non_nullable
as String?,redactedHash: freezed == redactedHash ? _self.redactedHash : redactedHash // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionTraceItemDto].
extension ExecutionTraceItemDtoPatterns on ExecutionTraceItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionTraceItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionTraceItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionTraceItemDto value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionTraceItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionTraceItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionTraceItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'event_id')  String? eventId,  int? v,  String? timestamp, @JsonKey(name: 'step_name')  String? stepName, @JsonKey(name: 'event_type')  String? eventType,  Object? content,  Object? reasoning,  Object? metadata, @JsonKey(name: 'mcp_audit_traces')  List<Object?> mcpAuditTraces, @JsonKey(name: 'error_code')  String? errorCode, @JsonKey(name: 'error_message')  String? errorMessage, @JsonKey(name: 'redacted_hash')  String? redactedHash)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionTraceItemDto() when $default != null:
return $default(_that.eventId,_that.v,_that.timestamp,_that.stepName,_that.eventType,_that.content,_that.reasoning,_that.metadata,_that.mcpAuditTraces,_that.errorCode,_that.errorMessage,_that.redactedHash);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'event_id')  String? eventId,  int? v,  String? timestamp, @JsonKey(name: 'step_name')  String? stepName, @JsonKey(name: 'event_type')  String? eventType,  Object? content,  Object? reasoning,  Object? metadata, @JsonKey(name: 'mcp_audit_traces')  List<Object?> mcpAuditTraces, @JsonKey(name: 'error_code')  String? errorCode, @JsonKey(name: 'error_message')  String? errorMessage, @JsonKey(name: 'redacted_hash')  String? redactedHash)  $default,) {final _that = this;
switch (_that) {
case _ExecutionTraceItemDto():
return $default(_that.eventId,_that.v,_that.timestamp,_that.stepName,_that.eventType,_that.content,_that.reasoning,_that.metadata,_that.mcpAuditTraces,_that.errorCode,_that.errorMessage,_that.redactedHash);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'event_id')  String? eventId,  int? v,  String? timestamp, @JsonKey(name: 'step_name')  String? stepName, @JsonKey(name: 'event_type')  String? eventType,  Object? content,  Object? reasoning,  Object? metadata, @JsonKey(name: 'mcp_audit_traces')  List<Object?> mcpAuditTraces, @JsonKey(name: 'error_code')  String? errorCode, @JsonKey(name: 'error_message')  String? errorMessage, @JsonKey(name: 'redacted_hash')  String? redactedHash)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionTraceItemDto() when $default != null:
return $default(_that.eventId,_that.v,_that.timestamp,_that.stepName,_that.eventType,_that.content,_that.reasoning,_that.metadata,_that.mcpAuditTraces,_that.errorCode,_that.errorMessage,_that.redactedHash);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionTraceItemDto extends ExecutionTraceItemDto {
  const _ExecutionTraceItemDto({@JsonKey(name: 'event_id') this.eventId, this.v, this.timestamp, @JsonKey(name: 'step_name') this.stepName, @JsonKey(name: 'event_type') this.eventType, this.content, this.reasoning, this.metadata, @JsonKey(name: 'mcp_audit_traces') final  List<Object?> mcpAuditTraces = const <Object?>[], @JsonKey(name: 'error_code') this.errorCode, @JsonKey(name: 'error_message') this.errorMessage, @JsonKey(name: 'redacted_hash') this.redactedHash}): _mcpAuditTraces = mcpAuditTraces,super._();
  factory _ExecutionTraceItemDto.fromJson(Map<String, dynamic> json) => _$ExecutionTraceItemDtoFromJson(json);

@override@JsonKey(name: 'event_id') final  String? eventId;
@override final  int? v;
@override final  String? timestamp;
@override@JsonKey(name: 'step_name') final  String? stepName;
@override@JsonKey(name: 'event_type') final  String? eventType;
@override final  Object? content;
@override final  Object? reasoning;
@override final  Object? metadata;
 final  List<Object?> _mcpAuditTraces;
@override@JsonKey(name: 'mcp_audit_traces') List<Object?> get mcpAuditTraces {
  if (_mcpAuditTraces is EqualUnmodifiableListView) return _mcpAuditTraces;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mcpAuditTraces);
}

@override@JsonKey(name: 'error_code') final  String? errorCode;
@override@JsonKey(name: 'error_message') final  String? errorMessage;
@override@JsonKey(name: 'redacted_hash') final  String? redactedHash;

/// Create a copy of ExecutionTraceItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionTraceItemDtoCopyWith<_ExecutionTraceItemDto> get copyWith => __$ExecutionTraceItemDtoCopyWithImpl<_ExecutionTraceItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionTraceItemDtoToJson(this, );
}



@override
String toString() {
  return 'ExecutionTraceItemDto(eventId: $eventId, v: $v, timestamp: $timestamp, stepName: $stepName, eventType: $eventType, content: $content, reasoning: $reasoning, metadata: $metadata, mcpAuditTraces: $mcpAuditTraces, errorCode: $errorCode, errorMessage: $errorMessage, redactedHash: $redactedHash)';
}


}

/// @nodoc
abstract mixin class _$ExecutionTraceItemDtoCopyWith<$Res> implements $ExecutionTraceItemDtoCopyWith<$Res> {
  factory _$ExecutionTraceItemDtoCopyWith(_ExecutionTraceItemDto value, $Res Function(_ExecutionTraceItemDto) _then) = __$ExecutionTraceItemDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'event_id') String? eventId, int? v, String? timestamp,@JsonKey(name: 'step_name') String? stepName,@JsonKey(name: 'event_type') String? eventType, Object? content, Object? reasoning, Object? metadata,@JsonKey(name: 'mcp_audit_traces') List<Object?> mcpAuditTraces,@JsonKey(name: 'error_code') String? errorCode,@JsonKey(name: 'error_message') String? errorMessage,@JsonKey(name: 'redacted_hash') String? redactedHash
});




}
/// @nodoc
class __$ExecutionTraceItemDtoCopyWithImpl<$Res>
    implements _$ExecutionTraceItemDtoCopyWith<$Res> {
  __$ExecutionTraceItemDtoCopyWithImpl(this._self, this._then);

  final _ExecutionTraceItemDto _self;
  final $Res Function(_ExecutionTraceItemDto) _then;

/// Create a copy of ExecutionTraceItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? eventId = freezed,Object? v = freezed,Object? timestamp = freezed,Object? stepName = freezed,Object? eventType = freezed,Object? content = freezed,Object? reasoning = freezed,Object? metadata = freezed,Object? mcpAuditTraces = null,Object? errorCode = freezed,Object? errorMessage = freezed,Object? redactedHash = freezed,}) {
  return _then(_ExecutionTraceItemDto(
eventId: freezed == eventId ? _self.eventId : eventId // ignore: cast_nullable_to_non_nullable
as String?,v: freezed == v ? _self.v : v // ignore: cast_nullable_to_non_nullable
as int?,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,stepName: freezed == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String?,eventType: freezed == eventType ? _self.eventType : eventType // ignore: cast_nullable_to_non_nullable
as String?,content: freezed == content ? _self.content : content ,reasoning: freezed == reasoning ? _self.reasoning : reasoning ,metadata: freezed == metadata ? _self.metadata : metadata ,mcpAuditTraces: null == mcpAuditTraces ? _self._mcpAuditTraces : mcpAuditTraces // ignore: cast_nullable_to_non_nullable
as List<Object?>,errorCode: freezed == errorCode ? _self.errorCode : errorCode // ignore: cast_nullable_to_non_nullable
as String?,errorMessage: freezed == errorMessage ? _self.errorMessage : errorMessage // ignore: cast_nullable_to_non_nullable
as String?,redactedHash: freezed == redactedHash ? _self.redactedHash : redactedHash // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ProfileSynthesisEntryDto {

@JsonKey(name: 'section_syntheses') Map<String, ContextVariableEntry> get sectionSyntheses;@JsonKey(name: 'row_explanations') Map<String, String> get rowExplanations;@JsonKey(name: 'row_curated_quotes') Map<String, List<String>> get rowCuratedQuotes;@JsonKey(name: 'variance_explanation') String? get varianceExplanation;@JsonKey(name: 'authenticity_explanation') String? get authenticityExplanation;@JsonKey(name: 'cited_sources') List<String> get citedSources;@JsonKey(name: 'xai_highlights') List<Object?> get xaiHighlights;@JsonKey(name: 'user_role') String? get userRole;@JsonKey(name: 'user_role_justification') String? get userRoleJustification;@JsonKey(name: 'extension_metrics') Object? get extensionMetrics;@JsonKey(name: 'data_starvation') Object? get dataStarvation;@JsonKey(name: 'created_at') String? get createdAt;
/// Create a copy of ProfileSynthesisEntryDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProfileSynthesisEntryDtoCopyWith<ProfileSynthesisEntryDto> get copyWith => _$ProfileSynthesisEntryDtoCopyWithImpl<ProfileSynthesisEntryDto>(this as ProfileSynthesisEntryDto, _$identity);

  /// Serializes this ProfileSynthesisEntryDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ProfileSynthesisEntryDto(sectionSyntheses: $sectionSyntheses, rowExplanations: $rowExplanations, rowCuratedQuotes: $rowCuratedQuotes, varianceExplanation: $varianceExplanation, authenticityExplanation: $authenticityExplanation, citedSources: $citedSources, xaiHighlights: $xaiHighlights, userRole: $userRole, userRoleJustification: $userRoleJustification, extensionMetrics: $extensionMetrics, dataStarvation: $dataStarvation, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $ProfileSynthesisEntryDtoCopyWith<$Res>  {
  factory $ProfileSynthesisEntryDtoCopyWith(ProfileSynthesisEntryDto value, $Res Function(ProfileSynthesisEntryDto) _then) = _$ProfileSynthesisEntryDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'section_syntheses') Map<String, ContextVariableEntry> sectionSyntheses,@JsonKey(name: 'row_explanations') Map<String, String> rowExplanations,@JsonKey(name: 'row_curated_quotes') Map<String, List<String>> rowCuratedQuotes,@JsonKey(name: 'variance_explanation') String? varianceExplanation,@JsonKey(name: 'authenticity_explanation') String? authenticityExplanation,@JsonKey(name: 'cited_sources') List<String> citedSources,@JsonKey(name: 'xai_highlights') List<Object?> xaiHighlights,@JsonKey(name: 'user_role') String? userRole,@JsonKey(name: 'user_role_justification') String? userRoleJustification,@JsonKey(name: 'extension_metrics') Object? extensionMetrics,@JsonKey(name: 'data_starvation') Object? dataStarvation,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class _$ProfileSynthesisEntryDtoCopyWithImpl<$Res>
    implements $ProfileSynthesisEntryDtoCopyWith<$Res> {
  _$ProfileSynthesisEntryDtoCopyWithImpl(this._self, this._then);

  final ProfileSynthesisEntryDto _self;
  final $Res Function(ProfileSynthesisEntryDto) _then;

/// Create a copy of ProfileSynthesisEntryDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sectionSyntheses = null,Object? rowExplanations = null,Object? rowCuratedQuotes = null,Object? varianceExplanation = freezed,Object? authenticityExplanation = freezed,Object? citedSources = null,Object? xaiHighlights = null,Object? userRole = freezed,Object? userRoleJustification = freezed,Object? extensionMetrics = freezed,Object? dataStarvation = freezed,Object? createdAt = freezed,}) {
  return _then(_self.copyWith(
sectionSyntheses: null == sectionSyntheses ? _self.sectionSyntheses : sectionSyntheses // ignore: cast_nullable_to_non_nullable
as Map<String, ContextVariableEntry>,rowExplanations: null == rowExplanations ? _self.rowExplanations : rowExplanations // ignore: cast_nullable_to_non_nullable
as Map<String, String>,rowCuratedQuotes: null == rowCuratedQuotes ? _self.rowCuratedQuotes : rowCuratedQuotes // ignore: cast_nullable_to_non_nullable
as Map<String, List<String>>,varianceExplanation: freezed == varianceExplanation ? _self.varianceExplanation : varianceExplanation // ignore: cast_nullable_to_non_nullable
as String?,authenticityExplanation: freezed == authenticityExplanation ? _self.authenticityExplanation : authenticityExplanation // ignore: cast_nullable_to_non_nullable
as String?,citedSources: null == citedSources ? _self.citedSources : citedSources // ignore: cast_nullable_to_non_nullable
as List<String>,xaiHighlights: null == xaiHighlights ? _self.xaiHighlights : xaiHighlights // ignore: cast_nullable_to_non_nullable
as List<Object?>,userRole: freezed == userRole ? _self.userRole : userRole // ignore: cast_nullable_to_non_nullable
as String?,userRoleJustification: freezed == userRoleJustification ? _self.userRoleJustification : userRoleJustification // ignore: cast_nullable_to_non_nullable
as String?,extensionMetrics: freezed == extensionMetrics ? _self.extensionMetrics : extensionMetrics ,dataStarvation: freezed == dataStarvation ? _self.dataStarvation : dataStarvation ,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ProfileSynthesisEntryDto].
extension ProfileSynthesisEntryDtoPatterns on ProfileSynthesisEntryDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ProfileSynthesisEntryDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ProfileSynthesisEntryDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ProfileSynthesisEntryDto value)  $default,){
final _that = this;
switch (_that) {
case _ProfileSynthesisEntryDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ProfileSynthesisEntryDto value)?  $default,){
final _that = this;
switch (_that) {
case _ProfileSynthesisEntryDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'section_syntheses')  Map<String, ContextVariableEntry> sectionSyntheses, @JsonKey(name: 'row_explanations')  Map<String, String> rowExplanations, @JsonKey(name: 'row_curated_quotes')  Map<String, List<String>> rowCuratedQuotes, @JsonKey(name: 'variance_explanation')  String? varianceExplanation, @JsonKey(name: 'authenticity_explanation')  String? authenticityExplanation, @JsonKey(name: 'cited_sources')  List<String> citedSources, @JsonKey(name: 'xai_highlights')  List<Object?> xaiHighlights, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'user_role_justification')  String? userRoleJustification, @JsonKey(name: 'extension_metrics')  Object? extensionMetrics, @JsonKey(name: 'data_starvation')  Object? dataStarvation, @JsonKey(name: 'created_at')  String? createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ProfileSynthesisEntryDto() when $default != null:
return $default(_that.sectionSyntheses,_that.rowExplanations,_that.rowCuratedQuotes,_that.varianceExplanation,_that.authenticityExplanation,_that.citedSources,_that.xaiHighlights,_that.userRole,_that.userRoleJustification,_that.extensionMetrics,_that.dataStarvation,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'section_syntheses')  Map<String, ContextVariableEntry> sectionSyntheses, @JsonKey(name: 'row_explanations')  Map<String, String> rowExplanations, @JsonKey(name: 'row_curated_quotes')  Map<String, List<String>> rowCuratedQuotes, @JsonKey(name: 'variance_explanation')  String? varianceExplanation, @JsonKey(name: 'authenticity_explanation')  String? authenticityExplanation, @JsonKey(name: 'cited_sources')  List<String> citedSources, @JsonKey(name: 'xai_highlights')  List<Object?> xaiHighlights, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'user_role_justification')  String? userRoleJustification, @JsonKey(name: 'extension_metrics')  Object? extensionMetrics, @JsonKey(name: 'data_starvation')  Object? dataStarvation, @JsonKey(name: 'created_at')  String? createdAt)  $default,) {final _that = this;
switch (_that) {
case _ProfileSynthesisEntryDto():
return $default(_that.sectionSyntheses,_that.rowExplanations,_that.rowCuratedQuotes,_that.varianceExplanation,_that.authenticityExplanation,_that.citedSources,_that.xaiHighlights,_that.userRole,_that.userRoleJustification,_that.extensionMetrics,_that.dataStarvation,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'section_syntheses')  Map<String, ContextVariableEntry> sectionSyntheses, @JsonKey(name: 'row_explanations')  Map<String, String> rowExplanations, @JsonKey(name: 'row_curated_quotes')  Map<String, List<String>> rowCuratedQuotes, @JsonKey(name: 'variance_explanation')  String? varianceExplanation, @JsonKey(name: 'authenticity_explanation')  String? authenticityExplanation, @JsonKey(name: 'cited_sources')  List<String> citedSources, @JsonKey(name: 'xai_highlights')  List<Object?> xaiHighlights, @JsonKey(name: 'user_role')  String? userRole, @JsonKey(name: 'user_role_justification')  String? userRoleJustification, @JsonKey(name: 'extension_metrics')  Object? extensionMetrics, @JsonKey(name: 'data_starvation')  Object? dataStarvation, @JsonKey(name: 'created_at')  String? createdAt)?  $default,) {final _that = this;
switch (_that) {
case _ProfileSynthesisEntryDto() when $default != null:
return $default(_that.sectionSyntheses,_that.rowExplanations,_that.rowCuratedQuotes,_that.varianceExplanation,_that.authenticityExplanation,_that.citedSources,_that.xaiHighlights,_that.userRole,_that.userRoleJustification,_that.extensionMetrics,_that.dataStarvation,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ProfileSynthesisEntryDto extends ProfileSynthesisEntryDto {
  const _ProfileSynthesisEntryDto({@JsonKey(name: 'section_syntheses') final  Map<String, ContextVariableEntry> sectionSyntheses = const <String, ContextVariableEntry>{}, @JsonKey(name: 'row_explanations') final  Map<String, String> rowExplanations = const <String, String>{}, @JsonKey(name: 'row_curated_quotes') final  Map<String, List<String>> rowCuratedQuotes = const <String, List<String>>{}, @JsonKey(name: 'variance_explanation') this.varianceExplanation, @JsonKey(name: 'authenticity_explanation') this.authenticityExplanation, @JsonKey(name: 'cited_sources') final  List<String> citedSources = const <String>[], @JsonKey(name: 'xai_highlights') final  List<Object?> xaiHighlights = const <Object?>[], @JsonKey(name: 'user_role') this.userRole, @JsonKey(name: 'user_role_justification') this.userRoleJustification, @JsonKey(name: 'extension_metrics') this.extensionMetrics, @JsonKey(name: 'data_starvation') this.dataStarvation, @JsonKey(name: 'created_at') this.createdAt}): _sectionSyntheses = sectionSyntheses,_rowExplanations = rowExplanations,_rowCuratedQuotes = rowCuratedQuotes,_citedSources = citedSources,_xaiHighlights = xaiHighlights,super._();
  factory _ProfileSynthesisEntryDto.fromJson(Map<String, dynamic> json) => _$ProfileSynthesisEntryDtoFromJson(json);

 final  Map<String, ContextVariableEntry> _sectionSyntheses;
@override@JsonKey(name: 'section_syntheses') Map<String, ContextVariableEntry> get sectionSyntheses {
  if (_sectionSyntheses is EqualUnmodifiableMapView) return _sectionSyntheses;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_sectionSyntheses);
}

 final  Map<String, String> _rowExplanations;
@override@JsonKey(name: 'row_explanations') Map<String, String> get rowExplanations {
  if (_rowExplanations is EqualUnmodifiableMapView) return _rowExplanations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_rowExplanations);
}

 final  Map<String, List<String>> _rowCuratedQuotes;
@override@JsonKey(name: 'row_curated_quotes') Map<String, List<String>> get rowCuratedQuotes {
  if (_rowCuratedQuotes is EqualUnmodifiableMapView) return _rowCuratedQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_rowCuratedQuotes);
}

@override@JsonKey(name: 'variance_explanation') final  String? varianceExplanation;
@override@JsonKey(name: 'authenticity_explanation') final  String? authenticityExplanation;
 final  List<String> _citedSources;
@override@JsonKey(name: 'cited_sources') List<String> get citedSources {
  if (_citedSources is EqualUnmodifiableListView) return _citedSources;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citedSources);
}

 final  List<Object?> _xaiHighlights;
@override@JsonKey(name: 'xai_highlights') List<Object?> get xaiHighlights {
  if (_xaiHighlights is EqualUnmodifiableListView) return _xaiHighlights;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_xaiHighlights);
}

@override@JsonKey(name: 'user_role') final  String? userRole;
@override@JsonKey(name: 'user_role_justification') final  String? userRoleJustification;
@override@JsonKey(name: 'extension_metrics') final  Object? extensionMetrics;
@override@JsonKey(name: 'data_starvation') final  Object? dataStarvation;
@override@JsonKey(name: 'created_at') final  String? createdAt;

/// Create a copy of ProfileSynthesisEntryDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProfileSynthesisEntryDtoCopyWith<_ProfileSynthesisEntryDto> get copyWith => __$ProfileSynthesisEntryDtoCopyWithImpl<_ProfileSynthesisEntryDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProfileSynthesisEntryDtoToJson(this, );
}



@override
String toString() {
  return 'ProfileSynthesisEntryDto(sectionSyntheses: $sectionSyntheses, rowExplanations: $rowExplanations, rowCuratedQuotes: $rowCuratedQuotes, varianceExplanation: $varianceExplanation, authenticityExplanation: $authenticityExplanation, citedSources: $citedSources, xaiHighlights: $xaiHighlights, userRole: $userRole, userRoleJustification: $userRoleJustification, extensionMetrics: $extensionMetrics, dataStarvation: $dataStarvation, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$ProfileSynthesisEntryDtoCopyWith<$Res> implements $ProfileSynthesisEntryDtoCopyWith<$Res> {
  factory _$ProfileSynthesisEntryDtoCopyWith(_ProfileSynthesisEntryDto value, $Res Function(_ProfileSynthesisEntryDto) _then) = __$ProfileSynthesisEntryDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'section_syntheses') Map<String, ContextVariableEntry> sectionSyntheses,@JsonKey(name: 'row_explanations') Map<String, String> rowExplanations,@JsonKey(name: 'row_curated_quotes') Map<String, List<String>> rowCuratedQuotes,@JsonKey(name: 'variance_explanation') String? varianceExplanation,@JsonKey(name: 'authenticity_explanation') String? authenticityExplanation,@JsonKey(name: 'cited_sources') List<String> citedSources,@JsonKey(name: 'xai_highlights') List<Object?> xaiHighlights,@JsonKey(name: 'user_role') String? userRole,@JsonKey(name: 'user_role_justification') String? userRoleJustification,@JsonKey(name: 'extension_metrics') Object? extensionMetrics,@JsonKey(name: 'data_starvation') Object? dataStarvation,@JsonKey(name: 'created_at') String? createdAt
});




}
/// @nodoc
class __$ProfileSynthesisEntryDtoCopyWithImpl<$Res>
    implements _$ProfileSynthesisEntryDtoCopyWith<$Res> {
  __$ProfileSynthesisEntryDtoCopyWithImpl(this._self, this._then);

  final _ProfileSynthesisEntryDto _self;
  final $Res Function(_ProfileSynthesisEntryDto) _then;

/// Create a copy of ProfileSynthesisEntryDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sectionSyntheses = null,Object? rowExplanations = null,Object? rowCuratedQuotes = null,Object? varianceExplanation = freezed,Object? authenticityExplanation = freezed,Object? citedSources = null,Object? xaiHighlights = null,Object? userRole = freezed,Object? userRoleJustification = freezed,Object? extensionMetrics = freezed,Object? dataStarvation = freezed,Object? createdAt = freezed,}) {
  return _then(_ProfileSynthesisEntryDto(
sectionSyntheses: null == sectionSyntheses ? _self._sectionSyntheses : sectionSyntheses // ignore: cast_nullable_to_non_nullable
as Map<String, ContextVariableEntry>,rowExplanations: null == rowExplanations ? _self._rowExplanations : rowExplanations // ignore: cast_nullable_to_non_nullable
as Map<String, String>,rowCuratedQuotes: null == rowCuratedQuotes ? _self._rowCuratedQuotes : rowCuratedQuotes // ignore: cast_nullable_to_non_nullable
as Map<String, List<String>>,varianceExplanation: freezed == varianceExplanation ? _self.varianceExplanation : varianceExplanation // ignore: cast_nullable_to_non_nullable
as String?,authenticityExplanation: freezed == authenticityExplanation ? _self.authenticityExplanation : authenticityExplanation // ignore: cast_nullable_to_non_nullable
as String?,citedSources: null == citedSources ? _self._citedSources : citedSources // ignore: cast_nullable_to_non_nullable
as List<String>,xaiHighlights: null == xaiHighlights ? _self._xaiHighlights : xaiHighlights // ignore: cast_nullable_to_non_nullable
as List<Object?>,userRole: freezed == userRole ? _self.userRole : userRole // ignore: cast_nullable_to_non_nullable
as String?,userRoleJustification: freezed == userRoleJustification ? _self.userRoleJustification : userRoleJustification // ignore: cast_nullable_to_non_nullable
as String?,extensionMetrics: freezed == extensionMetrics ? _self.extensionMetrics : extensionMetrics ,dataStarvation: freezed == dataStarvation ? _self.dataStarvation : dataStarvation ,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ExecutionRecord {

 String get id;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(fromJson: _statusFromJson) String get status;@JsonKey(name: 'workflow_version') int get workflowVersion;@JsonKey(name: 'state_version') int get stateVersion;@JsonKey(name: 'active_profile_id') String? get activeProfileId;@JsonKey(name: 'output_profile_id') String? get outputProfileId;@JsonKey(name: 'raw_inputs') WorkflowInputs? get rawInputs;@JsonKey(name: 'duration_ms') int? get durationMs;@JsonKey(name: 'cost_estimate') double? get costEstimate;@JsonKey(name: 'prompt_tokens') int get promptTokens;@JsonKey(name: 'completion_tokens') int get completionTokens;@JsonKey(name: 'cached_tokens') int get cachedTokens;@JsonKey(name: 'reasoning_tokens') int get reasoningTokens;@JsonKey(name: 'dag_cost_usd') double get dagCostUsd;@JsonKey(name: 'cumulative_synthesis_tokens') int? get cumulativeSynthesisTokens;@JsonKey(name: 'cumulative_synthesis_cost') double? get cumulativeSynthesisCost;@JsonKey(name: 'models_used') Map<String, int>? get modelsUsed;@JsonKey(name: 'execution_summary') ExecutionSummarySnapshot? get executionSummary;@JsonKey(name: 'metadata') ExecutionMetadata? get metadata;@JsonKey(name: 'error') String? get error;@JsonKey(name: 'is_resumable') bool? get isResumable;@JsonKey(name: 'frozen_context') FrozenContextSnapshot? get frozenContext;@JsonKey(name: 'frozen_context_storage_path') String? get frozenContextStoragePath;@JsonKey(name: 'context_variables') ContextVariablesDto? get contextVariables;@JsonKey(name: 'context_variables_storage_path') String? get contextVariablesStoragePath;@JsonKey(name: 'execution_trace') List<ExecutionTraceItemDto>? get executionTrace;@JsonKey(name: 'execution_trace_storage_path') String? get executionTraceStoragePath;@JsonKey(name: 'pdf_report_path') String? get pdfReportPath;@JsonKey(name: 'source_identity_manifest') Map<String, String>? get sourceIdentityManifest;@JsonKey(name: 'steps') List<ExecutionStep> get steps;@JsonKey(name: 'step_states') Map<String, ExecutionStep>? get stepStates;@JsonKey(name: 'profile_syntheses') Map<String, ProfileSynthesisEntryDto>? get profileSyntheses;@JsonKey(name: 'progress') int? get progress;@JsonKey(name: 'status_message') String? get statusMessage;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'updated_at') String? get updatedAt;@JsonKey(name: 'completed_at') String? get completedAt;@JsonKey(name: 'created_by') String? get createdBy;@JsonKey(name: 'organization_id') String? get organizationId;
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionRecordCopyWith<ExecutionRecord> get copyWith => _$ExecutionRecordCopyWithImpl<ExecutionRecord>(this as ExecutionRecord, _$identity);

  /// Serializes this ExecutionRecord to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, targetLocale: $targetLocale, status: $status, workflowVersion: $workflowVersion, stateVersion: $stateVersion, activeProfileId: $activeProfileId, outputProfileId: $outputProfileId, rawInputs: $rawInputs, durationMs: $durationMs, costEstimate: $costEstimate, promptTokens: $promptTokens, completionTokens: $completionTokens, cachedTokens: $cachedTokens, reasoningTokens: $reasoningTokens, dagCostUsd: $dagCostUsd, cumulativeSynthesisTokens: $cumulativeSynthesisTokens, cumulativeSynthesisCost: $cumulativeSynthesisCost, modelsUsed: $modelsUsed, executionSummary: $executionSummary, metadata: $metadata, error: $error, isResumable: $isResumable, frozenContext: $frozenContext, frozenContextStoragePath: $frozenContextStoragePath, contextVariables: $contextVariables, contextVariablesStoragePath: $contextVariablesStoragePath, executionTrace: $executionTrace, executionTraceStoragePath: $executionTraceStoragePath, pdfReportPath: $pdfReportPath, sourceIdentityManifest: $sourceIdentityManifest, steps: $steps, stepStates: $stepStates, profileSyntheses: $profileSyntheses, progress: $progress, statusMessage: $statusMessage, createdAt: $createdAt, updatedAt: $updatedAt, completedAt: $completedAt, createdBy: $createdBy, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class $ExecutionRecordCopyWith<$Res>  {
  factory $ExecutionRecordCopyWith(ExecutionRecord value, $Res Function(ExecutionRecord) _then) = _$ExecutionRecordCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'workflow_version') int workflowVersion,@JsonKey(name: 'state_version') int stateVersion,@JsonKey(name: 'active_profile_id') String? activeProfileId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'raw_inputs') WorkflowInputs? rawInputs,@JsonKey(name: 'duration_ms') int? durationMs,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'prompt_tokens') int promptTokens,@JsonKey(name: 'completion_tokens') int completionTokens,@JsonKey(name: 'cached_tokens') int cachedTokens,@JsonKey(name: 'reasoning_tokens') int reasoningTokens,@JsonKey(name: 'dag_cost_usd') double dagCostUsd,@JsonKey(name: 'cumulative_synthesis_tokens') int? cumulativeSynthesisTokens,@JsonKey(name: 'cumulative_synthesis_cost') double? cumulativeSynthesisCost,@JsonKey(name: 'models_used') Map<String, int>? modelsUsed,@JsonKey(name: 'execution_summary') ExecutionSummarySnapshot? executionSummary,@JsonKey(name: 'metadata') ExecutionMetadata? metadata,@JsonKey(name: 'error') String? error,@JsonKey(name: 'is_resumable') bool? isResumable,@JsonKey(name: 'frozen_context') FrozenContextSnapshot? frozenContext,@JsonKey(name: 'frozen_context_storage_path') String? frozenContextStoragePath,@JsonKey(name: 'context_variables') ContextVariablesDto? contextVariables,@JsonKey(name: 'context_variables_storage_path') String? contextVariablesStoragePath,@JsonKey(name: 'execution_trace') List<ExecutionTraceItemDto>? executionTrace,@JsonKey(name: 'execution_trace_storage_path') String? executionTraceStoragePath,@JsonKey(name: 'pdf_report_path') String? pdfReportPath,@JsonKey(name: 'source_identity_manifest') Map<String, String>? sourceIdentityManifest,@JsonKey(name: 'steps') List<ExecutionStep> steps,@JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates,@JsonKey(name: 'profile_syntheses') Map<String, ProfileSynthesisEntryDto>? profileSyntheses,@JsonKey(name: 'progress') int? progress,@JsonKey(name: 'status_message') String? statusMessage,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'updated_at') String? updatedAt,@JsonKey(name: 'completed_at') String? completedAt,@JsonKey(name: 'created_by') String? createdBy,@JsonKey(name: 'organization_id') String? organizationId
});


$WorkflowInputsCopyWith<$Res>? get rawInputs;$ExecutionSummarySnapshotCopyWith<$Res>? get executionSummary;$ExecutionMetadataCopyWith<$Res>? get metadata;$FrozenContextSnapshotCopyWith<$Res>? get frozenContext;$ContextVariablesDtoCopyWith<$Res>? get contextVariables;

}
/// @nodoc
class _$ExecutionRecordCopyWithImpl<$Res>
    implements $ExecutionRecordCopyWith<$Res> {
  _$ExecutionRecordCopyWithImpl(this._self, this._then);

  final ExecutionRecord _self;
  final $Res Function(ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? workflowId = null,Object? targetLocale = null,Object? status = null,Object? workflowVersion = null,Object? stateVersion = null,Object? activeProfileId = freezed,Object? outputProfileId = freezed,Object? rawInputs = freezed,Object? durationMs = freezed,Object? costEstimate = freezed,Object? promptTokens = null,Object? completionTokens = null,Object? cachedTokens = null,Object? reasoningTokens = null,Object? dagCostUsd = null,Object? cumulativeSynthesisTokens = freezed,Object? cumulativeSynthesisCost = freezed,Object? modelsUsed = freezed,Object? executionSummary = freezed,Object? metadata = freezed,Object? error = freezed,Object? isResumable = freezed,Object? frozenContext = freezed,Object? frozenContextStoragePath = freezed,Object? contextVariables = freezed,Object? contextVariablesStoragePath = freezed,Object? executionTrace = freezed,Object? executionTraceStoragePath = freezed,Object? pdfReportPath = freezed,Object? sourceIdentityManifest = freezed,Object? steps = null,Object? stepStates = freezed,Object? profileSyntheses = freezed,Object? progress = freezed,Object? statusMessage = freezed,Object? createdAt = freezed,Object? updatedAt = freezed,Object? completedAt = freezed,Object? createdBy = freezed,Object? organizationId = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,workflowVersion: null == workflowVersion ? _self.workflowVersion : workflowVersion // ignore: cast_nullable_to_non_nullable
as int,stateVersion: null == stateVersion ? _self.stateVersion : stateVersion // ignore: cast_nullable_to_non_nullable
as int,activeProfileId: freezed == activeProfileId ? _self.activeProfileId : activeProfileId // ignore: cast_nullable_to_non_nullable
as String?,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,rawInputs: freezed == rawInputs ? _self.rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs?,durationMs: freezed == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,promptTokens: null == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int,completionTokens: null == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int,cachedTokens: null == cachedTokens ? _self.cachedTokens : cachedTokens // ignore: cast_nullable_to_non_nullable
as int,reasoningTokens: null == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int,dagCostUsd: null == dagCostUsd ? _self.dagCostUsd : dagCostUsd // ignore: cast_nullable_to_non_nullable
as double,cumulativeSynthesisTokens: freezed == cumulativeSynthesisTokens ? _self.cumulativeSynthesisTokens : cumulativeSynthesisTokens // ignore: cast_nullable_to_non_nullable
as int?,cumulativeSynthesisCost: freezed == cumulativeSynthesisCost ? _self.cumulativeSynthesisCost : cumulativeSynthesisCost // ignore: cast_nullable_to_non_nullable
as double?,modelsUsed: freezed == modelsUsed ? _self.modelsUsed : modelsUsed // ignore: cast_nullable_to_non_nullable
as Map<String, int>?,executionSummary: freezed == executionSummary ? _self.executionSummary : executionSummary // ignore: cast_nullable_to_non_nullable
as ExecutionSummarySnapshot?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as ExecutionMetadata?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isResumable: freezed == isResumable ? _self.isResumable : isResumable // ignore: cast_nullable_to_non_nullable
as bool?,frozenContext: freezed == frozenContext ? _self.frozenContext : frozenContext // ignore: cast_nullable_to_non_nullable
as FrozenContextSnapshot?,frozenContextStoragePath: freezed == frozenContextStoragePath ? _self.frozenContextStoragePath : frozenContextStoragePath // ignore: cast_nullable_to_non_nullable
as String?,contextVariables: freezed == contextVariables ? _self.contextVariables : contextVariables // ignore: cast_nullable_to_non_nullable
as ContextVariablesDto?,contextVariablesStoragePath: freezed == contextVariablesStoragePath ? _self.contextVariablesStoragePath : contextVariablesStoragePath // ignore: cast_nullable_to_non_nullable
as String?,executionTrace: freezed == executionTrace ? _self.executionTrace : executionTrace // ignore: cast_nullable_to_non_nullable
as List<ExecutionTraceItemDto>?,executionTraceStoragePath: freezed == executionTraceStoragePath ? _self.executionTraceStoragePath : executionTraceStoragePath // ignore: cast_nullable_to_non_nullable
as String?,pdfReportPath: freezed == pdfReportPath ? _self.pdfReportPath : pdfReportPath // ignore: cast_nullable_to_non_nullable
as String?,sourceIdentityManifest: freezed == sourceIdentityManifest ? _self.sourceIdentityManifest : sourceIdentityManifest // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<ExecutionStep>,stepStates: freezed == stepStates ? _self.stepStates : stepStates // ignore: cast_nullable_to_non_nullable
as Map<String, ExecutionStep>?,profileSyntheses: freezed == profileSyntheses ? _self.profileSyntheses : profileSyntheses // ignore: cast_nullable_to_non_nullable
as Map<String, ProfileSynthesisEntryDto>?,progress: freezed == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int?,statusMessage: freezed == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: freezed == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res>? get rawInputs {
    if (_self.rawInputs == null) {
    return null;
  }

  return $WorkflowInputsCopyWith<$Res>(_self.rawInputs!, (value) {
    return _then(_self.copyWith(rawInputs: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionSummarySnapshotCopyWith<$Res>? get executionSummary {
    if (_self.executionSummary == null) {
    return null;
  }

  return $ExecutionSummarySnapshotCopyWith<$Res>(_self.executionSummary!, (value) {
    return _then(_self.copyWith(executionSummary: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetadataCopyWith<$Res>? get metadata {
    if (_self.metadata == null) {
    return null;
  }

  return $ExecutionMetadataCopyWith<$Res>(_self.metadata!, (value) {
    return _then(_self.copyWith(metadata: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$FrozenContextSnapshotCopyWith<$Res>? get frozenContext {
    if (_self.frozenContext == null) {
    return null;
  }

  return $FrozenContextSnapshotCopyWith<$Res>(_self.frozenContext!, (value) {
    return _then(_self.copyWith(frozenContext: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ContextVariablesDtoCopyWith<$Res>? get contextVariables {
    if (_self.contextVariables == null) {
    return null;
  }

  return $ContextVariablesDtoCopyWith<$Res>(_self.contextVariables!, (value) {
    return _then(_self.copyWith(contextVariables: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExecutionRecord].
extension ExecutionRecordPatterns on ExecutionRecord {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionRecord value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionRecord value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionRecord():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionRecord value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'state_version')  int stateVersion, @JsonKey(name: 'active_profile_id')  String? activeProfileId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'raw_inputs')  WorkflowInputs? rawInputs, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'prompt_tokens')  int promptTokens, @JsonKey(name: 'completion_tokens')  int completionTokens, @JsonKey(name: 'cached_tokens')  int cachedTokens, @JsonKey(name: 'reasoning_tokens')  int reasoningTokens, @JsonKey(name: 'dag_cost_usd')  double dagCostUsd, @JsonKey(name: 'cumulative_synthesis_tokens')  int? cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost')  double? cumulativeSynthesisCost, @JsonKey(name: 'models_used')  Map<String, int>? modelsUsed, @JsonKey(name: 'execution_summary')  ExecutionSummarySnapshot? executionSummary, @JsonKey(name: 'metadata')  ExecutionMetadata? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  FrozenContextSnapshot? frozenContext, @JsonKey(name: 'frozen_context_storage_path')  String? frozenContextStoragePath, @JsonKey(name: 'context_variables')  ContextVariablesDto? contextVariables, @JsonKey(name: 'context_variables_storage_path')  String? contextVariablesStoragePath, @JsonKey(name: 'execution_trace')  List<ExecutionTraceItemDto>? executionTrace, @JsonKey(name: 'execution_trace_storage_path')  String? executionTraceStoragePath, @JsonKey(name: 'pdf_report_path')  String? pdfReportPath, @JsonKey(name: 'source_identity_manifest')  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'steps')  List<ExecutionStep> steps, @JsonKey(name: 'step_states')  Map<String, ExecutionStep>? stepStates, @JsonKey(name: 'profile_syntheses')  Map<String, ProfileSynthesisEntryDto>? profileSyntheses, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'organization_id')  String? organizationId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.targetLocale,_that.status,_that.workflowVersion,_that.stateVersion,_that.activeProfileId,_that.outputProfileId,_that.rawInputs,_that.durationMs,_that.costEstimate,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens,_that.dagCostUsd,_that.cumulativeSynthesisTokens,_that.cumulativeSynthesisCost,_that.modelsUsed,_that.executionSummary,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.frozenContextStoragePath,_that.contextVariables,_that.contextVariablesStoragePath,_that.executionTrace,_that.executionTraceStoragePath,_that.pdfReportPath,_that.sourceIdentityManifest,_that.steps,_that.stepStates,_that.profileSyntheses,_that.progress,_that.statusMessage,_that.createdAt,_that.updatedAt,_that.completedAt,_that.createdBy,_that.organizationId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'state_version')  int stateVersion, @JsonKey(name: 'active_profile_id')  String? activeProfileId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'raw_inputs')  WorkflowInputs? rawInputs, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'prompt_tokens')  int promptTokens, @JsonKey(name: 'completion_tokens')  int completionTokens, @JsonKey(name: 'cached_tokens')  int cachedTokens, @JsonKey(name: 'reasoning_tokens')  int reasoningTokens, @JsonKey(name: 'dag_cost_usd')  double dagCostUsd, @JsonKey(name: 'cumulative_synthesis_tokens')  int? cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost')  double? cumulativeSynthesisCost, @JsonKey(name: 'models_used')  Map<String, int>? modelsUsed, @JsonKey(name: 'execution_summary')  ExecutionSummarySnapshot? executionSummary, @JsonKey(name: 'metadata')  ExecutionMetadata? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  FrozenContextSnapshot? frozenContext, @JsonKey(name: 'frozen_context_storage_path')  String? frozenContextStoragePath, @JsonKey(name: 'context_variables')  ContextVariablesDto? contextVariables, @JsonKey(name: 'context_variables_storage_path')  String? contextVariablesStoragePath, @JsonKey(name: 'execution_trace')  List<ExecutionTraceItemDto>? executionTrace, @JsonKey(name: 'execution_trace_storage_path')  String? executionTraceStoragePath, @JsonKey(name: 'pdf_report_path')  String? pdfReportPath, @JsonKey(name: 'source_identity_manifest')  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'steps')  List<ExecutionStep> steps, @JsonKey(name: 'step_states')  Map<String, ExecutionStep>? stepStates, @JsonKey(name: 'profile_syntheses')  Map<String, ProfileSynthesisEntryDto>? profileSyntheses, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'organization_id')  String? organizationId)  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord():
return $default(_that.id,_that.workflowId,_that.targetLocale,_that.status,_that.workflowVersion,_that.stateVersion,_that.activeProfileId,_that.outputProfileId,_that.rawInputs,_that.durationMs,_that.costEstimate,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens,_that.dagCostUsd,_that.cumulativeSynthesisTokens,_that.cumulativeSynthesisCost,_that.modelsUsed,_that.executionSummary,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.frozenContextStoragePath,_that.contextVariables,_that.contextVariablesStoragePath,_that.executionTrace,_that.executionTraceStoragePath,_that.pdfReportPath,_that.sourceIdentityManifest,_that.steps,_that.stepStates,_that.profileSyntheses,_that.progress,_that.statusMessage,_that.createdAt,_that.updatedAt,_that.completedAt,_that.createdBy,_that.organizationId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'workflow_version')  int workflowVersion, @JsonKey(name: 'state_version')  int stateVersion, @JsonKey(name: 'active_profile_id')  String? activeProfileId, @JsonKey(name: 'output_profile_id')  String? outputProfileId, @JsonKey(name: 'raw_inputs')  WorkflowInputs? rawInputs, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'prompt_tokens')  int promptTokens, @JsonKey(name: 'completion_tokens')  int completionTokens, @JsonKey(name: 'cached_tokens')  int cachedTokens, @JsonKey(name: 'reasoning_tokens')  int reasoningTokens, @JsonKey(name: 'dag_cost_usd')  double dagCostUsd, @JsonKey(name: 'cumulative_synthesis_tokens')  int? cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost')  double? cumulativeSynthesisCost, @JsonKey(name: 'models_used')  Map<String, int>? modelsUsed, @JsonKey(name: 'execution_summary')  ExecutionSummarySnapshot? executionSummary, @JsonKey(name: 'metadata')  ExecutionMetadata? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  FrozenContextSnapshot? frozenContext, @JsonKey(name: 'frozen_context_storage_path')  String? frozenContextStoragePath, @JsonKey(name: 'context_variables')  ContextVariablesDto? contextVariables, @JsonKey(name: 'context_variables_storage_path')  String? contextVariablesStoragePath, @JsonKey(name: 'execution_trace')  List<ExecutionTraceItemDto>? executionTrace, @JsonKey(name: 'execution_trace_storage_path')  String? executionTraceStoragePath, @JsonKey(name: 'pdf_report_path')  String? pdfReportPath, @JsonKey(name: 'source_identity_manifest')  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'steps')  List<ExecutionStep> steps, @JsonKey(name: 'step_states')  Map<String, ExecutionStep>? stepStates, @JsonKey(name: 'profile_syntheses')  Map<String, ProfileSynthesisEntryDto>? profileSyntheses, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'updated_at')  String? updatedAt, @JsonKey(name: 'completed_at')  String? completedAt, @JsonKey(name: 'created_by')  String? createdBy, @JsonKey(name: 'organization_id')  String? organizationId)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.targetLocale,_that.status,_that.workflowVersion,_that.stateVersion,_that.activeProfileId,_that.outputProfileId,_that.rawInputs,_that.durationMs,_that.costEstimate,_that.promptTokens,_that.completionTokens,_that.cachedTokens,_that.reasoningTokens,_that.dagCostUsd,_that.cumulativeSynthesisTokens,_that.cumulativeSynthesisCost,_that.modelsUsed,_that.executionSummary,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.frozenContextStoragePath,_that.contextVariables,_that.contextVariablesStoragePath,_that.executionTrace,_that.executionTraceStoragePath,_that.pdfReportPath,_that.sourceIdentityManifest,_that.steps,_that.stepStates,_that.profileSyntheses,_that.progress,_that.statusMessage,_that.createdAt,_that.updatedAt,_that.completedAt,_that.createdBy,_that.organizationId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _ExecutionRecord extends ExecutionRecord {
  const _ExecutionRecord({required this.id, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'target_locale') required this.targetLocale, @JsonKey(fromJson: _statusFromJson) required this.status, @JsonKey(name: 'workflow_version') this.workflowVersion = 1, @JsonKey(name: 'state_version') this.stateVersion = 1, @JsonKey(name: 'active_profile_id') this.activeProfileId, @JsonKey(name: 'output_profile_id') this.outputProfileId, @JsonKey(name: 'raw_inputs') this.rawInputs, @JsonKey(name: 'duration_ms') this.durationMs, @JsonKey(name: 'cost_estimate') this.costEstimate, @JsonKey(name: 'prompt_tokens') this.promptTokens = 0, @JsonKey(name: 'completion_tokens') this.completionTokens = 0, @JsonKey(name: 'cached_tokens') this.cachedTokens = 0, @JsonKey(name: 'reasoning_tokens') this.reasoningTokens = 0, @JsonKey(name: 'dag_cost_usd') this.dagCostUsd = 0.0, @JsonKey(name: 'cumulative_synthesis_tokens') this.cumulativeSynthesisTokens, @JsonKey(name: 'cumulative_synthesis_cost') this.cumulativeSynthesisCost, @JsonKey(name: 'models_used') final  Map<String, int>? modelsUsed, @JsonKey(name: 'execution_summary') this.executionSummary, @JsonKey(name: 'metadata') this.metadata, @JsonKey(name: 'error') this.error, @JsonKey(name: 'is_resumable') this.isResumable, @JsonKey(name: 'frozen_context') this.frozenContext, @JsonKey(name: 'frozen_context_storage_path') this.frozenContextStoragePath, @JsonKey(name: 'context_variables') this.contextVariables, @JsonKey(name: 'context_variables_storage_path') this.contextVariablesStoragePath, @JsonKey(name: 'execution_trace') final  List<ExecutionTraceItemDto>? executionTrace, @JsonKey(name: 'execution_trace_storage_path') this.executionTraceStoragePath, @JsonKey(name: 'pdf_report_path') this.pdfReportPath, @JsonKey(name: 'source_identity_manifest') final  Map<String, String>? sourceIdentityManifest, @JsonKey(name: 'steps') final  List<ExecutionStep> steps = const [], @JsonKey(name: 'step_states') final  Map<String, ExecutionStep>? stepStates, @JsonKey(name: 'profile_syntheses') final  Map<String, ProfileSynthesisEntryDto>? profileSyntheses, @JsonKey(name: 'progress') this.progress, @JsonKey(name: 'status_message') this.statusMessage, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'updated_at') this.updatedAt, @JsonKey(name: 'completed_at') this.completedAt, @JsonKey(name: 'created_by') this.createdBy, @JsonKey(name: 'organization_id') this.organizationId}): _modelsUsed = modelsUsed,_executionTrace = executionTrace,_sourceIdentityManifest = sourceIdentityManifest,_steps = steps,_stepStates = stepStates,_profileSyntheses = profileSyntheses,super._();
  factory _ExecutionRecord.fromJson(Map<String, dynamic> json) => _$ExecutionRecordFromJson(json);

@override final  String id;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(fromJson: _statusFromJson) final  String status;
@override@JsonKey(name: 'workflow_version') final  int workflowVersion;
@override@JsonKey(name: 'state_version') final  int stateVersion;
@override@JsonKey(name: 'active_profile_id') final  String? activeProfileId;
@override@JsonKey(name: 'output_profile_id') final  String? outputProfileId;
@override@JsonKey(name: 'raw_inputs') final  WorkflowInputs? rawInputs;
@override@JsonKey(name: 'duration_ms') final  int? durationMs;
@override@JsonKey(name: 'cost_estimate') final  double? costEstimate;
@override@JsonKey(name: 'prompt_tokens') final  int promptTokens;
@override@JsonKey(name: 'completion_tokens') final  int completionTokens;
@override@JsonKey(name: 'cached_tokens') final  int cachedTokens;
@override@JsonKey(name: 'reasoning_tokens') final  int reasoningTokens;
@override@JsonKey(name: 'dag_cost_usd') final  double dagCostUsd;
@override@JsonKey(name: 'cumulative_synthesis_tokens') final  int? cumulativeSynthesisTokens;
@override@JsonKey(name: 'cumulative_synthesis_cost') final  double? cumulativeSynthesisCost;
 final  Map<String, int>? _modelsUsed;
@override@JsonKey(name: 'models_used') Map<String, int>? get modelsUsed {
  final value = _modelsUsed;
  if (value == null) return null;
  if (_modelsUsed is EqualUnmodifiableMapView) return _modelsUsed;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'execution_summary') final  ExecutionSummarySnapshot? executionSummary;
@override@JsonKey(name: 'metadata') final  ExecutionMetadata? metadata;
@override@JsonKey(name: 'error') final  String? error;
@override@JsonKey(name: 'is_resumable') final  bool? isResumable;
@override@JsonKey(name: 'frozen_context') final  FrozenContextSnapshot? frozenContext;
@override@JsonKey(name: 'frozen_context_storage_path') final  String? frozenContextStoragePath;
@override@JsonKey(name: 'context_variables') final  ContextVariablesDto? contextVariables;
@override@JsonKey(name: 'context_variables_storage_path') final  String? contextVariablesStoragePath;
 final  List<ExecutionTraceItemDto>? _executionTrace;
@override@JsonKey(name: 'execution_trace') List<ExecutionTraceItemDto>? get executionTrace {
  final value = _executionTrace;
  if (value == null) return null;
  if (_executionTrace is EqualUnmodifiableListView) return _executionTrace;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey(name: 'execution_trace_storage_path') final  String? executionTraceStoragePath;
@override@JsonKey(name: 'pdf_report_path') final  String? pdfReportPath;
 final  Map<String, String>? _sourceIdentityManifest;
@override@JsonKey(name: 'source_identity_manifest') Map<String, String>? get sourceIdentityManifest {
  final value = _sourceIdentityManifest;
  if (value == null) return null;
  if (_sourceIdentityManifest is EqualUnmodifiableMapView) return _sourceIdentityManifest;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  List<ExecutionStep> _steps;
@override@JsonKey(name: 'steps') List<ExecutionStep> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}

 final  Map<String, ExecutionStep>? _stepStates;
@override@JsonKey(name: 'step_states') Map<String, ExecutionStep>? get stepStates {
  final value = _stepStates;
  if (value == null) return null;
  if (_stepStates is EqualUnmodifiableMapView) return _stepStates;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, ProfileSynthesisEntryDto>? _profileSyntheses;
@override@JsonKey(name: 'profile_syntheses') Map<String, ProfileSynthesisEntryDto>? get profileSyntheses {
  final value = _profileSyntheses;
  if (value == null) return null;
  if (_profileSyntheses is EqualUnmodifiableMapView) return _profileSyntheses;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'progress') final  int? progress;
@override@JsonKey(name: 'status_message') final  String? statusMessage;
@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'updated_at') final  String? updatedAt;
@override@JsonKey(name: 'completed_at') final  String? completedAt;
@override@JsonKey(name: 'created_by') final  String? createdBy;
@override@JsonKey(name: 'organization_id') final  String? organizationId;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionRecordCopyWith<_ExecutionRecord> get copyWith => __$ExecutionRecordCopyWithImpl<_ExecutionRecord>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionRecordToJson(this, );
}



@override
String toString() {
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, targetLocale: $targetLocale, status: $status, workflowVersion: $workflowVersion, stateVersion: $stateVersion, activeProfileId: $activeProfileId, outputProfileId: $outputProfileId, rawInputs: $rawInputs, durationMs: $durationMs, costEstimate: $costEstimate, promptTokens: $promptTokens, completionTokens: $completionTokens, cachedTokens: $cachedTokens, reasoningTokens: $reasoningTokens, dagCostUsd: $dagCostUsd, cumulativeSynthesisTokens: $cumulativeSynthesisTokens, cumulativeSynthesisCost: $cumulativeSynthesisCost, modelsUsed: $modelsUsed, executionSummary: $executionSummary, metadata: $metadata, error: $error, isResumable: $isResumable, frozenContext: $frozenContext, frozenContextStoragePath: $frozenContextStoragePath, contextVariables: $contextVariables, contextVariablesStoragePath: $contextVariablesStoragePath, executionTrace: $executionTrace, executionTraceStoragePath: $executionTraceStoragePath, pdfReportPath: $pdfReportPath, sourceIdentityManifest: $sourceIdentityManifest, steps: $steps, stepStates: $stepStates, profileSyntheses: $profileSyntheses, progress: $progress, statusMessage: $statusMessage, createdAt: $createdAt, updatedAt: $updatedAt, completedAt: $completedAt, createdBy: $createdBy, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class _$ExecutionRecordCopyWith<$Res> implements $ExecutionRecordCopyWith<$Res> {
  factory _$ExecutionRecordCopyWith(_ExecutionRecord value, $Res Function(_ExecutionRecord) _then) = __$ExecutionRecordCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'workflow_version') int workflowVersion,@JsonKey(name: 'state_version') int stateVersion,@JsonKey(name: 'active_profile_id') String? activeProfileId,@JsonKey(name: 'output_profile_id') String? outputProfileId,@JsonKey(name: 'raw_inputs') WorkflowInputs? rawInputs,@JsonKey(name: 'duration_ms') int? durationMs,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'prompt_tokens') int promptTokens,@JsonKey(name: 'completion_tokens') int completionTokens,@JsonKey(name: 'cached_tokens') int cachedTokens,@JsonKey(name: 'reasoning_tokens') int reasoningTokens,@JsonKey(name: 'dag_cost_usd') double dagCostUsd,@JsonKey(name: 'cumulative_synthesis_tokens') int? cumulativeSynthesisTokens,@JsonKey(name: 'cumulative_synthesis_cost') double? cumulativeSynthesisCost,@JsonKey(name: 'models_used') Map<String, int>? modelsUsed,@JsonKey(name: 'execution_summary') ExecutionSummarySnapshot? executionSummary,@JsonKey(name: 'metadata') ExecutionMetadata? metadata,@JsonKey(name: 'error') String? error,@JsonKey(name: 'is_resumable') bool? isResumable,@JsonKey(name: 'frozen_context') FrozenContextSnapshot? frozenContext,@JsonKey(name: 'frozen_context_storage_path') String? frozenContextStoragePath,@JsonKey(name: 'context_variables') ContextVariablesDto? contextVariables,@JsonKey(name: 'context_variables_storage_path') String? contextVariablesStoragePath,@JsonKey(name: 'execution_trace') List<ExecutionTraceItemDto>? executionTrace,@JsonKey(name: 'execution_trace_storage_path') String? executionTraceStoragePath,@JsonKey(name: 'pdf_report_path') String? pdfReportPath,@JsonKey(name: 'source_identity_manifest') Map<String, String>? sourceIdentityManifest,@JsonKey(name: 'steps') List<ExecutionStep> steps,@JsonKey(name: 'step_states') Map<String, ExecutionStep>? stepStates,@JsonKey(name: 'profile_syntheses') Map<String, ProfileSynthesisEntryDto>? profileSyntheses,@JsonKey(name: 'progress') int? progress,@JsonKey(name: 'status_message') String? statusMessage,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'updated_at') String? updatedAt,@JsonKey(name: 'completed_at') String? completedAt,@JsonKey(name: 'created_by') String? createdBy,@JsonKey(name: 'organization_id') String? organizationId
});


@override $WorkflowInputsCopyWith<$Res>? get rawInputs;@override $ExecutionSummarySnapshotCopyWith<$Res>? get executionSummary;@override $ExecutionMetadataCopyWith<$Res>? get metadata;@override $FrozenContextSnapshotCopyWith<$Res>? get frozenContext;@override $ContextVariablesDtoCopyWith<$Res>? get contextVariables;

}
/// @nodoc
class __$ExecutionRecordCopyWithImpl<$Res>
    implements _$ExecutionRecordCopyWith<$Res> {
  __$ExecutionRecordCopyWithImpl(this._self, this._then);

  final _ExecutionRecord _self;
  final $Res Function(_ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? workflowId = null,Object? targetLocale = null,Object? status = null,Object? workflowVersion = null,Object? stateVersion = null,Object? activeProfileId = freezed,Object? outputProfileId = freezed,Object? rawInputs = freezed,Object? durationMs = freezed,Object? costEstimate = freezed,Object? promptTokens = null,Object? completionTokens = null,Object? cachedTokens = null,Object? reasoningTokens = null,Object? dagCostUsd = null,Object? cumulativeSynthesisTokens = freezed,Object? cumulativeSynthesisCost = freezed,Object? modelsUsed = freezed,Object? executionSummary = freezed,Object? metadata = freezed,Object? error = freezed,Object? isResumable = freezed,Object? frozenContext = freezed,Object? frozenContextStoragePath = freezed,Object? contextVariables = freezed,Object? contextVariablesStoragePath = freezed,Object? executionTrace = freezed,Object? executionTraceStoragePath = freezed,Object? pdfReportPath = freezed,Object? sourceIdentityManifest = freezed,Object? steps = null,Object? stepStates = freezed,Object? profileSyntheses = freezed,Object? progress = freezed,Object? statusMessage = freezed,Object? createdAt = freezed,Object? updatedAt = freezed,Object? completedAt = freezed,Object? createdBy = freezed,Object? organizationId = freezed,}) {
  return _then(_ExecutionRecord(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,workflowVersion: null == workflowVersion ? _self.workflowVersion : workflowVersion // ignore: cast_nullable_to_non_nullable
as int,stateVersion: null == stateVersion ? _self.stateVersion : stateVersion // ignore: cast_nullable_to_non_nullable
as int,activeProfileId: freezed == activeProfileId ? _self.activeProfileId : activeProfileId // ignore: cast_nullable_to_non_nullable
as String?,outputProfileId: freezed == outputProfileId ? _self.outputProfileId : outputProfileId // ignore: cast_nullable_to_non_nullable
as String?,rawInputs: freezed == rawInputs ? _self.rawInputs : rawInputs // ignore: cast_nullable_to_non_nullable
as WorkflowInputs?,durationMs: freezed == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,promptTokens: null == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int,completionTokens: null == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int,cachedTokens: null == cachedTokens ? _self.cachedTokens : cachedTokens // ignore: cast_nullable_to_non_nullable
as int,reasoningTokens: null == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int,dagCostUsd: null == dagCostUsd ? _self.dagCostUsd : dagCostUsd // ignore: cast_nullable_to_non_nullable
as double,cumulativeSynthesisTokens: freezed == cumulativeSynthesisTokens ? _self.cumulativeSynthesisTokens : cumulativeSynthesisTokens // ignore: cast_nullable_to_non_nullable
as int?,cumulativeSynthesisCost: freezed == cumulativeSynthesisCost ? _self.cumulativeSynthesisCost : cumulativeSynthesisCost // ignore: cast_nullable_to_non_nullable
as double?,modelsUsed: freezed == modelsUsed ? _self._modelsUsed : modelsUsed // ignore: cast_nullable_to_non_nullable
as Map<String, int>?,executionSummary: freezed == executionSummary ? _self.executionSummary : executionSummary // ignore: cast_nullable_to_non_nullable
as ExecutionSummarySnapshot?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as ExecutionMetadata?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isResumable: freezed == isResumable ? _self.isResumable : isResumable // ignore: cast_nullable_to_non_nullable
as bool?,frozenContext: freezed == frozenContext ? _self.frozenContext : frozenContext // ignore: cast_nullable_to_non_nullable
as FrozenContextSnapshot?,frozenContextStoragePath: freezed == frozenContextStoragePath ? _self.frozenContextStoragePath : frozenContextStoragePath // ignore: cast_nullable_to_non_nullable
as String?,contextVariables: freezed == contextVariables ? _self.contextVariables : contextVariables // ignore: cast_nullable_to_non_nullable
as ContextVariablesDto?,contextVariablesStoragePath: freezed == contextVariablesStoragePath ? _self.contextVariablesStoragePath : contextVariablesStoragePath // ignore: cast_nullable_to_non_nullable
as String?,executionTrace: freezed == executionTrace ? _self._executionTrace : executionTrace // ignore: cast_nullable_to_non_nullable
as List<ExecutionTraceItemDto>?,executionTraceStoragePath: freezed == executionTraceStoragePath ? _self.executionTraceStoragePath : executionTraceStoragePath // ignore: cast_nullable_to_non_nullable
as String?,pdfReportPath: freezed == pdfReportPath ? _self.pdfReportPath : pdfReportPath // ignore: cast_nullable_to_non_nullable
as String?,sourceIdentityManifest: freezed == sourceIdentityManifest ? _self._sourceIdentityManifest : sourceIdentityManifest // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<ExecutionStep>,stepStates: freezed == stepStates ? _self._stepStates : stepStates // ignore: cast_nullable_to_non_nullable
as Map<String, ExecutionStep>?,profileSyntheses: freezed == profileSyntheses ? _self._profileSyntheses : profileSyntheses // ignore: cast_nullable_to_non_nullable
as Map<String, ProfileSynthesisEntryDto>?,progress: freezed == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int?,statusMessage: freezed == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: freezed == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<$Res>? get rawInputs {
    if (_self.rawInputs == null) {
    return null;
  }

  return $WorkflowInputsCopyWith<$Res>(_self.rawInputs!, (value) {
    return _then(_self.copyWith(rawInputs: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionSummarySnapshotCopyWith<$Res>? get executionSummary {
    if (_self.executionSummary == null) {
    return null;
  }

  return $ExecutionSummarySnapshotCopyWith<$Res>(_self.executionSummary!, (value) {
    return _then(_self.copyWith(executionSummary: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetadataCopyWith<$Res>? get metadata {
    if (_self.metadata == null) {
    return null;
  }

  return $ExecutionMetadataCopyWith<$Res>(_self.metadata!, (value) {
    return _then(_self.copyWith(metadata: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$FrozenContextSnapshotCopyWith<$Res>? get frozenContext {
    if (_self.frozenContext == null) {
    return null;
  }

  return $FrozenContextSnapshotCopyWith<$Res>(_self.frozenContext!, (value) {
    return _then(_self.copyWith(frozenContext: value));
  });
}/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ContextVariablesDtoCopyWith<$Res>? get contextVariables {
    if (_self.contextVariables == null) {
    return null;
  }

  return $ContextVariablesDtoCopyWith<$Res>(_self.contextVariables!, (value) {
    return _then(_self.copyWith(contextVariables: value));
  });
}
}

// dart format on
