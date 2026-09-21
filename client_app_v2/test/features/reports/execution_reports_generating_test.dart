import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/execution_reports_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockReportsClient extends Mock implements ReportsClient {}

void main() {
  late MockReportsClient mockClient;

  const testExecutionId = 'exe_1234567890abcdef';
  const testReportId = 'rep_1234567890abcdef';

  final generatingSummary = ReportArtifactSummary(
    id: testReportId,
    executionId: testExecutionId,
    profileId: 'prf_01b1d71000000001',
    locale: 'fi',
    title: 'Raportti (Luodaan)',
    status: ReportStatus.generating,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  final generatingReport = ReportArtifact(
    id: testReportId,
    executionId: testExecutionId,
    workflowId: 'wf_test',
    profileId: 'prf_01b1d71000000001',
    locale: 'fi',
    title: 'Raportti (Luodaan)',
    status: ReportStatus.generating,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  setUp(() {
    mockClient = MockReportsClient();
  });

  testWidgets(
    'ExecutionReportsView does not eagerly fetch SDUI or rows when report status is generating',
    (WidgetTester tester) async {
      when(() => mockClient.listReports(testExecutionId))
          .thenAnswer((_) async => [generatingSummary]);
      when(() => mockClient.getReport(testReportId))
          .thenAnswer((_) async => generatingReport);
      when(() => mockClient.getPdfDownloadUrl(any()))
          .thenReturn('http://localhost/api/reports/$testReportId/pdf');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            reportsClientProvider.overrideWithValue(mockClient),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('fi'),
            home: Scaffold(
              body: ExecutionReportsView(
                executionId: testExecutionId,
              ),
            ),
          ),
        ),
      );

      // Pump to resolve executionReportsProvider and initial build
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // REGRESSION ASSERTION:
      // While report is generating, neither getReportSdui nor getReportRows should be called.
      verifyNever(() => mockClient.getReportSdui(any()));
      verifyNever(() => mockClient.getReportRows(any()));
    },
  );
}
