import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';

void main() {
  group('PromptBlockSimulation DTO Contract Tests', () {
    final samplePromptBlockJson = {
      'category_id': 'system_rule',
      'id': 'blk_7a8b9c0d1e2f3a4b',
      'slug': 'test-block',
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

      expect(request.block.id, 'blk_7a8b9c0d1e2f3a4b');
      expect(request.mockInputs['target_speaker'], 'speaker_0');
      expect(request.targetScaleScore, 3);
      expect(request.targetLocale, 'en');
      expect(request.contextText, 'Simulated document text');
    });

    test(
      'test_prompt_block_simulation_request_hallucinated_fields_fail_fast',
      () {
        final hallucinatedJson = {
          'block': samplePromptBlockJson,
          'mock_inputs': {},
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

    test('test_prompt_block_simulation_response_deserialization_success', () {
      final validResponseJson = {
        'valid': true,
        'errors': <String>[],
        'rendered_prompt': 'Rendered prompt output text',
        'trace': {'duration_ms': 12.5},
        'prompt_context': null,
      };

      final response = PromptBlockSimulationResponse.fromJson(
        validResponseJson,
      );

      expect(response.valid, isTrue);
      expect(response.errors, isEmpty);
      expect(response.renderedPrompt, 'Rendered prompt output text');
      expect(response.trace['duration_ms'], 12.5);
      expect(response.promptContext, isNull);
    });

    test(
      'test_prompt_block_simulation_response_hallucinated_fields_fail_fast',
      () {
        final hallucinatedJson = {
          'valid': true,
          'errors': <String>[],
          'rendered_prompt': 'Output',
          'trace': {},
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
  });
}
