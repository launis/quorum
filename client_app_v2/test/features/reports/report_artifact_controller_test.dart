import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/controllers/report_artifact_controller.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';

class MockReportsClient implements ReportsClient {
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<ReportArtifactSummary> createReport({
    required String executionId,
    required String profileId,
    String locale = 'fi',
    String? customPrefaceMd,
    String? modelRegistryId,
  }) async {
    // Yield to the event loop so that autoDispose has a chance to trigger
    await Future<void>.delayed(const Duration(milliseconds: 10));
    return ReportArtifactSummary(
      id: 'rep_1234567890abcdef',
      executionId: executionId,
      profileId: profileId,
      locale: locale,
      title: 'Test Report',
      status: ReportStatus.ready,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
}

void main() {
  test(
    'calling createReport imperatively via ref.read must succeed without disposed Ref StateError',
    () async {
      final container = ProviderContainer(
        overrides: [
          reportsClientProvider.overrideWithValue(MockReportsClient()),
        ],
      );
      addTearDown(container.dispose);

      // Calling createReport imperatively without an active UI widget watcher
      final summary = await container
          .read(reportArtifactActionsProvider.notifier)
          .createReport(executionId: 'exe_test', profileId: 'prf_test');

      expect(summary, isNotNull);
      expect(summary!.id, 'rep_1234567890abcdef');
    },
  );
}
