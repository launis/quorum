import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/expected_input_editor_box.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

ExpectedInput _buildDefaultInput({
  String inputKey = 'product_text',
  bool required = false,
  bool isChatHistory = false,
  bool isEndorsedDeliverable = false,
  bool scanForPerformativePatterns = false,
  List<String> inputModes = const <String>['file'],
  String? aiDescription = 'Primary document under evaluation.',
  List<QuestionnaireItem> questionnaireDefinition = const <QuestionnaireItem>[],
}) {
  return ExpectedInput(
    inputKey: inputKey,
    label: const I18nText(
      translations: <String, String>{'en': 'Final Product', 'fi': 'Lopputuote'},
    ),
    description: const I18nText(
      translations: <String, String>{
        'en': 'Upload the final deliverable.',
        'fi': 'Lataa lopputuote.',
      },
    ),
    required: required,
    isChatHistory: isChatHistory,
    isEndorsedDeliverable: isEndorsedDeliverable,
    scanForPerformativePatterns: scanForPerformativePatterns,
    inputModes: inputModes,
    aiDescription: aiDescription,
    questionnaireDefinition: questionnaireDefinition,
  );
}

Widget _buildTestHarness({
  required ExpectedInput initialInput,
  required ValueChanged<ExpectedInput> onChanged,
  VoidCallback? onDelete,
  Locale locale = const Locale('en'),
}) {
  ExpectedInput currentInput = initialInput;
  return MaterialApp(
    locale: locale,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: StatefulBuilder(
      builder: (BuildContext context, StateSetter setState) {
        return Scaffold(
          body: SingleChildScrollView(
            child: ExpectedInputEditorBox(
              inputDef: currentInput,
              onDelete: onDelete ?? () {},
              onChanged: (ExpectedInput updated) {
                setState(() {
                  currentInput = updated;
                });
                onChanged(updated);
              },
            ),
          ),
        );
      },
    ),
  );
}

