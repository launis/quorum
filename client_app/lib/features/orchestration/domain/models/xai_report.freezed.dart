// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'xai_report.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ScoreCardItem {

@JsonKey(name: 'agent_name') String get agentName;@JsonKey(name: 'total_score') double get totalScore;@JsonKey(name: 'min_score') int get minScore;@JsonKey(name: 'max_score') int get maxScore; String get verdict; List<DimensionResultItem> get dimensions;
/// Create a copy of ScoreCardItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScoreCardItemCopyWith<ScoreCardItem> get copyWith => _$ScoreCardItemCopyWithImpl<ScoreCardItem>(this as ScoreCardItem, _$identity);

  /// Serializes this ScoreCardItem to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ScoreCardItem&&(identical(other.agentName, agentName) || other.agentName == agentName)&&(identical(other.totalScore, totalScore) || other.totalScore == totalScore)&&(identical(other.minScore, minScore) || other.minScore == minScore)&&(identical(other.maxScore, maxScore) || other.maxScore == maxScore)&&(identical(other.verdict, verdict) || other.verdict == verdict)&&const DeepCollectionEquality().equals(other.dimensions, dimensions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,agentName,totalScore,minScore,maxScore,verdict,const DeepCollectionEquality().hash(dimensions));

@override
String toString() {
  return 'ScoreCardItem(agentName: $agentName, totalScore: $totalScore, minScore: $minScore, maxScore: $maxScore, verdict: $verdict, dimensions: $dimensions)';
}


}

/// @nodoc
abstract mixin class $ScoreCardItemCopyWith<$Res>  {
  factory $ScoreCardItemCopyWith(ScoreCardItem value, $Res Function(ScoreCardItem) _then) = _$ScoreCardItemCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'agent_name') String agentName,@JsonKey(name: 'total_score') double totalScore,@JsonKey(name: 'min_score') int minScore,@JsonKey(name: 'max_score') int maxScore, String verdict, List<DimensionResultItem> dimensions
});




}
/// @nodoc
class _$ScoreCardItemCopyWithImpl<$Res>
    implements $ScoreCardItemCopyWith<$Res> {
  _$ScoreCardItemCopyWithImpl(this._self, this._then);

  final ScoreCardItem _self;
  final $Res Function(ScoreCardItem) _then;

/// Create a copy of ScoreCardItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? agentName = null,Object? totalScore = null,Object? minScore = null,Object? maxScore = null,Object? verdict = null,Object? dimensions = null,}) {
  return _then(_self.copyWith(
agentName: null == agentName ? _self.agentName : agentName // ignore: cast_nullable_to_non_nullable
as String,totalScore: null == totalScore ? _self.totalScore : totalScore // ignore: cast_nullable_to_non_nullable
as double,minScore: null == minScore ? _self.minScore : minScore // ignore: cast_nullable_to_non_nullable
as int,maxScore: null == maxScore ? _self.maxScore : maxScore // ignore: cast_nullable_to_non_nullable
as int,verdict: null == verdict ? _self.verdict : verdict // ignore: cast_nullable_to_non_nullable
as String,dimensions: null == dimensions ? _self.dimensions : dimensions // ignore: cast_nullable_to_non_nullable
as List<DimensionResultItem>,
  ));
}

}


