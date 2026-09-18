// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'execution_summary_snapshot.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExecutionSummarySnapshot {

@JsonKey(name: 'strictness_level') int get strictnessLevel;@JsonKey(name: 'is_ensemble_run') bool get isEnsembleRun;@JsonKey(name: 'is_degraded') bool get isDegraded;@JsonKey(name: 'system_concurrency_snapshot') Map<String, int> get systemConcurrencySnapshot;
/// Create a copy of ExecutionSummarySnapshot
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExecutionSummarySnapshotCopyWith<ExecutionSummarySnapshot> get copyWith => _$ExecutionSummarySnapshotCopyWithImpl<ExecutionSummarySnapshot>(this as ExecutionSummarySnapshot, _$identity);

  /// Serializes this ExecutionSummarySnapshot to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExecutionSummarySnapshot(strictnessLevel: $strictnessLevel, isEnsembleRun: $isEnsembleRun, isDegraded: $isDegraded, systemConcurrencySnapshot: $systemConcurrencySnapshot)';
}


}

/// @nodoc
abstract mixin class $ExecutionSummarySnapshotCopyWith<$Res>  {
  factory $ExecutionSummarySnapshotCopyWith(ExecutionSummarySnapshot value, $Res Function(ExecutionSummarySnapshot) _then) = _$ExecutionSummarySnapshotCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'strictness_level') int strictnessLevel,@JsonKey(name: 'is_ensemble_run') bool isEnsembleRun,@JsonKey(name: 'is_degraded') bool isDegraded,@JsonKey(name: 'system_concurrency_snapshot') Map<String, int> systemConcurrencySnapshot
});




}
/// @nodoc
class _$ExecutionSummarySnapshotCopyWithImpl<$Res>
    implements $ExecutionSummarySnapshotCopyWith<$Res> {
  _$ExecutionSummarySnapshotCopyWithImpl(this._self, this._then);

  final ExecutionSummarySnapshot _self;
  final $Res Function(ExecutionSummarySnapshot) _then;

/// Create a copy of ExecutionSummarySnapshot
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? strictnessLevel = null,Object? isEnsembleRun = null,Object? isDegraded = null,Object? systemConcurrencySnapshot = null,}) {
  return _then(_self.copyWith(
strictnessLevel: null == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int,isEnsembleRun: null == isEnsembleRun ? _self.isEnsembleRun : isEnsembleRun // ignore: cast_nullable_to_non_nullable
as bool,isDegraded: null == isDegraded ? _self.isDegraded : isDegraded // ignore: cast_nullable_to_non_nullable
as bool,systemConcurrencySnapshot: null == systemConcurrencySnapshot ? _self.systemConcurrencySnapshot : systemConcurrencySnapshot // ignore: cast_nullable_to_non_nullable
as Map<String, int>,
  ));
}

}


