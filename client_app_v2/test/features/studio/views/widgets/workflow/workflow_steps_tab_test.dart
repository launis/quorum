import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_steps_tab.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_step_card.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('WorkflowStepsTab Widget & Step Symmetry Tests', () {
    late List<NodeStrategy> mockBlueprints;
    late Workflow mockWorkflow;

    setUp(() {
      mockBlueprints = [
        const NodeStrategy.logic(
          id: 'sp_input_processing',
          slug: 'input_processing',
          name: I18nText(
            translations: {
              'en': 'Input Processing',
              'fi': 'Syötteiden käsittely',
            },
          ),
          hook: 'process_inputs',
          isSystemCore: true,
          engineType: EngineType.prompt,
          zone: StepZone.zoneA,
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
          engineType: EngineType.prompt,
          zone: StepZone.zoneB,
        ),
        const NodeStrategy.causalDiscovery(
          id: 'sp_causal_discovery',
          slug: 'causal_discovery',
          name: I18nText(
            translations: {
              'en': 'Causal Discovery Engine',
              'fi': 'Kausaalipäättelyn moottori',
            },
          ),
          isSystemCore: true,
          engineType: EngineType.causalDiscovery,
          zone: StepZone.zoneB,
        ),
        const NodeStrategy.causalDiscovery(
          id: 'sp_causal_discovery_deletable',
          slug: 'causal_discovery_deletable',
          name: I18nText(
            translations: {
              'en': 'Deletable Causal Discovery',
              'fi': 'Poistettava kausaalipäättely',
            },
          ),
          isSystemCore: false,
          engineType: EngineType.causalDiscovery,
          zone: StepZone.zoneB,
        ),
        const NodeStrategy.llm(
          id: 'sp_ai_steering',
          slug: 'ai_steering',
          name: I18nText(
            translations: {
              'en': 'AI Steering Evaluator',
              'fi': 'Tekoälyohjauksen arvioija',
            },
          ),
          isSystemCore: false,
          engineType: EngineType.prompt,
          zone: StepZone.zoneB,
        ),
        const NodeStrategy.logic(
          id: 'sp_xai_reporter',
          slug: 'xai_reporter',
          name: I18nText(
            translations: {
              'en': 'XAI Reporter & Aggregator',
              'fi': 'XAI Raportointi & Koonti',
            },
          ),
          hook: 'aggregate_xai',
          isSystemCore: true,
          engineType: EngineType.prompt,
          zone: StepZone.zoneC,
        ),
      ];

      mockWorkflow = const Workflow(
        id: 'wf_test_workflow_01',
        slug: 'test_workflow',
        name: I18nText(
          translations: {'en': 'Test Workflow', 'fi': 'Testityövoo'},
        ),
        description: I18nText(
          translations: {'en': 'Workflow description', 'fi': 'Kuvaus'},
        ),
        modelRegistryId: 'mr_test_01',
        steps: [
          StepRule(
            id: 'sr_input_001',
            taskBlueprint: 'sp_input_processing',
            dependsOn: [],
            isSynthesisSource: false,
          ),
          StepRule(
            id: 'sr_specialist_001',
            taskBlueprint: 'sp_specialist_coach',
            dependsOn: ['sr_input_001'],
            isSynthesisSource: true,
          ),
          StepRule(
            id: 'sr_causal_001',
            taskBlueprint: 'sp_causal_discovery',
            dependsOn: ['sr_input_001'],
            isSynthesisSource: false,
          ),
          StepRule(
            id: 'sr_steering_001',
            taskBlueprint: 'sp_ai_steering',
            dependsOn: ['sr_input_001', 'sr_causal_001'],
            causalSourceStepId: 'sr_causal_001',
            isSynthesisSource: true,
          ),
          StepRule(
            id: 'sr_funnel_001',
            taskBlueprint: 'sp_xai_reporter',
            dependsOn: [
              'sr_specialist_001',
              'sr_causal_001',
              'sr_steering_001',
            ],
            isSynthesisSource: false,
          ),
        ],
      );
    });

    Widget createTestWidget({
      required Workflow workflow,
      List<NodeStrategy>? customBlueprints,
      Function(Workflow)? onChanged,
      Locale locale = const Locale('fi'),
    }) {
      return MaterialApp(
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: WorkflowStepsTab(
            workflow: workflow,
            blueprints: customBlueprints ?? mockBlueprints,
            mcpGateways: const [],
            onChanged: onChanged ?? (_) {},
          ),
        ),
      );
    }

    testWidgets(
      '100% Engine Symmetry: renders all 5 steps including causal discovery as visible cards',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1280, 1600);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        await tester.pumpWidget(createTestWidget(workflow: mockWorkflow));
        await tester.pumpAndSettle();

        // Verify all 5 steps are rendered as visible cards
        final cardFinder = find.byType(WorkflowStepCard);
        expect(cardFinder, findsNWidgets(5));

        // Causal discovery step is rendered in the list as a first-class card
        expect(
          find.widgetWithText(WorkflowStepCard, 'sr_causal_001'),
          findsOneWidget,
        );
        expect(
          find.widgetWithText(WorkflowStepCard, 'sr_steering_001'),
          findsOneWidget,
        );
        expect(
          find.text('Kausaalipäättelyn moottori'),
          findsAtLeastNWidgets(1),
        );
        expect(find.text('Tekoälyohjauksen arvioija'), findsAtLeastNWidgets(1));
      },
    );

    testWidgets(
      '_findFirstZoneCIndex correctly ignores causalDiscovery steps even if isSystemCore is true, placing new steps before funnel anchor',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1280, 1600);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        Workflow? updatedWorkflow;

        await tester.pumpWidget(
          createTestWidget(
            workflow: mockWorkflow,
            onChanged: (wf) => updatedWorkflow = wf,
          ),
        );
        await tester.pumpAndSettle();

        // Tap Add Step Node button
        final addButton = find.byIcon(Icons.add);
        expect(addButton, findsOneWidget);
        await tester.tap(addButton);
        await tester.pumpAndSettle();

        expect(updatedWorkflow, isNotNull);
        final steps = updatedWorkflow!.steps;
        expect(steps.length, equals(6));

        // Zone C funnel anchor (sr_funnel_001) must remain at the very end
        expect(steps.last.id, equals('sr_funnel_001'));

        // The newly inserted step should be at index 4 (before the Zone C funnel anchor at index 5)
        final newStep = steps[4];
        expect(newStep.id.startsWith('sr_'), isTrue);

        // Zone C funnel anchor must have been updated to depend on the new step
        final funnelStep = steps.last;
        expect(funnelStep.dependsOn.contains(newStep.id), isTrue);
      },
    );

    testWidgets(
      '_deleteStep cleanly cascades to prune dependsOn and reset causalSourceStepId to null',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1280, 1600);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        Workflow? updatedWorkflow;

        // Use deletable causal discovery blueprint for sr_causal_001
        final workflowWithDeletableCausal = mockWorkflow.copyWith(
          steps: [
            mockWorkflow.steps[0],
            mockWorkflow.steps[1],
            mockWorkflow.steps[2].copyWith(
              taskBlueprint: 'sp_causal_discovery_deletable',
            ),
            mockWorkflow.steps[3],
            mockWorkflow.steps[4],
          ],
        );

        await tester.pumpWidget(
          createTestWidget(
            workflow: workflowWithDeletableCausal,
            onChanged: (wf) => updatedWorkflow = wf,
          ),
        );
        await tester.pumpAndSettle();

        // Find delete icon buttons:
        // Step 0 (Zone A): protected (no delete button)
        // Step 1 (sr_specialist_001): not protected (delete button 0)
        // Step 2 (sr_causal_001): not protected (delete button 1)
        // Step 3 (sr_steering_001): not protected (delete button 2)
        // Step 4 (sr_funnel_001, Zone C): protected (no delete button)
        final deleteButtons = find.byIcon(Icons.delete);
        expect(deleteButtons, findsNWidgets(3));

        // Delete button at index 1 corresponds to Step 2 (sr_causal_001)
        await tester.ensureVisible(deleteButtons.at(1));
        await tester.tap(deleteButtons.at(1));
        await tester.pumpAndSettle();

        expect(updatedWorkflow, isNotNull);
        final steps = updatedWorkflow!.steps;
        expect(steps.length, equals(4));

        // sr_causal_001 should be deleted
        expect(steps.any((s) => s.id == 'sr_causal_001'), isFalse);

        // Step sr_steering_001 should have causalSourceStepId reset to null and dependsOn pruned
        final steeringStep = steps.firstWhere((s) => s.id == 'sr_steering_001');
        expect(steeringStep.causalSourceStepId, isNull);
        expect(steeringStep.dependsOn.contains('sr_causal_001'), isFalse);
        expect(steeringStep.dependsOn, equals(['sr_input_001']));

        // Funnel anchor sr_funnel_001 should also have sr_causal_001 pruned from dependsOn
        final funnelStep = steps.firstWhere((s) => s.id == 'sr_funnel_001');
        expect(funnelStep.dependsOn.contains('sr_causal_001'), isFalse);
        expect(
          funnelStep.dependsOn,
          equals(['sr_specialist_001', 'sr_steering_001']),
        );
      },
    );
  });
}
