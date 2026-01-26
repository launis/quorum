import 'package:client_app/features/studio/data/schema_repository.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:client_app/features/studio/presentation/providers/studio_workflow_controller.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateNiceMocks([
  MockSpec<SchemaRepository>(),
  MockSpec<StudioRepository>(),
])
import 'studio_workflow_controller_test.mocks.dart';

void main() {
  late MockSchemaRepository mockSchemaRepository;
  late MockStudioRepository mockStudioRepository;
  late ProviderContainer container;

  setUp(() {
    mockSchemaRepository = MockSchemaRepository();
    mockStudioRepository = MockStudioRepository();
    
    container = ProviderContainer(
      overrides: [
        schemaRepositoryProvider.overrideWith((ref) => mockSchemaRepository),
        studioRepositoryProvider.overrideWith((ref) => mockStudioRepository),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  test('build fetches schema and data', () async {
    // Arrange
    const schema = JsonSchema(type: 'object');
    final data = {'name': 'Test Flow'};
    
    when(mockSchemaRepository.fetchSchema('workflow'))
        .thenAnswer((_) async => schema);
    when(mockStudioRepository.fetchWorkflow('123'))
        .thenAnswer((_) async => data);

    // Act
    final controller = container.read(studioWorkflowControllerProvider('123').future);
    final state = await controller;

    // Assert
    expect(state.schema, schema);
    expect(state.data, data);
    expect(state.isSaving, false);
  });

  test('save performs optimistic update and calls repository', () async {
    // Arrange
    const schema = JsonSchema(type: 'object');
    final initialData = {'name': 'Old'};
    final newData = {'name': 'New'};
    
    when(mockSchemaRepository.fetchSchema('workflow'))
        .thenAnswer((_) async => schema);
    when(mockStudioRepository.fetchWorkflow('123'))
        .thenAnswer((_) async => initialData);

    // Initialize state
    await container.read(studioWorkflowControllerProvider('123').future);
    final notifier = container.read(studioWorkflowControllerProvider('123').notifier);

    // Act
    await notifier.save(newData);

    // Assert
    verify(mockStudioRepository.updateWorkflow('123', newData)).called(1);
    
    final finalState = await container.read(studioWorkflowControllerProvider('123').future);
    expect(finalState.data, newData);
    expect(finalState.isSaving, false);
  });
}
