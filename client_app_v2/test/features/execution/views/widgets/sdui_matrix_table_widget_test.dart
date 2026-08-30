import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/sdui_matrix_table_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  testWidgets(
    'SduiMatrixTableWidget renders table with quotes and normalized_score',
    (WidgetTester tester) async {
      const atom1 = ScorecardAtomDto(
        atomId: 'atm_1',
        level: 1,
        levelName: 'Basic Level',
        claimLabel: 'Basic Claim',
        extractedFacts: {'f1': 'v1'},
        exactQuotes: [
          QuoteEvidenceDto(quote: 'Verbatim evidence quote from doc'),
        ],
        internalLogicEn: ReasoningStepDto(
          step1IdentifyPremise: 'p1',
          step2ScanSource: 's1',
          step3EvaluateAntiPatterns: 'a1',
          step4FinalConclusion: 'c1',
        ),
        status: ExecutionStatus.passed,
        semanticReasoning: 'Reasoning ok',
        contextualOverride: false,
        chartDisplayLabel: 'Atom 1 Label',
        visualIntent: VisualIntent.success,
      );

      final block = SduiMatrixTableBlock(
        title: const I18nText(
          translations: {'en': 'Test Matrix Table', 'fi': 'Testitaulukko'},
        ),
        matrixVisibleColumns: const [
          'label',
          'atomic_breakdown',
          'row_explanation',
          'criteria',
          'quotes',
          'source',
          'normalized_score',
          'score',
        ],
        matrixColumnLabels: const {
          'label': I18nText(
            translations: {'en': 'Dimension', 'fi': 'Ulottuvuus'},
          ),
          'atomic_breakdown': I18nText(
            translations: {'en': 'Breakdown', 'fi': 'Jakauma'},
          ),
          'row_explanation': I18nText(
            translations: {'en': 'Summary', 'fi': 'Selite'},
          ),
          'criteria': I18nText(
            translations: {'en': 'Criterion', 'fi': 'Kriteeri'},
          ),
          'quotes': I18nText(
            translations: {'en': 'Text Observation', 'fi': 'Tekstin havainto'},
          ),
          'source': I18nText(
            translations: {'en': 'Citation', 'fi': 'Lähdeviite'},
          ),
          'normalized_score': I18nText(
            translations: {'en': 'Normalized', 'fi': 'Normalisoitu'},
          ),
          'score': I18nText(translations: {'en': 'Score', 'fi': 'Pisteet'}),
        },
        axes: [
          const MatrixScorecardRowDto(
            blockId: 'axis_1',
            name: 'Executive Leadership',
            labelI18n: I18nText(translations: {'en': 'Executive Leadership'}),
            rowExplanation: 'Consistent executive leadership demonstrated.',
            scoreDisplayLabel: '8.5 / 10',
            normalizedScore: 85.0,
            uiPlotRatio: 0.85,
            isEvaluative: true,
            allowContextualOverride: true,
            levelNames: {'1': 'Basic Level'},
            levelBreakdown: {'1': '1/1'},
            evaluatedAtoms: [atom1],
            citedSourceTitle: 'Popper (1959)',
            citedSourceUrl: 'https://doi.org/10.1000/182',
          ),
        ],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1200, 800)),
            child: Scaffold(
              body: SingleChildScrollView(
                child: SduiMatrixTableWidget(block: block),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Test Matrix Table'), findsOneWidget);
      expect(find.text('Executive Leadership * **'), findsOneWidget);
      expect(
        find.text('Consistent executive leadership demonstrated.'),
        findsOneWidget,
      );
      expect(find.text('85.0 %'), findsOneWidget);
      expect(find.text('8.5 / 10'), findsOneWidget);
      expect(find.text('- Atom 1 Label'), findsOneWidget);
      expect(find.text('"Verbatim evidence quote from doc"'), findsOneWidget);
      expect(find.text('Popper (1959)'), findsOneWidget);
    },
  );

  testWidgets(
    'SduiMatrixTableWidget renders dash when quotes are empty across all levels',
    (WidgetTester tester) async {
      const atomNoQuotes = ScorecardAtomDto(
        atomId: 'atm_2',
        level: 1,
        levelName: 'Basic Level',
        claimLabel: 'Claim Without Quotes',
        extractedFacts: {},
        exactQuotes: [],
        internalLogicEn: ReasoningStepDto(
          step1IdentifyPremise: '',
          step2ScanSource: '',
          step3EvaluateAntiPatterns: '',
          step4FinalConclusion: '',
        ),
        status: ExecutionStatus.passed,
        semanticReasoning: '',
        contextualOverride: false,
        chartDisplayLabel: 'Atom 2 Label',
        visualIntent: VisualIntent.neutral,
      );

      final block = SduiMatrixTableBlock(
        title: const I18nText(
          translations: {'en': 'Test Matrix Table', 'fi': 'Testitaulukko'},
        ),
        matrixVisibleColumns: const ['label', 'quotes'],
        matrixColumnLabels: const {
          'label': I18nText(translations: {'en': 'Dimension'}),
          'quotes': I18nText(translations: {'en': 'Text Observation'}),
        },
        axes: [
          const MatrixScorecardRowDto(
            blockId: 'axis_2',
            name: 'Strategy Implementation',
            labelI18n: I18nText(
              translations: {'en': 'Strategy Implementation'},
            ),
            rowExplanation: 'Strategy explanation text.',
            scoreDisplayLabel: '5.0 / 10',
            uiPlotRatio: 0.5,
            isEvaluative: false,
            allowContextualOverride: false,
            levelNames: {'1': 'Basic Level'},
            levelBreakdown: {'1': '0/1'},
            evaluatedAtoms: [atomNoQuotes],
          ),
        ],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1200, 800)),
            child: Scaffold(
              body: SingleChildScrollView(
                child: SduiMatrixTableWidget(block: block),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Strategy Implementation'), findsOneWidget);
      expect(find.text('-'), findsOneWidget);
    },
  );

  testWidgets(
    'SduiMatrixTableWidget renders context_target badge in label column and dedicated columns',
    (WidgetTester tester) async {
      final block = SduiMatrixTableBlock(
        title: const I18nText(
          translations: {'en': 'Evaluated Targets', 'fi': 'Arvioidut kohteet'},
        ),
        matrixVisibleColumns: const [
          'label',
          'context_target',
          'row_explanation',
        ],
        matrixColumnLabels: const {
          'label': I18nText(translations: {'en': 'Dimension'}),
          'context_target': I18nText(translations: {'en': 'Target'}),
          'row_explanation': I18nText(translations: {'en': 'Row Explanation'}),
        },
        axes: [
          const MatrixScorecardRowDto(
            blockId: 'axis_dynamic',
            name: 'Risk Management',
            labelI18n: I18nText(translations: {'en': 'Risk Management'}),
            contextTarget: 'financials_q3.pdf',
            contextTargetLabel: I18nText(
              translations: {'en': 'financials_q3.pdf'},
            ),
            rowExplanation: 'Focus on downside protection.',
            isEvaluative: true,
            allowContextualOverride: false,
          ),
        ],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1200, 800)),
            child: Scaffold(
              body: SingleChildScrollView(
                child: SduiMatrixTableWidget(block: block),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Risk Management *'), findsOneWidget);
      // Badge in label cell and text in dedicated column
      expect(find.text('financials_q3.pdf'), findsNWidgets(2));
      expect(find.text('Focus on downside protection.'), findsOneWidget);
    },
  );
}
