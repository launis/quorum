import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  const validStepId = 'stp_0195f3a00000700080008172bda70c86';

  group('StepSimulationTraceDto Tests', () {
    test(
      'Positive: deserializes valid JSON payload, applies defaults, and roundtrips cleanly',
      () {
        final emptyTrace = StepSimulationTraceDto.fromJson(<String, Object?>{});
        expect(emptyTrace.executionTimeMs, equals(0.0));
        expect(emptyTrace.estimatedTokens, equals(0));

        final validJson = <String, Object?>{
          'execution_time_ms': 42.5,
          'estimated_tokens': 1250,
        };
        final trace = StepSimulationTraceDto.fromJson(validJson);
        expect(trace.executionTimeMs, equals(42.5));
        expect(trace.estimatedTokens, equals(1250));
        expect(trace.toJson(), equals(validJson));

        final updated = trace.copyWith(estimatedTokens: 1500);
        expect(updated.executionTimeMs, equals(42.5));
        expect(updated.estimatedTokens, equals(1500));
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'execution_time_ms': 10.0,
          'estimated_tokens': 100,
          'unexpected_field': 'forbidden',
        };
        expect(
          () => StepSimulationTraceDto.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when field types are invalid',
      () {
        final invalidFieldType = <String, Object?>{
          'execution_time_ms': 'not_a_number',
          'estimated_tokens': 100,
        };
        expect(
          () => StepSimulationTraceDto.fromJson(invalidFieldType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });

  group('LlmMessageDto & PromptContextDto Tests', () {
    test(
      'Positive: deserializes LlmMessageDto and PromptContextDto cleanly and preserves metadata',
      () {
        final msgJson = <String, Object?>{
          'role': 'system',
          'content': 'You are an analytical assistant.',
          'tool_calls': null,
          'tool_call_id': 'call_123',
          'name': 'analyzer_tool',
        };
        final msg = LlmMessageDto.fromJson(msgJson);
        expect(msg.role, equals('system'));
        expect(msg.content, equals('You are an analytical assistant.'));
        expect(msg.toolCalls, isNull);
        expect(msg.toolCallId, equals('call_123'));
        expect(msg.name, equals('analyzer_tool'));
        expect(msg.toJson(), equals(msgJson));

        final contextJson = <String, Object?>{
          'static_messages': <Object?>[msgJson],
          'dynamic_messages': <Object?>[],
          'metadata': <String, Object?>{
            'token_proxy': 512,
            'model_tier': 'fast',
            'cache_hit': true,
            'tags': <Object?>['alpha', 'beta'],
          },
        };
        final ctx = PromptContextDto.fromJson(contextJson);
        expect(ctx.staticMessages, hasLength(1));
        expect(ctx.staticMessages.first.role, equals('system'));
        expect(ctx.dynamicMessages, isEmpty);
        expect(ctx.metadata['token_proxy']?.numberValue, equals(512.0));
        expect(ctx.metadata['token_proxy']?.rawValue, equals(512.0));
        expect(ctx.metadata['model_tier']?.stringValue, equals('fast'));
        expect(ctx.metadata['cache_hit']?.boolValue, isTrue);
        expect(
          ctx.metadata['tags']?.stringListValue,
          equals(<String>['alpha', 'beta']),
        );
        expect(ctx.toJson(), equals(contextJson));
      },
    );

    test(
      'Negative 1: rejects unrecognized keys in LlmMessageDto, PromptContextDto, and PromptContextMetaValue',
      () {
        expect(
          () => LlmMessageDto.fromJson(<String, Object?>{
            'role': 'user',
            'content': 'Hello',
            'extra_key': true,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => PromptContextDto.fromJson(<String, Object?>{
            'static_messages': <Object?>[],
            'unknown_key': 123,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => PromptContextMetaValue.fromJson(<String, Object?>{
            'string_value': 'ok',
            'unrecognized_meta_field': 1,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when required LlmMessageDto fields or metadata types are malformed',
      () {
        expect(
          () => LlmMessageDto.fromJson(<String, Object?>{'role': 'user'}),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => LlmMessageDto.fromJson(<String, Object?>{
            'role': 999,
            'content': 'Invalid role type',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => PromptContextDto.fromJson(<String, Object?>{
            'metadata': <String, Object?>{
              'nested_object': <String, Object?>{'invalid': true},
            },
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => PromptContextDto.fromJson(<String, Object?>{
            'metadata': <String, Object?>{
              'bad_list': <Object?>['valid_string', 42],
            },
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });

  group('StepSimulationRequest & StepSimulationResponse Tests', () {
    test(
      'Positive: serializes and deserializes StepSimulationRequest and StepSimulationResponse',
      () {
        const step = NodeStrategy.llm(
          id: validStepId,
          slug: 'step_analysis',
          name: I18nText(
            translations: {'en': 'Analysis Step', 'fi': 'Analyysivaihe'},
          ),
          cognitiveTier: CognitiveTier.fast,
          expectedInputs: ['doc_text'],
        );

        const request = StepSimulationRequest(
          step: step,
          mockInputs: {'doc_text': 'Sample context'},
          targetLocale: 'fi',
          contextText: 'Custom context document',
        );

        final requestJson = request.toJson();
        final roundtrippedRequest = StepSimulationRequest.fromJson(requestJson);
        expect(roundtrippedRequest.step.id, equals(validStepId));
        expect(roundtrippedRequest.targetLocale, equals('fi'));
        expect(
          roundtrippedRequest.mockInputs['doc_text'],
          equals('Sample context'),
        );
        expect(
          roundtrippedRequest.contextText,
          equals('Custom context document'),
        );

        final responseJson = <String, Object?>{
          'valid': true,
          'errors': <Object?>[],
          'rendered_prompt': 'Rendered prompt text',
          'trace': <String, Object?>{
            'execution_time_ms': 15.2,
            'estimated_tokens': 320,
          },
          'prompt_context': <String, Object?>{
            'static_messages': <Object?>[
              <String, Object?>{
                'role': 'system',
                'content': 'Static system prompt',
                'tool_calls': null,
                'tool_call_id': null,
                'name': null,
              },
            ],
            'dynamic_messages': <Object?>[],
            'metadata': <String, Object?>{},
          },
        };

        final response = StepSimulationResponse.fromJson(responseJson);
        expect(response.valid, isTrue);
        expect(response.errors, isEmpty);
        expect(response.renderedPrompt, equals('Rendered prompt text'));
        expect(response.trace.executionTimeMs, equals(15.2));
        expect(response.trace.estimatedTokens, equals(320));
        expect(response.promptContext?.staticMessages, hasLength(1));
        expect(response.toJson(), equals(responseJson));
      },
    );

    test(
      'Negative 1: rejects unrecognized keys in StepSimulationRequest and StepSimulationResponse',
      () {
        expect(
          () => StepSimulationResponse.fromJson(<String, Object?>{
            'valid': true,
            'forbidden_extra': 'value',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => StepSimulationRequest.fromJson(<String, Object?>{
            'target_locale': 'en',
            'unrecognized_field': 42,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: rejects missing required step or malformed opaque ID in StepSimulationRequest',
      () {
        expect(
          () => StepSimulationRequest.fromJson(<String, Object?>{
            'target_locale': 'en',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => StepSimulationRequest.fromJson(<String, Object?>{
            'step': <String, Object?>{
              'type': 'llm',
              'id': 'invalid_short_id',
              'slug': 'step_bad',
              'name': <String, Object?>{'en': 'Bad Step'},
            },
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
