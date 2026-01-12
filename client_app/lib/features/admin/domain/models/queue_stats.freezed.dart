// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'queue_stats.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$QueueStats {

/// Number of jobs currently waiting in the queue.
@JsonKey(name: 'queued_jobs') int get queuedJobs;/// Number of jobs currently being processed by workers.
/// Note: Might be 0 if deep introspection is disabled/mocked.
@JsonKey(name: 'active_jobs') int get activeJobs;/// Number of jobs in the dead-letter queue (failed permanently).
@JsonKey(name: 'dead_jobs') int get deadJobs;
/// Create a copy of QueueStats
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$QueueStatsCopyWith<QueueStats> get copyWith => _$QueueStatsCopyWithImpl<QueueStats>(this as QueueStats, _$identity);

  /// Serializes this QueueStats to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is QueueStats&&(identical(other.queuedJobs, queuedJobs) || other.queuedJobs == queuedJobs)&&(identical(other.activeJobs, activeJobs) || other.activeJobs == activeJobs)&&(identical(other.deadJobs, deadJobs) || other.deadJobs == deadJobs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,queuedJobs,activeJobs,deadJobs);

@override
String toString() {
  return 'QueueStats(queuedJobs: $queuedJobs, activeJobs: $activeJobs, deadJobs: $deadJobs)';
}


}

/// @nodoc
abstract mixin class $QueueStatsCopyWith<$Res>  {
  factory $QueueStatsCopyWith(QueueStats value, $Res Function(QueueStats) _then) = _$QueueStatsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'queued_jobs') int queuedJobs,@JsonKey(name: 'active_jobs') int activeJobs,@JsonKey(name: 'dead_jobs') int deadJobs
});




}
/// @nodoc
class _$QueueStatsCopyWithImpl<$Res>
    implements $QueueStatsCopyWith<$Res> {
  _$QueueStatsCopyWithImpl(this._self, this._then);

  final QueueStats _self;
  final $Res Function(QueueStats) _then;

/// Create a copy of QueueStats
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? queuedJobs = null,Object? activeJobs = null,Object? deadJobs = null,}) {
  return _then(_self.copyWith(
queuedJobs: null == queuedJobs ? _self.queuedJobs : queuedJobs // ignore: cast_nullable_to_non_nullable
as int,activeJobs: null == activeJobs ? _self.activeJobs : activeJobs // ignore: cast_nullable_to_non_nullable
as int,deadJobs: null == deadJobs ? _self.deadJobs : deadJobs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [QueueStats].
extension QueueStatsPatterns on QueueStats {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _QueueStats value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _QueueStats() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _QueueStats value)  $default,){
final _that = this;
switch (_that) {
case _QueueStats():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _QueueStats value)?  $default,){
final _that = this;
switch (_that) {
case _QueueStats() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'queued_jobs')  int queuedJobs, @JsonKey(name: 'active_jobs')  int activeJobs, @JsonKey(name: 'dead_jobs')  int deadJobs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _QueueStats() when $default != null:
return $default(_that.queuedJobs,_that.activeJobs,_that.deadJobs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'queued_jobs')  int queuedJobs, @JsonKey(name: 'active_jobs')  int activeJobs, @JsonKey(name: 'dead_jobs')  int deadJobs)  $default,) {final _that = this;
switch (_that) {
case _QueueStats():
return $default(_that.queuedJobs,_that.activeJobs,_that.deadJobs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'queued_jobs')  int queuedJobs, @JsonKey(name: 'active_jobs')  int activeJobs, @JsonKey(name: 'dead_jobs')  int deadJobs)?  $default,) {final _that = this;
switch (_that) {
case _QueueStats() when $default != null:
return $default(_that.queuedJobs,_that.activeJobs,_that.deadJobs);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _QueueStats implements QueueStats {
  const _QueueStats({@JsonKey(name: 'queued_jobs') required this.queuedJobs, @JsonKey(name: 'active_jobs') required this.activeJobs, @JsonKey(name: 'dead_jobs') required this.deadJobs});
  factory _QueueStats.fromJson(Map<String, dynamic> json) => _$QueueStatsFromJson(json);

/// Number of jobs currently waiting in the queue.
@override@JsonKey(name: 'queued_jobs') final  int queuedJobs;
/// Number of jobs currently being processed by workers.
/// Note: Might be 0 if deep introspection is disabled/mocked.
@override@JsonKey(name: 'active_jobs') final  int activeJobs;
/// Number of jobs in the dead-letter queue (failed permanently).
@override@JsonKey(name: 'dead_jobs') final  int deadJobs;

/// Create a copy of QueueStats
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$QueueStatsCopyWith<_QueueStats> get copyWith => __$QueueStatsCopyWithImpl<_QueueStats>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$QueueStatsToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _QueueStats&&(identical(other.queuedJobs, queuedJobs) || other.queuedJobs == queuedJobs)&&(identical(other.activeJobs, activeJobs) || other.activeJobs == activeJobs)&&(identical(other.deadJobs, deadJobs) || other.deadJobs == deadJobs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,queuedJobs,activeJobs,deadJobs);

@override
String toString() {
  return 'QueueStats(queuedJobs: $queuedJobs, activeJobs: $activeJobs, deadJobs: $deadJobs)';
}


}

/// @nodoc
abstract mixin class _$QueueStatsCopyWith<$Res> implements $QueueStatsCopyWith<$Res> {
  factory _$QueueStatsCopyWith(_QueueStats value, $Res Function(_QueueStats) _then) = __$QueueStatsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'queued_jobs') int queuedJobs,@JsonKey(name: 'active_jobs') int activeJobs,@JsonKey(name: 'dead_jobs') int deadJobs
});




}
/// @nodoc
class __$QueueStatsCopyWithImpl<$Res>
    implements _$QueueStatsCopyWith<$Res> {
  __$QueueStatsCopyWithImpl(this._self, this._then);

  final _QueueStats _self;
  final $Res Function(_QueueStats) _then;

/// Create a copy of QueueStats
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? queuedJobs = null,Object? activeJobs = null,Object? deadJobs = null,}) {
  return _then(_QueueStats(
queuedJobs: null == queuedJobs ? _self.queuedJobs : queuedJobs // ignore: cast_nullable_to_non_nullable
as int,activeJobs: null == activeJobs ? _self.activeJobs : activeJobs // ignore: cast_nullable_to_non_nullable
as int,deadJobs: null == deadJobs ? _self.deadJobs : deadJobs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
