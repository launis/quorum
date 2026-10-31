import 'dart:typed_data';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'reports_client.g.dart';

/// Reports API Client Provider
@Riverpod(keepAlive: true)
ReportsClient reportsClient(Ref ref) {
  return ReportsClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with the V2 Report Artifacts REST API.
class ReportsClient {
  final Dio _dio;
  final LoggerService? _logger;
  static const StrictOpaqueIdConverter _idValidator = StrictOpaqueIdConverter();

  ReportsClient(this._dio, [this._logger]);

  void _validateOpaqueId(String id, String fieldName, String methodName) {
    try {
      _idValidator.fromJson(id);
    } on AppException catch (e, st) {
      _logger?.error(
        'ReportsClient',
        'Invalid $fieldName format "$id" for $methodName',
        e,
        st,
      );
      rethrow;
    }
  }

  T _parseResponse<T>(
    Response<Map<String, Object?>> response,
    T Function(Map<String, Object?>) parser,
    String methodName,
  ) {
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null response payload received in ReportsClient.$methodName',
      );
      _logger?.error(
        'ReportsClient',
        'Null response data for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return parser(data);
  }

  List<T> _parseListResponse<T>(
    Response<List<Object?>> response,
    T Function(Map<String, Object?>) itemParser,
    String methodName,
  ) {
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null list response payload received in ReportsClient.$methodName',
      );
      _logger?.error(
        'ReportsClient',
        'Null list response data for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return data
        .map((item) {
          if (item is! Map<String, Object?>) {
            final error = AppException.validation(
              'Malformed list element in ReportsClient.$methodName: expected Map<String, Object?>.',
            );
            _logger?.error(
              'ReportsClient',
              'Malformed list item for $methodName',
              error,
              StackTrace.current,
            );
            throw error;
          }
          return itemParser(item);
        })
        .toList(growable: false);
  }

  Uint8List _parseBytesResponse(
    Response<List<int>> response,
    String methodName,
  ) {
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null binary response payload received in ReportsClient.$methodName',
      );
      _logger?.error(
        'ReportsClient',
        'Null binary response data for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return Uint8List.fromList(data);
  }

  /// Initiates compilation of a materialized report artifact for a completed execution.
  Future<ReportArtifactSummary> createReport({
    required String executionId,
    required CreateReportRequest request,
  }) async {
    _validateOpaqueId(executionId, 'executionId', 'createReport');
    _validateOpaqueId(request.profileId, 'profileId', 'createReport');
    if (request.modelRegistryId != null) {
      _validateOpaqueId(
        request.modelRegistryId!,
        'modelRegistryId',
        'createReport',
      );
    }

    final response = await _dio.post<Map<String, Object?>>(
      '/executions/$executionId/reports',
      data: request.toJson(),
    );
    return _parseResponse(
      response,
      ReportArtifactSummary.fromJson,
      'createReport',
    );
  }

  /// Lists all materialized report artifacts compiled for an execution.
  Future<List<ReportArtifactSummary>> listReports(String executionId) async {
    _validateOpaqueId(executionId, 'executionId', 'listReports');

    final response = await _dio.get<List<Object?>>(
      '/executions/$executionId/reports',
    );
    return _parseListResponse(
      response,
      ReportArtifactSummary.fromJson,
      'listReports',
    );
  }

  /// Fetches the full domain model detail for a report artifact.
  Future<ReportArtifact> getReport(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'getReport');

    final response = await _dio.get<Map<String, Object?>>('/reports/$reportId');
    return _parseResponse(response, ReportArtifact.fromJson, 'getReport');
  }

  /// Retrieves the pre-compiled SDUI presentation JSON tree.
  Future<ReportDataDto> getReportSdui(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'getReportSdui');

    final response = await _dio.get<Map<String, Object?>>(
      '/reports/$reportId/sdui',
    );
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null response payload received in ReportsClient.getReportSdui',
      );
      _logger?.error(
        'ReportsClient',
        'Null response data for getReportSdui',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return safeIsolateRun(() => ReportDataDto.fromJson(data));
  }

  /// Retrieves tabular B2B evidence scorecard rows.
  Future<List<ReportRowItem>> getReportRows(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'getReportRows');

    final response = await _dio.get<List<Object?>>('/reports/$reportId/rows');
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null list response payload received in ReportsClient.getReportRows',
      );
      _logger?.error(
        'ReportsClient',
        'Null list response data for getReportRows',
        error,
        StackTrace.current,
      );
      throw error;
    }
    for (final item in data) {
      if (item is! Map<String, Object?>) {
        final error = AppException.validation(
          'Malformed list element in ReportsClient.getReportRows: expected Map<String, Object?>.',
        );
        _logger?.error(
          'ReportsClient',
          'Malformed list item for getReportRows',
          error,
          StackTrace.current,
        );
        throw error;
      }
    }
    return safeIsolateRun(
      () => data
          .cast<Map<String, Object?>>()
          .map(ReportRowItem.fromJson)
          .toList(growable: false),
    );
  }

  /// Re-enqueues report synthesis and formatting generation without re-running DAG.
  Future<ReportArtifactSummary> regenerateReport(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'regenerateReport');

    final response = await _dio.post<Map<String, Object?>>(
      '/reports/$reportId/regenerate',
    );
    return _parseResponse(
      response,
      ReportArtifactSummary.fromJson,
      'regenerateReport',
    );
  }

  /// Deletes a report artifact and its associated disk files.
  Future<void> deleteReport(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'deleteReport');

    await _dio.delete<void>('/reports/$reportId');
  }

  /// Downloads compiled binary PDF document for a report artifact.
  Future<Uint8List> downloadPdf(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'downloadPdf');

    final response = await _dio.get<List<int>>(
      '/reports/$reportId/pdf',
      options: Options(responseType: ResponseType.bytes),
    );
    return _parseBytesResponse(response, 'downloadPdf');
  }

  /// Downloads generated forensic Excel workbook for a report artifact.
  Future<Uint8List> downloadExcel(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'downloadExcel');

    final response = await _dio.get<List<int>>(
      '/reports/$reportId/excel',
      options: Options(responseType: ResponseType.bytes),
    );
    return _parseBytesResponse(response, 'downloadExcel');
  }

  /// Downloads flat CSV export for a report artifact.
  Future<Uint8List> downloadCsv(String reportId) async {
    _validateOpaqueId(reportId, 'reportId', 'downloadCsv');

    final response = await _dio.get<List<int>>(
      '/reports/$reportId/csv',
      options: Options(responseType: ResponseType.bytes),
    );
    return _parseBytesResponse(response, 'downloadCsv');
  }

  String _normalizeBaseUrl() {
    final base = _dio.options.baseUrl;
    return base.replaceAll(RegExp(r'/+$'), '');
  }

  /// Download URL builders for direct browser/file streaming
  String getPdfDownloadUrl(String reportId) {
    _validateOpaqueId(reportId, 'reportId', 'getPdfDownloadUrl');
    return '${_normalizeBaseUrl()}/reports/$reportId/pdf';
  }

  String getExcelDownloadUrl(String reportId) {
    _validateOpaqueId(reportId, 'reportId', 'getExcelDownloadUrl');
    return '${_normalizeBaseUrl()}/reports/$reportId/excel';
  }

  String getCsvDownloadUrl(String reportId) {
    _validateOpaqueId(reportId, 'reportId', 'getCsvDownloadUrl');
    return '${_normalizeBaseUrl()}/reports/$reportId/csv';
  }
}
