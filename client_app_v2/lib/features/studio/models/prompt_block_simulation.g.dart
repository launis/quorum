// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prompt_block_simulation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_PromptBlockSimulationRequest _$PromptBlockSimulationRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_PromptBlockSimulationRequest',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'block',
        'mock_inputs',
        'target_scale_score',
        'target_locale',
        'context_text',
      ],
    );
    final val = _PromptBlockSimulationRequest(
      block: $checkedConvert(
        'block',
        (v) => PromptBlock.fromJson(v as Map<String, dynamic>),
      ),
      mockInputs: $checkedConvert(
        'mock_inputs',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      targetScaleScore: $checkedConvert(
        'target_scale_score',
        (v) => (v as num?)?.toInt(),
      ),
      targetLocale: $checkedConvert(
        'target_locale',
        (v) => v as String? ?? 'en',
      ),
      contextText: $checkedConvert(
        'context_text',
        (v) => v as String? ?? '[SIMULATED CONTEXT DOCUMENT]',
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'mockInputs': 'mock_inputs',
    'targetScaleScore': 'target_scale_score',
    'targetLocale': 'target_locale',
    'contextText': 'context_text',
  },
);

Map<String, dynamic> _$PromptBlockSimulationRequestToJson(
  _PromptBlockSimulationRequest instance,
) => <String, dynamic>{
  'block': instance.block.toJson(),
  'mock_inputs': instance.mockInputs,
  'target_scale_score': instance.targetScaleScore,
  'target_locale': instance.targetLocale,
  'context_text': instance.contextText,
};

_PromptBlockSimulationResponse _$PromptBlockSimulationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_PromptBlockSimulationResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'valid',
        'errors',
        'rendered_prompt',
        'trace',
        'prompt_context',
      ],
    );
    final val = _PromptBlockSimulationResponse(
      valid: $checkedConvert('valid', (v) => v as bool? ?? true),
      errors: $checkedConvert(
        'errors',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      renderedPrompt: $checkedConvert(
        'rendered_prompt',
        (v) => v as String? ?? '',
      ),
      trace: $checkedConvert(
        'trace',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
      promptContext: $checkedConvert(
        'prompt_context',
        (v) => v == null
            ? null
            : PromptContextDto.fromJson(v as Map<String, dynamic>),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'renderedPrompt': 'rendered_prompt',
    'promptContext': 'prompt_context',
  },
);

Map<String, dynamic> _$PromptBlockSimulationResponseToJson(
  _PromptBlockSimulationResponse instance,
) => <String, dynamic>{
  'valid': instance.valid,
  'errors': instance.errors,
  'rendered_prompt': instance.renderedPrompt,
  'trace': instance.trace,
  'prompt_context': instance.promptContext?.toJson(),
};
