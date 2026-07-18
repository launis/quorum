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
mixin _$ExecutionRecord {

 String get id;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(fromJson: _statusFromJson) String get status;@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? get traceVersion;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'cost_estimate') double? get costEstimate;@JsonKey(name: 'metadata') Map<String, dynamic>? get metadata;@JsonKey(name: 'error') String? get error;@JsonKey(name: 'is_resumable') bool? get isResumable;@JsonKey(name: 'frozen_context') Map<String, dynamic>? get frozenContext;@JsonKey(name: 'step_states') Map<String, dynamic>? get stepStates;@JsonKey(name: 'results') Map<String, dynamic>? get results;@JsonKey(name: 'progress') int? get progress;@JsonKey(name: 'status_message') String? get statusMessage;/// The strictly typed DTO containing the presentation flat data.
/// Replaces the legacy `results` Map.
@JsonKey(name: 'report_data') ReportDataDto? get reportData;
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionRecordCopyWith<ExecutionRecord> get copyWith => _$ExecutionRecordCopyWithImpl<ExecutionRecord>(this as ExecutionRecord, _$identity);

  /// Serializes this ExecutionRecord to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, status: $status, traceVersion: $traceVersion, strictnessLevel: $strictnessLevel, createdAt: $createdAt, costEstimate: $costEstimate, metadata: $metadata, error: $error, isResumable: $isResumable, frozenContext: $frozenContext, stepStates: $stepStates, results: $results, progress: $progress, statusMessage: $statusMessage, reportData: $reportData)';
}


}

/// @nodoc
abstract mixin class $ExecutionRecordCopyWith<$Res>  {
  factory $ExecutionRecordCopyWith(ExecutionRecord value, $Res Function(ExecutionRecord) _then) = _$ExecutionRecordCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? traceVersion,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'metadata') Map<String, dynamic>? metadata,@JsonKey(name: 'error') String? error,@JsonKey(name: 'is_resumable') bool? isResumable,@JsonKey(name: 'frozen_context') Map<String, dynamic>? frozenContext,@JsonKey(name: 'step_states') Map<String, dynamic>? stepStates,@JsonKey(name: 'results') Map<String, dynamic>? results,@JsonKey(name: 'progress') int? progress,@JsonKey(name: 'status_message') String? statusMessage,@JsonKey(name: 'report_data') ReportDataDto? reportData
});


$ReportDataDtoCopyWith<$Res>? get reportData;

}
/// @nodoc
class _$ExecutionRecordCopyWithImpl<$Res>
    implements $ExecutionRecordCopyWith<$Res> {
  _$ExecutionRecordCopyWithImpl(this._self, this._then);

  final ExecutionRecord _self;
  final $Res Function(ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? workflowId = null,Object? status = null,Object? traceVersion = freezed,Object? strictnessLevel = freezed,Object? createdAt = freezed,Object? costEstimate = freezed,Object? metadata = freezed,Object? error = freezed,Object? isResumable = freezed,Object? frozenContext = freezed,Object? stepStates = freezed,Object? results = freezed,Object? progress = freezed,Object? statusMessage = freezed,Object? reportData = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,traceVersion: freezed == traceVersion ? _self.traceVersion : traceVersion // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isResumable: freezed == isResumable ? _self.isResumable : isResumable // ignore: cast_nullable_to_non_nullable
as bool?,frozenContext: freezed == frozenContext ? _self.frozenContext : frozenContext // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepStates: freezed == stepStates ? _self.stepStates : stepStates // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,results: freezed == results ? _self.results : results // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,progress: freezed == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int?,statusMessage: freezed == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String?,reportData: freezed == reportData ? _self.reportData : reportData // ignore: cast_nullable_to_non_nullable
as ReportDataDto?,
  ));
}
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportDataDtoCopyWith<$Res>? get reportData {
    if (_self.reportData == null) {
    return null;
  }

  return $ReportDataDtoCopyWith<$Res>(_self.reportData!, (value) {
    return _then(_self.copyWith(reportData: value));
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'metadata')  Map<String, dynamic>? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  Map<String, dynamic>? frozenContext, @JsonKey(name: 'step_states')  Map<String, dynamic>? stepStates, @JsonKey(name: 'results')  Map<String, dynamic>? results, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'report_data')  ReportDataDto? reportData)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.status,_that.traceVersion,_that.strictnessLevel,_that.createdAt,_that.costEstimate,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.stepStates,_that.results,_that.progress,_that.statusMessage,_that.reportData);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'metadata')  Map<String, dynamic>? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  Map<String, dynamic>? frozenContext, @JsonKey(name: 'step_states')  Map<String, dynamic>? stepStates, @JsonKey(name: 'results')  Map<String, dynamic>? results, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'report_data')  ReportDataDto? reportData)  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord():
return $default(_that.id,_that.workflowId,_that.status,_that.traceVersion,_that.strictnessLevel,_that.createdAt,_that.costEstimate,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.stepStates,_that.results,_that.progress,_that.statusMessage,_that.reportData);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'metadata')  Map<String, dynamic>? metadata, @JsonKey(name: 'error')  String? error, @JsonKey(name: 'is_resumable')  bool? isResumable, @JsonKey(name: 'frozen_context')  Map<String, dynamic>? frozenContext, @JsonKey(name: 'step_states')  Map<String, dynamic>? stepStates, @JsonKey(name: 'results')  Map<String, dynamic>? results, @JsonKey(name: 'progress')  int? progress, @JsonKey(name: 'status_message')  String? statusMessage, @JsonKey(name: 'report_data')  ReportDataDto? reportData)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.status,_that.traceVersion,_that.strictnessLevel,_that.createdAt,_that.costEstimate,_that.metadata,_that.error,_that.isResumable,_that.frozenContext,_that.stepStates,_that.results,_that.progress,_that.statusMessage,_that.reportData);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionRecord extends ExecutionRecord {
  const _ExecutionRecord({required this.id, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(fromJson: _statusFromJson) required this.status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) this.traceVersion, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'cost_estimate') this.costEstimate, @JsonKey(name: 'metadata') final  Map<String, dynamic>? metadata, @JsonKey(name: 'error') this.error, @JsonKey(name: 'is_resumable') this.isResumable, @JsonKey(name: 'frozen_context') final  Map<String, dynamic>? frozenContext, @JsonKey(name: 'step_states') final  Map<String, dynamic>? stepStates, @JsonKey(name: 'results') final  Map<String, dynamic>? results, @JsonKey(name: 'progress') this.progress, @JsonKey(name: 'status_message') this.statusMessage, @JsonKey(name: 'report_data') this.reportData}): _metadata = metadata,_frozenContext = frozenContext,_stepStates = stepStates,_results = results,super._();
  factory _ExecutionRecord.fromJson(Map<String, dynamic> json) => _$ExecutionRecordFromJson(json);

