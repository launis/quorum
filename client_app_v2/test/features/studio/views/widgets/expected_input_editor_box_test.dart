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
}
