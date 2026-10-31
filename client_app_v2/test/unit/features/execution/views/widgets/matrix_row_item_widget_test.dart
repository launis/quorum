import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:client_app/features/execution/views/widgets/matrix_row_item_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/theme/app_theme.dart';

void main() {
  Widget buildTestHarness(
    MatrixScorecardRowDto matrix, {
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
  }) {
    final child = MatrixRowItemWidget(matrix: matrix);
    return MaterialApp(
      theme: theme ?? AppTheme.light,
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: width != null ? SizedBox(width: width, child: child) : child,
        ),
      ),
    );
  }

  group('MatrixRowItemWidget Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders localized label, evaluative/override indicators, XAI justification, level breakdown, scores, and inner SDUI blocks',
      (WidgetTester tester) async {
        const matrix = MatrixScorecardRowDto(
          blockId: 'blk_01960000000070008000000000000001',
          name: 'strategic_alignment',
          labelI18n: I18nText(
            translations: {
              'en': 'Strategic Alignment',
              'fi': 'Strateginen linjaus',
            },
          ),
          score: 4.5,
          scaleMax: 5.0,
          normalizedScore: 87.5,
          trueAtoms: 7,
          totalAtoms: 8,
          rowExplanation: 'Strong evidence across levels 1 to 3.',
          isEvaluative: true,
          allowContextualOverride: true,
          levelBreakdown: {'1': '2/2', '2': '-'},
          levelNames: {'1': 'Foundation', '2': 'Advanced'},
          innerSduiBlocks: [
            SduiBlockDTO.heroInsight(text: 'Key executive takeaway'),
          ],
        );

        await tester.pumpWidget(buildTestHarness(matrix));
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.text('Strategic Alignment * **'), findsOneWidget);
        expect(find.text(l10n.xaiJustification), findsOneWidget);
        expect(
          find.text('Strong evidence across levels 1 to 3.'),
          findsOneWidget,
        );
        expect(find.text('4.5 / 5.0'), findsOneWidget);
        expect(find.text('87.5 %'), findsOneWidget);
        expect(find.text('7 / 8'), findsOneWidget);
        expect(find.text('Foundation'), findsOneWidget);
        expect(find.text('2/2'), findsOneWidget);
        expect(find.text('Advanced'), findsOneWidget);
        expect(find.text('-'), findsOneWidget);
        expect(find.text('Key executive takeaway'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 1: DLQ state renders semantic warning icon and neutral surface tokens in dark mode without overflow on narrow 120px width',
      (WidgetTester tester) async {
        const dlqMatrix = MatrixScorecardRowDto(
          blockId: 'blk_01960000000070008000000000000002',
          name: 'dlq_axis',
          labelI18n: I18nText(translations: {'en': 'DLQ Axis'}),
          score: null,
          scaleMax: null,
          normalizedScore: null,
          trueAtoms: 0,
          totalAtoms: 0,
          rowExplanation: 'Evaluation halted due to upstream parser error.',
          isEvaluative: false,
          tdaState: TDAState.dlq(
            userReason:
                'Upstream TDA validation failed with prolonged timeout and schema mismatch',
            backendTrace: 'TraceID: 00-4bf92f3577b34da6a3ce929d0e0e4736-01',
          ),
        );

        await tester.pumpWidget(
          buildTestHarness(dlqMatrix, theme: AppTheme.dark, width: 120),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('DLQ Axis'), findsOneWidget);
        expect(find.text('-'), findsOneWidget);
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);

        final icon = tester.widget<Icon>(
          find.byIcon(Icons.warning_amber_rounded),
        );
        expect(icon.color, equals(AppSemanticColors.dark.warning));
      },
    );

    testWidgets(
      'Negative/Boundary 2: missing required translation in I18nText triggers Fail-Fast AppException',
      (WidgetTester tester) async {
        const invalidMatrix = MatrixScorecardRowDto(
          blockId: 'blk_01960000000070008000000000000003',
          name: 'empty_i18n_axis',
          labelI18n: I18nText(translations: {}),
        );

        await tester.pumpWidget(buildTestHarness(invalidMatrix));

        final exception = tester.takeException();
        expect(exception, isA<AppException>());
      },
    );
  });
}
