// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_input.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionInput _$ExecutionInputFromJson(Map<String, dynamic> json) =>
    _ExecutionInput(
      workflowId: json['workflow_id'] as String,
      inputs: json['inputs'] as Map<String, dynamic>? ?? const {},
      files:
          (json['files'] as Map<String, dynamic>?)?.map(
            (k, e) =>
                MapEntry(k, ExecutionFile.fromJson(e as Map<String, dynamic>)),
          ) ??
          const {},
      guidedReflection:
          json['guided_reflection'] == null
              ? null
              : GuidedReflectionDTO.fromJson(
                json['guided_reflection'] as Map<String, dynamic>,
              ),
    );

Map<String, dynamic> _$ExecutionInputToJson(_ExecutionInput instance) =>
    <String, dynamic>{
      'workflow_id': instance.workflowId,
      'inputs': instance.inputs,
      'guided_reflection': instance.guidedReflection,
    };
