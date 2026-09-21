import 'dart:typed_data';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/execution_reports_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:file_picker/file_picker.dart';
import 'package:file_picker/src/platform/file_picker_platform_interface.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockReportsClient extends Mock implements ReportsClient {}

class FakeFilePickerPlatform extends FilePickerPlatform {
  final List<Map<String, dynamic>> saveFileCalls = [];

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

  const testExecutionId = 'exe_1234567890abcdef';
  const testReportId = 'rep_1234567890abcdef';

  final readySummary = ReportArtifactSummary(
    id: testReportId,
    executionId: testExecutionId,
    profileId: 'prf_01b1d71000000001',
    locale: 'fi',
    title: 'Tekoälyajokortti: Vuorovaikutus ja Ohjaus',
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
    title: 'Tekoälyajokortti: Vuorovaikutus ja Ohjaus',
    status: ReportStatus.ready,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  setUp(() {
    mockClient = MockReportsClient();
    fakeFilePicker = FakeFilePickerPlatform();
    FilePickerPlatform.instance = fakeFilePicker;
  });

  testWidgets(
    'ExecutionReportsView triggers FilePicker.saveFile on PDF, Excel, and CSV download without crashing',
    (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1280, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      when(
        () => mockClient.listReports(testExecutionId),
      ).thenAnswer((_) async => [readySummary]);
      when(
        () => mockClient.getReport(testReportId),
      ).thenAnswer((_) async => readyReport);
      when(
        () => mockClient.getPdfDownloadUrl(any()),
      ).thenReturn('http://localhost/api/reports/$testReportId/pdf');
      when(
        () => mockClient.downloadPdf(testReportId),
      ).thenAnswer((_) async => Uint8List.fromList([1, 2, 3]));
      when(
        () => mockClient.downloadExcel(testReportId),
      ).thenAnswer((_) async => Uint8List.fromList([4, 5, 6]));
      when(
        () => mockClient.downloadCsv(testReportId),
      ).thenAnswer((_) async => Uint8List.fromList([7, 8, 9]));

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

      // 1. Verify PDF button triggers downloadPdf and FilePicker.saveFile
      final pdfBtn = find.widgetWithText(OutlinedButton, 'PDF');
      expect(pdfBtn, findsOneWidget);
      await tester.tap(pdfBtn);
      await tester.pumpAndSettle();

      verify(() => mockClient.downloadPdf(testReportId)).called(1);
      expect(fakeFilePicker.saveFileCalls.length, 1);
      expect(
        fakeFilePicker.saveFileCalls.last['fileName'],
        'report_$testReportId.pdf',
      );
      expect(fakeFilePicker.saveFileCalls.last['allowedExtensions'], ['pdf']);
      expect(fakeFilePicker.saveFileCalls.last['lockParentWindow'], true);

      // 2. Verify Excel button triggers downloadExcel and FilePicker.saveFile
      final excelBtn = find.widgetWithText(OutlinedButton, 'Excel');
      expect(excelBtn, findsOneWidget);
      await tester.tap(excelBtn);
      await tester.pumpAndSettle();

      verify(() => mockClient.downloadExcel(testReportId)).called(1);
      expect(fakeFilePicker.saveFileCalls.length, 2);
      expect(
        fakeFilePicker.saveFileCalls.last['fileName'],
        'report_$testReportId.xlsx',
      );
      expect(fakeFilePicker.saveFileCalls.last['allowedExtensions'], ['xlsx']);
      expect(fakeFilePicker.saveFileCalls.last['lockParentWindow'], true);

      // 3. Verify CSV button triggers downloadCsv and FilePicker.saveFile
      final csvBtn = find.widgetWithText(OutlinedButton, 'CSV');
      expect(csvBtn, findsOneWidget);
      await tester.tap(csvBtn);
      await tester.pumpAndSettle();

      verify(() => mockClient.downloadCsv(testReportId)).called(1);
      expect(fakeFilePicker.saveFileCalls.length, 3);
      expect(
        fakeFilePicker.saveFileCalls.last['fileName'],
        'report_$testReportId.csv',
      );
      expect(fakeFilePicker.saveFileCalls.last['allowedExtensions'], ['csv']);
      expect(fakeFilePicker.saveFileCalls.last['lockParentWindow'], true);
    },
  );
}
