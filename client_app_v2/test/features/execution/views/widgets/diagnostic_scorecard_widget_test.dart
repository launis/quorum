import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  testWidgets(
    'DiagnosticScorecardWidget renders successfully and includes AtomMatrixTableWidget',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: const Scaffold(
            body: DiagnosticScorecardWidget(
              evaluativeMatrices: [
                MatrixScorecardRowDto(
                  blockId: 'm1',
                  labelI18n: const I18nText(
                    translations: {'fi': 'Testimatriisi', 'en': 'Test Matrix'},
                  ),
                  name: 'Test Matrix',
                  score: 4.5,
                  isEvaluative: true,
                  trueAtoms: 2,
                  totalAtoms: 2,
                  levelBreakdown: {'Level 1': '2 / 2'},
                ),
              ],
              informationalMatrices: [],
              visibleColumns: const [
                'label',
                'score',
                'normalized_score',
                'distribution',
              ],
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // We expect the matrix table to exist
      expect(find.byType(AtomMatrixTableWidget), findsOneWidget);

      // Check specific data from the mock
      expect(find.text('Test Matrix *'), findsWidgets);
    },
  );

  testWidgets('DiagnosticScorecardWidget renders empty state gracefully', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
        home: const Scaffold(
          body: DiagnosticScorecardWidget(
            evaluativeMatrices: [],
            informationalMatrices: [],
            visibleColumns: const [
              'label',
              'score',
              'normalized_score',
              'distribution',
            ],
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify it doesn't render anything
    expect(find.byType(AtomMatrixTableWidget), findsNothing);
  });
}
