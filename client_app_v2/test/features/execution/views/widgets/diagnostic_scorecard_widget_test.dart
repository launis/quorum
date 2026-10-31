import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
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
              axes: [
                MatrixScorecardRowDto(
                  blockId: 'blk_01965b88000070008000000000000001',
                  labelI18n: I18nText(
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
              visibleColumns: [
                'label',
                'score',
                'normalized_score',
                'distribution',
              ],
              executionId: 'exe_01965b88000070008000000000000001',
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
            axes: [],
            visibleColumns: [
              'label',
              'score',
              'normalized_score',
              'distribution',
            ],
            executionId: 'exe_01965b88000070008000000000000001',
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify it doesn't render anything
    expect(find.byType(AtomMatrixTableWidget), findsNothing);
  });

  testWidgets(
    'DiagnosticScorecardWidget skips rendering when visibleColumns is empty',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: const Scaffold(
            body: DiagnosticScorecardWidget(
              axes: [
                MatrixScorecardRowDto(
                  blockId: 'blk_01965b88000070008000000000000001',
                  labelI18n: I18nText(
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
              visibleColumns: [],
              executionId: 'exe_01965b88000070008000000000000001',
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.byType(AtomMatrixTableWidget), findsNothing);
    },
  );
}
