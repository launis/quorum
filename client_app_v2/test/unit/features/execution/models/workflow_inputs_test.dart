import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('WorkflowInputs Tests', () {
    test(
      'Positive: deserializes full and default JSON payloads and roundtrips cleanly',
      () {
        final orgId = generateOpaqueUuid7('org');
        final userId = generateOpaqueUuid7('usr');
        final fullJson = <String, Object?>{
          'organization_id': orgId,
          'user_id': userId,
          'simulation_mode': true,
          'language': 'fi',
          'dynamic_inputs': <String, Object?>{
            'transcript_text': 'Sample coaching session transcript.',
            'file_doc': <String, Object?>{
              'filename': 'session.pdf',
              'content_base64': 'YWJj',
            },
          },
        };

        final inputs = WorkflowInputs.fromJson(fullJson);
        expect(inputs.organizationId, equals(orgId));
        expect(inputs.userId, equals(userId));
        expect(inputs.simulationMode, isTrue);
        expect(inputs.language, equals('fi'));
        expect(
          inputs.dynamicInputs['transcript_text']?.textValue,
          equals('Sample coaching session transcript.'),
        );
        expect(
          inputs.dynamicInputs['file_doc']?.fileValue?.filename,
          equals('session.pdf'),
        );
        expect(inputs.toJson(), equals(fullJson));

        final minimalJson = <String, Object?>{};
        final defaultInputs = WorkflowInputs.fromJson(minimalJson);
        expect(defaultInputs.organizationId, isNull);
        expect(defaultInputs.userId, isNull);
        expect(defaultInputs.simulationMode, isFalse);
        expect(defaultInputs.language, equals('en'));
        expect(defaultInputs.dynamicInputs, isEmpty);
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'language': 'en',
          'simulation_mode': false,
          'unexpected_field': 'forbidden',
        };

        expect(
          () => WorkflowInputs.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException when fields have invalid types',
      () {
        final invalidSimulationModeType = <String, Object?>{
          'simulation_mode': 'not_a_bool',
        };
        expect(
          () => WorkflowInputs.fromJson(invalidSimulationModeType),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidDynamicInputsType = <String, Object?>{
          'dynamic_inputs': <Object?>['not', 'a', 'map'],
        };
        expect(
          () => WorkflowInputs.fromJson(invalidDynamicInputsType),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
