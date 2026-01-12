import 'dart:io';

import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/domain/models/execution_file.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// Manual Mock
class MockDio extends Mock implements Dio {}

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
      // Allow any request to post
      when(
        () =>
            mockDio.post<Map<String, dynamic>>(any(), data: any(named: 'data')),
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
        () => mockDio.post<Map<String, dynamic>>(
          '/executions',
          data: any(named: 'data'),
        ),
      ).called(1);
    });

    test('createExecution handles multiple files correctly', () async {
      // Create a real temp file so MultipartFile.fromFile doesn't crash
      final tempDir = Directory.systemTemp.createTempSync();
      final tempFile = File('${tempDir.path}/test.pdf');
      tempFile.writeAsBytesSync([1, 2, 3]);

      try {
        final fileInput = ExecutionInput(
          workflowId: 'wf-files',
          inputs: {'meta': 'data'},
          files: {
            'doc1': const ExecutionFile(
              name: 'a.pdf',
              bytes: [1, 2],
            ), // Web-like
            'doc2': ExecutionFile(
              name: 'b.pdf',
              path: tempFile.path,
            ), // IO-like
          },
        );

        when(
          () => mockDio.post<Map<String, dynamic>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response(
            data: {'execution_id': 'exec-files'},
            statusCode: 201,
            requestOptions: RequestOptions(path: '/executions'),
          ),
        );

        await repository.createExecution(fileInput).run();

        verify(
          () => mockDio.post<Map<String, dynamic>>(
            '/executions',
            data: any(named: 'data'),
          ),
        ).called(1);
      } finally {
        if (tempDir.existsSync()) {
          tempDir.deleteSync(recursive: true);
        }
      }
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
        () => mockDio.get<List<dynamic>>(
          '/executions/recent',
          queryParameters: any(named: 'queryParameters'),
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
      when(
        () => mockDio.get<Map<String, dynamic>>('/executions/999'),
      ).thenThrow(
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
