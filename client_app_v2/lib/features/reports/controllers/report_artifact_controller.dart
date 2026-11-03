import 'dart:async';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'report_artifact_controller.g.dart';

// Phase 3, Step 3: Polling interval and transient network/503 classifier for compiling reports
const _kReportPollInterval = Duration(seconds: 3);

bool _isTransientPollingError(Object error) {
  if (error is AppException) {
    final status = error.status;
    final code = error.errorCode;
    return status == 502 ||
        status == 503 ||
        status == 504 ||
        status == 408 ||
        status == 0 ||
        code == 'SERVICE_UNAVAILABLE' ||
        code == 'NETWORK_FATAL' ||
        code == 'TIMEOUT';
  }
  if (error is DioException) {
    final wrapped = error.error;
    if (wrapped != null && _isTransientPollingError(wrapped)) {
      return true;
    }
    final statusCode = error.response?.statusCode;
    if (statusCode == 502 ||
        statusCode == 503 ||
        statusCode == 504 ||
        statusCode == 408) {
      return true;
    }
    return error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError;
  }
  return false;
}

bool _isCompilingStatus(ReportStatus status) =>
    status == ReportStatus.generating || status == ReportStatus.pending;

/// Fetches the list of all report artifacts for a given execution.
@riverpod
Future<List<ReportArtifactSummary>> executionReports(
  Ref ref,
  String executionId,
) async {
  final currentState = ref.isFirstBuild
      ? const AsyncValue<List<ReportArtifactSummary>>.loading()
      : ref.container.read(executionReportsProvider(executionId));
  final previous = switch (currentState) {
    AsyncData(:final value) => value,
    _ => null,
  };
  final client = ref.watch(reportsClientProvider);
  final List<ReportArtifactSummary> reports;
  try {
    reports = await client.listReports(executionId);
  } catch (e, st) {
    final hadCompiling =
        previous != null && previous.any((r) => _isCompilingStatus(r.status));
    if (hadCompiling && _isTransientPollingError(e)) {
      ref
          .read(loggerServiceProvider)
          .warning(
            'ReportArtifactController',
            'Transient polling error while fetching executionReports($executionId); retaining prior compiling state.',
            e,
            st,
          );
      final timer = Timer(_kReportPollInterval, ref.invalidateSelf);
      ref.onDispose(timer.cancel);
      return previous;
    }
    ref
        .read(loggerServiceProvider)
        .error(
          'ReportArtifactController',
          'EXECUTION_REPORTS_FETCH_FAILED: Failed to fetch reports for execution $executionId',
          e,
          st,
        );
    rethrow;
  }

  // Self-invalidate after 3s interval while any report artifact is still compiling.
  final isAnyCompiling = reports.any((r) => _isCompilingStatus(r.status));
  if (isAnyCompiling) {
    final timer = Timer(_kReportPollInterval, ref.invalidateSelf);
    ref.onDispose(timer.cancel);
  }

  return reports;
}

/// Fetches the full detailed domain model for a report artifact.
@riverpod
Future<ReportArtifact> reportDetail(Ref ref, String reportId) async {
  final currentState = ref.isFirstBuild
      ? const AsyncValue<ReportArtifact>.loading()
      : ref.container.read(reportDetailProvider(reportId));
  final previous = switch (currentState) {
    AsyncData(:final value) => value,
    _ => null,
  };
  final client = ref.watch(reportsClientProvider);
  final ReportArtifact report;
  try {
    report = await client.getReport(reportId);
  } catch (e, st) {
    final hadCompiling =
        previous != null && _isCompilingStatus(previous.status);
    if (hadCompiling && _isTransientPollingError(e)) {
      ref
          .read(loggerServiceProvider)
          .warning(
            'ReportArtifactController',
            'Transient polling error while fetching reportDetail($reportId); retaining prior compiling state.',
            e,
            st,
          );
      final timer = Timer(_kReportPollInterval, ref.invalidateSelf);
      ref.onDispose(timer.cancel);
      return previous;
    }
    ref
        .read(loggerServiceProvider)
        .error(
          'ReportArtifactController',
          'REPORT_DETAIL_FETCH_FAILED: Failed to fetch report $reportId',
          e,
          st,
        );
    rethrow;
  }

  // Self-invalidate after 3s interval while report is compiling; invalidate downstream SDUI and row providers once ready.
  if (_isCompilingStatus(report.status)) {
    final timer = Timer(_kReportPollInterval, ref.invalidateSelf);
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
///
/// Retains alive state so imperative `ref.read` action dispatches from UI callbacks
/// do not dispose the notifier mid-flight.
@Riverpod(keepAlive: true)
class ReportArtifactActions extends _$ReportArtifactActions {
  @override
  AsyncValue<void> build() => const AsyncValue.data(null);

  Future<ReportArtifactSummary?> createReport({
    required String executionId,
    required CreateReportRequest request,
  }) async {
    state = const AsyncValue.loading();
    try {
      final client = ref.read(reportsClientProvider);
      final summary = await client.createReport(
        executionId: executionId,
        request: request,
      );
      if (ref.mounted) {
        ref.invalidate(executionReportsProvider(executionId));
        state = const AsyncValue.data(null);
      }
      return summary;
    } catch (e, st) {
      if (ref.mounted) {
        ref
            .read(loggerServiceProvider)
            .error(
              'ReportArtifactActions',
              'CREATE_REPORT_FAILED: Failed to create report for execution $executionId',
              e,
              st,
            );
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
        ref
            .read(loggerServiceProvider)
            .error(
              'ReportArtifactActions',
              'REGENERATE_REPORT_FAILED: Failed to regenerate report $reportId',
              e,
              st,
            );
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
        ref
            .read(loggerServiceProvider)
            .error(
              'ReportArtifactActions',
              'DELETE_REPORT_FAILED: Failed to delete report $reportId',
              e,
              st,
            );
        state = AsyncValue.error(e, st);
      }
      rethrow;
    }
  }
}