/// Adds pattern-matching-related methods to [ExecutionSummarySnapshot].
extension ExecutionSummarySnapshotPatterns on ExecutionSummarySnapshot {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExecutionSummarySnapshot value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExecutionSummarySnapshot() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExecutionSummarySnapshot value)  $default,){
final _that = this;
switch (_that) {
case _ExecutionSummarySnapshot():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExecutionSummarySnapshot value)?  $default,){
final _that = this;
switch (_that) {
case _ExecutionSummarySnapshot() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'strictness_level')  int strictnessLevel, @JsonKey(name: 'is_ensemble_run')  bool isEnsembleRun, @JsonKey(name: 'is_degraded')  bool isDegraded, @JsonKey(name: 'system_concurrency_snapshot')  Map<String, int> systemConcurrencySnapshot)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExecutionSummarySnapshot() when $default != null:
return $default(_that.strictnessLevel,_that.isEnsembleRun,_that.isDegraded,_that.systemConcurrencySnapshot);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'strictness_level')  int strictnessLevel, @JsonKey(name: 'is_ensemble_run')  bool isEnsembleRun, @JsonKey(name: 'is_degraded')  bool isDegraded, @JsonKey(name: 'system_concurrency_snapshot')  Map<String, int> systemConcurrencySnapshot)  $default,) {final _that = this;
switch (_that) {
case _ExecutionSummarySnapshot():
return $default(_that.strictnessLevel,_that.isEnsembleRun,_that.isDegraded,_that.systemConcurrencySnapshot);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'strictness_level')  int strictnessLevel, @JsonKey(name: 'is_ensemble_run')  bool isEnsembleRun, @JsonKey(name: 'is_degraded')  bool isDegraded, @JsonKey(name: 'system_concurrency_snapshot')  Map<String, int> systemConcurrencySnapshot)?  $default,) {final _that = this;
switch (_that) {
case _ExecutionSummarySnapshot() when $default != null:
return $default(_that.strictnessLevel,_that.isEnsembleRun,_that.isDegraded,_that.systemConcurrencySnapshot);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExecutionSummarySnapshot extends ExecutionSummarySnapshot {
  const _ExecutionSummarySnapshot({@JsonKey(name: 'strictness_level') this.strictnessLevel = 100, @JsonKey(name: 'is_ensemble_run') this.isEnsembleRun = false, @JsonKey(name: 'is_degraded') this.isDegraded = false, @JsonKey(name: 'system_concurrency_snapshot') final  Map<String, int> systemConcurrencySnapshot = const {}}): _systemConcurrencySnapshot = systemConcurrencySnapshot,super._();
  factory _ExecutionSummarySnapshot.fromJson(Map<String, dynamic> json) => _$ExecutionSummarySnapshotFromJson(json);

@override@JsonKey(name: 'strictness_level') final  int strictnessLevel;
@override@JsonKey(name: 'is_ensemble_run') final  bool isEnsembleRun;
@override@JsonKey(name: 'is_degraded') final  bool isDegraded;
 final  Map<String, int> _systemConcurrencySnapshot;
@override@JsonKey(name: 'system_concurrency_snapshot') Map<String, int> get systemConcurrencySnapshot {
  if (_systemConcurrencySnapshot is EqualUnmodifiableMapView) return _systemConcurrencySnapshot;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_systemConcurrencySnapshot);
}


/// Create a copy of ExecutionSummarySnapshot
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExecutionSummarySnapshotCopyWith<_ExecutionSummarySnapshot> get copyWith => __$ExecutionSummarySnapshotCopyWithImpl<_ExecutionSummarySnapshot>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExecutionSummarySnapshotToJson(this, );
}



@override
String toString() {
  return 'ExecutionSummarySnapshot(strictnessLevel: $strictnessLevel, isEnsembleRun: $isEnsembleRun, isDegraded: $isDegraded, systemConcurrencySnapshot: $systemConcurrencySnapshot)';
}


}

/// @nodoc
abstract mixin class _$ExecutionSummarySnapshotCopyWith<$Res> implements $ExecutionSummarySnapshotCopyWith<$Res> {
  factory _$ExecutionSummarySnapshotCopyWith(_ExecutionSummarySnapshot value, $Res Function(_ExecutionSummarySnapshot) _then) = __$ExecutionSummarySnapshotCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'strictness_level') int strictnessLevel,@JsonKey(name: 'is_ensemble_run') bool isEnsembleRun,@JsonKey(name: 'is_degraded') bool isDegraded,@JsonKey(name: 'system_concurrency_snapshot') Map<String, int> systemConcurrencySnapshot
});




}
/// @nodoc
class __$ExecutionSummarySnapshotCopyWithImpl<$Res>
    implements _$ExecutionSummarySnapshotCopyWith<$Res> {
  __$ExecutionSummarySnapshotCopyWithImpl(this._self, this._then);

  final _ExecutionSummarySnapshot _self;
  final $Res Function(_ExecutionSummarySnapshot) _then;

/// Create a copy of ExecutionSummarySnapshot
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? strictnessLevel = null,Object? isEnsembleRun = null,Object? isDegraded = null,Object? systemConcurrencySnapshot = null,}) {
  return _then(_ExecutionSummarySnapshot(
strictnessLevel: null == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int,isEnsembleRun: null == isEnsembleRun ? _self.isEnsembleRun : isEnsembleRun // ignore: cast_nullable_to_non_nullable
as bool,isDegraded: null == isDegraded ? _self.isDegraded : isDegraded // ignore: cast_nullable_to_non_nullable
as bool,systemConcurrencySnapshot: null == systemConcurrencySnapshot ? _self._systemConcurrencySnapshot : systemConcurrencySnapshot // ignore: cast_nullable_to_non_nullable
as Map<String, int>,
  ));
}


}

// dart format on
