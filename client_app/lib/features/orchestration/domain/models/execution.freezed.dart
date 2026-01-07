// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
Execution _$ExecutionFromJson(
  Map<String, dynamic> json
) {
        switch (json['status']) {
                  case 'pending':
          return ExecutionPending.fromJson(
            json
          );
                case 'running':
          return ExecutionRunning.fromJson(
            json
          );
                case 'completed':
          return ExecutionCompleted.fromJson(
            json
          );
                case 'failed':
          return ExecutionFailed.fromJson(
            json
          );
                case 'unknown':
          return ExecutionUnknown.fromJson(
            json
          );
        
          default:
            throw CheckedFromJsonException(
  json,
  'status',
  'Execution',
  'Invalid union type "${json['status']}"!'
);
        }
      
}

/// @nodoc
mixin _$Execution {

@JsonKey(name: 'execution_id') String get id;@JsonKey(name: 'start_time') DateTime get createdAt;@JsonKey(name: 'workflow_name') String? get workflowName; Map<String, dynamic> get inputs;@JsonKey(name: 'current_step_name') String? get currentStepName; ExecutionStatus get status;
/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionCopyWith<Execution> get copyWith => _$ExecutionCopyWithImpl<Execution>(this as Execution, _$identity);

  /// Serializes this Execution to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Execution&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&const DeepCollectionEquality().equals(other.inputs, inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,const DeepCollectionEquality().hash(inputs),currentStepName,status);

@override
String toString() {
  return 'Execution(id: $id, createdAt: $createdAt, workflowName: $workflowName, inputs: $inputs, currentStepName: $currentStepName, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionCopyWith<$Res>  {
  factory $ExecutionCopyWith(Execution value, $Res Function(Execution) _then) = _$ExecutionCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'execution_id') String id,@JsonKey(name: 'start_time') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionCopyWithImpl<$Res>
    implements $ExecutionCopyWith<$Res> {
  _$ExecutionCopyWithImpl(this._self, this._then);

  final Execution _self;
  final $Res Function(Execution) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? status = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self.inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}

}


/// Adds pattern-matching-related methods to [Execution].
extension ExecutionPatterns on Execution {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( ExecutionPending value)?  pending,TResult Function( ExecutionRunning value)?  running,TResult Function( ExecutionCompleted value)?  completed,TResult Function( ExecutionFailed value)?  failed,TResult Function( ExecutionUnknown value)?  unknown,required TResult orElse(),}){
final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that);case ExecutionRunning() when running != null:
return running(_that);case ExecutionCompleted() when completed != null:
return completed(_that);case ExecutionFailed() when failed != null:
return failed(_that);case ExecutionUnknown() when unknown != null:
return unknown(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( ExecutionPending value)  pending,required TResult Function( ExecutionRunning value)  running,required TResult Function( ExecutionCompleted value)  completed,required TResult Function( ExecutionFailed value)  failed,required TResult Function( ExecutionUnknown value)  unknown,}){
final _that = this;
switch (_that) {
case ExecutionPending():
return pending(_that);case ExecutionRunning():
return running(_that);case ExecutionCompleted():
return completed(_that);case ExecutionFailed():
return failed(_that);case ExecutionUnknown():
return unknown(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( ExecutionPending value)?  pending,TResult? Function( ExecutionRunning value)?  running,TResult? Function( ExecutionCompleted value)?  completed,TResult? Function( ExecutionFailed value)?  failed,TResult? Function( ExecutionUnknown value)?  unknown,}){
final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that);case ExecutionRunning() when running != null:
return running(_that);case ExecutionCompleted() when completed != null:
return completed(_that);case ExecutionFailed() when failed != null:
return failed(_that);case ExecutionUnknown() when unknown != null:
return unknown(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status)?  pending,TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status)?  running,TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  Map<String, dynamic> result, @JsonKey(name: 'xai_report_formatted')  String? xaiReport,  ExecutionStatus status)?  completed,TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  String? error,  ExecutionStatus status)?  failed,TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status,  Map<String, dynamic>? result,  String? error)?  unknown,required TResult orElse(),}) {final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.status);case ExecutionRunning() when running != null:
return running(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.status);case ExecutionCompleted() when completed != null:
return completed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.result,_that.xaiReport,_that.status);case ExecutionFailed() when failed != null:
return failed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.error,_that.status);case ExecutionUnknown() when unknown != null:
return unknown(_that.id,_that.createdAt,_that.workflowName,_that.inputs,_that.currentStepName,_that.status,_that.result,_that.error);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status)  pending,required TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status)  running,required TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  Map<String, dynamic> result, @JsonKey(name: 'xai_report_formatted')  String? xaiReport,  ExecutionStatus status)  completed,required TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  String? error,  ExecutionStatus status)  failed,required TResult Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status,  Map<String, dynamic>? result,  String? error)  unknown,}) {final _that = this;
switch (_that) {
case ExecutionPending():
return pending(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.status);case ExecutionRunning():
return running(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.status);case ExecutionCompleted():
return completed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.result,_that.xaiReport,_that.status);case ExecutionFailed():
return failed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.error,_that.status);case ExecutionUnknown():
return unknown(_that.id,_that.createdAt,_that.workflowName,_that.inputs,_that.currentStepName,_that.status,_that.result,_that.error);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status)?  pending,TResult? Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status)?  running,TResult? Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  Map<String, dynamic> result, @JsonKey(name: 'xai_report_formatted')  String? xaiReport,  ExecutionStatus status)?  completed,TResult? Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  String? error,  ExecutionStatus status)?  failed,TResult? Function(@JsonKey(name: 'execution_id')  String id, @JsonKey(name: 'start_time')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName,  ExecutionStatus status,  Map<String, dynamic>? result,  String? error)?  unknown,}) {final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.status);case ExecutionRunning() when running != null:
return running(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.status);case ExecutionCompleted() when completed != null:
return completed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.result,_that.xaiReport,_that.status);case ExecutionFailed() when failed != null:
return failed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.error,_that.status);case ExecutionUnknown() when unknown != null:
return unknown(_that.id,_that.createdAt,_that.workflowName,_that.inputs,_that.currentStepName,_that.status,_that.result,_that.error);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class ExecutionPending implements Execution {
  const ExecutionPending({@JsonKey(name: 'execution_id') required this.id, @JsonKey(name: 'start_time') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, this.status = ExecutionStatus.pending}): _inputs = inputs;
  factory ExecutionPending.fromJson(Map<String, dynamic> json) => _$ExecutionPendingFromJson(json);

@override@JsonKey(name: 'execution_id') final  String id;
@override@JsonKey(name: 'start_time') final  DateTime createdAt;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
@JsonKey(name: 'organization_id') final  String? organizationId;
@JsonKey(name: 'user_id') final  String? userId;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey(name: 'current_step_name') final  String? currentStepName;
@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionPendingCopyWith<ExecutionPending> get copyWith => _$ExecutionPendingCopyWithImpl<ExecutionPending>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionPendingToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionPending&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,status);

