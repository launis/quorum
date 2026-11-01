import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('I18nTextField Widget & Hardening Tests', () {
    testWidgets(
      'Positive 1: I18nTextField should only emit onChanged upon focus loss, not on every keystroke',
      (WidgetTester tester) async {
        int emitCount = 0;
        I18nText? emittedText;

        final FocusNode externalFocusNode = FocusNode();
        addTearDown(externalFocusNode.dispose);

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
                    initialData: const I18nText(
                      translations: {'en': 'Initial'},
                    ),
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

    testWidgets(
      'Positive 2: adds secondary language translation via dialog, edits text, syncs didUpdateWidget, and deletes translation',
      (WidgetTester tester) async {
        I18nText? currentData = const I18nText(
          translations: {'en': 'English Base'},
        );
        late StateSetter outerSetState;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: StatefulBuilder(
              builder: (context, setState) {
                outerSetState = setState;
                return Scaffold(
                  body: SingleChildScrollView(
                    child: I18nTextField(
                      label: 'Title Field',
                      initialData: currentData,
                      onChanged: (val) {
                        currentData = val;
                      },
                    ),
                  ),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Open Add Translation dialog
        await tester.tap(find.byIcon(Icons.add_circle_outline));
        await tester.pumpAndSettle();

        expect(find.byType(AlertDialog), findsOneWidget);
        final dialogField = find.descendant(
          of: find.byType(AlertDialog),
          matching: find.byType(TextField),
        );
        await tester.enterText(dialogField, 'FI');
        await tester.tap(find.widgetWithText(FilledButton, 'Create'));
        await tester.pumpAndSettle();

        expect(find.text('FI'), findsOneWidget);

        // Enter Finnish translation text and wait for debounce timer (600ms)
        final textFields = find.byType(TextField);
        expect(textFields, findsNWidgets(2));
        await tester.enterText(textFields.at(1), 'Suomenkielinen otsikko');
        await tester.pump(const Duration(milliseconds: 650));
        await tester.pumpAndSettle();

        expect(
          currentData?.translations,
          equals({'en': 'English Base', 'fi': 'Suomenkielinen otsikko'}),
        );

        // Verify delete IconButton uses SystemMouseCursors.click
        final deleteBtn = tester.widget<IconButton>(
          find.widgetWithIcon(IconButton, Icons.delete_outline),
        );
        expect(deleteBtn.mouseCursor, equals(SystemMouseCursors.click));

        // External didUpdateWidget update adding 'sv' and updating 'fi'
        outerSetState(() {
          currentData = const I18nText(
            translations: {
              'en': 'English Updated',
              'fi': 'Päivitetty otsikko',
              'sv': 'Svensk rubrik',
            },
          );
        });
        await tester.pumpAndSettle();

        expect(find.text('SV'), findsOneWidget);
        expect(find.text('Svensk rubrik'), findsOneWidget);

        // Delete 'FI' translation
        await tester.tap(
          find.widgetWithIcon(IconButton, Icons.delete_outline).first,
        );
        await tester.pumpAndSettle();

        expect(find.text('FI'), findsNothing);
        expect(currentData?.translations.containsKey('fi'), isFalse);
        expect(currentData?.translations['sv'], equals('Svensk rubrik'));
      },
    );

    testWidgets(
      'Negative/Boundary 1: blank language code in dialog is rejected and clearing default text removes empty keys',
      (WidgetTester tester) async {
        I18nText? emitted;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: I18nTextField(
                label: 'Boundary Label',
                initialData: const I18nText(
                  translations: {'en': 'Non-empty', 'de': 'Deutsch'},
                ),
                onChanged: (val) => emitted = val,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Open dialog and attempt to create with whitespace-only language code
        await tester.tap(find.byIcon(Icons.add_circle_outline));
        await tester.pumpAndSettle();

        final dialogField = find.descendant(
          of: find.byType(AlertDialog),
          matching: find.byType(TextField),
        );
        await tester.enterText(dialogField, '  ');
        await tester.tap(find.widgetWithText(FilledButton, 'Create'));
        await tester.pumpAndSettle();

        // Dialog remains open because blank language code is rejected
        expect(find.byType(AlertDialog), findsOneWidget);

        // Cancel dialog
        await tester.tap(find.widgetWithText(TextButton, 'Cancel'));
        await tester.pumpAndSettle();
        expect(find.byType(AlertDialog), findsNothing);

        // Clear both 'en' and 'de' fields and verify empty strings are stripped from emitted map
        final fields = find.byType(TextField);
        await tester.enterText(fields.at(0), '');
        await tester.enterText(fields.at(1), '');
        await tester.pump(const Duration(milliseconds: 650));
        await tester.pumpAndSettle();

        expect(emitted, isNotNull);
        expect(emitted!.translations, isEmpty);
      },
    );

    testWidgets(
      'Negative/Boundary 2: LayoutBuilder switches at 400px width boundary with leadingInput/bottomInput and null initialData clears secondary controllers',
      (WidgetTester tester) async {
        I18nText? initialData = const I18nText(
          translations: {'en': 'Main', 'fr': 'Français'},
        );
        double containerWidth = 399.0;
        late StateSetter outerSetState;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: StatefulBuilder(
              builder: (context, setState) {
                outerSetState = setState;
                return Scaffold(
                  body: SingleChildScrollView(
                    child: Center(
                      child: SizedBox(
                        width: containerWidth,
                        child: I18nTextField(
                          label: 'Responsive Field',
                          initialData: initialData,
                          leadingInput: const SizedBox(
                            key: ValueKey<String>('leading_widget'),
                            width: 80,
                            height: 40,
                          ),
                          bottomInput: const SizedBox(
                            key: ValueKey<String>('bottom_widget'),
                            height: 24,
                          ),
                          onChanged: (_) {},
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(
          find.byKey(const ValueKey<String>('leading_widget')),
          findsOneWidget,
        );
        expect(
          find.byKey(const ValueKey<String>('bottom_widget')),
          findsOneWidget,
        );
        expect(find.text('FR'), findsOneWidget);
        expect(tester.takeException(), isNull);

        // Expand width across >= 400px boundary (accounting for Card padding 32px -> 440px outer width)
        outerSetState(() {
          containerWidth = 440.0;
          initialData = null;
        });
        await tester.pumpAndSettle();

        expect(find.text('FR'), findsNothing);
        expect(tester.takeException(), isNull);
      },
    );
  });
}
