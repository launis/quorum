// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_inputs.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WorkflowInputs _$WorkflowInputsFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_WorkflowInputs',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'organization_id',
            'user_id',
            'simulation_mode',
            'language',
            'dynamic_inputs',
          ],
        );
        final val = _WorkflowInputs(
          organizationId: $checkedConvert(
            'organization_id',
            (v) => v as String?,
          ),
          userId: $checkedConvert('user_id', (v) => v as String?),
          simulationMode: $checkedConvert(
            'simulation_mode',
            (v) => v as bool? ?? false,
          ),
          language: $checkedConvert('language', (v) => v as String? ?? 'en'),
          dynamicInputs: $checkedConvert(
            'dynamic_inputs',
            (v) => v as Map<String, dynamic>? ?? const {},
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'organizationId': 'organization_id',
        'userId': 'user_id',
        'simulationMode': 'simulation_mode',
        'dynamicInputs': 'dynamic_inputs',
      },
    );

Map<String, dynamic> _$WorkflowInputsToJson(_WorkflowInputs instance) =>
    <String, dynamic>{
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'simulation_mode': instance.simulationMode,
      'language': instance.language,
      'dynamic_inputs': instance.dynamicInputs,
    };
