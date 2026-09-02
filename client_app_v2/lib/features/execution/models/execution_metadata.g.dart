// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_metadata.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionMetadata _$ExecutionMetadataFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionMetadata',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'matrix_sampling_strategy',
            'workflow_version',
            'global_context_vars',
          ],
        );
        final val = _ExecutionMetadata(
          matrixSamplingStrategy: $checkedConvert(
            'matrix_sampling_strategy',
            (v) => (v as num?)?.toInt(),
          ),
          workflowVersion: $checkedConvert(
            'workflow_version',
            (v) => (v as num?)?.toInt() ?? 1,
          ),
          globalContextVars: $checkedConvert(
            'global_context_vars',
            (v) => v as Map<String, dynamic>?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'matrixSamplingStrategy': 'matrix_sampling_strategy',
        'workflowVersion': 'workflow_version',
        'globalContextVars': 'global_context_vars',
      },
    );

Map<String, dynamic> _$ExecutionMetadataToJson(_ExecutionMetadata instance) =>
    <String, dynamic>{
      'matrix_sampling_strategy': instance.matrixSamplingStrategy,
      'workflow_version': instance.workflowVersion,
      'global_context_vars': instance.globalContextVars,
    };