/// Adds pattern-matching-related methods to [ScoreCardItem].
extension ScoreCardItemPatterns on ScoreCardItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScoreCardItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScoreCardItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScoreCardItem value)  $default,){
final _that = this;
switch (_that) {
case _ScoreCardItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScoreCardItem value)?  $default,){
final _that = this;
switch (_that) {
case _ScoreCardItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'agent_name')  String agentName, @JsonKey(name: 'total_score')  double totalScore, @JsonKey(name: 'min_score')  int minScore, @JsonKey(name: 'max_score')  int maxScore,  String verdict,  List<DimensionResultItem> dimensions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScoreCardItem() when $default != null:
return $default(_that.agentName,_that.totalScore,_that.minScore,_that.maxScore,_that.verdict,_that.dimensions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'agent_name')  String agentName, @JsonKey(name: 'total_score')  double totalScore, @JsonKey(name: 'min_score')  int minScore, @JsonKey(name: 'max_score')  int maxScore,  String verdict,  List<DimensionResultItem> dimensions)  $default,) {final _that = this;
switch (_that) {
case _ScoreCardItem():
return $default(_that.agentName,_that.totalScore,_that.minScore,_that.maxScore,_that.verdict,_that.dimensions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'agent_name')  String agentName, @JsonKey(name: 'total_score')  double totalScore, @JsonKey(name: 'min_score')  int minScore, @JsonKey(name: 'max_score')  int maxScore,  String verdict,  List<DimensionResultItem> dimensions)?  $default,) {final _that = this;
switch (_that) {
case _ScoreCardItem() when $default != null:
return $default(_that.agentName,_that.totalScore,_that.minScore,_that.maxScore,_that.verdict,_that.dimensions);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ScoreCardItem implements ScoreCardItem {
  const _ScoreCardItem({@JsonKey(name: 'agent_name') required this.agentName, @JsonKey(name: 'total_score') required this.totalScore, @JsonKey(name: 'min_score') this.minScore = 0, @JsonKey(name: 'max_score') this.maxScore = 5, required this.verdict, final  List<DimensionResultItem> dimensions = const []}): _dimensions = dimensions;
  factory _ScoreCardItem.fromJson(Map<String, dynamic> json) => _$ScoreCardItemFromJson(json);

@override@JsonKey(name: 'agent_name') final  String agentName;
@override@JsonKey(name: 'total_score') final  double totalScore;
@override@JsonKey(name: 'min_score') final  int minScore;
@override@JsonKey(name: 'max_score') final  int maxScore;
@override final  String verdict;
 final  List<DimensionResultItem> _dimensions;
@override@JsonKey() List<DimensionResultItem> get dimensions {
  if (_dimensions is EqualUnmodifiableListView) return _dimensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dimensions);
}


/// Create a copy of ScoreCardItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScoreCardItemCopyWith<_ScoreCardItem> get copyWith => __$ScoreCardItemCopyWithImpl<_ScoreCardItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ScoreCardItemToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ScoreCardItem&&(identical(other.agentName, agentName) || other.agentName == agentName)&&(identical(other.totalScore, totalScore) || other.totalScore == totalScore)&&(identical(other.minScore, minScore) || other.minScore == minScore)&&(identical(other.maxScore, maxScore) || other.maxScore == maxScore)&&(identical(other.verdict, verdict) || other.verdict == verdict)&&const DeepCollectionEquality().equals(other._dimensions, _dimensions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,agentName,totalScore,minScore,maxScore,verdict,const DeepCollectionEquality().hash(_dimensions));

@override
String toString() {
  return 'ScoreCardItem(agentName: $agentName, totalScore: $totalScore, minScore: $minScore, maxScore: $maxScore, verdict: $verdict, dimensions: $dimensions)';
}


}

/// @nodoc
abstract mixin class _$ScoreCardItemCopyWith<$Res> implements $ScoreCardItemCopyWith<$Res> {
  factory _$ScoreCardItemCopyWith(_ScoreCardItem value, $Res Function(_ScoreCardItem) _then) = __$ScoreCardItemCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'agent_name') String agentName,@JsonKey(name: 'total_score') double totalScore,@JsonKey(name: 'min_score') int minScore,@JsonKey(name: 'max_score') int maxScore, String verdict, List<DimensionResultItem> dimensions
});




}
/// @nodoc
class __$ScoreCardItemCopyWithImpl<$Res>
    implements _$ScoreCardItemCopyWith<$Res> {
  __$ScoreCardItemCopyWithImpl(this._self, this._then);

  final _ScoreCardItem _self;
  final $Res Function(_ScoreCardItem) _then;

/// Create a copy of ScoreCardItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? agentName = null,Object? totalScore = null,Object? minScore = null,Object? maxScore = null,Object? verdict = null,Object? dimensions = null,}) {
  return _then(_ScoreCardItem(
agentName: null == agentName ? _self.agentName : agentName // ignore: cast_nullable_to_non_nullable
as String,totalScore: null == totalScore ? _self.totalScore : totalScore // ignore: cast_nullable_to_non_nullable
as double,minScore: null == minScore ? _self.minScore : minScore // ignore: cast_nullable_to_non_nullable
as int,maxScore: null == maxScore ? _self.maxScore : maxScore // ignore: cast_nullable_to_non_nullable
as int,verdict: null == verdict ? _self.verdict : verdict // ignore: cast_nullable_to_non_nullable
as String,dimensions: null == dimensions ? _self._dimensions : dimensions // ignore: cast_nullable_to_non_nullable
as List<DimensionResultItem>,
  ));
}


}


