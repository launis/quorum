import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/expected_input_editor_box.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_inputs_tab.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

Workflow _buildValidWorkflow({
  String id = 'wf_0195f000000070008000000000000001',
  List<ExpectedInput> expectedInputs = const <ExpectedInput>[],
}) {
  return Workflow(
    id: id,
    slug: 'test-workflow',
    name: const I18nText(translations: <String, String>{'en': 'Test Workflow'}),
    description: const I18nText(
      translations: <String, String>{'en': 'Workflow Description'},
    ),
    modelRegistryId: 'mr_0195f000000070008000000000000001',
    expectedInputs: expectedInputs,
  );
}

Widget _wrapWithMaterialApp(
  Widget child, {
  Locale locale = const Locale('en'),
}) {
  return MaterialApp(
    locale: locale,
    localizationsDelegates: const <LocalizationsDelegate<dynamic>>[
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    supportedLocales: const <Locale>[Locale('en'), Locale('fi')],
    home: Scaffold(body: child),
  );
}

void main() {
  group('WorkflowInputsTab Widget Tests', () {
    testWidgets(
      'renders empty state message when expectedInputs list is empty and adds new input on button click',
      (WidgetTester tester) async {
        Workflow currentWorkflow = _buildValidWorkflow();

        await tester.pumpWidget(
          _wrapWithMaterialApp(
            StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                return WorkflowInputsTab(
                  workflow: currentWorkflow,
                  onChanged: (Workflow updated) {
                    setState(() {
                      currentWorkflow = updated;
                    });
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        final BuildContext innerContext = tester.element(
          find.byType(WorkflowInputsTab),
        );
        final AppLocalizations l10n = AppLocalizations.of(innerContext)!;

        expect(find.text(l10n.studioWorkflowInputsEmpty), findsOneWidget);
        expect(find.byType(ExpectedInputEditorBox), findsNothing);

        await tester.tap(
          find.byKey(const ValueKey<String>('workflow_add_expected_input_btn')),
        );
        await tester.pumpAndSettle();

        expect(currentWorkflow.expectedInputs, hasLength(1));
        expect(
          currentWorkflow.expectedInputs.first.inputKey,
          'new_input_key_0',
        );
        expect(currentWorkflow.expectedInputs.first.inputModes, <String>[
          'file',
        ]);
        expect(find.byType(ExpectedInputEditorBox), findsOneWidget);
      },
    );

    testWidgets(
      'updates and deletes existing expected inputs and avoids duplicate keys on subsequent additions',
      (WidgetTester tester) async {
        Workflow currentWorkflow = _buildValidWorkflow(
          expectedInputs: const <ExpectedInput>[
            ExpectedInput(
              inputKey: 'new_input_key_0',
              label: I18nText(translations: <String, String>{'en': 'First'}),
              required: false,
              inputModes: <String>['file'],
              description: I18nText(
                translations: <String, String>{'en': 'Desc 1'},
              ),
            ),
            ExpectedInput(
              inputKey: 'new_input_key_1',
              label: I18nText(translations: <String, String>{'en': 'Second'}),
              required: true,
              inputModes: <String>['paste'],
              description: I18nText(
                translations: <String, String>{'en': 'Desc 2'},
              ),
            ),
          ],
        );

        await tester.pumpWidget(
          _wrapWithMaterialApp(
            StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                return WorkflowInputsTab(
                  workflow: currentWorkflow,
                  onChanged: (Workflow updated) {
                    setState(() {
                      currentWorkflow = updated;
                    });
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ExpectedInputEditorBox), findsNWidgets(2));

        // Toggle 'Required' FilterChip on the first ExpectedInputEditorBox
        final Finder firstBox = find.byType(ExpectedInputEditorBox).first;
        final Finder requiredChip = find.descendant(
          of: firstBox,
          matching: find.byKey(
            const ValueKey<String>('expected_input_required_chip'),
          ),
        );
        await tester.tap(requiredChip);
        await tester.pumpAndSettle();

        expect(currentWorkflow.expectedInputs.first.required, isTrue);

        // Delete the first input so only 'new_input_key_1' remains at index 0
        final Finder deleteBtn = find.descendant(
          of: firstBox,
          matching: find.byKey(
            const ValueKey<String>('expected_input_delete_button'),
          ),
        );
        await tester.tap(deleteBtn);
        await tester.pumpAndSettle();

        expect(currentWorkflow.expectedInputs, hasLength(1));
        expect(
          currentWorkflow.expectedInputs.single.inputKey,
          'new_input_key_1',
        );

        // Adding a new input when 'new_input_key_1' already exists should mint 'new_input_key_2'
        await tester.tap(
          find.byKey(const ValueKey<String>('workflow_add_expected_input_btn')),
        );
        await tester.pumpAndSettle();

        expect(currentWorkflow.expectedInputs, hasLength(2));
        expect(currentWorkflow.expectedInputs.last.inputKey, 'new_input_key_2');
      },
    );

    testWidgets(
      'Negative Case 1: throws Fail-Fast AppException when workflow id is empty or whitespace',
      (WidgetTester tester) async {
        final Workflow invalidWorkflow = _buildValidWorkflow(id: '   ');

        await tester.pumpWidget(
          _wrapWithMaterialApp(
            WorkflowInputsTab(workflow: invalidWorkflow, onChanged: (_) {}),
          ),
        );

        final Object? exception = tester.takeException();
        expect(exception, isA<AppException>());
        expect(
          (exception as AppException).detail,
          contains('Workflow id cannot be empty in WorkflowInputsTab'),
        );
      },
    );

    testWidgets(
      'Negative Case 2: throws Fail-Fast AppException when an ExpectedInput has an empty inputKey',
      (WidgetTester tester) async {
        final Workflow invalidWorkflow = _buildValidWorkflow(
          expectedInputs: const <ExpectedInput>[
            ExpectedInput(
              inputKey: '  ',
              label: I18nText(translations: <String, String>{'en': 'Invalid'}),
              required: false,
              inputModes: <String>['file'],
              description: I18nText(
                translations: <String, String>{'en': 'Invalid Desc'},
              ),
            ),
          ],
        );

        await tester.pumpWidget(
          _wrapWithMaterialApp(
            WorkflowInputsTab(workflow: invalidWorkflow, onChanged: (_) {}),
          ),
        );

        final Object? exception = tester.takeException();
        expect(exception, isA<AppException>());
        expect(
          (exception as AppException).detail,
          contains(
            'ExpectedInput inputKey cannot be empty in WorkflowInputsTab',
          ),
        );
      },
    );
  });
}
