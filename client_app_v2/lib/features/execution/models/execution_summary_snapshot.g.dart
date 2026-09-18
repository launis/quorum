// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_summary_snapshot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionSummarySnapshot _$ExecutionSummarySnapshotFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionSummarySnapshot',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'strictness_level',
        'is_ensemble_run',
        'is_degraded',
        'system_concurrency_snapshot',
      ],
    );
    final val = _ExecutionSummarySnapshot(
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt() ?? 100,
      ),
      isEnsembleRun: $checkedConvert(
        'is_ensemble_run',
        (v) => v as bool? ?? false,
      ),
      isDegraded: $checkedConvert('is_degraded', (v) => v as bool? ?? false),
      systemConcurrencySnapshot: $checkedConvert(
        'system_concurrency_snapshot',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, (e as num).toInt()),
            ) ??
            const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'strictnessLevel': 'strictness_level',
    'isEnsembleRun': 'is_ensemble_run',
    'isDegraded': 'is_degraded',
    'systemConcurrencySnapshot': 'system_concurrency_snapshot',
  },
);

Map<String, dynamic> _$ExecutionSummarySnapshotToJson(
  _ExecutionSummarySnapshot instance,
) => <String, dynamic>{
  'strictness_level': instance.strictnessLevel,
  'is_ensemble_run': instance.isEnsembleRun,
  'is_degraded': instance.isDegraded,
  'system_concurrency_snapshot': instance.systemConcurrencySnapshot,
};
