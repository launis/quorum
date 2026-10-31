// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sdui_block_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
SduiBlockDTO _$SduiBlockDTOFromJson(
  Map<String, dynamic> json
) {
        switch (json['block_type']) {
                  case 'paragraph':
          return SduiParagraphBlock.fromJson(
            json
          );
                case 'bullet_list':
          return SduiBulletListBlock.fromJson(
            json
          );
                case 'accordion':
          return SduiAccordionBlock.fromJson(
            json
          );
                case 'alert_box':
          return SduiAlertBoxBlock.fromJson(
            json
          );
                case 'hero_insight':
          return SduiHeroInsightBlock.fromJson(
            json
          );
                case 'markdown':
          return SduiMarkdownBlock.fromJson(
            json
          );
                case 'quote_card':
          return SduiQuoteCardBlock.fromJson(
            json
          );
                case 'warning_card':
          return SduiWarningCardBlock.fromJson(
            json
          );
                case 'n_a_card':
          return SduiNACardBlock.fromJson(
            json
          );
                case 'grid':
          return SduiGridBlock.fromJson(
            json
          );
                case 'metadata':
          return SduiMetadataBlock.fromJson(
            json
          );
                case 'score_card':
          return SduiScoreCardBlock.fromJson(
            json
          );
                case 'audit_trail':
          return SduiAuditTrailBlock.fromJson(
            json
          );
                case '3d_matrix':
          return SduiRadarChartBlock.fromJson(
            json
          );
                case '2d_compare':
          return SduiScatterPlotBlock.fromJson(
            json
          );
                case 'quadrant_matrix':
          return SduiQuadrantMatrixBlock.fromJson(
            json
          );
                case '1d_metrics':
          return SduiMetrics1DBlock.fromJson(
            json
          );
                case 'matrix_summary':
          return SduiMatrixTableBlock.fromJson(
            json
          );
                case 'causal_graph':
          return SduiCausalGraphBlock.fromJson(
            json
          );
        
          default:
            throw CheckedFromJsonException(
  json,
  'block_type',
  'SduiBlockDTO',
  'Invalid union type "${json['block_type']}"!'
);
        }
      
}

/// @nodoc
mixin _$SduiBlockDTO {

 String? get id;
/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBlockDTOCopyWith<SduiBlockDTO> get copyWith => _$SduiBlockDTOCopyWithImpl<SduiBlockDTO>(this as SduiBlockDTO, _$identity);

  /// Serializes this SduiBlockDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SduiBlockDTO(id: $id)';
}


}

