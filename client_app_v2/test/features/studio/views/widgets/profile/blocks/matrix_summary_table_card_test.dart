import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  const String validPrfId = 'prf_01964528b7707d5081986327cf9a6e82';
  const String validWfId = 'wf_01964528b7707d5081986327cf9a6e82';

  OutputProfile createTestProfile({
    List<TargetBlockType> targetBlockOrder = const [
      TargetBlockType.matrixSummaryTableBlock,
    ],
    List<String> matrixVisibleColumns = const ['label', 'raw_score'],
    String? rowExplanationDirective,
    int? rowExplanationLengthConstraint,
  }) {
    return OutputProfile(
      id: validPrfId,
      workflowId: validWfId,
      name: const I18nText(translations: {'en': 'Test Profile'}),
      targetBlockOrder: targetBlockOrder,
      matrixVisibleColumns: matrixVisibleColumns,
      rowExplanationDirective: rowExplanationDirective,
      rowExplanationLengthConstraint: rowExplanationLengthConstraint,
    );
  }

  Widget buildTestHarness({
    required OutputProfile initialPayload,
    required void Function(OutputProfile) onUpdate,
    Locale locale = const Locale('en'),
  }) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: StatefulBuilder(
            builder: (context, setState) {
              OutputProfile currentPayload = initialPayload;
              return MatrixSummaryTableCard(
                payload: currentPayload,
                updatePayload: (newPayload) {
                  setState(() {
                    currentPayload = newPayload;
                  });
                  onUpdate(newPayload);
                },
              );
            },
          ),
        ),
      ),
    );
  }

  group('MatrixSummaryTableCard Positive & Functional Tests', () {
    testWidgets('renders all 8 column FilterChips with localized labels', (
      WidgetTester tester,
    ) async {
      final payload = createTestProfile();

      await tester.pumpWidget(
        buildTestHarness(initialPayload: payload, onUpdate: (_) {}),
      );
      await tester.pumpAndSettle();

      expect(find.byType(MatrixSummaryTableCard), findsOneWidget);
      expect(
        find.byType(FilterChip),
        findsNWidgets(MatrixSummaryTableCard.availableColumnKeys.length),
      );
    });

    testWidgets(
      'renders Finnish localizations cleanly when fi locale is active',
      (WidgetTester tester) async {
        final payload = createTestProfile();

        late AppLocalizations fiL10n;
        await tester.pumpWidget(
          MaterialApp(
            locale: const Locale('fi'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: Builder(
                  builder: (context) {
                    fiL10n = AppLocalizations.of(context)!;
                    return MatrixSummaryTableCard(
                      payload: payload,
                      updatePayload: (_) {},
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text(fiL10n.blockMatrixSummaryTitle), findsOneWidget);
        expect(find.text(fiL10n.studioMatrixColLabel), findsOneWidget);
        expect(find.text(fiL10n.studioMatrixColScore), findsOneWidget);
      },
    );

    testWidgets(
      'toggles TargetBlockType.matrixSummaryTableBlock in targetBlockOrder on switch tap',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          targetBlockOrder: [TargetBlockType.matrixSummaryTableBlock],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return MatrixSummaryTableCard(
                      payload: payload,
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          payload.targetBlockOrder,
          isNot(contains(TargetBlockType.matrixSummaryTableBlock)),
        );

        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          payload.targetBlockOrder,
          contains(TargetBlockType.matrixSummaryTableBlock),
        );
      },
    );

    testWidgets(
      'toggles column keys in matrixVisibleColumns when tapping FilterChip',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          matrixVisibleColumns: ['label'],
        );

        late AppLocalizations l10n;
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    l10n = AppLocalizations.of(context)!;
                    return MatrixSummaryTableCard(
                      payload: payload,
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Select 'criteria' chip
        await tester.tap(find.widgetWithText(FilterChip, l10n.studioMatrixColCriteria));
        await tester.pumpAndSettle();
        expect(payload.matrixVisibleColumns, contains('criteria'));
        expect(payload.matrixVisibleColumns, contains('label'));

        // Deselect 'label' chip
        await tester.tap(find.widgetWithText(FilterChip, l10n.studioMatrixColLabel));
        await tester.pumpAndSettle();
        expect(payload.matrixVisibleColumns, isNot(contains('label')));
        expect(payload.matrixVisibleColumns, contains('criteria'));
      },
    );

    testWidgets(
      'updates rowExplanationDirective and rowExplanationLengthConstraint on valid input',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          rowExplanationDirective: 'Initial directive',
          rowExplanationLengthConstraint: 250,
        );

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (newPayload) => payload = newPayload,
          ),
        );
        await tester.pumpAndSettle();

        final directiveFinder = find.byKey(
          const Key('profile_row_explanation_directive_field'),
        );
        final lengthFinder = find.byKey(
          const Key('profile_row_explanation_length_constraint_field'),
        );

        expect(directiveFinder, findsOneWidget);
        expect(lengthFinder, findsOneWidget);

        await tester.enterText(directiveFinder, '  Explain score variance  ');
        await tester.pumpAndSettle();
        expect(payload.rowExplanationDirective, equals('Explain score variance'));

        await tester.enterText(lengthFinder, '400');
        await tester.pumpAndSettle();
        expect(payload.rowExplanationLengthConstraint, equals(400));
      },
    );
  });

  group('MatrixSummaryTableCard ISTQB Negative & Boundary Tests', () {
    testWidgets(
      'Negative ISTQB: filters out non-digit input in rowExplanationLengthConstraint field via inputFormatters',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          rowExplanationLengthConstraint: null,
        );

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (newPayload) => payload = newPayload,
          ),
        );
        await tester.pumpAndSettle();

        final lengthFinder = find.byKey(
          const Key('profile_row_explanation_length_constraint_field'),
        );
        await tester.enterText(lengthFinder, 'abc-!@#');
        await tester.pumpAndSettle();

        expect(payload.rowExplanationLengthConstraint, isNull);
      },
    );

    testWidgets(
      'Negative ISTQB: whitespace-only directive and empty length constraint reset fields to null',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          rowExplanationDirective: 'Existing directive',
          rowExplanationLengthConstraint: 300,
        );

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (newPayload) => payload = newPayload,
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('profile_row_explanation_directive_field')),
          '   ',
        );
        await tester.pumpAndSettle();
        expect(payload.rowExplanationDirective, isNull);

        await tester.enterText(
          find.byKey(
            const Key('profile_row_explanation_length_constraint_field'),
          ),
          '',
        );
        await tester.pumpAndSettle();
        expect(payload.rowExplanationLengthConstraint, isNull);
      },
    );

    testWidgets(
      'Negative ISTQB: unknown column key fallback in getColumnLabel returns raw key without crashing',
      (WidgetTester tester) async {
        late String resolvedLabel;
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  resolvedLabel = MatrixSummaryTableCard.getColumnLabel(
                    context,
                    'unknown_column_key',
                  );
                  return Text(resolvedLabel);
                },
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(resolvedLabel, equals('unknown_column_key'));
        expect(find.text('unknown_column_key'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary ISTQB: empty matrixVisibleColumns and excluded block state render cleanly on narrow viewport (360x640)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 640);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        // First verify empty matrixVisibleColumns when included
        final emptyColsPayload = createTestProfile(matrixVisibleColumns: []);
        await tester.pumpWidget(
          buildTestHarness(initialPayload: emptyColsPayload, onUpdate: (_) {}),
        );
        await tester.pumpAndSettle();

        for (final chip in tester.widgetList<FilterChip>(
          find.byType(FilterChip),
        )) {
          expect(chip.selected, isFalse);
        }
        expect(tester.takeException(), isNull);

        // Next verify excluded block hides body
        final excludedPayload = createTestProfile(targetBlockOrder: const []);
        await tester.pumpWidget(
          buildTestHarness(initialPayload: excludedPayload, onUpdate: (_) {}),
        );
        await tester.pumpAndSettle();

        expect(find.byType(FilterChip), findsNothing);
        expect(
          find.byKey(const Key('profile_row_explanation_directive_field')),
          findsNothing,
        );
      },
    );
  });
}
