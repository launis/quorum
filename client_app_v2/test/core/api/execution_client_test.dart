import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late ExecutionClient client;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    when(() => mockDio.options).thenReturn(BaseOptions(baseUrl: 'https://api.test/api/v2'));
    client = ExecutionClient(mockDio);
  });

  group('ExecutionClient', () {
    const testExecutionId = 'exe_1234567890abcdef';
    const testWorkflowId = 'wf_1234567890abcdef';

    final testRecordJson = {
      'id': testExecutionId,
      'workflow_id': testWorkflowId,
      'target_locale': 'fi',
      'status': 'PASSED',
    };

    test('startExecution posts request and returns ExecutionRecord', () async {
      final request = ExecutionCreateRequestDto(
        workflowId: testWorkflowId,
        targetLocale: 'fi',
        rawInputs: {},
      );

      when(
        () => mockDio.post(
          '/execution/executions/',
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/execution/executions/'),
          data: testRecordJson,
          statusCode: 200,
        ),
      );

      final result = await client.startExecution(request: request);
      expect(result.id, equals(testExecutionId));
      expect(result.workflowId, equals(testWorkflowId));
      expect(result.status, equals('PASSED'));
      verify(() => mockDio.post('/execution/executions/', data: any(named: 'data'))).called(1);
    });

    test('resumeExecution calls resume endpoint and returns ExecutionRecord', () async {
      when(
        () => mockDio.post(
          '/execution/executions/$testExecutionId/resume',
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/execution/executions/$testExecutionId/resume'),
          data: testRecordJson,
          statusCode: 200,
        ),
      );

      final result = await client.resumeExecution(testExecutionId);
      expect(result.id, equals(testExecutionId));
      verify(() => mockDio.post('/execution/executions/$testExecutionId/resume')).called(1);
    });

    test('getExecutionStatus fetches execution record by id', () async {
      when(
        () => mockDio.get('/execution/executions/$testExecutionId'),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/execution/executions/$testExecutionId'),
          data: testRecordJson,
          statusCode: 200,
        ),
      );

      final result = await client.getExecutionStatus(testExecutionId);
      expect(result.id, equals(testExecutionId));
      verify(() => mockDio.get('/execution/executions/$testExecutionId')).called(1);
    });

    test('renderExecution returns ReportDataDto when server completes synthesis', () async {
      final sduiJson = {
        'execution_id': testExecutionId,
        'workflow_id': testWorkflowId,
        'profile_id': 'prf_default',
      };

      when(
        () => mockDio.get(
          '/execution/executions/$testExecutionId/render',
          queryParameters: any(named: 'queryParameters'),
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/execution/executions/$testExecutionId/render'),
          data: sduiJson,
          statusCode: 200,
        ),
      );

      final result = await client.renderExecution(testExecutionId);
      expect(result.executionId, equals(testExecutionId));
      expect(result.profileId, equals('prf_default'));
    });

    test('overrideAtom patches override endpoint and returns GenericStatusResponseDto', () async {
      final overrideResponseJson = {
        'status': 'ok',
        'message': 'Atom overridden successfully.',
      };

      when(
        () => mockDio.patch(
          '/execution/executions/$testExecutionId/atoms/atm_123/override',
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/execution/executions/$testExecutionId/atoms/atm_123/override'),
          data: overrideResponseJson,
          statusCode: 200,
        ),
      );

      final result = await client.overrideAtom(
        executionId: testExecutionId,
        atomId: 'atm_123',
        payload: {'new_status': 'PASSED', 'reason': 'Manual verification'},
      );

      expect(result.status, equals('ok'));
      expect(result.message, equals('Atom overridden successfully.'));
      verify(
        () => mockDio.patch(
          '/execution/executions/$testExecutionId/atoms/atm_123/override',
          data: {'new_status': 'PASSED', 'reason': 'Manual verification'},
        ),
      ).called(1);
    });

    test('Negative Test 1: startExecution propagates DioException on network/server error', () async {
      when(
        () => mockDio.post(
          '/execution/executions/',
          data: any(named: 'data'),
        ),
      ).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/execution/executions/'),
          type: DioExceptionType.connectionTimeout,
        ),
      );

      final request = ExecutionCreateRequestDto(
        workflowId: testWorkflowId,
        targetLocale: 'fi',
        rawInputs: {},
      );

      expect(
        () => client.startExecution(request: request),
        throwsA(isA<DioException>()),
      );
    });

    test('Negative Test 2: overrideAtom throws when server returns malformed payload', () async {
      when(
        () => mockDio.patch(
          any(),
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/override'),
          data: {'unexpected_key': 'no message'},
          statusCode: 200,
        ),
      );

      expect(
        () => client.overrideAtom(
          executionId: testExecutionId,
          atomId: 'atm_123',
          payload: {},
        ),
        throwsA(anything),
      );
    });
  });
}
