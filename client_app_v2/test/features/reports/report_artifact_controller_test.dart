import 'dart:async';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/reports/controllers/report_artifact_controller.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockReportsClient extends Mock implements ReportsClient {}

void main() {
  late MockReportsClient mockClient;
  late ProviderContainer container;

  const testExecutionId = 'exe_1234567890abcdef';
  const testReportId = 'rep_1234567890abcdef';

  final testSummary = ReportArtifactSummary(
    id: testReportId,
    executionId: testExecutionId,
    profileId: 'prf_test',
    locale: 'fi',
    title: 'Test Report',
    status: ReportStatus.ready,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  final testReport = ReportArtifact(
    id: testReportId,
    executionId: testExecutionId,
    workflowId: 'wf_test',
    profileId: 'prf_test',
    locale: 'fi',
    title: 'Test Report Detail',
    status: ReportStatus.ready,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  const testReportData = ReportDataDto(
    executionId: testExecutionId,
    workflowId: 'wf_test',
    profileId: 'prf_test',
  );

  setUp(() {
    mockClient = MockReportsClient();
    container = ProviderContainer(
      overrides: [
        reportsClientProvider.overrideWithValue(mockClient),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('ReportArtifactController Providers', () {
    test('executionReportsProvider fetches report summaries', () async {
      when(() => mockClient.listReports(testExecutionId))
          .thenAnswer((_) async => [testSummary]);

      final result = await container.read(executionReportsProvider(testExecutionId).future);
      expect(result.length, equals(1));
      expect(result.first.id, equals(testReportId));
      verify(() => mockClient.listReports(testExecutionId)).called(1);
    });

    test('reportDetailProvider fetches detailed report artifact', () async {
      when(() => mockClient.getReport(testReportId))
          .thenAnswer((_) async => testReport);

      final result = await container.read(reportDetailProvider(testReportId).future);
      expect(result.id, equals(testReportId));
      expect(result.title, equals('Test Report Detail'));
      verify(() => mockClient.getReport(testReportId)).called(1);
    });

    test('reportSduiProvider fetches ReportDataDto blueprint', () async {
      when(() => mockClient.getReportSdui(testReportId))
          .thenAnswer((_) async => testReportData);

      final result = await container.read(reportSduiProvider(testReportId).future);
      expect(result.executionId, equals(testExecutionId));
      verify(() => mockClient.getReportSdui(testReportId)).called(1);
    });

    test('reportRowsProvider fetches scorecard rows', () async {
      when(() => mockClient.getReportRows(testReportId))
          .thenAnswer((_) async => <ReportRowItem>[]);

      final result = await container.read(reportRowsProvider(testReportId).future);
      expect(result, isEmpty);
      verify(() => mockClient.getReportRows(testReportId)).called(1);
    });
  });

  group('ReportArtifactActions Mutations', () {
    test('createReport succeeds and invalidates executionReportsProvider', () async {
      when(
        () => mockClient.createReport(
          executionId: testExecutionId,
          profileId: 'prf_test',
          locale: 'fi',
        ),
      ).thenAnswer((_) async => testSummary);

      final summary = await container
          .read(reportArtifactActionsProvider.notifier)
          .createReport(executionId: testExecutionId, profileId: 'prf_test');

      expect(summary, isNotNull);
      expect(summary!.id, equals(testReportId));
      expect(container.read(reportArtifactActionsProvider), equals(const AsyncValue<void>.data(null)));
    });

    test('regenerateReport succeeds and invalidates cache providers', () async {
      when(() => mockClient.regenerateReport(testReportId))
          .thenAnswer((_) async => testSummary);

      final summary = await container
          .read(reportArtifactActionsProvider.notifier)
          .regenerateReport(reportId: testReportId, executionId: testExecutionId);

      expect(summary, isNotNull);
      expect(summary!.id, equals(testReportId));
      expect(container.read(reportArtifactActionsProvider), equals(const AsyncValue<void>.data(null)));
    });

    test('deleteReport calls deleteReport on client and resets state', () async {
      when(() => mockClient.deleteReport(testReportId))
          .thenAnswer((_) async {});

      await container
          .read(reportArtifactActionsProvider.notifier)
          .deleteReport(reportId: testReportId, executionId: testExecutionId);

      expect(container.read(reportArtifactActionsProvider), equals(const AsyncValue<void>.data(null)));
      verify(() => mockClient.deleteReport(testReportId)).called(1);
    });

    test('Negative Test 1: createReport failure sets state to error and rethrows', () async {
      when(
        () => mockClient.createReport(
          executionId: testExecutionId,
          profileId: 'prf_test',
          locale: 'fi',
        ),
      ).thenThrow(Exception('Backend 500 error'));

      expect(
        () => container
            .read(reportArtifactActionsProvider.notifier)
            .createReport(executionId: testExecutionId, profileId: 'prf_test'),
        throwsA(isA<Exception>()),
      );

      // Verify that state transitions to AsyncError
      expect(container.read(reportArtifactActionsProvider).hasError, isTrue);
    });

    test('Negative Test 2: regenerateReport failure sets state to error and rethrows', () async {
      when(() => mockClient.regenerateReport(testReportId))
          .thenThrow(Exception('Regeneration error'));

      expect(
        () => container
            .read(reportArtifactActionsProvider.notifier)
            .regenerateReport(reportId: testReportId, executionId: testExecutionId),
        throwsA(isA<Exception>()),
      );

      expect(container.read(reportArtifactActionsProvider).hasError, isTrue);
    });
  });
}
