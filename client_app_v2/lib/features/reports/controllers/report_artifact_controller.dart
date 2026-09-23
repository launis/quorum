import 'dart:async';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'report_artifact_controller.g.dart';

/// Fetches the list of all report artifacts for a given execution.
@riverpod
Future<List<ReportArtifactSummary>> executionReports(
  Ref ref,
  String executionId,
) async {
  final client = ref.watch(reportsClientProvider);
  final reports = await client.listReports(executionId);

  // If any report is still compiling, self-invalidate after 2s interval
  final isAnyCompiling = reports.any(
    (r) =>
        r.status == ReportStatus.generating || r.status == ReportStatus.pending,
  );
  if (isAnyCompiling) {
    final timer = Timer(const Duration(seconds: 2), () {
      ref.invalidateSelf();
    });
    ref.onDispose(timer.cancel);
  }

  return reports;
}

/// Fetches the full detailed domain model for a report artifact.
@riverpod
Future<ReportArtifact> reportDetail(Ref ref, String reportId) async {
  final client = ref.watch(reportsClientProvider);
  final report = await client.getReport(reportId);

  // If report is still compiling, self-invalidate after 2s interval.
  // When compilation transitions to ready, invalidate downstream artifact providers.
  if (report.status == ReportStatus.generating ||
      report.status == ReportStatus.pending) {
    final timer = Timer(const Duration(seconds: 2), () {
      ref.invalidateSelf();
    });
    ref.onDispose(timer.cancel);
  } else if (report.status == ReportStatus.ready) {
    ref.invalidate(reportSduiProvider(reportId));
    ref.invalidate(reportRowsProvider(reportId));
  }

  return report;
}

/// Fetches the pre-compiled SDUI data tree for rendering in SduiRenderer.
@riverpod
Future<ReportDataDto> reportSdui(Ref ref, String reportId) async {
  final client = ref.watch(reportsClientProvider);
  return await client.getReportSdui(reportId);
}

/// Fetches tabular B2B evidence scorecard rows.
@riverpod
Future<List<ReportRowItem>> reportRows(Ref ref, String reportId) async {
  final client = ref.watch(reportsClientProvider);
  return await client.getReportRows(reportId);
}

/// Controller managing report lifecycle mutations (create, regenerate, delete).
// Plan Step 1: Harden lifecycle with keepAlive: true to satisfy riverpod_autodispose_read_ban
@Riverpod(keepAlive: true)
class ReportArtifactActions extends _$ReportArtifactActions {
  @override
  AsyncValue<void> build() => const AsyncValue.data(null);

  Future<ReportArtifactSummary?> createReport({
    required String executionId,
    required String profileId,
    String locale = 'fi',
    String? customPrefaceMd,
    String? modelRegistryId,
  }) async {
    state = const AsyncValue.loading();
    try {
      final client = ref.read(reportsClientProvider);
      final summary = await client.createReport(
        executionId: executionId,
        profileId: profileId,
        locale: locale,
        customPrefaceMd: customPrefaceMd,
        modelRegistryId: modelRegistryId,
      );
      if (ref.mounted) {
        ref.invalidate(executionReportsProvider(executionId));
        state = const AsyncValue.data(null);
      }
      return summary;
    } catch (e, st) {
      if (ref.mounted) {
        state = AsyncValue.error(e, st);
      }
      rethrow;
    }
  }

  Future<ReportArtifactSummary?> regenerateReport({
    required String reportId,
    required String executionId,
  }) async {
    state = const AsyncValue.loading();
    try {
      final client = ref.read(reportsClientProvider);
      final summary = await client.regenerateReport(reportId);
      if (ref.mounted) {
        ref.invalidate(executionReportsProvider(executionId));
        ref.invalidate(reportDetailProvider(reportId));
        state = const AsyncValue.data(null);
      }
      return summary;
    } catch (e, st) {
      if (ref.mounted) {
        state = AsyncValue.error(e, st);
      }
      rethrow;
    }
  }

  Future<void> deleteReport({
    required String reportId,
    required String executionId,
  }) async {
    state = const AsyncValue.loading();
    try {
      final client = ref.read(reportsClientProvider);
      await client.deleteReport(reportId);
      if (ref.mounted) {
        ref.invalidate(executionReportsProvider(executionId));
        ref.invalidate(reportDetailProvider(reportId));
        state = const AsyncValue.data(null);
      }
    } catch (e, st) {
      if (ref.mounted) {
        state = AsyncValue.error(e, st);
      }
      rethrow;
    }
  }
}
