// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'causal_discovery_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CausalNodeDto {

@JsonKey(name: 'node_id') String get nodeId; String get claim;@JsonKey(name: 'source_quote') String? get sourceQuote;@JsonKey(name: 'paragraph_ref') String? get paragraphRef; ExecutionStatus get status;@JsonKey(name: 'blame_parent_ids') List<String> get blameParentIds;@JsonKey(name: 'dependent_child_ids') List<String> get dependentChildIds;@JsonKey(name: 'tda_score') double? get tdaScore;@JsonKey(name: 'tda_level_key') String? get tdaLevelKey;@JsonKey(name: 'source_input_key') String? get sourceInputKey;
/// Create a copy of CausalNodeDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CausalNodeDtoCopyWith<CausalNodeDto> get copyWith => _$CausalNodeDtoCopyWithImpl<CausalNodeDto>(this as CausalNodeDto, _$identity);

  /// Serializes this CausalNodeDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'CausalNodeDto(nodeId: $nodeId, claim: $claim, sourceQuote: $sourceQuote, paragraphRef: $paragraphRef, status: $status, blameParentIds: $blameParentIds, dependentChildIds: $dependentChildIds, tdaScore: $tdaScore, tdaLevelKey: $tdaLevelKey, sourceInputKey: $sourceInputKey)';
}


}

/// @nodoc
abstract mixin class $CausalNodeDtoCopyWith<$Res>  {
  factory $CausalNodeDtoCopyWith(CausalNodeDto value, $Res Function(CausalNodeDto) _then) = _$CausalNodeDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'node_id') String nodeId, String claim,@JsonKey(name: 'source_quote') String? sourceQuote,@JsonKey(name: 'paragraph_ref') String? paragraphRef, ExecutionStatus status,@JsonKey(name: 'blame_parent_ids') List<String> blameParentIds,@JsonKey(name: 'dependent_child_ids') List<String> dependentChildIds,@JsonKey(name: 'tda_score') double? tdaScore,@JsonKey(name: 'tda_level_key') String? tdaLevelKey,@JsonKey(name: 'source_input_key') String? sourceInputKey
});




}
/// @nodoc
class _$CausalNodeDtoCopyWithImpl<$Res>
    implements $CausalNodeDtoCopyWith<$Res> {
  _$CausalNodeDtoCopyWithImpl(this._self, this._then);

  final CausalNodeDto _self;
  final $Res Function(CausalNodeDto) _then;

/// Create a copy of CausalNodeDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nodeId = null,Object? claim = null,Object? sourceQuote = freezed,Object? paragraphRef = freezed,Object? status = null,Object? blameParentIds = null,Object? dependentChildIds = null,Object? tdaScore = freezed,Object? tdaLevelKey = freezed,Object? sourceInputKey = freezed,}) {
  return _then(_self.copyWith(
nodeId: null == nodeId ? _self.nodeId : nodeId // ignore: cast_nullable_to_non_nullable
as String,claim: null == claim ? _self.claim : claim // ignore: cast_nullable_to_non_nullable
as String,sourceQuote: freezed == sourceQuote ? _self.sourceQuote : sourceQuote // ignore: cast_nullable_to_non_nullable
as String?,paragraphRef: freezed == paragraphRef ? _self.paragraphRef : paragraphRef // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,blameParentIds: null == blameParentIds ? _self.blameParentIds : blameParentIds // ignore: cast_nullable_to_non_nullable
as List<String>,dependentChildIds: null == dependentChildIds ? _self.dependentChildIds : dependentChildIds // ignore: cast_nullable_to_non_nullable
as List<String>,tdaScore: freezed == tdaScore ? _self.tdaScore : tdaScore // ignore: cast_nullable_to_non_nullable
as double?,tdaLevelKey: freezed == tdaLevelKey ? _self.tdaLevelKey : tdaLevelKey // ignore: cast_nullable_to_non_nullable
as String?,sourceInputKey: freezed == sourceInputKey ? _self.sourceInputKey : sourceInputKey // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [CausalNodeDto].
extension CausalNodeDtoPatterns on CausalNodeDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CausalNodeDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CausalNodeDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CausalNodeDto value)  $default,){
final _that = this;
switch (_that) {
case _CausalNodeDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CausalNodeDto value)?  $default,){
final _that = this;
switch (_that) {
case _CausalNodeDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'node_id')  String nodeId,  String claim, @JsonKey(name: 'source_quote')  String? sourceQuote, @JsonKey(name: 'paragraph_ref')  String? paragraphRef,  ExecutionStatus status, @JsonKey(name: 'blame_parent_ids')  List<String> blameParentIds, @JsonKey(name: 'dependent_child_ids')  List<String> dependentChildIds, @JsonKey(name: 'tda_score')  double? tdaScore, @JsonKey(name: 'tda_level_key')  String? tdaLevelKey, @JsonKey(name: 'source_input_key')  String? sourceInputKey)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CausalNodeDto() when $default != null:
return $default(_that.nodeId,_that.claim,_that.sourceQuote,_that.paragraphRef,_that.status,_that.blameParentIds,_that.dependentChildIds,_that.tdaScore,_that.tdaLevelKey,_that.sourceInputKey);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'node_id')  String nodeId,  String claim, @JsonKey(name: 'source_quote')  String? sourceQuote, @JsonKey(name: 'paragraph_ref')  String? paragraphRef,  ExecutionStatus status, @JsonKey(name: 'blame_parent_ids')  List<String> blameParentIds, @JsonKey(name: 'dependent_child_ids')  List<String> dependentChildIds, @JsonKey(name: 'tda_score')  double? tdaScore, @JsonKey(name: 'tda_level_key')  String? tdaLevelKey, @JsonKey(name: 'source_input_key')  String? sourceInputKey)  $default,) {final _that = this;
switch (_that) {
case _CausalNodeDto():
return $default(_that.nodeId,_that.claim,_that.sourceQuote,_that.paragraphRef,_that.status,_that.blameParentIds,_that.dependentChildIds,_that.tdaScore,_that.tdaLevelKey,_that.sourceInputKey);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'node_id')  String nodeId,  String claim, @JsonKey(name: 'source_quote')  String? sourceQuote, @JsonKey(name: 'paragraph_ref')  String? paragraphRef,  ExecutionStatus status, @JsonKey(name: 'blame_parent_ids')  List<String> blameParentIds, @JsonKey(name: 'dependent_child_ids')  List<String> dependentChildIds, @JsonKey(name: 'tda_score')  double? tdaScore, @JsonKey(name: 'tda_level_key')  String? tdaLevelKey, @JsonKey(name: 'source_input_key')  String? sourceInputKey)?  $default,) {final _that = this;
switch (_that) {
case _CausalNodeDto() when $default != null:
return $default(_that.nodeId,_that.claim,_that.sourceQuote,_that.paragraphRef,_that.status,_that.blameParentIds,_that.dependentChildIds,_that.tdaScore,_that.tdaLevelKey,_that.sourceInputKey);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _CausalNodeDto implements CausalNodeDto {
  const _CausalNodeDto({@JsonKey(name: 'node_id') required this.nodeId, required this.claim, @JsonKey(name: 'source_quote') this.sourceQuote, @JsonKey(name: 'paragraph_ref') this.paragraphRef, required this.status, @JsonKey(name: 'blame_parent_ids') final  List<String> blameParentIds = const [], @JsonKey(name: 'dependent_child_ids') final  List<String> dependentChildIds = const [], @JsonKey(name: 'tda_score') this.tdaScore, @JsonKey(name: 'tda_level_key') this.tdaLevelKey, @JsonKey(name: 'source_input_key') this.sourceInputKey = null}): _blameParentIds = blameParentIds,_dependentChildIds = dependentChildIds;
  factory _CausalNodeDto.fromJson(Map<String, dynamic> json) => _$CausalNodeDtoFromJson(json);

@override@JsonKey(name: 'node_id') final  String nodeId;
@override final  String claim;
@override@JsonKey(name: 'source_quote') final  String? sourceQuote;
@override@JsonKey(name: 'paragraph_ref') final  String? paragraphRef;
@override final  ExecutionStatus status;
 final  List<String> _blameParentIds;
@override@JsonKey(name: 'blame_parent_ids') List<String> get blameParentIds {
  if (_blameParentIds is EqualUnmodifiableListView) return _blameParentIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_blameParentIds);
}

 final  List<String> _dependentChildIds;
@override@JsonKey(name: 'dependent_child_ids') List<String> get dependentChildIds {
  if (_dependentChildIds is EqualUnmodifiableListView) return _dependentChildIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dependentChildIds);
}

@override@JsonKey(name: 'tda_score') final  double? tdaScore;
@override@JsonKey(name: 'tda_level_key') final  String? tdaLevelKey;
@override@JsonKey(name: 'source_input_key') final  String? sourceInputKey;

/// Create a copy of CausalNodeDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CausalNodeDtoCopyWith<_CausalNodeDto> get copyWith => __$CausalNodeDtoCopyWithImpl<_CausalNodeDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CausalNodeDtoToJson(this, );
}



