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
                case 'started':
          return ExecutionStarted.fromJson(
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
                case 'rejected':
          return ExecutionRejected.fromJson(
            json
          );
                case 'failed':
          return ExecutionFailed.fromJson(
            json
          );
                case 'interrupted':
          return ExecutionInterrupted.fromJson(
            json
          );
                case 'cancelling':
          return ExecutionCancelling.fromJson(
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

@JsonKey(name: 'id') String get id;@JsonKey(name: 'started_at') DateTime get createdAt;@JsonKey(name: 'workflow_name') String? get workflowName; Map<String, dynamic> get inputs;@JsonKey(name: 'current_step_name') String? get currentStepName;@JsonKey(name: 'current_step_index') int? get currentStepIndex;@JsonKey(name: 'total_steps') int? get totalSteps;@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps; ExecutionStatus get status;
/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionCopyWith<Execution> get copyWith => _$ExecutionCopyWithImpl<Execution>(this as Execution, _$identity);

  /// Serializes this Execution to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Execution&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&const DeepCollectionEquality().equals(other.inputs, inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other.workflowSteps, workflowSteps)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,const DeepCollectionEquality().hash(inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(workflowSteps),status);

@override
String toString() {
  return 'Execution(id: $id, createdAt: $createdAt, workflowName: $workflowName, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionCopyWith<$Res>  {
  factory $ExecutionCopyWith(Execution value, $Res Function(Execution) _then) = _$ExecutionCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? status = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self.inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self.workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( ExecutionPending value)?  pending,TResult Function( ExecutionStarted value)?  started,TResult Function( ExecutionRunning value)?  running,TResult Function( ExecutionCompleted value)?  completed,TResult Function( ExecutionRejected value)?  rejected,TResult Function( ExecutionFailed value)?  failed,TResult Function( ExecutionInterrupted value)?  interrupted,TResult Function( ExecutionCancelling value)?  cancelling,TResult Function( ExecutionUnknown value)?  unknown,required TResult orElse(),}){
final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that);case ExecutionStarted() when started != null:
return started(_that);case ExecutionRunning() when running != null:
return running(_that);case ExecutionCompleted() when completed != null:
return completed(_that);case ExecutionRejected() when rejected != null:
return rejected(_that);case ExecutionFailed() when failed != null:
return failed(_that);case ExecutionInterrupted() when interrupted != null:
return interrupted(_that);case ExecutionCancelling() when cancelling != null:
return cancelling(_that);case ExecutionUnknown() when unknown != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( ExecutionPending value)  pending,required TResult Function( ExecutionStarted value)  started,required TResult Function( ExecutionRunning value)  running,required TResult Function( ExecutionCompleted value)  completed,required TResult Function( ExecutionRejected value)  rejected,required TResult Function( ExecutionFailed value)  failed,required TResult Function( ExecutionInterrupted value)  interrupted,required TResult Function( ExecutionCancelling value)  cancelling,required TResult Function( ExecutionUnknown value)  unknown,}){
final _that = this;
switch (_that) {
case ExecutionPending():
return pending(_that);case ExecutionStarted():
return started(_that);case ExecutionRunning():
return running(_that);case ExecutionCompleted():
return completed(_that);case ExecutionRejected():
return rejected(_that);case ExecutionFailed():
return failed(_that);case ExecutionInterrupted():
return interrupted(_that);case ExecutionCancelling():
return cancelling(_that);case ExecutionUnknown():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( ExecutionPending value)?  pending,TResult? Function( ExecutionStarted value)?  started,TResult? Function( ExecutionRunning value)?  running,TResult? Function( ExecutionCompleted value)?  completed,TResult? Function( ExecutionRejected value)?  rejected,TResult? Function( ExecutionFailed value)?  failed,TResult? Function( ExecutionInterrupted value)?  interrupted,TResult? Function( ExecutionCancelling value)?  cancelling,TResult? Function( ExecutionUnknown value)?  unknown,}){
final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that);case ExecutionStarted() when started != null:
return started(_that);case ExecutionRunning() when running != null:
return running(_that);case ExecutionCompleted() when completed != null:
return completed(_that);case ExecutionRejected() when rejected != null:
return rejected(_that);case ExecutionFailed() when failed != null:
return failed(_that);case ExecutionInterrupted() when interrupted != null:
return interrupted(_that);case ExecutionCancelling() when cancelling != null:
return cancelling(_that);case ExecutionUnknown() when unknown != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  pending,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  started,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  running,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps,  Map<String, dynamic> result, @JsonKey(name: 'xai_report_formatted')  String? xaiReport, @JsonKey(name: 'audit_results')  Map<String, EvaluationResult> auditResults,  Map<String, dynamic> usage, @JsonKey(name: 'step_guard')  Map<String, dynamic>? stepGuard, @JsonKey(name: 'step_analyst')  Map<String, dynamic>? stepAnalyst, @JsonKey(name: 'step_profiler')  Map<String, dynamic>? stepProfiler, @JsonKey(name: 'step_logician')  Map<String, dynamic>? stepLogician, @JsonKey(name: 'step_falsifier')  Map<String, dynamic>? stepFalsifier, @JsonKey(name: 'step_overseer')  Map<String, dynamic>? stepOverseer, @JsonKey(name: 'step_causal')  Map<String, dynamic>? stepCausal, @JsonKey(name: 'step_detector')  Map<String, dynamic>? stepDetector, @JsonKey(name: 'step_judge')  Map<String, dynamic>? stepJudge, @JsonKey(name: 'step_judge_cognitive')  Map<String, dynamic>? stepJudgeCognitive, @JsonKey(name: 'step_archivist')  Map<String, dynamic>? stepArchivist, @JsonKey(name: 'step_coach')  Map<String, dynamic>? stepCoach, @JsonKey(name: 'step_interaction')  Map<String, dynamic>? stepInteraction, @JsonKey(name: 'step_panel')  Map<String, dynamic>? stepPanel, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  completed,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)?  rejected,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)?  failed,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)?  interrupted,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  cancelling,TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status,  Map<String, dynamic>? result,  String? error)?  unknown,required TResult orElse(),}) {final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionStarted() when started != null:
return started(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionRunning() when running != null:
return running(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionCompleted() when completed != null:
return completed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.result,_that.xaiReport,_that.auditResults,_that.usage,_that.stepGuard,_that.stepAnalyst,_that.stepProfiler,_that.stepLogician,_that.stepFalsifier,_that.stepOverseer,_that.stepCausal,_that.stepDetector,_that.stepJudge,_that.stepJudgeCognitive,_that.stepArchivist,_that.stepCoach,_that.stepInteraction,_that.stepPanel,_that.workflowSteps,_that.status);case ExecutionRejected() when rejected != null:
return rejected(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionFailed() when failed != null:
return failed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionInterrupted() when interrupted != null:
return interrupted(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionCancelling() when cancelling != null:
return cancelling(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionUnknown() when unknown != null:
return unknown(_that.id,_that.createdAt,_that.workflowName,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status,_that.result,_that.error);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)  pending,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)  started,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)  running,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps,  Map<String, dynamic> result, @JsonKey(name: 'xai_report_formatted')  String? xaiReport, @JsonKey(name: 'audit_results')  Map<String, EvaluationResult> auditResults,  Map<String, dynamic> usage, @JsonKey(name: 'step_guard')  Map<String, dynamic>? stepGuard, @JsonKey(name: 'step_analyst')  Map<String, dynamic>? stepAnalyst, @JsonKey(name: 'step_profiler')  Map<String, dynamic>? stepProfiler, @JsonKey(name: 'step_logician')  Map<String, dynamic>? stepLogician, @JsonKey(name: 'step_falsifier')  Map<String, dynamic>? stepFalsifier, @JsonKey(name: 'step_overseer')  Map<String, dynamic>? stepOverseer, @JsonKey(name: 'step_causal')  Map<String, dynamic>? stepCausal, @JsonKey(name: 'step_detector')  Map<String, dynamic>? stepDetector, @JsonKey(name: 'step_judge')  Map<String, dynamic>? stepJudge, @JsonKey(name: 'step_judge_cognitive')  Map<String, dynamic>? stepJudgeCognitive, @JsonKey(name: 'step_archivist')  Map<String, dynamic>? stepArchivist, @JsonKey(name: 'step_coach')  Map<String, dynamic>? stepCoach, @JsonKey(name: 'step_interaction')  Map<String, dynamic>? stepInteraction, @JsonKey(name: 'step_panel')  Map<String, dynamic>? stepPanel, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)  completed,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)  rejected,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)  failed,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)  interrupted,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)  cancelling,required TResult Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status,  Map<String, dynamic>? result,  String? error)  unknown,}) {final _that = this;
switch (_that) {
case ExecutionPending():
return pending(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionStarted():
return started(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionRunning():
return running(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionCompleted():
return completed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.result,_that.xaiReport,_that.auditResults,_that.usage,_that.stepGuard,_that.stepAnalyst,_that.stepProfiler,_that.stepLogician,_that.stepFalsifier,_that.stepOverseer,_that.stepCausal,_that.stepDetector,_that.stepJudge,_that.stepJudgeCognitive,_that.stepArchivist,_that.stepCoach,_that.stepInteraction,_that.stepPanel,_that.workflowSteps,_that.status);case ExecutionRejected():
return rejected(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionFailed():
return failed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionInterrupted():
return interrupted(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionCancelling():
return cancelling(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionUnknown():
return unknown(_that.id,_that.createdAt,_that.workflowName,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status,_that.result,_that.error);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  pending,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  started,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  running,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps,  Map<String, dynamic> result, @JsonKey(name: 'xai_report_formatted')  String? xaiReport, @JsonKey(name: 'audit_results')  Map<String, EvaluationResult> auditResults,  Map<String, dynamic> usage, @JsonKey(name: 'step_guard')  Map<String, dynamic>? stepGuard, @JsonKey(name: 'step_analyst')  Map<String, dynamic>? stepAnalyst, @JsonKey(name: 'step_profiler')  Map<String, dynamic>? stepProfiler, @JsonKey(name: 'step_logician')  Map<String, dynamic>? stepLogician, @JsonKey(name: 'step_falsifier')  Map<String, dynamic>? stepFalsifier, @JsonKey(name: 'step_overseer')  Map<String, dynamic>? stepOverseer, @JsonKey(name: 'step_causal')  Map<String, dynamic>? stepCausal, @JsonKey(name: 'step_detector')  Map<String, dynamic>? stepDetector, @JsonKey(name: 'step_judge')  Map<String, dynamic>? stepJudge, @JsonKey(name: 'step_judge_cognitive')  Map<String, dynamic>? stepJudgeCognitive, @JsonKey(name: 'step_archivist')  Map<String, dynamic>? stepArchivist, @JsonKey(name: 'step_coach')  Map<String, dynamic>? stepCoach, @JsonKey(name: 'step_interaction')  Map<String, dynamic>? stepInteraction, @JsonKey(name: 'step_panel')  Map<String, dynamic>? stepPanel, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  completed,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)?  rejected,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)?  failed,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  String? error,  ExecutionStatus status)?  interrupted,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status)?  cancelling,TResult? Function(@JsonKey(name: 'id')  String id, @JsonKey(name: 'started_at')  DateTime createdAt, @JsonKey(name: 'workflow_name')  String? workflowName,  Map<String, dynamic> inputs, @JsonKey(name: 'current_step_name')  String? currentStepName, @JsonKey(name: 'current_step_index')  int? currentStepIndex, @JsonKey(name: 'total_steps')  int? totalSteps, @JsonKey(name: 'workflow_steps')  List<String>? workflowSteps,  ExecutionStatus status,  Map<String, dynamic>? result,  String? error)?  unknown,}) {final _that = this;
switch (_that) {
case ExecutionPending() when pending != null:
return pending(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionStarted() when started != null:
return started(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionRunning() when running != null:
return running(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionCompleted() when completed != null:
return completed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.result,_that.xaiReport,_that.auditResults,_that.usage,_that.stepGuard,_that.stepAnalyst,_that.stepProfiler,_that.stepLogician,_that.stepFalsifier,_that.stepOverseer,_that.stepCausal,_that.stepDetector,_that.stepJudge,_that.stepJudgeCognitive,_that.stepArchivist,_that.stepCoach,_that.stepInteraction,_that.stepPanel,_that.workflowSteps,_that.status);case ExecutionRejected() when rejected != null:
return rejected(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionFailed() when failed != null:
return failed(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionInterrupted() when interrupted != null:
return interrupted(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.error,_that.status);case ExecutionCancelling() when cancelling != null:
return cancelling(_that.id,_that.createdAt,_that.workflowName,_that.organizationId,_that.userId,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status);case ExecutionUnknown() when unknown != null:
return unknown(_that.id,_that.createdAt,_that.workflowName,_that.inputs,_that.currentStepName,_that.currentStepIndex,_that.totalSteps,_that.workflowSteps,_that.status,_that.result,_that.error);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class ExecutionPending implements Execution {
  const ExecutionPending({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.status = ExecutionStatus.pending}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionPending.fromJson(Map<String, dynamic> json) => _$ExecutionPendingFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionPending&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),status);

@override
String toString() {
  return 'Execution.pending(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionPendingCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionPendingCopyWith(ExecutionPending value, $Res Function(ExecutionPending) _then) = _$ExecutionPendingCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? status = null,}) {
  return _then(ExecutionPending(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionStarted implements Execution {
  const ExecutionStarted({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.status = ExecutionStatus.started}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionStarted.fromJson(Map<String, dynamic> json) => _$ExecutionStartedFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionStartedCopyWith<ExecutionStarted> get copyWith => _$ExecutionStartedCopyWithImpl<ExecutionStarted>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionStartedToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionStarted&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),status);

@override
String toString() {
  return 'Execution.started(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionStartedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionStartedCopyWith(ExecutionStarted value, $Res Function(ExecutionStarted) _then) = _$ExecutionStartedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionStartedCopyWithImpl<$Res>
    implements $ExecutionStartedCopyWith<$Res> {
  _$ExecutionStartedCopyWithImpl(this._self, this._then);

  final ExecutionStarted _self;
  final $Res Function(ExecutionStarted) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? status = null,}) {
  return _then(ExecutionStarted(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionRunning implements Execution {
  const ExecutionRunning({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.status = ExecutionStatus.running}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionRunning.fromJson(Map<String, dynamic> json) => _$ExecutionRunningFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionRunning&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),status);

@override
String toString() {
  return 'Execution.running(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionRunningCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionRunningCopyWith(ExecutionRunning value, $Res Function(ExecutionRunning) _then) = _$ExecutionRunningCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? status = null,}) {
  return _then(ExecutionRunning(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionCompleted implements Execution {
  const ExecutionCompleted({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, final  Map<String, dynamic> result = const {}, @JsonKey(name: 'xai_report_formatted') this.xaiReport, @JsonKey(name: 'audit_results') final  Map<String, EvaluationResult> auditResults = const {}, final  Map<String, dynamic> usage = const {}, @JsonKey(name: 'step_guard') final  Map<String, dynamic>? stepGuard, @JsonKey(name: 'step_analyst') final  Map<String, dynamic>? stepAnalyst, @JsonKey(name: 'step_profiler') final  Map<String, dynamic>? stepProfiler, @JsonKey(name: 'step_logician') final  Map<String, dynamic>? stepLogician, @JsonKey(name: 'step_falsifier') final  Map<String, dynamic>? stepFalsifier, @JsonKey(name: 'step_overseer') final  Map<String, dynamic>? stepOverseer, @JsonKey(name: 'step_causal') final  Map<String, dynamic>? stepCausal, @JsonKey(name: 'step_detector') final  Map<String, dynamic>? stepDetector, @JsonKey(name: 'step_judge') final  Map<String, dynamic>? stepJudge, @JsonKey(name: 'step_judge_cognitive') final  Map<String, dynamic>? stepJudgeCognitive, @JsonKey(name: 'step_archivist') final  Map<String, dynamic>? stepArchivist, @JsonKey(name: 'step_coach') final  Map<String, dynamic>? stepCoach, @JsonKey(name: 'step_interaction') final  Map<String, dynamic>? stepInteraction, @JsonKey(name: 'step_panel') final  Map<String, dynamic>? stepPanel, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.status = ExecutionStatus.completed}): _inputs = inputs,_result = result,_auditResults = auditResults,_usage = usage,_stepGuard = stepGuard,_stepAnalyst = stepAnalyst,_stepProfiler = stepProfiler,_stepLogician = stepLogician,_stepFalsifier = stepFalsifier,_stepOverseer = stepOverseer,_stepCausal = stepCausal,_stepDetector = stepDetector,_stepJudge = stepJudge,_stepJudgeCognitive = stepJudgeCognitive,_stepArchivist = stepArchivist,_stepCoach = stepCoach,_stepInteraction = stepInteraction,_stepPanel = stepPanel,_workflowSteps = workflowSteps;
  factory ExecutionCompleted.fromJson(Map<String, dynamic> json) => _$ExecutionCompletedFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
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
/// Dynamic Evaluation Results (New Multi-Matrix System)
/// Key = Step ID (e.g. "step_judge_cognitive")
 final  Map<String, EvaluationResult> _auditResults;
/// Dynamic Evaluation Results (New Multi-Matrix System)
/// Key = Step ID (e.g. "step_judge_cognitive")
@JsonKey(name: 'audit_results') Map<String, EvaluationResult> get auditResults {
  if (_auditResults is EqualUnmodifiableMapView) return _auditResults;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_auditResults);
}

/// Usage Metrics (Cost Tracking)
 final  Map<String, dynamic> _usage;
/// Usage Metrics (Cost Tracking)
@JsonKey() Map<String, dynamic> get usage {
  if (_usage is EqualUnmodifiableMapView) return _usage;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_usage);
}

/// Agent Outputs (Typed as Maps for now, or generic structures)
 final  Map<String, dynamic>? _stepGuard;
/// Agent Outputs (Typed as Maps for now, or generic structures)
@JsonKey(name: 'step_guard') Map<String, dynamic>? get stepGuard {
  final value = _stepGuard;
  if (value == null) return null;
  if (_stepGuard is EqualUnmodifiableMapView) return _stepGuard;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepAnalyst;
@JsonKey(name: 'step_analyst') Map<String, dynamic>? get stepAnalyst {
  final value = _stepAnalyst;
  if (value == null) return null;
  if (_stepAnalyst is EqualUnmodifiableMapView) return _stepAnalyst;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepProfiler;
@JsonKey(name: 'step_profiler') Map<String, dynamic>? get stepProfiler {
  final value = _stepProfiler;
  if (value == null) return null;
  if (_stepProfiler is EqualUnmodifiableMapView) return _stepProfiler;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepLogician;
@JsonKey(name: 'step_logician') Map<String, dynamic>? get stepLogician {
  final value = _stepLogician;
  if (value == null) return null;
  if (_stepLogician is EqualUnmodifiableMapView) return _stepLogician;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepFalsifier;
@JsonKey(name: 'step_falsifier') Map<String, dynamic>? get stepFalsifier {
  final value = _stepFalsifier;
  if (value == null) return null;
  if (_stepFalsifier is EqualUnmodifiableMapView) return _stepFalsifier;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepOverseer;
@JsonKey(name: 'step_overseer') Map<String, dynamic>? get stepOverseer {
  final value = _stepOverseer;
  if (value == null) return null;
  if (_stepOverseer is EqualUnmodifiableMapView) return _stepOverseer;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepCausal;
@JsonKey(name: 'step_causal') Map<String, dynamic>? get stepCausal {
  final value = _stepCausal;
  if (value == null) return null;
  if (_stepCausal is EqualUnmodifiableMapView) return _stepCausal;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepDetector;
@JsonKey(name: 'step_detector') Map<String, dynamic>? get stepDetector {
  final value = _stepDetector;
  if (value == null) return null;
  if (_stepDetector is EqualUnmodifiableMapView) return _stepDetector;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepJudge;
@JsonKey(name: 'step_judge') Map<String, dynamic>? get stepJudge {
  final value = _stepJudge;
  if (value == null) return null;
  if (_stepJudge is EqualUnmodifiableMapView) return _stepJudge;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepJudgeCognitive;
@JsonKey(name: 'step_judge_cognitive') Map<String, dynamic>? get stepJudgeCognitive {
  final value = _stepJudgeCognitive;
  if (value == null) return null;
  if (_stepJudgeCognitive is EqualUnmodifiableMapView) return _stepJudgeCognitive;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepArchivist;
@JsonKey(name: 'step_archivist') Map<String, dynamic>? get stepArchivist {
  final value = _stepArchivist;
  if (value == null) return null;
  if (_stepArchivist is EqualUnmodifiableMapView) return _stepArchivist;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepCoach;
@JsonKey(name: 'step_coach') Map<String, dynamic>? get stepCoach {
  final value = _stepCoach;
  if (value == null) return null;
  if (_stepCoach is EqualUnmodifiableMapView) return _stepCoach;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepInteraction;
@JsonKey(name: 'step_interaction') Map<String, dynamic>? get stepInteraction {
  final value = _stepInteraction;
  if (value == null) return null;
  if (_stepInteraction is EqualUnmodifiableMapView) return _stepInteraction;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _stepPanel;
@JsonKey(name: 'step_panel') Map<String, dynamic>? get stepPanel {
  final value = _stepPanel;
  if (value == null) return null;
  if (_stepPanel is EqualUnmodifiableMapView) return _stepPanel;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionCompleted&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._result, _result)&&(identical(other.xaiReport, xaiReport) || other.xaiReport == xaiReport)&&const DeepCollectionEquality().equals(other._auditResults, _auditResults)&&const DeepCollectionEquality().equals(other._usage, _usage)&&const DeepCollectionEquality().equals(other._stepGuard, _stepGuard)&&const DeepCollectionEquality().equals(other._stepAnalyst, _stepAnalyst)&&const DeepCollectionEquality().equals(other._stepProfiler, _stepProfiler)&&const DeepCollectionEquality().equals(other._stepLogician, _stepLogician)&&const DeepCollectionEquality().equals(other._stepFalsifier, _stepFalsifier)&&const DeepCollectionEquality().equals(other._stepOverseer, _stepOverseer)&&const DeepCollectionEquality().equals(other._stepCausal, _stepCausal)&&const DeepCollectionEquality().equals(other._stepDetector, _stepDetector)&&const DeepCollectionEquality().equals(other._stepJudge, _stepJudge)&&const DeepCollectionEquality().equals(other._stepJudgeCognitive, _stepJudgeCognitive)&&const DeepCollectionEquality().equals(other._stepArchivist, _stepArchivist)&&const DeepCollectionEquality().equals(other._stepCoach, _stepCoach)&&const DeepCollectionEquality().equals(other._stepInteraction, _stepInteraction)&&const DeepCollectionEquality().equals(other._stepPanel, _stepPanel)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_result),xaiReport,const DeepCollectionEquality().hash(_auditResults),const DeepCollectionEquality().hash(_usage),const DeepCollectionEquality().hash(_stepGuard),const DeepCollectionEquality().hash(_stepAnalyst),const DeepCollectionEquality().hash(_stepProfiler),const DeepCollectionEquality().hash(_stepLogician),const DeepCollectionEquality().hash(_stepFalsifier),const DeepCollectionEquality().hash(_stepOverseer),const DeepCollectionEquality().hash(_stepCausal),const DeepCollectionEquality().hash(_stepDetector),const DeepCollectionEquality().hash(_stepJudge),const DeepCollectionEquality().hash(_stepJudgeCognitive),const DeepCollectionEquality().hash(_stepArchivist),const DeepCollectionEquality().hash(_stepCoach),const DeepCollectionEquality().hash(_stepInteraction),const DeepCollectionEquality().hash(_stepPanel),const DeepCollectionEquality().hash(_workflowSteps),status]);

@override
String toString() {
  return 'Execution.completed(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, result: $result, xaiReport: $xaiReport, auditResults: $auditResults, usage: $usage, stepGuard: $stepGuard, stepAnalyst: $stepAnalyst, stepProfiler: $stepProfiler, stepLogician: $stepLogician, stepFalsifier: $stepFalsifier, stepOverseer: $stepOverseer, stepCausal: $stepCausal, stepDetector: $stepDetector, stepJudge: $stepJudge, stepJudgeCognitive: $stepJudgeCognitive, stepArchivist: $stepArchivist, stepCoach: $stepCoach, stepInteraction: $stepInteraction, stepPanel: $stepPanel, workflowSteps: $workflowSteps, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionCompletedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionCompletedCopyWith(ExecutionCompleted value, $Res Function(ExecutionCompleted) _then) = _$ExecutionCompletedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps, Map<String, dynamic> result,@JsonKey(name: 'xai_report_formatted') String? xaiReport,@JsonKey(name: 'audit_results') Map<String, EvaluationResult> auditResults, Map<String, dynamic> usage,@JsonKey(name: 'step_guard') Map<String, dynamic>? stepGuard,@JsonKey(name: 'step_analyst') Map<String, dynamic>? stepAnalyst,@JsonKey(name: 'step_profiler') Map<String, dynamic>? stepProfiler,@JsonKey(name: 'step_logician') Map<String, dynamic>? stepLogician,@JsonKey(name: 'step_falsifier') Map<String, dynamic>? stepFalsifier,@JsonKey(name: 'step_overseer') Map<String, dynamic>? stepOverseer,@JsonKey(name: 'step_causal') Map<String, dynamic>? stepCausal,@JsonKey(name: 'step_detector') Map<String, dynamic>? stepDetector,@JsonKey(name: 'step_judge') Map<String, dynamic>? stepJudge,@JsonKey(name: 'step_judge_cognitive') Map<String, dynamic>? stepJudgeCognitive,@JsonKey(name: 'step_archivist') Map<String, dynamic>? stepArchivist,@JsonKey(name: 'step_coach') Map<String, dynamic>? stepCoach,@JsonKey(name: 'step_interaction') Map<String, dynamic>? stepInteraction,@JsonKey(name: 'step_panel') Map<String, dynamic>? stepPanel,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? result = null,Object? xaiReport = freezed,Object? auditResults = null,Object? usage = null,Object? stepGuard = freezed,Object? stepAnalyst = freezed,Object? stepProfiler = freezed,Object? stepLogician = freezed,Object? stepFalsifier = freezed,Object? stepOverseer = freezed,Object? stepCausal = freezed,Object? stepDetector = freezed,Object? stepJudge = freezed,Object? stepJudgeCognitive = freezed,Object? stepArchivist = freezed,Object? stepCoach = freezed,Object? stepInteraction = freezed,Object? stepPanel = freezed,Object? workflowSteps = freezed,Object? status = null,}) {
  return _then(ExecutionCompleted(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,result: null == result ? _self._result : result // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,xaiReport: freezed == xaiReport ? _self.xaiReport : xaiReport // ignore: cast_nullable_to_non_nullable
as String?,auditResults: null == auditResults ? _self._auditResults : auditResults // ignore: cast_nullable_to_non_nullable
as Map<String, EvaluationResult>,usage: null == usage ? _self._usage : usage // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,stepGuard: freezed == stepGuard ? _self._stepGuard : stepGuard // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepAnalyst: freezed == stepAnalyst ? _self._stepAnalyst : stepAnalyst // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepProfiler: freezed == stepProfiler ? _self._stepProfiler : stepProfiler // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepLogician: freezed == stepLogician ? _self._stepLogician : stepLogician // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepFalsifier: freezed == stepFalsifier ? _self._stepFalsifier : stepFalsifier // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepOverseer: freezed == stepOverseer ? _self._stepOverseer : stepOverseer // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepCausal: freezed == stepCausal ? _self._stepCausal : stepCausal // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepDetector: freezed == stepDetector ? _self._stepDetector : stepDetector // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepJudge: freezed == stepJudge ? _self._stepJudge : stepJudge // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepJudgeCognitive: freezed == stepJudgeCognitive ? _self._stepJudgeCognitive : stepJudgeCognitive // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepArchivist: freezed == stepArchivist ? _self._stepArchivist : stepArchivist // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepCoach: freezed == stepCoach ? _self._stepCoach : stepCoach // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepInteraction: freezed == stepInteraction ? _self._stepInteraction : stepInteraction // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,stepPanel: freezed == stepPanel ? _self._stepPanel : stepPanel // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionRejected implements Execution {
  const ExecutionRejected({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.error, this.status = ExecutionStatus.rejected}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionRejected.fromJson(Map<String, dynamic> json) => _$ExecutionRejectedFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  String? error;
@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionRejectedCopyWith<ExecutionRejected> get copyWith => _$ExecutionRejectedCopyWithImpl<ExecutionRejected>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionRejectedToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionRejected&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.error, error) || other.error == error)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),error,status);

@override
String toString() {
  return 'Execution.rejected(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, error: $error, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionRejectedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionRejectedCopyWith(ExecutionRejected value, $Res Function(ExecutionRejected) _then) = _$ExecutionRejectedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, String? error, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionRejectedCopyWithImpl<$Res>
    implements $ExecutionRejectedCopyWith<$Res> {
  _$ExecutionRejectedCopyWithImpl(this._self, this._then);

  final ExecutionRejected _self;
  final $Res Function(ExecutionRejected) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? error = freezed,Object? status = null,}) {
  return _then(ExecutionRejected(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionFailed implements Execution {
  const ExecutionFailed({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.error, this.status = ExecutionStatus.failed}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionFailed.fromJson(Map<String, dynamic> json) => _$ExecutionFailedFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionFailed&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.error, error) || other.error == error)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),error,status);

@override
String toString() {
  return 'Execution.failed(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, error: $error, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionFailedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionFailedCopyWith(ExecutionFailed value, $Res Function(ExecutionFailed) _then) = _$ExecutionFailedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, String? error, ExecutionStatus status
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? error = freezed,Object? status = null,}) {
  return _then(ExecutionFailed(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionInterrupted implements Execution {
  const ExecutionInterrupted({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.error, this.status = ExecutionStatus.interrupted}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionInterrupted.fromJson(Map<String, dynamic> json) => _$ExecutionInterruptedFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  String? error;
@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionInterruptedCopyWith<ExecutionInterrupted> get copyWith => _$ExecutionInterruptedCopyWithImpl<ExecutionInterrupted>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionInterruptedToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionInterrupted&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.error, error) || other.error == error)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),error,status);

@override
String toString() {
  return 'Execution.interrupted(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, error: $error, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionInterruptedCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionInterruptedCopyWith(ExecutionInterrupted value, $Res Function(ExecutionInterrupted) _then) = _$ExecutionInterruptedCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, String? error, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionInterruptedCopyWithImpl<$Res>
    implements $ExecutionInterruptedCopyWith<$Res> {
  _$ExecutionInterruptedCopyWithImpl(this._self, this._then);

  final ExecutionInterrupted _self;
  final $Res Function(ExecutionInterrupted) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? error = freezed,Object? status = null,}) {
  return _then(ExecutionInterrupted(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionCancelling implements Execution {
  const ExecutionCancelling({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.status = ExecutionStatus.cancelling}): _inputs = inputs,_workflowSteps = workflowSteps;
  factory ExecutionCancelling.fromJson(Map<String, dynamic> json) => _$ExecutionCancellingFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
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
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey() final  ExecutionStatus status;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionCancellingCopyWith<ExecutionCancelling> get copyWith => _$ExecutionCancellingCopyWithImpl<ExecutionCancelling>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionCancellingToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionCancelling&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,organizationId,userId,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),status);

@override
String toString() {
  return 'Execution.cancelling(id: $id, createdAt: $createdAt, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, status: $status)';
}


}

/// @nodoc
abstract mixin class $ExecutionCancellingCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionCancellingCopyWith(ExecutionCancelling value, $Res Function(ExecutionCancelling) _then) = _$ExecutionCancellingCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status
});




}
/// @nodoc
class _$ExecutionCancellingCopyWithImpl<$Res>
    implements $ExecutionCancellingCopyWith<$Res> {
  _$ExecutionCancellingCopyWithImpl(this._self, this._then);

  final ExecutionCancelling _self;
  final $Res Function(ExecutionCancelling) _then;

/// Create a copy of Execution
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? status = null,}) {
  return _then(ExecutionCancelling(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,
  ));
}


}

/// @nodoc
@JsonSerializable()

class ExecutionUnknown implements Execution {
  const ExecutionUnknown({@JsonKey(name: 'id') required this.id, @JsonKey(name: 'started_at') required this.createdAt, @JsonKey(name: 'workflow_name') this.workflowName, final  Map<String, dynamic> inputs = const {}, @JsonKey(name: 'current_step_name') this.currentStepName, @JsonKey(name: 'current_step_index') this.currentStepIndex, @JsonKey(name: 'total_steps') this.totalSteps, @JsonKey(name: 'workflow_steps') final  List<String>? workflowSteps, this.status = ExecutionStatus.unknown, final  Map<String, dynamic>? result, this.error}): _inputs = inputs,_workflowSteps = workflowSteps,_result = result;
  factory ExecutionUnknown.fromJson(Map<String, dynamic> json) => _$ExecutionUnknownFromJson(json);

@override@JsonKey(name: 'id') final  String id;
@override@JsonKey(name: 'started_at') final  DateTime createdAt;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
 final  Map<String, dynamic> _inputs;
@override@JsonKey() Map<String, dynamic> get inputs {
  if (_inputs is EqualUnmodifiableMapView) return _inputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputs);
}

@override@JsonKey(name: 'current_step_name') final  String? currentStepName;
@override@JsonKey(name: 'current_step_index') final  int? currentStepIndex;
@override@JsonKey(name: 'total_steps') final  int? totalSteps;
 final  List<String>? _workflowSteps;
@override@JsonKey(name: 'workflow_steps') List<String>? get workflowSteps {
  final value = _workflowSteps;
  if (value == null) return null;
  if (_workflowSteps is EqualUnmodifiableListView) return _workflowSteps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecutionUnknown&&(identical(other.id, id) || other.id == id)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.workflowName, workflowName) || other.workflowName == workflowName)&&const DeepCollectionEquality().equals(other._inputs, _inputs)&&(identical(other.currentStepName, currentStepName) || other.currentStepName == currentStepName)&&(identical(other.currentStepIndex, currentStepIndex) || other.currentStepIndex == currentStepIndex)&&(identical(other.totalSteps, totalSteps) || other.totalSteps == totalSteps)&&const DeepCollectionEquality().equals(other._workflowSteps, _workflowSteps)&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other._result, _result)&&(identical(other.error, error) || other.error == error));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,createdAt,workflowName,const DeepCollectionEquality().hash(_inputs),currentStepName,currentStepIndex,totalSteps,const DeepCollectionEquality().hash(_workflowSteps),status,const DeepCollectionEquality().hash(_result),error);

@override
String toString() {
  return 'Execution.unknown(id: $id, createdAt: $createdAt, workflowName: $workflowName, inputs: $inputs, currentStepName: $currentStepName, currentStepIndex: $currentStepIndex, totalSteps: $totalSteps, workflowSteps: $workflowSteps, status: $status, result: $result, error: $error)';
}


}

/// @nodoc
abstract mixin class $ExecutionUnknownCopyWith<$Res> implements $ExecutionCopyWith<$Res> {
  factory $ExecutionUnknownCopyWith(ExecutionUnknown value, $Res Function(ExecutionUnknown) _then) = _$ExecutionUnknownCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String id,@JsonKey(name: 'started_at') DateTime createdAt,@JsonKey(name: 'workflow_name') String? workflowName, Map<String, dynamic> inputs,@JsonKey(name: 'current_step_name') String? currentStepName,@JsonKey(name: 'current_step_index') int? currentStepIndex,@JsonKey(name: 'total_steps') int? totalSteps,@JsonKey(name: 'workflow_steps') List<String>? workflowSteps, ExecutionStatus status, Map<String, dynamic>? result, String? error
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? createdAt = null,Object? workflowName = freezed,Object? inputs = null,Object? currentStepName = freezed,Object? currentStepIndex = freezed,Object? totalSteps = freezed,Object? workflowSteps = freezed,Object? status = null,Object? result = freezed,Object? error = freezed,}) {
  return _then(ExecutionUnknown(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,inputs: null == inputs ? _self._inputs : inputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,currentStepName: freezed == currentStepName ? _self.currentStepName : currentStepName // ignore: cast_nullable_to_non_nullable
as String?,currentStepIndex: freezed == currentStepIndex ? _self.currentStepIndex : currentStepIndex // ignore: cast_nullable_to_non_nullable
as int?,totalSteps: freezed == totalSteps ? _self.totalSteps : totalSteps // ignore: cast_nullable_to_non_nullable
as int?,workflowSteps: freezed == workflowSteps ? _self._workflowSteps : workflowSteps // ignore: cast_nullable_to_non_nullable
as List<String>?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,result: freezed == result ? _self._result : result // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
