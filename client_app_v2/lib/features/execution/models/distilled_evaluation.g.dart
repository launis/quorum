// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'distilled_evaluation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DistilledEvaluation _$DistilledEvaluationFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_DistilledEvaluation',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'atom_id',
        'exact_quotes',
        'semantic_reasoning',
        'status',
        'extensions',
        'depends_on_tda_ids',
        'short_circuit_reason_tda_ids',
        'is_inverse_evidence',
        'topological_out_degree',
      ],
    );
    final val = _DistilledEvaluation(
      atomId: $checkedConvert('atom_id', (v) => v as String?),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
      semanticReasoning: $checkedConvert(
        'semantic_reasoning',
        (v) => v as String?,
      ),
      status: $checkedConvert('status', (v) => v as String?),
      extensions: $checkedConvert(
        'extensions',
        (v) => v as Map<String, dynamic>?,
      ),
      dependsOnTdaIds: $checkedConvert(
        'depends_on_tda_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      shortCircuitReasonTdaIds: $checkedConvert(
        'short_circuit_reason_tda_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      isInverseEvidence: $checkedConvert(
        'is_inverse_evidence',
        (v) => v as bool? ?? false,
      ),
      topologicalOutDegree: $checkedConvert(
        'topological_out_degree',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'atomId': 'atom_id',
    'exactQuotes': 'exact_quotes',
    'semanticReasoning': 'semantic_reasoning',
    'dependsOnTdaIds': 'depends_on_tda_ids',
    'shortCircuitReasonTdaIds': 'short_circuit_reason_tda_ids',
    'isInverseEvidence': 'is_inverse_evidence',
    'topologicalOutDegree': 'topological_out_degree',
  },
);

Map<String, dynamic> _$DistilledEvaluationToJson(
  _DistilledEvaluation instance,
) => <String, dynamic>{
  'atom_id': instance.atomId,
  'exact_quotes': instance.exactQuotes,
  'semantic_reasoning': instance.semanticReasoning,
  'status': instance.status,
  'extensions': instance.extensions,
  'depends_on_tda_ids': instance.dependsOnTdaIds,
  'short_circuit_reason_tda_ids': instance.shortCircuitReasonTdaIds,
  'is_inverse_evidence': instance.isInverseEvidence,
  'topological_out_degree': instance.topologicalOutDegree,
};
