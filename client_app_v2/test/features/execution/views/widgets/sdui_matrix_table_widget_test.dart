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
          'quotes',
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
          'quotes': I18nText(
            translations: {'en': 'Quotes', 'fi': 'Lainaukset'},
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
            uiPlotRatio: 0.85,
            isEvaluative: true,
            allowContextualOverride: true,
            levelNames: {'1': 'Basic Level'},
            levelBreakdown: {'1': '1/1'},
            evaluatedAtoms: [atom1],
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
      expect(find.text('85.0%'), findsOneWidget);
      expect(find.text('8.5 / 10'), findsOneWidget);
      expect(find.text('- Atom 1 Label'), findsOneWidget);
      expect(find.text('"Verbatim evidence quote from doc"'), findsOneWidget);
    },
  );
}
