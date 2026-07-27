// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'synthesis_config_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_SynthesisConfigDto _$SynthesisConfigDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_SynthesisConfigDto',
      json,
      ($checkedConvert) {
        final val = _SynthesisConfigDto(
          systemPrompt: $checkedConvert('system_prompt', (v) => v as String?),
          synthesisBlockId: $checkedConvert(
            'synthesis_block_id',
            (v) => v as String?,
          ),
          rowExplanationsBlockId: $checkedConvert(
            'row_explanations_block_id',
            (v) => v as String?,
          ),
          modelStrategy: $checkedConvert(
            'model_strategy',
            (v) => v as String? ?? 'synthesis',
          ),
          lengthConstraint: $checkedConvert(
            'length_constraint',
            (v) => (v as num?)?.toInt(),
          ),
          enablePiiMasking: $checkedConvert(
            'enable_pii_masking',
            (v) => v as bool? ?? false,
          ),
          omitEmptySections: $checkedConvert(
            'omit_empty_sections',
            (v) => v as bool? ?? true,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemPrompt': 'system_prompt',
        'synthesisBlockId': 'synthesis_block_id',
        'rowExplanationsBlockId': 'row_explanations_block_id',
        'modelStrategy': 'model_strategy',
        'lengthConstraint': 'length_constraint',
        'enablePiiMasking': 'enable_pii_masking',
        'omitEmptySections': 'omit_empty_sections',
      },
    );

Map<String, dynamic> _$SynthesisConfigDtoToJson(_SynthesisConfigDto instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'synthesis_block_id': instance.synthesisBlockId,
      'row_explanations_block_id': instance.rowExplanationsBlockId,
      'model_strategy': instance.modelStrategy,
      'length_constraint': instance.lengthConstraint,
      'enable_pii_masking': instance.enablePiiMasking,
      'omit_empty_sections': instance.omitEmptySections,
    };
