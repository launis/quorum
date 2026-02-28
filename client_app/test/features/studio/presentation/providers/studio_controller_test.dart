import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
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
      overrides: [studioRepositoryProvider.overrideWithValue(mockRepository)],
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

  const List<StudioComponentDef> testComponents = [
    StudioComponentDef(id: 'c1', name: 'Comp 1', type: 'prompt', content: {}),
  ];

  test('loadWorkflow loads data into activeWorkflow', () async {
    // Arrange
    when(
      () => mockRepository.getWorkflow('1'),
    ).thenAnswer((_) async => testWorkflow);

    // Act
    await container.read(studioControllerProvider.notifier).loadWorkflow('1');

    // Assert
    final state = container.read(studioControllerProvider);
    expect(state.activeWorkflow.value, testWorkflow);
  });

  test('loadComponents loads data into components', () async {
    // Arrange
    when(
      () => mockRepository.getComponents(),
    ).thenAnswer((_) async => testComponents);
    when(
      () => mockRepository.getAgents(),
    ).thenAnswer((_) async => <StudioComponentDef>[]);
    when(
      () => mockRepository.getOutputConfigs(),
    ).thenAnswer((_) async => <StudioComponentDef>[]);

    // Act
    await container.read(studioControllerProvider.notifier).loadComponents();

    // Assert
    final state = container.read(studioControllerProvider);
    expect(state.components.value, testComponents);
  });

  test('updateStep updates activeWorkflow optimistically', () async {
    // Arrange
    when(
      () => mockRepository.getWorkflow('1'),
    ).thenAnswer((_) async => testWorkflow);
    when(() => mockRepository.saveWorkflow(any())).thenAnswer((_) async => {});

    // Initialize state
    await container.read(studioControllerProvider.notifier).loadWorkflow('1');

    // Act
    final newConfig = {'key': 'newValue'};
    await container
        .read(studioControllerProvider.notifier)
        .updateStep('step1', newConfig);

    // Assert
    final state = container.read(studioControllerProvider);
    expect(state.activeWorkflow.value!.steps.first.config['key'], 'newValue');
    verify(() => mockRepository.saveWorkflow(any())).called(1);
  });

  test('updateStep rolls back on failure', () async {
    // Arrange
    when(
      () => mockRepository.getWorkflow('1'),
    ).thenAnswer((_) async => testWorkflow);
    when(
      () => mockRepository.saveWorkflow(any()),
    ).thenThrow(Exception('Save failed'));

    // Initialize state
    await container.read(studioControllerProvider.notifier).loadWorkflow('1');

    // Act
    final newConfig = {'key': 'newValue'};
    await container
        .read(studioControllerProvider.notifier)
        .updateStep('step1', newConfig);

    // Assert
    final state = container.read(studioControllerProvider);
    // Should be rolled back to original
    expect(state.activeWorkflow.value!.steps.first.config['key'], 'value');

    // Error is swallowed to keep UI usable, but state is reverted.
    expect(state.activeWorkflow.hasError, false);
  });

  test('copyWorkflow calls repo and reloads list', () async {
    // Arrange
    when(
      () => mockRepository.copyWorkflow('1', 'New Name'),
    ).thenAnswer((_) async => {});
    when(() => mockRepository.getWorkflows()).thenAnswer(
      (_) async => [testWorkflow],
    ); // Return list with copy? For test just return something.

    // Act
    await container
        .read(studioControllerProvider.notifier)
        .copyWorkflow('1', 'New Name');

    // Assert
    verify(() => mockRepository.copyWorkflow('1', 'New Name')).called(1);
    verify(() => mockRepository.getWorkflows()).called(1);
    final state = container.read(studioControllerProvider);
    expect(state.workflows.value, [testWorkflow]);
  });
}
