import 'dart:typed_data';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/execution_reports_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:file_picker/file_picker.dart';
import 'package:file_picker/src/platform/file_picker_platform_interface.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockReportsClient extends Mock implements ReportsClient {}

class FakeFilePickerPlatform extends FilePickerPlatform {
  final List<Map<String, Object?>> saveFileCalls = [];

  @override
  Future<String?> saveFile({
    String? dialogTitle,
    String? fileName,
    String? initialDirectory,
    FileType type = FileType.any,
    List<String>? allowedExtensions,
    Uint8List? bytes,
    bool lockParentWindow = false,
  }) async {
    saveFileCalls.add({
      'dialogTitle': dialogTitle,
      'fileName': fileName,
      'type': type,
      'allowedExtensions': allowedExtensions,
      'bytes': bytes,
      'lockParentWindow': lockParentWindow,
    });
    return 'C:\\Users\\Test\\Downloads\\$fileName';
  }
}

void main() {
  late MockReportsClient mockClient;
  late FakeFilePickerPlatform fakeFilePicker;

  const validExecutionId = 'exec_01960000000070008000000000000001';
  const validReportId = 'rep_01960000000070008000000000000001';
  const validWorkflowId = 'wf_01960000000070008000000000000001';
  const validProfileId = 'prf_01960000000070008000000000000001';

  final now = DateTime.utc(2026, 11, 1);

  final readySummary = ReportArtifactSummary(
    id: validReportId,
    executionId: validExecutionId,
    profileId: validProfileId,
    locale: 'fi',
    title: 'Executive Synthesis Report',
    status: ReportStatus.ready,
    createdAt: now,
    updatedAt: now,
  );

  final readyReport = ReportArtifact(
    id: validReportId,
    executionId: validExecutionId,
    workflowId: validWorkflowId,
    profileId: validProfileId,
    locale: 'fi',
    title: 'Executive Synthesis Report',
    status: ReportStatus.ready,
    metadata: const ReportMetadata(
      costUsd: 0.0425,
      durationMs: 1240,
      tokensUsed: 4200,
      thinkingTokens: 800,
      llmModel: 'gemini-2.5-pro',
      provider: 'vertex_ai',
    ),
    storagePaths: const ReportStoragePaths(
      pdfPath: '/data/reports/rep_1.pdf',
      sduiJsonPath: '/data/reports/rep_1.json',
      excelPath: '/data/reports/rep_1.xlsx',
      csvPath: '/data/reports/rep_1.csv',
    ),
    createdAt: now,
    updatedAt: now,
  );

  setUp(() {
    mockClient = MockReportsClient();
    fakeFilePicker = FakeFilePickerPlatform();
    FilePickerPlatform.instance = fakeFilePicker;
  });

  Widget buildHarness({Locale locale = const Locale('fi'), ThemeData? theme}) {
    return ProviderScope(
      overrides: [reportsClientProvider.overrideWithValue(mockClient)],
      child: MaterialApp(
        theme: theme ?? AppTheme.light,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: locale,
        home: const ExecutionReportsView(
          executionId: validExecutionId,
          workflowId: validWorkflowId,
        ),
      ),
    );
  }

  group('ExecutionReportsView Hardening & ISTQB Widget Tests', () {
    testWidgets(
      'Positive: renders ready report, localized format actions (PDF, Excel, CSV), interactive SDUI tab, and localized metadata tab',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1280, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        when(
          () => mockClient.listReports(validExecutionId),
        ).thenAnswer((_) async => [readySummary]);
        when(
          () => mockClient.getReport(validReportId),
        ).thenAnswer((_) async => readyReport);
        when(() => mockClient.getReportSdui(validReportId)).thenAnswer(
          (_) async => const ReportDataDto(
            executionId: validExecutionId,
            workflowId: validWorkflowId,
            profileId: validProfileId,
            innerSduiBlocks: [
              SduiBlockDTO.heroInsight(text: 'Verified SDUI Insight'),
            ],
          ),
        );
        when(
          () => mockClient.getPdfDownloadUrl(any()),
        ).thenReturn('/api/v2/reports/$validReportId/pdf');
        when(
          () => mockClient.downloadPdf(validReportId),
        ).thenAnswer((_) async => Uint8List.fromList([1, 2, 3]));

        await tester.pumpWidget(buildHarness(locale: const Locale('en')));
        await tester.pumpAndSettle();

        final l10nEn = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.byType(AppErrorBoundary), findsWidgets);
        expect(find.text('Verified SDUI Insight'), findsOneWidget);

        final pdfBtn = find.widgetWithText(
          OutlinedButton,
          l10nEn.reportFormatPdf,
        );
        final excelBtn = find.widgetWithText(
          OutlinedButton,
          l10nEn.reportFormatExcel,
        );
        final csvBtn = find.widgetWithText(
          OutlinedButton,
          l10nEn.reportFormatCsv,
        );
        expect(pdfBtn, findsOneWidget);
        expect(excelBtn, findsOneWidget);
        expect(csvBtn, findsOneWidget);

        await tester.tap(pdfBtn);
        await tester.pumpAndSettle();
        verify(() => mockClient.downloadPdf(validReportId)).called(1);
        expect(fakeFilePicker.saveFileCalls.length, 1);

        // Navigate to Metadata tab and verify localized labels
        await tester.tap(find.text(l10nEn.tabTelemetryMetadata));
        await tester.pumpAndSettle();

        expect(find.text(l10nEn.reportMetaSectionExecution), findsOneWidget);
        expect(find.text(l10nEn.reportMetaSectionFinOps), findsOneWidget);
        expect(find.text(l10nEn.reportMetaSectionStoragePaths), findsOneWidget);
        expect(find.text('\$0.0425'), findsOneWidget);
        expect(find.text('gemini-2.5-pro'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 1: renders empty reports placeholder when listReports returns empty list and handles compact mobile viewport (<800px) without overflow',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(420, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        when(
          () => mockClient.listReports(validExecutionId),
        ).thenAnswer((_) async => []);

        await tester.pumpWidget(
          buildHarness(locale: const Locale('fi'), theme: AppTheme.dark),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.reportsCountSubtitle(0)), findsOneWidget);
        expect(find.byIcon(Icons.description_outlined), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 2: renders failed report state with error message and disables PDF/Excel/CSV download buttons when status is failed',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(480, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        final failedSummary = ReportArtifactSummary(
          id: validReportId,
          executionId: validExecutionId,
          profileId: validProfileId,
          locale: 'fi',
          title: 'Failed Synthesis Report',
          status: ReportStatus.failed,
          createdAt: now,
          updatedAt: now,
        );

        final failedReport = ReportArtifact(
          id: validReportId,
          executionId: validExecutionId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          locale: 'fi',
          title: 'Failed Synthesis Report',
          status: ReportStatus.failed,
          errorMessage: 'SYNTHESIS_ERROR: Missing upstream matrix state.',
          createdAt: now,
          updatedAt: now,
        );

        when(
          () => mockClient.listReports(validExecutionId),
        ).thenAnswer((_) async => [failedSummary]);
        when(
          () => mockClient.getReport(validReportId),
        ).thenAnswer((_) async => failedReport);
        when(
          () => mockClient.getPdfDownloadUrl(any()),
        ).thenReturn('/api/v2/reports/$validReportId/pdf');

        await tester.pumpWidget(buildHarness(locale: const Locale('fi')));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.reportGenerationFailedNotice), findsOneWidget);
        expect(
          find.text('SYNTHESIS_ERROR: Missing upstream matrix state.'),
          findsOneWidget,
        );

        // Verify download buttons are disabled when status != ready
        final pdfButton = tester.widget<OutlinedButton>(
          find.widgetWithText(OutlinedButton, l10nFi.reportFormatPdf),
        );
        final excelButton = tester.widget<OutlinedButton>(
          find.widgetWithText(OutlinedButton, l10nFi.reportFormatExcel),
        );
        final csvButton = tester.widget<OutlinedButton>(
          find.widgetWithText(OutlinedButton, l10nFi.reportFormatCsv),
        );
        expect(pdfButton.onPressed, isNull);
        expect(excelButton.onPressed, isNull);
        expect(csvButton.onPressed, isNull);
      },
    );
  });
}
