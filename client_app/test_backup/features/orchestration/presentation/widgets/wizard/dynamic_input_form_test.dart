import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/dynamic_input_form.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// Fake Notifier to inject state
class FakeWizardState extends WizardState {
  final WizardStateModel testState;
  FakeWizardState(this.testState);

  @override
  WizardStateModel build() => testState;
}

void main() {
  Widget createWidgetUnderTest({
    required Workflow workflow,
    required WizardStateModel mockState,
  }) {
    return ProviderScope(
      overrides: [
        workflowListProvider.overrideWith((ref) => Future.value([workflow])),
        wizardStateProvider.overrideWith(() => FakeWizardState(mockState)),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
        ],
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: const DynamicInputForm(), // Correct: No args
        ),
      ),
    );
  }

  group('DynamicInputForm', () {
    testWidgets('renders file inputs based on uiSchema', (tester) async {
      const workflow = Workflow(
        id: 'test_wf',
        name: 'Test Workflow',
        description: 'Testing Dynamic UI',
        uiSchema: {
          'file_1': {
            'type': 'file',
            'label': 'First Evidence',
            'icon': 'history',
          },
          'file_2': {
            'type': 'file',
            'label': 'Second Evidence',
            'icon': 'inventory_2',
          },
        },
      );

      final state = WizardStateModel(selectedWorkflowId: 'test_wf');

      await tester.pumpWidget(
        createWidgetUnderTest(workflow: workflow, mockState: state),
      );
      await tester.pumpAndSettle();

      // Verify labels are present
      expect(find.text('First Evidence'), findsOneWidget);
      expect(find.text('Second Evidence'), findsOneWidget);

      // Verify icons are present
      expect(find.byIcon(Icons.history), findsOneWidget);
      expect(find.byIcon(Icons.inventory_2), findsOneWidget);
    });

    testWidgets('renders fallback message if uiSchema is empty', (
      tester,
    ) async {
      const workflow = Workflow(
        id: 'empty_wf',
        name: 'Empty Workflow',
        description: 'No Schema',
        uiSchema: {},
      );

      final state = WizardStateModel(selectedWorkflowId: 'empty_wf');

      await tester.pumpWidget(
        createWidgetUnderTest(workflow: workflow, mockState: state),
      );
      await tester.pumpAndSettle();

      // Should find no input fields
      expect(find.byType(TextField), findsNothing);
      expect(find.byIcon(Icons.history), findsNothing);
      // Should find the fallback text
      expect(find.byType(Text), findsWidgets);
    });

    testWidgets('renders text inputs based on uiSchema', (tester) async {
      const workflow = Workflow(
        id: 'text_wf',
        name: 'Text Workflow',
        description: 'Testing Text Inputs',
        uiSchema: {
          'user_name': {'type': 'text', 'label': 'Your Name'},
        },
      );

      final state = WizardStateModel(selectedWorkflowId: 'text_wf');

      await tester.pumpWidget(
        createWidgetUnderTest(workflow: workflow, mockState: state),
      );
      await tester.pumpAndSettle();

      expect(find.text('Your Name'), findsOneWidget);
      expect(find.byType(TextFormField), findsOneWidget);
    });
  });
}
