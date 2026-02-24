import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/screens/workflow_studio_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockStudioRepository extends Mock implements StudioRepository {}

void main() {
  late MockStudioRepository mockRepository;

  setUp(() {
    mockRepository = MockStudioRepository();
    registerFallbackValue(
      const WorkflowDef(id: 'fb', name: 'fb', description: 'fb'),
    );
  });

  const testWorkflow = WorkflowDef(
    id: '1',
    name: 'Test Workflow',
    description: 'Desc',
    steps: [
      WorkflowStepDef(
        id: 's1',
        name: 'Step 1',
        taskKey: 't1',
        config: {'param': 'value'},
      ),
    ],
  );

  testWidgets('WorkflowStudioScreen full flow', (tester) async {
    // 1. Arrange
    when(() => mockRepository.getWorkflow('1'))
        .thenAnswer((_) async => testWorkflow);
        
    when(() => mockRepository.saveWorkflow(any()))
        .thenAnswer((_) async => {}); // Successful save

    when(() => mockRepository.getComponents())
        .thenAnswer((_) async => <StudioComponentDef>[]);

    when(() => mockRepository.getAgents())
        .thenAnswer((_) async => <StudioComponentDef>[]);
        
    when(() => mockRepository.getOutputConfigs())
        .thenAnswer((_) async => <StudioComponentDef>[]);

    // 2. Pump Screen
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          studioRepositoryProvider.overrideWithValue(mockRepository),
        ],
        child: const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: WorkflowStudioScreen(workflowId: '1'),
        ),
      ),
    );

    // 3. Wait for load (useEffect -> Future.microtask -> loadWorkflow)
    await tester.pumpAndSettle();

    // 4. Verify loaded
    expect(find.text('Step 1'), findsOneWidget);
    // Verify Editor Empty initially
    expect(find.text('Sequencer'), findsOneWidget);

    // 5. Select Step
    await tester.tap(find.text('Step 1'));
    await tester.pumpAndSettle();

    // 6. Verify Editor shows Config
    expect(find.text('Configuration: Step 1'), findsOneWidget);
    expect(find.text('Param'), findsOneWidget); // Capitalized label
    expect(find.text('value'), findsOneWidget);

    // 7. Edit Config (Enter new value)
    await tester.enterText(find.widgetWithText(TextField, 'Param'), 'newVal');
    await tester.testTextInput.receiveAction(TextInputAction.done); // Trigger submit
    await tester.pumpAndSettle();

    // 8. Verify Save called (Auto-save on field change)
    verify(() => mockRepository.saveWorkflow(any())).called(greaterThan(0));

    // 9. Manual Save
    await tester.tap(find.byIcon(Icons.save));
    await tester.pump(); // Start save
    // Should show "Saving..." if slow, but mock is instant.
    // Check for success snackbar
    await tester.pumpAndSettle();
    expect(find.text('Changes saved'), findsOneWidget);
  });
}
