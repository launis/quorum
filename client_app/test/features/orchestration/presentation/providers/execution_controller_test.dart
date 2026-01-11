import 'dart:typed_data';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/data/repositories/execution_repository.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:file_picker/file_picker.dart';

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
        final requiredInputs = ['history_text', 'product_text'];

        try {
          await controller.startAnalysis(
            workflowId: 'audit_workflow',
            inputs: inputs,
            requiredInputs: requiredInputs,
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
            requiredInputs: [],
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
          requiredInputs: [],
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
          requiredInputs: [],
        ),
        throwsA(isA<AppError>()),
      );
    });

    test(
      'startAnalysis optimizes file handling for IO (path present -> bytes null)',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        // Simulate IO file with both path and bytes (bytes shouldn't be used)
        final ioFile = PlatformFile(
          name: 'doc.pdf',
          size: 100,
          path: '/tmp/doc.pdf',
          bytes: Uint8List.fromList([1, 2, 3]),
        );
        final inputs = {'my_file': ioFile};

        when(
          mockRepository.createExecution(any),
        ).thenAnswer((_) => TaskEither<AppError, String>.right('exec-io'));

        await controller.startAnalysis(
          workflowId: 'io_workflow',
          inputs: inputs,
          requiredInputs: [],
        );

        final captured =
            verify(mockRepository.createExecution(captureAny)).captured;
        final input = captured.first as ExecutionInput;

        expect(input.files.containsKey('my_file'), isTrue);
        final file = input.files['my_file']!;
        expect(file.path, '/tmp/doc.pdf');
        expect(
          file.bytes,
          isNull,
          reason:
              'Bytes should be cleared to prevent OOM when path is available',
        );
      },
    );

    test('startAnalysis maintains bytes for Web (path null)', () async {
      final controller = container.read(executionControllerProvider.notifier);
      // Simulate Web file (no path, only bytes)
      final webFile = PlatformFile(
        name: 'doc_web.pdf',
        size: 100,
        path: null,
        bytes: Uint8List.fromList([4, 5, 6]),
      );
      final inputs = {'my_web_file': webFile};

      when(
        mockRepository.createExecution(any),
      ).thenAnswer((_) => TaskEither<AppError, String>.right('exec-web'));

      await controller.startAnalysis(
        workflowId: 'web_workflow',
        inputs: inputs,
        requiredInputs: [],
      );

      final captured =
          verify(mockRepository.createExecution(captureAny)).captured;
      final input = captured.first as ExecutionInput;

      expect(input.files.containsKey('my_web_file'), isTrue);
      final file = input.files['my_web_file']!;
      expect(file.path, isNull);
      expect(file.bytes, [4, 5, 6]);
    });

    test('startAnalysis processes varying numbers of files (1 file)', () async {
      final controller = container.read(executionControllerProvider.notifier);
      final file1 = PlatformFile(
        name: 'f1.pdf',
        size: 10,
        path: '/tmp/f1.pdf',
        bytes: null,
      );
      final inputs = {'file_1': file1};

      when(
        mockRepository.createExecution(any),
      ).thenAnswer((_) => TaskEither<AppError, String>.right('exec-1'));

      await controller.startAnalysis(
        workflowId: 'wf_1',
        inputs: inputs,
        requiredInputs: [],
      );

      final captured =
          verify(mockRepository.createExecution(captureAny)).captured;
      final input = captured.first as ExecutionInput;

      expect(input.files.length, 1);
      expect(input.files.keys, contains('file_1'));
    });

    test(
      'startAnalysis processes varying numbers of files (3 files)',
      () async {
        final controller = container.read(executionControllerProvider.notifier);
        final file1 = PlatformFile(
          name: 'f1.pdf',
          size: 10,
          path: '/tmp/f1.pdf',
          bytes: null,
        );
        final file2 = PlatformFile(
          name: 'f2.pdf',
          size: 10,
          path: '/tmp/f2.pdf',
          bytes: null,
        );
        final file3 = PlatformFile(
          name: 'f3.pdf',
          size: 10,
          path: '/tmp/f3.pdf',
          bytes: null,
        );

        final inputs = {
          'history': file1,
          'product': file2,
          'reflection': file3,
        };

        when(
          mockRepository.createExecution(any),
        ).thenAnswer((_) => TaskEither<AppError, String>.right('exec-3'));

        await controller.startAnalysis(
          workflowId: 'wf_3',
          inputs: inputs,
          requiredInputs: [],
        );

        final captured =
            verify(mockRepository.createExecution(captureAny)).captured;
        final input = captured.first as ExecutionInput;

        expect(input.files.length, 3);
        expect(
          input.files.keys,
          containsAll(['history', 'product', 'reflection']),
        );
      },
    );
  });
}
