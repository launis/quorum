import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_step_card.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('WorkflowStepCard Dumb Painter & Zone Decoupling Tests', () {
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
        const NodeStrategy.causalDiscovery(
          id: 'sp_c4a5a1d15c00438a',
          slug: 'step_causal_discovery',
          name: I18nText(
            translations: {
              'en': 'Dynamic Causal Discovery & Argument Mining',
              'fi': 'Kausaalipäättelyn ja Argumentaation Louhinta',
            },
          ),
          isSystemCore: true,
          engineType: EngineType.causalDiscovery,
          zone: StepZone.zoneB,
        ),
        const NodeStrategy.llm(
          id: 'sp_specialist_coach',
          slug: 'executive_coach',
          name: I18nText(
            translations: {
              'en': 'Executive Coach',
              'fi': 'Johtamisen valmentaja',
            },
          ),
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
      ];

      mockGlobalInputs = [
        const ExpectedInput(
          inputKey: 'product_text',
          label: I18nText(
            translations: {'en': 'Product Text', 'fi': 'Tuoteteksti'},
          ),
          description: I18nText(
            translations: {'en': 'Product details', 'fi': 'Tuotetiedot'},
          ),
          required: true,
        ),
      ];
    });

    Widget createTestWidget({
      required int index,
      required StepRule stepDef,
      required List<StepRule> allSteps,
      List<NodeStrategy>? customBlueprints,
      Function(StepRule)? onChanged,
      VoidCallback? onDelete,
      VoidCallback? onCopy,
      Locale locale = const Locale('en'),
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
                  blueprints: customBlueprints ?? mockBlueprints,
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

    testWidgets(
      'Protected system core step in Zone B (Causal Discovery sp_c4a5a1d15c00438a) renders system core badge and Zone B specialist controls instead of Zone C anchor box',
      (WidgetTester tester) async {
        final stepInput = const StepRule(
          id: 'sr_input_01',
          taskBlueprint: 'sp_db849f9790984585',
        );
        final stepCausal = const StepRule(
          id: 'sr_causal_01',
          taskBlueprint: 'sp_c4a5a1d15c00438a',
          dependsOn: ['sr_input_01'],
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 1,
            stepDef: stepCausal,
            allSteps: [stepInput, stepCausal],
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        // 1. Renders system core badge
        expect(find.text(l10n.studioSystemCoreBadge), findsOneWidget);

        // 2. Action lock: deletes and clone buttons are suppressed
        expect(find.byIcon(Icons.delete), findsNothing);
        expect(find.byIcon(Icons.copy), findsNothing);

        // 3. Task profile dropdown is locked to static text
        expect(find.byType(DropdownButtonFormField<String>), findsNothing);
        expect(
          find.text('Dynamic Causal Discovery & Argument Mining'),
          findsOneWidget,
        );

        // 4. Critically: renders Zone B Execution Order & Dependencies instead of Zone C automated anchor box
        expect(
          find.text(l10n.studioWorkflowExecutionOrderTitle),
          findsOneWidget,
        );
        expect(find.text(l10n.studioWorkflowZoneCAutoTitle), findsNothing);
        expect(find.text(l10n.studioWorkflowStep1IngestionTitle), findsNothing);
      },
    );

    testWidgets(
      'Protected system core step in Zone A (Input Processing) renders system core badge and Zone A input ingestion box',
      (WidgetTester tester) async {
        final stepInput = const StepRule(
          id: 'sr_input_01',
          taskBlueprint: 'sp_db849f9790984585',
        );

        await tester.pumpWidget(
          createTestWidget(index: 0, stepDef: stepInput, allSteps: [stepInput]),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        // 1. Renders system core badge
        expect(find.text(l10n.studioSystemCoreBadge), findsOneWidget);

        // 2. Action lock
        expect(find.byIcon(Icons.delete), findsNothing);
        expect(find.byIcon(Icons.copy), findsNothing);

        // 3. Renders Zone A Input Ingestion Anchor
        expect(
          find.text(l10n.studioWorkflowStep1IngestionTitle),
          findsOneWidget,
        );

        // 4. Suppresses Zone B and Zone C elements
        expect(find.text(l10n.studioWorkflowExecutionOrderTitle), findsNothing);
        expect(find.text(l10n.studioWorkflowZoneCAutoTitle), findsNothing);
      },
    );

    testWidgets(
      'Protected system core step in Zone C (XAI Reporter) renders system core badge and Zone C automated anchor box',
      (WidgetTester tester) async {
        final stepInput = const StepRule(
          id: 'sr_input_01',
          taskBlueprint: 'sp_db849f9790984585',
        );
        final stepXai = const StepRule(
          id: 'sr_xai_01',
          taskBlueprint: 'sp_192910b5f5a34c79',
          dependsOn: ['sr_input_01'],
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 1,
            stepDef: stepXai,
            allSteps: [stepInput, stepXai],
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        // 1. Renders system core badge
        expect(find.text(l10n.studioSystemCoreBadge), findsOneWidget);

        // 2. Action lock
        expect(find.byIcon(Icons.delete), findsNothing);
        expect(find.byIcon(Icons.copy), findsNothing);

        // 3. Renders Zone C Automated Anchor box
        expect(find.text(l10n.studioWorkflowZoneCAutoTitle), findsOneWidget);

        // 4. Suppresses Zone A and Zone B elements
        expect(find.text(l10n.studioWorkflowStep1IngestionTitle), findsNothing);
        expect(find.text(l10n.studioWorkflowExecutionOrderTitle), findsNothing);
      },
    );

    testWidgets(
      'Unmapped or missing blueprint fails gracefully without throwing unhandled index assertion errors',
      (WidgetTester tester) async {
        final stepUnmapped = const StepRule(
          id: 'sr_unmapped_01',
          taskBlueprint: 'sp_unknown_orphan_blueprint',
        );

        await tester.pumpWidget(
          createTestWidget(
            index: 0,
            stepDef: stepUnmapped,
            allSteps: [stepUnmapped],
          ),
        );
        await tester.pumpAndSettle();

        // 1. Zero unhandled exceptions
        expect(tester.takeException(), isNull);

        // 2. Renders step identifier
        expect(find.text('sr_unmapped_01'), findsOneWidget);

        // 3. Dropdown renders safely with null selection preventing Flutter assertion crashes
        expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);

        // 4. Not marked as system core: delete button is available
        expect(find.byIcon(Icons.delete), findsOneWidget);
      },
    );
  });
}
