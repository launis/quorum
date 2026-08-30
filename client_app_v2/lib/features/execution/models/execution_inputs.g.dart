// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_inputs.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionInputs _$ExecutionInputsFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionInputs',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'raw_inputs',
            'dynamic_inputs',
            'user_role',
            'target_locale',
          ],
        );
        final val = _ExecutionInputs(
          rawInputs: $checkedConvert(
            'raw_inputs',
            (v) => v as Map<String, dynamic>? ?? const {},
          ),
          dynamicInputs: $checkedConvert(
            'dynamic_inputs',
            (v) => v as Map<String, dynamic>? ?? const {},
          ),
          userRole: $checkedConvert('user_role', (v) => v as String?),
          targetLocale: $checkedConvert('target_locale', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'rawInputs': 'raw_inputs',
        'dynamicInputs': 'dynamic_inputs',
        'userRole': 'user_role',
        'targetLocale': 'target_locale',
      },
    );

Map<String, dynamic> _$ExecutionInputsToJson(_ExecutionInputs instance) =>
    <String, dynamic>{
      'raw_inputs': instance.rawInputs,
      'dynamic_inputs': instance.dynamicInputs,
      'user_role': instance.userRole,
      'target_locale': instance.targetLocale,
    };