/// @nodoc
mixin _$XAIReport {

// --- BaseJSON Metadata ---
 Map<String, dynamic> get metadata;@JsonKey(name: 'metodologinen_loki') String get metodologinenLoki;@JsonKey(name: 'edellisen_vaiheen_validointi') String get edellisenVaiheenValidointi;@JsonKey(name: 'semanttinen_tarkistussumma') String get semanttinenTarkistussumma;// --- Report Fields ---
@JsonKey(name: 'executive_summary') String get executiveSummary;@JsonKey(name: 'analysis_strengths') String get analysisStrengths;@JsonKey(name: 'analysis_weaknesses') String get analysisWeaknesses;@JsonKey(name: 'analysis_opportunities') String get analysisOpportunities;@JsonKey(name: 'analysis_recommendations') String get analysisRecommendations;@JsonKey(name: 'final_verdict') String get finalVerdict;@JsonKey(name: 'confidence_score') double get confidenceScore;@JsonKey(name: 'xai_report_formatted') String? get xaiReportFormatted;@JsonKey(name: 'comparison_data') Map<String, dynamic>? get comparisonData;// --- New Aggregated Scores ---
@JsonKey(name: 'score_cards') List<ScoreCardItem> get scoreCards;
/// Create a copy of XAIReport
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$XAIReportCopyWith<XAIReport> get copyWith => _$XAIReportCopyWithImpl<XAIReport>(this as XAIReport, _$identity);

  /// Serializes this XAIReport to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is XAIReport&&const DeepCollectionEquality().equals(other.metadata, metadata)&&(identical(other.metodologinenLoki, metodologinenLoki) || other.metodologinenLoki == metodologinenLoki)&&(identical(other.edellisenVaiheenValidointi, edellisenVaiheenValidointi) || other.edellisenVaiheenValidointi == edellisenVaiheenValidointi)&&(identical(other.semanttinenTarkistussumma, semanttinenTarkistussumma) || other.semanttinenTarkistussumma == semanttinenTarkistussumma)&&(identical(other.executiveSummary, executiveSummary) || other.executiveSummary == executiveSummary)&&(identical(other.analysisStrengths, analysisStrengths) || other.analysisStrengths == analysisStrengths)&&(identical(other.analysisWeaknesses, analysisWeaknesses) || other.analysisWeaknesses == analysisWeaknesses)&&(identical(other.analysisOpportunities, analysisOpportunities) || other.analysisOpportunities == analysisOpportunities)&&(identical(other.analysisRecommendations, analysisRecommendations) || other.analysisRecommendations == analysisRecommendations)&&(identical(other.finalVerdict, finalVerdict) || other.finalVerdict == finalVerdict)&&(identical(other.confidenceScore, confidenceScore) || other.confidenceScore == confidenceScore)&&(identical(other.xaiReportFormatted, xaiReportFormatted) || other.xaiReportFormatted == xaiReportFormatted)&&const DeepCollectionEquality().equals(other.comparisonData, comparisonData)&&const DeepCollectionEquality().equals(other.scoreCards, scoreCards));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(metadata),metodologinenLoki,edellisenVaiheenValidointi,semanttinenTarkistussumma,executiveSummary,analysisStrengths,analysisWeaknesses,analysisOpportunities,analysisRecommendations,finalVerdict,confidenceScore,xaiReportFormatted,const DeepCollectionEquality().hash(comparisonData),const DeepCollectionEquality().hash(scoreCards));

@override
String toString() {
  return 'XAIReport(metadata: $metadata, metodologinenLoki: $metodologinenLoki, edellisenVaiheenValidointi: $edellisenVaiheenValidointi, semanttinenTarkistussumma: $semanttinenTarkistussumma, executiveSummary: $executiveSummary, analysisStrengths: $analysisStrengths, analysisWeaknesses: $analysisWeaknesses, analysisOpportunities: $analysisOpportunities, analysisRecommendations: $analysisRecommendations, finalVerdict: $finalVerdict, confidenceScore: $confidenceScore, xaiReportFormatted: $xaiReportFormatted, comparisonData: $comparisonData, scoreCards: $scoreCards)';
}


}