/// @nodoc
abstract mixin class $SduiBlockDTOCopyWith<$Res>  {
  factory $SduiBlockDTOCopyWith(SduiBlockDTO value, $Res Function(SduiBlockDTO) _then) = _$SduiBlockDTOCopyWithImpl;
@useResult
$Res call({
 String? id
});




}
/// @nodoc
class _$SduiBlockDTOCopyWithImpl<$Res>
    implements $SduiBlockDTOCopyWith<$Res> {
  _$SduiBlockDTOCopyWithImpl(this._self, this._then);

  final SduiBlockDTO _self;
  final $Res Function(SduiBlockDTO) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,}) {
  return _then(_self.copyWith(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SduiBlockDTO].
extension SduiBlockDTOPatterns on SduiBlockDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( SduiParagraphBlock value)?  paragraph,TResult Function( SduiBulletListBlock value)?  bulletList,TResult Function( SduiAccordionBlock value)?  accordion,TResult Function( SduiAlertBoxBlock value)?  alertBox,TResult Function( SduiHeroInsightBlock value)?  heroInsight,TResult Function( SduiMarkdownBlock value)?  markdown,TResult Function( SduiQuoteCardBlock value)?  quoteCard,TResult Function( SduiWarningCardBlock value)?  warningCard,TResult Function( SduiNACardBlock value)?  nACard,TResult Function( SduiGridBlock value)?  grid,TResult Function( SduiMetadataBlock value)?  metadata,TResult Function( SduiScoreCardBlock value)?  scoreCard,TResult Function( SduiAuditTrailBlock value)?  auditTrail,TResult Function( SduiRadarChartBlock value)?  matrix3d,TResult Function( SduiScatterPlotBlock value)?  compare2d,TResult Function( SduiQuadrantMatrixBlock value)?  quadrantMatrix,TResult Function( SduiMetrics1DBlock value)?  metrics1d,TResult Function( SduiMatrixTableBlock value)?  matrixSummary,TResult Function( SduiCausalGraphBlock value)?  causalGraph,required TResult orElse(),}){
final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that);case SduiAccordionBlock() when accordion != null:
return accordion(_that);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that);case SduiMarkdownBlock() when markdown != null:
return markdown(_that);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that);case SduiNACardBlock() when nACard != null:
return nACard(_that);case SduiGridBlock() when grid != null:
return grid(_that);case SduiMetadataBlock() when metadata != null:
return metadata(_that);case SduiScoreCardBlock() when scoreCard != null:
return scoreCard(_that);case SduiAuditTrailBlock() when auditTrail != null:
return auditTrail(_that);case SduiRadarChartBlock() when matrix3d != null:
return matrix3d(_that);case SduiScatterPlotBlock() when compare2d != null:
return compare2d(_that);case SduiQuadrantMatrixBlock() when quadrantMatrix != null:
return quadrantMatrix(_that);case SduiMetrics1DBlock() when metrics1d != null:
return metrics1d(_that);case SduiMatrixTableBlock() when matrixSummary != null:
return matrixSummary(_that);case SduiCausalGraphBlock() when causalGraph != null:
return causalGraph(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( SduiParagraphBlock value)  paragraph,required TResult Function( SduiBulletListBlock value)  bulletList,required TResult Function( SduiAccordionBlock value)  accordion,required TResult Function( SduiAlertBoxBlock value)  alertBox,required TResult Function( SduiHeroInsightBlock value)  heroInsight,required TResult Function( SduiMarkdownBlock value)  markdown,required TResult Function( SduiQuoteCardBlock value)  quoteCard,required TResult Function( SduiWarningCardBlock value)  warningCard,required TResult Function( SduiNACardBlock value)  nACard,required TResult Function( SduiGridBlock value)  grid,required TResult Function( SduiMetadataBlock value)  metadata,required TResult Function( SduiScoreCardBlock value)  scoreCard,required TResult Function( SduiAuditTrailBlock value)  auditTrail,required TResult Function( SduiRadarChartBlock value)  matrix3d,required TResult Function( SduiScatterPlotBlock value)  compare2d,required TResult Function( SduiQuadrantMatrixBlock value)  quadrantMatrix,required TResult Function( SduiMetrics1DBlock value)  metrics1d,required TResult Function( SduiMatrixTableBlock value)  matrixSummary,required TResult Function( SduiCausalGraphBlock value)  causalGraph,}){
final _that = this;
switch (_that) {
case SduiParagraphBlock():
return paragraph(_that);case SduiBulletListBlock():
return bulletList(_that);case SduiAccordionBlock():
return accordion(_that);case SduiAlertBoxBlock():
return alertBox(_that);case SduiHeroInsightBlock():
return heroInsight(_that);case SduiMarkdownBlock():
return markdown(_that);case SduiQuoteCardBlock():
return quoteCard(_that);case SduiWarningCardBlock():
return warningCard(_that);case SduiNACardBlock():
return nACard(_that);case SduiGridBlock():
return grid(_that);case SduiMetadataBlock():
return metadata(_that);case SduiScoreCardBlock():
return scoreCard(_that);case SduiAuditTrailBlock():
return auditTrail(_that);case SduiRadarChartBlock():
return matrix3d(_that);case SduiScatterPlotBlock():
return compare2d(_that);case SduiQuadrantMatrixBlock():
return quadrantMatrix(_that);case SduiMetrics1DBlock():
return metrics1d(_that);case SduiMatrixTableBlock():
return matrixSummary(_that);case SduiCausalGraphBlock():
return causalGraph(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( SduiParagraphBlock value)?  paragraph,TResult? Function( SduiBulletListBlock value)?  bulletList,TResult? Function( SduiAccordionBlock value)?  accordion,TResult? Function( SduiAlertBoxBlock value)?  alertBox,TResult? Function( SduiHeroInsightBlock value)?  heroInsight,TResult? Function( SduiMarkdownBlock value)?  markdown,TResult? Function( SduiQuoteCardBlock value)?  quoteCard,TResult? Function( SduiWarningCardBlock value)?  warningCard,TResult? Function( SduiNACardBlock value)?  nACard,TResult? Function( SduiGridBlock value)?  grid,TResult? Function( SduiMetadataBlock value)?  metadata,TResult? Function( SduiScoreCardBlock value)?  scoreCard,TResult? Function( SduiAuditTrailBlock value)?  auditTrail,TResult? Function( SduiRadarChartBlock value)?  matrix3d,TResult? Function( SduiScatterPlotBlock value)?  compare2d,TResult? Function( SduiQuadrantMatrixBlock value)?  quadrantMatrix,TResult? Function( SduiMetrics1DBlock value)?  metrics1d,TResult? Function( SduiMatrixTableBlock value)?  matrixSummary,TResult? Function( SduiCausalGraphBlock value)?  causalGraph,}){
final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that);case SduiAccordionBlock() when accordion != null:
return accordion(_that);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that);case SduiMarkdownBlock() when markdown != null:
return markdown(_that);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that);case SduiNACardBlock() when nACard != null:
return nACard(_that);case SduiGridBlock() when grid != null:
return grid(_that);case SduiMetadataBlock() when metadata != null:
return metadata(_that);case SduiScoreCardBlock() when scoreCard != null:
return scoreCard(_that);case SduiAuditTrailBlock() when auditTrail != null:
return auditTrail(_that);case SduiRadarChartBlock() when matrix3d != null:
return matrix3d(_that);case SduiScatterPlotBlock() when compare2d != null:
return compare2d(_that);case SduiQuadrantMatrixBlock() when quadrantMatrix != null:
return quadrantMatrix(_that);case SduiMetrics1DBlock() when metrics1d != null:
return metrics1d(_that);case SduiMatrixTableBlock() when matrixSummary != null:
return matrixSummary(_that);case SduiCausalGraphBlock() when causalGraph != null:
return causalGraph(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  paragraph,TResult Function( String? id,  List<SduiBulletListItemDTO> items)?  bulletList,TResult Function( String? id,  String title,  String severity, @JsonKey(name: 'icon_name')  String? iconName,  List<SduiBlockDTO> children)?  accordion,TResult Function( String? id,  String text,  AlertSeverity severity,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  alertBox,TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  heroInsight,TResult Function( String? id,  String text)?  markdown,TResult Function( String? id,  String quote, @JsonKey(name: 'source_aliases')  List<String> sourceAliases,  List<int> citations)?  quoteCard,TResult Function( String? id,  String message, @JsonKey(name: 'quote_text')  String? quoteText)?  warningCard,TResult Function( String? id, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds,  String message)?  nACard,TResult Function( String? id,  List<SduiBlockDTO> items)?  grid,TResult Function( String? id,  String title,  List<String> badges, @JsonKey(name: 'metadata_lines')  List<String> metadataLines,  String? costs,  Map<String, String>? tokens, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd)?  metadata,TResult Function( String? id, @JsonKey(name: 'global_score')  double? globalScore)?  scoreCard,TResult Function( String? id)?  auditTrail,TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  matrix3d,TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  compare2d,TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  quadrantMatrix,TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  metrics1d,TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels, @JsonKey(name: 'extension_labels')  Map<XaiExtensionType, I18nText> extensionLabels, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'short_circuited_by_claims')  List<String> shortCircuitedByClaims, @JsonKey(name: 'falsified_warrant_claims')  List<String> falsifiedWarrantClaims)?  matrixSummary,TResult Function( String? id, @JsonKey(name: 'critical_path_nodes')  List<CausalNodeDto> criticalPathNodes, @JsonKey(name: 'critical_edges')  List<CausalEdgeDto> criticalEdges, @JsonKey(name: 'root_cause_diagnoses')  List<CausalRootCauseDiagnosisDto> rootCauseDiagnoses, @JsonKey(name: 'anti_fluff_audit')  AntiFluffAuditDto antiFluffAudit, @JsonKey(name: 'prescriptive_remediations')  List<PrescriptiveRemediationDto> prescriptiveRemediations, @JsonKey(name: 'fair_scoring')  FairScoringBreakdownDto? fairScoring, @JsonKey(name: 'intact_claims_count')  int intactClaimsCount, @JsonKey(name: 'total_claims_count')  int totalClaimsCount,  I18nText summary, @JsonKey(name: 'short_circuited_by_claims')  List<String> shortCircuitedByClaims, @JsonKey(name: 'falsified_warrant_claims')  List<String> falsifiedWarrantClaims)?  causalGraph,required TResult orElse(),}) {final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that.id,_that.items);case SduiAccordionBlock() when accordion != null:
return accordion(_that.id,_that.title,_that.severity,_that.iconName,_that.children);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that.id,_that.text,_that.severity,_that.citations,_that.exactQuotes);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiMarkdownBlock() when markdown != null:
return markdown(_that.id,_that.text);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that.id,_that.quote,_that.sourceAliases,_that.citations);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that.id,_that.message,_that.quoteText);case SduiNACardBlock() when nACard != null:
return nACard(_that.id,_that.shortCircuitReasonTdaIds,_that.message);case SduiGridBlock() when grid != null:
return grid(_that.id,_that.items);case SduiMetadataBlock() when metadata != null:
return metadata(_that.id,_that.title,_that.badges,_that.metadataLines,_that.costs,_that.tokens,_that.customPrefaceMd);case SduiScoreCardBlock() when scoreCard != null:
return scoreCard(_that.id,_that.globalScore);case SduiAuditTrailBlock() when auditTrail != null:
return auditTrail(_that.id);case SduiRadarChartBlock() when matrix3d != null:
return matrix3d(_that.id,_that.title,_that.axes);case SduiScatterPlotBlock() when compare2d != null:
return compare2d(_that.id,_that.title,_that.axes);case SduiQuadrantMatrixBlock() when quadrantMatrix != null:
return quadrantMatrix(_that.id,_that.title,_that.axes);case SduiMetrics1DBlock() when metrics1d != null:
return metrics1d(_that.id,_that.title,_that.axes);case SduiMatrixTableBlock() when matrixSummary != null:
return matrixSummary(_that.id,_that.title,_that.axes,_that.matrixColumnLabels,_that.extensionLabels,_that.matrixVisibleColumns,_that.shortCircuitedByClaims,_that.falsifiedWarrantClaims);case SduiCausalGraphBlock() when causalGraph != null:
return causalGraph(_that.id,_that.criticalPathNodes,_that.criticalEdges,_that.rootCauseDiagnoses,_that.antiFluffAudit,_that.prescriptiveRemediations,_that.fairScoring,_that.intactClaimsCount,_that.totalClaimsCount,_that.summary,_that.shortCircuitedByClaims,_that.falsifiedWarrantClaims);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  paragraph,required TResult Function( String? id,  List<SduiBulletListItemDTO> items)  bulletList,required TResult Function( String? id,  String title,  String severity, @JsonKey(name: 'icon_name')  String? iconName,  List<SduiBlockDTO> children)  accordion,required TResult Function( String? id,  String text,  AlertSeverity severity,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  alertBox,required TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  heroInsight,required TResult Function( String? id,  String text)  markdown,required TResult Function( String? id,  String quote, @JsonKey(name: 'source_aliases')  List<String> sourceAliases,  List<int> citations)  quoteCard,required TResult Function( String? id,  String message, @JsonKey(name: 'quote_text')  String? quoteText)  warningCard,required TResult Function( String? id, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds,  String message)  nACard,required TResult Function( String? id,  List<SduiBlockDTO> items)  grid,required TResult Function( String? id,  String title,  List<String> badges, @JsonKey(name: 'metadata_lines')  List<String> metadataLines,  String? costs,  Map<String, String>? tokens, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd)  metadata,required TResult Function( String? id, @JsonKey(name: 'global_score')  double? globalScore)  scoreCard,required TResult Function( String? id)  auditTrail,required TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)  matrix3d,required TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)  compare2d,required TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)  quadrantMatrix,required TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)  metrics1d,required TResult Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels, @JsonKey(name: 'extension_labels')  Map<XaiExtensionType, I18nText> extensionLabels, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'short_circuited_by_claims')  List<String> shortCircuitedByClaims, @JsonKey(name: 'falsified_warrant_claims')  List<String> falsifiedWarrantClaims)  matrixSummary,required TResult Function( String? id, @JsonKey(name: 'critical_path_nodes')  List<CausalNodeDto> criticalPathNodes, @JsonKey(name: 'critical_edges')  List<CausalEdgeDto> criticalEdges, @JsonKey(name: 'root_cause_diagnoses')  List<CausalRootCauseDiagnosisDto> rootCauseDiagnoses, @JsonKey(name: 'anti_fluff_audit')  AntiFluffAuditDto antiFluffAudit, @JsonKey(name: 'prescriptive_remediations')  List<PrescriptiveRemediationDto> prescriptiveRemediations, @JsonKey(name: 'fair_scoring')  FairScoringBreakdownDto? fairScoring, @JsonKey(name: 'intact_claims_count')  int intactClaimsCount, @JsonKey(name: 'total_claims_count')  int totalClaimsCount,  I18nText summary, @JsonKey(name: 'short_circuited_by_claims')  List<String> shortCircuitedByClaims, @JsonKey(name: 'falsified_warrant_claims')  List<String> falsifiedWarrantClaims)  causalGraph,}) {final _that = this;
switch (_that) {
case SduiParagraphBlock():
return paragraph(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiBulletListBlock():
return bulletList(_that.id,_that.items);case SduiAccordionBlock():
return accordion(_that.id,_that.title,_that.severity,_that.iconName,_that.children);case SduiAlertBoxBlock():
return alertBox(_that.id,_that.text,_that.severity,_that.citations,_that.exactQuotes);case SduiHeroInsightBlock():
return heroInsight(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiMarkdownBlock():
return markdown(_that.id,_that.text);case SduiQuoteCardBlock():
return quoteCard(_that.id,_that.quote,_that.sourceAliases,_that.citations);case SduiWarningCardBlock():
return warningCard(_that.id,_that.message,_that.quoteText);case SduiNACardBlock():
return nACard(_that.id,_that.shortCircuitReasonTdaIds,_that.message);case SduiGridBlock():
return grid(_that.id,_that.items);case SduiMetadataBlock():
return metadata(_that.id,_that.title,_that.badges,_that.metadataLines,_that.costs,_that.tokens,_that.customPrefaceMd);case SduiScoreCardBlock():
return scoreCard(_that.id,_that.globalScore);case SduiAuditTrailBlock():
return auditTrail(_that.id);case SduiRadarChartBlock():
return matrix3d(_that.id,_that.title,_that.axes);case SduiScatterPlotBlock():
return compare2d(_that.id,_that.title,_that.axes);case SduiQuadrantMatrixBlock():
return quadrantMatrix(_that.id,_that.title,_that.axes);case SduiMetrics1DBlock():
return metrics1d(_that.id,_that.title,_that.axes);case SduiMatrixTableBlock():
return matrixSummary(_that.id,_that.title,_that.axes,_that.matrixColumnLabels,_that.extensionLabels,_that.matrixVisibleColumns,_that.shortCircuitedByClaims,_that.falsifiedWarrantClaims);case SduiCausalGraphBlock():
return causalGraph(_that.id,_that.criticalPathNodes,_that.criticalEdges,_that.rootCauseDiagnoses,_that.antiFluffAudit,_that.prescriptiveRemediations,_that.fairScoring,_that.intactClaimsCount,_that.totalClaimsCount,_that.summary,_that.shortCircuitedByClaims,_that.falsifiedWarrantClaims);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  paragraph,TResult? Function( String? id,  List<SduiBulletListItemDTO> items)?  bulletList,TResult? Function( String? id,  String title,  String severity, @JsonKey(name: 'icon_name')  String? iconName,  List<SduiBlockDTO> children)?  accordion,TResult? Function( String? id,  String text,  AlertSeverity severity,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  alertBox,TResult? Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  heroInsight,TResult? Function( String? id,  String text)?  markdown,TResult? Function( String? id,  String quote, @JsonKey(name: 'source_aliases')  List<String> sourceAliases,  List<int> citations)?  quoteCard,TResult? Function( String? id,  String message, @JsonKey(name: 'quote_text')  String? quoteText)?  warningCard,TResult? Function( String? id, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds,  String message)?  nACard,TResult? Function( String? id,  List<SduiBlockDTO> items)?  grid,TResult? Function( String? id,  String title,  List<String> badges, @JsonKey(name: 'metadata_lines')  List<String> metadataLines,  String? costs,  Map<String, String>? tokens, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd)?  metadata,TResult? Function( String? id, @JsonKey(name: 'global_score')  double? globalScore)?  scoreCard,TResult? Function( String? id)?  auditTrail,TResult? Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  matrix3d,TResult? Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  compare2d,TResult? Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  quadrantMatrix,TResult? Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes)?  metrics1d,TResult? Function( String? id,  I18nText? title,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels, @JsonKey(name: 'extension_labels')  Map<XaiExtensionType, I18nText> extensionLabels, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'short_circuited_by_claims')  List<String> shortCircuitedByClaims, @JsonKey(name: 'falsified_warrant_claims')  List<String> falsifiedWarrantClaims)?  matrixSummary,TResult? Function( String? id, @JsonKey(name: 'critical_path_nodes')  List<CausalNodeDto> criticalPathNodes, @JsonKey(name: 'critical_edges')  List<CausalEdgeDto> criticalEdges, @JsonKey(name: 'root_cause_diagnoses')  List<CausalRootCauseDiagnosisDto> rootCauseDiagnoses, @JsonKey(name: 'anti_fluff_audit')  AntiFluffAuditDto antiFluffAudit, @JsonKey(name: 'prescriptive_remediations')  List<PrescriptiveRemediationDto> prescriptiveRemediations, @JsonKey(name: 'fair_scoring')  FairScoringBreakdownDto? fairScoring, @JsonKey(name: 'intact_claims_count')  int intactClaimsCount, @JsonKey(name: 'total_claims_count')  int totalClaimsCount,  I18nText summary, @JsonKey(name: 'short_circuited_by_claims')  List<String> shortCircuitedByClaims, @JsonKey(name: 'falsified_warrant_claims')  List<String> falsifiedWarrantClaims)?  causalGraph,}) {final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that.id,_that.items);case SduiAccordionBlock() when accordion != null:
return accordion(_that.id,_that.title,_that.severity,_that.iconName,_that.children);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that.id,_that.text,_that.severity,_that.citations,_that.exactQuotes);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiMarkdownBlock() when markdown != null:
return markdown(_that.id,_that.text);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that.id,_that.quote,_that.sourceAliases,_that.citations);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that.id,_that.message,_that.quoteText);case SduiNACardBlock() when nACard != null:
return nACard(_that.id,_that.shortCircuitReasonTdaIds,_that.message);case SduiGridBlock() when grid != null:
return grid(_that.id,_that.items);case SduiMetadataBlock() when metadata != null:
return metadata(_that.id,_that.title,_that.badges,_that.metadataLines,_that.costs,_that.tokens,_that.customPrefaceMd);case SduiScoreCardBlock() when scoreCard != null:
return scoreCard(_that.id,_that.globalScore);case SduiAuditTrailBlock() when auditTrail != null:
return auditTrail(_that.id);case SduiRadarChartBlock() when matrix3d != null:
return matrix3d(_that.id,_that.title,_that.axes);case SduiScatterPlotBlock() when compare2d != null:
return compare2d(_that.id,_that.title,_that.axes);case SduiQuadrantMatrixBlock() when quadrantMatrix != null:
return quadrantMatrix(_that.id,_that.title,_that.axes);case SduiMetrics1DBlock() when metrics1d != null:
return metrics1d(_that.id,_that.title,_that.axes);case SduiMatrixTableBlock() when matrixSummary != null:
return matrixSummary(_that.id,_that.title,_that.axes,_that.matrixColumnLabels,_that.extensionLabels,_that.matrixVisibleColumns,_that.shortCircuitedByClaims,_that.falsifiedWarrantClaims);case SduiCausalGraphBlock() when causalGraph != null:
return causalGraph(_that.id,_that.criticalPathNodes,_that.criticalEdges,_that.rootCauseDiagnoses,_that.antiFluffAudit,_that.prescriptiveRemediations,_that.fairScoring,_that.intactClaimsCount,_that.totalClaimsCount,_that.summary,_that.shortCircuitedByClaims,_that.falsifiedWarrantClaims);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiParagraphBlock extends SduiBlockDTO {
  const SduiParagraphBlock({this.id, required this.text, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const [], final  String? $type}): _citations = citations,_exactQuotes = exactQuotes,$type = $type ?? 'paragraph',super._();
  factory SduiParagraphBlock.fromJson(Map<String, dynamic> json) => _$SduiParagraphBlockFromJson(json);

@override final  String? id;
 final  String text;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiParagraphBlockCopyWith<SduiParagraphBlock> get copyWith => _$SduiParagraphBlockCopyWithImpl<SduiParagraphBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiParagraphBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.paragraph(id: $id, text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiParagraphBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiParagraphBlockCopyWith(SduiParagraphBlock value, $Res Function(SduiParagraphBlock) _then) = _$SduiParagraphBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
});




}
/// @nodoc
class _$SduiParagraphBlockCopyWithImpl<$Res>
    implements $SduiParagraphBlockCopyWith<$Res> {
  _$SduiParagraphBlockCopyWithImpl(this._self, this._then);

  final SduiParagraphBlock _self;
  final $Res Function(SduiParagraphBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(SduiParagraphBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiBulletListBlock extends SduiBlockDTO {
  const SduiBulletListBlock({this.id, required final  List<SduiBulletListItemDTO> items, final  String? $type}): _items = items,$type = $type ?? 'bullet_list',super._();
  factory SduiBulletListBlock.fromJson(Map<String, dynamic> json) => _$SduiBulletListBlockFromJson(json);

@override final  String? id;
 final  List<SduiBulletListItemDTO> _items;
 List<SduiBulletListItemDTO> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBulletListBlockCopyWith<SduiBulletListBlock> get copyWith => _$SduiBulletListBlockCopyWithImpl<SduiBulletListBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiBulletListBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.bulletList(id: $id, items: $items)';
}


}

/// @nodoc
abstract mixin class $SduiBulletListBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiBulletListBlockCopyWith(SduiBulletListBlock value, $Res Function(SduiBulletListBlock) _then) = _$SduiBulletListBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, List<SduiBulletListItemDTO> items
});




}
/// @nodoc
class _$SduiBulletListBlockCopyWithImpl<$Res>
    implements $SduiBulletListBlockCopyWith<$Res> {
  _$SduiBulletListBlockCopyWithImpl(this._self, this._then);

  final SduiBulletListBlock _self;
  final $Res Function(SduiBulletListBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? items = null,}) {
  return _then(SduiBulletListBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<SduiBulletListItemDTO>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiAccordionBlock extends SduiBlockDTO {
  const SduiAccordionBlock({this.id, required this.title, this.severity = 'default', @JsonKey(name: 'icon_name') this.iconName, final  List<SduiBlockDTO> children = const [], final  String? $type}): _children = children,$type = $type ?? 'accordion',super._();
  factory SduiAccordionBlock.fromJson(Map<String, dynamic> json) => _$SduiAccordionBlockFromJson(json);

@override final  String? id;
 final  String title;
@JsonKey() final  String severity;
@JsonKey(name: 'icon_name') final  String? iconName;
 final  List<SduiBlockDTO> _children;
@JsonKey() List<SduiBlockDTO> get children {
  if (_children is EqualUnmodifiableListView) return _children;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_children);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiAccordionBlockCopyWith<SduiAccordionBlock> get copyWith => _$SduiAccordionBlockCopyWithImpl<SduiAccordionBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiAccordionBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.accordion(id: $id, title: $title, severity: $severity, iconName: $iconName, children: $children)';
}


}

/// @nodoc
abstract mixin class $SduiAccordionBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiAccordionBlockCopyWith(SduiAccordionBlock value, $Res Function(SduiAccordionBlock) _then) = _$SduiAccordionBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String title, String severity,@JsonKey(name: 'icon_name') String? iconName, List<SduiBlockDTO> children
});




}
/// @nodoc
class _$SduiAccordionBlockCopyWithImpl<$Res>
    implements $SduiAccordionBlockCopyWith<$Res> {
  _$SduiAccordionBlockCopyWithImpl(this._self, this._then);

  final SduiAccordionBlock _self;
  final $Res Function(SduiAccordionBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = null,Object? severity = null,Object? iconName = freezed,Object? children = null,}) {
  return _then(SduiAccordionBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,iconName: freezed == iconName ? _self.iconName : iconName // ignore: cast_nullable_to_non_nullable
as String?,children: null == children ? _self._children : children // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiAlertBoxBlock extends SduiBlockDTO {
  const SduiAlertBoxBlock({this.id, required this.text, required this.severity, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const [], final  String? $type}): _citations = citations,_exactQuotes = exactQuotes,$type = $type ?? 'alert_box',super._();
  factory SduiAlertBoxBlock.fromJson(Map<String, dynamic> json) => _$SduiAlertBoxBlockFromJson(json);

@override final  String? id;
 final  String text;
 final  AlertSeverity severity;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiAlertBoxBlockCopyWith<SduiAlertBoxBlock> get copyWith => _$SduiAlertBoxBlockCopyWithImpl<SduiAlertBoxBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiAlertBoxBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.alertBox(id: $id, text: $text, severity: $severity, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiAlertBoxBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiAlertBoxBlockCopyWith(SduiAlertBoxBlock value, $Res Function(SduiAlertBoxBlock) _then) = _$SduiAlertBoxBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text, AlertSeverity severity, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
});




}
/// @nodoc
class _$SduiAlertBoxBlockCopyWithImpl<$Res>
    implements $SduiAlertBoxBlockCopyWith<$Res> {
  _$SduiAlertBoxBlockCopyWithImpl(this._self, this._then);

  final SduiAlertBoxBlock _self;
  final $Res Function(SduiAlertBoxBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,Object? severity = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(SduiAlertBoxBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as AlertSeverity,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiHeroInsightBlock extends SduiBlockDTO {
  const SduiHeroInsightBlock({this.id, required this.text, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const [], final  String? $type}): _citations = citations,_exactQuotes = exactQuotes,$type = $type ?? 'hero_insight',super._();
  factory SduiHeroInsightBlock.fromJson(Map<String, dynamic> json) => _$SduiHeroInsightBlockFromJson(json);

@override final  String? id;
 final  String text;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiHeroInsightBlockCopyWith<SduiHeroInsightBlock> get copyWith => _$SduiHeroInsightBlockCopyWithImpl<SduiHeroInsightBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiHeroInsightBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.heroInsight(id: $id, text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiHeroInsightBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiHeroInsightBlockCopyWith(SduiHeroInsightBlock value, $Res Function(SduiHeroInsightBlock) _then) = _$SduiHeroInsightBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
});




}
/// @nodoc
class _$SduiHeroInsightBlockCopyWithImpl<$Res>
    implements $SduiHeroInsightBlockCopyWith<$Res> {
  _$SduiHeroInsightBlockCopyWithImpl(this._self, this._then);

  final SduiHeroInsightBlock _self;
  final $Res Function(SduiHeroInsightBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(SduiHeroInsightBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiMarkdownBlock extends SduiBlockDTO {
  const SduiMarkdownBlock({this.id, required this.text, final  String? $type}): $type = $type ?? 'markdown',super._();
  factory SduiMarkdownBlock.fromJson(Map<String, dynamic> json) => _$SduiMarkdownBlockFromJson(json);

@override final  String? id;
 final  String text;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiMarkdownBlockCopyWith<SduiMarkdownBlock> get copyWith => _$SduiMarkdownBlockCopyWithImpl<SduiMarkdownBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiMarkdownBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.markdown(id: $id, text: $text)';
}


}

/// @nodoc
abstract mixin class $SduiMarkdownBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiMarkdownBlockCopyWith(SduiMarkdownBlock value, $Res Function(SduiMarkdownBlock) _then) = _$SduiMarkdownBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text
});




}
/// @nodoc
class _$SduiMarkdownBlockCopyWithImpl<$Res>
    implements $SduiMarkdownBlockCopyWith<$Res> {
  _$SduiMarkdownBlockCopyWithImpl(this._self, this._then);

  final SduiMarkdownBlock _self;
  final $Res Function(SduiMarkdownBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,}) {
  return _then(SduiMarkdownBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiQuoteCardBlock extends SduiBlockDTO {
  const SduiQuoteCardBlock({this.id, required this.quote, @JsonKey(name: 'source_aliases') required final  List<String> sourceAliases, required final  List<int> citations, final  String? $type}): _sourceAliases = sourceAliases,_citations = citations,$type = $type ?? 'quote_card',super._();
  factory SduiQuoteCardBlock.fromJson(Map<String, dynamic> json) => _$SduiQuoteCardBlockFromJson(json);

@override final  String? id;
 final  String quote;
 final  List<String> _sourceAliases;
@JsonKey(name: 'source_aliases') List<String> get sourceAliases {
  if (_sourceAliases is EqualUnmodifiableListView) return _sourceAliases;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sourceAliases);
}

 final  List<int> _citations;
 List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiQuoteCardBlockCopyWith<SduiQuoteCardBlock> get copyWith => _$SduiQuoteCardBlockCopyWithImpl<SduiQuoteCardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiQuoteCardBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.quoteCard(id: $id, quote: $quote, sourceAliases: $sourceAliases, citations: $citations)';
}


}

/// @nodoc
abstract mixin class $SduiQuoteCardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiQuoteCardBlockCopyWith(SduiQuoteCardBlock value, $Res Function(SduiQuoteCardBlock) _then) = _$SduiQuoteCardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String quote,@JsonKey(name: 'source_aliases') List<String> sourceAliases, List<int> citations
});




}
/// @nodoc
class _$SduiQuoteCardBlockCopyWithImpl<$Res>
    implements $SduiQuoteCardBlockCopyWith<$Res> {
  _$SduiQuoteCardBlockCopyWithImpl(this._self, this._then);

  final SduiQuoteCardBlock _self;
  final $Res Function(SduiQuoteCardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? quote = null,Object? sourceAliases = null,Object? citations = null,}) {
  return _then(SduiQuoteCardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,quote: null == quote ? _self.quote : quote // ignore: cast_nullable_to_non_nullable
as String,sourceAliases: null == sourceAliases ? _self._sourceAliases : sourceAliases // ignore: cast_nullable_to_non_nullable
as List<String>,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiWarningCardBlock extends SduiBlockDTO {
  const SduiWarningCardBlock({this.id, required this.message, @JsonKey(name: 'quote_text') this.quoteText, final  String? $type}): $type = $type ?? 'warning_card',super._();
  factory SduiWarningCardBlock.fromJson(Map<String, dynamic> json) => _$SduiWarningCardBlockFromJson(json);

@override final  String? id;
 final  String message;
@JsonKey(name: 'quote_text') final  String? quoteText;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiWarningCardBlockCopyWith<SduiWarningCardBlock> get copyWith => _$SduiWarningCardBlockCopyWithImpl<SduiWarningCardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiWarningCardBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.warningCard(id: $id, message: $message, quoteText: $quoteText)';
}


}

/// @nodoc
abstract mixin class $SduiWarningCardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiWarningCardBlockCopyWith(SduiWarningCardBlock value, $Res Function(SduiWarningCardBlock) _then) = _$SduiWarningCardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String message,@JsonKey(name: 'quote_text') String? quoteText
});




}
/// @nodoc
class _$SduiWarningCardBlockCopyWithImpl<$Res>
    implements $SduiWarningCardBlockCopyWith<$Res> {
  _$SduiWarningCardBlockCopyWithImpl(this._self, this._then);

  final SduiWarningCardBlock _self;
  final $Res Function(SduiWarningCardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? message = null,Object? quoteText = freezed,}) {
  return _then(SduiWarningCardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,quoteText: freezed == quoteText ? _self.quoteText : quoteText // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiNACardBlock extends SduiBlockDTO {
  const SduiNACardBlock({this.id, @JsonKey(name: 'short_circuit_reason_tda_ids') required final  List<String> shortCircuitReasonTdaIds, required this.message, final  String? $type}): _shortCircuitReasonTdaIds = shortCircuitReasonTdaIds,$type = $type ?? 'n_a_card',super._();
  factory SduiNACardBlock.fromJson(Map<String, dynamic> json) => _$SduiNACardBlockFromJson(json);

@override final  String? id;
 final  List<String> _shortCircuitReasonTdaIds;
@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> get shortCircuitReasonTdaIds {
  if (_shortCircuitReasonTdaIds is EqualUnmodifiableListView) return _shortCircuitReasonTdaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortCircuitReasonTdaIds);
}

 final  String message;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiNACardBlockCopyWith<SduiNACardBlock> get copyWith => _$SduiNACardBlockCopyWithImpl<SduiNACardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiNACardBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.nACard(id: $id, shortCircuitReasonTdaIds: $shortCircuitReasonTdaIds, message: $message)';
}


}

