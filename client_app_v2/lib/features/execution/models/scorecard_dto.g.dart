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
