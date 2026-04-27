import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets('AtomMatrixTableWidget renders table correctly with matrix data', (
    WidgetTester tester,
  ) async {
    final matrices = [
      const MatrixScorecardRowDto(
        blockId: 'block_1',
        labelFi: 'Kognitio',
        labelEn: 'Cognition',
        name: 'Cognition',
        score: 3.5,
        scaleMax: 5.0,
        trueAtoms: 5,
        totalAtoms: 10,
        levelBreakdown: {'Level 1': '3 / 5', 'Level 2': '2 / 5'},
      ),
    ];

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          // Set a large screen size to render the DataTable instead of mobile list
          home: MediaQuery(
            data: const MediaQueryData(size: Size(800, 600)),
            child: Scaffold(body: AtomMatrixTableWidget(matrices: matrices)),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Kognitio'), findsOneWidget);
    expect(find.text('5 / 10'), findsOneWidget);
    expect(find.text('Level 1'), findsOneWidget);
    expect(find.text('3 / 5'), findsOneWidget);
    expect(find.text('Level 2'), findsOneWidget);
    expect(find.text('2 / 5'), findsOneWidget);
  });

  testWidgets(
    'AtomMatrixTableWidget renders mobile list correctly on small screens',
    (WidgetTester tester) async {
      final matrices = [
        const MatrixScorecardRowDto(
          blockId: 'block_1',
          labelFi: 'Kognitio',
          labelEn: 'Cognition',
          name: 'Cognition',
          score: 3.5,
          scaleMax: 5.0,
          trueAtoms: 5,
          totalAtoms: 10,
          levelBreakdown: {'Level 1': '3 / 5'},
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            // Small screen size to trigger mobile layout
            home: MediaQuery(
              data: const MediaQueryData(size: Size(400, 800)),
              child: Scaffold(body: AtomMatrixTableWidget(matrices: matrices)),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // ExpansionTile should be present
      expect(find.text('Kognitio'), findsOneWidget);
      expect(find.textContaining('5 / 10'), findsWidgets);

      // Tap to expand
      await tester.tap(find.text('Kognitio'));
      await tester.pumpAndSettle();

      expect(find.text('Level 1'), findsOneWidget);
      expect(find.text('3 / 5'), findsOneWidget);
    },
  );

  testWidgets(
    'AtomMatrixTableWidget renders nothing when levelBreakdown is null',
    (WidgetTester tester) async {
      final matrices = [
        const MatrixScorecardRowDto(
          blockId: 'block_1',
          labelFi: 'Kognitio',
          labelEn: 'Cognition',
          name: 'Cognition',
          score: 3.5,
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: AtomMatrixTableWidget(matrices: matrices)),
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
