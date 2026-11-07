// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'distilled_evaluation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DistilledExtensionValue _$DistilledExtensionValueFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_DistilledExtensionValue',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'string_value',
        'number_value',
        'bool_value',
        'string_list_value',
      ],
    );
    final val = _DistilledExtensionValue(
      stringValue: $checkedConvert('string_value', (v) => v as String?),
      numberValue: $checkedConvert(
        'number_value',
        (v) => (v as num?)?.toDouble(),
      ),
      boolValue: $checkedConvert('bool_value', (v) => v as bool?),
      stringListValue: $checkedConvert(
        'string_list_value',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'stringValue': 'string_value',
    'numberValue': 'number_value',
    'boolValue': 'bool_value',
    'stringListValue': 'string_list_value',
  },
);

Map<String, dynamic> _$DistilledExtensionValueToJson(
  _DistilledExtensionValue instance,
) => <String, dynamic>{
  'string_value': instance.stringValue,
  'number_value': instance.numberValue,
  'bool_value': instance.boolValue,
  'string_list_value': instance.stringListValue,
};

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
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) =>
              MapEntry(k, const DistilledExtensionValueConverter().fromJson(e)),
        ),
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
  'extensions': instance.extensions?.map(
    (k, e) => MapEntry(k, const DistilledExtensionValueConverter().toJson(e)),
  ),
  'depends_on_tda_ids': instance.dependsOnTdaIds,
  'short_circuit_reason_tda_ids': instance.shortCircuitReasonTdaIds,
  'is_inverse_evidence': instance.isInverseEvidence,
  'topological_out_degree': instance.topologicalOutDegree,
};
