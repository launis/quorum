// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_ui_schema.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WorkflowUiSchema _$WorkflowUiSchemaFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_WorkflowUiSchema', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['expected_inputs']);
      final val = _WorkflowUiSchema(
        expectedInputs: $checkedConvert(
          'expected_inputs',
          (v) =>
              (v as List<dynamic>?)
                  ?.map(
                    (e) => ExpectedInput.fromJson(e as Map<String, dynamic>),
                  )
                  .toList() ??
              const [],
        ),
      );
      return val;
    }, fieldKeyMap: const {'expectedInputs': 'expected_inputs'});

Map<String, dynamic> _$WorkflowUiSchemaToJson(
  _WorkflowUiSchema instance,
) => <String, dynamic>{
  'expected_inputs': instance.expectedInputs.map((e) => e.toJson()).toList(),
};
