// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_data_v2_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReportDataDto {

@JsonKey(name: 'execution_id') String get executionId;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'global_metrics') ExecutionMetricsDTO get globalMetrics;@JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? get globalSynthesis; List<AtomResultDTO> get results;@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> get hydratedReferences;
/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportDataDtoCopyWith<ReportDataDto> get copyWith => _$ReportDataDtoCopyWithImpl<ReportDataDto>(this as ReportDataDto, _$identity);

  /// Serializes this ReportDataDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportDataDto(executionId: $executionId, workflowId: $workflowId, globalMetrics: $globalMetrics, globalSynthesis: $globalSynthesis, results: $results, hydratedReferences: $hydratedReferences)';
}


}

/// @nodoc
abstract mixin class $ReportDataDtoCopyWith<$Res>  {
  factory $ReportDataDtoCopyWith(ReportDataDto value, $Res Function(ReportDataDto) _then) = _$ReportDataDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'global_metrics') ExecutionMetricsDTO globalMetrics,@JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? globalSynthesis, List<AtomResultDTO> results,@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> hydratedReferences
});


$ExecutionMetricsDTOCopyWith<$Res> get globalMetrics;$GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis;

}
/// @nodoc
class _$ReportDataDtoCopyWithImpl<$Res>
    implements $ReportDataDtoCopyWith<$Res> {
  _$ReportDataDtoCopyWithImpl(this._self, this._then);

  final ReportDataDto _self;
  final $Res Function(ReportDataDto) _then;

/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executionId = null,Object? workflowId = null,Object? globalMetrics = null,Object? globalSynthesis = freezed,Object? results = null,Object? hydratedReferences = null,}) {
  return _then(_self.copyWith(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,globalMetrics: null == globalMetrics ? _self.globalMetrics : globalMetrics // ignore: cast_nullable_to_non_nullable
as ExecutionMetricsDTO,globalSynthesis: freezed == globalSynthesis ? _self.globalSynthesis : globalSynthesis // ignore: cast_nullable_to_non_nullable
as GlobalSynthesisDTO?,results: null == results ? _self.results : results // ignore: cast_nullable_to_non_nullable
as List<AtomResultDTO>,hydratedReferences: null == hydratedReferences ? _self.hydratedReferences : hydratedReferences // ignore: cast_nullable_to_non_nullable
as Map<String, HydratedAtomDTO>,
  ));
}
/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetricsDTOCopyWith<$Res> get globalMetrics {
  
  return $ExecutionMetricsDTOCopyWith<$Res>(_self.globalMetrics, (value) {
    return _then(_self.copyWith(globalMetrics: value));
  });
}/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis {
    if (_self.globalSynthesis == null) {
    return null;
  }

  return $GlobalSynthesisDTOCopyWith<$Res>(_self.globalSynthesis!, (value) {
    return _then(_self.copyWith(globalSynthesis: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportDataDto].
extension ReportDataDtoPatterns on ReportDataDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportDataDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportDataDto value)  $default,){
final _that = this;
switch (_that) {
case _ReportDataDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportDataDto value)?  $default,){
final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'global_metrics')  ExecutionMetricsDTO globalMetrics, @JsonKey(name: 'global_synthesis')  GlobalSynthesisDTO? globalSynthesis,  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references')  Map<String, HydratedAtomDTO> hydratedReferences)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
return $default(_that.executionId,_that.workflowId,_that.globalMetrics,_that.globalSynthesis,_that.results,_that.hydratedReferences);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'global_metrics')  ExecutionMetricsDTO globalMetrics, @JsonKey(name: 'global_synthesis')  GlobalSynthesisDTO? globalSynthesis,  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references')  Map<String, HydratedAtomDTO> hydratedReferences)  $default,) {final _that = this;
switch (_that) {
case _ReportDataDto():
return $default(_that.executionId,_that.workflowId,_that.globalMetrics,_that.globalSynthesis,_that.results,_that.hydratedReferences);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'global_metrics')  ExecutionMetricsDTO globalMetrics, @JsonKey(name: 'global_synthesis')  GlobalSynthesisDTO? globalSynthesis,  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references')  Map<String, HydratedAtomDTO> hydratedReferences)?  $default,) {final _that = this;
switch (_that) {
case _ReportDataDto() when $default != null:
return $default(_that.executionId,_that.workflowId,_that.globalMetrics,_that.globalSynthesis,_that.results,_that.hydratedReferences);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportDataDto implements ReportDataDto {
  const _ReportDataDto({@JsonKey(name: 'execution_id') required this.executionId, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'global_metrics') required this.globalMetrics, @JsonKey(name: 'global_synthesis') this.globalSynthesis, required final  List<AtomResultDTO> results, @JsonKey(name: 'hydrated_references') required final  Map<String, HydratedAtomDTO> hydratedReferences}): _results = results,_hydratedReferences = hydratedReferences;
  factory _ReportDataDto.fromJson(Map<String, dynamic> json) => _$ReportDataDtoFromJson(json);

@override@JsonKey(name: 'execution_id') final  String executionId;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'global_metrics') final  ExecutionMetricsDTO globalMetrics;
@override@JsonKey(name: 'global_synthesis') final  GlobalSynthesisDTO? globalSynthesis;
 final  List<AtomResultDTO> _results;
@override List<AtomResultDTO> get results {
  if (_results is EqualUnmodifiableListView) return _results;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_results);
}

 final  Map<String, HydratedAtomDTO> _hydratedReferences;
