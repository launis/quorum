// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_simulation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_StepSimulationTraceDto _$StepSimulationTraceDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_StepSimulationTraceDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['execution_time_ms', 'estimated_tokens'],
    );
    final val = _StepSimulationTraceDto(
      executionTimeMs: $checkedConvert(
        'execution_time_ms',
        (v) => (v as num?)?.toDouble() ?? 0.0,
      ),
      estimatedTokens: $checkedConvert(
        'estimated_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'executionTimeMs': 'execution_time_ms',
    'estimatedTokens': 'estimated_tokens',
  },
);

Map<String, dynamic> _$StepSimulationTraceDtoToJson(
  _StepSimulationTraceDto instance,
) => <String, dynamic>{
  'execution_time_ms': instance.executionTimeMs,
  'estimated_tokens': instance.estimatedTokens,
};

_LlmMessageDto _$LlmMessageDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_LlmMessageDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'role',
            'content',
            'tool_calls',
            'tool_call_id',
            'name',
          ],
        );
        final val = _LlmMessageDto(
          role: $checkedConvert('role', (v) => v as String),
          content: $checkedConvert('content', (v) => v as String),
          toolCalls: $checkedConvert('tool_calls', (v) => v),
          toolCallId: $checkedConvert('tool_call_id', (v) => v as String?),
          name: $checkedConvert('name', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'toolCalls': 'tool_calls',
        'toolCallId': 'tool_call_id',
      },
    );

Map<String, dynamic> _$LlmMessageDtoToJson(_LlmMessageDto instance) =>
    <String, dynamic>{
      'role': instance.role,
      'content': instance.content,
      'tool_calls': instance.toolCalls,
      'tool_call_id': instance.toolCallId,
      'name': instance.name,
    };

_PromptContextDto _$PromptContextDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_PromptContextDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['static_messages', 'dynamic_messages', 'metadata'],
    );
    final val = _PromptContextDto(
      staticMessages: $checkedConvert(
        'static_messages',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => LlmMessageDto.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      dynamicMessages: $checkedConvert(
        'dynamic_messages',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => LlmMessageDto.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      metadata: $checkedConvert(
        'metadata',
        (v) => v as Map<String, dynamic>? ?? const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'staticMessages': 'static_messages',
    'dynamicMessages': 'dynamic_messages',
  },
);

Map<String, dynamic> _$PromptContextDtoToJson(
  _PromptContextDto instance,
) => <String, dynamic>{
  'static_messages': instance.staticMessages.map((e) => e.toJson()).toList(),
  'dynamic_messages': instance.dynamicMessages.map((e) => e.toJson()).toList(),
  'metadata': instance.metadata,
};

_StepSimulationRequest _$StepSimulationRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_StepSimulationRequest',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'step',
        'mock_inputs',
        'target_locale',
        'context_text',
      ],
    );
    final val = _StepSimulationRequest(
      step: $checkedConvert(
        'step',
        (v) => NodeStrategy.fromJson(v as Map<String, dynamic>),
      ),
      mockInputs: $checkedConvert(
        'mock_inputs',
        (v) => v as Map<String, dynamic>? ?? const {},
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
    'targetLocale': 'target_locale',
    'contextText': 'context_text',
  },
);

Map<String, dynamic> _$StepSimulationRequestToJson(
  _StepSimulationRequest instance,
) => <String, dynamic>{
  'step': instance.step.toJson(),
  'mock_inputs': instance.mockInputs,
  'target_locale': instance.targetLocale,
  'context_text': instance.contextText,
};

_StepSimulationResponse _$StepSimulationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_StepSimulationResponse',
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
    final val = _StepSimulationResponse(
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
        (v) => v == null
            ? const StepSimulationTraceDto()
            : StepSimulationTraceDto.fromJson(v as Map<String, dynamic>),
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

Map<String, dynamic> _$StepSimulationResponseToJson(
  _StepSimulationResponse instance,
) => <String, dynamic>{
  'valid': instance.valid,
  'errors': instance.errors,
  'rendered_prompt': instance.renderedPrompt,
  'trace': instance.trace.toJson(),
  'prompt_context': instance.promptContext?.toJson(),
};
