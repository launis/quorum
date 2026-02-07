// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'evaluation_result.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DimensionResultItem {

@JsonKey(name: 'dimension_id') String get dimensionId;@JsonKey(name: 'dimension_label') String get dimensionLabel; double get score;// Python allows int|float, Dart uses double
 String get reasoning;
/// Create a copy of DimensionResultItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DimensionResultItemCopyWith<DimensionResultItem> get copyWith => _$DimensionResultItemCopyWithImpl<DimensionResultItem>(this as DimensionResultItem, _$identity);

  /// Serializes this DimensionResultItem to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DimensionResultItem&&(identical(other.dimensionId, dimensionId) || other.dimensionId == dimensionId)&&(identical(other.dimensionLabel, dimensionLabel) || other.dimensionLabel == dimensionLabel)&&(identical(other.score, score) || other.score == score)&&(identical(other.reasoning, reasoning) || other.reasoning == reasoning));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dimensionId,dimensionLabel,score,reasoning);

@override
String toString() {
  return 'DimensionResultItem(dimensionId: $dimensionId, dimensionLabel: $dimensionLabel, score: $score, reasoning: $reasoning)';
}


}

/// @nodoc
abstract mixin class $DimensionResultItemCopyWith<$Res>  {
  factory $DimensionResultItemCopyWith(DimensionResultItem value, $Res Function(DimensionResultItem) _then) = _$DimensionResultItemCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'dimension_id') String dimensionId,@JsonKey(name: 'dimension_label') String dimensionLabel, double score, String reasoning
});




}
/// @nodoc
class _$DimensionResultItemCopyWithImpl<$Res>
    implements $DimensionResultItemCopyWith<$Res> {
  _$DimensionResultItemCopyWithImpl(this._self, this._then);

  final DimensionResultItem _self;
  final $Res Function(DimensionResultItem) _then;

/// Create a copy of DimensionResultItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dimensionId = null,Object? dimensionLabel = null,Object? score = null,Object? reasoning = null,}) {
  return _then(_self.copyWith(
dimensionId: null == dimensionId ? _self.dimensionId : dimensionId // ignore: cast_nullable_to_non_nullable
as String,dimensionLabel: null == dimensionLabel ? _self.dimensionLabel : dimensionLabel // ignore: cast_nullable_to_non_nullable
as String,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [DimensionResultItem].
extension DimensionResultItemPatterns on DimensionResultItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DimensionResultItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DimensionResultItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DimensionResultItem value)  $default,){
final _that = this;
switch (_that) {
case _DimensionResultItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DimensionResultItem value)?  $default,){
final _that = this;
switch (_that) {
case _DimensionResultItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'dimension_id')  String dimensionId, @JsonKey(name: 'dimension_label')  String dimensionLabel,  double score,  String reasoning)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DimensionResultItem() when $default != null:
return $default(_that.dimensionId,_that.dimensionLabel,_that.score,_that.reasoning);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'dimension_id')  String dimensionId, @JsonKey(name: 'dimension_label')  String dimensionLabel,  double score,  String reasoning)  $default,) {final _that = this;
switch (_that) {
case _DimensionResultItem():
return $default(_that.dimensionId,_that.dimensionLabel,_that.score,_that.reasoning);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'dimension_id')  String dimensionId, @JsonKey(name: 'dimension_label')  String dimensionLabel,  double score,  String reasoning)?  $default,) {final _that = this;
switch (_that) {
case _DimensionResultItem() when $default != null:
return $default(_that.dimensionId,_that.dimensionLabel,_that.score,_that.reasoning);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DimensionResultItem implements DimensionResultItem {
  const _DimensionResultItem({@JsonKey(name: 'dimension_id') required this.dimensionId, @JsonKey(name: 'dimension_label') this.dimensionLabel = '', required this.score, required this.reasoning});
  factory _DimensionResultItem.fromJson(Map<String, dynamic> json) => _$DimensionResultItemFromJson(json);

@override@JsonKey(name: 'dimension_id') final  String dimensionId;
@override@JsonKey(name: 'dimension_label') final  String dimensionLabel;
@override final  double score;
// Python allows int|float, Dart uses double
@override final  String reasoning;

/// Create a copy of DimensionResultItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DimensionResultItemCopyWith<_DimensionResultItem> get copyWith => __$DimensionResultItemCopyWithImpl<_DimensionResultItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DimensionResultItemToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DimensionResultItem&&(identical(other.dimensionId, dimensionId) || other.dimensionId == dimensionId)&&(identical(other.dimensionLabel, dimensionLabel) || other.dimensionLabel == dimensionLabel)&&(identical(other.score, score) || other.score == score)&&(identical(other.reasoning, reasoning) || other.reasoning == reasoning));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dimensionId,dimensionLabel,score,reasoning);

@override
String toString() {
  return 'DimensionResultItem(dimensionId: $dimensionId, dimensionLabel: $dimensionLabel, score: $score, reasoning: $reasoning)';
}


}

/// @nodoc
abstract mixin class _$DimensionResultItemCopyWith<$Res> implements $DimensionResultItemCopyWith<$Res> {
  factory _$DimensionResultItemCopyWith(_DimensionResultItem value, $Res Function(_DimensionResultItem) _then) = __$DimensionResultItemCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'dimension_id') String dimensionId,@JsonKey(name: 'dimension_label') String dimensionLabel, double score, String reasoning
});




}
/// @nodoc
class __$DimensionResultItemCopyWithImpl<$Res>
    implements _$DimensionResultItemCopyWith<$Res> {
  __$DimensionResultItemCopyWithImpl(this._self, this._then);

  final _DimensionResultItem _self;
  final $Res Function(_DimensionResultItem) _then;

/// Create a copy of DimensionResultItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dimensionId = null,Object? dimensionLabel = null,Object? score = null,Object? reasoning = null,}) {
  return _then(_DimensionResultItem(
dimensionId: null == dimensionId ? _self.dimensionId : dimensionId // ignore: cast_nullable_to_non_nullable
as String,dimensionLabel: null == dimensionLabel ? _self.dimensionLabel : dimensionLabel // ignore: cast_nullable_to_non_nullable
as String,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$EvaluationResult {

// --- BaseJSON Metadata ---
 String get luontiaika; String get agentti; double get vaihe; String get versio;@JsonKey(name: 'suoritus_ymparisto') String? get suoritusYmparisto;// --- BaseJSON Common Fields ---
@JsonKey(name: 'reasoning_trace') String? get reasoningTrace;@JsonKey(name: 'metodologinen_loki') String get metodologinenLoki;@JsonKey(name: 'edellisen_vaiheen_validointi') String get edellisenVaiheenValidointi;@JsonKey(name: 'semanttinen_tarkistussumma') String get semanttinenTarkistussumma;// --- EvaluationResult Specifics ---
@JsonKey(name: 'matrix_id') String get matrixId;@JsonKey(name: 'scale_min') int get scaleMin;@JsonKey(name: 'scale_max') int get scaleMax;@JsonKey(name: 'total_score') double get totalScore; List<DimensionResultItem> get dimensions;@JsonKey(name: 'critical_findings') List<String> get criticalFindings;
/// Create a copy of EvaluationResult
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EvaluationResultCopyWith<EvaluationResult> get copyWith => _$EvaluationResultCopyWithImpl<EvaluationResult>(this as EvaluationResult, _$identity);

  /// Serializes this EvaluationResult to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EvaluationResult&&(identical(other.luontiaika, luontiaika) || other.luontiaika == luontiaika)&&(identical(other.agentti, agentti) || other.agentti == agentti)&&(identical(other.vaihe, vaihe) || other.vaihe == vaihe)&&(identical(other.versio, versio) || other.versio == versio)&&(identical(other.suoritusYmparisto, suoritusYmparisto) || other.suoritusYmparisto == suoritusYmparisto)&&(identical(other.reasoningTrace, reasoningTrace) || other.reasoningTrace == reasoningTrace)&&(identical(other.metodologinenLoki, metodologinenLoki) || other.metodologinenLoki == metodologinenLoki)&&(identical(other.edellisenVaiheenValidointi, edellisenVaiheenValidointi) || other.edellisenVaiheenValidointi == edellisenVaiheenValidointi)&&(identical(other.semanttinenTarkistussumma, semanttinenTarkistussumma) || other.semanttinenTarkistussumma == semanttinenTarkistussumma)&&(identical(other.matrixId, matrixId) || other.matrixId == matrixId)&&(identical(other.scaleMin, scaleMin) || other.scaleMin == scaleMin)&&(identical(other.scaleMax, scaleMax) || other.scaleMax == scaleMax)&&(identical(other.totalScore, totalScore) || other.totalScore == totalScore)&&const DeepCollectionEquality().equals(other.dimensions, dimensions)&&const DeepCollectionEquality().equals(other.criticalFindings, criticalFindings));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,luontiaika,agentti,vaihe,versio,suoritusYmparisto,reasoningTrace,metodologinenLoki,edellisenVaiheenValidointi,semanttinenTarkistussumma,matrixId,scaleMin,scaleMax,totalScore,const DeepCollectionEquality().hash(dimensions),const DeepCollectionEquality().hash(criticalFindings));

@override
String toString() {
  return 'EvaluationResult(luontiaika: $luontiaika, agentti: $agentti, vaihe: $vaihe, versio: $versio, suoritusYmparisto: $suoritusYmparisto, reasoningTrace: $reasoningTrace, metodologinenLoki: $metodologinenLoki, edellisenVaiheenValidointi: $edellisenVaiheenValidointi, semanttinenTarkistussumma: $semanttinenTarkistussumma, matrixId: $matrixId, scaleMin: $scaleMin, scaleMax: $scaleMax, totalScore: $totalScore, dimensions: $dimensions, criticalFindings: $criticalFindings)';
}


}

/// @nodoc
abstract mixin class $EvaluationResultCopyWith<$Res>  {
  factory $EvaluationResultCopyWith(EvaluationResult value, $Res Function(EvaluationResult) _then) = _$EvaluationResultCopyWithImpl;
@useResult
$Res call({
 String luontiaika, String agentti, double vaihe, String versio,@JsonKey(name: 'suoritus_ymparisto') String? suoritusYmparisto,@JsonKey(name: 'reasoning_trace') String? reasoningTrace,@JsonKey(name: 'metodologinen_loki') String metodologinenLoki,@JsonKey(name: 'edellisen_vaiheen_validointi') String edellisenVaiheenValidointi,@JsonKey(name: 'semanttinen_tarkistussumma') String semanttinenTarkistussumma,@JsonKey(name: 'matrix_id') String matrixId,@JsonKey(name: 'scale_min') int scaleMin,@JsonKey(name: 'scale_max') int scaleMax,@JsonKey(name: 'total_score') double totalScore, List<DimensionResultItem> dimensions,@JsonKey(name: 'critical_findings') List<String> criticalFindings
});




}
/// @nodoc
class _$EvaluationResultCopyWithImpl<$Res>
    implements $EvaluationResultCopyWith<$Res> {
  _$EvaluationResultCopyWithImpl(this._self, this._then);

  final EvaluationResult _self;
  final $Res Function(EvaluationResult) _then;

/// Create a copy of EvaluationResult
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? luontiaika = null,Object? agentti = null,Object? vaihe = null,Object? versio = null,Object? suoritusYmparisto = freezed,Object? reasoningTrace = freezed,Object? metodologinenLoki = null,Object? edellisenVaiheenValidointi = null,Object? semanttinenTarkistussumma = null,Object? matrixId = null,Object? scaleMin = null,Object? scaleMax = null,Object? totalScore = null,Object? dimensions = null,Object? criticalFindings = null,}) {
  return _then(_self.copyWith(
luontiaika: null == luontiaika ? _self.luontiaika : luontiaika // ignore: cast_nullable_to_non_nullable
as String,agentti: null == agentti ? _self.agentti : agentti // ignore: cast_nullable_to_non_nullable
as String,vaihe: null == vaihe ? _self.vaihe : vaihe // ignore: cast_nullable_to_non_nullable
as double,versio: null == versio ? _self.versio : versio // ignore: cast_nullable_to_non_nullable
as String,suoritusYmparisto: freezed == suoritusYmparisto ? _self.suoritusYmparisto : suoritusYmparisto // ignore: cast_nullable_to_non_nullable
as String?,reasoningTrace: freezed == reasoningTrace ? _self.reasoningTrace : reasoningTrace // ignore: cast_nullable_to_non_nullable
as String?,metodologinenLoki: null == metodologinenLoki ? _self.metodologinenLoki : metodologinenLoki // ignore: cast_nullable_to_non_nullable
as String,edellisenVaiheenValidointi: null == edellisenVaiheenValidointi ? _self.edellisenVaiheenValidointi : edellisenVaiheenValidointi // ignore: cast_nullable_to_non_nullable
as String,semanttinenTarkistussumma: null == semanttinenTarkistussumma ? _self.semanttinenTarkistussumma : semanttinenTarkistussumma // ignore: cast_nullable_to_non_nullable
as String,matrixId: null == matrixId ? _self.matrixId : matrixId // ignore: cast_nullable_to_non_nullable
as String,scaleMin: null == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as int,scaleMax: null == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as int,totalScore: null == totalScore ? _self.totalScore : totalScore // ignore: cast_nullable_to_non_nullable
as double,dimensions: null == dimensions ? _self.dimensions : dimensions // ignore: cast_nullable_to_non_nullable
as List<DimensionResultItem>,criticalFindings: null == criticalFindings ? _self.criticalFindings : criticalFindings // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [EvaluationResult].
extension EvaluationResultPatterns on EvaluationResult {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EvaluationResult value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EvaluationResult() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EvaluationResult value)  $default,){
final _that = this;
switch (_that) {
case _EvaluationResult():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EvaluationResult value)?  $default,){
final _that = this;
switch (_that) {
case _EvaluationResult() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String luontiaika,  String agentti,  double vaihe,  String versio, @JsonKey(name: 'suoritus_ymparisto')  String? suoritusYmparisto, @JsonKey(name: 'reasoning_trace')  String? reasoningTrace, @JsonKey(name: 'metodologinen_loki')  String metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi')  String edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma')  String semanttinenTarkistussumma, @JsonKey(name: 'matrix_id')  String matrixId, @JsonKey(name: 'scale_min')  int scaleMin, @JsonKey(name: 'scale_max')  int scaleMax, @JsonKey(name: 'total_score')  double totalScore,  List<DimensionResultItem> dimensions, @JsonKey(name: 'critical_findings')  List<String> criticalFindings)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EvaluationResult() when $default != null:
return $default(_that.luontiaika,_that.agentti,_that.vaihe,_that.versio,_that.suoritusYmparisto,_that.reasoningTrace,_that.metodologinenLoki,_that.edellisenVaiheenValidointi,_that.semanttinenTarkistussumma,_that.matrixId,_that.scaleMin,_that.scaleMax,_that.totalScore,_that.dimensions,_that.criticalFindings);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String luontiaika,  String agentti,  double vaihe,  String versio, @JsonKey(name: 'suoritus_ymparisto')  String? suoritusYmparisto, @JsonKey(name: 'reasoning_trace')  String? reasoningTrace, @JsonKey(name: 'metodologinen_loki')  String metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi')  String edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma')  String semanttinenTarkistussumma, @JsonKey(name: 'matrix_id')  String matrixId, @JsonKey(name: 'scale_min')  int scaleMin, @JsonKey(name: 'scale_max')  int scaleMax, @JsonKey(name: 'total_score')  double totalScore,  List<DimensionResultItem> dimensions, @JsonKey(name: 'critical_findings')  List<String> criticalFindings)  $default,) {final _that = this;
switch (_that) {
case _EvaluationResult():
return $default(_that.luontiaika,_that.agentti,_that.vaihe,_that.versio,_that.suoritusYmparisto,_that.reasoningTrace,_that.metodologinenLoki,_that.edellisenVaiheenValidointi,_that.semanttinenTarkistussumma,_that.matrixId,_that.scaleMin,_that.scaleMax,_that.totalScore,_that.dimensions,_that.criticalFindings);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String luontiaika,  String agentti,  double vaihe,  String versio, @JsonKey(name: 'suoritus_ymparisto')  String? suoritusYmparisto, @JsonKey(name: 'reasoning_trace')  String? reasoningTrace, @JsonKey(name: 'metodologinen_loki')  String metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi')  String edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma')  String semanttinenTarkistussumma, @JsonKey(name: 'matrix_id')  String matrixId, @JsonKey(name: 'scale_min')  int scaleMin, @JsonKey(name: 'scale_max')  int scaleMax, @JsonKey(name: 'total_score')  double totalScore,  List<DimensionResultItem> dimensions, @JsonKey(name: 'critical_findings')  List<String> criticalFindings)?  $default,) {final _that = this;
switch (_that) {
case _EvaluationResult() when $default != null:
return $default(_that.luontiaika,_that.agentti,_that.vaihe,_that.versio,_that.suoritusYmparisto,_that.reasoningTrace,_that.metodologinenLoki,_that.edellisenVaiheenValidointi,_that.semanttinenTarkistussumma,_that.matrixId,_that.scaleMin,_that.scaleMax,_that.totalScore,_that.dimensions,_that.criticalFindings);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EvaluationResult implements EvaluationResult {
  const _EvaluationResult({required this.luontiaika, required this.agentti, required this.vaihe, this.versio = '2.0', @JsonKey(name: 'suoritus_ymparisto') this.suoritusYmparisto, @JsonKey(name: 'reasoning_trace') this.reasoningTrace, @JsonKey(name: 'metodologinen_loki') required this.metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi') required this.edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma') required this.semanttinenTarkistussumma, @JsonKey(name: 'matrix_id') required this.matrixId, @JsonKey(name: 'scale_min') this.scaleMin = 1, @JsonKey(name: 'scale_max') this.scaleMax = 5, @JsonKey(name: 'total_score') required this.totalScore, required final  List<DimensionResultItem> dimensions, @JsonKey(name: 'critical_findings') final  List<String> criticalFindings = const []}): _dimensions = dimensions,_criticalFindings = criticalFindings;
  factory _EvaluationResult.fromJson(Map<String, dynamic> json) => _$EvaluationResultFromJson(json);

// --- BaseJSON Metadata ---
@override final  String luontiaika;
@override final  String agentti;
@override final  double vaihe;
@override@JsonKey() final  String versio;
@override@JsonKey(name: 'suoritus_ymparisto') final  String? suoritusYmparisto;
// --- BaseJSON Common Fields ---
@override@JsonKey(name: 'reasoning_trace') final  String? reasoningTrace;
@override@JsonKey(name: 'metodologinen_loki') final  String metodologinenLoki;
@override@JsonKey(name: 'edellisen_vaiheen_validointi') final  String edellisenVaiheenValidointi;
@override@JsonKey(name: 'semanttinen_tarkistussumma') final  String semanttinenTarkistussumma;
// --- EvaluationResult Specifics ---
@override@JsonKey(name: 'matrix_id') final  String matrixId;
@override@JsonKey(name: 'scale_min') final  int scaleMin;
@override@JsonKey(name: 'scale_max') final  int scaleMax;
@override@JsonKey(name: 'total_score') final  double totalScore;
 final  List<DimensionResultItem> _dimensions;
@override List<DimensionResultItem> get dimensions {
  if (_dimensions is EqualUnmodifiableListView) return _dimensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dimensions);
}

 final  List<String> _criticalFindings;
@override@JsonKey(name: 'critical_findings') List<String> get criticalFindings {
  if (_criticalFindings is EqualUnmodifiableListView) return _criticalFindings;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_criticalFindings);
}


