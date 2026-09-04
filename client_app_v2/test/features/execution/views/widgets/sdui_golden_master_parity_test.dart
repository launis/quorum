import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';

void main() {
  Widget buildTestableWidget({
    required Widget child,
    Locale locale = const Locale('en'),
  }) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: locale,
      home: Scaffold(body: SingleChildScrollView(child: child)),
    );
  }

  Map<String, dynamic> loadGoldenMasterJson() {
    // Look up fixture from backend_v2/tests/fixtures
    final candidatePaths = [
      '../backend_v2/tests/fixtures/sdui_golden_master.json',
      'backend_v2/tests/fixtures/sdui_golden_master.json',
      '../../backend_v2/tests/fixtures/sdui_golden_master.json',
    ];

    for (final p in candidatePaths) {
      final file = File(p);
      if (file.existsSync()) {
        final content = file.readAsStringSync();
        return jsonDecode(content) as Map<String, dynamic>;
      }
    }
    throw StateError(
      'Could not find sdui_golden_master.json in candidate paths: $candidatePaths',
    );
  }

  group('SDUI Golden Master Parity & Widget Tests', () {
    late Map<String, dynamic> masterJson;
    late List<SduiBlockDTO> parsedBlocks;
    late List<McpAuditTraceDto> parsedAudit;

    setUp(() {
      masterJson = loadGoldenMasterJson();
      final rawBlocks = masterJson['inner_sdui_blocks'] as List<dynamic>;
      parsedBlocks = rawBlocks
          .map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
          .toList();

      final rawAudit = masterJson['mcp_tool_audit'] as List<dynamic>?;
      parsedAudit = (rawAudit ?? [])
          .map((e) => McpAuditTraceDto.fromJson(e as Map<String, dynamic>))
          .toList();
    });

    test(
      'verifies deserialization exhaustiveness across all 17 AnySduiBlock types',
      () {
        expect(parsedBlocks.length, equals(17));

        final typesFound = parsedBlocks.map((b) => b.runtimeType).toSet();
        expect(typesFound, contains(SduiMetadataBlock));
        expect(typesFound, contains(SduiHeroInsightBlock));
        expect(typesFound, contains(SduiParagraphBlock));
        expect(typesFound, contains(SduiBulletListBlock));
        expect(typesFound, contains(SduiAlertBoxBlock));
        expect(typesFound, contains(SduiQuoteCardBlock));
        expect(typesFound, contains(SduiWarningCardBlock));
        expect(typesFound, contains(SduiNACardBlock));
        expect(typesFound, contains(SduiMarkdownBlock));
        expect(typesFound, contains(SduiAccordionBlock));
        expect(typesFound, contains(SduiScoreCardBlock));
        expect(typesFound, contains(SduiGridBlock));
        expect(typesFound, contains(SduiMetrics1DBlock));
        expect(typesFound, contains(SduiRadarChartBlock));
        expect(typesFound, contains(SduiScatterPlotBlock));
        expect(typesFound, contains(SduiMatrixTableBlock));
        expect(typesFound, contains(SduiAuditTrailBlock));
      },
    );

    for (final locale in [const Locale('en'), const Locale('fi')]) {
      testWidgets(
        'renders all 17 Golden Master SDUI blocks correctly in ${locale.languageCode}',
        (tester) async {
          // Provide adequate desktop canvas dimensions for multi-block render
          tester.view.physicalSize = const Size(1920, 10800);
          tester.view.devicePixelRatio = 1.0;
          addTearDown(() => tester.view.resetPhysicalSize());

          await tester.pumpWidget(
            buildTestableWidget(
              child: SduiBlocksRenderer(
                blocks: parsedBlocks,
                mcpToolAudit: parsedAudit,
              ),
              locale: locale,
            ),
          );
          await tester.pumpAndSettle();

          // 1. SduiMetadataBlock
          expect(find.text('Executive Assessment Profile'), findsWidgets);
          expect(
            tester
                .widget<Text>(find.text('Executive Assessment Profile').first)
                .style
                ?.fontWeight,
            equals(FontWeight.bold),
          );
          expect(find.text('Pillar 4 SDUI'), findsOneWidget);
          expect(find.textContaining('Dr. Evelyn Vance'), findsOneWidget);
          expect(
            find.textContaining('Quorum Cognitive Enterprise'),
            findsOneWidget,
          );
          expect(find.text('\$0.042'), findsOneWidget);

          // 2. SduiHeroInsightBlock
          expect(find.byIcon(Icons.lightbulb_outline), findsOneWidget);
          expect(
            find.textContaining('Strong strategic synthesis'),
            findsOneWidget,
          );

          // 3. SduiParagraphBlock
          expect(find.textContaining('cognitive clarity'), findsOneWidget);

          // 4. SduiBulletListBlock
          expect(
            find.textContaining('Demonstrates proactive risk anticipation'),
            findsOneWidget,
          );
          expect(
            find.textContaining('Enforces Fail-Fast verification'),
            findsOneWidget,
          );

          // 5. SduiAlertBoxBlock
          expect(
            find.textContaining('High degree of cognitive agility'),
            findsOneWidget,
          );

          // 6. SduiQuoteCardBlock
          expect(find.byIcon(Icons.format_quote), findsOneWidget);
          expect(find.textContaining('fail loudly'), findsOneWidget);
          expect(
            tester
                .widget<Text>(find.textContaining('fail loudly'))
                .style
                ?.fontStyle,
            equals(FontStyle.italic),
          );
          expect(find.text('doc_transcription'), findsOneWidget);
          expect(find.text('src_0'), findsOneWidget);

          // 7. SduiWarningCardBlock
          expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
          expect(find.textContaining('Mild hesitation noted'), findsOneWidget);
          expect(
            find.textContaining(
              'legacy refactoring might take an extra sprint',
            ),
            findsOneWidget,
          );

          // 8. SduiNACardBlock
          expect(find.byIcon(Icons.info_outline), findsWidgets);
          expect(
            find.textContaining(
              'External supply chain compliance was not evaluated',
            ),
            findsOneWidget,
          );
          expect(find.text('tda_short_circuit_01'), findsOneWidget);

          // 9. SduiMarkdownBlock
          expect(
            find.textContaining('Detailed Analytical Commentary'),
            findsOneWidget,
          );

          // 10. SduiAccordionBlock
          expect(find.text('Coaching & Development Guidance'), findsOneWidget);
          expect(
            find.textContaining('delegating micro-decisions'),
            findsOneWidget,
          );

          // 11. SduiScoreCardBlock
          expect(find.text('88.50/100'), findsOneWidget);
          expect(
            tester.widget<Text>(find.text('88.50/100')).style?.fontWeight,
            equals(FontWeight.bold),
          );

          // 12. SduiGridBlock
          expect(find.textContaining('Grid Cell A'), findsOneWidget);
          expect(find.textContaining('Grid Cell B'), findsOneWidget);

          // 13. SduiMetrics1DBlock
          final expected1dTitle = locale.languageCode == 'fi'
              ? 'Johtamiskompetenssien erittely'
              : 'Leadership Competency Breakdown';
          expect(find.text(expected1dTitle), findsOneWidget);
          final expectedAxisName = locale.languageCode == 'fi'
              ? 'Strateginen toimeenpano'
              : 'Strategic Execution';
          expect(find.textContaining(expectedAxisName), findsWidgets);

          // 14. SduiRadarChartBlock
          final expected3dTitle = locale.languageCode == 'fi'
              ? 'Kokonaisvaltainen johtamisprofiili (3D-tutka)'
              : 'Holistic Leadership Profile (3D Radar)';
          expect(find.text(expected3dTitle), findsOneWidget);

          // 15. SduiScatterPlotBlock
          final expected2dTitle = locale.languageCode == 'fi'
              ? 'Vertaileva päätöksenteko (2D-matriisi)'
              : 'Comparative Decision Making (2D Matrix)';
          expect(find.text(expected2dTitle), findsOneWidget);

          // 16. SduiMatrixTableBlock
          expect(find.text('Strategic Synthesis *'), findsOneWidget);

          // 17. SduiAuditTrailBlock
          expect(find.text('tavily_search'), findsOneWidget);
          expect(
            find.textContaining('Enterprise Cognitive Architecture Standards'),
            findsOneWidget,
          );

          // Anti-happy-path negative testing
          expect(
            find.text('NonExistentQuantumWidgetString12345'),
            findsNothing,
          );
        },
      );
    }
  });
}
