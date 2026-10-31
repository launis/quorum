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
        $checkKeys(
          json,
          allowedKeys: const [
            'system_prompt',
            'synthesis_block_id',
            'row_explanations_block_id',
            'length_constraint',
            'preamble_text',
            'tone_instruction',
          ],
        );
        final val = _SynthesisConfigDto(
          systemPrompt: $checkedConvert('system_prompt', (v) => v as String?),
          synthesisBlockId: $checkedConvert(
            'synthesis_block_id',
            (v) => _$JsonConverterFromJson<String, String>(
              v,
              const StrictOpaqueIdConverter().fromJson,
            ),
          ),
          rowExplanationsBlockId: $checkedConvert(
            'row_explanations_block_id',
            (v) => _$JsonConverterFromJson<String, String>(
              v,
              const StrictOpaqueIdConverter().fromJson,
            ),
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
      'synthesis_block_id': _$JsonConverterToJson<String, String>(
        instance.synthesisBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'row_explanations_block_id': _$JsonConverterToJson<String, String>(
        instance.rowExplanationsBlockId,
        const StrictOpaqueIdConverter().toJson,
      ),
      'length_constraint': instance.lengthConstraint,
      'preamble_text': instance.preambleText?.toJson(),
      'tone_instruction': instance.toneInstruction?.toJson(),
    };

Value? _$JsonConverterFromJson<Json, Value>(
  Object? json,
  Value? Function(Json json) fromJson,
) => json == null ? null : fromJson(json as Json);

Json? _$JsonConverterToJson<Json, Value>(
  Value? value,
  Json? Function(Value value) toJson,
) => value == null ? null : toJson(value);