/// @nodoc
abstract mixin class $SduiNACardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiNACardBlockCopyWith(SduiNACardBlock value, $Res Function(SduiNACardBlock) _then) = _$SduiNACardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> shortCircuitReasonTdaIds, String message
});




}
/// @nodoc
class _$SduiNACardBlockCopyWithImpl<$Res>
    implements $SduiNACardBlockCopyWith<$Res> {
  _$SduiNACardBlockCopyWithImpl(this._self, this._then);

  final SduiNACardBlock _self;
  final $Res Function(SduiNACardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? shortCircuitReasonTdaIds = null,Object? message = null,}) {
  return _then(SduiNACardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,shortCircuitReasonTdaIds: null == shortCircuitReasonTdaIds ? _self._shortCircuitReasonTdaIds : shortCircuitReasonTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiGridBlock extends SduiBlockDTO {
  const SduiGridBlock({this.id, required final  List<SduiBlockDTO> items, final  String? $type}): _items = items,$type = $type ?? 'grid',super._();
  factory SduiGridBlock.fromJson(Map<String, dynamic> json) => _$SduiGridBlockFromJson(json);

@override final  String? id;
 final  List<SduiBlockDTO> _items;
 List<SduiBlockDTO> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiGridBlockCopyWith<SduiGridBlock> get copyWith => _$SduiGridBlockCopyWithImpl<SduiGridBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiGridBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.grid(id: $id, items: $items)';
}


}

/// @nodoc
abstract mixin class $SduiGridBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiGridBlockCopyWith(SduiGridBlock value, $Res Function(SduiGridBlock) _then) = _$SduiGridBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, List<SduiBlockDTO> items
});




}
/// @nodoc
class _$SduiGridBlockCopyWithImpl<$Res>
    implements $SduiGridBlockCopyWith<$Res> {
  _$SduiGridBlockCopyWithImpl(this._self, this._then);

  final SduiGridBlock _self;
  final $Res Function(SduiGridBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? items = null,}) {
  return _then(SduiGridBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiMetadataBlock extends SduiBlockDTO {
  const SduiMetadataBlock({this.id, required this.title, final  List<String> badges = const [], @JsonKey(name: 'metadata_lines') final  List<String> metadataLines = const [], this.costs, final  Map<String, String>? tokens, @JsonKey(name: 'custom_preface_md') this.customPrefaceMd, final  String? $type}): _badges = badges,_metadataLines = metadataLines,_tokens = tokens,$type = $type ?? 'metadata',super._();
  factory SduiMetadataBlock.fromJson(Map<String, dynamic> json) => _$SduiMetadataBlockFromJson(json);

@override final  String? id;
 final  String title;
 final  List<String> _badges;
@JsonKey() List<String> get badges {
  if (_badges is EqualUnmodifiableListView) return _badges;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_badges);
}

 final  List<String> _metadataLines;
@JsonKey(name: 'metadata_lines') List<String> get metadataLines {
  if (_metadataLines is EqualUnmodifiableListView) return _metadataLines;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_metadataLines);
}

 final  String? costs;
 final  Map<String, String>? _tokens;
 Map<String, String>? get tokens {
  final value = _tokens;
  if (value == null) return null;
  if (_tokens is EqualUnmodifiableMapView) return _tokens;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@JsonKey(name: 'custom_preface_md') final  String? customPrefaceMd;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiMetadataBlockCopyWith<SduiMetadataBlock> get copyWith => _$SduiMetadataBlockCopyWithImpl<SduiMetadataBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiMetadataBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.metadata(id: $id, title: $title, badges: $badges, metadataLines: $metadataLines, costs: $costs, tokens: $tokens, customPrefaceMd: $customPrefaceMd)';
}


}

