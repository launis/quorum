import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/features/execution/views/widgets/matrix_row_item_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  testWidgets(
    'MatrixRowItemWidget renders correctly and matches golden snapshot',
    (WidgetTester tester) async {
      const matrix = MatrixScorecardRowDto(
        blockId: 'block_row_1',
        labelI18n: I18nText(
          translations: {'fi': 'Kognitio', 'en': 'Cognition'},
        ),
        name: 'Cognition',
        score: 4.5,
        scaleMax: 5.0,
        normalizedScore: 90.0,
        trueAtoms: 9,
        totalAtoms: 10,
        isEvaluative: true,
        rowExplanation: 'Very high cognitive score based on facts.',
        levelBreakdown: {'1': '5/5', '2': '4/5'},
        levelNames: {'1': 'T1', '2': 'T2'},
      );

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: const Scaffold(
              body: Padding(
                padding: EdgeInsets.all(16.0),
                child: MatrixRowItemWidget(matrix: matrix),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      await expectLater(
        find.byType(MatrixRowItemWidget),
        matchesGoldenFile('goldens/matrix_row_item_snapshot.png'),
      );
    },
  );

  testWidgets(
    'AtomMatrixTableWidget renders correctly and matches golden snapshot',
    (WidgetTester tester) async {
      final matrices = [
        MatrixScorecardRowDto(
          blockId: 'block_override',
          labelI18n: const I18nText(
            translations: {'fi': 'Yliohjaus', 'en': 'Override'},
          ),
          name: 'Override',
          score: 0.0,
          scaleMax: 5.0,
          trueAtoms: 0,
          totalAtoms: 1,
          isEvaluative: true,
          rowExplanation: 'This is an explanation for the AI decision.',
          levelBreakdown: const {'1': '0 / 1'},
          levelNames: const {'1': 'T1'},
          evaluatedAtoms: [
            ScorecardAtomDto(
              atomId: 'atom_1',
              level: 1,
              levelName: 'T1',
              claimLabel: 'Claim test with human override',
              chartDisplayLabel: 'Claim test with human override',
              visualIntent: VisualIntent.info,
              extractedFacts: const {},
              exactQuotes: const [
                QuoteEvidenceDto(
                  sourceId: 'doc_1',
                  displayName: 'DOC-1',
                  quoteText: 'AI says FAIL',
                ),
              ],
              internalLogicEn: const ReasoningStepDto(
                step1IdentifyPremise: '',
                step2ScanSource: '',
                step3EvaluateAntiPatterns: '',
                step4FinalConclusion: '',
              ),
              status: 'FAIL',
              semanticReasoning: 'AI reasoning says it fails',
              contextualOverride: false,
              structuralLocation: '',
              humanOverride: const HumanOverrideDto(
                newStatus: 'PASS',
                reason: 'Human thinks it is PASS',
                evidenceQuotes: [
                  QuoteEvidenceDto(
                    sourceId: 'manual',
                    displayName: 'MANUAL',
                    quoteText: 'Human evidence',
                  ),
                ],
              ),
            ),
          ],
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: MediaQuery(
              data: const MediaQueryData(size: Size(800, 600)),
              child: Scaffold(
                body: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: SingleChildScrollView(
                    child: AtomMatrixTableWidget(
                      matrices: matrices,
                      visibleColumns: const [
                        'label',
                        'score',
                        'normalized_score',
                        'distribution',
                        'row_explanation',
                        'quotes',
                      ],
                      executionId: 'test_execution_1',
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      await expectLater(
        find.byType(AtomMatrixTableWidget),
        matchesGoldenFile('goldens/atom_matrix_table_snapshot.png'),
      );
    },
  );
}
