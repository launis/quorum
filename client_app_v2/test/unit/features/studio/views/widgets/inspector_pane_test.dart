import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/inspector_pane.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

const String _kWorkflowId = 'wkf_0195f3a0000070008000000000000001';
const String _kModelRegistryId = 'mrg_0195f3a0000070008000000000000001';
const String _kStep1Id = 'stp_0195f3a0000070008000000000000001';
const String _kStep2Id = 'stp_0195f3a0000070008000000000000002';
const String _kBlueprint1Id = 'stp_0195f3a0000070008000000000000010';
const String _kBlueprint2Id = 'stp_0195f3a0000070008000000000000020';

List<NodeStrategy> _buildTestBlueprints() {
  return const <NodeStrategy>[
    NodeStrategy.llm(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: _kBlueprint1Id,
      slug: 'analyst-blueprint',
      name: I18nText(
        translations: <String, String>{
          'en': 'Analyst Blueprint',
          'fi': 'Analyytikkosuunnitelma',
        },
      ),
    ),
    NodeStrategy.logic(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: _kBlueprint2Id,
      slug: 'validator-blueprint',
      hook: 'validation_hook',
      name: I18nText(translations: <String, String>{'en': 'Validator Logic'}),
    ),
  ];
}

Workflow _buildTestWorkflow({String id = _kWorkflowId, List<StepRule>? steps}) {
  return Workflow(
    organizationId: 'org_0195f3a0000070008000000000000001',
    id: id,
    slug: 'inspector-test-workflow',
    name: const I18nText(
      translations: <String, String>{
        'en': 'Inspector Test Workflow',
        'fi': 'Tarkastimen testityönkulku',
      },
    ),
    description: const I18nText(
      translations: <String, String>{
        'en': 'Workflow for InspectorPane unit tests.',
        'fi': 'Työnkulku InspectorPane-yksikkötesteille.',
      },
    ),
    modelRegistryId: _kModelRegistryId,
    steps:
        steps ??
        const <StepRule>[
          StepRule(
            id: _kStep1Id,
            taskBlueprint: _kBlueprint1Id,
            dependsOn: <String>[_kStep2Id],
            inputMappings: <String, String>{'inputs': r'$inputs.doc'},
          ),
          StepRule(id: _kStep2Id, taskBlueprint: _kBlueprint2Id),
        ],
  );
}

Widget _wrapWithL10n(Widget child, {Locale locale = const Locale('en')}) {
  return MaterialApp(
    locale: locale,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: Scaffold(body: child),
  );
}

