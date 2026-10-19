import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_strictness_tab.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Workflow createTestWorkflow({
    int defaultStrictnessLevel = 50,
    int defaultLexicalStrictnessLevel = 50,
  }) {
    return Workflow(
      id: 'wor_1234567890abcdef',
      slug: 'test-workflow',
      name: const I18nText(translations: {'en': 'Test Workflow'}),
      description: const I18nText(translations: {'en': 'Test Description'}),
      modelRegistryId: 'sys_b1c2d3e4f5a60718',
      defaultStrictnessLevel: defaultStrictnessLevel,
      defaultLexicalStrictnessLevel: defaultLexicalStrictnessLevel,
    );
  }

  Widget buildTestApp(
    Workflow workflow, {
    Function(Workflow)? onChanged,
    Locale locale = const Locale('en'),
  }) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: WorkflowStrictnessTab(
            workflow: workflow,
            onChanged: onChanged ?? (_) {},
          ),
        ),
      ),
    );
  }

  group('WorkflowStrictnessTab Widget Tests', () {
    testWidgets('test_workflow_strictness_tab_renders_slider_chips_and_badge', (
      WidgetTester tester,
    ) async {
      final workflow = createTestWorkflow(
        defaultStrictnessLevel: 50,
        defaultLexicalStrictnessLevel: 85,
      );

      await tester.pumpWidget(buildTestApp(workflow));
      await tester.pumpAndSettle();

      expect(find.byType(Slider), findsNWidgets(2));
      expect(find.byType(ChoiceChip), findsNWidgets(8));
      expect(find.text('50%'), findsOneWidget); // Scoring pill badge
      expect(find.text('85%'), findsWidgets); // Lexical pill badge & chip
      expect(find.text('Scoring Strictness Level'), findsOneWidget);
      expect(
        find.text('Lexical Verification Strictness Level'),
        findsOneWidget,
      );
      expect(find.text('50% Normal'), findsOneWidget);
      expect(find.text('85% Strict'), findsNWidgets(2));
    });

    testWidgets(
      'test_workflow_strictness_tab_tapping_preset_chips_updates_workflow',
      (WidgetTester tester) async {
        Workflow currentWorkflow = createTestWorkflow(
          defaultStrictnessLevel: 50,
          defaultLexicalStrictnessLevel: 50,
        );
        Workflow? lastUpdatedWorkflow;

        await tester.pumpWidget(
          StatefulBuilder(
            builder: (context, setState) {
              return buildTestApp(
                currentWorkflow,
                onChanged: (updated) {
                  lastUpdatedWorkflow = updated;
                  setState(() {
                    currentWorkflow = updated;
                  });
                },
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        // Tap the 0% (Free) preset chip
        final freeChip = find.widgetWithText(ChoiceChip, '0% Free');
        expect(freeChip, findsOneWidget);
        await tester.tap(freeChip);
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.defaultStrictnessLevel, 0);
        expect(find.text('0%'), findsWidgets);

        // Tap the 85% (Strict) preset chip for scoring
        final strictChip = find.widgetWithText(ChoiceChip, '85% Strict').first;
        expect(strictChip, findsOneWidget);
        await tester.tap(strictChip);
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.defaultStrictnessLevel, 85);
        expect(find.text('85%'), findsWidgets);

        // Tap the 100% (Absolute) preset chip for scoring
        final absoluteChip = find
            .widgetWithText(ChoiceChip, '100% Absolute')
            .first;
        expect(absoluteChip, findsOneWidget);
        await tester.tap(absoluteChip);
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.defaultStrictnessLevel, 100);
        expect(find.text('100%'), findsWidgets);
      },
    );

    testWidgets(
      'test_workflow_strictness_tab_tapping_lexical_preset_chips_updates_workflow',
      (WidgetTester tester) async {
        Workflow currentWorkflow = createTestWorkflow(
          defaultStrictnessLevel: 50,
          defaultLexicalStrictnessLevel: 50,
        );
        Workflow? lastUpdatedWorkflow;

        await tester.pumpWidget(
          StatefulBuilder(
            builder: (context, setState) {
              return buildTestApp(
                currentWorkflow,
                onChanged: (updated) {
                  lastUpdatedWorkflow = updated;
                  setState(() {
                    currentWorkflow = updated;
                  });
                },
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        // Tap the 0% (Flexible) preset chip
        final flexibleChip = find.widgetWithText(ChoiceChip, '0% Flexible');
        expect(flexibleChip, findsOneWidget);
        await tester.tap(flexibleChip);
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.defaultLexicalStrictnessLevel, 0);

        // Tap the 85% (Strict) preset chip for lexical
        final strictChip = find.widgetWithText(ChoiceChip, '85% Strict').last;
        await tester.tap(strictChip);
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.defaultLexicalStrictnessLevel, 85);

        // Tap the 100% (Absolute) preset chip for lexical
        final absoluteChip = find
            .widgetWithText(ChoiceChip, '100% Absolute')
            .last;
        await tester.tap(absoluteChip);
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.defaultLexicalStrictnessLevel, 100);
      },
    );

    testWidgets(
      'test_workflow_strictness_tab_displays_consequences_across_all_4_zones',
      (WidgetTester tester) async {
        // Zone 1: Free (0%)
        final wf0 = createTestWorkflow(
          defaultStrictnessLevel: 0,
          defaultLexicalStrictnessLevel: 50,
        );
        await tester.pumpWidget(buildTestApp(wf0));
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.info_outline), findsOneWidget);

        // Zone 2: Normal (50%)
        final wf50 = createTestWorkflow(
          defaultStrictnessLevel: 50,
          defaultLexicalStrictnessLevel: 0,
        );
        await tester.pumpWidget(buildTestApp(wf50));
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.check_circle_outline), findsOneWidget);

        // Zone 3: Strict (85%)
        final wf85 = createTestWorkflow(
          defaultStrictnessLevel: 85,
          defaultLexicalStrictnessLevel: 0,
        );
        await tester.pumpWidget(buildTestApp(wf85));
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.shield_outlined), findsOneWidget);

        // Zone 4: Absolute (100%)
        final wf100 = createTestWorkflow(
          defaultStrictnessLevel: 100,
          defaultLexicalStrictnessLevel: 0,
        );
        await tester.pumpWidget(buildTestApp(wf100));
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      },
    );

    testWidgets('test_workflow_strictness_tab_fi_locale_360px_no_overflow', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(360, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      final workflow = createTestWorkflow(
        defaultStrictnessLevel: 85,
        defaultLexicalStrictnessLevel: 85,
      );
      await tester.pumpWidget(
        buildTestApp(workflow, locale: const Locale('fi')),
      );
      await tester.pumpAndSettle();

      expect(find.byType(Slider), findsNWidgets(2));
      expect(find.text('85%'), findsWidgets);
      expect(find.text('Pisteytyksen ankaruustaso'), findsOneWidget);
      expect(
        find.text('Leksikaalisen tarkistuksen tiukkuustaso'),
        findsOneWidget,
      );
      expect(find.text('85% Tiukka'), findsNWidgets(2));
      expect(find.text('Automaattiset pistevähennykset'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(3));
      expect(tester.takeException(), isNull);
    });

    testWidgets(
      'test_workflow_strictness_tab_renders_penalty_inputs_and_updates_workflow',
      (WidgetTester tester) async {
        Workflow currentWorkflow = createTestWorkflow(
          defaultStrictnessLevel: 50,
        );
        Workflow? lastUpdatedWorkflow;

        await tester.pumpWidget(
          StatefulBuilder(
            builder: (context, setState) {
              return buildTestApp(
                currentWorkflow,
                onChanged: (updated) {
                  lastUpdatedWorkflow = updated;
                  setState(() {
                    currentWorkflow = updated;
                  });
                },
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        // Verify penalties Card and 3 TextFormFields are rendered
        expect(find.text('Automated Score Penalties'), findsOneWidget);
        expect(find.byType(TextFormField), findsNWidgets(3));
        expect(find.text('Security Penalty (%)'), findsOneWidget);
        expect(find.text('Post-Hoc Penalty (%)'), findsOneWidget);
        expect(find.text('Passivity Penalty (%)'), findsOneWidget);

        // Enter 15 into security penalty input
        final securityInput = find.widgetWithText(
          TextFormField,
          'Security Penalty (%)',
        );
        await tester.enterText(securityInput, '15');
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.securityPenalty, 0.15);

        // Enter 20 into post-hoc penalty input
        final postHocInput = find.widgetWithText(
          TextFormField,
          'Post-Hoc Penalty (%)',
        );
        await tester.enterText(postHocInput, '20');
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.postHocPenalty, 0.20);

        // Enter 5 into passivity penalty input
        final passivityInput = find.widgetWithText(
          TextFormField,
          'Passivity Penalty (%)',
        );
        await tester.enterText(passivityInput, '5');
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.passivityPenalty, 0.05);

        // Clear security penalty input to empty string -> should reset to 0.0
        await tester.enterText(securityInput, '');
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.securityPenalty, 0.0);

        // Enter out-of-bounds input (e.g. 150) -> should be rejected and not update
        await tester.enterText(securityInput, '150');
        await tester.pumpAndSettle();

        expect(lastUpdatedWorkflow?.securityPenalty, 0.0);
      },
    );
  });
}