/// Create a copy of EvaluationResult
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EvaluationResultCopyWith<_EvaluationResult> get copyWith => __$EvaluationResultCopyWithImpl<_EvaluationResult>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EvaluationResultToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EvaluationResult&&(identical(other.luontiaika, luontiaika) || other.luontiaika == luontiaika)&&(identical(other.agentti, agentti) || other.agentti == agentti)&&(identical(other.vaihe, vaihe) || other.vaihe == vaihe)&&(identical(other.versio, versio) || other.versio == versio)&&(identical(other.suoritusYmparisto, suoritusYmparisto) || other.suoritusYmparisto == suoritusYmparisto)&&(identical(other.reasoningTrace, reasoningTrace) || other.reasoningTrace == reasoningTrace)&&(identical(other.metodologinenLoki, metodologinenLoki) || other.metodologinenLoki == metodologinenLoki)&&(identical(other.edellisenVaiheenValidointi, edellisenVaiheenValidointi) || other.edellisenVaiheenValidointi == edellisenVaiheenValidointi)&&(identical(other.semanttinenTarkistussumma, semanttinenTarkistussumma) || other.semanttinenTarkistussumma == semanttinenTarkistussumma)&&(identical(other.matrixId, matrixId) || other.matrixId == matrixId)&&(identical(other.scaleMin, scaleMin) || other.scaleMin == scaleMin)&&(identical(other.scaleMax, scaleMax) || other.scaleMax == scaleMax)&&(identical(other.totalScore, totalScore) || other.totalScore == totalScore)&&const DeepCollectionEquality().equals(other._dimensions, _dimensions)&&const DeepCollectionEquality().equals(other._criticalFindings, _criticalFindings));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,luontiaika,agentti,vaihe,versio,suoritusYmparisto,reasoningTrace,metodologinenLoki,edellisenVaiheenValidointi,semanttinenTarkistussumma,matrixId,scaleMin,scaleMax,totalScore,const DeepCollectionEquality().hash(_dimensions),const DeepCollectionEquality().hash(_criticalFindings));

