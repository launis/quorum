import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child) {
    return ProviderScope(
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en')],
        home: Scaffold(body: child),
      ),
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
              contrastiveExample: const ContrastivePairDTO(
                acceptable: 'Acceptable sentence with deep reasoning.',
                rejected:
                    'Rejected counterpart demonstrating disqualification.',
              ),
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

  group('ScaleEditorModal Modernized Tests', () {
    testWidgets(
      'renders initial scale and all 5 visual cards with elevation 2',
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

        // Verify the 5 semantic section headers
        expect(
          find.text('1. Core Hypothesis & Scope', skipOffstage: false),
          findsOneWidget,
        );
        expect(
          find.text('2. Reasoning Chain & Anti-Patterns', skipOffstage: false),
          findsOneWidget,
        );
        expect(
          find.text('3. Contrastive Calibration', skipOffstage: false),
          findsOneWidget,
        );
        expect(
          find.text(
            '4. Lexical Anchors & Fast Falsification',
            skipOffstage: false,
          ),
          findsOneWidget,
        );
        expect(
          find.text('5. Aggregation & Reverse Polarity', skipOffstage: false),
          findsOneWidget,
        );

        // Verify Card widgets with elevation 2
        final cards = tester.widgetList<Card>(find.byType(Card));
        expect(
          cards.where((c) => c.elevation == 2).length,
          greaterThanOrEqualTo(5),
        );
      },
    );

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

      final addCriterionBtn = find.byType(OutlinedButton).first;
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

      // Start with 2 claims so delete button is visible
      final sampleScale = createSampleScale().copyWith(
        claims: [
          createSampleScale().claims.first,
          MatrixClaim(
            label: const I18nText(translations: {'en': 'Claim Level 5b'}),
            tdaAssertions: [
              TDAAssertion.create(
                conceptDescription: 'Second claim concept description',
                inverseEvidence: false,
                aggregationMode: AggregationMode.exists,
              ),
            ],
          ),
        ],
      );
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

      final saveButton = find.widgetWithText(FilledButton, 'Save');
      await tester.tap(saveButton);
      await tester.pumpAndSettle();

      expect(savedResult, isNotNull);
      expect(savedResult!.claims.length, 1);
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

        await tester.enterText(initialField, 'Bad');
        await tester.pumpAndSettle();

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

        expect(find.text('Facts To Find (Comma-separated list)'), findsNothing);

        final dropdown = find
            .byType(DropdownButtonFormField<EvaluationTrack>)
            .first;
        await tester.ensureVisible(dropdown);
        await tester.tap(dropdown);
        await tester.pumpAndSettle();

        final sensorItem = find.text('Technical Fact Extraction').last;
        await tester.tap(sensorItem);
        await tester.pumpAndSettle();

        expect(
          find.text('Facts To Find (Comma-separated list)'),
          findsOneWidget,
        );
        expect(find.text('Logical Expression'), findsOneWidget);
      },
    );

    testWidgets(
      'typing anchor in TagChipInput without Enter and clicking Save retains anchor (Dual-Shield auto-flush)',
      (WidgetTester tester) async {
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

        // Find anchor chip input field inside Card 4
        final anchorField = find.widgetWithText(
          TextField,
          'Type word and press Enter...',
        );
        await tester.ensureVisible(anchorField);
        await tester.enterText(anchorField, 'uncommitted_anchor');
        await tester.pumpAndSettle();

        // Click save button without pressing Enter
        final saveBtn = find.widgetWithText(FilledButton, 'Save');
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(savedResult, isNotNull);
        final anchors =
            savedResult!.claims.first.tdaAssertions.first.syntacticAnchors;
        expect(anchors, contains('uncommitted_anchor'));
      },
    );

    testWidgets(
      'typing anchor without Enter and pressing Ctrl+S retains anchor',
      (WidgetTester tester) async {
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

        final anchorField = find.widgetWithText(
          TextField,
          'Type word and press Enter...',
        );
        await tester.ensureVisible(anchorField);
        await tester.enterText(anchorField, 'shortcut_anchor');
        await tester.pumpAndSettle();

        // Trigger Ctrl + S shortcut
        await tester.sendKeyDownEvent(LogicalKeyboardKey.control);
        await tester.sendKeyEvent(LogicalKeyboardKey.keyS);
        await tester.sendKeyUpEvent(LogicalKeyboardKey.control);
        await tester.pumpAndSettle();

        expect(savedResult, isNotNull);
        final anchors =
            savedResult!.claims.first.tdaAssertions.first.syntacticAnchors;
        expect(anchors, contains('shortcut_anchor'));
      },
    );

    testWidgets(
      'rapid double-clicks on Save invoke save debouncing without duplicate pops',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final sampleScale = createSampleScale();
        int popCount = 0;

        await tester.pumpWidget(
          createTestWidget(
            Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () async {
                    final res = await showDialog<MatrixScale>(
                      context: context,
                      builder: (ctx) =>
                          ScaleEditorModal(initialScale: sampleScale),
                    );
                    if (res != null) popCount++;
                  },
                  child: const Text('Open Modal'),
                );
              },
            ),
          ),
        );

        await tester.tap(find.text('Open Modal'));
        await tester.pumpAndSettle();

        final saveBtn = find.widgetWithText(FilledButton, 'Save');
        // Rapidly tap save twice
        await tester.tap(saveBtn);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(popCount, 1);
      },
    );

    testWidgets(
      'validation error on unselected claim switches master selector to offending claim',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        // Create scale where Claim 2 has an invalid short description
        final sampleScale = createSampleScale().copyWith(
          claims: [
            createSampleScale().claims.first,
            MatrixClaim(
              label: const I18nText(translations: {'en': 'Claim 2'}),
              tdaAssertions: [
                TDAAssertion.create(
                  conceptDescription: 'Short', // < 10 characters!
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
          ],
        );

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

        // We are on Claim 1. Click Save -> should detect Claim 2 is invalid and navigate to Claim 2
        final saveBtn = find.widgetWithText(FilledButton, 'Save');
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        // Offending short text from Claim 2 should now be visible
        expect(find.widgetWithText(TextFormField, 'Short'), findsOneWidget);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();
        expect(
          find.text('Concept description must be at least 10 characters long.'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'pressing Esc or close button with dirty state triggers discard dialog',
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

        // Mutate a field to make model dirty
        final aiLabelField = find.widgetWithText(TextFormField, 'EXEMPLARY_5');
        await tester.enterText(aiLabelField, 'DIRTY_STATE_LABEL');
        await tester.pumpAndSettle();

        // Tap close button in AppBar
        final closeBtn = find.byIcon(Icons.close);
        await tester.tap(closeBtn);
        await tester.pumpAndSettle();

        expect(find.text('Discard Changes?'), findsOneWidget);
        expect(
          find.text(
            'You have unsaved changes to this evaluation scale. Are you sure you want to close without saving?',
          ),
          findsOneWidget,
        );

        // Tap "Continue Editing"
        await tester.tap(find.text('Continue Editing'));
        await tester.pumpAndSettle();

        // Modal is still open with dirty changes intact
        expect(find.text('DIRTY_STATE_LABEL'), findsOneWidget);
      },
    );

    testWidgets(
      'pressing close button with clean state dismisses without discard dialog',
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

        // Tap close button in AppBar WITHOUT modifying anything
        final closeBtn = find.byIcon(Icons.close);
        await tester.tap(closeBtn);
        await tester.pumpAndSettle();

        expect(find.text('Discard Changes?'), findsNothing);
      },
    );

    testWidgets(
      'scale with name: null dismisses cleanly without discard dialog',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final nullNameScale = createSampleScale().copyWith(name: null);

        await tester.pumpWidget(
          createTestWidget(
            Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) =>
                          ScaleEditorModal(initialScale: nullNameScale),
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

        // Tap close button in AppBar WITHOUT modifying anything
        final closeBtn = find.byIcon(Icons.close);
        await tester.tap(closeBtn);
        await tester.pumpAndSettle();

        expect(find.text('Discard Changes?'), findsNothing);
      },
    );

    testWidgets(
      'immediate Esc after typing in concept description triggers discard dialog',
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

        // Type into concept description
        final conceptField = find.widgetWithText(
          TextFormField,
          sampleScale.claims.first.tdaAssertions.first.conceptDescription,
        );
        await tester.enterText(
          conceptField,
          'Modified concept description with extra depth',
        );

        // Immediate Esc key event
        await tester.sendKeyEvent(LogicalKeyboardKey.escape);
        await tester.pumpAndSettle();

        expect(find.text('Discard Changes?'), findsOneWidget);
      },
    );

    testWidgets(
      'renders without RenderFlex overflow on narrow viewport (800x600)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(800, 600);
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

        expect(find.byType(ScaleEditorModal), findsOneWidget);
      },
    );

    testWidgets(
      'renders preview prompt button with tooltip in app bar',
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

        expect(find.byIcon(Icons.code), findsOneWidget);
        expect(
          find.byTooltip('Preview scale model prompt (XML)'),
          findsOneWidget,
        );
      },
    );
  });
}