void main() {
  group('ExpectedInputEditorBox Widget & Hardening Tests', () {
    testWidgets(
      'Positive 1: renders localized fields, updates key and AI description on blur, enforces chatHistory/endorsed mutual exclusion, and triggers onDelete',
      (WidgetTester tester) async {
        ExpectedInput captured = _buildDefaultInput(
          inputModes: const <String>['file', 'assignment'],
        );
        int deleteCount = 0;

        await tester.pumpWidget(
          _buildTestHarness(
            initialInput: captured,
            onChanged: (ExpectedInput updated) => captured = updated,
            onDelete: () => deleteCount++,
          ),
        );
        await tester.pumpAndSettle();

        // Verify Desktop Pro Tool mouse cursor on delete button and chips
        final IconButton deleteBtn = tester.widget<IconButton>(
          find.byKey(const ValueKey<String>('expected_input_delete_button')),
        );
        expect(deleteBtn.mouseCursor, equals(SystemMouseCursors.click));

        final FilterChip requiredChip = tester.widget<FilterChip>(
          find.byKey(const ValueKey<String>('expected_input_required_chip')),
        );
        expect(requiredChip.mouseCursor, equals(SystemMouseCursors.click));

        // Edit inputKey and unfocus by focusing AI description field
        final Finder keyField = find.byKey(
          const ValueKey<String>('expected_input_key_field'),
        );
        final Finder aiDescField = find.byKey(
          const ValueKey<String>('expected_input_ai_desc_field'),
        );

        await tester.enterText(keyField, '  updated_role_key  ');
        await tester.ensureVisible(aiDescField);
        await tester.tap(aiDescField);
        await tester.pumpAndSettle();
        expect(captured.inputKey, equals('updated_role_key'));

        // Edit AI description and submit
        await tester.enterText(aiDescField, '  Updated English AI directive  ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();
        expect(captured.aiDescription, equals('Updated English AI directive'));

        // Toggle Required and ScanPerformative
        final Finder reqChipFinder = find.byKey(
          const ValueKey<String>('expected_input_required_chip'),
        );
        await tester.ensureVisible(reqChipFinder);
        await tester.tap(reqChipFinder);
        await tester.pumpAndSettle();
        expect(captured.required, isTrue);

        final Finder scanChipFinder = find.byKey(
          const ValueKey<String>('expected_input_scan_performative_chip'),
        );
        await tester.ensureVisible(scanChipFinder);
        await tester.tap(scanChipFinder);
        await tester.pumpAndSettle();
        expect(captured.scanForPerformativePatterns, isTrue);

        // Toggle Endorsed Deliverable -> removes 'assignment' mode
        final Finder endorsedChipFinder = find.byKey(
          const ValueKey<String>('expected_input_endorsed_chip'),
        );
        await tester.ensureVisible(endorsedChipFinder);
        await tester.tap(endorsedChipFinder);
        await tester.pumpAndSettle();
        expect(captured.isEndorsedDeliverable, isTrue);
        expect(captured.isChatHistory, isFalse);
        expect(captured.inputModes, equals(<String>['file']));

        // Toggle Chat History -> disables Endorsed Deliverable automatically
        final Finder chatChipFinder = find.byKey(
          const ValueKey<String>('expected_input_chat_history_chip'),
        );
        await tester.ensureVisible(chatChipFinder);
        await tester.tap(chatChipFinder);
        await tester.pumpAndSettle();
        expect(captured.isChatHistory, isTrue);
        expect(captured.isEndorsedDeliverable, isFalse);

        // Trigger delete callback
        final Finder delBtnFinder = find.byKey(
          const ValueKey<String>('expected_input_delete_button'),
        );
        await tester.ensureVisible(delBtnFinder);
        await tester.tap(delBtnFinder);
        await tester.pumpAndSettle();
        expect(deleteCount, equals(1));
      },
    );

    testWidgets(
      'Positive 2: switches to questionnaire mode, adds questions, edits questionId, and deletes first question without stale state',
      (WidgetTester tester) async {
        ExpectedInput captured = _buildDefaultInput(
          isChatHistory: true,
          inputModes: const <String>['file'],
        );

        await tester.pumpWidget(
          _buildTestHarness(
            initialInput: captured,
            onChanged: (ExpectedInput updated) => captured = updated,
          ),
        );
        await tester.pumpAndSettle();

        // Select 'questionnaire' mode -> clears other modes and resets isChatHistory
        await tester.tap(
          find.byKey(
            const ValueKey<String>('expected_input_mode_chip_questionnaire'),
          ),
        );
        await tester.pumpAndSettle();

        expect(captured.inputModes, equals(<String>['questionnaire']));
        expect(captured.isChatHistory, isFalse);
        expect(
          find.text('No questions defined yet. Add one below.'),
          findsOneWidget,
        );

        // Add two questions
        final Finder addBtn = find.byKey(
          const ValueKey<String>('questionnaire_add_btn'),
        );
        await tester.ensureVisible(addBtn);
        await tester.tap(addBtn);
        await tester.pumpAndSettle();

        await tester.ensureVisible(addBtn);
        await tester.tap(addBtn);
        await tester.pumpAndSettle();

        expect(captured.questionnaireDefinition.length, equals(2));
        expect(captured.questionnaireDefinition[0].questionId, equals('q1'));
        expect(captured.questionnaireDefinition[1].questionId, equals('q2'));

        // Edit second questionId and submit
        final Finder q2Field = find.byKey(
          const ValueKey<String>('question_id_field_1'),
        );
        await tester.ensureVisible(q2Field);
        await tester.enterText(q2Field, '  custom_q2  ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();
        expect(
          captured.questionnaireDefinition[1].questionId,
          equals('custom_q2'),
        );

        // Delete the FIRST question ('q1') and verify remaining controller syncs to 'custom_q2'
        final Finder deleteFirstBtn = find.byKey(
          const ValueKey<String>('question_delete_btn_0'),
        );
        await tester.ensureVisible(deleteFirstBtn);
        await tester.tap(deleteFirstBtn);
        await tester.pumpAndSettle();

        expect(captured.questionnaireDefinition.length, equals(1));
        expect(
          captured.questionnaireDefinition[0].questionId,
          equals('custom_q2'),
        );
        final TextField remainingField = tester.widget<TextField>(
          find.byKey(const ValueKey<String>('question_id_field_0')),
        );
        expect(remainingField.controller?.text, equals('custom_q2'));
      },
    );

    testWidgets(
      'Negative 1: throws AppException when ExpectedInput inputKey is empty or whitespace (Fail-Fast)',
      (WidgetTester tester) async {
        final ExpectedInput invalidInput = _buildDefaultInput(inputKey: '   ');

        await tester.pumpWidget(
          _buildTestHarness(initialInput: invalidInput, onChanged: (_) {}),
        );

        expect(tester.takeException(), isA<AppException>());
      },
    );

    testWidgets(
      'Negative 2: throws AppException when inputModes contains unsupported mode or QuestionnaireItem has empty questionId (Fail-Fast)',
      (WidgetTester tester) async {
        final ExpectedInput unsupportedModeInput = _buildDefaultInput(
          inputModes: const <String>['unsupported_mode'],
        );

        await tester.pumpWidget(
          _buildTestHarness(
            initialInput: unsupportedModeInput,
            onChanged: (_) {},
          ),
        );

        expect(tester.takeException(), isA<AppException>());

        final ExpectedInput invalidQuestionInput = _buildDefaultInput(
          inputModes: const <String>['questionnaire'],
          questionnaireDefinition: const <QuestionnaireItem>[
            QuestionnaireItem(
              questionId: '  ',
              question: I18nText(translations: <String, String>{'en': 'Q?'}),
              type: 'text',
            ),
          ],
        );

        await tester.pumpWidget(
          _buildTestHarness(
            initialInput: invalidQuestionInput,
            onChanged: (_) {},
          ),
        );

        expect(tester.takeException(), isA<AppException>());
      },
    );

    testWidgets(
      'Boundary (ISTQB BVA): prevents deselecting the last remaining input mode (min=1) and restores previous inputKey when cleared to whitespace',
      (WidgetTester tester) async {
        ExpectedInput captured = _buildDefaultInput(
          inputKey: 'preserved_key',
          inputModes: const <String>['file'],
        );

        await tester.pumpWidget(
          _buildTestHarness(
            initialInput: captured,
            onChanged: (ExpectedInput updated) => captured = updated,
          ),
        );
        await tester.pumpAndSettle();

        // Attempt to deselect the sole active mode ('file') -> must remain ['file']
        await tester.tap(
          find.byKey(const ValueKey<String>('expected_input_mode_chip_file')),
        );
        await tester.pumpAndSettle();
        expect(captured.inputModes, equals(<String>['file']));

        // Attempt to clear inputKey to whitespace and submit -> restores 'preserved_key'
        final Finder keyField = find.byKey(
          const ValueKey<String>('expected_input_key_field'),
        );
        await tester.enterText(keyField, '   ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();

        expect(captured.inputKey, equals('preserved_key'));
        final TextField keyWidget = tester.widget<TextField>(keyField);
        expect(keyWidget.controller?.text, equals('preserved_key'));
      },
    );
  });
}
