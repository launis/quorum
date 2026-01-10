import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import '../../../helpers/test_helper.mocks.dart';

void main() {
  late MockDio mockDio;
  late ExecutionRepository repository;

  setUp(() {
    mockDio = MockDio();
    repository = ExecutionRepository(mockDio);
  });

  group('ExecutionRepository', () {
    const executedId = 'exec-1';
    final input = ExecutionInput(workflowId: 'wf-1', inputs: {'a': 1});

    test('createExecution calls correct endpoint with FormData', () async {
      when(
        mockDio.post<Map<String, dynamic>>(any, data: anyNamed('data')),
      ).thenAnswer(
        (_) async => Response(
          data: {'execution_id': executedId},
          statusCode: 201,
          requestOptions: RequestOptions(path: '/executions'),
        ),
      );

      final result = await repository.createExecution(input).run();

      expect(result.isRight(), true);
      expect(result.fold((l) => null, (r) => r), executedId);

      verify(
        mockDio.post<Map<String, dynamic>>(
          '/executions',
          data: anyNamed(
            'data',
          ), // Can't easily inspect FormData content in mockito basics
        ),
      ).called(1);
    });

    test('fetchExecutions returns list of Executions', () async {
      final jsonList = [
        {
          'execution_id': '1',
          'start_time': DateTime.now().toIso8601String(),
          'status': 'completed',
          'workflow_name': 'Test',
        },
        {
          'execution_id': '2',
          'start_time': DateTime.now().toIso8601String(),
          'status': 'running',
          'workflow_name': 'Test',
        },
      ];

      when(
        mockDio.get<List<dynamic>>(
          '/executions/recent',
          queryParameters: anyNamed('queryParameters'),
        ),
      ).thenAnswer(
        (_) async => Response(
          data: jsonList,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/executions/recent'),
        ),
      );

      final result = await repository.fetchExecutions().run();

      expect(result.isRight(), true);
      final list = result.getOrElse((l) => []);
      expect(list.length, 2);
      expect(list[0].id, '1');
      expect(list[1].status, ExecutionStatus.running);
    });

    test('getExecution handles error correctly', () async {
      when(mockDio.get<Map<String, dynamic>>('/executions/999')).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 404,
            data: {'detail': 'Not Found'},
          ),
          type: DioExceptionType.badResponse,
        ),
      );

      final result = await repository.getExecution('999').run();

      expect(result.isLeft(), true);
      result.fold((l) {
        expect(l, isA<AppError>());
        l.maybeWhen(
          notFound: (msg) => expect(msg, 'Not Found'),
          orElse: () => fail('Wrong error type'),
        );
      }, (r) => fail('Should have failed'));
    });
  });
}
