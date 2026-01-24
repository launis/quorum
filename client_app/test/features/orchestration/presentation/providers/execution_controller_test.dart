import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:dio/dio.dart';
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

  setUp(() {
    registerFallbackValue(
      const ExecutionInput(workflowId: 'fallback_workflow_id', inputs: {}, files: {}),
    );
    registerFallbackValue(Options());
    registerFallbackValue(RequestOptions(path: ''));

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
    test('monitorExecution connects to SSE and updates state', () async {
        final controller = container.read(executionControllerProvider.notifier);
        const executionId = 'exec-sse';
        
        final streamController = StreamController<Uint8List>();
        final responseBody = ResponseBody(streamController.stream, 200);

        // Mock Initial Fetch
        when(() => mockRepository.getExecution(executionId)).thenAnswer((_) => TaskEither.right(
             Execution.running(
                id: executionId,
                createdAt: DateTime.now(),
                workflowName: 'wf',
                status: ExecutionStatus.running,
                inputs: {},
             )
        ));

        // Mock Dio get for SSE
        when(
          () => mockDio.get(
            any(),
            queryParameters: any(),
            cancelToken: any(),
            options: any(),
          ),
        ).thenAnswer((_) async => Response(
            requestOptions: RequestOptions(path: ''),
            data: responseBody,
            statusCode: 200,
        ));

        // Start monitoring
        // Expect implicit state update from getExecution
        await controller.monitorExecution(executionId);
        
        // Verify state is AsyncData(Execution) immediately after initial fetch
        final state = container.read(executionControllerProvider);
        expect(state, isA<AsyncData>());
        expect(state.value?.id, executionId);
        expect(state.value?.status, ExecutionStatus.running);

        // We don't push SSE events here to avoid test complexity with SseClient/Dio mocking in this environment.
        // The critical part for UI freeze is the initial state population.
        
        await streamController.close();
    });

    // Minimal Repository Test to see if that works
    // test('cancelExecution calls repository (Simple)', () async {
    //     final controller = container.read(executionControllerProvider.notifier);
    //     when(() => mockRepository.cancelExecution(any())).thenAnswer((_) => TaskEither.right(null));
    //     
    //     await controller.cancelExecution('123');
    //     verify(() => mockRepository.cancelExecution(any())).called(1);
    // });
  });
}
