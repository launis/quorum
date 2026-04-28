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

 String get id;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(fromJson: _statusFromJson) String get status;@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? get traceVersion;/// The strictly typed DTO containing the presentation flat data.
/// Replaces the legacy `results` Map.
@JsonKey(name: 'report_data') ReportDataDTO? get reportData;
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionRecordCopyWith<ExecutionRecord> get copyWith => _$ExecutionRecordCopyWithImpl<ExecutionRecord>(this as ExecutionRecord, _$identity);

  /// Serializes this ExecutionRecord to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, status: $status, traceVersion: $traceVersion, reportData: $reportData)';
}


}

/// @nodoc
abstract mixin class $ExecutionRecordCopyWith<$Res>  {
  factory $ExecutionRecordCopyWith(ExecutionRecord value, $Res Function(ExecutionRecord) _then) = _$ExecutionRecordCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? traceVersion,@JsonKey(name: 'report_data') ReportDataDTO? reportData
});


$ReportDataDTOCopyWith<$Res>? get reportData;

}
/// @nodoc
class _$ExecutionRecordCopyWithImpl<$Res>
    implements $ExecutionRecordCopyWith<$Res> {
  _$ExecutionRecordCopyWithImpl(this._self, this._then);

  final ExecutionRecord _self;
  final $Res Function(ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? workflowId = null,Object? status = null,Object? traceVersion = freezed,Object? reportData = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,traceVersion: freezed == traceVersion ? _self.traceVersion : traceVersion // ignore: cast_nullable_to_non_nullable
as String?,reportData: freezed == reportData ? _self.reportData : reportData // ignore: cast_nullable_to_non_nullable
as ReportDataDTO?,
  ));
}
/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportDataDTOCopyWith<$Res>? get reportData {
    if (_self.reportData == null) {
    return null;
  }

  return $ReportDataDTOCopyWith<$Res>(_self.reportData!, (value) {
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'report_data')  ReportDataDTO? reportData)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.status,_that.traceVersion,_that.reportData);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'report_data')  ReportDataDTO? reportData)  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord():
return $default(_that.id,_that.workflowId,_that.status,_that.traceVersion,_that.reportData);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(fromJson: _statusFromJson)  String status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson)  String? traceVersion, @JsonKey(name: 'report_data')  ReportDataDTO? reportData)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionRecord() when $default != null:
return $default(_that.id,_that.workflowId,_that.status,_that.traceVersion,_that.reportData);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionRecord extends ExecutionRecord {
  const _ExecutionRecord({required this.id, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(fromJson: _statusFromJson) required this.status, @JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) this.traceVersion, @JsonKey(name: 'report_data') this.reportData}): super._();
  factory _ExecutionRecord.fromJson(Map<String, dynamic> json) => _$ExecutionRecordFromJson(json);

@override final  String id;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(fromJson: _statusFromJson) final  String status;
@override@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) final  String? traceVersion;
/// The strictly typed DTO containing the presentation flat data.
/// Replaces the legacy `results` Map.
@override@JsonKey(name: 'report_data') final  ReportDataDTO? reportData;

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
  return 'ExecutionRecord(id: $id, workflowId: $workflowId, status: $status, traceVersion: $traceVersion, reportData: $reportData)';
}


}

/// @nodoc
abstract mixin class _$ExecutionRecordCopyWith<$Res> implements $ExecutionRecordCopyWith<$Res> {
  factory _$ExecutionRecordCopyWith(_ExecutionRecord value, $Res Function(_ExecutionRecord) _then) = __$ExecutionRecordCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(fromJson: _statusFromJson) String status,@JsonKey(name: 'trace_version', fromJson: _traceVersionFromJson) String? traceVersion,@JsonKey(name: 'report_data') ReportDataDTO? reportData
});


@override $ReportDataDTOCopyWith<$Res>? get reportData;

}
/// @nodoc
class __$ExecutionRecordCopyWithImpl<$Res>
    implements _$ExecutionRecordCopyWith<$Res> {
  __$ExecutionRecordCopyWithImpl(this._self, this._then);

  final _ExecutionRecord _self;
  final $Res Function(_ExecutionRecord) _then;

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? workflowId = null,Object? status = null,Object? traceVersion = freezed,Object? reportData = freezed,}) {
  return _then(_ExecutionRecord(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,traceVersion: freezed == traceVersion ? _self.traceVersion : traceVersion // ignore: cast_nullable_to_non_nullable
as String?,reportData: freezed == reportData ? _self.reportData : reportData // ignore: cast_nullable_to_non_nullable
as ReportDataDTO?,
  ));
}

/// Create a copy of ExecutionRecord
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportDataDTOCopyWith<$Res>? get reportData {
    if (_self.reportData == null) {
    return null;
  }

  return $ReportDataDTOCopyWith<$Res>(_self.reportData!, (value) {
    return _then(_self.copyWith(reportData: value));
  });
}
}

// dart format on
