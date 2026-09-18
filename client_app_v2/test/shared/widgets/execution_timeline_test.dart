import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/execution_timeline.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  Widget createTimelineWidget({
    required List<ExecutionStep> steps,
    bool compact = false,
  }) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('en'),
      home: Scaffold(
        body: ExecutionTimeline(steps: steps, compact: compact),
      ),
    );
  }

  testWidgets('ExecutionTimeline renders empty list with SizedBox.shrink', (
    tester,
  ) async {
    await tester.pumpWidget(createTimelineWidget(steps: []));
    await tester.pumpAndSettle();
    expect(find.byType(Card), findsNothing);
  });

  testWidgets(
    'ExecutionTimeline renders steps with labels and canonical status',
    (tester) async {
      final steps = [
        const ExecutionStep(
          id: 'stp_1',
          label: 'Step Ingestion',
          status: 'passed',
          durationMs: 1200,
          progress: 100,
        ),
        const ExecutionStep(
          id: 'stp_2',
          label: 'Step Analysis',
          status: 'running',
          progress: 45,
        ),
        const ExecutionStep(
          id: 'stp_3',
          label: 'Step Synthesis',
          status: 'failed',
          lastError: 'Quota exceeded',
          hasWarning: true,
        ),
      ];

      await tester.pumpWidget(createTimelineWidget(steps: steps));
      await tester.pump();

      expect(find.text('Step Ingestion'), findsOneWidget);
      expect(find.text('Step Analysis'), findsOneWidget);
      expect(find.text('Step Synthesis'), findsOneWidget);
      expect(find.text('Quota exceeded'), findsOneWidget);
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    },
  );
}
