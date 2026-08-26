import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'I18nTextField should only emit onChanged upon focus loss, not on every keystroke',
    (WidgetTester tester) async {
      int emitCount = 0;
      I18nText? emittedText;

      final FocusNode externalFocusNode = FocusNode();

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
            body: Column(
              children: [
                I18nTextField(
                  label: 'Test Label',
                  initialData: const I18nText(translations: {'en': 'Initial'}),
                  onChanged: (val) {
                    emitCount++;
                    emittedText = val;
                  },
                ),
                TextField(
                  focusNode: externalFocusNode,
                  decoration: const InputDecoration(labelText: 'External'),
                ),
              ],
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      final textFieldFinder = find.byType(TextField).first;
      expect(textFieldFinder, findsOneWidget);

      // Tap to gain focus
      await tester.tap(textFieldFinder);
      await tester.pumpAndSettle();

      // Type text
      await tester.enterText(textFieldFinder, 'Initial Updated');
      await tester.pumpAndSettle();

      // The key architectural constraint: Riverpod state must NOT be rebuilt on every keystroke
      // If emitCount > 0 here, it means we emitted on keypress, which is a bug.
      expect(
        emitCount,
        0,
        reason:
            'I18nTextField must not emit changes on every keystroke to prevent RawKeyboard assertion crashes',
      );

      // Move focus away to trigger the onChanged
      externalFocusNode.requestFocus();
      await tester.pumpAndSettle();

      expect(
        emitCount,
        1,
        reason: 'I18nTextField must emit exactly once upon focus loss',
      );
      expect(emittedText?.translations['en'], 'Initial Updated');
    },
  );
}