@override
String toString() {
  return 'CausalNodeDto(nodeId: $nodeId, claim: $claim, sourceQuote: $sourceQuote, paragraphRef: $paragraphRef, status: $status, blameParentIds: $blameParentIds, dependentChildIds: $dependentChildIds, tdaScore: $tdaScore, tdaLevelKey: $tdaLevelKey, sourceInputKey: $sourceInputKey)';
}


}

/// @nodoc
abstract mixin class _$CausalNodeDtoCopyWith<$Res> implements $CausalNodeDtoCopyWith<$Res> {
  factory _$CausalNodeDtoCopyWith(_CausalNodeDto value, $Res Function(_CausalNodeDto) _then) = __$CausalNodeDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'node_id') String nodeId, String claim,@JsonKey(name: 'source_quote') String? sourceQuote,@JsonKey(name: 'paragraph_ref') String? paragraphRef, ExecutionStatus status,@JsonKey(name: 'blame_parent_ids') List<String> blameParentIds,@JsonKey(name: 'dependent_child_ids') List<String> dependentChildIds,@JsonKey(name: 'tda_score') double? tdaScore,@JsonKey(name: 'tda_level_key') String? tdaLevelKey,@JsonKey(name: 'source_input_key') String? sourceInputKey
});




}
/// @nodoc
class __$CausalNodeDtoCopyWithImpl<$Res>
    implements _$CausalNodeDtoCopyWith<$Res> {
  __$CausalNodeDtoCopyWithImpl(this._self, this._then);

  final _CausalNodeDto _self;
  final $Res Function(_CausalNodeDto) _then;

/// Create a copy of CausalNodeDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nodeId = null,Object? claim = null,Object? sourceQuote = freezed,Object? paragraphRef = freezed,Object? status = null,Object? blameParentIds = null,Object? dependentChildIds = null,Object? tdaScore = freezed,Object? tdaLevelKey = freezed,Object? sourceInputKey = freezed,}) {
  return _then(_CausalNodeDto(
nodeId: null == nodeId ? _self.nodeId : nodeId // ignore: cast_nullable_to_non_nullable
as String,claim: null == claim ? _self.claim : claim // ignore: cast_nullable_to_non_nullable
as String,sourceQuote: freezed == sourceQuote ? _self.sourceQuote : sourceQuote // ignore: cast_nullable_to_non_nullable
as String?,paragraphRef: freezed == paragraphRef ? _self.paragraphRef : paragraphRef // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,blameParentIds: null == blameParentIds ? _self._blameParentIds : blameParentIds // ignore: cast_nullable_to_non_nullable
as List<String>,dependentChildIds: null == dependentChildIds ? _self._dependentChildIds : dependentChildIds // ignore: cast_nullable_to_non_nullable
as List<String>,tdaScore: freezed == tdaScore ? _self.tdaScore : tdaScore // ignore: cast_nullable_to_non_nullable
as double?,tdaLevelKey: freezed == tdaLevelKey ? _self.tdaLevelKey : tdaLevelKey // ignore: cast_nullable_to_non_nullable
as String?,sourceInputKey: freezed == sourceInputKey ? _self.sourceInputKey : sourceInputKey // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$CausalEdgeDto {

@JsonKey(name: 'source_id') String get sourceId;@JsonKey(name: 'target_id') String get targetId; String get reasoning;
/// Create a copy of CausalEdgeDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CausalEdgeDtoCopyWith<CausalEdgeDto> get copyWith => _$CausalEdgeDtoCopyWithImpl<CausalEdgeDto>(this as CausalEdgeDto, _$identity);

  /// Serializes this CausalEdgeDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'CausalEdgeDto(sourceId: $sourceId, targetId: $targetId, reasoning: $reasoning)';
}


}

/// @nodoc
abstract mixin class $CausalEdgeDtoCopyWith<$Res>  {
  factory $CausalEdgeDtoCopyWith(CausalEdgeDto value, $Res Function(CausalEdgeDto) _then) = _$CausalEdgeDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'source_id') String sourceId,@JsonKey(name: 'target_id') String targetId, String reasoning
});




}
/// @nodoc
class _$CausalEdgeDtoCopyWithImpl<$Res>
    implements $CausalEdgeDtoCopyWith<$Res> {
  _$CausalEdgeDtoCopyWithImpl(this._self, this._then);

  final CausalEdgeDto _self;
  final $Res Function(CausalEdgeDto) _then;

/// Create a copy of CausalEdgeDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sourceId = null,Object? targetId = null,Object? reasoning = null,}) {
  return _then(_self.copyWith(
sourceId: null == sourceId ? _self.sourceId : sourceId // ignore: cast_nullable_to_non_nullable
as String,targetId: null == targetId ? _self.targetId : targetId // ignore: cast_nullable_to_non_nullable
as String,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [CausalEdgeDto].
extension CausalEdgeDtoPatterns on CausalEdgeDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CausalEdgeDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CausalEdgeDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CausalEdgeDto value)  $default,){
final _that = this;
switch (_that) {
case _CausalEdgeDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CausalEdgeDto value)?  $default,){
final _that = this;
switch (_that) {
case _CausalEdgeDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'source_id')  String sourceId, @JsonKey(name: 'target_id')  String targetId,  String reasoning)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CausalEdgeDto() when $default != null:
return $default(_that.sourceId,_that.targetId,_that.reasoning);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'source_id')  String sourceId, @JsonKey(name: 'target_id')  String targetId,  String reasoning)  $default,) {final _that = this;
switch (_that) {
case _CausalEdgeDto():
return $default(_that.sourceId,_that.targetId,_that.reasoning);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'source_id')  String sourceId, @JsonKey(name: 'target_id')  String targetId,  String reasoning)?  $default,) {final _that = this;
switch (_that) {
case _CausalEdgeDto() when $default != null:
return $default(_that.sourceId,_that.targetId,_that.reasoning);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _CausalEdgeDto implements CausalEdgeDto {
  const _CausalEdgeDto({@JsonKey(name: 'source_id') required this.sourceId, @JsonKey(name: 'target_id') required this.targetId, required this.reasoning});
  factory _CausalEdgeDto.fromJson(Map<String, dynamic> json) => _$CausalEdgeDtoFromJson(json);

@override@JsonKey(name: 'source_id') final  String sourceId;
@override@JsonKey(name: 'target_id') final  String targetId;
@override final  String reasoning;

/// Create a copy of CausalEdgeDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CausalEdgeDtoCopyWith<_CausalEdgeDto> get copyWith => __$CausalEdgeDtoCopyWithImpl<_CausalEdgeDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CausalEdgeDtoToJson(this, );
}



@override
String toString() {
  return 'CausalEdgeDto(sourceId: $sourceId, targetId: $targetId, reasoning: $reasoning)';
}


}

/// @nodoc
abstract mixin class _$CausalEdgeDtoCopyWith<$Res> implements $CausalEdgeDtoCopyWith<$Res> {
  factory _$CausalEdgeDtoCopyWith(_CausalEdgeDto value, $Res Function(_CausalEdgeDto) _then) = __$CausalEdgeDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'source_id') String sourceId,@JsonKey(name: 'target_id') String targetId, String reasoning
});




}
/// @nodoc
class __$CausalEdgeDtoCopyWithImpl<$Res>
    implements _$CausalEdgeDtoCopyWith<$Res> {
  __$CausalEdgeDtoCopyWithImpl(this._self, this._then);

  final _CausalEdgeDto _self;
  final $Res Function(_CausalEdgeDto) _then;

/// Create a copy of CausalEdgeDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sourceId = null,Object? targetId = null,Object? reasoning = null,}) {
  return _then(_CausalEdgeDto(
sourceId: null == sourceId ? _self.sourceId : sourceId // ignore: cast_nullable_to_non_nullable
as String,targetId: null == targetId ? _self.targetId : targetId // ignore: cast_nullable_to_non_nullable
as String,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CausalRootCauseDiagnosisDto {

@JsonKey(name: 'failing_node_id') String get failingNodeId;@JsonKey(name: 'root_cause_parent_id') String get rootCauseParentId;@JsonKey(name: 'paragraph_ref') String get paragraphRef; String get explanation;@JsonKey(name: 'penalty_points') double get penaltyPoints;@JsonKey(name: 'root_cause_type') CausalRootCauseType get rootCauseType;
/// Create a copy of CausalRootCauseDiagnosisDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CausalRootCauseDiagnosisDtoCopyWith<CausalRootCauseDiagnosisDto> get copyWith => _$CausalRootCauseDiagnosisDtoCopyWithImpl<CausalRootCauseDiagnosisDto>(this as CausalRootCauseDiagnosisDto, _$identity);

  /// Serializes this CausalRootCauseDiagnosisDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'CausalRootCauseDiagnosisDto(failingNodeId: $failingNodeId, rootCauseParentId: $rootCauseParentId, paragraphRef: $paragraphRef, explanation: $explanation, penaltyPoints: $penaltyPoints, rootCauseType: $rootCauseType)';
}


}

/// @nodoc
abstract mixin class $CausalRootCauseDiagnosisDtoCopyWith<$Res>  {
  factory $CausalRootCauseDiagnosisDtoCopyWith(CausalRootCauseDiagnosisDto value, $Res Function(CausalRootCauseDiagnosisDto) _then) = _$CausalRootCauseDiagnosisDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'failing_node_id') String failingNodeId,@JsonKey(name: 'root_cause_parent_id') String rootCauseParentId,@JsonKey(name: 'paragraph_ref') String paragraphRef, String explanation,@JsonKey(name: 'penalty_points') double penaltyPoints,@JsonKey(name: 'root_cause_type') CausalRootCauseType rootCauseType
});




}
/// @nodoc
class _$CausalRootCauseDiagnosisDtoCopyWithImpl<$Res>
    implements $CausalRootCauseDiagnosisDtoCopyWith<$Res> {
  _$CausalRootCauseDiagnosisDtoCopyWithImpl(this._self, this._then);

  final CausalRootCauseDiagnosisDto _self;
  final $Res Function(CausalRootCauseDiagnosisDto) _then;

/// Create a copy of CausalRootCauseDiagnosisDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? failingNodeId = null,Object? rootCauseParentId = null,Object? paragraphRef = null,Object? explanation = null,Object? penaltyPoints = null,Object? rootCauseType = null,}) {
  return _then(_self.copyWith(
failingNodeId: null == failingNodeId ? _self.failingNodeId : failingNodeId // ignore: cast_nullable_to_non_nullable
as String,rootCauseParentId: null == rootCauseParentId ? _self.rootCauseParentId : rootCauseParentId // ignore: cast_nullable_to_non_nullable
as String,paragraphRef: null == paragraphRef ? _self.paragraphRef : paragraphRef // ignore: cast_nullable_to_non_nullable
as String,explanation: null == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String,penaltyPoints: null == penaltyPoints ? _self.penaltyPoints : penaltyPoints // ignore: cast_nullable_to_non_nullable
as double,rootCauseType: null == rootCauseType ? _self.rootCauseType : rootCauseType // ignore: cast_nullable_to_non_nullable
as CausalRootCauseType,
  ));
}

}


