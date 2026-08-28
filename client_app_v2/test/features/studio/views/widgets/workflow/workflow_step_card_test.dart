import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_step_card.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('WorkflowStepCard 3-Zone Management Tests', () {
    late List<NodeStrategy> mockBlueprints;
    late List<ExpectedInput> mockGlobalInputs;

    setUp(() {
      mockBlueprints = [
        const NodeStrategy.logic(
          id: 'sp_db849f9790984585',
          slug: 'input_processing',
          name: I18nText(
            translations: {
              'en': 'Input Processing & Decomposition',
              'fi': 'Syötteiden käsittely ja purku',
            },
          ),
          hook: 'process_inputs',
          isSystemCore: true,
        ),
        const NodeStrategy.llm(
          id: 'sp_agent_specialist_1',
          slug: 'senior_executive_coach',
          name: I18nText(
            translations: {
              'en': 'Senior Executive Coach',
              'fi': 'Johtamisen asiantuntija',
            },
          ),
          modelStrategy: 'fast',
          isSystemCore: false,
        ),
        const NodeStrategy.llm(
          id: 'sp_agent_specialist_2',
          slug: 'strategy_analyst',
          name: I18nText(
            translations: {
              'en': 'Strategy Analyst',
              'fi': 'Strategia-analyytikko',
            },
          ),
          modelStrategy: 'fast',
          isSystemCore: false,
        ),
        const NodeStrategy.logic(
          id: 'sp_192910b5f5a34c79',
          slug: 'xai_reporter',
          name: I18nText(
            translations: {
              'en': 'XAI Reporter & Aggregator',
              'fi': 'XAI Raportointi & Koonti',
            },
          ),
          hook: 'aggregate_xai',
          isSystemCore: true,
        ),
      ];

      mockGlobalInputs = [
        const ExpectedInput(
          inputKey: 'source_documents',
          label: I18nText(
            translations: {'en': 'Source Documents', 'fi': 'Lähdedokumentit'},
          ),
          description: I18nText(
            translations: {
              'en': 'Primary source materials',
              'fi': 'Ensisijaiset lähdemateriaalit',
            },
          ),
          required: true,
        ),
        const ExpectedInput(
          inputKey: 'interview_notes',
          label: I18nText(
            translations: {
              'en': 'Interview Notes',
              'fi': 'Haastattelumuistiinpanot',
            },
          ),
          description: I18nText(
            translations: {
              'en': 'Interview summaries',
              'fi': 'Haastattelujen yhteenvedot',
            },
          ),
          required: false,
        ),
      ];
    });

    Widget createTestWidget({
      required int index,
      required StepRule stepDef,
      required List<StepRule> allSteps,
      Function(StepRule)? onChanged,
      VoidCallback? onDelete,
      Locale locale = const Locale('fi'),
    }) {
      return MaterialApp(
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: Builder(
              builder: (context) {
                final l10n = AppLocalizations.of(context)!;
                return WorkflowStepCard(
                  index: index,
                  stepDef: stepDef,
                  blueprints: mockBlueprints,
                  allSteps: allSteps,
                  mcpGateways: const [],
                  globalWorkflowInputs: mockGlobalInputs,
                  l10n: l10n,
                  onChanged: onChanged ?? (_) {},
                  onDelete: onDelete ?? () {},
                );
              },
            ),
          ),
        ),
      );
    }

    // Positive 1: Zone A (Step 1 - Input Processing)
    testWidgets(
      'Zone A (Step 1) hides delete button, displays system core badge, and renders raw ingestion badge',
      (WidgetTester tester) async {
        final step1 = const StepRule(
          id: 'sr_f0a26d17cc9b48a7',
          taskBlueprint: 'sp_db849f9790984585',
          isSynthesisSource: false,
        );

        await tester.pumpWidget(
          createTestWidget(index: 0, stepDef: step1, allSteps: [step1]),
        );
        await tester.pumpAndSettle();

        // 1. Delete button should NOT be rendered in Zone A
        expect(find.byIcon(Icons.delete), findsNothing);

        // 2. System Core badge should be visible
        expect(
          find.text('🔒 Järjestelmän perusaskel (Suojattu)'),
          findsOneWidget,
        );

        // 3. Blueprint dropdown is locked/display-only
        expect(find.byType(DropdownButtonFormField<String>), findsNothing);
        expect(find.text('Syötteiden käsittely ja purku'), findsOneWidget);

        // 4. Zone A raw ingestion container content
        expect(
          find.text('Syötenäytöllä määritetyt raakatiedostot (PDF, DOCX)'),
          findsOneWidget,
        );
        expect(
          find.text('✨ Muuntaa tiedostot puretuiksi atomeiksi loppuketjulle.'),
          findsOneWidget,
        );
      },
    );

    // Positive 2: Zone B (Steps 2..N - Dynamic Specialists)
    testWidgets(
      'Zone B renders delete button, filtered blueprint dropdown, and dual categorized scope sections',
      (WidgetTester tester) async {
        final step1 = const StepRule(
          id: 'sr_step1',
          taskBlueprint: 'sp_db849f9790984585',
          isSynthesisSource: false,
        );
        final step2 = const StepRule(
          id: 'sr_step2',
          taskBlueprint: 'sp_agent_specialist_1',
          dependsOn: ['sr_step1'],
          inputMappings: {'source_documents': r'$inputs.source_documents'},
          isSynthesisSource: true,
        );

        bool deleteTriggered = false;

        await tester.pumpWidget(
          createTestWidget(
            index: 1,
            stepDef: step2,
            allSteps: [step1, step2],
            onDelete: () => deleteTriggered = true,
          ),
        );
        await tester.pumpAndSettle();

        // 1. Delete button should be visible and clickable in Zone B
        expect(find.byIcon(Icons.delete), findsOneWidget);
        await tester.tap(find.byIcon(Icons.delete));
        expect(deleteTriggered, isTrue);

        // 2. System Core badge should NOT be shown
        expect(
          find.text('🔒 Järjestelmän perusaskel (Suojattu)'),
          findsNothing,
        );

        // 3. Dropdown should be interactive
        expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);

        // 4. Execution Order & Dependencies section
        expect(find.text('Suoritusjärjestys & Riippuvuudet'), findsOneWidget);
        expect(find.byType(FilterChip), findsOneWidget);

        // 5. Categorized Section 1: Atomized materials
        expect(
          find.text('Atomisoidut aineistot (Valitse analysoitavat sisällöt)'),
          findsOneWidget,
        );
        expect(find.text('Syöte: Lähdedokumentit'), findsOneWidget);

        // 6. Categorized Section 2: Prior step reports
        expect(
          find.text('Edeltävien askeleiden kontekstiankkurointi (Valinnainen)'),
          findsOneWidget,
        );
        expect(
          find.text('Askel: Syötteiden käsittely ja purku'),
          findsOneWidget,
        );
      },
    );

    // Positive 3: Zone C (Pipeline Funnel Anchors)
    testWidgets(
      'Zone C renders locked system core funnel with XAI aggregator badge and zero manual inputs',
      (WidgetTester tester) async {
        final step1 = const StepRule(
          id: 'sr_step1',
          taskBlueprint: 'sp_db849f9790984585',
          isSynthesisSource: false,
        );
        final step2 = const StepRule(
          id: 'sr_step2',
          taskBlueprint: 'sp_agent_specialist_1',
          dependsOn: ['sr_step1'],
          isSynthesisSource: true,
        );
        final step3 = const StepRule(
          id: 'sr_step3',
          taskBlueprint:
              'sp_192910b5f5a34c79', // XAI Reporter (isSystemCore: true, index > 0)
          dependsOn: ['sr_step2'],
          isSynthesisSource: true,
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 2,
            stepDef: step3,
            allSteps: [step1, step2, step3],
          ),
        );
        await tester.pumpAndSettle();

        // 1. Delete button hidden for Zone C
        expect(find.byIcon(Icons.delete), findsNothing);

        // 2. System Core badge visible
        expect(
          find.text('🔒 Järjestelmän perusaskel (Suojattu)'),
          findsOneWidget,
        );

        // 3. Dropdown locked/display-only
        expect(find.byType(DropdownButtonFormField<String>), findsNothing);
        expect(find.text('XAI Raportointi & Koonti'), findsOneWidget);

        // 4. Zone C aggregate content rendered
        expect(
          find.text('Automaattinen järjestelmäankkuri (Suojattu)'),
          findsOneWidget,
        );
        expect(
          find.text(
            '⚡ Automaattinen koonti: Kokoaa automaattisesti kaikki yllä määritellyt työnkulun asiantuntijat.',
          ),
          findsOneWidget,
        );

        // 5. Zero manual input checkboxes in Zone C
        expect(find.byType(CheckboxListTile), findsNothing);
      },
    );

    // Positive 4: Localized resolution via I18nText
    testWidgets(
      'Resolves English localization cleanly when English locale is active',
      (WidgetTester tester) async {
        final step1 = const StepRule(
          id: 'sr_step1',
          taskBlueprint: 'sp_db849f9790984585',
          isSynthesisSource: false,
        );
        final step2 = const StepRule(
          id: 'sr_step2',
          taskBlueprint: 'sp_agent_specialist_1',
          dependsOn: ['sr_step1'],
          inputMappings: {'source_documents': r'$inputs.source_documents'},
          isSynthesisSource: true,
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 1,
            stepDef: step2,
            allSteps: [step1, step2],
            locale: const Locale('en'),
          ),
        );
        await tester.pumpAndSettle();

        // English headers
        expect(find.text('Execution Order & Dependencies'), findsOneWidget);
        expect(
          find.text('Atomized Materials (Select Analyzed Contents)'),
          findsOneWidget,
        );
        expect(find.text('Input: Source Documents'), findsOneWidget);
        expect(
          find.text('Step: Input Processing & Decomposition'),
          findsOneWidget,
        );
      },
    );

    // Positive 5: TextOverflow.ellipsis prevents horizontal overflow on long IDs and labels
    testWidgets(
      'Renders long IDs and long blueprint labels with TextOverflow.ellipsis without overflow exceptions',
      (WidgetTester tester) async {
        final veryLongId =
            'sr_extremely_long_opaque_identifier_that_would_overflow_screen_1234567890';
        final longStep = StepRule(
          id: veryLongId,
          taskBlueprint: 'sp_agent_specialist_1',
          dependsOn: const [],
          isSynthesisSource: true,
        );

        await tester.pumpWidget(
          createTestWidget(index: 1, stepDef: longStep, allSteps: [longStep]),
        );
        await tester.pumpAndSettle();

        // Check that selectable text contains the long ID
        expect(find.text(veryLongId), findsOneWidget);
        expect(tester.takeException(), isNull);
      },
    );

    // Negative ISTQB 1: Zone B blueprint dropdown excludes system core blueprints
    testWidgets(
      'Negative ISTQB: Zone B blueprint dropdown never contains system core blueprints',
      (WidgetTester tester) async {
        final step1 = const StepRule(
          id: 'sr_step1',
          taskBlueprint: 'sp_db849f9790984585',
          isSynthesisSource: false,
        );
        final step2 = const StepRule(
          id: 'sr_step2',
          taskBlueprint: 'sp_agent_specialist_1',
          dependsOn: ['sr_step1'],
          isSynthesisSource: true,
        );

        await tester.pumpWidget(
          createTestWidget(index: 1, stepDef: step2, allSteps: [step1, step2]),
        );
        await tester.pumpAndSettle();

        final dropdownFinder = find.byType(DropdownButtonFormField<String>);
        expect(dropdownFinder, findsOneWidget);

        await tester.tap(dropdownFinder);
        await tester.pumpAndSettle();

        // Scoped check inside DropdownMenuItem widgets to ensure system core items are excluded
        final dropdownMenuItemFinder = find.descendant(
          of: find.byType(DropdownMenuItem<String>),
          matching: find.byType(Text),
        );
        final dropdownTextWidgets = tester
            .widgetList<Text>(dropdownMenuItemFinder)
            .map((t) => t.data)
            .toList();

        expect(dropdownTextWidgets, contains('Johtamisen asiantuntija'));
        expect(dropdownTextWidgets, contains('Strategia-analyytikko'));
        expect(
          dropdownTextWidgets,
          isNot(contains('Syötteiden käsittely ja purku')),
        );
        expect(
          dropdownTextWidgets,
          isNot(contains('XAI Raportointi & Koonti')),
        );
      },
    );

    // Negative ISTQB 2: Delete callback is not triggerable for Zone A or Zone C
    testWidgets(
      'Negative ISTQB: Delete callback is absent and cannot be triggered on Zone A or Zone C steps',
      (WidgetTester tester) async {
        bool deleteAttempted = false;

        // Test Zone A (index == 0)
        final step1 = const StepRule(
          id: 'sr_step1',
          taskBlueprint: 'sp_db849f9790984585',
          isSynthesisSource: false,
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 0,
            stepDef: step1,
            allSteps: [step1],
            onDelete: () => deleteAttempted = true,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.delete), findsNothing);
        expect(deleteAttempted, isFalse);

        // Test Zone C (isSystemCore == true && index > 0)
        final step3 = const StepRule(
          id: 'sr_step3',
          taskBlueprint: 'sp_192910b5f5a34c79',
          isSynthesisSource: true,
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 2,
            stepDef: step3,
            allSteps: [step1, step3],
            onDelete: () => deleteAttempted = true,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.delete), findsNothing);
        expect(deleteAttempted, isFalse);
      },
    );
  });
}
