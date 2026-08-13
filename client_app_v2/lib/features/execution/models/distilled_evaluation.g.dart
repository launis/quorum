// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'distilled_evaluation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DistilledEvaluation _$DistilledEvaluationFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_DistilledEvaluation',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'atom_id',
            'exact_quotes',
            'semantic_reasoning',
            'extensions',
          ],
        );
        final val = _DistilledEvaluation(
          atomId: $checkedConvert('atom_id', (v) => v as String?),
          exactQuotes: $checkedConvert(
            'exact_quotes',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const [],
          ),
          semanticReasoning: $checkedConvert(
            'semantic_reasoning',
            (v) => v as String?,
          ),
          extensions: $checkedConvert(
            'extensions',
            (v) => v as Map<String, dynamic>?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'atomId': 'atom_id',
        'exactQuotes': 'exact_quotes',
        'semanticReasoning': 'semantic_reasoning',
      },
    );

Map<String, dynamic> _$DistilledEvaluationToJson(
  _DistilledEvaluation instance,
) => <String, dynamic>{
  'atom_id': instance.atomId,
  'exact_quotes': instance.exactQuotes,
  'semantic_reasoning': instance.semanticReasoning,
  'extensions': instance.extensions,
};