@override
String toString() {
  return 'Execution.pending(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionPendingCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionPendingCopyWith(ExecutionPending value, $Res Function(ExecutionPending) _then) = _$ExecutionPendingCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String id,@JsonKey(name: 'start_time') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionPendingCopyWithImpl<$Res>
    implements $ExecutionPendingCopyWith<$Res> {
  _$ExecutionPendingCopyWithImpl(this._self, this._then);

  final ExecutionPending _self;
  final $Res Function(ExecutionPending) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? status = null,}) {
  return _then(ExecutionPending(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionRunning implements Execution {
  const ExecutionRunning({@JsonKey(name: 'execution_id') required this.id, @JsonKey(name: 'start_time') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, this.status = ExecutionStatus.running}): _inputs = inputs;
  factory ExecutionRunning.fromJson(Map<String, dynamic> json) => _$ExecutionRunningFromJson(json);

@override@JsonKey(name: 'execution_id') final  String id;
@override@JsonKey(name: 'start_time') final  DateTime createdAt;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
@JsonKey(name: 'organization_id') final  String? organizationId;
@JsonKey(name: 'user_id') final  String? userId;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey(name: 'current_step_name') final  String? currentStepName;
@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionRunningCopyWith<ExecutionRunning> get copyWith => _$ExecutionRunningCopyWithImpl<ExecutionRunning>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionRunningToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionRunning&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,status);

@override
String toString() {
  return 'Execution.running(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionRunningCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionRunningCopyWith(ExecutionRunning value, $Res Function(ExecutionRunning) _then) = _$ExecutionRunningCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String id,@JsonKey(name: 'start_time') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionRunningCopyWithImpl<$Res>
    implements $ExecutionRunningCopyWith<$Res> {
  _$ExecutionRunningCopyWithImpl(this._self, this._then);

  final ExecutionRunning _self;
  final $Res Function(ExecutionRunning) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? status = null,}) {
  return _then(ExecutionRunning(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionCompleted implements Execution {
  const ExecutionCompleted({@JsonKey(name: 'execution_id') required this.id, @JsonKey(name: 'start_time') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, final  Map<String, dynamic> result = const {}, @JsonKey(name: 'xai_report_formatted') this.xaiReport, this.status = ExecutionStatus.completed}): _inputs = inputs,_result = result;
  factory ExecutionCompleted.fromJson(Map<String, dynamic> json) => _$ExecutionCompletedFromJson(json);

@override@JsonKey(name: 'execution_id') final  String id;
@override@JsonKey(name: 'start_time') final  DateTime createdAt;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
@JsonKey(name: 'organization_id') final  String? organizationId;
@JsonKey(name: 'user_id') final  String? userId;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey(name: 'current_step_name') final  String? currentStepName;
/// The final output of the workflow (e.g., the Report object).
/// Only available in completed state.
 final  Map<String, dynamic> _result;
/// The final output of the workflow (e.g., the Report object).
/// Only available in completed state.
@JsonKey() Map<String, dynamic> get result {
  if (_result is EqualUnmodifiableMapView) return _result;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_result);
}

/// Optional formatted markdown report, if pre-rendered.
@JsonKey(name: 'xai_report_formatted') final  String? xaiReport;
@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionCompletedCopyWith<ExecutionCompleted> get copyWith => _$ExecutionCompletedCopyWithImpl<ExecutionCompleted>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionCompletedToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionCompleted&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&const DeepCollectionEquality().equals(other._result, _result)&&(identical(other.xaiReport, xaiReport) || other.xaiReport == xaiReport)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,const DeepCollectionEquality().hash(_result),xaiReport,status);

@override
String toString() {
  return 'Execution.completed(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, result: $result, xaiReport: $xaiReport, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionCompletedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionCompletedCopyWith(ExecutionCompleted value, $Res Function(ExecutionCompleted) _then) = _$ExecutionCompletedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String id,@JsonKey(name: 'start_time') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName, Map<String, dynamic> result,@JsonKey(name: 'xai_report_formatted') String? xaiReport, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionCompletedCopyWithImpl<$Res>
    implements $ExecutionCompletedCopyWith<$Res> {
  _$ExecutionCompletedCopyWithImpl(this._self, this._then);

  final ExecutionCompleted _self;
  final $Res Function(ExecutionCompleted) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? result = null,Object? xaiReport = freezed,Object? status = null,}) {
  return _then(ExecutionCompleted(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,result: null == result ? _self._result : result // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,xaiReport: freezed == xaiReport ? _self.xaiReport : xaiReport // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionFailed implements Execution {
  const ExecutionFailed({@JsonKey(name: 'execution_id') required this.id, @JsonKey(name: 'start_time') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, this.error, this.status = ExecutionStatus.failed}): _inputs = inputs;
  factory ExecutionFailed.fromJson(Map<String, dynamic> json) => _$ExecutionFailedFromJson(json);

@override@JsonKey(name: 'execution_id') final  String id;
@override@JsonKey(name: 'start_time') final  DateTime createdAt;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
@JsonKey(name: 'organization_id') final  String? organizationId;
@JsonKey(name: 'user_id') final  String? userId;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey(name: 'current_step_name') final  String? currentStepName;
/// Error message or failure reason.
 final  String? error;
@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionFailedCopyWith<ExecutionFailed> get copyWith => _$ExecutionFailedCopyWithImpl<ExecutionFailed>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionFailedToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionFailed&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.error, error) || other.error == error)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,error,status);

@override
String toString() {
  return 'Execution.failed(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, error: $error, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionFailedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionFailedCopyWith(ExecutionFailed value, $Res Function(ExecutionFailed) _then) = _$ExecutionFailedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String id,@JsonKey(name: 'start_time') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName, String? error, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionFailedCopyWithImpl<$Res>
    implements $ExecutionFailedCopyWith<$Res> {
  _$ExecutionFailedCopyWithImpl(this._self, this._then);

  final ExecutionFailed _self;
  final $Res Function(ExecutionFailed) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? error = freezed,Object? status = null,}) {
  return _then(ExecutionFailed(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionUnknown implements Execution {
  const ExecutionUnknown({@JsonKey(name: 'execution_id') required this.id, @JsonKey(name: 'start_time') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, this.status = ExecutionStatus.unknown, final  Map<String, dynamic>? result, this.error}): _inputs = inputs,_result = result;
  factory ExecutionUnknown.fromJson(Map<String, dynamic> json) => _$ExecutionUnknownFromJson(json);

@override@JsonKey(name: 'execution_id') final  String id;
@override@JsonKey(name: 'start_time') final  DateTime createdAt;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey(name: 'current_step_name') final  String? currentStepName;
@override@JsonKey() final  ExecutionStatus status;
 final  Map<String, dynamic>? _result;
 Map<String, dynamic>? get result {
  final value = _result;
  if (value == null) return null;
  if (_result is EqualUnmodifiableMapView) return _result;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  String? error;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionUnknownCopyWith<ExecutionUnknown> get copyWith => _$ExecutionUnknownCopyWithImpl<ExecutionUnknown>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionUnknownToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionUnknown&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other._result, _result)&&(identical(other.error, error) || other.error == error));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,const DeepCollectionEquality().hash(_inputs),currentStepName,status,const DeepCollectionEquality().hash(_result),error);

@override
String toString() {
  return 'Execution.unknown(id: $id, createdAt: $createdAt, workflowName: $workflowName, inputs: $inputs, currentStepName: $currentStepName, status: $status, result: $result, error: $error)';
}


}

/// @nodoc
abstract mixin class $ExecutionUnknownCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionUnknownCopyWith(ExecutionUnknown value, $Res Function(ExecutionUnknown) _then) = _$ExecutionUnknownCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String id,@JsonKey(name: 'start_time') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName, ExecutionStatus status, Map<String, dynamic>? result, String? error
});




}
/// @nodoc
class _$ExecutionUnknownCopyWithImpl<$Res>
    implements $ExecutionUnknownCopyWith<$Res> {
  _$ExecutionUnknownCopyWithImpl(this._self, this._then);

  final ExecutionUnknown _self;
  final $Res Function(ExecutionUnknown) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? status = null,Object? result = freezed,Object? error = freezed,}) {
  return _then(ExecutionUnknown(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,result: freezed == result ? _self._result : result // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
