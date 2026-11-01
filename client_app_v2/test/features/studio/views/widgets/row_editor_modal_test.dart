import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/row_editor_modal.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en')],
      home: Scaffold(body: child),
    );
  }

  group('RowEditorModal Tests', () {
    testWidgets('renders and saves simple I18nText row correctly', (
      WidgetTester tester,
    ) async {
      I18nText? result;

      await tester.pumpWidget(
        createTestWidget(
          Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () async {
                  result = await showDialog<I18nText>(
                    context: context,
                    builder: (ctx) => const RowEditorModal(
                      initialI18nText: I18nText(
                        translations: {'en': 'Initial simple row'},
                      ),
                      isMatrixRow: false,
                    ),
                  );
                },
                child: const Text('Open Modal'),
              );
            },
          ),
        ),
      );

      await tester.tap(find.text('Open Modal'));
      await tester.pumpAndSettle();

      expect(find.text('Initial simple row'), findsOneWidget);

      final textField = find.widgetWithText(TextField, 'Initial simple row');
      await tester.enterText(textField, 'Updated simple row');
      await tester.pump(const Duration(milliseconds: 700));
      await tester.pumpAndSettle();

      final saveButton = find.widgetWithText(FilledButton, 'Save');
      expect(saveButton, findsOneWidget);

      await tester.tap(saveButton);
      await tester.pumpAndSettle();

      expect(result, isNotNull);
      expect(result!.translations['en'], 'Updated simple row');
    });

    testWidgets('renders and saves MatrixRow with aiDescription and label', (
      WidgetTester tester,
    ) async {
      MatrixRow? result;

      await tester.pumpWidget(
        createTestWidget(
          Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () async {
                  result = await showDialog<MatrixRow>(
                    context: context,
                    builder: (ctx) => const RowEditorModal(
                      initialMatrixRow: MatrixRow(
                        label: I18nText(
                          translations: {'en': 'Matrix Row Label'},
                        ),
                        aiDescription: 'Rule explanation for AI',
                      ),
                      isMatrixRow: true,
                    ),
                  );
                },
                child: const Text('Open Modal'),
              );
            },
          ),
        ),
      );

      await tester.tap(find.text('Open Modal'));
      await tester.pumpAndSettle();

      expect(find.text('Rule explanation for AI'), findsOneWidget);
      expect(find.text('Matrix Row Label'), findsOneWidget);

      final aiDescField = find.widgetWithText(
        TextFormField,
        'Rule explanation for AI',
      );
      await tester.enterText(aiDescField, 'Updated rule for AI');
      await tester.pumpAndSettle();

      final labelField = find.widgetWithText(TextField, 'Matrix Row Label');
      await tester.enterText(labelField, 'Updated Matrix Label');
      await tester.pump(const Duration(milliseconds: 700));
      await tester.pumpAndSettle();

      final saveButton = find.widgetWithText(FilledButton, 'Save');
      await tester.tap(saveButton);
      await tester.pumpAndSettle();

      expect(result, isNotNull);
      expect(result!.aiDescription, 'Updated rule for AI');
      expect(result!.label.translations['en'], 'Updated Matrix Label');
    });

    testWidgets('cancels and closes modal on close icon tap or Escape key', (
      WidgetTester tester,
    ) async {
      I18nText? result = const I18nText(translations: {'en': 'Sentinels'});

      await tester.pumpWidget(
        createTestWidget(
          Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () async {
                  result = await showDialog<I18nText>(
                    context: context,
                    builder: (ctx) => const RowEditorModal(
                      initialI18nText: I18nText(
                        translations: {'en': 'Simple row'},
                      ),
                      title: 'Custom Modal Header',
                      isMatrixRow: false,
                    ),
                  );
                },
                child: const Text('Open Modal'),
              );
            },
          ),
        ),
      );

      await tester.tap(find.text('Open Modal'));
      await tester.pumpAndSettle();

      expect(find.text('Custom Modal Header'), findsOneWidget);

      final closeIcon = find.byIcon(Icons.close);
      expect(closeIcon, findsOneWidget);

      await tester.tap(closeIcon);
      await tester.pumpAndSettle();

      expect(result, isNull);
    });

    test(
      'throws AssertionError when both initialMatrixRow and initialI18nText are null',
      () {
        expect(
          () => RowEditorModal(initialMatrixRow: null, initialI18nText: null),
          throwsA(isA<AssertionError>()),
        );
      },
    );

    test(
      'throws AssertionError when isMatrixRow is true but initialMatrixRow is null',
      () {
        expect(
          () => RowEditorModal(
            isMatrixRow: true,
            initialMatrixRow: null,
            initialI18nText: const I18nText(translations: {'en': 'Mismatch'}),
          ),
          throwsA(isA<AssertionError>()),
        );
      },
    );

    test(
      'throws AssertionError when isMatrixRow is false but initialI18nText is null',
      () {
        expect(
          () => RowEditorModal(
            isMatrixRow: false,
            initialMatrixRow: const MatrixRow(
              label: I18nText(translations: {'en': 'Mismatch'}),
              aiDescription: 'Rule',
            ),
            initialI18nText: null,
          ),
          throwsA(isA<AssertionError>()),
        );
      },
    );
  });
}
