import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/causal_discovery_dto.dart';
import 'package:client_app/features/execution/views/widgets/sdui_causal_graph_widget.dart';
import 'package:client_app/features/execution/presentation/causal_inspector_modal.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  final fullBlock = SduiCausalGraphBlock(
    id: 'blk_causal_1',
    summary: const I18nText(
      translations: {
        'en': 'Causal Discovery & Fault Analysis: Root Cause Traced',
        'fi': 'Kausaalilöydökset ja virheanalyysi: Juurisyy jäljitetty',
      },
    ),
    intactClaimsCount: 8,
    totalClaimsCount: 10,
    criticalPathNodes: [
      const CausalNodeDto(
        nodeId: 'atm_root_01',
        claim: 'Root prerequisite holds.',
        sourceQuote: 'Foundational assumptions verified.',
        paragraphRef: 'Section 1.1',
        status: ExecutionStatus.passed,
        blameParentIds: [],
        dependentChildIds: ['atm_child_02'],
        tdaScore: 5.0,
        tdaLevelKey: 'L5',
      ),
      const CausalNodeDto(
        nodeId: 'atm_child_02',
        claim: 'Downstream contract verification failed.',
        sourceQuote: 'Interface mismatch caused failure.',
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
        reasoning: 'Direct dependency propagation.',
      ),
    ],
    rootCauseDiagnoses: [
      const CausalRootCauseDiagnosisDto(
        failingNodeId: 'atm_child_02',
        rootCauseParentId: 'atm_root_01',
        paragraphRef: 'Section 2.4',
        explanation: 'Root interface definition lacks schema bounds.',
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
        requiredAction: 'Enforce explicit schema contract.',
        unlocksNodeIds: ['atm_child_03'],
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
        body: SingleChildScrollView(child: SduiCausalGraphWidget(block: block)),
      ),
    );
  }

  group('SduiCausalGraphWidget', () {
    late ErrorWidgetBuilder originalErrorBuilder;

    setUp(() {
      originalErrorBuilder = ErrorWidget.builder;
    });

    tearDown(() {
      ErrorWidget.builder = originalErrorBuilder;
    });

    testWidgets(
      'renders SduiCausalGraphWidget with full causal data successfully',
      (tester) async {
        await tester.pumpWidget(createWidgetUnderTest(fullBlock));
        await tester.pumpAndSettle();

        // Summary text
        expect(
          find.text('Causal Discovery & Fault Analysis: Root Cause Traced'),
          findsOneWidget,
        );

        // Intact badge
        expect(find.text('8 / 10 Intact'), findsOneWidget);

        // Inspector button
        expect(find.byType(OutlinedButton), findsOneWidget);

        // Detailed sections are no longer rendered inline in the compact card
        expect(find.text('CRITICAL CAUSAL PATH'), findsNothing);
        expect(find.textContaining('[atm_root_01]'), findsNothing);
        expect(find.text('ROOT CAUSE DIAGNOSES'), findsNothing);
        expect(find.text('PRESCRIPTIVE REMEDIATIONS'), findsNothing);
      },
    );

    testWidgets('renders SduiCausalGraphWidget in Finnish locale correctly', (
      tester,
    ) async {
      await tester.pumpWidget(
        createWidgetUnderTest(fullBlock, locale: const Locale('fi')),
      );
      await tester.pumpAndSettle();

      // Summary text in Finnish
      expect(
        find.text('Kausaalilöydökset ja virheanalyysi: Juurisyy jäljitetty'),
        findsOneWidget,
      );
      expect(find.text('8 / 10 Intact'), findsOneWidget);
    });

    testWidgets('opens CausalInspectorModal when clicking inspector button', (
      tester,
    ) async {
      await tester.pumpWidget(createWidgetUnderTest(fullBlock));
      await tester.pumpAndSettle();

      final inspectorButton = find.byType(OutlinedButton);
      expect(inspectorButton, findsOneWidget);

      await tester.tap(inspectorButton);
      await tester.pumpAndSettle();

      expect(find.byType(CausalInspectorModal), findsOneWidget);

      // Cleanly pop the dialog and unmount
      final closeButton = find.widgetWithText(TextButton, 'Close');
      if (closeButton.evaluate().isNotEmpty) {
        await tester.tap(closeButton);
      } else {
        Navigator.of(tester.element(find.byType(CausalInspectorModal))).pop();
      }
      await tester.pumpAndSettle();
    });

    testWidgets(
      'renders minimal SduiCausalGraphWidget gracefully with empty lists',
      (tester) async {
        const minimalBlock = SduiCausalGraphBlock(
          id: 'blk_min',
          summary: I18nText(translations: {'en': 'Minimal Causal Summary'}),
          intactClaimsCount: 5,
          totalClaimsCount: 5,
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

        await tester.pumpWidget(createWidgetUnderTest(minimalBlock));
        await tester.pumpAndSettle();

        expect(find.text('Minimal Causal Summary'), findsOneWidget);
        expect(find.text('5 / 5 Intact'), findsOneWidget);

        // Empty sections should not be rendered
        expect(find.text('CRITICAL CAUSAL PATH'), findsNothing);
        expect(find.text('ROOT CAUSE DIAGNOSES'), findsNothing);
        expect(find.text('PRESCRIPTIVE REMEDIATIONS'), findsNothing);
      },
    );
  });
}
