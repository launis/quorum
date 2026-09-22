import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/dialogs/create_report_dialog.dart';
import 'package:client_app/features/reports/views/execution_reports_view.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockReportsClient extends Mock implements ReportsClient {}

class MockStudioClient extends Mock implements StudioClient {}

class MockExecutionClient extends Mock implements ExecutionClient {}

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
      when(
        () => mockClient.listReports(testExecutionId),
      ).thenAnswer((_) async => [generatingSummary]);
      when(
        () => mockClient.getReport(testReportId),
      ).thenAnswer((_) async => generatingReport);
      when(
        () => mockClient.getPdfDownloadUrl(any()),
      ).thenReturn('http://localhost/api/reports/$testReportId/pdf');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [reportsClientProvider.overrideWithValue(mockClient)],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('fi'),
            home: Scaffold(
              body: ExecutionReportsView(executionId: testExecutionId),
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

  testWidgets(
    'CreateReportDialog filters output profiles strictly matching workflowId',
    (WidgetTester tester) async {
      final mockStudioClient = MockStudioClient();
      const profiles = [
        OutputProfile(
          id: 'prf_01b1d71000000001',
          workflowId: 'wor_01b1d71000000001',
          name: I18nText(
            translations: {
              'fi': 'Oma Työnkulkuni Profiili',
              'en': 'Target Workflow Profile',
            },
          ),
        ),
        OutputProfile(
          id: 'prf_01b1d71000000002',
          workflowId: 'wor_01b1d71000000002',
          name: I18nText(
            translations: {
              'fi': 'Toisen Työnkulun Profiili',
              'en': 'Other Workflow Profile',
            },
          ),
        ),
      ];
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenAnswer((_) async => profiles);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [studioClientProvider.overrideWithValue(mockStudioClient)],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('fi'),
            home: Scaffold(
              body: CreateReportDialog(
                executionId: 'exe_1234567890abcdef',
                workflowId: 'wor_01b1d71000000001',
              ),
            ),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(find.text('Oma Työnkulkuni Profiili'), findsOneWidget);
      expect(find.text('Toisen Työnkulun Profiili'), findsNothing);
    },
  );

  testWidgets(
    'CreateReportDialog resolves execution workflowId when widget.workflowId is null',
    (WidgetTester tester) async {
      final mockStudioClient = MockStudioClient();
      final mockExecClient = MockExecutionClient();
      const profiles = [
        OutputProfile(
          id: 'prf_01b1d71000000001',
          workflowId: 'wor_01b1d71000000001',
          name: I18nText(
            translations: {
              'fi': 'Dynaaminen Profiili',
              'en': 'Dynamic Profile',
            },
          ),
        ),
        OutputProfile(
          id: 'prf_01b1d71000000002',
          workflowId: 'wor_01b1d71000000002',
          name: I18nText(
            translations: {'fi': 'Väärä Profiili', 'en': 'Wrong Profile'},
          ),
        ),
      ];
      final execRecord = ExecutionRecord.fromJson({
        'id': 'exe_01b1d71000000001',
        'workflow_id': 'wor_01b1d71000000001',
        'target_locale': 'fi',
        'status': 'PASSED',
      });

      when(
        () => mockExecClient.getExecutionStatus('exe_01b1d71000000001'),
      ).thenAnswer((_) async => execRecord);
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenAnswer((_) async => profiles);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            studioClientProvider.overrideWithValue(mockStudioClient),
            executionClientProvider.overrideWithValue(mockExecClient),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('fi'),
            home: Scaffold(
              body: CreateReportDialog(executionId: 'exe_01b1d71000000001'),
            ),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      verify(
        () => mockExecClient.getExecutionStatus('exe_01b1d71000000001'),
      ).called(1);
      expect(find.text('Dynaaminen Profiili'), findsOneWidget);
      expect(find.text('Väärä Profiili'), findsNothing);
    },
  );

  testWidgets(
    'CreateReportDialog shows informational warning when no profiles match workflow',
    (WidgetTester tester) async {
      final mockStudioClient = MockStudioClient();
      const profiles = [
        OutputProfile(
          id: 'prf_01b1d71000000002',
          workflowId: 'wor_01b1d71000000002',
          name: I18nText(
            translations: {'fi': 'Muu Profiili', 'en': 'Other Profile'},
          ),
        ),
      ];
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenAnswer((_) async => profiles);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [studioClientProvider.overrideWithValue(mockStudioClient)],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('fi'),
            home: Scaffold(
              body: CreateReportDialog(
                executionId: 'exe_1234567890abcdef',
                workflowId: 'wor_01b1d71000000099',
              ),
            ),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(
        find.text('Tälle työnkululle ei löytynyt sopivia tulosteprofiileja.'),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'ExecutionReportsView mounts horizontal SingleChildScrollView in _buildRowsTab',
    (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1280, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final readySummary = ReportArtifactSummary(
        id: testReportId,
        executionId: testExecutionId,
        profileId: 'prf_01b1d71000000001',
        locale: 'fi',
        title: 'Raportti (Valmis)',
        status: ReportStatus.ready,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final readyReport = ReportArtifact(
        id: testReportId,
        executionId: testExecutionId,
        workflowId: 'wf_test',
        profileId: 'prf_01b1d71000000001',
        locale: 'fi',
        title: 'Raportti (Valmis)',
        status: ReportStatus.ready,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      const rowItem = ReportRowItem(
        executionId: testExecutionId,
        reportId: testReportId,
        metricKey: 'metric_01',
        metricLabel: 'Pitkä metriikkaotsikko ilman renderflex ylivuotoa',
        score: 4.5,
        maxScale: 5.0,
        weight: 1.0,
        reasoning: 'Perustelu',
        quote: 'Sitaatti',
      );

      when(
        () => mockClient.listReports(testExecutionId),
      ).thenAnswer((_) async => [readySummary]);
      when(
        () => mockClient.getReport(testReportId),
      ).thenAnswer((_) async => readyReport);
      when(
        () => mockClient.getReportRows(testReportId),
      ).thenAnswer((_) async => [rowItem]);
      when(
        () => mockClient.getPdfDownloadUrl(any()),
      ).thenReturn('http://localhost/api/reports/$testReportId/pdf');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [reportsClientProvider.overrideWithValue(mockClient)],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('fi'),
            home: Scaffold(
              body: ExecutionReportsView(executionId: testExecutionId),
            ),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Switch to tabular rows tab
      await tester.tap(find.text('Rividata & Taulukot'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(find.byType(DataTable), findsOneWidget);
      final horizontalScroll = find.ancestor(
        of: find.byType(DataTable),
        matching: find.byWidgetPredicate(
          (w) =>
              w is SingleChildScrollView &&
              w.scrollDirection == Axis.horizontal,
        ),
      );
      expect(horizontalScroll, findsOneWidget);
    },
  );
}
