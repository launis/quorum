import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/dag_canvas_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

Workflow _buildTestWorkflow({
  String id = 'wkf_0195f3a0000070008000000000000001',
  List<StepRule>? steps,
}) {
  return Workflow(
    organizationId: 'org_0195f3a0000070008000000000000001',
    id: id,
    slug: 'test-dag-workflow',
    name: const I18nText(
      translations: <String, String>{
        'en': 'Test DAG Workflow',
        'fi': 'Testi-DAG-työnkulku',
      },
    ),
    description: const I18nText(
      translations: <String, String>{
        'en': 'DAG canvas verification workflow.',
        'fi': 'DAG-näkymän tarkistustyönkulku.',
      },
    ),
    modelRegistryId: 'mrg_0195f3a0000070008000000000000001',
    steps:
        steps ??
        const <StepRule>[
          StepRule(
            id: 'stp_0195f3a0000070008000000000000001',
            taskBlueprint: 'bp_0195f3a0000070008000000000000010',
            uiPosX: 100.0,
            uiPosY: 120.0,
          ),
          StepRule(
            id: 'stp_0195f3a0000070008000000000000002',
            taskBlueprint: '',
            dependsOn: <String>['stp_0195f3a0000070008000000000000001'],
            uiPosX: 0.0,
            uiPosY: 0.0,
          ),
        ],
  );
}

Widget _wrapWithL10n(Widget child, {Locale locale = const Locale('en')}) {
  return MaterialApp(
    locale: locale,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: child,
  );
}