/// @nodoc
abstract mixin class $SduiMetadataBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiMetadataBlockCopyWith(SduiMetadataBlock value, $Res Function(SduiMetadataBlock) _then) = _$SduiMetadataBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String title, List<String> badges,@JsonKey(name: 'metadata_lines') List<String> metadataLines, String? costs, Map<String, String>? tokens,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd
});




}
/// @nodoc
class _$SduiMetadataBlockCopyWithImpl<$Res>
    implements $SduiMetadataBlockCopyWith<$Res> {
  _$SduiMetadataBlockCopyWithImpl(this._self, this._then);

  final SduiMetadataBlock _self;
  final $Res Function(SduiMetadataBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = null,Object? badges = null,Object? metadataLines = null,Object? costs = freezed,Object? tokens = freezed,Object? customPrefaceMd = freezed,}) {
  return _then(SduiMetadataBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,badges: null == badges ? _self._badges : badges // ignore: cast_nullable_to_non_nullable
as List<String>,metadataLines: null == metadataLines ? _self._metadataLines : metadataLines // ignore: cast_nullable_to_non_nullable
as List<String>,costs: freezed == costs ? _self.costs : costs // ignore: cast_nullable_to_non_nullable
as String?,tokens: freezed == tokens ? _self._tokens : tokens // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiScoreCardBlock extends SduiBlockDTO {
  const SduiScoreCardBlock({this.id, @JsonKey(name: 'global_score') this.globalScore, final  String? $type}): $type = $type ?? 'score_card',super._();
  factory SduiScoreCardBlock.fromJson(Map<String, dynamic> json) => _$SduiScoreCardBlockFromJson(json);

@override final  String? id;
@JsonKey(name: 'global_score') final  double? globalScore;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiScoreCardBlockCopyWith<SduiScoreCardBlock> get copyWith => _$SduiScoreCardBlockCopyWithImpl<SduiScoreCardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiScoreCardBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.scoreCard(id: $id, globalScore: $globalScore)';
}


}

