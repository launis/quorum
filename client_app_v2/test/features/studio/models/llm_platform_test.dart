import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/llm_platform.dart';

void main() {
  group('LlmPlatform Contract Tests', () {
    test('test_llm_platform_json_deserialization_success', () {
      final validJson = {
        'id': 'vertex_ai',
        'label': 'Google Vertex AI',
        'has_regions': true,
      };

      final platform = LlmPlatform.fromJson(validJson);

      expect(platform.id, 'vertex_ai');
      expect(platform.label, 'Google Vertex AI');
      expect(platform.hasRegions, true);
    });

    test('test_llm_platform_missing_required_field_fail_fast', () {
      final incompleteJson = {
        'id': 'openai',
        'label': 'OpenAI',
        // 'has_regions' missing
      };

      expect(
        () => LlmPlatform.fromJson(incompleteJson),
        throwsA(anyOf(isA<FormatException>(), isA<CheckedFromJsonException>(), isA<TypeError>())),
      );
    });

    test('test_llm_platform_hallucinated_fields_fail_fast', () {
      final hallucinatedJson = {
        'id': 'openai',
        'label': 'OpenAI',
        'has_regions': false,
        'api_key': 'secret_123', // Unrecognized hallucinated key
      };

      expect(
        () => LlmPlatform.fromJson(hallucinatedJson),
        throwsA(anyOf(isA<FormatException>(), isA<CheckedFromJsonException>())),
      );
    });
  });
}
