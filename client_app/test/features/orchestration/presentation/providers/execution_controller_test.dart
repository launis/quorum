import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateNiceMocks([MockSpec<ExecutionRepository>()])
import 'execution_controller_test.mocks.dart';

void main() {
  late MockExecutionRepository mockRepository;
  late ProviderContainer container;

  setUpAll(() {
    provideDummy<TaskEither<AppError, String>>(
      TaskEither.left(const AppError.unknown()),
    );
  });

  setUp(() {
    mockRepository = MockExecutionRepository();
    container = ProviderContainer(
      overrides: [
        executionRepositoryProvider.overrideWithValue(mockRepository),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('ExecutionController', () {
    test(
      'startAnalysis throws AppError.validationMissing if inputs are invalid for Audit',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        // Missing required audit fields
        final inputs = {'some_other_field': 'value'};

        try {
          await controller.startAnalysis(
            workflowId: 'audit_workflow',
            inputs: inputs,
          );
          fail('Should have thrown AppError');
        } catch (e) {
          expect(e, isA<AppError>());
          final error = e as AppError;
          error.maybeMap(
            validationMissing: (value) {
              expect(value.fields, contains('history_text'));
              expect(value.fields, contains('product_text'));
            },
            orElse: () => fail('Wrong error type: $error'),
          );
        }
      },
    );

    test(
      'startAnalysis throws AppError.validation if inputs are empty',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        try {
          await controller.startAnalysis(
            workflowId: 'generic_workflow',
            inputs: {},
          );
          fail('Should have thrown AppError');
        } catch (e) {
          expect(e, isA<AppError>());
          final error = e as AppError;
          error.maybeMap(
            validation:
                (value) =>
                    expect(value.reason, ValidationErrorReason.emptyInput),
            orElse: () => fail('Wrong error type: $error'),
          );
        }
      },
    );

    test(
      'startAnalysis calls repository and returns executionId on success',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        final inputs = {'generic_field': 'value'};
        const executionId = 'exec-123';

        when(
          mockRepository.createExecution(any),
        ).thenAnswer((_) => TaskEither<AppError, String>.right(executionId));

        final result = await controller.startAnalysis(
          workflowId: 'generic_workflow',
          inputs: inputs,
        );

        expect(result, executionId);
        verify(mockRepository.createExecution(any)).called(1);
      },
    );

    test('startAnalysis throws AppError if repository fails', () async {
      final controller = container.read(executionControllerProvider.notifier);
      final inputs = {'generic_field': 'value'};
      final error = AppError.server('API Error');

      when(
        mockRepository.createExecution(any),
      ).thenAnswer((_) => TaskEither<AppError, String>.left(error));

      await expectLater(
        controller.startAnalysis(
          workflowId: 'generic_workflow',
          inputs: inputs,
        ),
        throwsA(isA<AppError>()),
      );
    });
  });
}