void main() {
  group('InspectorPane Dumb Painter & Desktop Pro UX Widget Tests', () {
    testWidgets(
      'renders empty state with localized labels and triggers onAddStep when selectedStepId is null (Positive 1)',
      (WidgetTester tester) async {
        bool addStepCalled = false;

        await tester.pumpWidget(
          _wrapWithL10n(
            InspectorPane(
              selectedStepId: null,
              workflow: _buildTestWorkflow(),
              availableBlueprints: _buildTestBlueprints(),
              onStepUpdated: (_, _) {},
              onAddStep: () {
                addStepCalled = true;
              },
              onDeleteStep: (_) {},
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('System Inspector'), findsOneWidget);
        expect(find.text('Select a step to configure'), findsOneWidget);
        expect(find.text('Add Step Node'), findsOneWidget);

        await tester.tap(
          find.byKey(const ValueKey<String>('inspector_add_step_btn')),
        );
        await tester.pump();
        expect(addStepCalled, isTrue);
      },
    );

    testWidgets(
      'renders selected step details, read-only ID, localized blueprint dropdown, and mutates step fields (Positive 2)',
      (WidgetTester tester) async {
        Workflow currentWorkflow = _buildTestWorkflow();
        String? deletedStepId;

        await tester.pumpWidget(
          _wrapWithL10n(
            locale: const Locale('fi'),
            StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                return InspectorPane(
                  selectedStepId: _kStep1Id,
                  workflow: currentWorkflow,
                  availableBlueprints: _buildTestBlueprints(),
                  onStepUpdated: (String stepId, StepRule updatedStep) {
                    setState(() {
                      currentWorkflow = currentWorkflow.copyWith(
                        steps: currentWorkflow.steps
                            .map(
                              (StepRule s) => s.id == stepId ? updatedStep : s,
                            )
                            .toList(),
                      );
                    });
                  },
                  onAddStep: () {},
                  onDeleteStep: (String stepId) {
                    deletedStepId = stepId;
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Read-only SelectableText displays opaque step ID
        expect(find.widgetWithText(SelectableText, _kStep1Id), findsOneWidget);
        // Active locale ('fi') label for Blueprint 1 and Lingua Franca ('en') fallback for Blueprint 2
        expect(find.text('Analyytikkosuunnitelma'), findsOneWidget);

        // Select Blueprint 2 from dropdown
        await tester.tap(
          find.byKey(
            const ValueKey<String>(
              'inspector_blueprint_dropdown_${_kStep1Id}_$_kBlueprint1Id',
            ),
          ),
        );
        await tester.pumpAndSettle();
        await tester.tap(find.text('Validator Logic').last);
        await tester.pumpAndSettle();

        expect(
          currentWorkflow.steps.first.taskBlueprint,
          equals(_kBlueprint2Id),
        );

        // Update dependsOn field (with extra whitespace and trailing comma BVA)
        final Finder dependsOnFinder = find.byKey(
          const ValueKey<String>(
            'inspector_depends_on_${_kStep1Id}_$_kStep2Id',
          ),
        );
        await tester.enterText(
          dependsOnFinder,
          '  $_kStep2Id ,  , stp_0195f3a0000070008000000000000099  ',
        );
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();

        expect(
          currentWorkflow.steps.first.dependsOn,
          equals(<String>[_kStep2Id, 'stp_0195f3a0000070008000000000000099']),
        );

        // Update input mapping value
        final Finder mappingValFinder = find.byKey(
          const ValueKey<String>(
            r'inspector_mapping_val_stp_0195f3a0000070008000000000000001_inputs_$inputs.doc',
          ),
        );
        await tester.enterText(mappingValFinder, r'  $steps.prev.output  ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();

        expect(
          currentWorkflow.steps.first.inputMappings['inputs'],
          equals(r'$steps.prev.output'),
        );

        // Rename input mapping key
        final Finder mappingKeyFinder = find.byKey(
          const ValueKey<String>('inspector_mapping_key_${_kStep1Id}_inputs'),
        );
        await tester.enterText(mappingKeyFinder, '  source_payload  ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();

        expect(
          currentWorkflow.steps.first.inputMappings.containsKey('inputs'),
          isFalse,
        );
        expect(
          currentWorkflow.steps.first.inputMappings['source_payload'],
          equals(r'$steps.prev.output'),
        );

        // Add new mapping
        await tester.tap(
          find.byKey(const ValueKey<String>('inspector_add_mapping_btn')),
        );
        await tester.pumpAndSettle();
        expect(
          currentWorkflow.steps.first.inputMappings['new_param_1'],
          equals(r'$inputs.'),
        );

        // Remove mapping
        await tester.tap(
          find.byKey(
            const ValueKey<String>(
              'inspector_mapping_remove_${_kStep1Id}_new_param_1',
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(
          currentWorkflow.steps.first.inputMappings.containsKey('new_param_1'),
          isFalse,
        );

        // Delete step callback
        await tester.tap(
          find.byKey(const ValueKey<String>('inspector_delete_step_btn')),
        );
        await tester.pump();
        expect(deletedStepId, equals(_kStep1Id));
      },
    );

    testWidgets(
      'ignores blank or unchanged mapping key rename and handles empty dependsOn (ISTQB BVA)',
      (WidgetTester tester) async {
        int updateCount = 0;
        StepRule latestStep = const StepRule(
          id: _kStep1Id,
          taskBlueprint: 'stp_0195f3a0000070008000000000000099',
          dependsOn: <String>[_kStep2Id],
          inputMappings: <String, String>{'inputs': r'$inputs.doc'},
        );

        await tester.pumpWidget(
          _wrapWithL10n(
            InspectorPane(
              selectedStepId: _kStep1Id,
              workflow: _buildTestWorkflow(steps: <StepRule>[latestStep]),
              availableBlueprints: _buildTestBlueprints(),
              onStepUpdated: (_, StepRule updatedStep) {
                updateCount++;
                latestStep = updatedStep;
              },
              onAddStep: () {},
              onDeleteStep: (_) {},
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Submitting whitespace-only key does not trigger update
        final Finder mappingKeyFinder = find.byKey(
          const ValueKey<String>('inspector_mapping_key_${_kStep1Id}_inputs'),
        );
        await tester.enterText(mappingKeyFinder, '   ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();
        expect(updateCount, equals(0));

        // Submitting empty dependsOn clears list to 0 items
        final Finder dependsOnFinder = find.byKey(
          const ValueKey<String>(
            'inspector_depends_on_${_kStep1Id}_$_kStep2Id',
          ),
        );
        await tester.enterText(dependsOnFinder, ' ,  , ');
        await tester.testTextInput.receiveAction(TextInputAction.done);
        await tester.pumpAndSettle();
        expect(updateCount, equals(1));
        expect(latestStep.dependsOn, isEmpty);
      },
    );

    testWidgets('throws AppException when workflow ID is empty (Negative 1)', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        _wrapWithL10n(
          InspectorPane(
            selectedStepId: null,
            workflow: _buildTestWorkflow(id: '   '),
            availableBlueprints: _buildTestBlueprints(),
            onStepUpdated: (_, _) {},
            onAddStep: () {},
            onDeleteStep: (_) {},
          ),
        ),
      );

      expect(tester.takeException(), isA<AppException>());
    });

    testWidgets(
      'throws AppException when selectedStepId is blank or not found in workflow steps (Negative 2)',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _wrapWithL10n(
            InspectorPane(
              selectedStepId: '   ',
              workflow: _buildTestWorkflow(),
              availableBlueprints: _buildTestBlueprints(),
              onStepUpdated: (_, _) {},
              onAddStep: () {},
              onDeleteStep: (_) {},
            ),
          ),
        );
        expect(tester.takeException(), isA<AppException>());

        await tester.pumpWidget(
          _wrapWithL10n(
            InspectorPane(
              selectedStepId: 'stp_0195f3a0000070008000000000000999',
              workflow: _buildTestWorkflow(),
              availableBlueprints: _buildTestBlueprints(),
              onStepUpdated: (_, _) {},
              onAddStep: () {},
              onDeleteStep: (_) {},
            ),
          ),
        );
        expect(tester.takeException(), isA<AppException>());
      },
    );

    testWidgets(
      'throws AppException when blueprint ID is empty or blueprint translation is missing (Negative 3)',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _wrapWithL10n(
            InspectorPane(
              selectedStepId: _kStep1Id,
              workflow: _buildTestWorkflow(),
              availableBlueprints: const <NodeStrategy>[
                NodeStrategy.llm(
                  organizationId: 'org_0195f3a0000070008000000000000001',
                  id: '   ',
                  slug: 'empty-id',
                  name: I18nText(translations: <String, String>{'en': 'Valid'}),
                ),
              ],
              onStepUpdated: (_, _) {},
              onAddStep: () {},
              onDeleteStep: (_) {},
            ),
          ),
        );
        expect(tester.takeException(), isA<AppException>());

        await tester.pumpWidget(
          _wrapWithL10n(
            InspectorPane(
              selectedStepId: _kStep1Id,
              workflow: _buildTestWorkflow(),
              availableBlueprints: const <NodeStrategy>[
                NodeStrategy.llm(
                  organizationId: 'org_0195f3a0000070008000000000000001',
                  id: _kBlueprint1Id,
                  slug: 'missing-translation',
                  name: I18nText(translations: <String, String>{}),
                ),
              ],
              onStepUpdated: (_, _) {},
              onAddStep: () {},
              onDeleteStep: (_) {},
            ),
          ),
        );
        expect(tester.takeException(), isA<AppException>());
      },
    );
  });
}
