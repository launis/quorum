// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_metrics_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionMetricsDTO _$ExecutionMetricsDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionMetricsDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'total_atoms',
            'evaluated',
            'short_circuited_na',
            'duration_ms',
          ],
        );
        final val = _ExecutionMetricsDTO(
          totalAtoms: $checkedConvert('total_atoms', (v) => (v as num).toInt()),
          evaluated: $checkedConvert('evaluated', (v) => (v as num).toInt()),
          shortCircuitedNa: $checkedConvert(
            'short_circuited_na',
            (v) => (v as num).toInt(),
          ),
          durationMs: $checkedConvert(
            'duration_ms',
            (v) => (v as num?)?.toInt() ?? 0,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'totalAtoms': 'total_atoms',
        'shortCircuitedNa': 'short_circuited_na',
        'durationMs': 'duration_ms',
      },
    );

Map<String, dynamic> _$ExecutionMetricsDTOToJson(
  _ExecutionMetricsDTO instance,
) => <String, dynamic>{
  'total_atoms': instance.totalAtoms,
  'evaluated': instance.evaluated,
  'short_circuited_na': instance.shortCircuitedNa,
  'duration_ms': instance.durationMs,
};