/// Adds pattern-matching-related methods to [CausalRootCauseDiagnosisDto].
extension CausalRootCauseDiagnosisDtoPatterns on CausalRootCauseDiagnosisDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CausalRootCauseDiagnosisDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CausalRootCauseDiagnosisDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CausalRootCauseDiagnosisDto value)  $default,){
final _that = this;
switch (_that) {
case _CausalRootCauseDiagnosisDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CausalRootCauseDiagnosisDto value)?  $default,){
final _that = this;
switch (_that) {
case _CausalRootCauseDiagnosisDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'failing_node_id')  String failingNodeId, @JsonKey(name: 'root_cause_parent_id')  String rootCauseParentId, @JsonKey(name: 'paragraph_ref')  String paragraphRef,  String explanation, @JsonKey(name: 'penalty_points')  double penaltyPoints, @JsonKey(name: 'root_cause_type')  CausalRootCauseType rootCauseType)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CausalRootCauseDiagnosisDto() when $default != null:
return $default(_that.failingNodeId,_that.rootCauseParentId,_that.paragraphRef,_that.explanation,_that.penaltyPoints,_that.rootCauseType);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'failing_node_id')  String failingNodeId, @JsonKey(name: 'root_cause_parent_id')  String rootCauseParentId, @JsonKey(name: 'paragraph_ref')  String paragraphRef,  String explanation, @JsonKey(name: 'penalty_points')  double penaltyPoints, @JsonKey(name: 'root_cause_type')  CausalRootCauseType rootCauseType)  $default,) {final _that = this;
switch (_that) {
case _CausalRootCauseDiagnosisDto():
return $default(_that.failingNodeId,_that.rootCauseParentId,_that.paragraphRef,_that.explanation,_that.penaltyPoints,_that.rootCauseType);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'failing_node_id')  String failingNodeId, @JsonKey(name: 'root_cause_parent_id')  String rootCauseParentId, @JsonKey(name: 'paragraph_ref')  String paragraphRef,  String explanation, @JsonKey(name: 'penalty_points')  double penaltyPoints, @JsonKey(name: 'root_cause_type')  CausalRootCauseType rootCauseType)?  $default,) {final _that = this;
switch (_that) {
case _CausalRootCauseDiagnosisDto() when $default != null:
return $default(_that.failingNodeId,_that.rootCauseParentId,_that.paragraphRef,_that.explanation,_that.penaltyPoints,_that.rootCauseType);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _CausalRootCauseDiagnosisDto implements CausalRootCauseDiagnosisDto {
  const _CausalRootCauseDiagnosisDto({@JsonKey(name: 'failing_node_id') required this.failingNodeId, @JsonKey(name: 'root_cause_parent_id') required this.rootCauseParentId, @JsonKey(name: 'paragraph_ref') required this.paragraphRef, required this.explanation, @JsonKey(name: 'penalty_points') required this.penaltyPoints, @JsonKey(name: 'root_cause_type') this.rootCauseType = CausalRootCauseType.nodeFailure});
  factory _CausalRootCauseDiagnosisDto.fromJson(Map<String, dynamic> json) => _$CausalRootCauseDiagnosisDtoFromJson(json);

@override@JsonKey(name: 'failing_node_id') final  String failingNodeId;
@override@JsonKey(name: 'root_cause_parent_id') final  String rootCauseParentId;
@override@JsonKey(name: 'paragraph_ref') final  String paragraphRef;
@override final  String explanation;
@override@JsonKey(name: 'penalty_points') final  double penaltyPoints;
@override@JsonKey(name: 'root_cause_type') final  CausalRootCauseType rootCauseType;

/// Create a copy of CausalRootCauseDiagnosisDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CausalRootCauseDiagnosisDtoCopyWith<_CausalRootCauseDiagnosisDto> get copyWith => __$CausalRootCauseDiagnosisDtoCopyWithImpl<_CausalRootCauseDiagnosisDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CausalRootCauseDiagnosisDtoToJson(this, );
}



@override
String toString() {
  return 'CausalRootCauseDiagnosisDto(failingNodeId: $failingNodeId, rootCauseParentId: $rootCauseParentId, paragraphRef: $paragraphRef, explanation: $explanation, penaltyPoints: $penaltyPoints, rootCauseType: $rootCauseType)';
}


}

/// @nodoc
abstract mixin class _$CausalRootCauseDiagnosisDtoCopyWith<$Res> implements $CausalRootCauseDiagnosisDtoCopyWith<$Res> {
  factory _$CausalRootCauseDiagnosisDtoCopyWith(_CausalRootCauseDiagnosisDto value, $Res Function(_CausalRootCauseDiagnosisDto) _then) = __$CausalRootCauseDiagnosisDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'failing_node_id') String failingNodeId,@JsonKey(name: 'root_cause_parent_id') String rootCauseParentId,@JsonKey(name: 'paragraph_ref') String paragraphRef, String explanation,@JsonKey(name: 'penalty_points') double penaltyPoints,@JsonKey(name: 'root_cause_type') CausalRootCauseType rootCauseType
});




}
/// @nodoc
class __$CausalRootCauseDiagnosisDtoCopyWithImpl<$Res>
    implements _$CausalRootCauseDiagnosisDtoCopyWith<$Res> {
  __$CausalRootCauseDiagnosisDtoCopyWithImpl(this._self, this._then);

  final _CausalRootCauseDiagnosisDto _self;
  final $Res Function(_CausalRootCauseDiagnosisDto) _then;

/// Create a copy of CausalRootCauseDiagnosisDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? failingNodeId = null,Object? rootCauseParentId = null,Object? paragraphRef = null,Object? explanation = null,Object? penaltyPoints = null,Object? rootCauseType = null,}) {
  return _then(_CausalRootCauseDiagnosisDto(
failingNodeId: null == failingNodeId ? _self.failingNodeId : failingNodeId // ignore: cast_nullable_to_non_nullable
as String,rootCauseParentId: null == rootCauseParentId ? _self.rootCauseParentId : rootCauseParentId // ignore: cast_nullable_to_non_nullable
as String,paragraphRef: null == paragraphRef ? _self.paragraphRef : paragraphRef // ignore: cast_nullable_to_non_nullable
as String,explanation: null == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String,penaltyPoints: null == penaltyPoints ? _self.penaltyPoints : penaltyPoints // ignore: cast_nullable_to_non_nullable
as double,rootCauseType: null == rootCauseType ? _self.rootCauseType : rootCauseType // ignore: cast_nullable_to_non_nullable
as CausalRootCauseType,
  ));
}


}