/// @nodoc
abstract mixin class $XAIReportCopyWith<$Res>  {
  factory $XAIReportCopyWith(XAIReport value, $Res Function(XAIReport) _then) = _$XAIReportCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> metadata,@JsonKey(name: 'metodologinen_loki') String metodologinenLoki,@JsonKey(name: 'edellisen_vaiheen_validointi') String edellisenVaiheenValidointi,@JsonKey(name: 'semanttinen_tarkistussumma') String semanttinenTarkistussumma,@JsonKey(name: 'executive_summary') String executiveSummary,@JsonKey(name: 'analysis_strengths') String analysisStrengths,@JsonKey(name: 'analysis_weaknesses') String analysisWeaknesses,@JsonKey(name: 'analysis_opportunities') String analysisOpportunities,@JsonKey(name: 'analysis_recommendations') String analysisRecommendations,@JsonKey(name: 'final_verdict') String finalVerdict,@JsonKey(name: 'confidence_score') double confidenceScore,@JsonKey(name: 'xai_report_formatted') String? xaiReportFormatted,@JsonKey(name: 'comparison_data') Map<String, dynamic>? comparisonData,@JsonKey(name: 'score_cards') List<ScoreCardItem> scoreCards
});




}
/// @nodoc
class _$XAIReportCopyWithImpl<$Res>
    implements $XAIReportCopyWith<$Res> {
  _$XAIReportCopyWithImpl(this._self, this._then);

  final XAIReport _self;
  final $Res Function(XAIReport) _then;

/// Create a copy of XAIReport
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? metadata = null,Object? metodologinenLoki = null,Object? edellisenVaiheenValidointi = null,Object? semanttinenTarkistussumma = null,Object? executiveSummary = null,Object? analysisStrengths = null,Object? analysisWeaknesses = null,Object? analysisOpportunities = null,Object? analysisRecommendations = null,Object? finalVerdict = null,Object? confidenceScore = null,Object? xaiReportFormatted = freezed,Object? comparisonData = freezed,Object? scoreCards = null,}) {
  return _then(_self.copyWith(
metadata: null == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,metodologinenLoki: null == metodologinenLoki ? _self.metodologinenLoki : metodologinenLoki // ignore: cast_nullable_to_non_nullable
as String,edellisenVaiheenValidointi: null == edellisenVaiheenValidointi ? _self.edellisenVaiheenValidointi : edellisenVaiheenValidointi // ignore: cast_nullable_to_non_nullable
as String,semanttinenTarkistussumma: null == semanttinenTarkistussumma ? _self.semanttinenTarkistussumma : semanttinenTarkistussumma // ignore: cast_nullable_to_non_nullable
as String,executiveSummary: null == executiveSummary ? _self.executiveSummary : executiveSummary // ignore: cast_nullable_to_non_nullable
as String,analysisStrengths: null == analysisStrengths ? _self.analysisStrengths : analysisStrengths // ignore: cast_nullable_to_non_nullable
as String,analysisWeaknesses: null == analysisWeaknesses ? _self.analysisWeaknesses : analysisWeaknesses // ignore: cast_nullable_to_non_nullable
as String,analysisOpportunities: null == analysisOpportunities ? _self.analysisOpportunities : analysisOpportunities // ignore: cast_nullable_to_non_nullable
as String,analysisRecommendations: null == analysisRecommendations ? _self.analysisRecommendations : analysisRecommendations // ignore: cast_nullable_to_non_nullable
as String,finalVerdict: null == finalVerdict ? _self.finalVerdict : finalVerdict // ignore: cast_nullable_to_non_nullable
as String,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,xaiReportFormatted: freezed == xaiReportFormatted ? _self.xaiReportFormatted : xaiReportFormatted // ignore: cast_nullable_to_non_nullable
as String?,comparisonData: freezed == comparisonData ? _self.comparisonData : comparisonData // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,scoreCards: null == scoreCards ? _self.scoreCards : scoreCards // ignore: cast_nullable_to_non_nullable
as List<ScoreCardItem>,
  ));
}

}


