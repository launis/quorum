// ignore_for_file: invalid_annotation_target
import 'package:client_app/core/utils/safe_isolate.dart';
import 'dart:convert';
import 'package:uuid/uuid.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';

part 'prompt_block.freezed.dart';
part 'prompt_block.g.dart';

/// Data types allowed for PromptBlock extracted values.
enum BlockDataType {
  @JsonValue('float')
  floatType('float'),
  @JsonValue('int')
  intType('int'),
  @JsonValue('string')
  stringType('string'),
  @JsonValue('instruction')
  instruction('instruction'),
  @JsonValue('panel')
  panel('panel'),
  @JsonValue('compliance')
  compliance('compliance'),
  @JsonValue('question')
  question('question'),
  @JsonValue('criteria')
  criteria('criteria');

  final String backendValue;
  const BlockDataType(this.backendValue);

  static BlockDataType fromString(String val) {
    final lower = val.toLowerCase();
    return BlockDataType.values.firstWhere(
      (e) => e.backendValue == lower,
      orElse: () => BlockDataType.stringType,
    );
  }
}

@Freezed(equal: false)
abstract class TheoryGrounding with _$TheoryGrounding {
  const TheoryGrounding._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TheoryGrounding({
    required String sourceUrl,
    required String citationReference,
  }) = _TheoryGrounding;

  factory TheoryGrounding.fromJson(Map<String, dynamic> json) =>
      _$TheoryGroundingFromJson(json);
}

@Freezed(equal: false)
abstract class AcceptanceCriterion with _$AcceptanceCriterion {
  const AcceptanceCriterion._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory AcceptanceCriterion({
    required String instruction,
    @JsonKey(name: 'requires_contextual_override')
    @Default(false)
    bool requiresContextualOverride,
  }) = _AcceptanceCriterion;

  factory AcceptanceCriterion.fromJson(Map<String, dynamic> json) =>
      _$AcceptanceCriterionFromJson(json);
}

@Freezed(equal: false)
abstract class AntiPattern with _$AntiPattern {
  const AntiPattern._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory AntiPattern({
    required String pattern,
    @JsonKey(name: 'allows_contextual_excuse')
    @Default(false)
    bool allowsContextualExcuse,
  }) = _AntiPattern;

  factory AntiPattern.fromJson(Map<String, dynamic> json) =>
      _$AntiPatternFromJson(json);
}

@Freezed(equal: false)
abstract class TDAAssertion with _$TDAAssertion {
  const TDAAssertion._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TDAAssertion({
    @JsonKey(name: 'tda_id') required String tdaId,
    @JsonKey(name: 'concept_description') required String conceptDescription,
    @JsonKey(name: 'acceptance_criteria')
    @Default([])
    List<AcceptanceCriterion> acceptanceCriteria,
    @JsonKey(name: 'anti_patterns') @Default([]) List<AntiPattern> antiPatterns,
    @JsonKey(name: 'contrastive_example') String? contrastiveExample,
    @JsonKey(name: 'syntactic_anchors')
    @Default([])
    List<String> syntacticAnchors,
    @JsonKey(name: 'enforce_pre_flight') @Default(false) bool enforcePreFlight,
    @JsonKey(name: 'inverse_evidence') required bool inverseEvidence,
    @JsonKey(name: 'aggregation_mode') required AggregationMode aggregationMode,
    @JsonKey(name: 'evaluation_track')
    @Default(EvaluationTrack.cognitiveJudgement)
    EvaluationTrack evaluationTrack,
    @JsonKey(name: 'facts_to_find') @Default([]) List<String> factsToFind,
    @JsonKey(name: 'logical_expression') String? logicalExpression,
    @JsonKey(name: 'allow_contextual_override')
    @Default(false)
    bool allowContextualOverride,
    @JsonKey(name: 'high_entropy') @Default(false) bool highEntropy,
    @JsonKey(name: 'anchor_target') String? anchorTarget,
    @JsonKey(name: 'bounding_box_scope')
    @Default('paragraph')
    String boundingBoxScope,
    @JsonKey(name: 'extraction_rule') String? extractionRule,
  }) = _TDAAssertion;

