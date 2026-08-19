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
          lengthConstraint: $checkedConvert(
            'length_constraint',
            (v) => (v as num?)?.toInt(),
          ),
          preambleText: $checkedConvert(
            'preamble_text',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          toneInstruction: $checkedConvert(
            'tone_instruction',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemPrompt': 'system_prompt',
        'synthesisBlockId': 'synthesis_block_id',
        'rowExplanationsBlockId': 'row_explanations_block_id',
        'lengthConstraint': 'length_constraint',
        'preambleText': 'preamble_text',
        'toneInstruction': 'tone_instruction',
      },
    );

Map<String, dynamic> _$SynthesisConfigDtoToJson(_SynthesisConfigDto instance) =>
    <String, dynamic>{
      'system_prompt': instance.systemPrompt,
      'synthesis_block_id': instance.synthesisBlockId,
      'row_explanations_block_id': instance.rowExplanationsBlockId,
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'tone_instruction': instance.toneInstruction?.toJson(),
    };
