import 'dart:typed_data';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/api/api_client.dart'; // For dioProvider override
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mocktail/mocktail.dart';

class MockExecutionRepository extends Mock implements ExecutionRepository {}
class MockDio extends Mock implements Dio {}

void main() {
  late MockExecutionRepository mockRepository;
  late MockDio mockDio;
  late ProviderContainer container;

  setUpAll(() {
    registerFallbackValue(
      const ExecutionInput(workflowId: 'fallback_workflow_id'),
    );
    registerFallbackValue(Options());
    registerFallbackValue(RequestOptions(path: ''));
  });

  setUp(() {
    mockRepository = MockExecutionRepository();
    mockDio = MockDio();
    container = ProviderContainer(
      overrides: [
        executionRepositoryProvider.overrideWithValue(mockRepository),
        dioProvider.overrideWithValue(mockDio),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('ExecutionController', () {
    // START ANALYSIS TESTS (Preserved & Adjusted)
    test(
      'startAnalysis throws AppError.validation if inputs are empty',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        try {
          await controller.startAnalysis(
            workflowId: 'generic_workflow',
            inputs: {},
            requiredInputs: [],
          );
          fail('Should have thrown AppError');
        } catch (e) {
            // State should be error
            expect(container.read(executionControllerProvider), isA<AsyncError>());
            expect(e, isA<AppError>());
        }
      },
    );

    test(
      'startAnalysis calls repository and returns executionId on success',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        final inputs = {'generic_field': 'value'};
        const executionId = 'exec-123';

        // Mock createExecution
        when(
          () => mockRepository.createExecution(any()),
        ).thenAnswer((_) => TaskEither<AppError, String>.right(executionId));
        
        // Mock getExecution
        when(() => mockRepository.getExecution(any())).thenAnswer((_) => TaskEither.right(
          Execution.running(
            id: executionId,
            createdAt: DateTime.now(),
            workflowName: 'wf',
            status: ExecutionStatus.running,
            inputs: {},
            // files: {}, // ExecutionRunning doesn't have files/results in current definition?
            // Checking ExecutionRunning definition: id, createdAt, workflowName, organizationId, userId, inputs, currentStepName, status.
            // No files or results field in ExecutionRunning.
          ),
        ));

        // Mock Dio for SseClient (fire and forget, but must not crash)
        when(() => mockDio.get<ResponseBody>(
              any(),
              options: any(named: 'options'),
            )).thenAnswer((_) async => Response(
              requestOptions: RequestOptions(path: ''),
              data: ResponseBody(
                Stream.empty(), // Empty stream to finish immediately
                200,
              ),
            ));

        final result = await controller.startAnalysis(
          workflowId: 'generic_workflow',
          inputs: inputs,
          requiredInputs: [],
        );

        expect(result, executionId);
        verify(() => mockRepository.createExecution(any())).called(1);
      },
    );

    // CANCELLATION TEST
    test('cancelExecution calls repository', () async {
        final controller = container.read(executionControllerProvider.notifier);
        const executionId = 'exec-cancel';

        // Setup initial state (optional, but good practice)
        // controller.state = AsyncData(Execution(...)); 

        when(() => mockRepository.cancelExecution(executionId))
            .thenAnswer((_) => TaskEither.right(null));

        await controller.cancelExecution(executionId);

        verify(() => mockRepository.cancelExecution(executionId)).called(1);
    });

    test('cancelExecution handles error', () async {
        final controller = container.read(executionControllerProvider.notifier);
        const executionId = 'exec-cancel-fail';
        final error = const AppError.server('Fail', 500);

        when(() => mockRepository.cancelExecution(executionId))
            .thenAnswer((_) => TaskEither.left(error));

        await controller.cancelExecution(executionId);

        verify(() => mockRepository.cancelExecution(executionId)).called(1);
        expect(container.read(executionControllerProvider), isA<AsyncError>());
    });
  });
}