/// @nodoc
abstract mixin class $SduiScoreCardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiScoreCardBlockCopyWith(SduiScoreCardBlock value, $Res Function(SduiScoreCardBlock) _then) = _$SduiScoreCardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'global_score') double? globalScore
});




}
/// @nodoc
class _$SduiScoreCardBlockCopyWithImpl<$Res>
    implements $SduiScoreCardBlockCopyWith<$Res> {
  _$SduiScoreCardBlockCopyWithImpl(this._self, this._then);

  final SduiScoreCardBlock _self;
  final $Res Function(SduiScoreCardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? globalScore = freezed,}) {
  return _then(SduiScoreCardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiAuditTrailBlock extends SduiBlockDTO {
  const SduiAuditTrailBlock({this.id, final  String? $type}): $type = $type ?? 'audit_trail',super._();
  factory SduiAuditTrailBlock.fromJson(Map<String, dynamic> json) => _$SduiAuditTrailBlockFromJson(json);

@override final  String? id;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiAuditTrailBlockCopyWith<SduiAuditTrailBlock> get copyWith => _$SduiAuditTrailBlockCopyWithImpl<SduiAuditTrailBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiAuditTrailBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.auditTrail(id: $id)';
}


}

/// @nodoc
abstract mixin class $SduiAuditTrailBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiAuditTrailBlockCopyWith(SduiAuditTrailBlock value, $Res Function(SduiAuditTrailBlock) _then) = _$SduiAuditTrailBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id
});




}
/// @nodoc
class _$SduiAuditTrailBlockCopyWithImpl<$Res>
    implements $SduiAuditTrailBlockCopyWith<$Res> {
  _$SduiAuditTrailBlockCopyWithImpl(this._self, this._then);

  final SduiAuditTrailBlock _self;
  final $Res Function(SduiAuditTrailBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,}) {
  return _then(SduiAuditTrailBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiRadarChartBlock extends SduiBlockDTO {
  const SduiRadarChartBlock({this.id, this.title, final  List<MatrixScorecardRowDto> axes = const [], final  String? $type}): _axes = axes,$type = $type ?? '3d_matrix',super._();
  factory SduiRadarChartBlock.fromJson(Map<String, dynamic> json) => _$SduiRadarChartBlockFromJson(json);

@override final  String? id;
 final  I18nText? title;
 final  List<MatrixScorecardRowDto> _axes;
@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiRadarChartBlockCopyWith<SduiRadarChartBlock> get copyWith => _$SduiRadarChartBlockCopyWithImpl<SduiRadarChartBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiRadarChartBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.matrix3d(id: $id, title: $title, axes: $axes)';
}


}

/// @nodoc
abstract mixin class $SduiRadarChartBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiRadarChartBlockCopyWith(SduiRadarChartBlock value, $Res Function(SduiRadarChartBlock) _then) = _$SduiRadarChartBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, I18nText? title, List<MatrixScorecardRowDto> axes
});