/// @nodoc
mixin _$AntiFluffAuditDto {

@JsonKey(name: 'isolated_concept_count') int get isolatedConceptCount;@JsonKey(name: 'cycle_detected') bool get cycleDetected;@JsonKey(name: 'unsupported_claims_count') int get unsupportedClaimsCount;@JsonKey(name: 'logical_cohesion_score') double get logicalCohesionScore;@JsonKey(name: 'detected_hollow_terms') List<String> get detectedHollowTerms;
/// Create a copy of AntiFluffAuditDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AntiFluffAuditDtoCopyWith<AntiFluffAuditDto> get copyWith => _$AntiFluffAuditDtoCopyWithImpl<AntiFluffAuditDto>(this as AntiFluffAuditDto, _$identity);

  /// Serializes this AntiFluffAuditDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'AntiFluffAuditDto(isolatedConceptCount: $isolatedConceptCount, cycleDetected: $cycleDetected, unsupportedClaimsCount: $unsupportedClaimsCount, logicalCohesionScore: $logicalCohesionScore, detectedHollowTerms: $detectedHollowTerms)';
}


}

/// @nodoc
abstract mixin class $AntiFluffAuditDtoCopyWith<$Res>  {
  factory $AntiFluffAuditDtoCopyWith(AntiFluffAuditDto value, $Res Function(AntiFluffAuditDto) _then) = _$AntiFluffAuditDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'isolated_concept_count') int isolatedConceptCount,@JsonKey(name: 'cycle_detected') bool cycleDetected,@JsonKey(name: 'unsupported_claims_count') int unsupportedClaimsCount,@JsonKey(name: 'logical_cohesion_score') double logicalCohesionScore,@JsonKey(name: 'detected_hollow_terms') List<String> detectedHollowTerms
});




}
/// @nodoc
class _$AntiFluffAuditDtoCopyWithImpl<$Res>
    implements $AntiFluffAuditDtoCopyWith<$Res> {
  _$AntiFluffAuditDtoCopyWithImpl(this._self, this._then);

  final AntiFluffAuditDto _self;
  final $Res Function(AntiFluffAuditDto) _then;

/// Create a copy of AntiFluffAuditDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? isolatedConceptCount = null,Object? cycleDetected = null,Object? unsupportedClaimsCount = null,Object? logicalCohesionScore = null,Object? detectedHollowTerms = null,}) {
  return _then(_self.copyWith(
isolatedConceptCount: null == isolatedConceptCount ? _self.isolatedConceptCount : isolatedConceptCount // ignore: cast_nullable_to_non_nullable
as int,cycleDetected: null == cycleDetected ? _self.cycleDetected : cycleDetected // ignore: cast_nullable_to_non_nullable
as bool,unsupportedClaimsCount: null == unsupportedClaimsCount ? _self.unsupportedClaimsCount : unsupportedClaimsCount // ignore: cast_nullable_to_non_nullable
as int,logicalCohesionScore: null == logicalCohesionScore ? _self.logicalCohesionScore : logicalCohesionScore // ignore: cast_nullable_to_non_nullable
as double,detectedHollowTerms: null == detectedHollowTerms ? _self.detectedHollowTerms : detectedHollowTerms // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [AntiFluffAuditDto].
extension AntiFluffAuditDtoPatterns on AntiFluffAuditDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AntiFluffAuditDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AntiFluffAuditDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AntiFluffAuditDto value)  $default,){
final _that = this;
switch (_that) {
case _AntiFluffAuditDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AntiFluffAuditDto value)?  $default,){
final _that = this;
switch (_that) {
case _AntiFluffAuditDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'isolated_concept_count')  int isolatedConceptCount, @JsonKey(name: 'cycle_detected')  bool cycleDetected, @JsonKey(name: 'unsupported_claims_count')  int unsupportedClaimsCount, @JsonKey(name: 'logical_cohesion_score')  double logicalCohesionScore, @JsonKey(name: 'detected_hollow_terms')  List<String> detectedHollowTerms)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AntiFluffAuditDto() when $default != null:
return $default(_that.isolatedConceptCount,_that.cycleDetected,_that.unsupportedClaimsCount,_that.logicalCohesionScore,_that.detectedHollowTerms);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'isolated_concept_count')  int isolatedConceptCount, @JsonKey(name: 'cycle_detected')  bool cycleDetected, @JsonKey(name: 'unsupported_claims_count')  int unsupportedClaimsCount, @JsonKey(name: 'logical_cohesion_score')  double logicalCohesionScore, @JsonKey(name: 'detected_hollow_terms')  List<String> detectedHollowTerms)  $default,) {final _that = this;
switch (_that) {
case _AntiFluffAuditDto():
return $default(_that.isolatedConceptCount,_that.cycleDetected,_that.unsupportedClaimsCount,_that.logicalCohesionScore,_that.detectedHollowTerms);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'isolated_concept_count')  int isolatedConceptCount, @JsonKey(name: 'cycle_detected')  bool cycleDetected, @JsonKey(name: 'unsupported_claims_count')  int unsupportedClaimsCount, @JsonKey(name: 'logical_cohesion_score')  double logicalCohesionScore, @JsonKey(name: 'detected_hollow_terms')  List<String> detectedHollowTerms)?  $default,) {final _that = this;
switch (_that) {
case _AntiFluffAuditDto() when $default != null:
return $default(_that.isolatedConceptCount,_that.cycleDetected,_that.unsupportedClaimsCount,_that.logicalCohesionScore,_that.detectedHollowTerms);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _AntiFluffAuditDto implements AntiFluffAuditDto {
  const _AntiFluffAuditDto({@JsonKey(name: 'isolated_concept_count') required this.isolatedConceptCount, @JsonKey(name: 'cycle_detected') required this.cycleDetected, @JsonKey(name: 'unsupported_claims_count') required this.unsupportedClaimsCount, @JsonKey(name: 'logical_cohesion_score') required this.logicalCohesionScore, @JsonKey(name: 'detected_hollow_terms') final  List<String> detectedHollowTerms = const []}): _detectedHollowTerms = detectedHollowTerms;
  factory _AntiFluffAuditDto.fromJson(Map<String, dynamic> json) => _$AntiFluffAuditDtoFromJson(json);

@override@JsonKey(name: 'isolated_concept_count') final  int isolatedConceptCount;
@override@JsonKey(name: 'cycle_detected') final  bool cycleDetected;
@override@JsonKey(name: 'unsupported_claims_count') final  int unsupportedClaimsCount;
@override@JsonKey(name: 'logical_cohesion_score') final  double logicalCohesionScore;
 final  List<String> _detectedHollowTerms;
@override@JsonKey(name: 'detected_hollow_terms') List<String> get detectedHollowTerms {
  if (_detectedHollowTerms is EqualUnmodifiableListView) return _detectedHollowTerms;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_detectedHollowTerms);
}


/// Create a copy of AntiFluffAuditDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AntiFluffAuditDtoCopyWith<_AntiFluffAuditDto> get copyWith => __$AntiFluffAuditDtoCopyWithImpl<_AntiFluffAuditDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AntiFluffAuditDtoToJson(this, );
}



@override
String toString() {
  return 'AntiFluffAuditDto(isolatedConceptCount: $isolatedConceptCount, cycleDetected: $cycleDetected, unsupportedClaimsCount: $unsupportedClaimsCount, logicalCohesionScore: $logicalCohesionScore, detectedHollowTerms: $detectedHollowTerms)';
}


}

