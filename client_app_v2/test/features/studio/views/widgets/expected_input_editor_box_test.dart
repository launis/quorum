import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/expected_input_editor_box.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'ExpectedInputEditorBox safely unfocuses nodes before disposal without crashing',
    (WidgetTester tester) async {
      final inputDef = ExpectedInput(
        inputKey: 'test_key',
        label: const I18nText(translations: {'en': 'Test Label'}),
        required: true,
        description: const I18nText(translations: {'en': 'Test Description'}),
        aiDescription: 'AI description',
      );

      final stateNotifier = ValueNotifier<bool>(true);

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [Locale('en')],
          home: Scaffold(
            body: ValueListenableBuilder<bool>(
              valueListenable: stateNotifier,
              builder: (context, showEditor, child) {
                if (!showEditor) {
                  return const Text('Editor Removed');
                }
                return SingleChildScrollView(
                  child: ExpectedInputEditorBox(
                    inputDef: inputDef,
                    onDelete: () {},
                    onChanged: (updated) {},
                  ),
                );
              },
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find the TextField for the inputKey
      final keyTextFieldFinder = find.widgetWithText(TextField, 'test_key');
      expect(keyTextFieldFinder, findsOneWidget);

      // Tap to give it focus
      await tester.tap(keyTextFieldFinder);
      await tester.pumpAndSettle();

      // Trigger disposal while focused
      stateNotifier.value = false;
      await tester.pumpAndSettle();

      // If it doesn't crash (e.g. RawKeyDownEvent assertion), the dispose logic is safe.
      expect(find.text('Editor Removed'), findsOneWidget);
    },
  );

  testWidgets(
    'ExpectedInputEditorBox renders all four input mode chips in English and Finnish',
    (WidgetTester tester) async {
      final inputDef = ExpectedInput(
        inputKey: 'test_key',
        label: const I18nText(translations: {'en': 'Test Label'}),
        required: true,
        inputModes: const ['file', 'paste'],
        description: const I18nText(translations: {'en': 'Test Description'}),
      );

      // 1. Test English locale
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          locale: const Locale('en'),
          supportedLocales: const [Locale('en'), Locale('fi')],
          home: Scaffold(
            body: SingleChildScrollView(
              child: ExpectedInputEditorBox(
                inputDef: inputDef,
                onDelete: () {},
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.widgetWithText(FilterChip, 'file'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'paste'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'questionnaire'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'assignment'), findsOneWidget);

      // 2. Test Finnish locale
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          locale: const Locale('fi'),
          supportedLocales: const [Locale('en'), Locale('fi')],
          home: Scaffold(
            body: SingleChildScrollView(
              child: ExpectedInputEditorBox(
                inputDef: inputDef,
                onDelete: () {},
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.widgetWithText(FilterChip, 'tiedosto'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'teksti'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'kysely'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'tehtävä'), findsOneWidget);
    },
  );

  testWidgets(
    'ExpectedInputEditorBox selecting assignment mode clears questionnaire and isChatHistory',
    (WidgetTester tester) async {
      ExpectedInput currentDef = ExpectedInput(
        inputKey: 'test_key',
        label: const I18nText(translations: {'en': 'Test Label'}),
        required: true,
        isChatHistory: true,
        inputModes: const ['questionnaire'],
        description: const I18nText(translations: {'en': 'Test Description'}),
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          locale: const Locale('en'),
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                return SingleChildScrollView(
                  child: ExpectedInputEditorBox(
                    inputDef: currentDef,
                    onDelete: () {},
                    onChanged: (updated) {
                      setState(() {
                        currentDef = updated;
                      });
                    },
                  ),
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap assignment chip
      await tester.tap(find.widgetWithText(FilterChip, 'assignment'));
      await tester.pumpAndSettle();

      expect(currentDef.inputModes.contains('assignment'), isTrue);
      expect(currentDef.inputModes.contains('questionnaire'), isFalse);
      expect(currentDef.isChatHistory, isFalse);
    },
  );

  testWidgets(
    'ExpectedInputEditorBox enabling isChatHistory removes assignment mode',
    (WidgetTester tester) async {
      ExpectedInput currentDef = ExpectedInput(
        inputKey: 'test_key',
        label: const I18nText(translations: {'en': 'Test Label'}),
        required: true,
        isChatHistory: false,
        inputModes: const ['file', 'assignment'],
        description: const I18nText(translations: {'en': 'Test Description'}),
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          locale: const Locale('en'),
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                return SingleChildScrollView(
                  child: ExpectedInputEditorBox(
                    inputDef: currentDef,
                    onDelete: () {},
                    onChanged: (updated) {
                      setState(() {
                        currentDef = updated;
                      });
                    },
                  ),
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap isChatHistory chip
      await tester.tap(find.widgetWithText(FilterChip, 'Is Chat History (LLM Parse)'));
      await tester.pumpAndSettle();

      expect(currentDef.isChatHistory, isTrue);
      expect(currentDef.inputModes.contains('assignment'), isFalse);
      expect(currentDef.inputModes.contains('file'), isTrue);
    },
  );
}

