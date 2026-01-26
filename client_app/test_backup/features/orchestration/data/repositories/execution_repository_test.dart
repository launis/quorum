import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late ExecutionRepository repository;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    repository = ExecutionRepository(mockDio);
  });

  group('ExecutionRepository Error Handling', () {
    test(
      'Should map 422 with VALUE_ERROR to ValidationErrorReason.emptyInput',
      () async {
        // Arrange
        final input = ExecutionInput(workflowId: 'test-wf', inputs: {});
        when(
          () => mockDio.post<Map<String, dynamic>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/executions'),
            response: Response(
              requestOptions: RequestOptions(path: '/executions'),
              statusCode: 422,
              data: {'error_code': 'VALUE_ERROR', 'message': 'Input is empty'},
            ),
          ),
        );

        // Act
        final result = await repository.createExecution(input).run();

        // Assert
        result.fold((error) {
          expect(error, isA<AppError>());
          error.maybeWhen(
            validation:
                (reason) => expect(reason, ValidationErrorReason.emptyInput),
            orElse: () => fail('Expected validation error'),
          );
        }, (r) => fail('Expected error'));
      },
    );

    test(
      'Should map 422 with VALIDATION_ERROR to ValidationErrorReason.emptyInput (Standard Backend Code)',
      () async {
        // Arrange
        final input = ExecutionInput(workflowId: 'test-wf', inputs: {});
        when(
          () => mockDio.post<Map<String, dynamic>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/executions'),
            response: Response(
              requestOptions: RequestOptions(path: '/executions'),
              statusCode: 422,
              data: {
                'error_code': 'VALIDATION_ERROR',
                'message': 'Input is invalid',
              },
            ),
          ),
        );

        // Act
        final result = await repository.createExecution(input).run();

        // Assert
        result.fold((error) {
          error.maybeWhen(
            validation:
                (reason) => expect(reason, ValidationErrorReason.emptyInput),
            orElse: () => fail('Expected validation error'),
          );
        }, (r) => fail('Expected error'));
      },
    );

    test(
      'Should map 400 with generic code to ValidationErrorReason.unknown',
      () async {
        // Arrange
        final input = ExecutionInput(workflowId: 'test-wf', inputs: {});
        when(
          () => mockDio.post<Map<String, dynamic>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/executions'),
            response: Response(
              requestOptions: RequestOptions(path: '/executions'),
              statusCode: 400,
              data: {
                'error_code': 'SOME_WEIRD_ERROR', // Unknown code
                'detail': 'Something went wrong',
              },
            ),
          ),
        );

        // Act
        final result = await repository.createExecution(input).run();

        // Assert
        result.fold((error) {
          error.maybeWhen(
            validation:
                (reason) => expect(reason, ValidationErrorReason.unknown),
            orElse: () => fail('Expected validation error'),
          );
        }, (r) => fail('Expected error'));
      },
    );

    test(
      'Should map 422 with INVALID_EMAIL to ValidationErrorReason.invalidEmail',
      () async {
        // Arrange
        final input = ExecutionInput(workflowId: 'test-wf', inputs: {});
        when(
          () => mockDio.post<Map<String, dynamic>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/executions'),
            response: Response(
              requestOptions: RequestOptions(path: '/executions'),
              statusCode: 422,
              data: {'error_code': 'INVALID_EMAIL'},
            ),
          ),
        );

        // Act
        final result = await repository.createExecution(input).run();

        // Assert
        result.fold((error) {
          error.maybeWhen(
            validation:
                (reason) => expect(reason, ValidationErrorReason.invalidEmail),
            orElse: () => fail('Expected validation error'),
          );
        }, (r) => fail('Expected error'));
      },
    );

    test('Should map 500 to AppError.server', () async {
      // Arrange
      final input = ExecutionInput(workflowId: 'test-wf', inputs: {});
      when(
        () =>
            mockDio.post<Map<String, dynamic>>(any(), data: any(named: 'data')),
      ).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/executions'),
          response: Response(
            requestOptions: RequestOptions(path: '/executions'),
            statusCode: 500,
            data: {'detail': 'Internal Server Error'},
          ),
        ),
      );

      // Act
      final result = await repository.createExecution(input).run();

      // Assert
      result.fold((error) {
        error.maybeWhen(
          server: (msg, code) {
            expect(code, 500);
            expect(msg, 'Internal Server Error');
          },
          orElse: () => fail('Expected server error'),
        );
      }, (r) => fail('Expected error'));
    });
  });
}
