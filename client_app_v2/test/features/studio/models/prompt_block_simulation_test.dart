import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';

void main() {
  group('PromptBlockSimulation DTO Contract Tests', () {
    final samplePromptBlockJson = {
      'category_id': 'system_rule',
      'id': 'blk_0195f3a0000070008000000000000001',
      'slug': 'test-block',
      'organization_id': 'org_0195f3a0000070008000000000000001',
      'label': {
        'translations': {'en': 'Test Block'},
      },
      'description': {
        'translations': {'en': 'Test description'},
      },
      'instruction_text': 'You are a test agent.',
    };

    test('test_prompt_block_simulation_request_deserialization_success', () {
      final validRequestJson = {
        'block': samplePromptBlockJson,
        'mock_inputs': {'target_speaker': 'speaker_0'},
        'target_scale_score': 3,
        'target_locale': 'en',
        'context_text': 'Simulated document text',
      };

      final request = PromptBlockSimulationRequest.fromJson(validRequestJson);

      expect(request.block.id, 'blk_0195f3a0000070008000000000000001');
      expect(request.mockInputs['target_speaker'], 'speaker_0');
      expect(request.targetScaleScore, 3);
      expect(request.targetLocale, 'en');
      expect(request.contextText, 'Simulated document text');

      final serialized = request.toJson();
      expect(serialized['target_scale_score'], 3);
      expect(serialized['target_locale'], 'en');
    });

    test(
      'test_prompt_block_simulation_request_hallucinated_fields_fail_fast',
      () {
        final hallucinatedJson = {
          'block': samplePromptBlockJson,
          'mock_inputs': <String, Object?>{},
          'hallucinated_field': 'invalid_value',
        };

        expect(
          () => PromptBlockSimulationRequest.fromJson(hallucinatedJson),
          throwsA(
            anyOf(
              isA<FormatException>(),
              isA<TypeError>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'test_prompt_block_simulation_request_missing_required_block_fails_fast',
      () {
        final missingBlockJson = <String, Object?>{
          'mock_inputs': {'target_speaker': 'speaker_0'},
          'target_locale': 'en',
        };

        expect(
          () => PromptBlockSimulationRequest.fromJson(missingBlockJson),
          throwsA(
            anyOf(
              isA<FormatException>(),
              isA<TypeError>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'test_prompt_block_simulation_request_invalid_scale_score_type_fails_fast',
      () {
        final invalidTypeJson = <String, Object?>{
          'block': samplePromptBlockJson,
          'target_scale_score': 'not_an_int',
        };

        expect(
          () => PromptBlockSimulationRequest.fromJson(invalidTypeJson),
          throwsA(
            anyOf(
              isA<FormatException>(),
              isA<TypeError>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test('test_prompt_block_simulation_response_deserialization_success', () {
      final validResponseJson = {
        'valid': true,
        'errors': <String>[],
        'rendered_prompt': 'Rendered prompt output text',
        'trace': {'execution_time_ms': 12.5},
        'prompt_context': null,
      };

      final response = PromptBlockSimulationResponse.fromJson(
        validResponseJson,
      );

      expect(response.valid, isTrue);
      expect(response.errors, isEmpty);
      expect(response.renderedPrompt, 'Rendered prompt output text');
      expect(response.trace.executionTimeMs, 12.5);
      expect(response.promptContext, isNull);

      final serialized = response.toJson();
      expect(serialized['rendered_prompt'], 'Rendered prompt output text');
      expect(serialized['valid'], isTrue);
    });

    test(
      'test_prompt_block_simulation_response_hallucinated_fields_fail_fast',
      () {
        final hallucinatedJson = {
          'valid': true,
          'errors': <String>[],
          'rendered_prompt': 'Output',
          'trace': <String, Object?>{},
          'unexpected_token': 999,
        };

        expect(
          () => PromptBlockSimulationResponse.fromJson(hallucinatedJson),
          throwsA(
            anyOf(
              isA<FormatException>(),
              isA<TypeError>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'test_prompt_block_simulation_response_invalid_field_types_fail_fast',
      () {
        final invalidTypeJson = <String, Object?>{
          'valid': 'not_a_boolean',
          'errors': 'not_a_list',
        };

        expect(
          () => PromptBlockSimulationResponse.fromJson(invalidTypeJson),
          throwsA(
            anyOf(
              isA<FormatException>(),
              isA<TypeError>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );
  });
}