$I18nTextCopyWith<$Res>? get title;

}
/// @nodoc
class _$SduiRadarChartBlockCopyWithImpl<$Res>
    implements $SduiRadarChartBlockCopyWith<$Res> {
  _$SduiRadarChartBlockCopyWithImpl(this._self, this._then);

  final SduiRadarChartBlock _self;
  final $Res Function(SduiRadarChartBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = freezed,Object? axes = null,}) {
  return _then(SduiRadarChartBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiScatterPlotBlock extends SduiBlockDTO {
  const SduiScatterPlotBlock({this.id, this.title, final  List<MatrixScorecardRowDto> axes = const [], final  String? $type}): _axes = axes,$type = $type ?? '2d_compare',super._();
  factory SduiScatterPlotBlock.fromJson(Map<String, dynamic> json) => _$SduiScatterPlotBlockFromJson(json);

@override final  String? id;
 final  I18nText? title;
 final  List<MatrixScorecardRowDto> _axes;
@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiScatterPlotBlockCopyWith<SduiScatterPlotBlock> get copyWith => _$SduiScatterPlotBlockCopyWithImpl<SduiScatterPlotBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiScatterPlotBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.compare2d(id: $id, title: $title, axes: $axes)';
}


}

/// @nodoc
abstract mixin class $SduiScatterPlotBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiScatterPlotBlockCopyWith(SduiScatterPlotBlock value, $Res Function(SduiScatterPlotBlock) _then) = _$SduiScatterPlotBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, I18nText? title, List<MatrixScorecardRowDto> axes
});


$I18nTextCopyWith<$Res>? get title;

}
/// @nodoc
class _$SduiScatterPlotBlockCopyWithImpl<$Res>
    implements $SduiScatterPlotBlockCopyWith<$Res> {
  _$SduiScatterPlotBlockCopyWithImpl(this._self, this._then);

  final SduiScatterPlotBlock _self;
  final $Res Function(SduiScatterPlotBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = freezed,Object? axes = null,}) {
  return _then(SduiScatterPlotBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiQuadrantMatrixBlock extends SduiBlockDTO {
  const SduiQuadrantMatrixBlock({this.id, this.title, final  List<MatrixScorecardRowDto> axes = const [], final  String? $type}): _axes = axes,$type = $type ?? 'quadrant_matrix',super._();
  factory SduiQuadrantMatrixBlock.fromJson(Map<String, dynamic> json) => _$SduiQuadrantMatrixBlockFromJson(json);

@override final  String? id;
 final  I18nText? title;
 final  List<MatrixScorecardRowDto> _axes;
@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiQuadrantMatrixBlockCopyWith<SduiQuadrantMatrixBlock> get copyWith => _$SduiQuadrantMatrixBlockCopyWithImpl<SduiQuadrantMatrixBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiQuadrantMatrixBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.quadrantMatrix(id: $id, title: $title, axes: $axes)';
}


}

/// @nodoc
abstract mixin class $SduiQuadrantMatrixBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiQuadrantMatrixBlockCopyWith(SduiQuadrantMatrixBlock value, $Res Function(SduiQuadrantMatrixBlock) _then) = _$SduiQuadrantMatrixBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, I18nText? title, List<MatrixScorecardRowDto> axes
});


$I18nTextCopyWith<$Res>? get title;

}
/// @nodoc
class _$SduiQuadrantMatrixBlockCopyWithImpl<$Res>
    implements $SduiQuadrantMatrixBlockCopyWith<$Res> {
  _$SduiQuadrantMatrixBlockCopyWithImpl(this._self, this._then);

  final SduiQuadrantMatrixBlock _self;
  final $Res Function(SduiQuadrantMatrixBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = freezed,Object? axes = null,}) {
  return _then(SduiQuadrantMatrixBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiMetrics1DBlock extends SduiBlockDTO {
  const SduiMetrics1DBlock({this.id, this.title, final  List<MatrixScorecardRowDto> axes = const [], final  String? $type}): _axes = axes,$type = $type ?? '1d_metrics',super._();
  factory SduiMetrics1DBlock.fromJson(Map<String, dynamic> json) => _$SduiMetrics1DBlockFromJson(json);

@override final  String? id;
 final  I18nText? title;
 final  List<MatrixScorecardRowDto> _axes;
@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiMetrics1DBlockCopyWith<SduiMetrics1DBlock> get copyWith => _$SduiMetrics1DBlockCopyWithImpl<SduiMetrics1DBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiMetrics1DBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.metrics1d(id: $id, title: $title, axes: $axes)';
}


}

/// @nodoc
abstract mixin class $SduiMetrics1DBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiMetrics1DBlockCopyWith(SduiMetrics1DBlock value, $Res Function(SduiMetrics1DBlock) _then) = _$SduiMetrics1DBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, I18nText? title, List<MatrixScorecardRowDto> axes
});


$I18nTextCopyWith<$Res>? get title;

}
/// @nodoc
class _$SduiMetrics1DBlockCopyWithImpl<$Res>
    implements $SduiMetrics1DBlockCopyWith<$Res> {
  _$SduiMetrics1DBlockCopyWithImpl(this._self, this._then);

  final SduiMetrics1DBlock _self;
  final $Res Function(SduiMetrics1DBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = freezed,Object? axes = null,}) {
  return _then(SduiMetrics1DBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiMatrixTableBlock extends SduiBlockDTO {
  const SduiMatrixTableBlock({this.id, this.title, final  List<MatrixScorecardRowDto> axes = const [], @JsonKey(name: 'matrix_column_labels') final  Map<String, I18nText> matrixColumnLabels = const {}, @JsonKey(name: 'extension_labels') final  Map<XaiExtensionType, I18nText> extensionLabels = const {}, @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const [], @JsonKey(name: 'short_circuited_by_claims') final  List<String> shortCircuitedByClaims = const <String>[], @JsonKey(name: 'falsified_warrant_claims') final  List<String> falsifiedWarrantClaims = const <String>[], final  String? $type}): _axes = axes,_matrixColumnLabels = matrixColumnLabels,_extensionLabels = extensionLabels,_matrixVisibleColumns = matrixVisibleColumns,_shortCircuitedByClaims = shortCircuitedByClaims,_falsifiedWarrantClaims = falsifiedWarrantClaims,$type = $type ?? 'matrix_summary',super._();
  factory SduiMatrixTableBlock.fromJson(Map<String, dynamic> json) => _$SduiMatrixTableBlockFromJson(json);

@override final  String? id;
 final  I18nText? title;
 final  List<MatrixScorecardRowDto> _axes;
@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}

 final  Map<String, I18nText> _matrixColumnLabels;
@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> get matrixColumnLabels {
  if (_matrixColumnLabels is EqualUnmodifiableMapView) return _matrixColumnLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_matrixColumnLabels);
}

 final  Map<XaiExtensionType, I18nText> _extensionLabels;
@JsonKey(name: 'extension_labels') Map<XaiExtensionType, I18nText> get extensionLabels {
  if (_extensionLabels is EqualUnmodifiableMapView) return _extensionLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_extensionLabels);
}

 final  List<String> _matrixVisibleColumns;