/// Adds pattern-matching-related methods to [XAIReport].
extension XAIReportPatterns on XAIReport {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _XAIReport value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _XAIReport() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _XAIReport value)  $default,){
final _that = this;
switch (_that) {
case _XAIReport():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _XAIReport value)?  $default,){
final _that = this;
switch (_that) {
case _XAIReport() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Map<String, dynamic> metadata, @JsonKey(name: 'metodologinen_loki')  String metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi')  String edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma')  String semanttinenTarkistussumma, @JsonKey(name: 'executive_summary')  String executiveSummary, @JsonKey(name: 'analysis_strengths')  String analysisStrengths, @JsonKey(name: 'analysis_weaknesses')  String analysisWeaknesses, @JsonKey(name: 'analysis_opportunities')  String analysisOpportunities, @JsonKey(name: 'analysis_recommendations')  String analysisRecommendations, @JsonKey(name: 'final_verdict')  String finalVerdict, @JsonKey(name: 'confidence_score')  double confidenceScore, @JsonKey(name: 'xai_report_formatted')  String? xaiReportFormatted, @JsonKey(name: 'comparison_data')  Map<String, dynamic>? comparisonData, @JsonKey(name: 'score_cards')  List<ScoreCardItem> scoreCards)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _XAIReport() when $default != null:
return $default(_that.metadata,_that.metodologinenLoki,_that.edellisenVaiheenValidointi,_that.semanttinenTarkistussumma,_that.executiveSummary,_that.analysisStrengths,_that.analysisWeaknesses,_that.analysisOpportunities,_that.analysisRecommendations,_that.finalVerdict,_that.confidenceScore,_that.xaiReportFormatted,_that.comparisonData,_that.scoreCards);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Map<String, dynamic> metadata, @JsonKey(name: 'metodologinen_loki')  String metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi')  String edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma')  String semanttinenTarkistussumma, @JsonKey(name: 'executive_summary')  String executiveSummary, @JsonKey(name: 'analysis_strengths')  String analysisStrengths, @JsonKey(name: 'analysis_weaknesses')  String analysisWeaknesses, @JsonKey(name: 'analysis_opportunities')  String analysisOpportunities, @JsonKey(name: 'analysis_recommendations')  String analysisRecommendations, @JsonKey(name: 'final_verdict')  String finalVerdict, @JsonKey(name: 'confidence_score')  double confidenceScore, @JsonKey(name: 'xai_report_formatted')  String? xaiReportFormatted, @JsonKey(name: 'comparison_data')  Map<String, dynamic>? comparisonData, @JsonKey(name: 'score_cards')  List<ScoreCardItem> scoreCards)  $default,) {final _that = this;
switch (_that) {
case _XAIReport():
return $default(_that.metadata,_that.metodologinenLoki,_that.edellisenVaiheenValidointi,_that.semanttinenTarkistussumma,_that.executiveSummary,_that.analysisStrengths,_that.analysisWeaknesses,_that.analysisOpportunities,_that.analysisRecommendations,_that.finalVerdict,_that.confidenceScore,_that.xaiReportFormatted,_that.comparisonData,_that.scoreCards);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Map<String, dynamic> metadata, @JsonKey(name: 'metodologinen_loki')  String metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi')  String edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma')  String semanttinenTarkistussumma, @JsonKey(name: 'executive_summary')  String executiveSummary, @JsonKey(name: 'analysis_strengths')  String analysisStrengths, @JsonKey(name: 'analysis_weaknesses')  String analysisWeaknesses, @JsonKey(name: 'analysis_opportunities')  String analysisOpportunities, @JsonKey(name: 'analysis_recommendations')  String analysisRecommendations, @JsonKey(name: 'final_verdict')  String finalVerdict, @JsonKey(name: 'confidence_score')  double confidenceScore, @JsonKey(name: 'xai_report_formatted')  String? xaiReportFormatted, @JsonKey(name: 'comparison_data')  Map<String, dynamic>? comparisonData, @JsonKey(name: 'score_cards')  List<ScoreCardItem> scoreCards)?  $default,) {final _that = this;
switch (_that) {
case _XAIReport() when $default != null:
return $default(_that.metadata,_that.metodologinenLoki,_that.edellisenVaiheenValidointi,_that.semanttinenTarkistussumma,_that.executiveSummary,_that.analysisStrengths,_that.analysisWeaknesses,_that.analysisOpportunities,_that.analysisRecommendations,_that.finalVerdict,_that.confidenceScore,_that.xaiReportFormatted,_that.comparisonData,_that.scoreCards);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _XAIReport implements XAIReport {
  const _XAIReport({required final  Map<String, dynamic> metadata, @JsonKey(name: 'metodologinen_loki') required this.metodologinenLoki, @JsonKey(name: 'edellisen_vaiheen_validointi') required this.edellisenVaiheenValidointi, @JsonKey(name: 'semanttinen_tarkistussumma') required this.semanttinenTarkistussumma, @JsonKey(name: 'executive_summary') required this.executiveSummary, @JsonKey(name: 'analysis_strengths') required this.analysisStrengths, @JsonKey(name: 'analysis_weaknesses') required this.analysisWeaknesses, @JsonKey(name: 'analysis_opportunities') required this.analysisOpportunities, @JsonKey(name: 'analysis_recommendations') required this.analysisRecommendations, @JsonKey(name: 'final_verdict') required this.finalVerdict, @JsonKey(name: 'confidence_score') required this.confidenceScore, @JsonKey(name: 'xai_report_formatted') this.xaiReportFormatted, @JsonKey(name: 'comparison_data') final  Map<String, dynamic>? comparisonData, @JsonKey(name: 'score_cards') final  List<ScoreCardItem> scoreCards = const []}): _metadata = metadata,_comparisonData = comparisonData,_scoreCards = scoreCards;
  factory _XAIReport.fromJson(Map<String, dynamic> json) => _$XAIReportFromJson(json);

// --- BaseJSON Metadata ---
 final  Map<String, dynamic> _metadata;
// --- BaseJSON Metadata ---
@override Map<String, dynamic> get metadata {
  if (_metadata is EqualUnmodifiableMapView) return _metadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_metadata);
}

@override@JsonKey(name: 'metodologinen_loki') final  String metodologinenLoki;
@override@JsonKey(name: 'edellisen_vaiheen_validointi') final  String edellisenVaiheenValidointi;
@override@JsonKey(name: 'semanttinen_tarkistussumma') final  String semanttinenTarkistussumma;
// --- Report Fields ---
@override@JsonKey(name: 'executive_summary') final  String executiveSummary;
@override@JsonKey(name: 'analysis_strengths') final  String analysisStrengths;
@override@JsonKey(name: 'analysis_weaknesses') final  String analysisWeaknesses;
@override@JsonKey(name: 'analysis_opportunities') final  String analysisOpportunities;
@override@JsonKey(name: 'analysis_recommendations') final  String analysisRecommendations;
@override@JsonKey(name: 'final_verdict') final  String finalVerdict;
@override@JsonKey(name: 'confidence_score') final  double confidenceScore;
@override@JsonKey(name: 'xai_report_formatted') final  String? xaiReportFormatted;
 final  Map<String, dynamic>? _comparisonData;
@override@JsonKey(name: 'comparison_data') Map<String, dynamic>? get comparisonData {
  final value = _comparisonData;
  if (value == null) return null;
  if (_comparisonData is EqualUnmodifiableMapView) return _comparisonData;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// --- New Aggregated Scores ---
 final  List<ScoreCardItem> _scoreCards;
// --- New Aggregated Scores ---
@override@JsonKey(name: 'score_cards') List<ScoreCardItem> get scoreCards {
  if (_scoreCards is EqualUnmodifiableListView) return _scoreCards;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_scoreCards);
}


/// Create a copy of XAIReport
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$XAIReportCopyWith<_XAIReport> get copyWith => __$XAIReportCopyWithImpl<_XAIReport>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$XAIReportToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _XAIReport&&const DeepCollectionEquality().equals(other._metadata, _metadata)&&(identical(other.metodologinenLoki, metodologinenLoki) || other.metodologinenLoki == metodologinenLoki)&&(identical(other.edellisenVaiheenValidointi, edellisenVaiheenValidointi) || other.edellisenVaiheenValidointi == edellisenVaiheenValidointi)&&(identical(other.semanttinenTarkistussumma, semanttinenTarkistussumma) || other.semanttinenTarkistussumma == semanttinenTarkistussumma)&&(identical(other.executiveSummary, executiveSummary) || other.executiveSummary == executiveSummary)&&(identical(other.analysisStrengths, analysisStrengths) || other.analysisStrengths == analysisStrengths)&&(identical(other.analysisWeaknesses, analysisWeaknesses) || other.analysisWeaknesses == analysisWeaknesses)&&(identical(other.analysisOpportunities, analysisOpportunities) || other.analysisOpportunities == analysisOpportunities)&&(identical(other.analysisRecommendations, analysisRecommendations) || other.analysisRecommendations == analysisRecommendations)&&(identical(other.finalVerdict, finalVerdict) || other.finalVerdict == finalVerdict)&&(identical(other.confidenceScore, confidenceScore) || other.confidenceScore == confidenceScore)&&(identical(other.xaiReportFormatted, xaiReportFormatted) || other.xaiReportFormatted == xaiReportFormatted)&&const DeepCollectionEquality().equals(other._comparisonData, _comparisonData)&&const DeepCollectionEquality().equals(other._scoreCards, _scoreCards));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_metadata),metodologinenLoki,edellisenVaiheenValidointi,semanttinenTarkistussumma,executiveSummary,analysisStrengths,analysisWeaknesses,analysisOpportunities,analysisRecommendations,finalVerdict,confidenceScore,xaiReportFormatted,const DeepCollectionEquality().hash(_comparisonData),const DeepCollectionEquality().hash(_scoreCards));

