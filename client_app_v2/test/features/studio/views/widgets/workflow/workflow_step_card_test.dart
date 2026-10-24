import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
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
          zone: StepZone.zoneA,
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
          cognitiveTier: CognitiveTier.fast,
          isSystemCore: false,
          zone: StepZone.zoneB,
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
          cognitiveTier: CognitiveTier.fast,
          isSystemCore: false,
          zone: StepZone.zoneB,
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
          zone: StepZone.zoneC,
        ),
        const NodeStrategy.causalDiscovery(
          id: 'sp_causal_discovery_1',
          slug: 'causal_discovery_1',
          name: I18nText(
            translations: {
              'en': 'Causal Discovery Alpha',
              'fi': 'Kausaalipäättely Alfa',
            },
          ),
          engineType: EngineType.causalDiscovery,
          zone: StepZone.zoneB,
        ),
        const NodeStrategy.causalDiscovery(
          id: 'sp_causal_discovery_2',
          slug: 'causal_discovery_2',
          name: I18nText(
            translations: {
              'en': 'Causal Discovery Beta',
              'fi': 'Kausaalipäättely Beta',
            },
          ),
          engineType: EngineType.causalDiscovery,
          zone: StepZone.zoneB,
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
      VoidCallback? onCopy,
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
                  onCopy: onCopy,
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

        // 1. Delete and copy buttons should NOT be rendered in Zone A
        expect(find.byIcon(Icons.delete), findsNothing);
        expect(find.byIcon(Icons.copy), findsNothing);

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

    testWidgets(
      'Zone B renders copy button, triggers onCopy when clicked, and copy button is hidden in Zone A and Zone C',
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
          taskBlueprint: 'sp_192910b5f5a34c79', // System core
          dependsOn: ['sr_step2'],
          isSynthesisSource: true,
        );

        // 1. Zone A: copy button hidden
        await tester.pumpWidget(
          createTestWidget(
            index: 0,
            stepDef: step1,
            allSteps: [step1, step2, step3],
          ),
        );
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.copy), findsNothing);

        // 2. Zone B: copy button rendered and clickable
        bool copyTriggered = false;
        await tester.pumpWidget(
          createTestWidget(
            index: 1,
            stepDef: step2,
            allSteps: [step1, step2, step3],
            onCopy: () => copyTriggered = true,
          ),
        );
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.copy), findsOneWidget);
        await tester.tap(find.byIcon(Icons.copy));
        expect(copyTriggered, isTrue);

        // 3. Zone C: copy button hidden
        await tester.pumpWidget(
          createTestWidget(
            index: 2,
            stepDef: step3,
            allSteps: [step1, step2, step3],
          ),
        );
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.copy), findsNothing);
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

        // 1. Delete and copy buttons hidden for Zone C
        expect(find.byIcon(Icons.delete), findsNothing);
        expect(find.byIcon(Icons.copy), findsNothing);

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

        // Test Zone C (currentBlueprint.zone == StepZone.zoneC renders automated anchor box and suppresses deletion)
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

        final l10n = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10n.studioWorkflowZoneCAutoTitle), findsOneWidget);
      },
    );

    group('Specialist Causal Source Selector & Full-Duplex Reactive Sync Tests', () {
      testWidgets(
        'Renders DropdownButtonFormField for causal source when upstream causal discovery steps exist, excluding causal steps themselves',
        (WidgetTester tester) async {
          final stepInput = const StepRule(
            id: 'sr_step1',
            taskBlueprint: 'sp_db849f9790984585',
            isSynthesisSource: false,
          );
          final stepCausal = const StepRule(
            id: 'sr_causal_alpha',
            taskBlueprint: 'sp_causal_discovery_1',
            dependsOn: ['sr_step1'],
            isSynthesisSource: false,
          );
          final stepSpecialist = const StepRule(
            id: 'sr_specialist_coach',
            taskBlueprint: 'sp_agent_specialist_1',
            dependsOn: ['sr_step1', 'sr_causal_alpha'],
            causalSourceStepId: 'sr_causal_alpha',
            isSynthesisSource: true,
          );

          // 1. Verify causal step itself (index 1) does NOT render the causal source selector
          await tester.pumpWidget(
            createTestWidget(
              index: 1,
              stepDef: stepCausal,
              allSteps: [stepInput, stepCausal, stepSpecialist],
            ),
          );
          await tester.pumpAndSettle();
          expect(find.byType(DropdownButtonFormField<String?>), findsNothing);

          // 2. Verify specialist step (index 2) DOES render the causal source selector with items
          await tester.pumpWidget(
            createTestWidget(
              index: 2,
              stepDef: stepSpecialist,
              allSteps: [stepInput, stepCausal, stepSpecialist],
            ),
          );
          await tester.pumpAndSettle();

          final causalDropdownFinder = find.byType(
            DropdownButtonFormField<String?>,
          );
          expect(causalDropdownFinder, findsOneWidget);

          // Tap dropdown to verify items
          await tester.tap(causalDropdownFinder);
          await tester.pumpAndSettle();

          final menuItemFinder = find.descendant(
            of: find.byType(DropdownMenuItem<String?>),
            matching: find.byType(Text),
          );
          final menuItemTexts = tester
              .widgetList<Text>(menuItemFinder)
              .map((t) => t.data)
              .toList();

          expect(menuItemTexts, contains('Ei käytössä'));
          expect(menuItemTexts, contains('Kausaalipäättely Alfa'));
        },
      );

      testWidgets(
        'Defensive value guard resolves malformed/non-upstream causal source ID safely to null without crashing',
        (WidgetTester tester) async {
          final stepInput = const StepRule(
            id: 'sr_step1',
            taskBlueprint: 'sp_db849f9790984585',
            isSynthesisSource: false,
          );
          final stepCausal = const StepRule(
            id: 'sr_causal_alpha',
            taskBlueprint: 'sp_causal_discovery_1',
            dependsOn: ['sr_step1'],
            isSynthesisSource: false,
          );
          // Malformed step referencing non-existent or downstream causal source
          final stepSpecialistMalformed = const StepRule(
            id: 'sr_specialist_coach',
            taskBlueprint: 'sp_agent_specialist_1',
            dependsOn: ['sr_step1'],
            causalSourceStepId: 'sr_corrupted_id_9999',
            isSynthesisSource: true,
          );

          await tester.pumpWidget(
            createTestWidget(
              index: 2,
              stepDef: stepSpecialistMalformed,
              allSteps: [stepInput, stepCausal, stepSpecialistMalformed],
            ),
          );
          await tester.pumpAndSettle();

          // Must render cleanly without throwing Flutter assertion errors
          final causalDropdownFinder = find.byType(
            DropdownButtonFormField<String?>,
          );
          expect(causalDropdownFinder, findsOneWidget);

          // Verify initialValue safely rendered as None ('Ei käytössä')
          expect(find.text('Ei käytössä'), findsOneWidget);
        },
      );

      testWidgets(
        'Full-Duplex Reactive Sync: swapping causal source from Step A to Step B prunes Step A from dependsOn and appends Step B',
        (WidgetTester tester) async {
          final stepInput = const StepRule(
            id: 'sr_step1',
            taskBlueprint: 'sp_db849f9790984585',
            isSynthesisSource: false,
          );
          final stepCausalA = const StepRule(
            id: 'sr_causal_alpha',
            taskBlueprint: 'sp_causal_discovery_1',
            dependsOn: ['sr_step1'],
            isSynthesisSource: false,
          );
          final stepCausalB = const StepRule(
            id: 'sr_causal_beta',
            taskBlueprint: 'sp_causal_discovery_2',
            dependsOn: ['sr_step1'],
            isSynthesisSource: false,
          );
          final stepSpecialist = const StepRule(
            id: 'sr_specialist_coach',
            taskBlueprint: 'sp_agent_specialist_1',
            dependsOn: ['sr_step1', 'sr_causal_alpha'],
            causalSourceStepId: 'sr_causal_alpha',
            isSynthesisSource: true,
          );

          StepRule? updatedStep;

          await tester.pumpWidget(
            createTestWidget(
              index: 3,
              stepDef: stepSpecialist,
              allSteps: [stepInput, stepCausalA, stepCausalB, stepSpecialist],
              onChanged: (step) => updatedStep = step,
            ),
          );
          await tester.pumpAndSettle();

          final causalDropdownFinder = find.byType(
            DropdownButtonFormField<String?>,
          );
          expect(causalDropdownFinder, findsOneWidget);

          // Open dropdown and tap 'Kausaalipäättely Beta'
          await tester.tap(causalDropdownFinder);
          await tester.pumpAndSettle();

          await tester.tap(find.text('Kausaalipäättely Beta').last);
          await tester.pumpAndSettle();

          expect(updatedStep, isNotNull);
          expect(updatedStep!.causalSourceStepId, equals('sr_causal_beta'));
          expect(updatedStep!.dependsOn.contains('sr_causal_alpha'), isFalse);
          expect(updatedStep!.dependsOn.contains('sr_causal_beta'), isTrue);
          expect(
            updatedStep!.dependsOn,
            equals(['sr_step1', 'sr_causal_beta']),
          );
        },
      );

      testWidgets(
        'Full-Duplex Reactive Sync: selecting None in causal dropdown resets causalSourceStepId to null and removes causal step from dependsOn',
        (WidgetTester tester) async {
          final stepInput = const StepRule(
            id: 'sr_step1',
            taskBlueprint: 'sp_db849f9790984585',
            isSynthesisSource: false,
          );
          final stepCausalA = const StepRule(
            id: 'sr_causal_alpha',
            taskBlueprint: 'sp_causal_discovery_1',
            dependsOn: ['sr_step1'],
            isSynthesisSource: false,
          );
          final stepSpecialist = const StepRule(
            id: 'sr_specialist_coach',
            taskBlueprint: 'sp_agent_specialist_1',
            dependsOn: ['sr_step1', 'sr_causal_alpha'],
            causalSourceStepId: 'sr_causal_alpha',
            isSynthesisSource: true,
          );

          StepRule? updatedStep;

          await tester.pumpWidget(
            createTestWidget(
              index: 2,
              stepDef: stepSpecialist,
              allSteps: [stepInput, stepCausalA, stepSpecialist],
              onChanged: (step) => updatedStep = step,
            ),
          );
          await tester.pumpAndSettle();

          final causalDropdownFinder = find.byType(
            DropdownButtonFormField<String?>,
          );
          expect(causalDropdownFinder, findsOneWidget);

          // Open dropdown and tap 'Ei käytössä'
          await tester.tap(causalDropdownFinder);
          await tester.pumpAndSettle();

          await tester.tap(find.text('Ei käytössä').last);
          await tester.pumpAndSettle();

          expect(updatedStep, isNotNull);
          expect(updatedStep!.causalSourceStepId, isNull);
          expect(updatedStep!.dependsOn.contains('sr_causal_alpha'), isFalse);
          expect(updatedStep!.dependsOn, equals(['sr_step1']));
        },
      );

      testWidgets(
        'Full-Duplex Reactive Sync: deselecting dependency chip matching active causal source auto-resets causalSourceStepId to null',
        (WidgetTester tester) async {
          final stepInput = const StepRule(
            id: 'sr_step1',
            taskBlueprint: 'sp_db849f9790984585',
            isSynthesisSource: false,
          );
          final stepCausalA = const StepRule(
            id: 'sr_causal_alpha',
            taskBlueprint: 'sp_causal_discovery_1',
            dependsOn: ['sr_step1'],
            isSynthesisSource: false,
          );
          final stepSpecialist = const StepRule(
            id: 'sr_specialist_coach',
            taskBlueprint: 'sp_agent_specialist_1',
            dependsOn: ['sr_step1', 'sr_causal_alpha'],
            causalSourceStepId: 'sr_causal_alpha',
            isSynthesisSource: true,
          );

          StepRule? updatedStep;

          await tester.pumpWidget(
            createTestWidget(
              index: 2,
              stepDef: stepSpecialist,
              allSteps: [stepInput, stepCausalA, stepSpecialist],
              onChanged: (step) => updatedStep = step,
            ),
          );
          await tester.pumpAndSettle();

          // Find the FilterChip for 'Kausaalipäättely Alfa' (sr_causal_alpha)
          final causalChipFinder = find.widgetWithText(
            FilterChip,
            'Kausaalipäättely Alfa',
          );
          expect(causalChipFinder, findsOneWidget);

          // Tap the chip to deselect it
          await tester.tap(causalChipFinder);
          await tester.pumpAndSettle();

          expect(updatedStep, isNotNull);
          // Must have pruned sr_causal_alpha from dependsOn
          expect(updatedStep!.dependsOn.contains('sr_causal_alpha'), isFalse);
          expect(updatedStep!.dependsOn, equals(['sr_step1']));
          // Must have automatically reset causalSourceStepId to null to prevent 422 crash!
          expect(updatedStep!.causalSourceStepId, isNull);
        },
      );
    });
  });
}
