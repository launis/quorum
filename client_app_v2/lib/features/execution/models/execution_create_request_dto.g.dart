// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_create_request_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionCreateRequestDto _$ExecutionCreateRequestDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionCreateRequestDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'workflow_id',
        'target_locale',
        'raw_inputs',
        'profile_id',
        'matrix_sampling_strategy',
      ],
    );
    final val = _ExecutionCreateRequestDto(
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      targetLocale: $checkedConvert('target_locale', (v) => v as String),
      rawInputs: $checkedConvert(
        'raw_inputs',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      profileId: $checkedConvert('profile_id', (v) => v as String?),
      matrixSamplingStrategy: $checkedConvert(
        'matrix_sampling_strategy',
        (v) => (v as num?)?.toInt(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'targetLocale': 'target_locale',
    'rawInputs': 'raw_inputs',
    'profileId': 'profile_id',
    'matrixSamplingStrategy': 'matrix_sampling_strategy',
  },
);

Map<String, dynamic> _$ExecutionCreateRequestDtoToJson(
  _ExecutionCreateRequestDto instance,
) => <String, dynamic>{
  'workflow_id': instance.workflowId,
  'target_locale': instance.targetLocale,
  'raw_inputs': instance.rawInputs,
  'profile_id': instance.profileId,
  'matrix_sampling_strategy': instance.matrixSamplingStrategy,
};