@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
}

// Phase 3, Step 3.3: Inline topological short-circuit and Toulmin falsification lineage
 final  List<String> _shortCircuitedByClaims;
// Phase 3, Step 3.3: Inline topological short-circuit and Toulmin falsification lineage
@JsonKey(name: 'short_circuited_by_claims') List<String> get shortCircuitedByClaims {
  if (_shortCircuitedByClaims is EqualUnmodifiableListView) return _shortCircuitedByClaims;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortCircuitedByClaims);
}

 final  List<String> _falsifiedWarrantClaims;
@JsonKey(name: 'falsified_warrant_claims') List<String> get falsifiedWarrantClaims {
  if (_falsifiedWarrantClaims is EqualUnmodifiableListView) return _falsifiedWarrantClaims;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_falsifiedWarrantClaims);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiMatrixTableBlockCopyWith<SduiMatrixTableBlock> get copyWith => _$SduiMatrixTableBlockCopyWithImpl<SduiMatrixTableBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiMatrixTableBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.matrixSummary(id: $id, title: $title, axes: $axes, matrixColumnLabels: $matrixColumnLabels, extensionLabels: $extensionLabels, matrixVisibleColumns: $matrixVisibleColumns, shortCircuitedByClaims: $shortCircuitedByClaims, falsifiedWarrantClaims: $falsifiedWarrantClaims)';
}


}

/// @nodoc
abstract mixin class $SduiMatrixTableBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiMatrixTableBlockCopyWith(SduiMatrixTableBlock value, $Res Function(SduiMatrixTableBlock) _then) = _$SduiMatrixTableBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, I18nText? title, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> matrixColumnLabels,@JsonKey(name: 'extension_labels') Map<XaiExtensionType, I18nText> extensionLabels,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns,@JsonKey(name: 'short_circuited_by_claims') List<String> shortCircuitedByClaims,@JsonKey(name: 'falsified_warrant_claims') List<String> falsifiedWarrantClaims
});


$I18nTextCopyWith<$Res>? get title;

}
/// @nodoc
class _$SduiMatrixTableBlockCopyWithImpl<$Res>
    implements $SduiMatrixTableBlockCopyWith<$Res> {
  _$SduiMatrixTableBlockCopyWithImpl(this._self, this._then);

  final SduiMatrixTableBlock _self;
  final $Res Function(SduiMatrixTableBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? title = freezed,Object? axes = null,Object? matrixColumnLabels = null,Object? extensionLabels = null,Object? matrixVisibleColumns = null,Object? shortCircuitedByClaims = null,Object? falsifiedWarrantClaims = null,}) {
  return _then(SduiMatrixTableBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,matrixColumnLabels: null == matrixColumnLabels ? _self._matrixColumnLabels : matrixColumnLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,extensionLabels: null == extensionLabels ? _self._extensionLabels : extensionLabels // ignore: cast_nullable_to_non_nullable
as Map<XaiExtensionType, I18nText>,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,shortCircuitedByClaims: null == shortCircuitedByClaims ? _self._shortCircuitedByClaims : shortCircuitedByClaims // ignore: cast_nullable_to_non_nullable
as List<String>,falsifiedWarrantClaims: null == falsifiedWarrantClaims ? _self._falsifiedWarrantClaims : falsifiedWarrantClaims // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiCausalGraphBlock extends SduiBlockDTO {
  const SduiCausalGraphBlock({this.id, @JsonKey(name: 'critical_path_nodes') final  List<CausalNodeDto> criticalPathNodes = const [], @JsonKey(name: 'critical_edges') final  List<CausalEdgeDto> criticalEdges = const [], @JsonKey(name: 'root_cause_diagnoses') final  List<CausalRootCauseDiagnosisDto> rootCauseDiagnoses = const [], @JsonKey(name: 'anti_fluff_audit') required this.antiFluffAudit, @JsonKey(name: 'prescriptive_remediations') final  List<PrescriptiveRemediationDto> prescriptiveRemediations = const [], @JsonKey(name: 'fair_scoring') this.fairScoring, @JsonKey(name: 'intact_claims_count') required this.intactClaimsCount, @JsonKey(name: 'total_claims_count') required this.totalClaimsCount, required this.summary, @JsonKey(name: 'short_circuited_by_claims') final  List<String> shortCircuitedByClaims = const <String>[], @JsonKey(name: 'falsified_warrant_claims') final  List<String> falsifiedWarrantClaims = const <String>[], final  String? $type}): _criticalPathNodes = criticalPathNodes,_criticalEdges = criticalEdges,_rootCauseDiagnoses = rootCauseDiagnoses,_prescriptiveRemediations = prescriptiveRemediations,_shortCircuitedByClaims = shortCircuitedByClaims,_falsifiedWarrantClaims = falsifiedWarrantClaims,$type = $type ?? 'causal_graph',super._();
  factory SduiCausalGraphBlock.fromJson(Map<String, dynamic> json) => _$SduiCausalGraphBlockFromJson(json);

@override final  String? id;
 final  List<CausalNodeDto> _criticalPathNodes;
@JsonKey(name: 'critical_path_nodes') List<CausalNodeDto> get criticalPathNodes {
  if (_criticalPathNodes is EqualUnmodifiableListView) return _criticalPathNodes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_criticalPathNodes);
}

 final  List<CausalEdgeDto> _criticalEdges;
@JsonKey(name: 'critical_edges') List<CausalEdgeDto> get criticalEdges {
  if (_criticalEdges is EqualUnmodifiableListView) return _criticalEdges;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_criticalEdges);
}

 final  List<CausalRootCauseDiagnosisDto> _rootCauseDiagnoses;
@JsonKey(name: 'root_cause_diagnoses') List<CausalRootCauseDiagnosisDto> get rootCauseDiagnoses {
  if (_rootCauseDiagnoses is EqualUnmodifiableListView) return _rootCauseDiagnoses;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_rootCauseDiagnoses);
}

@JsonKey(name: 'anti_fluff_audit') final  AntiFluffAuditDto antiFluffAudit;
 final  List<PrescriptiveRemediationDto> _prescriptiveRemediations;
@JsonKey(name: 'prescriptive_remediations') List<PrescriptiveRemediationDto> get prescriptiveRemediations {
  if (_prescriptiveRemediations is EqualUnmodifiableListView) return _prescriptiveRemediations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_prescriptiveRemediations);
}

@JsonKey(name: 'fair_scoring') final  FairScoringBreakdownDto? fairScoring;
@JsonKey(name: 'intact_claims_count') final  int intactClaimsCount;
@JsonKey(name: 'total_claims_count') final  int totalClaimsCount;
 final  I18nText summary;
// Phase 3, Step 3.3: Inline topological short-circuit and Toulmin falsification lineage
 final  List<String> _shortCircuitedByClaims;
// Phase 3, Step 3.3: Inline topological short-circuit and Toulmin falsification lineage
@JsonKey(name: 'short_circuited_by_claims') List<String> get shortCircuitedByClaims {
  if (_shortCircuitedByClaims is EqualUnmodifiableListView) return _shortCircuitedByClaims;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortCircuitedByClaims);
}

 final  List<String> _falsifiedWarrantClaims;
@JsonKey(name: 'falsified_warrant_claims') List<String> get falsifiedWarrantClaims {
  if (_falsifiedWarrantClaims is EqualUnmodifiableListView) return _falsifiedWarrantClaims;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_falsifiedWarrantClaims);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiCausalGraphBlockCopyWith<SduiCausalGraphBlock> get copyWith => _$SduiCausalGraphBlockCopyWithImpl<SduiCausalGraphBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiCausalGraphBlockToJson(this, );
}



