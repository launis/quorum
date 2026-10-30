import 'package:client_app/core/api/workflow_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late WorkflowClient client;
  late MockDio mockDio;
  late MockLoggerService mockLogger;

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    client = WorkflowClient(mockDio, mockLogger);
  });

  group('WorkflowClient Unit Tests', () {
    const validWorkflowId = 'wf_0195f3a0000070008000000000000001';

    test(
      'getWorkflowUiSchema returns strongly typed WorkflowUiSchema on valid 200',
      () async {
        final mockPayload = <String, Object?>{
          'expected_inputs': <Map<String, Object?>>[
            <String, Object?>{
              'input_key': 'deliverable_text',
              'label': <String, Object?>{
                'translations': <String, String>{
                  'en': 'Deliverable Document',
                  'fi': 'Asiakirja',
                },
              },
              'required': true,
              'is_chat_history': false,
              'is_endorsed_deliverable': true,
              'input_modes': <String>['text', 'file'],
              'description': <String, Object?>{
                'translations': <String, String>{
                  'en': 'Executive coaching brief',
                  'fi': 'Johtamisen valmennustehtävä',
                },
              },
              'scan_for_performative_patterns': false,
              'ai_description': 'Primary text deliverable to evaluate',
              'questionnaire_definition': <Map<String, Object?>>[],
            },
          ],
        };

        when(
          () => mockDio.get('studio/workflows/$validWorkflowId/ui_schema'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$validWorkflowId/ui_schema',
            ),
            data: mockPayload,
            statusCode: 200,
          ),
        );

        final result = await client.getWorkflowUiSchema(validWorkflowId);

        expect(result, isA<WorkflowUiSchema>());
        expect(result.expectedInputs.length, 1);
        final input = result.expectedInputs.first;
        expect(input.inputKey, 'deliverable_text');
        expect(input.isEndorsedDeliverable, isTrue);
        expect(input.required, isTrue);
        expect(input.label.get('en'), 'Deliverable Document');
        expect(input.description.get('fi'), 'Johtamisen valmennustehtävä');

        verify(
          () => mockDio.get('studio/workflows/$validWorkflowId/ui_schema'),
        ).called(1);
      },
    );

    test(
      'Negative Test 1: getWorkflowUiSchema fails fast with AppException on invalid Opaque Stripe ID',
      () async {
        for (final invalidId in const [
          '',
          'wf_short',
          'wf_0195f3a000007000800000000000000', // 31 hex chars (min-1)
          'wf_0195f3a00000700080000000000000012', // 33 hex chars (max+1)
          'invalid_prefix_0195f3a0000070008000000000000001',
        ]) {
          expect(
            () => client.getWorkflowUiSchema(invalidId),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                'VALIDATION_FAILED',
              ),
            ),
          );
        }

        verify(
          () => mockLogger.error('WorkflowClient', any(), any(), any()),
        ).called(5);
        verifyNever(() => mockDio.get(any()));
      },
    );

    test(
      'Negative Test 2: getWorkflowUiSchema fails fast with CheckedFromJsonException on unrecognized keys',
      () async {
        final corruptPayload = <String, Object?>{
          'expected_inputs': <Map<String, Object?>>[],
          'unrecognized_legacy_parameter': 'corrupt_data',
        };

        when(
          () => mockDio.get('studio/workflows/$validWorkflowId/ui_schema'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$validWorkflowId/ui_schema',
            ),
            data: corruptPayload,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflowUiSchema(validWorkflowId),
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
      'Negative Test 3: getWorkflowUiSchema rethrows DioException on network or HTTP 404 failure',
      () async {
        when(
          () => mockDio.get('studio/workflows/$validWorkflowId/ui_schema'),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$validWorkflowId/ui_schema',
            ),
            response: Response(
              requestOptions: RequestOptions(
                path: 'studio/workflows/$validWorkflowId/ui_schema',
              ),
              statusCode: 404,
              statusMessage: 'Workflow Not Found',
            ),
            type: DioExceptionType.badResponse,
          ),
        );

        expect(
          () => client.getWorkflowUiSchema(validWorkflowId),
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
      'Negative Test 4: getWorkflowUiSchema fails fast on malformed inner expected_inputs payload',
      () async {
        final malformedPayload = <String, Object?>{
          'expected_inputs': <Map<String, Object?>>[
            <String, Object?>{
              // missing required input_key, label, description
              'required': true,
            },
          ],
        };

        when(
          () => mockDio.get('studio/workflows/$validWorkflowId/ui_schema'),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$validWorkflowId/ui_schema',
            ),
            data: malformedPayload,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflowUiSchema(validWorkflowId),
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
