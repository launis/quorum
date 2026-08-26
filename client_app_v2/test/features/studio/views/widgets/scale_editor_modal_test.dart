import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/core/models/enums.dart';
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

  MatrixScale createSampleScale() {
    return MatrixScale(
      score: 5,
      name: const I18nText(translations: {'en': 'Exemplary Mastery'}),
      aiLabel: 'EXEMPLARY_5',
      claims: [
        MatrixClaim(
          label: const I18nText(translations: {'en': 'Claim Level 5'}),
          tdaAssertions: [
            TDAAssertion(
              tdaId: 'tda_11112222333344445555666677778888',
              conceptDescription: 'Demonstrates deep systemic understanding',
              evaluationTrack: EvaluationTrack.cognitiveJudgement,
              aggregationMode: AggregationMode.exists,
              inverseEvidence: false,
              enforcePreFlight: true,
              anchorTarget: 'Paragraph 1',
              boundingBoxScope: 'paragraph',
              extractionRule: 'Extract complete causal explanation',
              antiPatterns: const [
                AntiPattern(pattern: 'Avoid superficial keywords'),
              ],
              contrastiveExample: 'Superficial: Good job.',
              acceptanceCriteria: const [
                AcceptanceCriterion(
                  instruction: 'Must include 2 causal connectors',
                ),
              ],
              syntacticAnchors: const ['because', 'therefore'],
              factsToFind: const [],
              logicalExpression: null,
            ),
          ],
        ),
      ],
    );
  }

  group('ScaleEditorModal Tests', () {
    testWidgets('renders initial scale and all nested TDA assertion fields', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final sampleScale = createSampleScale();

      await tester.pumpWidget(
        createTestWidget(
          Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (ctx) =>
                        ScaleEditorModal(initialScale: sampleScale),
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

      expect(find.text('Edit Observation'), findsOneWidget);
      expect(find.text('5'), findsOneWidget);
      expect(find.text('Exemplary Mastery'), findsOneWidget);
      expect(find.text('EXEMPLARY_5'), findsOneWidget);
      expect(find.text('Claim 1', skipOffstage: false), findsOneWidget);
      expect(
        find.text(
          'Demonstrates deep systemic understanding',
          skipOffstage: false,
        ),
        findsOneWidget,
      );
      expect(
        find.text('Extract complete causal explanation', skipOffstage: false),
        findsOneWidget,
      );
      expect(find.text('Paragraph 1', skipOffstage: false), findsOneWidget);
    });

    testWidgets('adds a new criterion claim and updates assertion state', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final sampleScale = createSampleScale();
      MatrixScale? savedResult;

      await tester.pumpWidget(
        createTestWidget(
          Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () async {
                  savedResult = await showDialog<MatrixScale>(
                    context: context,
                    builder: (ctx) =>
                        ScaleEditorModal(initialScale: sampleScale),
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

      final addCriterionBtn = find.byType(OutlinedButton);
      await tester.scrollUntilVisible(
        addCriterionBtn,
        200,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.pumpAndSettle();

      expect(addCriterionBtn, findsOneWidget);
      await tester.tap(addCriterionBtn);
      await tester.pumpAndSettle();

      final saveButton = find.widgetWithText(FilledButton, 'Save');
      await tester.tap(saveButton);
      await tester.pumpAndSettle();

      expect(savedResult, isNotNull);
      expect(savedResult!.claims.length, 2);
    });

    testWidgets('deletes an existing claim from the scale', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final sampleScale = createSampleScale();
      MatrixScale? savedResult;

      await tester.pumpWidget(
        createTestWidget(
          Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () async {
                  savedResult = await showDialog<MatrixScale>(
                    context: context,
                    builder: (ctx) =>
                        ScaleEditorModal(initialScale: sampleScale),
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

      final deleteClaimBtn = find.byIcon(Icons.delete).first;
      await tester.tap(deleteClaimBtn);
      await tester.pumpAndSettle();

      expect(find.text('Claim 1'), findsNothing);

      final saveButton = find.widgetWithText(FilledButton, 'Save');
      await tester.tap(saveButton);
      await tester.pumpAndSettle();

      expect(savedResult, isNotNull);
      expect(savedResult!.claims.isEmpty, isTrue);
    });

    testWidgets(
      'ISTQB Negative: conceptDescription validator rejects < 10 characters',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final sampleScale = createSampleScale();

        await tester.pumpWidget(
          createTestWidget(
            Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) =>
                          ScaleEditorModal(initialScale: sampleScale),
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

        final initialField = find.widgetWithText(
          TextFormField,
          'Demonstrates deep systemic understanding',
        );
        expect(initialField, findsOneWidget);

        // Enter short 4-char string (violates min length 10)
        await tester.enterText(initialField, 'Bad');
        await tester.pumpAndSettle();

        // Find Form / TextFormField to trigger validation
        final updatedField = find.widgetWithText(TextFormField, 'Bad');
        final formFieldState = tester.state<FormFieldState<String>>(
          updatedField,
        );
        final isValid = formFieldState.validate();

        expect(isValid, isFalse);
        expect(
          formFieldState.errorText,
          'Concept description must be at least 10 characters long.',
        );
      },
    );

    testWidgets(
      'switches to extractiveSensor and enables factsToFind and logicalExpression',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final sampleScale = createSampleScale();

        await tester.pumpWidget(
          createTestWidget(
            Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) =>
                          ScaleEditorModal(initialScale: sampleScale),
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

        // Initially cognitiveJudgement, sensor fields are not present
        expect(find.text('Facts To Find (Comma-separated list)'), findsNothing);

        // Open Dropdown to switch to Extractive Sensor
        final dropdown = find
            .byType(DropdownButtonFormField<EvaluationTrack>)
            .first;
        await tester.ensureVisible(dropdown);
        await tester.tap(dropdown);
        await tester.pumpAndSettle();

        final sensorItem = find.text('EXTRACTIVE_SENSOR (Mechanical)').last;
        await tester.tap(sensorItem);
        await tester.pumpAndSettle();

        // Now factsToFind field should be visible
        expect(
          find.text('Facts To Find (Comma-separated list)'),
          findsOneWidget,
        );
        expect(find.text('Logical Expression'), findsOneWidget);
      },
    );
  });
}