  factory TDAAssertion.fromJson(Map<String, dynamic> json) =>
      _$TDAAssertionFromJson(json);

  /// Phase 2: Generates an Opaque Stripe ID automatically
  factory TDAAssertion.create({
    required String conceptDescription,
    required bool inverseEvidence,
    required AggregationMode aggregationMode,
    EvaluationTrack evaluationTrack = EvaluationTrack.cognitiveJudgement,
    List<String> factsToFind = const [],
    String? logicalExpression,
    bool allowContextualOverride = false,
  }) {
    final uuidHex = const Uuid().v4().replaceAll('-', '');
    return TDAAssertion(
      tdaId: 'tda_${uuidHex.substring(0, 16)}',
      conceptDescription: conceptDescription,
      inverseEvidence: inverseEvidence,
      aggregationMode: aggregationMode,
      evaluationTrack: evaluationTrack,
      factsToFind: factsToFind,
      logicalExpression: logicalExpression,
      allowContextualOverride: allowContextualOverride,
      anchorTarget: null,
      boundingBoxScope: 'paragraph',
      extractionRule: null,
    );
  }
}

@Freezed(equal: false)
abstract class MatrixClaim with _$MatrixClaim {
  const MatrixClaim._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixClaim({
    required I18nText label,
    required String aiDescription,
    @JsonKey(name: 'tda_assertions')
    @Default([])
    List<TDAAssertion> tdaAssertions,
  }) = _MatrixClaim;

  factory MatrixClaim.fromJson(Map<String, dynamic> json) =>
      _$MatrixClaimFromJson(json);
}

@Freezed(equal: false)
abstract class MatrixRow with _$MatrixRow {
  const MatrixRow._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixRow({
    required I18nText label,
    required String aiDescription,
  }) = _MatrixRow;

  factory MatrixRow.fromJson(Map<String, dynamic> json) =>
      _$MatrixRowFromJson(json);
}

@Freezed(equal: false)
abstract class MatrixScale with _$MatrixScale {
  const MatrixScale._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory MatrixScale({
    required int score,
    I18nText? name,
    required String aiLabel,
    required List<MatrixClaim> claims,
  }) = _MatrixScale;

  factory MatrixScale.fromJson(Map<String, dynamic> json) =>
      _$MatrixScaleFromJson(json);
}

/// V2 PromptBlock representation.
/// Fuses legacy Components and Matrices into a unified directive model.
@Freezed(equal: false)
abstract class PromptBlock with _$PromptBlock {
  const PromptBlock._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory PromptBlock({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    String? organizationId,
    required I18nText label,
    required I18nText description,
    String? aiDescription,
    @Default('system') String categoryId,
    @Default(true) bool isEvaluative,
    @Default(BlockDataType.stringType) BlockDataType type,
    @Default(false) bool allowDecimals,
    @Default([]) List<String> outputExtensions,
    TheoryGrounding? theoryGrounding,
    @JsonKey(name: 'is_lightweight_protocol')
    @Default(false)
    bool isLightweightProtocol,
    int? scaleMin,
    int? scaleMax,
    @JsonKey(includeToJson: false) int? computedMin,
    @JsonKey(includeToJson: false) int? computedMax,
    List<MatrixScale>? scales,
    List<MatrixRow>? rows,
    List<I18nText>? columns,
  }) = _PromptBlock;

  factory PromptBlock.fromJson(Map<String, dynamic> json) =>
      _$PromptBlockFromJson(json);

  /// Parses raw JSON string to PromptBlock in a background isolate
  static Future<PromptBlock> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return PromptBlock.fromJson(decoded);
    });
  }

  static Future<List<PromptBlock>> parseListInBackground(
    List<dynamic> rawList,
  ) async {
    return safeIsolateRun(() {
      return rawList
          .map((e) => PromptBlock.fromJson(e as Map<String, dynamic>))
          .toList();
    });
  }
}
