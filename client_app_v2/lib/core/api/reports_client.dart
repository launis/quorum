import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'reports_client.g.dart';

/// Reports API Client Provider
@Riverpod(keepAlive: true)
ReportsClient reportsClient(Ref ref) {
  return ReportsClient(ref.watch(apiClientProvider));
}

/// Client for interacting with the V2 Report Artifacts REST API.
class ReportsClient {
  final Dio _dio;

  ReportsClient(this._dio);

  /// Initiates compilation of a materialized report artifact for a completed execution.
  Future<ReportArtifactSummary> createReport({
    required String executionId,
    required String profileId,
    String locale = 'fi',
    String? customPrefaceMd,
    String? modelRegistryId,
  }) async {
    final response = await _dio.post(
      '/executions/$executionId/reports',
      data: {
        'profile_id': profileId,
        'locale': locale,
        if (customPrefaceMd != null) 'custom_preface_md': customPrefaceMd,
        if (modelRegistryId != null) 'model_registry_id': modelRegistryId,
      },
    );
    return ReportArtifactSummary.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  /// Lists all materialized report artifacts compiled for an execution.
  Future<List<ReportArtifactSummary>> listReports(String executionId) async {
    final response = await _dio.get('/executions/$executionId/reports');
    final list = response.data as List<dynamic>;
    return list
        .map((item) => ReportArtifactSummary.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Fetches the full domain model detail for a report artifact.
  Future<ReportArtifact> getReport(String reportId) async {
    final response = await _dio.get('/reports/$reportId');
    return ReportArtifact.fromJson(response.data as Map<String, dynamic>);
  }

  /// Retrieves the pre-compiled SDUI presentation JSON tree.
  Future<Map<String, dynamic>> getReportSdui(String reportId) async {
    final response = await _dio.get('/reports/$reportId/sdui');
    return response.data as Map<String, dynamic>;
  }

  /// Retrieves tabular B2B evidence scorecard rows.
  Future<List<ReportRowItem>> getReportRows(String reportId) async {
    final response = await _dio.get('/reports/$reportId/rows');
    final list = response.data as List<dynamic>;
    return list
        .map((item) => ReportRowItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Re-enqueues report synthesis and formatting generation without re-running DAG.
  Future<ReportArtifactSummary> regenerateReport(String reportId) async {
    final response = await _dio.post('/reports/$reportId/regenerate');
    return ReportArtifactSummary.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  /// Deletes a report artifact and its associated disk files.
  Future<void> deleteReport(String reportId) async {
    await _dio.delete('/reports/$reportId');
  }

  /// Download URL builders for direct browser/file streaming
  String getPdfDownloadUrl(String reportId) => '${_dio.options.baseUrl}/reports/$reportId/pdf';
  String getExcelDownloadUrl(String reportId) => '${_dio.options.baseUrl}/reports/$reportId/excel';
  String getCsvDownloadUrl(String reportId) => '${_dio.options.baseUrl}/reports/$reportId/csv';
}
