// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_data_v2_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReportDataDto _$ReportDataDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ReportDataDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'execution_id',
            'workflow_id',
            'global_metrics',
            'global_synthesis',
            'results',
            'hydrated_references',
          ],
        );
        final val = _ReportDataDto(
          executionId: $checkedConvert('execution_id', (v) => v as String),
          workflowId: $checkedConvert('workflow_id', (v) => v as String),
          globalMetrics: $checkedConvert(
            'global_metrics',
            (v) => ExecutionMetricsDTO.fromJson(v as Map<String, dynamic>),
          ),
          globalSynthesis: $checkedConvert(
            'global_synthesis',
            (v) => v == null
                ? null
                : GlobalSynthesisDTO.fromJson(v as Map<String, dynamic>),
          ),
          results: $checkedConvert(
            'results',
            (v) => (v as List<dynamic>)
                .map((e) => AtomResultDTO.fromJson(e as Map<String, dynamic>))
                .toList(),
          ),
          hydratedReferences: $checkedConvert(
            'hydrated_references',
            (v) => (v as Map<String, dynamic>).map(
              (k, e) => MapEntry(
                k,
                HydratedAtomDTO.fromJson(e as Map<String, dynamic>),
              ),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'executionId': 'execution_id',
        'workflowId': 'workflow_id',
        'globalMetrics': 'global_metrics',
        'globalSynthesis': 'global_synthesis',
        'hydratedReferences': 'hydrated_references',
      },
    );

Map<String, dynamic> _$ReportDataDtoToJson(_ReportDataDto instance) =>
    <String, dynamic>{
      'execution_id': instance.executionId,
      'workflow_id': instance.workflowId,
      'global_metrics': instance.globalMetrics.toJson(),
      'global_synthesis': instance.globalSynthesis?.toJson(),
      'results': instance.results.map((e) => e.toJson()).toList(),
      'hydrated_references': instance.hydratedReferences.map(
        (k, e) => MapEntry(k, e.toJson()),
      ),
    };
