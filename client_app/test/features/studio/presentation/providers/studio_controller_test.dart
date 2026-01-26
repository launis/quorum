import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioRepository extends Mock implements StudioRepository {}

void main() {
  late MockStudioRepository mockRepository;
  late ProviderContainer container;

  setUp(() {
    mockRepository = MockStudioRepository();
    container = ProviderContainer(
      overrides: [
        studioRepositoryProvider.overrideWithValue(mockRepository),
      ],
    );

    // Register fallback values if needed
    registerFallbackValue(
      const WorkflowDef(
        id: 'fallback',
        name: 'fallback',
        description: 'fallback',
      ),
    );
  });

  tearDown(() {
    container.dispose();
  });

  const testWorkflow = WorkflowDef(
    id: '1',
    name: 'Test Workflow',
    description: 'Test Description',
    steps: [
      WorkflowStepDef(
        id: 'step1',
        name: 'Step 1',
        taskKey: 'task1',
        config: {'key': 'value'},
      ),
    ],
  );

  test('loadWorkflow loads data into state', () async {
    // Arrange
    when(() => mockRepository.getWorkflow('1'))
        .thenAnswer((_) async => testWorkflow);

    // Act
    await container
        .read(studioControllerProvider.notifier)
        .loadWorkflow('1');

    // Assert
    final state = container.read(studioControllerProvider);
    expect(state.value, testWorkflow);
  });

  test('updateStep updates state optimistically', () async {
    // Arrange
    when(() => mockRepository.getWorkflow('1'))
        .thenAnswer((_) async => testWorkflow);
    when(() => mockRepository.saveWorkflow(any()))
        .thenAnswer((_) async => {});

    // Initialize state
    await container
        .read(studioControllerProvider.notifier)
        .loadWorkflow('1');

    // Act
    final newConfig = {'key': 'newValue'};
    await container
        .read(studioControllerProvider.notifier)
        .updateStep('step1', newConfig);

    // Assert
    final state = container.read(studioControllerProvider);
    expect(state.value!.steps.first.config['key'], 'newValue');
    verify(() => mockRepository.saveWorkflow(any())).called(1);
  });

  test('updateStep rolls back on failure', () async {
    // Arrange
    when(() => mockRepository.getWorkflow('1'))
        .thenAnswer((_) async => testWorkflow);
    when(() => mockRepository.saveWorkflow(any()))
        .thenThrow(Exception('Save failed'));

    // Initialize state
    await container
        .read(studioControllerProvider.notifier)
        .loadWorkflow('1');

    // Act
    final newConfig = {'key': 'newValue'};
    await container
        .read(studioControllerProvider.notifier)
        .updateStep('step1', newConfig);

    // Assert
    final state = container.read(studioControllerProvider);
    // Should be rolled back to original
    expect(state.value!.steps.first.config['key'], 'value');
    // State should have error (though AsyncNotifier handling might be complex)
    expect(state.hasError, true);
  });
}
