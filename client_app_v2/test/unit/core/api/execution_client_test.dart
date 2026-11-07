import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late ExecutionClient client;
  late MockDio mockDio;
  late MockLoggerService mockLogger;

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    when(
      () => mockDio.options,
    ).thenReturn(BaseOptions(baseUrl: 'https://api.test/api/v2'));
    client = ExecutionClient(mockDio, mockLogger);
  });

  group('ExecutionClient Unit & ISTQB Boundary Tests', () {
    const testExecutionId = 'exe_0195f3a0000070008000000000000001';
    const testWorkflowId = 'wf_0195f3a0000070008000000000000002';
    const testProfileId = 'op_0195f3a0000070008000000000000003';
    const testAtomId = 'atm_0195f3a0000070008000000000000004';

    final testRecordJson = <String, Object?>{
      'id': testExecutionId,
      'workflow_id': testWorkflowId,
      'target_locale': 'fi',
      'status': 'PASSED',
    };

    test(
      'Positive 1: startExecution posts typed request and returns ExecutionRecord',
      () async {
        const request = ExecutionCreateRequestDto(
          workflowId: testWorkflowId,
          targetLocale: 'fi',
          rawInputs: WorkflowInputs(
            dynamicInputs: {
              'deliverable_text': WorkflowInputValue(
                textValue: 'Coaching brief',
              ),
            },
          ),
          profileId: testProfileId,
        );

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/execution/executions/',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/execution/executions/'),
            data: testRecordJson,
            statusCode: 202,
          ),
        );

        final result = await client.startExecution(request: request);
        expect(result.id, equals(testExecutionId));
        expect(result.workflowId, equals(testWorkflowId));
        expect(result.status, equals('PASSED'));
        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/execution/executions/',
            data: request.toJson(),
          ),
        ).called(1);
      },
    );

    test(
      'Positive 2: resumeExecution calls resume endpoint and returns ExecutionRecord',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/execution/executions/$testExecutionId/resume',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/execution/executions/$testExecutionId/resume',
            ),
            data: testRecordJson,
            statusCode: 202,
          ),
        );

        final result = await client.resumeExecution(testExecutionId);
        expect(result.id, equals(testExecutionId));
        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/execution/executions/$testExecutionId/resume',
          ),
        ).called(1);
      },
    );

    test(
      'Positive 3: getExecutionStatus fetches execution record by 32-hex UUIDv7 id',
      () async {
        when(
          () => mockDio.get<Map<String, Object?>>(
            '/execution/executions/$testExecutionId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/execution/executions/$testExecutionId',
            ),
            data: testRecordJson,
            statusCode: 200,
          ),
        );

        final result = await client.getExecutionStatus(testExecutionId);
        expect(result.id, equals(testExecutionId));
        verify(
          () => mockDio.get<Map<String, Object?>>(
            '/execution/executions/$testExecutionId',
          ),
        ).called(1);
      },
    );

    test(
      'Positive 4: overrideAtom patches override endpoint and returns GenericStatusResponseDto',
      () async {
        final overrideResponseJson = <String, Object?>{
          'status': 'ok',
          'message': 'Atom overridden successfully.',
        };

        when(
          () => mockDio.patch<Map<String, Object?>>(
            '/execution/executions/$testExecutionId/atoms/$testAtomId/override',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path:
                  '/execution/executions/$testExecutionId/atoms/$testAtomId/override',
            ),
            data: overrideResponseJson,
            statusCode: 200,
          ),
        );

        const payload = HumanOverrideRequestDto(
          newStatus: ExecutionStatus.passed,
          reason: 'Manual verification',
        );

        final result = await client.overrideAtom(
          executionId: testExecutionId,
          atomId: testAtomId,
          payload: payload,
        );

        expect(result.status, equals('ok'));
        expect(result.message, equals('Atom overridden successfully.'));
        verify(
          () => mockDio.patch<Map<String, Object?>>(
            '/execution/executions/$testExecutionId/atoms/$testAtomId/override',
            data: payload.toJson(),
          ),
        ).called(1);
      },
    );

    test(
      'Negative Test 1 (BVA): fails fast with AppException before HTTP call on invalid 32-hex Opaque Stripe IDs (empty, 16-hex, 31-hex min-1, 33-hex max+1)',
      () async {
        const invalidIds = <String>[
          '',
          'exe_1234567890abcdef', // legacy 16-hex
          'exe_0195f3a000007000800000000000000', // 31 hex chars (min-1)
          'exe_0195f3a00000700080000000000000012', // 33 hex chars (max+1)
          'x_0195f3a0000070008000000000000001', // 1-char prefix (min-1)
        ];

        for (final invalidId in invalidIds) {
          expect(
            () => client.getExecutionStatus(invalidId),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          expect(
            () => client.resumeExecution(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.startExecution(
              request: ExecutionCreateRequestDto(
                workflowId: invalidId,
                targetLocale: 'fi',
              ),
            ),
            throwsA(isA<AppException>()),
          );
        }

        // Also test invalid profileId and empty atomId
        expect(
          () => client.startExecution(
            request: const ExecutionCreateRequestDto(
              workflowId: testWorkflowId,
              targetLocale: 'fi',
              profileId: 'op_invalid_16hex',
            ),
          ),
          throwsA(isA<AppException>()),
        );

        expect(
          () => client.overrideAtom(
            executionId: testExecutionId,
            atomId: '   ',
            payload: const HumanOverrideRequestDto(
              newStatus: ExecutionStatus.passed,
              reason: 'Valid reason',
            ),
          ),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );

        verify(
          () => mockLogger.error('ExecutionClient', any(), any(), any()),
        ).called(17);
        verifyNever(() => mockDio.get<Map<String, Object?>>(any()));
        verifyNever(
          () => mockDio.post<Map<String, Object?>>(
            any(),
            data: any(named: 'data'),
          ),
        );
        verifyNever(
          () => mockDio.patch<Map<String, Object?>>(
            any(),
            data: any(named: 'data'),
          ),
        );
      },
    );

    test(
      'Negative Test 2: startExecution propagates DioException on network/server error',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/execution/executions/',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/execution/executions/'),
            type: DioExceptionType.connectionTimeout,
          ),
        );

        const request = ExecutionCreateRequestDto(
          workflowId: testWorkflowId,
          targetLocale: 'fi',
          rawInputs: WorkflowInputs(),
        );

        expect(
          () => client.startExecution(request: request),
          throwsA(isA<DioException>()),
        );
      },
    );

    test(
      'Negative Test 3: fails fast with CheckedFromJsonException or AppException when server returns unrecognized keys or null payload',
      () async {
        when(
          () => mockDio.patch<Map<String, Object?>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/override'),
            data: <String, Object?>{'unexpected_key': 'no message'},
            statusCode: 200,
          ),
        );

        expect(
          () => client.overrideAtom(
            executionId: testExecutionId,
            atomId: testAtomId,
            payload: const HumanOverrideRequestDto(
              newStatus: ExecutionStatus.failed,
              reason: 'Malformed test',
            ),
          ),
          throwsA(isA<CheckedFromJsonException>()),
        );

        when(
          () => mockDio.get<Map<String, Object?>>(
            '/execution/executions/$testExecutionId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/execution/executions/$testExecutionId',
            ),
            data: null,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getExecutionStatus(testExecutionId),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );
  });
}
