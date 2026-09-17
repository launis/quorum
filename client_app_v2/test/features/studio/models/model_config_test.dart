import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/features/studio/models/model_config.dart';

void main() {
  group('ModelConfig Domain & Serialization Parity', () {
    test(
      'Positive: Parses complete Option A ModelConfig with 4 canonical tiers',
      () {
        final payload = {
          'id': 'sys_e26807f3bfa3454d',
          'name': 'Google Gemini Sovereign Stack',
          'slug': 'gemini-stack',
          'type': 'model_registry',
          'default_provider': 'google',
          'tier_definitions': {
            'fast': {
              'provider': 'google',
              'model_name': 'gemini-3.8-flash',
              'temperature': 0.2,
              'max_tokens': 4096,
              'supports_grounding': true,
              'is_active': true,
              'allowed_tools': <String>['search'],
            },
            'balanced': {
              'provider': 'google',
              'model_name': 'gemini-3.8-flash',
              'temperature': 0.5,
            },
            'deep': {
              'provider': 'google',
              'model_name': 'gemini-3.8-pro',
              'temperature': 0.7,
            },
            'reasoning': {
              'provider': 'google',
              'model_name': 'gemini-3.8-pro',
              'thinking_budget_tokens': 8192,
            },
          },
        };

        final config = ModelConfig.fromJson(payload);
        expect(config.id, 'sys_e26807f3bfa3454d');
        expect(config.name, 'Google Gemini Sovereign Stack');
        expect(config.defaultProvider, 'google');
        expect(config.tierDefinitions.length, 4);
        expect(config.tierDefinitions['fast']!.modelName, 'gemini-3.8-flash');
        expect(config.tierDefinitions['fast']!.supportsGrounding, isTrue);
        expect(config.tierDefinitions['reasoning']!.thinkingBudgetTokens, 8192);
      },
    );

    test('Negative 1: Throws CheckedFromJsonException when id is missing', () {
      final payload = {
        'name': 'Invalid Stack',
        'type': 'model_registry',
        'tier_definitions': <String, dynamic>{},
      };

      expect(
        () => ModelConfig.fromJson(payload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test(
      'Negative 2: Throws CheckedFromJsonException on unrecognized key in ModelConfig',
      () {
        final payload = {
          'id': 'sys_1234567890abcdef',
          'type': 'model_registry',
          'unrecognized_extra_key': 'illegal',
          'tier_definitions': <String, dynamic>{},
        };

        expect(
          () => ModelConfig.fromJson(payload),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 3: Throws CheckedFromJsonException on unrecognized key in LlmModelConfig',
      () {
        final payload = {
          'id': 'sys_1234567890abcdef',
          'type': 'model_registry',
          'tier_definitions': {
            'fast': {
              'provider': 'google',
              'model_name': 'gemini-3.8-flash',
              'illegal_tier_key': 999,
            },
          },
        };

        expect(
          () => ModelConfig.fromJson(payload),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 4: Throws CheckedFromJsonException when numeric field receives invalid type',
      () {
        final payload = {
          'id': 'sys_1234567890abcdef',
          'type': 'model_registry',
          'tier_definitions': {
            'fast': {
              'provider': 'google',
              'model_name': 'gemini-3.8-flash',
              'temperature': 'invalid_string_instead_of_double',
            },
          },
        };

        expect(
          () => ModelConfig.fromJson(payload),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
