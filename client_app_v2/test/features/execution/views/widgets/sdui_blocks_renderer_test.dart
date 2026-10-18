import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/features/execution/views/widgets/sdui_causal_graph_widget.dart';
import 'package:client_app/features/execution/models/causal_discovery_dto.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/theme/app_theme.dart';

void main() {
  Widget buildTestableWidget(Widget child) {
    return MaterialApp(
      theme: AppTheme.light,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('en'),
      home: Scaffold(body: SingleChildScrollView(child: child)),
    );
  }

  group('SduiBlocksRenderer Tests', () {
    late ErrorWidgetBuilder originalErrorBuilder;

    setUp(() {
      originalErrorBuilder = ErrorWidget.builder;
    });

    tearDown(() {
      ErrorWidget.builder = originalErrorBuilder;
    });
    testWidgets('renders empty SizedBox when blocks list is empty', (
      tester,
    ) async {
      await tester.pumpWidget(
        buildTestableWidget(const SduiBlocksRenderer(blocks: [])),
      );
      expect(find.byType(SizedBox), findsOneWidget);
    });

    testWidgets(
      'renders SduiHeroInsightBlock with lightbulb and markdown text',
      (tester) async {
        final block = SduiHeroInsightBlock(
          text: '### Key Finding\nPerformance increased by **25%**.',
          citations: const [1, 2],
        );

        await tester.pumpWidget(
          buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.lightbulb_outline), findsOneWidget);
        expect(find.textContaining('Key Finding'), findsOneWidget);
        expect(find.textContaining('Performance increased by'), findsOneWidget);
      },
    );

    testWidgets('renders SduiHeroInsightBlock with empty text safely', (
      tester,
    ) async {
      final block = SduiHeroInsightBlock(text: '');

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.lightbulb_outline), findsNothing);
    });

    testWidgets(
      'renders SduiBulletListBlock with bullet items and circle icons',
      (tester) async {
        final block = SduiBulletListBlock(
          items: const [
            SduiBulletListItemDTO(text: 'First bullet point item'),
            SduiBulletListItemDTO(text: 'Second bullet point item'),
          ],
        );

        await tester.pumpWidget(
          buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
        );
        await tester.pumpAndSettle();

        expect(find.textContaining('First bullet point item'), findsOneWidget);
        expect(find.textContaining('Second bullet point item'), findsOneWidget);
        expect(find.byIcon(Icons.circle), findsNWidgets(2));
      },
    );

    testWidgets('renders SduiBulletListBlock with empty items list safely', (
      tester,
    ) async {
      final block = SduiBulletListBlock(items: const []);

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.circle), findsNothing);
    });

    testWidgets(
      'renders SduiQuoteCardBlock with quote, source aliases, and citations',
      (tester) async {
        final block = SduiQuoteCardBlock(
          quote: 'Architectural integrity is not negotiable.',
          sourceAliases: const ['src_0', 'src_1'],
          citations: const [1, 3],
        );

        await tester.pumpWidget(
          buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.format_quote), findsOneWidget);
        expect(
          find.textContaining('Architectural integrity is not negotiable.'),
          findsOneWidget,
        );
        expect(find.text('src_0'), findsOneWidget);
        expect(find.text('src_1'), findsOneWidget);
        expect(find.text('[1] [3]'), findsOneWidget);
      },
    );

    testWidgets('renders SduiQuoteCardBlock with empty aliases and citations', (
      tester,
    ) async {
      final block = SduiQuoteCardBlock(
        quote: 'Stand-alone quote without citations.',
        sourceAliases: const [],
        citations: const [],
      );

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.format_quote), findsOneWidget);
      expect(
        find.textContaining('Stand-alone quote without citations.'),
        findsOneWidget,
      );
      expect(find.byType(Chip), findsNothing);
    });

    testWidgets(
      'renders SduiWarningCardBlock with warning icon, message, and quoteText',
      (tester) async {
        final block = SduiWarningCardBlock(
          message: 'Potential cognitive drift detected in execution.',
          quoteText: 'Excerpt: "Model attempted to bypass strict schema."',
        );

        await tester.pumpWidget(
          buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
        expect(
          find.textContaining(
            'Potential cognitive drift detected in execution.',
          ),
          findsOneWidget,
        );
        expect(
          find.textContaining(
            'Excerpt: "Model attempted to bypass strict schema."',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets('renders SduiWarningCardBlock without quoteText', (
      tester,
    ) async {
      final block = SduiWarningCardBlock(
        message: 'Simple warning without quote text.',
      );

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      expect(
        find.textContaining('Simple warning without quote text.'),
        findsOneWidget,
      );
    });

    testWidgets('renders SduiNACardBlock with info icon and reason badges', (
      tester,
    ) async {
      final block = SduiNACardBlock(
        message: 'Evaluation was skipped due to precondition.',
        shortCircuitReasonTdaIds: const [
          'tda_precondition_01',
          'tda_precondition_02',
        ],
      );

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.info_outline), findsOneWidget);
      expect(
        find.textContaining('Evaluation was skipped due to precondition.'),
        findsOneWidget,
      );
      expect(find.text('tda_precondition_01'), findsOneWidget);
      expect(find.text('tda_precondition_02'), findsOneWidget);
    });

    testWidgets('renders SduiMarkdownBlock and SduiParagraphBlock', (
      tester,
    ) async {
      final blocks = [
        const SduiMarkdownBlock(text: '# Heading 1\nMarkdown paragraph.'),
        const SduiParagraphBlock(text: 'Regular paragraph block text.'),
      ];

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: blocks)),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Heading 1'), findsOneWidget);
      expect(find.textContaining('Markdown paragraph.'), findsOneWidget);
      expect(
        find.textContaining('Regular paragraph block text.'),
        findsOneWidget,
      );
    });

    testWidgets('renders SduiAlertBoxBlock with success severity', (
      tester,
    ) async {
      const block = SduiAlertBoxBlock(
        text: 'All audit checks passed successfully.',
        severity: AlertSeverity.success,
      );

      await tester.pumpWidget(
        buildTestableWidget(const SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.check_circle_outline), findsOneWidget);
      expect(
        find.textContaining('All audit checks passed successfully.'),
        findsOneWidget,
      );
    });

    testWidgets('renders SduiAccordionBlock with children', (tester) async {
      const block = SduiAccordionBlock(
        title: 'Deep Dive Analysis',
        severity: 'info',
        iconName: 'lightbulb',
        children: [SduiMarkdownBlock(text: 'Nested content inside accordion.')],
      );

      await tester.pumpWidget(
        buildTestableWidget(const SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.text('Deep Dive Analysis'), findsOneWidget);
      expect(find.byIcon(Icons.lightbulb), findsOneWidget);
      expect(
        find.textContaining('Nested content inside accordion.'),
        findsOneWidget,
      );
    });

    testWidgets('renders SduiMetadataBlock and SduiScoreCardBlock', (
      tester,
    ) async {
      const metadataBlock = SduiMetadataBlock(
        title: 'Execution Telemetry',
        badges: ['v2.1', 'PROD'],
        metadataLines: ['Model: gemini-1.5-pro', 'Latency: 1.2s'],
      );
      const scoreCardBlock = SduiScoreCardBlock(globalScore: 88.5);

      await tester.pumpWidget(
        buildTestableWidget(
          const SduiBlocksRenderer(blocks: [metadataBlock, scoreCardBlock]),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Execution Telemetry'), findsOneWidget);
      expect(find.text('v2.1'), findsOneWidget);
      expect(find.text('PROD'), findsOneWidget);
      expect(find.textContaining('Model: gemini-1.5-pro'), findsOneWidget);
      expect(find.text('88.50/100'), findsOneWidget);
    });

    testWidgets('test_sdui_blocks_renderer_zero_sized_box_shrink', (
      tester,
    ) async {
      final blocks = [
        SduiMarkdownBlock(text: ''),
        SduiParagraphBlock(text: ''),
        SduiHeroInsightBlock(text: ''),
        SduiBulletListBlock(items: const []),
        SduiQuoteCardBlock(
          quote: '',
          sourceAliases: const [],
          citations: const [],
        ),
        SduiWarningCardBlock(message: ''),
        const SduiScoreCardBlock(globalScore: null),
        const SduiAuditTrailBlock(),
      ];

      await tester.pumpWidget(
        buildTestableWidget(SduiBlocksRenderer(blocks: blocks)),
      );
      await tester.pumpAndSettle();

      final columnFinder = find.byType(Column);
      expect(columnFinder, findsOneWidget);
      final columnWidget = tester.widget<Column>(columnFinder);
      expect(columnWidget.children, isEmpty);
      expect(find.byType(SizedBox), findsNothing);
    });

    testWidgets(
      'renders SduiCausalGraphBlock with full causal discovery data',
      (tester) async {
        const block = SduiCausalGraphBlock(
          id: 'blk_causal_render_1',
          summary: I18nText(
            translations: {
              'en': 'Causal Discovery & Fault Analysis: Root Cause Traced',
            },
          ),
          intactClaimsCount: 8,
          totalClaimsCount: 10,
          criticalPathNodes: [
            CausalNodeDto(
              nodeId: 'atm_root_01',
              claim: 'Root prerequisite holds.',
              sourceQuotes: ['Foundational assumptions verified.'],
              paragraphRef: 'Section 1.1',
              status: ExecutionStatus.passed,
              blameParentIds: [],
              dependentChildIds: ['atm_child_02'],
              tdaScore: 5.0,
              tdaLevelKey: 'L5',
            ),
          ],
          criticalEdges: [
            CausalEdgeDto(
              sourceId: 'atm_root_01',
              targetId: 'atm_child_02',
              reasoning: 'Direct dependency propagation.',
            ),
          ],
          rootCauseDiagnoses: [
            CausalRootCauseDiagnosisDto(
              failingNodeId: 'atm_child_02',
              rootCauseParentId: 'atm_root_01',
              paragraphRef: 'Section 2.4',
              explanation: 'Root interface definition lacks schema bounds.',
              penaltyPoints: 1.5,
            ),
          ],
          antiFluffAudit: AntiFluffAuditDto(
            isolatedConceptCount: 0,
            cycleDetected: false,
            unsupportedClaimsCount: 1,
            logicalCohesionScore: 0.85,
            detectedHollowTerms: [],
          ),
          prescriptiveRemediations: [
            PrescriptiveRemediationDto(
              targetNodeId: 'atm_child_02',
              requiredAction: 'Enforce explicit schema contract.',
              unlocksNodeIds: ['atm_child_03'],
              potentialScoreImpact: 1.5,
            ),
          ],
          fairScoring: FairScoringBreakdownDto(
            independentErrorCount: 1,
            cascadingFaultCount: 1,
            rawPenaltyPoints: 3.0,
            deduplicatedPenaltyPoints: 1.5,
            dampenedSavingsPoints: 1.5,
          ),
        );

        await tester.pumpWidget(
          buildTestableWidget(const SduiBlocksRenderer(blocks: [block])),
        );
        await tester.pumpAndSettle();

        expect(find.byType(SduiCausalGraphWidget), findsOneWidget);
        expect(
          find.text('Causal Discovery & Fault Analysis: Root Cause Traced'),
          findsOneWidget,
        );
        expect(find.text('8 / 10 Intact'), findsOneWidget);
        expect(find.text('CRITICAL CAUSAL PATH'), findsNothing);
        expect(find.textContaining('[atm_root_01]'), findsNothing);
        expect(find.text('ROOT CAUSE DIAGNOSES'), findsNothing);
        expect(find.text('PRESCRIPTIVE REMEDIATIONS'), findsNothing);
      },
    );

    testWidgets(
      'renders SduiCausalGraphBlock minimal with empty lists safely',
      (tester) async {
        const block = SduiCausalGraphBlock(
          id: 'blk_causal_render_min',
          summary: I18nText(translations: {'en': 'Minimal Causal Discovery'}),
          intactClaimsCount: 3,
          totalClaimsCount: 3,
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

        await tester.pumpWidget(
          buildTestableWidget(const SduiBlocksRenderer(blocks: [block])),
        );
        await tester.pumpAndSettle();

        expect(find.byType(SduiCausalGraphWidget), findsOneWidget);
        expect(find.text('Minimal Causal Discovery'), findsOneWidget);
        expect(find.text('3 / 3 Intact'), findsOneWidget);
        expect(find.text('CRITICAL CAUSAL PATH'), findsNothing);
      },
    );

    testWidgets('renders SduiGridBlock with columns and children', (
      tester,
    ) async {
      const block = SduiGridBlock(
        items: [
          SduiMarkdownBlock(text: 'Grid Item 1'),
          SduiMarkdownBlock(text: 'Grid Item 2'),
        ],
      );

      await tester.pumpWidget(
        buildTestableWidget(const SduiBlocksRenderer(blocks: [block])),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Grid Item 1'), findsOneWidget);
      expect(find.textContaining('Grid Item 2'), findsOneWidget);
    });
  });
}
