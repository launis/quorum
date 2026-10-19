import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/causal_discovery_dto.dart';
import 'package:client_app/features/execution/presentation/causal_inspector_modal.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  final fullBlock = SduiCausalGraphBlock(
    id: 'blk_causal_inspector_1',
    summary: const I18nText(
      translations: {
        'en': 'Causal Discovery Full Inspection',
        'fi': 'Kausaalilöydösten täysi tarkastelu',
      },
    ),
    intactClaimsCount: 8,
    totalClaimsCount: 10,
    criticalPathNodes: [
      const CausalNodeDto(
        nodeId: 'atm_root_01',
        claim: 'Root prerequisite holds in system boundary.',
        sourceQuotes: ['Foundational assumptions verified in documentation.'],
        paragraphRef: 'Section 1.1',
        status: ExecutionStatus.passed,
        blameParentIds: [],
        dependentChildIds: ['atm_child_02'],
        tdaScore: 5.0,
        tdaLevelKey: 'L5',
      ),
      const CausalNodeDto(
        nodeId: 'atm_child_02',
        claim: 'Cascading interface contract failed.',
        sourceQuotes: [
          'Unverified interface coupling caused contract fracture.',
        ],
        paragraphRef: 'Section 2.4',
        status: ExecutionStatus.failed,
        blameParentIds: ['atm_root_01'],
        dependentChildIds: [],
        tdaScore: 1.0,
        tdaLevelKey: 'L1',
      ),
    ],
    criticalEdges: [
      const CausalEdgeDto(
        sourceId: 'atm_root_01',
        targetId: 'atm_child_02',
        reasoning: 'Component dependency propagates contract violation.',
      ),
    ],
    rootCauseDiagnoses: [
      const CausalRootCauseDiagnosisDto(
        failingNodeId: 'atm_child_02',
        rootCauseParentId: 'atm_root_01',
        paragraphRef: 'Section 2.4',
        explanation: 'Root interface definition lacks explicit schema bounds.',
        penaltyPoints: 1.5,
      ),
    ],
    antiFluffAudit: const AntiFluffAuditDto(
      isolatedConceptCount: 0,
      cycleDetected: false,
      unsupportedClaimsCount: 1,
      logicalCohesionScore: 0.85,
      detectedHollowTerms: [],
    ),
    prescriptiveRemediations: [
      const PrescriptiveRemediationDto(
        targetNodeId: 'atm_child_02',
        requiredAction: 'Enforce explicit schema contract with extra=forbid.',
        unlocksNodeIds: ['atm_downstream_03'],
        potentialScoreImpact: 1.5,
      ),
    ],
    fairScoring: const FairScoringBreakdownDto(
      independentErrorCount: 1,
      cascadingFaultCount: 1,
      rawPenaltyPoints: 3.0,
      deduplicatedPenaltyPoints: 1.5,
      dampenedSavingsPoints: 1.5,
    ),
  );

  Widget createWidgetUnderTest(
    SduiCausalGraphBlock block, {
    Locale locale = const Locale('en'),
  }) {
    return MaterialApp(
      theme: AppTheme.light,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: locale,
      home: Scaffold(
        body: Center(child: CausalInspectorModal(block: block)),
      ),
    );
  }

  group('CausalInspectorModal', () {
    late ErrorWidgetBuilder originalErrorBuilder;

    setUp(() {
      originalErrorBuilder = ErrorWidget.builder;
    });

    tearDown(() {
      ErrorWidget.builder = originalErrorBuilder;
    });

    testWidgets(
      'renders CausalInspectorModal with interactive canvas and details',
      (tester) async {
        await tester.pumpWidget(createWidgetUnderTest(fullBlock));
        await tester.pumpAndSettle();

        // Title & Summary
        expect(find.text('Causal Discovery Full Inspection'), findsOneWidget);
        expect(find.text('8 / 10 Intact'), findsOneWidget);

        // Section headers
        expect(
          find.text('CRITICAL CAUSAL PATH & DEPENDENCIES'),
          findsOneWidget,
        );
        expect(find.text('CRITICAL CAUSAL EDGES'), findsOneWidget);

        // Nodes on canvas
        expect(find.text('atm_root_01'), findsWidgets);
        expect(find.text('atm_child_02'), findsWidgets);

        // Edge link text
        expect(find.text('atm_root_01 → atm_child_02'), findsOneWidget);

        // Detail Panel (failing node selected initially)
        expect(find.text('Node Details'), findsOneWidget);
        expect(find.text('Citation Evidence'), findsOneWidget);
        expect(
          find.text(
            '"Unverified interface coupling caused contract fracture."',
          ),
          findsOneWidget,
        );
        expect(find.text('Location: Section 2.4'), findsOneWidget);

        // Root Cause and Remediation
        expect(find.text('ROOT CAUSE DIAGNOSIS'), findsOneWidget);
        expect(find.text('REMEDIATION SIMULATION'), findsOneWidget);

        // Footer
        expect(
          find.textContaining('Fair Scoring: 1 independent, 1 cascading'),
          findsOneWidget,
        );
        expect(find.widgetWithText(TextButton, 'Close'), findsOneWidget);
      },
    );

    testWidgets('switching selected node updates detail panel citation', (
      tester,
    ) async {
      await tester.pumpWidget(createWidgetUnderTest(fullBlock));
      await tester.pumpAndSettle();

      // Initially atm_child_02 is selected (the failing node)
      expect(
        find.text('"Unverified interface coupling caused contract fracture."'),
        findsOneWidget,
      );

      // Tap on atm_root_01 to select it
      final rootNodeFinder = find.text(
        'Root prerequisite holds in system boundary.',
      );
      expect(rootNodeFinder, findsOneWidget);
      await tester.tap(rootNodeFinder);
      await tester.pumpAndSettle();

      // Detail panel now shows atm_root_01 citation evidence
      expect(
        find.text('"Foundational assumptions verified in documentation."'),
        findsOneWidget,
      );
      expect(find.text('Location: Section 1.1'), findsOneWidget);
    });

    testWidgets(
      'renders gracefully when criticalPathNodes is empty and fairScoring is null',
      (tester) async {
        const emptyBlock = SduiCausalGraphBlock(
          id: 'blk_empty',
          summary: I18nText(translations: {'en': 'Empty Graph'}),
          intactClaimsCount: 0,
          totalClaimsCount: 0,
          criticalPathNodes: [],
          criticalEdges: [],
          rootCauseDiagnoses: [],
          antiFluffAudit: AntiFluffAuditDto(
            isolatedConceptCount: 0,
            cycleDetected: false,
            unsupportedClaimsCount: 0,
            logicalCohesionScore: 1.0,
            detectedHollowTerms: [],
          ),
          prescriptiveRemediations: [],
          fairScoring: null,
        );

        await tester.pumpWidget(createWidgetUnderTest(emptyBlock));
        await tester.pumpAndSettle();

        expect(find.text('Empty Graph'), findsOneWidget);
        expect(
          find.text('No critical path nodes discovered in this execution.'),
          findsOneWidget,
        );
        expect(
          find.text('Select a node to inspect citations and remediations.'),
          findsOneWidget,
        );
        expect(find.textContaining('Cohesion Score: 100%'), findsOneWidget);
      },
    );

    testWidgets('dismisses cleanly when close IconButton is tapped', (
      tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: Scaffold(
            body: Builder(
              builder: (ctx) => ElevatedButton(
                onPressed: () => showDialog<void>(
                  context: ctx,
                  builder: (_) => CausalInspectorModal(block: fullBlock),
                ),
                child: const Text('Open Modal'),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Open Modal'));
      await tester.pumpAndSettle();
      expect(find.byType(CausalInspectorModal), findsOneWidget);

      // Tap close icon button
      final closeIconFinder = find.byIcon(Icons.close);
      expect(closeIconFinder, findsOneWidget);
      await tester.tap(closeIconFinder);
      await tester.pumpAndSettle();

      expect(find.byType(CausalInspectorModal), findsNothing);
    });
  });
}
