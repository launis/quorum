// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scorecard_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ScorecardResponseDto _$ScorecardResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ScorecardResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'execution_id',
        'workflow_id',
        'global_average',
        'evaluative_matrices',
        'informational_matrices',
      ],
    );
    final val = _ScorecardResponseDto(
      executionId: $checkedConvert('execution_id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      globalAverage: $checkedConvert(
        'global_average',
        (v) => (v as num?)?.toDouble(),
      ),
      evaluativeMatrices: $checkedConvert(
        'evaluative_matrices',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      informationalMatrices: $checkedConvert(
        'informational_matrices',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'executionId': 'execution_id',
    'workflowId': 'workflow_id',
    'globalAverage': 'global_average',
    'evaluativeMatrices': 'evaluative_matrices',
    'informationalMatrices': 'informational_matrices',
  },
);

Map<String, dynamic> _$ScorecardResponseDtoToJson(
  _ScorecardResponseDto instance,
) => <String, dynamic>{
  'execution_id': instance.executionId,
  'workflow_id': instance.workflowId,
  'global_average': instance.globalAverage,
  'evaluative_matrices': instance.evaluativeMatrices
      .map((e) => e.toJson())
      .toList(),
  'informational_matrices': instance.informationalMatrices
      .map((e) => e.toJson())
      .toList(),
};

_MatrixScorecardRowDto _$MatrixScorecardRowDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_MatrixScorecardRowDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'block_id',
        'label_fi',
        'label_en',
        'score',
        'scale_max',
        'normalized_score',
        'true_atoms',
        'total_atoms',
        'justification',
        'missing_context',
        'level_breakdown',
        'is_evaluative',
      ],
    );
    final val = _MatrixScorecardRowDto(
      blockId: $checkedConvert('block_id', (v) => v as String),
      labelFi: $checkedConvert('label_fi', (v) => v as String),
      labelEn: $checkedConvert('label_en', (v) => v as String),
      score: $checkedConvert('score', (v) => (v as num).toDouble()),
      scaleMax: $checkedConvert('scale_max', (v) => (v as num?)?.toDouble()),
      normalizedScore: $checkedConvert(
        'normalized_score',
        (v) => (v as num?)?.toDouble(),
      ),
      trueAtoms: $checkedConvert('true_atoms', (v) => (v as num?)?.toInt()),
      totalAtoms: $checkedConvert('total_atoms', (v) => (v as num?)?.toInt()),
      justification: $checkedConvert(
        'justification',
        (v) => v as String? ?? '',
      ),
      missingContext: $checkedConvert(
        'missing_context',
        (v) => v as String? ?? '',
      ),
      levelBreakdown: $checkedConvert(
        'level_breakdown',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, Map<String, int>.from(e as Map)),
        ),
      ),
      isEvaluative: $checkedConvert('is_evaluative', (v) => v as bool? ?? true),
    );
    return val;
  },
  fieldKeyMap: const {
    'blockId': 'block_id',
    'labelFi': 'label_fi',
    'labelEn': 'label_en',
    'scaleMax': 'scale_max',
    'normalizedScore': 'normalized_score',
    'trueAtoms': 'true_atoms',
    'totalAtoms': 'total_atoms',
    'missingContext': 'missing_context',
    'levelBreakdown': 'level_breakdown',
    'isEvaluative': 'is_evaluative',
  },
);

Map<String, dynamic> _$MatrixScorecardRowDtoToJson(
  _MatrixScorecardRowDto instance,
) => <String, dynamic>{
  'block_id': instance.blockId,
  'label_fi': instance.labelFi,
  'label_en': instance.labelEn,
  'score': instance.score,
  'scale_max': instance.scaleMax,
  'normalized_score': instance.normalizedScore,
  'true_atoms': instance.trueAtoms,
  'total_atoms': instance.totalAtoms,
  'justification': instance.justification,
  'missing_context': instance.missingContext,
  'level_breakdown': instance.levelBreakdown,
  'is_evaluative': instance.isEvaluative,
};
