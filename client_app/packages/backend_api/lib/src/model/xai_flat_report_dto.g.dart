// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'xai_flat_report_dto.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$XAIFlatReportDTOCWProxy {
  XAIFlatReportDTO executionId(String executionId);

  XAIFlatReportDTO timestamp(DateTime timestamp);

  XAIFlatReportDTO verdict(String verdict);

  XAIFlatReportDTO scoreTotal(num scoreTotal);

  XAIFlatReportDTO confidenceScore(num confidenceScore);

  XAIFlatReportDTO topStrengthId(String? topStrengthId);

  XAIFlatReportDTO topWeaknessId(String? topWeaknessId);

  XAIFlatReportDTO flattenedScores(Map<String, num>? flattenedScores);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `XAIFlatReportDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// XAIFlatReportDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  XAIFlatReportDTO call({
    String executionId,
    DateTime timestamp,
    String verdict,
    num scoreTotal,
    num confidenceScore,
    String? topStrengthId,
    String? topWeaknessId,
    Map<String, num>? flattenedScores,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfXAIFlatReportDTO.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfXAIFlatReportDTO.copyWith.fieldName(...)`
class _$XAIFlatReportDTOCWProxyImpl implements _$XAIFlatReportDTOCWProxy {
  const _$XAIFlatReportDTOCWProxyImpl(this._value);

  final XAIFlatReportDTO _value;

  @override
  XAIFlatReportDTO executionId(String executionId) =>
      this(executionId: executionId);

  @override
  XAIFlatReportDTO timestamp(DateTime timestamp) => this(timestamp: timestamp);

  @override
  XAIFlatReportDTO verdict(String verdict) => this(verdict: verdict);

  @override
  XAIFlatReportDTO scoreTotal(num scoreTotal) => this(scoreTotal: scoreTotal);

  @override
  XAIFlatReportDTO confidenceScore(num confidenceScore) =>
      this(confidenceScore: confidenceScore);

  @override
  XAIFlatReportDTO topStrengthId(String? topStrengthId) =>
      this(topStrengthId: topStrengthId);

  @override
  XAIFlatReportDTO topWeaknessId(String? topWeaknessId) =>
      this(topWeaknessId: topWeaknessId);

  @override
  XAIFlatReportDTO flattenedScores(Map<String, num>? flattenedScores) =>
      this(flattenedScores: flattenedScores);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `XAIFlatReportDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// XAIFlatReportDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  XAIFlatReportDTO call({
    Object? executionId = const $CopyWithPlaceholder(),
    Object? timestamp = const $CopyWithPlaceholder(),
    Object? verdict = const $CopyWithPlaceholder(),
    Object? scoreTotal = const $CopyWithPlaceholder(),
    Object? confidenceScore = const $CopyWithPlaceholder(),
    Object? topStrengthId = const $CopyWithPlaceholder(),
    Object? topWeaknessId = const $CopyWithPlaceholder(),
    Object? flattenedScores = const $CopyWithPlaceholder(),
  }) {
    return XAIFlatReportDTO(
      executionId: executionId == const $CopyWithPlaceholder()
          ? _value.executionId
          // ignore: cast_nullable_to_non_nullable
          : executionId as String,
      timestamp: timestamp == const $CopyWithPlaceholder()
          ? _value.timestamp
          // ignore: cast_nullable_to_non_nullable
          : timestamp as DateTime,
      verdict: verdict == const $CopyWithPlaceholder()
          ? _value.verdict
          // ignore: cast_nullable_to_non_nullable
          : verdict as String,
      scoreTotal: scoreTotal == const $CopyWithPlaceholder()
          ? _value.scoreTotal
          // ignore: cast_nullable_to_non_nullable
          : scoreTotal as num,
      confidenceScore: confidenceScore == const $CopyWithPlaceholder()
          ? _value.confidenceScore
          // ignore: cast_nullable_to_non_nullable
          : confidenceScore as num,
      topStrengthId: topStrengthId == const $CopyWithPlaceholder()
          ? _value.topStrengthId
          // ignore: cast_nullable_to_non_nullable
          : topStrengthId as String?,
      topWeaknessId: topWeaknessId == const $CopyWithPlaceholder()
          ? _value.topWeaknessId
          // ignore: cast_nullable_to_non_nullable
          : topWeaknessId as String?,
      flattenedScores: flattenedScores == const $CopyWithPlaceholder()
          ? _value.flattenedScores
          // ignore: cast_nullable_to_non_nullable
          : flattenedScores as Map<String, num>?,
    );
  }
}

extension $XAIFlatReportDTOCopyWith on XAIFlatReportDTO {
  /// Returns a callable class that can be used as follows: `instanceOfXAIFlatReportDTO.copyWith(...)` or like so:`instanceOfXAIFlatReportDTO.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$XAIFlatReportDTOCWProxy get copyWith => _$XAIFlatReportDTOCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

XAIFlatReportDTO _$XAIFlatReportDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'XAIFlatReportDTO',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const [
        'execution_id',
        'timestamp',
        'verdict',
        'score_total',
        'confidence_score',
      ],
    );
    final val = XAIFlatReportDTO(
      executionId: $checkedConvert('execution_id', (v) => v as String),
      timestamp: $checkedConvert(
        'timestamp',
        (v) => DateTime.parse(v as String),
      ),
      verdict: $checkedConvert('verdict', (v) => v as String),
      scoreTotal: $checkedConvert('score_total', (v) => v as num),
      confidenceScore: $checkedConvert('confidence_score', (v) => v as num),
      topStrengthId: $checkedConvert('top_strength_id', (v) => v as String?),
      topWeaknessId: $checkedConvert('top_weakness_id', (v) => v as String?),
      flattenedScores: $checkedConvert(
        'flattened_scores',
        (v) =>
            (v as Map<String, dynamic>?)?.map((k, e) => MapEntry(k, e as num)),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'executionId': 'execution_id',
    'scoreTotal': 'score_total',
    'confidenceScore': 'confidence_score',
    'topStrengthId': 'top_strength_id',
    'topWeaknessId': 'top_weakness_id',
    'flattenedScores': 'flattened_scores',
  },
);

Map<String, dynamic> _$XAIFlatReportDTOToJson(XAIFlatReportDTO instance) =>
    <String, dynamic>{
      'execution_id': instance.executionId,
      'timestamp': instance.timestamp.toIso8601String(),
      'verdict': instance.verdict,
      'score_total': instance.scoreTotal,
      'confidence_score': instance.confidenceScore,
      'top_strength_id': ?instance.topStrengthId,
      'top_weakness_id': ?instance.topWeaknessId,
      'flattened_scores': ?instance.flattenedScores,
    };