@override
String toString() {
  return 'XAIReport(metadata: $metadata, metodologinenLoki: $metodologinenLoki, edellisenVaiheenValidointi: $edellisenVaiheenValidointi, semanttinenTarkistussumma: $semanttinenTarkistussumma, executiveSummary: $executiveSummary, analysisStrengths: $analysisStrengths, analysisWeaknesses: $analysisWeaknesses, analysisOpportunities: $analysisOpportunities, analysisRecommendations: $analysisRecommendations, finalVerdict: $finalVerdict, confidenceScore: $confidenceScore, xaiReportFormatted: $xaiReportFormatted, comparisonData: $comparisonData, scoreCards: $scoreCards)';
}


}

/// @nodoc
abstract mixin class _$XAIReportCopyWith<$Res> implements $XAIReportCopyWith<$Res> {
  factory _$XAIReportCopyWith(_XAIReport value, $Res Function(_XAIReport) _then) = __$XAIReportCopyWithImpl;
@override @useResult
$Res call({
 Map<String, dynamic> metadata,@JsonKey(name: 'metodologinen_loki') String metodologinenLoki,@JsonKey(name: 'edellisen_vaiheen_validointi') String edellisenVaiheenValidointi,@JsonKey(name: 'semanttinen_tarkistussumma') String semanttinenTarkistussumma,@JsonKey(name: 'executive_summary') String executiveSummary,@JsonKey(name: 'analysis_strengths') String analysisStrengths,@JsonKey(name: 'analysis_weaknesses') String analysisWeaknesses,@JsonKey(name: 'analysis_opportunities') String analysisOpportunities,@JsonKey(name: 'analysis_recommendations') String analysisRecommendations,@JsonKey(name: 'final_verdict') String finalVerdict,@JsonKey(name: 'confidence_score') double confidenceScore,@JsonKey(name: 'xai_report_formatted') String? xaiReportFormatted,@JsonKey(name: 'comparison_data') Map<String, dynamic>? comparisonData,@JsonKey(name: 'score_cards') List<ScoreCardItem> scoreCards
});




}
/// @nodoc
class __$XAIReportCopyWithImpl<$Res>
    implements _$XAIReportCopyWith<$Res> {
  __$XAIReportCopyWithImpl(this._self, this._then);

  final _XAIReport _self;
  final $Res Function(_XAIReport) _then;

/// Create a copy of XAIReport
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? metadata = null,Object? metodologinenLoki = null,Object? edellisenVaiheenValidointi = null,Object? semanttinenTarkistussumma = null,Object? executiveSummary = null,Object? analysisStrengths = null,Object? analysisWeaknesses = null,Object? analysisOpportunities = null,Object? analysisRecommendations = null,Object? finalVerdict = null,Object? confidenceScore = null,Object? xaiReportFormatted = freezed,Object? comparisonData = freezed,Object? scoreCards = null,}) {
  return _then(_XAIReport(
metadata: null == metadata ? _self._metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,metodologinenLoki: null == metodologinenLoki ? _self.metodologinenLoki : metodologinenLoki // ignore: cast_nullable_to_non_nullable
as String,edellisenVaiheenValidointi: null == edellisenVaiheenValidointi ? _self.edellisenVaiheenValidointi : edellisenVaiheenValidointi // ignore: cast_nullable_to_non_nullable
as String,semanttinenTarkistussumma: null == semanttinenTarkistussumma ? _self.semanttinenTarkistussumma : semanttinenTarkistussumma // ignore: cast_nullable_to_non_nullable
as String,executiveSummary: null == executiveSummary ? _self.executiveSummary : executiveSummary // ignore: cast_nullable_to_non_nullable
as String,analysisStrengths: null == analysisStrengths ? _self.analysisStrengths : analysisStrengths // ignore: cast_nullable_to_non_nullable
as String,analysisWeaknesses: null == analysisWeaknesses ? _self.analysisWeaknesses : analysisWeaknesses // ignore: cast_nullable_to_non_nullable
as String,analysisOpportunities: null == analysisOpportunities ? _self.analysisOpportunities : analysisOpportunities // ignore: cast_nullable_to_non_nullable
as String,analysisRecommendations: null == analysisRecommendations ? _self.analysisRecommendations : analysisRecommendations // ignore: cast_nullable_to_non_nullable
as String,finalVerdict: null == finalVerdict ? _self.finalVerdict : finalVerdict // ignore: cast_nullable_to_non_nullable
as String,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,xaiReportFormatted: freezed == xaiReportFormatted ? _self.xaiReportFormatted : xaiReportFormatted // ignore: cast_nullable_to_non_nullable
as String?,comparisonData: freezed == comparisonData ? _self._comparisonData : comparisonData // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,scoreCards: null == scoreCards ? _self._scoreCards : scoreCards // ignore: cast_nullable_to_non_nullable
as List<ScoreCardItem>,
  ));
}


}

// dart format on