@override
String toString() {
  return 'EvaluationResult(luontiaika: $luontiaika, agentti: $agentti, vaihe: $vaihe, versio: $versio, suoritusYmparisto: $suoritusYmparisto, reasoningTrace: $reasoningTrace, metodologinenLoki: $metodologinenLoki, edellisenVaiheenValidointi: $edellisenVaiheenValidointi, semanttinenTarkistussumma: $semanttinenTarkistussumma, matrixId: $matrixId, scaleMin: $scaleMin, scaleMax: $scaleMax, totalScore: $totalScore, dimensions: $dimensions, criticalFindings: $criticalFindings)';
}


}

/// @nodoc
abstract mixin class _$EvaluationResultCopyWith<$Res> implements $EvaluationResultCopyWith<$Res> {
  factory _$EvaluationResultCopyWith(_EvaluationResult value, $Res Function(_EvaluationResult) _then) = __$EvaluationResultCopyWithImpl;
@override @useResult
$Res call({
 String luontiaika, String agentti, double vaihe, String versio,@JsonKey(name: 'suoritus_ymparisto') String? suoritusYmparisto,@JsonKey(name: 'reasoning_trace') String? reasoningTrace,@JsonKey(name: 'metodologinen_loki') String metodologinenLoki,@JsonKey(name: 'edellisen_vaiheen_validointi') String edellisenVaiheenValidointi,@JsonKey(name: 'semanttinen_tarkistussumma') String semanttinenTarkistussumma,@JsonKey(name: 'matrix_id') String matrixId,@JsonKey(name: 'scale_min') int scaleMin,@JsonKey(name: 'scale_max') int scaleMax,@JsonKey(name: 'total_score') double totalScore, List<DimensionResultItem> dimensions,@JsonKey(name: 'critical_findings') List<String> criticalFindings
});




}
/// @nodoc
class __$EvaluationResultCopyWithImpl<$Res>
    implements _$EvaluationResultCopyWith<$Res> {
  __$EvaluationResultCopyWithImpl(this._self, this._then);

  final _EvaluationResult _self;
  final $Res Function(_EvaluationResult) _then;

/// Create a copy of EvaluationResult
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? luontiaika = null,Object? agentti = null,Object? vaihe = null,Object? versio = null,Object? suoritusYmparisto = freezed,Object? reasoningTrace = freezed,Object? metodologinenLoki = null,Object? edellisenVaiheenValidointi = null,Object? semanttinenTarkistussumma = null,Object? matrixId = null,Object? scaleMin = null,Object? scaleMax = null,Object? totalScore = null,Object? dimensions = null,Object? criticalFindings = null,}) {
  return _then(_EvaluationResult(
luontiaika: null == luontiaika ? _self.luontiaika : luontiaika // ignore: cast_nullable_to_non_nullable
as String,agentti: null == agentti ? _self.agentti : agentti // ignore: cast_nullable_to_non_nullable
as String,vaihe: null == vaihe ? _self.vaihe : vaihe // ignore: cast_nullable_to_non_nullable
as double,versio: null == versio ? _self.versio : versio // ignore: cast_nullable_to_non_nullable
as String,suoritusYmparisto: freezed == suoritusYmparisto ? _self.suoritusYmparisto : suoritusYmparisto // ignore: cast_nullable_to_non_nullable
as String?,reasoningTrace: freezed == reasoningTrace ? _self.reasoningTrace : reasoningTrace // ignore: cast_nullable_to_non_nullable
as String?,metodologinenLoki: null == metodologinenLoki ? _self.metodologinenLoki : metodologinenLoki // ignore: cast_nullable_to_non_nullable
as String,edellisenVaiheenValidointi: null == edellisenVaiheenValidointi ? _self.edellisenVaiheenValidointi : edellisenVaiheenValidointi // ignore: cast_nullable_to_non_nullable
as String,semanttinenTarkistussumma: null == semanttinenTarkistussumma ? _self.semanttinenTarkistussumma : semanttinenTarkistussumma // ignore: cast_nullable_to_non_nullable
as String,matrixId: null == matrixId ? _self.matrixId : matrixId // ignore: cast_nullable_to_non_nullable
as String,scaleMin: null == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as int,scaleMax: null == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as int,totalScore: null == totalScore ? _self.totalScore : totalScore // ignore: cast_nullable_to_non_nullable
as double,dimensions: null == dimensions ? _self._dimensions : dimensions // ignore: cast_nullable_to_non_nullable
as List<DimensionResultItem>,criticalFindings: null == criticalFindings ? _self._criticalFindings : criticalFindings // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