/// @nodoc
abstract mixin class _$AntiFluffAuditDtoCopyWith<$Res> implements $AntiFluffAuditDtoCopyWith<$Res> {
  factory _$AntiFluffAuditDtoCopyWith(_AntiFluffAuditDto value, $Res Function(_AntiFluffAuditDto) _then) = __$AntiFluffAuditDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'isolated_concept_count') int isolatedConceptCount,@JsonKey(name: 'cycle_detected') bool cycleDetected,@JsonKey(name: 'unsupported_claims_count') int unsupportedClaimsCount,@JsonKey(name: 'logical_cohesion_score') double logicalCohesionScore,@JsonKey(name: 'detected_hollow_terms') List<String> detectedHollowTerms
});




}
/// @nodoc
class __$AntiFluffAuditDtoCopyWithImpl<$Res>
    implements _$AntiFluffAuditDtoCopyWith<$Res> {
  __$AntiFluffAuditDtoCopyWithImpl(this._self, this._then);

  final _AntiFluffAuditDto _self;
  final $Res Function(_AntiFluffAuditDto) _then;

/// Create a copy of AntiFluffAuditDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? isolatedConceptCount = null,Object? cycleDetected = null,Object? unsupportedClaimsCount = null,Object? logicalCohesionScore = null,Object? detectedHollowTerms = null,}) {
  return _then(_AntiFluffAuditDto(
isolatedConceptCount: null == isolatedConceptCount ? _self.isolatedConceptCount : isolatedConceptCount // ignore: cast_nullable_to_non_nullable
as int,cycleDetected: null == cycleDetected ? _self.cycleDetected : cycleDetected // ignore: cast_nullable_to_non_nullable
as bool,unsupportedClaimsCount: null == unsupportedClaimsCount ? _self.unsupportedClaimsCount : unsupportedClaimsCount // ignore: cast_nullable_to_non_nullable
as int,logicalCohesionScore: null == logicalCohesionScore ? _self.logicalCohesionScore : logicalCohesionScore // ignore: cast_nullable_to_non_nullable
as double,detectedHollowTerms: null == detectedHollowTerms ? _self._detectedHollowTerms : detectedHollowTerms // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}


/// @nodoc
mixin _$PrescriptiveRemediationDto {

@JsonKey(name: 'target_node_id') String get targetNodeId;@JsonKey(name: 'required_action') String get requiredAction;@JsonKey(name: 'unlocks_node_ids') List<String> get unlocksNodeIds;@JsonKey(name: 'potential_score_impact') double get potentialScoreImpact;
/// Create a copy of PrescriptiveRemediationDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PrescriptiveRemediationDtoCopyWith<PrescriptiveRemediationDto> get copyWith => _$PrescriptiveRemediationDtoCopyWithImpl<PrescriptiveRemediationDto>(this as PrescriptiveRemediationDto, _$identity);

  /// Serializes this PrescriptiveRemediationDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'PrescriptiveRemediationDto(targetNodeId: $targetNodeId, requiredAction: $requiredAction, unlocksNodeIds: $unlocksNodeIds, potentialScoreImpact: $potentialScoreImpact)';
}


}

/// @nodoc
abstract mixin class $PrescriptiveRemediationDtoCopyWith<$Res>  {
  factory $PrescriptiveRemediationDtoCopyWith(PrescriptiveRemediationDto value, $Res Function(PrescriptiveRemediationDto) _then) = _$PrescriptiveRemediationDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'target_node_id') String targetNodeId,@JsonKey(name: 'required_action') String requiredAction,@JsonKey(name: 'unlocks_node_ids') List<String> unlocksNodeIds,@JsonKey(name: 'potential_score_impact') double potentialScoreImpact
});




}
/// @nodoc
class _$PrescriptiveRemediationDtoCopyWithImpl<$Res>
    implements $PrescriptiveRemediationDtoCopyWith<$Res> {
  _$PrescriptiveRemediationDtoCopyWithImpl(this._self, this._then);

  final PrescriptiveRemediationDto _self;
  final $Res Function(PrescriptiveRemediationDto) _then;

/// Create a copy of PrescriptiveRemediationDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? targetNodeId = null,Object? requiredAction = null,Object? unlocksNodeIds = null,Object? potentialScoreImpact = null,}) {
  return _then(_self.copyWith(
targetNodeId: null == targetNodeId ? _self.targetNodeId : targetNodeId // ignore: cast_nullable_to_non_nullable
as String,requiredAction: null == requiredAction ? _self.requiredAction : requiredAction // ignore: cast_nullable_to_non_nullable
as String,unlocksNodeIds: null == unlocksNodeIds ? _self.unlocksNodeIds : unlocksNodeIds // ignore: cast_nullable_to_non_nullable
as List<String>,potentialScoreImpact: null == potentialScoreImpact ? _self.potentialScoreImpact : potentialScoreImpact // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [PrescriptiveRemediationDto].
extension PrescriptiveRemediationDtoPatterns on PrescriptiveRemediationDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PrescriptiveRemediationDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PrescriptiveRemediationDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PrescriptiveRemediationDto value)  $default,){
final _that = this;
switch (_that) {
case _PrescriptiveRemediationDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PrescriptiveRemediationDto value)?  $default,){
final _that = this;
switch (_that) {
case _PrescriptiveRemediationDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'target_node_id')  String targetNodeId, @JsonKey(name: 'required_action')  String requiredAction, @JsonKey(name: 'unlocks_node_ids')  List<String> unlocksNodeIds, @JsonKey(name: 'potential_score_impact')  double potentialScoreImpact)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PrescriptiveRemediationDto() when $default != null:
return $default(_that.targetNodeId,_that.requiredAction,_that.unlocksNodeIds,_that.potentialScoreImpact);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'target_node_id')  String targetNodeId, @JsonKey(name: 'required_action')  String requiredAction, @JsonKey(name: 'unlocks_node_ids')  List<String> unlocksNodeIds, @JsonKey(name: 'potential_score_impact')  double potentialScoreImpact)  $default,) {final _that = this;
switch (_that) {
case _PrescriptiveRemediationDto():
return $default(_that.targetNodeId,_that.requiredAction,_that.unlocksNodeIds,_that.potentialScoreImpact);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'target_node_id')  String targetNodeId, @JsonKey(name: 'required_action')  String requiredAction, @JsonKey(name: 'unlocks_node_ids')  List<String> unlocksNodeIds, @JsonKey(name: 'potential_score_impact')  double potentialScoreImpact)?  $default,) {final _that = this;
switch (_that) {
case _PrescriptiveRemediationDto() when $default != null:
return $default(_that.targetNodeId,_that.requiredAction,_that.unlocksNodeIds,_that.potentialScoreImpact);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _PrescriptiveRemediationDto implements PrescriptiveRemediationDto {
  const _PrescriptiveRemediationDto({@JsonKey(name: 'target_node_id') required this.targetNodeId, @JsonKey(name: 'required_action') required this.requiredAction, @JsonKey(name: 'unlocks_node_ids') final  List<String> unlocksNodeIds = const [], @JsonKey(name: 'potential_score_impact') required this.potentialScoreImpact}): _unlocksNodeIds = unlocksNodeIds;
  factory _PrescriptiveRemediationDto.fromJson(Map<String, dynamic> json) => _$PrescriptiveRemediationDtoFromJson(json);

@override@JsonKey(name: 'target_node_id') final  String targetNodeId;
@override@JsonKey(name: 'required_action') final  String requiredAction;
 final  List<String> _unlocksNodeIds;
@override@JsonKey(name: 'unlocks_node_ids') List<String> get unlocksNodeIds {
  if (_unlocksNodeIds is EqualUnmodifiableListView) return _unlocksNodeIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_unlocksNodeIds);
}

@override@JsonKey(name: 'potential_score_impact') final  double potentialScoreImpact;

/// Create a copy of PrescriptiveRemediationDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PrescriptiveRemediationDtoCopyWith<_PrescriptiveRemediationDto> get copyWith => __$PrescriptiveRemediationDtoCopyWithImpl<_PrescriptiveRemediationDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PrescriptiveRemediationDtoToJson(this, );
}



@override
String toString() {
  return 'PrescriptiveRemediationDto(targetNodeId: $targetNodeId, requiredAction: $requiredAction, unlocksNodeIds: $unlocksNodeIds, potentialScoreImpact: $potentialScoreImpact)';
}


}