@override@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> get hydratedReferences {
  if (_hydratedReferences is EqualUnmodifiableMapView) return _hydratedReferences;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_hydratedReferences);
}


/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportDataDtoCopyWith<_ReportDataDto> get copyWith => __$ReportDataDtoCopyWithImpl<_ReportDataDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportDataDtoToJson(this, );
}



@override
String toString() {
  return 'ReportDataDto(executionId: $executionId, workflowId: $workflowId, globalMetrics: $globalMetrics, globalSynthesis: $globalSynthesis, results: $results, hydratedReferences: $hydratedReferences)';
}


}

/// @nodoc
abstract mixin class _$ReportDataDtoCopyWith<$Res> implements $ReportDataDtoCopyWith<$Res> {
  factory _$ReportDataDtoCopyWith(_ReportDataDto value, $Res Function(_ReportDataDto) _then) = __$ReportDataDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'global_metrics') ExecutionMetricsDTO globalMetrics,@JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? globalSynthesis, List<AtomResultDTO> results,@JsonKey(name: 'hydrated_references') Map<String, HydratedAtomDTO> hydratedReferences
});


@override $ExecutionMetricsDTOCopyWith<$Res> get globalMetrics;@override $GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis;

}
/// @nodoc
class __$ReportDataDtoCopyWithImpl<$Res>
    implements _$ReportDataDtoCopyWith<$Res> {
  __$ReportDataDtoCopyWithImpl(this._self, this._then);

  final _ReportDataDto _self;
  final $Res Function(_ReportDataDto) _then;

/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executionId = null,Object? workflowId = null,Object? globalMetrics = null,Object? globalSynthesis = freezed,Object? results = null,Object? hydratedReferences = null,}) {
  return _then(_ReportDataDto(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,globalMetrics: null == globalMetrics ? _self.globalMetrics : globalMetrics // ignore: cast_nullable_to_non_nullable
as ExecutionMetricsDTO,globalSynthesis: freezed == globalSynthesis ? _self.globalSynthesis : globalSynthesis // ignore: cast_nullable_to_non_nullable
as GlobalSynthesisDTO?,results: null == results ? _self._results : results // ignore: cast_nullable_to_non_nullable
as List<AtomResultDTO>,hydratedReferences: null == hydratedReferences ? _self._hydratedReferences : hydratedReferences // ignore: cast_nullable_to_non_nullable
as Map<String, HydratedAtomDTO>,
  ));
}

/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExecutionMetricsDTOCopyWith<$Res> get globalMetrics {
  
  return $ExecutionMetricsDTOCopyWith<$Res>(_self.globalMetrics, (value) {
    return _then(_self.copyWith(globalMetrics: value));
  });
}/// Create a copy of ReportDataDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GlobalSynthesisDTOCopyWith<$Res>? get globalSynthesis {
    if (_self.globalSynthesis == null) {
    return null;
  }

  return $GlobalSynthesisDTOCopyWith<$Res>(_self.globalSynthesis!, (value) {
    return _then(_self.copyWith(globalSynthesis: value));
  });
}
}

// dart format on
