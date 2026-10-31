import 'package:client_app/features/studio/models/llm_platform.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('LlmPlatform Tests', () {
    test(
      'Positive: deserializes valid JSON payload, supports copyWith, and roundtrips cleanly',
      () {
        final validJson = <String, Object?>{
          'id': 'vertex_ai',
          'label': 'Google Cloud Vertex AI',
          'has_regions': true,
        };

        final platform = LlmPlatform.fromJson(validJson);
        expect(platform.id, equals('vertex_ai'));
        expect(platform.label, equals('Google Cloud Vertex AI'));
        expect(platform.hasRegions, isTrue);
        expect(platform.toJson(), equals(validJson));

        final updated = platform.copyWith(
          id: 'ai_studio',
          label: 'Google AI Studio',
          hasRegions: false,
        );
        expect(updated.id, equals('ai_studio'));
        expect(updated.label, equals('Google AI Studio'));
        expect(updated.hasRegions, isFalse);
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'id': 'vertex_ai',
          'label': 'Google Cloud Vertex AI',
          'has_regions': true,
          'unexpected_field': 'forbidden',
        };

        expect(
          () => LlmPlatform.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when required fields are missing or have invalid types',
      () {
        final missingRequiredField = <String, Object?>{
          'id': 'vertex_ai',
          'label': 'Google Cloud Vertex AI',
        };
        expect(
          () => LlmPlatform.fromJson(missingRequiredField),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidFieldType = <String, Object?>{
          'id': 'vertex_ai',
          'label': 'Google Cloud Vertex AI',
          'has_regions': 'not_a_boolean',
        };
        expect(
          () => LlmPlatform.fromJson(invalidFieldType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