@override
String toString() {
  return 'SduiBlockDTO.causalGraph(id: $id, criticalPathNodes: $criticalPathNodes, criticalEdges: $criticalEdges, rootCauseDiagnoses: $rootCauseDiagnoses, antiFluffAudit: $antiFluffAudit, prescriptiveRemediations: $prescriptiveRemediations, fairScoring: $fairScoring, intactClaimsCount: $intactClaimsCount, totalClaimsCount: $totalClaimsCount, summary: $summary, shortCircuitedByClaims: $shortCircuitedByClaims, falsifiedWarrantClaims: $falsifiedWarrantClaims)';
}


}

/// @nodoc
abstract mixin class $SduiCausalGraphBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiCausalGraphBlockCopyWith(SduiCausalGraphBlock value, $Res Function(SduiCausalGraphBlock) _then) = _$SduiCausalGraphBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'critical_path_nodes') List<CausalNodeDto> criticalPathNodes,@JsonKey(name: 'critical_edges') List<CausalEdgeDto> criticalEdges,@JsonKey(name: 'root_cause_diagnoses') List<CausalRootCauseDiagnosisDto> rootCauseDiagnoses,@JsonKey(name: 'anti_fluff_audit') AntiFluffAuditDto antiFluffAudit,@JsonKey(name: 'prescriptive_remediations') List<PrescriptiveRemediationDto> prescriptiveRemediations,@JsonKey(name: 'fair_scoring') FairScoringBreakdownDto? fairScoring,@JsonKey(name: 'intact_claims_count') int intactClaimsCount,@JsonKey(name: 'total_claims_count') int totalClaimsCount, I18nText summary,@JsonKey(name: 'short_circuited_by_claims') List<String> shortCircuitedByClaims,@JsonKey(name: 'falsified_warrant_claims') List<String> falsifiedWarrantClaims
});


$AntiFluffAuditDtoCopyWith<$Res> get antiFluffAudit;$FairScoringBreakdownDtoCopyWith<$Res>? get fairScoring;$I18nTextCopyWith<$Res> get summary;

}
/// @nodoc
class _$SduiCausalGraphBlockCopyWithImpl<$Res>
    implements $SduiCausalGraphBlockCopyWith<$Res> {
  _$SduiCausalGraphBlockCopyWithImpl(this._self, this._then);

  final SduiCausalGraphBlock _self;
  final $Res Function(SduiCausalGraphBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? criticalPathNodes = null,Object? criticalEdges = null,Object? rootCauseDiagnoses = null,Object? antiFluffAudit = null,Object? prescriptiveRemediations = null,Object? fairScoring = freezed,Object? intactClaimsCount = null,Object? totalClaimsCount = null,Object? summary = null,Object? shortCircuitedByClaims = null,Object? falsifiedWarrantClaims = null,}) {
  return _then(SduiCausalGraphBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,criticalPathNodes: null == criticalPathNodes ? _self._criticalPathNodes : criticalPathNodes // ignore: cast_nullable_to_non_nullable
as List<CausalNodeDto>,criticalEdges: null == criticalEdges ? _self._criticalEdges : criticalEdges // ignore: cast_nullable_to_non_nullable
as List<CausalEdgeDto>,rootCauseDiagnoses: null == rootCauseDiagnoses ? _self._rootCauseDiagnoses : rootCauseDiagnoses // ignore: cast_nullable_to_non_nullable
as List<CausalRootCauseDiagnosisDto>,antiFluffAudit: null == antiFluffAudit ? _self.antiFluffAudit : antiFluffAudit // ignore: cast_nullable_to_non_nullable
as AntiFluffAuditDto,prescriptiveRemediations: null == prescriptiveRemediations ? _self._prescriptiveRemediations : prescriptiveRemediations // ignore: cast_nullable_to_non_nullable
as List<PrescriptiveRemediationDto>,fairScoring: freezed == fairScoring ? _self.fairScoring : fairScoring // ignore: cast_nullable_to_non_nullable
as FairScoringBreakdownDto?,intactClaimsCount: null == intactClaimsCount ? _self.intactClaimsCount : intactClaimsCount // ignore: cast_nullable_to_non_nullable
as int,totalClaimsCount: null == totalClaimsCount ? _self.totalClaimsCount : totalClaimsCount // ignore: cast_nullable_to_non_nullable
as int,summary: null == summary ? _self.summary : summary // ignore: cast_nullable_to_non_nullable
as I18nText,shortCircuitedByClaims: null == shortCircuitedByClaims ? _self._shortCircuitedByClaims : shortCircuitedByClaims // ignore: cast_nullable_to_non_nullable
as List<String>,falsifiedWarrantClaims: null == falsifiedWarrantClaims ? _self._falsifiedWarrantClaims : falsifiedWarrantClaims // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AntiFluffAuditDtoCopyWith<$Res> get antiFluffAudit {
  
  return $AntiFluffAuditDtoCopyWith<$Res>(_self.antiFluffAudit, (value) {
    return _then(_self.copyWith(antiFluffAudit: value));
  });
}/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$FairScoringBreakdownDtoCopyWith<$Res>? get fairScoring {
    if (_self.fairScoring == null) {
    return null;
  }

  return $FairScoringBreakdownDtoCopyWith<$Res>(_self.fairScoring!, (value) {
    return _then(_self.copyWith(fairScoring: value));
  });
}/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get summary {
  
  return $I18nTextCopyWith<$Res>(_self.summary, (value) {
    return _then(_self.copyWith(summary: value));
  });
}
}


/// @nodoc
mixin _$SduiBulletListItemDTO {

 String get text; List<int> get citations;@JsonKey(name: 'exact_quotes') List<String> get exactQuotes;
/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBulletListItemDTOCopyWith<SduiBulletListItemDTO> get copyWith => _$SduiBulletListItemDTOCopyWithImpl<SduiBulletListItemDTO>(this as SduiBulletListItemDTO, _$identity);

  /// Serializes this SduiBulletListItemDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SduiBulletListItemDTO(text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiBulletListItemDTOCopyWith<$Res>  {
  factory $SduiBulletListItemDTOCopyWith(SduiBulletListItemDTO value, $Res Function(SduiBulletListItemDTO) _then) = _$SduiBulletListItemDTOCopyWithImpl;
@useResult
$Res call({
 String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
});




}
/// @nodoc
class _$SduiBulletListItemDTOCopyWithImpl<$Res>
    implements $SduiBulletListItemDTOCopyWith<$Res> {
  _$SduiBulletListItemDTOCopyWithImpl(this._self, this._then);

  final SduiBulletListItemDTO _self;
  final $Res Function(SduiBulletListItemDTO) _then;

/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(_self.copyWith(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self.citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self.exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [SduiBulletListItemDTO].
extension SduiBulletListItemDTOPatterns on SduiBulletListItemDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SduiBulletListItemDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SduiBulletListItemDTO value)  $default,){
final _that = this;
switch (_that) {
case _SduiBulletListItemDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SduiBulletListItemDTO value)?  $default,){
final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
return $default(_that.text,_that.citations,_that.exactQuotes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  $default,) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO():
return $default(_that.text,_that.citations,_that.exactQuotes);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  $default,) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
return $default(_that.text,_that.citations,_that.exactQuotes);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _SduiBulletListItemDTO implements SduiBulletListItemDTO {
  const _SduiBulletListItemDTO({required this.text, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const []}): _citations = citations,_exactQuotes = exactQuotes;
  factory _SduiBulletListItemDTO.fromJson(Map<String, dynamic> json) => _$SduiBulletListItemDTOFromJson(json);

@override final  String text;
 final  List<int> _citations;
@override@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@override@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SduiBulletListItemDTOCopyWith<_SduiBulletListItemDTO> get copyWith => __$SduiBulletListItemDTOCopyWithImpl<_SduiBulletListItemDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiBulletListItemDTOToJson(this, );
}



@override
String toString() {
  return 'SduiBulletListItemDTO(text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class _$SduiBulletListItemDTOCopyWith<$Res> implements $SduiBulletListItemDTOCopyWith<$Res> {
  factory _$SduiBulletListItemDTOCopyWith(_SduiBulletListItemDTO value, $Res Function(_SduiBulletListItemDTO) _then) = __$SduiBulletListItemDTOCopyWithImpl;
@override @useResult
$Res call({
 String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
});




}
/// @nodoc
class __$SduiBulletListItemDTOCopyWithImpl<$Res>
    implements _$SduiBulletListItemDTOCopyWith<$Res> {
  __$SduiBulletListItemDTOCopyWithImpl(this._self, this._then);

  final _SduiBulletListItemDTO _self;
  final $Res Function(_SduiBulletListItemDTO) _then;

/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(_SduiBulletListItemDTO(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
