import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/studio_sidebar.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

// Create a Fake/Mock Controller?
// For widget tests, often easier to override the state directly or use a container.
// Here we'll override the provider to return a fixed AsyncValue.

void main() {
  const testSteps = [
    WorkflowStepDef(id: 's1', name: 'Step 1', taskKey: 't1'),
    WorkflowStepDef(id: 's2', name: 'Step 2', taskKey: 't2'),
  ];

  const testWorkflow = WorkflowDef(
    id: 'w1',
    name: 'W1',
    description: 'D1',
    steps: testSteps,
  );

  testWidgets('StudioSidebar renders steps', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          studioControllerProvider.overrideWith(() => FakeStudioController(testWorkflow)),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: StudioSidebar(
              selectedStepId: 's1',
              onStepSelected: (_) {},
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Step 1'), findsOneWidget);
    expect(find.text('Step 2'), findsOneWidget);
    // Add Button
    expect(find.byIcon(Icons.add), findsOneWidget);
  });

  testWidgets('StudioSidebar taps trigger callback', (tester) async {
    String? selectedId;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          studioControllerProvider.overrideWith(() => FakeStudioController(testWorkflow)),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: StudioSidebar(
              selectedStepId: null,
              onStepSelected: (id) => selectedId = id,
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    await tester.tap(find.text('Step 2'));
    expect(selectedId, 's2');
  });
}

// Simple Fake Controller for providing data
class FakeStudioController extends StudioController {
  final WorkflowDef? initialData;
  FakeStudioController(this.initialData);

  @override
  StudioState build() {
    return StudioState(
      workflows: AsyncValue.data(initialData != null ? [initialData!] : []),
      activeWorkflow: AsyncValue.data(initialData),
    );
  }
  
  // Stubs for other methods to satisfy interface if needed (runtime mixin usually handles it)
  // Since we only override 'build' for the state, we need to implement methods if called.
  // BUT: StudioSidebar calls addStep/reorderSteps on ref.read(notifier).
  // Implicitly this class IS the notifier.
  
  @override
  Future<void> addStep(WorkflowStepDef step) async {}
  
  @override
  Future<void> reorderSteps(int oldIndex, int newIndex) async {}
  
  @override
  Future<void> loadWorkflow(String id) async  {}
  
  @override
  Future<void> save() async {}

  @override
  Future<void> updateMetadata({String? name, String? description}) async {}
  
  @override
  Future<void> updateStep(String stepId, Map<String, dynamic> newConfig) async {}
  
  @override
  bool get isValid => true;

  @override
  Future<void> loadWorkflows() async {}

  @override
  Future<void> createWorkflow(WorkflowDef workflow) async {}

  @override
  Future<void> copyWorkflow(String originalId, String newName) async {}
}