/// @nodoc
abstract mixin class _$PrescriptiveRemediationDtoCopyWith<$Res> implements $PrescriptiveRemediationDtoCopyWith<$Res> {
  factory _$PrescriptiveRemediationDtoCopyWith(_PrescriptiveRemediationDto value, $Res Function(_PrescriptiveRemediationDto) _then) = __$PrescriptiveRemediationDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'target_node_id') String targetNodeId,@JsonKey(name: 'required_action') String requiredAction,@JsonKey(name: 'unlocks_node_ids') List<String> unlocksNodeIds,@JsonKey(name: 'potential_score_impact') double potentialScoreImpact
});




}
/// @nodoc
class __$PrescriptiveRemediationDtoCopyWithImpl<$Res>
    implements _$PrescriptiveRemediationDtoCopyWith<$Res> {
  __$PrescriptiveRemediationDtoCopyWithImpl(this._self, this._then);

  final _PrescriptiveRemediationDto _self;
  final $Res Function(_PrescriptiveRemediationDto) _then;

/// Create a copy of PrescriptiveRemediationDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? targetNodeId = null,Object? requiredAction = null,Object? unlocksNodeIds = null,Object? potentialScoreImpact = null,}) {
  return _then(_PrescriptiveRemediationDto(
targetNodeId: null == targetNodeId ? _self.targetNodeId : targetNodeId // ignore: cast_nullable_to_non_nullable
as String,requiredAction: null == requiredAction ? _self.requiredAction : requiredAction // ignore: cast_nullable_to_non_nullable
as String,unlocksNodeIds: null == unlocksNodeIds ? _self._unlocksNodeIds : unlocksNodeIds // ignore: cast_nullable_to_non_nullable
as List<String>,potentialScoreImpact: null == potentialScoreImpact ? _self.potentialScoreImpact : potentialScoreImpact // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}


/// @nodoc
mixin _$FairScoringBreakdownDto {

@JsonKey(name: 'independent_error_count') int get independentErrorCount;@JsonKey(name: 'cascading_fault_count') int get cascadingFaultCount;@JsonKey(name: 'raw_penalty_points') double get rawPenaltyPoints;@JsonKey(name: 'deduplicated_penalty_points') double get deduplicatedPenaltyPoints;@JsonKey(name: 'dampened_savings_points') double get dampenedSavingsPoints;
/// Create a copy of FairScoringBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FairScoringBreakdownDtoCopyWith<FairScoringBreakdownDto> get copyWith => _$FairScoringBreakdownDtoCopyWithImpl<FairScoringBreakdownDto>(this as FairScoringBreakdownDto, _$identity);

  /// Serializes this FairScoringBreakdownDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'FairScoringBreakdownDto(independentErrorCount: $independentErrorCount, cascadingFaultCount: $cascadingFaultCount, rawPenaltyPoints: $rawPenaltyPoints, deduplicatedPenaltyPoints: $deduplicatedPenaltyPoints, dampenedSavingsPoints: $dampenedSavingsPoints)';
}


}

/// @nodoc
abstract mixin class $FairScoringBreakdownDtoCopyWith<$Res>  {
  factory $FairScoringBreakdownDtoCopyWith(FairScoringBreakdownDto value, $Res Function(FairScoringBreakdownDto) _then) = _$FairScoringBreakdownDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'independent_error_count') int independentErrorCount,@JsonKey(name: 'cascading_fault_count') int cascadingFaultCount,@JsonKey(name: 'raw_penalty_points') double rawPenaltyPoints,@JsonKey(name: 'deduplicated_penalty_points') double deduplicatedPenaltyPoints,@JsonKey(name: 'dampened_savings_points') double dampenedSavingsPoints
});




}
/// @nodoc
class _$FairScoringBreakdownDtoCopyWithImpl<$Res>
    implements $FairScoringBreakdownDtoCopyWith<$Res> {
  _$FairScoringBreakdownDtoCopyWithImpl(this._self, this._then);

  final FairScoringBreakdownDto _self;
  final $Res Function(FairScoringBreakdownDto) _then;

/// Create a copy of FairScoringBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? independentErrorCount = null,Object? cascadingFaultCount = null,Object? rawPenaltyPoints = null,Object? deduplicatedPenaltyPoints = null,Object? dampenedSavingsPoints = null,}) {
  return _then(_self.copyWith(
independentErrorCount: null == independentErrorCount ? _self.independentErrorCount : independentErrorCount // ignore: cast_nullable_to_non_nullable
as int,cascadingFaultCount: null == cascadingFaultCount ? _self.cascadingFaultCount : cascadingFaultCount // ignore: cast_nullable_to_non_nullable
as int,rawPenaltyPoints: null == rawPenaltyPoints ? _self.rawPenaltyPoints : rawPenaltyPoints // ignore: cast_nullable_to_non_nullable
as double,deduplicatedPenaltyPoints: null == deduplicatedPenaltyPoints ? _self.deduplicatedPenaltyPoints : deduplicatedPenaltyPoints // ignore: cast_nullable_to_non_nullable
as double,dampenedSavingsPoints: null == dampenedSavingsPoints ? _self.dampenedSavingsPoints : dampenedSavingsPoints // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [FairScoringBreakdownDto].
extension FairScoringBreakdownDtoPatterns on FairScoringBreakdownDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FairScoringBreakdownDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FairScoringBreakdownDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FairScoringBreakdownDto value)  $default,){
final _that = this;
switch (_that) {
case _FairScoringBreakdownDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FairScoringBreakdownDto value)?  $default,){
final _that = this;
switch (_that) {
case _FairScoringBreakdownDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'independent_error_count')  int independentErrorCount, @JsonKey(name: 'cascading_fault_count')  int cascadingFaultCount, @JsonKey(name: 'raw_penalty_points')  double rawPenaltyPoints, @JsonKey(name: 'deduplicated_penalty_points')  double deduplicatedPenaltyPoints, @JsonKey(name: 'dampened_savings_points')  double dampenedSavingsPoints)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FairScoringBreakdownDto() when $default != null:
return $default(_that.independentErrorCount,_that.cascadingFaultCount,_that.rawPenaltyPoints,_that.deduplicatedPenaltyPoints,_that.dampenedSavingsPoints);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'independent_error_count')  int independentErrorCount, @JsonKey(name: 'cascading_fault_count')  int cascadingFaultCount, @JsonKey(name: 'raw_penalty_points')  double rawPenaltyPoints, @JsonKey(name: 'deduplicated_penalty_points')  double deduplicatedPenaltyPoints, @JsonKey(name: 'dampened_savings_points')  double dampenedSavingsPoints)  $default,) {final _that = this;
switch (_that) {
case _FairScoringBreakdownDto():
return $default(_that.independentErrorCount,_that.cascadingFaultCount,_that.rawPenaltyPoints,_that.deduplicatedPenaltyPoints,_that.dampenedSavingsPoints);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'independent_error_count')  int independentErrorCount, @JsonKey(name: 'cascading_fault_count')  int cascadingFaultCount, @JsonKey(name: 'raw_penalty_points')  double rawPenaltyPoints, @JsonKey(name: 'deduplicated_penalty_points')  double deduplicatedPenaltyPoints, @JsonKey(name: 'dampened_savings_points')  double dampenedSavingsPoints)?  $default,) {final _that = this;
switch (_that) {
case _FairScoringBreakdownDto() when $default != null:
return $default(_that.independentErrorCount,_that.cascadingFaultCount,_that.rawPenaltyPoints,_that.deduplicatedPenaltyPoints,_that.dampenedSavingsPoints);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _FairScoringBreakdownDto implements FairScoringBreakdownDto {
  const _FairScoringBreakdownDto({@JsonKey(name: 'independent_error_count') required this.independentErrorCount, @JsonKey(name: 'cascading_fault_count') required this.cascadingFaultCount, @JsonKey(name: 'raw_penalty_points') required this.rawPenaltyPoints, @JsonKey(name: 'deduplicated_penalty_points') required this.deduplicatedPenaltyPoints, @JsonKey(name: 'dampened_savings_points') required this.dampenedSavingsPoints});
  factory _FairScoringBreakdownDto.fromJson(Map<String, dynamic> json) => _$FairScoringBreakdownDtoFromJson(json);

@override@JsonKey(name: 'independent_error_count') final  int independentErrorCount;
@override@JsonKey(name: 'cascading_fault_count') final  int cascadingFaultCount;
@override@JsonKey(name: 'raw_penalty_points') final  double rawPenaltyPoints;
@override@JsonKey(name: 'deduplicated_penalty_points') final  double deduplicatedPenaltyPoints;
@override@JsonKey(name: 'dampened_savings_points') final  double dampenedSavingsPoints;

/// Create a copy of FairScoringBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FairScoringBreakdownDtoCopyWith<_FairScoringBreakdownDto> get copyWith => __$FairScoringBreakdownDtoCopyWithImpl<_FairScoringBreakdownDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FairScoringBreakdownDtoToJson(this, );
}



@override
String toString() {
  return 'FairScoringBreakdownDto(independentErrorCount: $independentErrorCount, cascadingFaultCount: $cascadingFaultCount, rawPenaltyPoints: $rawPenaltyPoints, deduplicatedPenaltyPoints: $deduplicatedPenaltyPoints, dampenedSavingsPoints: $dampenedSavingsPoints)';
}


}

/// @nodoc
abstract mixin class _$FairScoringBreakdownDtoCopyWith<$Res> implements $FairScoringBreakdownDtoCopyWith<$Res> {
  factory _$FairScoringBreakdownDtoCopyWith(_FairScoringBreakdownDto value, $Res Function(_FairScoringBreakdownDto) _then) = __$FairScoringBreakdownDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'independent_error_count') int independentErrorCount,@JsonKey(name: 'cascading_fault_count') int cascadingFaultCount,@JsonKey(name: 'raw_penalty_points') double rawPenaltyPoints,@JsonKey(name: 'deduplicated_penalty_points') double deduplicatedPenaltyPoints,@JsonKey(name: 'dampened_savings_points') double dampenedSavingsPoints
});




}
/// @nodoc
class __$FairScoringBreakdownDtoCopyWithImpl<$Res>
    implements _$FairScoringBreakdownDtoCopyWith<$Res> {
  __$FairScoringBreakdownDtoCopyWithImpl(this._self, this._then);

  final _FairScoringBreakdownDto _self;
  final $Res Function(_FairScoringBreakdownDto) _then;

/// Create a copy of FairScoringBreakdownDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? independentErrorCount = null,Object? cascadingFaultCount = null,Object? rawPenaltyPoints = null,Object? deduplicatedPenaltyPoints = null,Object? dampenedSavingsPoints = null,}) {
  return _then(_FairScoringBreakdownDto(
independentErrorCount: null == independentErrorCount ? _self.independentErrorCount : independentErrorCount // ignore: cast_nullable_to_non_nullable
as int,cascadingFaultCount: null == cascadingFaultCount ? _self.cascadingFaultCount : cascadingFaultCount // ignore: cast_nullable_to_non_nullable
as int,rawPenaltyPoints: null == rawPenaltyPoints ? _self.rawPenaltyPoints : rawPenaltyPoints // ignore: cast_nullable_to_non_nullable
as double,deduplicatedPenaltyPoints: null == deduplicatedPenaltyPoints ? _self.deduplicatedPenaltyPoints : deduplicatedPenaltyPoints // ignore: cast_nullable_to_non_nullable
as double,dampenedSavingsPoints: null == dampenedSavingsPoints ? _self.dampenedSavingsPoints : dampenedSavingsPoints // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

// dart format on