@override final  String id;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(fromJson: _statusFromJson) final  String status;
@override@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) final  String? traceVersion;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'cost_estimate') final  double? costEstimate;
 final  Map<String, dynamic>? _metadata;
@override@JsonKey(name: 'metadata') Map<String, dynamic>? get metadata {
  final value = _metadata;
  if (value == null) return null;
  if (_metadata is EqualUnmodifiableMapView) return _metadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'error') final  String? error;
@override@JsonKey(name: 'is_resumable') final  bool? isResumable;
 final  Map<String, dynamic>? _frozenContext;
@override@JsonKey(name: 'frozen_context') Map<String, dynamic>? get frozenContext {
  final value = _frozenContext;
  if (value == null) return null;
  if (_frozenContext is EqualUnmodifiableMapView) return _frozenContext;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepStates;
@override@JsonKey(name: 'step_states') Map<String, dynamic>? get stepStates {
  final value = _stepStates;
  if (value == null) return null;
  if (_stepStates is EqualUnmodifiableMapView) return _stepStates;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _results;
@override@JsonKey(name: 'results') Map<String, dynamic>? get results {
  final value = _results;
  if (value == null) return null;
  if (_results is EqualUnmodifiableMapView) return _results;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'progress') final  int? progress;
@override@JsonKey(name: 'status_message') final  String? statusMessage;
/// The strictly typed DTO containing the presentation flat data.
/// Replaces the legacy `results` Map.
@override@JsonKey(name: 'report_data') final  ReportDataDto? reportData;

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
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, status: $status, traceVersion: $traceVersion, strictnessLevel: $strictnessLevel, createdAt: $createdAt, costEstimate: $costEstimate, metadata: $metadata, error: $error, isResumable: $isResumable, frozenContext: $frozenContext, stepStates: $stepStates, results: $results, progress: $progress, statusMessage: $statusMessage, reportData: $reportData)';
}


}

/// @nodoc
abstract mixin class _$ExecutionRecordCopyWith<$Res> implements $ExecutionRecordCopyWith<$Res> {
  factory _$ExecutionRecordCopyWith(_ExecutionRecord value, $Res Function(_ExecutionRecord) _then) = __$ExecutionRecordCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? traceVersion,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'metadata') Map<String, dynamic>? metadata,@JsonKey(name: 'error') String? error,@JsonKey(name: 'is_resumable') bool? isResumable,@JsonKey(name: 'frozen_context') Map<String, dynamic>? frozenContext,@JsonKey(name: 'step_states') Map<String, dynamic>? stepStates,@JsonKey(name: 'results') Map<String, dynamic>? results,@JsonKey(name: 'progress') int? progress,@JsonKey(name: 'status_message') String? statusMessage,@JsonKey(name: 'report_data') ReportDataDto? reportData
});


@override $ReportDataDtoCopyWith<$Res>? get reportData;

}
/// @nodoc
class __$ExecutionRecordCopyWithImpl<$Res>
    implements _$ExecutionRecordCopyWith<$Res> {
  __$ExecutionRecordCopyWithImpl(this._self, this._then);

  final _ExecutionRecord _self;
  final $Res Function(_ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? workflowId = null,Object? status = null,Object? traceVersion = freezed,Object? strictnessLevel = freezed,Object? createdAt = freezed,Object? costEstimate = freezed,Object? metadata = freezed,Object? error = freezed,Object? isResumable = freezed,Object? frozenContext = freezed,Object? stepStates = freezed,Object? results = freezed,Object? progress = freezed,Object? statusMessage = freezed,Object? reportData = freezed,}) {
  return _then(_ExecutionRecord(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,traceVersion: freezed == traceVersion ? _self.traceVersion : traceVersion // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,metadata: freezed == metadata ? _self._metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isResumable: freezed == isResumable ? _self.isResumable : isResumable // ignore: cast_nullable_to_non_nullable
as bool?,frozenContext: freezed == frozenContext ? _self._frozenContext : frozenContext // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepStates: freezed == stepStates ? _self._stepStates : stepStates // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,results: freezed == results ? _self._results : results // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,progress: freezed == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int?,statusMessage: freezed == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String?,reportData: freezed == reportData ? _self.reportData : reportData // ignore: cast_nullable_to_non_nullable
as ReportDataDto?,
  ));
}

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportDataDtoCopyWith<$Res>? get reportData {
    if (_self.reportData == null) {
    return null;
  }

  return $ReportDataDtoCopyWith<$Res>(_self.reportData!, (value) {
    return _then(_self.copyWith(reportData: value));
  });
}
}

// dart format on
