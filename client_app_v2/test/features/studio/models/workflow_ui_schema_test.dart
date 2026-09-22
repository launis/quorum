import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';

void main() {
  group('WorkflowUiSchema Contract Tests', () {
    test('test_workflow_ui_schema_deserialization_success', () {
      // Input: Valid JSON matching WorkflowSchemaResponseDTO
      final validJson = {
        'expected_inputs': [
          {
            'input_key': 'deliverable_text',
            'label': {
              'translations': {'en': 'Deliverable Document'},
            },
            'required': true,
            'is_chat_history': false,
            'is_endorsed_deliverable': true,
            'input_modes': ['text', 'file'],
            'description': {
              'translations': {'en': 'The main candidate deliverable'},
            },
            'scan_for_performative_patterns': true,
            'ai_description': 'Executive strategy report',
            'questionnaire_definition': [],
          },
        ],
      };

      // Act
      final schema = WorkflowUiSchema.fromJson(validJson);

      // Expected: Instantiates WorkflowUiSchema with List<ExpectedInput>
      expect(schema.expectedInputs.length, 1);
      final input = schema.expectedInputs.first;
      expect(input.inputKey, 'deliverable_text');
      expect(input.label.translations['en'], 'Deliverable Document');
      expect(input.required, isTrue);
      expect(input.isEndorsedDeliverable, isTrue);
      expect(input.scanForPerformativePatterns, isTrue);
      expect(input.aiDescription, 'Executive strategy report');
    });

    test('test_workflow_ui_schema_hallucinated_fields_fail_fast', () {
      final hallucinatedJson = {
        'expected_inputs': [],
        'hallucinated_property': 'illegal_payload',
      };

      expect(
        () => WorkflowUiSchema.fromJson(hallucinatedJson),
        throwsA(anyOf(isA<FormatException>(), isA<TypeError>(), isA<CheckedFromJsonException>())),
      );
    });

    test('test_workflow_ui_schema_invalid_type_fail_fast', () {
      final invalidTypeJson = {
        'expected_inputs': 'not_a_list',
      };

      expect(
        () => WorkflowUiSchema.fromJson(invalidTypeJson),
        throwsA(anyOf(isA<TypeError>(), isA<FormatException>(), isA<CheckedFromJsonException>())),
      );
    });
  });
}
