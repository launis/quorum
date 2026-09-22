import 'package:client_app/core/api/workflow_client.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late WorkflowClient client;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    client = WorkflowClient(mockDio);
  });

  group('WorkflowClient Unit Tests', () {
    test(
      'getWorkflowUiSchema returns strongly typed WorkflowUiSchema on valid 200',
      () async {
        const workflowId = 'wf_executive_review';
        final mockPayload = {
          'expected_inputs': [
            {
              'input_key': 'deliverable_text',
              'label': {
                'translations': {
                  'en': 'Deliverable Document',
                  'fi': 'Asiakirja',
                },
              },
              'required': true,
              'is_chat_history': false,
              'is_endorsed_deliverable': true,
              'input_modes': ['text', 'file'],
              'description': {
                'translations': {
                  'en': 'Executive coaching brief',
                  'fi': 'Johtamisen valmennustehtävä',
                },
              },
              'scan_for_performative_patterns': false,
              'ai_description': 'Primary text deliverable to evaluate',
              'questionnaire_definition': <Map<String, dynamic>>[],
            },
          ],
        };

        when(
          () => mockDio.get('/api/v2/workflows/$workflowId/ui_schema'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/v2/workflows/$workflowId/ui_schema',
            ),
            data: mockPayload,
            statusCode: 200,
          ),
        );

        final result = await client.getWorkflowUiSchema(workflowId);

        expect(result, isA<WorkflowUiSchema>());
        expect(result.expectedInputs.length, 1);
        final input = result.expectedInputs.first;
        expect(input.inputKey, 'deliverable_text');
        expect(input.isEndorsedDeliverable, isTrue);
        expect(input.required, isTrue);
        expect(input.label.get('en'), 'Deliverable Document');
        expect(input.description.get('fi'), 'Johtamisen valmennustehtävä');

        verify(
          () => mockDio.get('/api/v2/workflows/$workflowId/ui_schema'),
        ).called(1);
      },
    );

    test(
      'getWorkflowUiSchema fails fast with UnrecognizedKeysException on unrecognized keys',
      () async {
        const workflowId = 'wf_test_drift';
        final corruptPayload = {
          'expected_inputs': <Map<String, dynamic>>[],
          'unrecognized_legacy_parameter': 'corrupt_data',
        };

        when(
          () => mockDio.get('/api/v2/workflows/$workflowId/ui_schema'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/v2/workflows/$workflowId/ui_schema',
            ),
            data: corruptPayload,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflowUiSchema(workflowId),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.message,
              'message',
              contains('Unrecognized keys: [unrecognized_legacy_parameter]'),
            ),
          ),
        );
      },
    );

    test(
      'getWorkflowUiSchema rethrows DioException on network or HTTP 404 failure',
      () async {
        const workflowId = 'wf_nonexistent';

        when(
          () => mockDio.get('/api/v2/workflows/$workflowId/ui_schema'),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: '/api/v2/workflows/$workflowId/ui_schema',
            ),
            response: Response(
              requestOptions: RequestOptions(
                path: '/api/v2/workflows/$workflowId/ui_schema',
              ),
              statusCode: 404,
              statusMessage: 'Workflow Not Found',
            ),
            type: DioExceptionType.badResponse,
          ),
        );

        expect(
          () => client.getWorkflowUiSchema(workflowId),
          throwsA(
            isA<DioException>().having(
              (e) => e.response?.statusCode,
              'statusCode',
              404,
            ),
          ),
        );
      },
    );

    test(
      'getWorkflowUiSchema fails fast on malformed inner expected_inputs payload',
      () async {
        const workflowId = 'wf_malformed_inputs';
        final malformedPayload = {
          'expected_inputs': [
            {
              // missing required input_key, label, description
              'required': true,
            },
          ],
        };

        when(
          () => mockDio.get('/api/v2/workflows/$workflowId/ui_schema'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: '/api/v2/workflows/$workflowId/ui_schema',
            ),
            data: malformedPayload,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflowUiSchema(workflowId),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.key,
              'key',
              'input_key',
            ),
          ),
        );
      },
    );
  });
}