void main() {
  group('DagCanvasView Dumb Painter & Desktop Pro UX Widget Tests', () {
    testWidgets(
      'renders nodes with localized labels, default 4000 coords, mouse cursor, and keyboard activation (Positive)',
      (WidgetTester tester) async {
        String? selectedStepId;
        Workflow currentWorkflow = _buildTestWorkflow();

        await tester.pumpWidget(
          _wrapWithL10n(
            DagCanvasView(
              workflow: currentWorkflow,
              onNodeSelected: (String stepId) {
                selectedStepId = stepId;
              },
              onWorkflowUpdated: (Workflow updated) {
                currentWorkflow = updated;
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        const String step1Id = 'stp_0195f3a0000070008000000000000001';
        const String step2Id = 'stp_0195f3a0000070008000000000000002';

        expect(find.text(step1Id), findsOneWidget);
        expect(find.text(step2Id), findsOneWidget);
        expect(
          find.text(
            'Task Profile (Cognitive Role): bp_0195f3a0000070008000000000000010',
          ),
          findsOneWidget,
        );
        expect(
          find.text('Task Profile (Cognitive Role): None'),
          findsOneWidget,
        );

        // Verify Positioned coordinates: explicit (100, 120) vs default (0.0 -> 4000.0)
        final Positioned pos1 = tester.widget<Positioned>(
          find.byKey(const ValueKey<String>('dag_node_pos_$step1Id')),
        );
        expect(pos1.left, equals(100.0));
        expect(pos1.top, equals(120.0));

        final Positioned pos2 = tester.widget<Positioned>(
          find.byKey(const ValueKey<String>('dag_node_pos_$step2Id')),
        );
        expect(pos2.left, equals(4000.0));
        expect(pos2.top, equals(4000.0));

        // Verify Desktop Pro Tool mouse cursor on FocusableActionDetector
        final FocusableActionDetector focusDetector1 = tester
            .widget<FocusableActionDetector>(
              find.byKey(const ValueKey<String>('dag_node_focus_$step1Id')),
            );
        expect(focusDetector1.mouseCursor, equals(SystemMouseCursors.click));

        // Verify tap selection via callback
        final GestureDetector gesture1 = tester.widget<GestureDetector>(
          find.byKey(const ValueKey<String>('dag_node_gesture_$step1Id')),
        );
        gesture1.onTap!();
        expect(selectedStepId, equals(step1Id));

        // Verify keyboard ActivateIntent triggers node selection
        Actions.invoke(
          tester.element(
            find.byKey(const ValueKey<String>('dag_node_gesture_$step2Id')),
          ),
          const ActivateIntent(),
        );
        await tester.pump();
        expect(selectedStepId, equals(step2Id));
      },
    );

    testWidgets(
      'clamps dragged coordinates within [0.0, 7800.0] canvas bounds (ISTQB BVA)',
      (WidgetTester tester) async {
        const String stepId = 'stp_0195f3a0000070008000000000000001';
        Workflow currentWorkflow = _buildTestWorkflow(
          steps: const <StepRule>[
            StepRule(
              id: stepId,
              taskBlueprint: 'bp_0195f3a0000070008000000000000010',
              uiPosX: 10.0,
              uiPosY: 7795.0,
            ),
          ],
        );

        await tester.pumpWidget(
          _wrapWithL10n(
            StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                return DagCanvasView(
                  workflow: currentWorkflow,
                  onNodeSelected: (_) {},
                  onWorkflowUpdated: (Workflow updated) {
                    setState(() {
                      currentWorkflow = updated;
                    });
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        final GestureDetector gesture = tester.widget<GestureDetector>(
          find.byKey(const ValueKey<String>('dag_node_gesture_$stepId')),
        );

        // BVA min-1 on X (10.0 - 25.0 = -15.0 -> clamped to 0.0)
        // and max+1 on Y (7795.0 + 20.0 = 7815.0 -> clamped to 7800.0)
        gesture.onPanUpdate!(
          DragUpdateDetails(
            globalPosition: const Offset(100, 100),
            delta: const Offset(-25.0, 20.0),
          ),
        );
        await tester.pumpAndSettle();

        expect(currentWorkflow.steps.first.uiPosX, equals(0.0));
        expect(currentWorkflow.steps.first.uiPosY, equals(7800.0));
      },
    );

    testWidgets('throws AppException when workflow ID is empty (Negative 1)', (
      WidgetTester tester,
    ) async {
      final Workflow invalidWorkflow = _buildTestWorkflow(id: '   ');

      await tester.pumpWidget(
        _wrapWithL10n(
          DagCanvasView(
            workflow: invalidWorkflow,
            onNodeSelected: (_) {},
            onWorkflowUpdated: (_) {},
          ),
        ),
      );

      expect(tester.takeException(), isA<AppException>());
    });

    testWidgets('throws AppException when step ID is empty (Negative 2)', (
      WidgetTester tester,
    ) async {
      final Workflow invalidWorkflow = _buildTestWorkflow(
        steps: const <StepRule>[
          StepRule(
            id: '',
            taskBlueprint: 'bp_0195f3a0000070008000000000000010',
          ),
        ],
      );

      await tester.pumpWidget(
        _wrapWithL10n(
          DagCanvasView(
            workflow: invalidWorkflow,
            onNodeSelected: (_) {},
            onWorkflowUpdated: (_) {},
          ),
        ),
      );

      expect(tester.takeException(), isA<AppException>());
    });

    testWidgets(
      'throws AppException when step coordinates violate [0.0, 8000.0] bounds (Negative 3 - BVA min-1 / max+1)',
      (WidgetTester tester) async {
        final Workflow minMinusOneWorkflow = _buildTestWorkflow(
          steps: const <StepRule>[
            StepRule(
              id: 'stp_0195f3a0000070008000000000000001',
              taskBlueprint: 'bp_0195f3a0000070008000000000000010',
              uiPosX: -0.1,
              uiPosY: 100.0,
            ),
          ],
        );

        await tester.pumpWidget(
          _wrapWithL10n(
            DagCanvasView(
              workflow: minMinusOneWorkflow,
              onNodeSelected: (_) {},
              onWorkflowUpdated: (_) {},
            ),
          ),
        );

        expect(tester.takeException(), isA<AppException>());

        final Workflow maxPlusOneWorkflow = _buildTestWorkflow(
          steps: const <StepRule>[
            StepRule(
              id: 'stp_0195f3a0000070008000000000000001',
              taskBlueprint: 'bp_0195f3a0000070008000000000000010',
              uiPosX: 100.0,
              uiPosY: 8000.1,
            ),
          ],
        );

        await tester.pumpWidget(
          _wrapWithL10n(
            DagCanvasView(
              workflow: maxPlusOneWorkflow,
              onNodeSelected: (_) {},
              onWorkflowUpdated: (_) {},
            ),
          ),
        );

        expect(tester.takeException(), isA<AppException>());
      },
    );
  });
}
