// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_simulation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WorkflowSimulationResponse _$WorkflowSimulationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_WorkflowSimulationResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'valid',
        'errors',
        'step_status',
        'execution_order',
        'trace',
      ],
    );
    final val = _WorkflowSimulationResponse(
      valid: $checkedConvert('valid', (v) => v as bool? ?? true),
      errors: $checkedConvert(
        'errors',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      stepStatus: $checkedConvert(
        'step_status',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ) ??
            const {},
      ),
      executionOrder: $checkedConvert(
        'execution_order',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      trace: $checkedConvert(
        'trace',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'stepStatus': 'step_status',
    'executionOrder': 'execution_order',
  },
);

Map<String, dynamic> _$WorkflowSimulationResponseToJson(
  _WorkflowSimulationResponse instance,
) => <String, dynamic>{
  'valid': instance.valid,
  'errors': instance.errors,
  'step_status': instance.stepStatus,
  'execution_order': instance.executionOrder,
  'trace': instance.trace,
};
