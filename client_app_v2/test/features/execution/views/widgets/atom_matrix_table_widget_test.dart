import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  testWidgets('AtomMatrixTableWidget renders table correctly with matrix data', (
    WidgetTester tester,
  ) async {
    final matrices = [
      const MatrixScorecardRowDto(
        blockId: 'block_1',
        labelI18n: const I18nText(
          translations: {'fi': 'Kognitio', 'en': 'Cognition'},
        ),
        name: 'Cognition',
        score: 3.5,
        scaleMax: 5.0,
        trueAtoms: 5,
        totalAtoms: 10,
        levelBreakdown: {'1': '3 / 5', '2': '2 / 5'},
      ),
    ];

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          // Set a large screen size to render the DataTable instead of mobile list
          home: MediaQuery(
            data: const MediaQueryData(size: Size(800, 600)),
            child: Scaffold(
              body: AtomMatrixTableWidget(
                matrices: matrices,
                visibleColumns: const [
                  'label',
                  'score',
                  'normalized_score',
                  'distribution',
                ],
              ),
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Cognition *'), findsOneWidget);
    expect(find.text('3.5 / 5.0'), findsOneWidget);
    expect(find.text('1 - T1: 3 / 5'), findsOneWidget);
    expect(find.text('2 - T2: 2 / 5'), findsOneWidget);
  });

  testWidgets(
    'AtomMatrixTableWidget renders mobile list correctly on small screens',
    (WidgetTester tester) async {
      final matrices = [
        const MatrixScorecardRowDto(
          blockId: 'block_1',
          labelI18n: const I18nText(
            translations: {'fi': 'Kognitio', 'en': 'Cognition'},
          ),
          name: 'Cognition',
          score: 3.5,
          scaleMax: 5.0,
          trueAtoms: 5,
          totalAtoms: 10,
          levelBreakdown: {'1': '3 / 5'},
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            // Small screen size to trigger mobile layout
            home: MediaQuery(
              data: const MediaQueryData(size: Size(400, 800)),
              child: Scaffold(
                body: AtomMatrixTableWidget(
                  matrices: matrices,
                  visibleColumns: const [
                    'label',
                    'score',
                    'normalized_score',
                    'distribution',
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // ExpansionTile should be present
      expect(find.text('Cognition *'), findsOneWidget);
      expect(find.textContaining('3.5 / 5.0'), findsWidgets);

      // Tap to expand
      await tester.tap(find.text('Cognition *'));
      await tester.pumpAndSettle();

      expect(find.text('1 - T1: 3 / 5'), findsOneWidget);
    },
  );

  testWidgets(
    'AtomMatrixTableWidget renders nothing when levelBreakdown is null',
    (WidgetTester tester) async {
      final matrices = [
        const MatrixScorecardRowDto(
          blockId: 'block_1',
          labelI18n: const I18nText(
            translations: {'fi': 'Kognitio', 'en': 'Cognition'},
          ),
          name: 'Cognition',
          score: 3.5,
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(
              body: AtomMatrixTableWidget(
                matrices: matrices,
                visibleColumns: const [
                  'score',
                  'normalized_score',
                  'distribution',
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.byType(AtomMatrixTableWidget), findsOneWidget);
      expect(find.byType(DataTable), findsNothing);
      expect(find.byType(ListView), findsNothing);
    },
  );
}
