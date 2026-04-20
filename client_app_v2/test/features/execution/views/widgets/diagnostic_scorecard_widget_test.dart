import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';
import 'package:client_app/features/execution/views/widgets/atom_matrix_table_widget.dart';
import 'package:client_app/shared/widgets/global_error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class FakeExecutionClient implements ExecutionClient {
  final bool shouldFail;

  FakeExecutionClient({this.shouldFail = false});

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<Map<String, dynamic>> getScorecard(String executionId) async {
    if (shouldFail) {
      throw Exception('Mock Error');
    }

    return {
      'execution_id': executionId,
      'workflow_id': 'wf_test',
      'global_average': 4.5,
      'evaluative_matrices': [
        {
          'block_id': 'm1',
          'label_fi': 'Testimatriisi',
          'label_en': 'Test Matrix',
          'score': 4.5,
          'is_evaluative': true,
          'true_atoms': 2,
          'total_atoms': 2,
          'level_breakdown': {
            'Level 1': {'true_atoms': 2, 'total_atoms': 2},
          },
        },
      ],
      'informational_matrices': [],
    };
  }
}

void main() {
  testWidgets(
    'DiagnosticScorecardWidget renders successfully and includes AtomMatrixTableWidget',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            executionClientProvider.overrideWithValue(FakeExecutionClient()),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: const Scaffold(
              body: DiagnosticScorecardWidget(executionId: 'exec_123'),
            ),
          ),
        ),
      );

      // Initial loading state
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Allow Isolate.run to execute in real async zone
      await tester.runAsync(() async {
        // Settle async fetch without timing out
        for (int i = 0; i < 50; i++) {
          await Future.delayed(const Duration(milliseconds: 100));
          await tester.pump();
          if (find.byType(CircularProgressIndicator).evaluate().isEmpty) {
            break;
          }
        }
      });
      await tester.pump();

      // Progress indicator is gone
      expect(find.byType(CircularProgressIndicator), findsNothing);

      // We expect the matrix table to exist
      expect(find.byType(AtomMatrixTableWidget), findsOneWidget);

      // Check specific data from the mock
      expect(find.text('Testimatriisi'), findsWidgets);
      expect(find.text('4.50'), findsOneWidget); // Global average formatted
    },
  );

  testWidgets('DiagnosticScorecardWidget renders error view when fetch fails', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          executionClientProvider.overrideWithValue(
            FakeExecutionClient(shouldFail: true),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const Scaffold(
            body: DiagnosticScorecardWidget(executionId: 'exec_failed'),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify Error View
    expect(find.byType(GlobalErrorView), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
  });
}
