import 'package:dio/dio.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_client.g.dart';

/// Execution API Client Provider
@Riverpod(keepAlive: true)
ExecutionClient executionClient(Ref ref) {
  return ExecutionClient(ref.watch(apiClientProvider));
}

/// Client for interacting with the V2 Executions API.
class ExecutionClient {
  final Dio _dio;

  ExecutionClient(this._dio);

  /// Starts a new workflow execution using [ExecutionCreateRequestDto].
  ///
  /// Validates Fail-Fast: Any HTTP errors like 400 or 500 will be caught by
  /// the ErrorInterceptor and thrown as an AppException.
  Future<ExecutionRecord> startExecution({
    required ExecutionCreateRequestDto request,
  }) async {
    final response = await _dio.post(
      '/execution/executions/',
      data: request.toJson(),
    );

    return ExecutionRecord.fromJson(response.data as Map<String, dynamic>);
  }

  /// Manually triggers a backend Rehydration for an interrupted/FAILED execution.
  /// Used alongside Riverpod Mutations for Optimistic UI updates.
  Future<ExecutionRecord> resumeExecution(String executionId) async {
    final response = await _dio.post(
      '/execution/executions/$executionId/resume',
    );
    return ExecutionRecord.fromJson(response.data as Map<String, dynamic>);
  }

  /// Retrieves the current status and results of an execution.
  Future<ExecutionRecord> getExecutionStatus(String executionId) async {
    final response = await _dio.get('/execution/executions/$executionId');
    return ExecutionRecord.fromJson(response.data as Map<String, dynamic>);
  }

  /// Retrieves the dynamically assembled SDUI render blueprint for an execution.
  ///
  /// Automatically polls when synthesis is pending (HTTP 202).
  Future<ReportDataDto> renderExecution(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
    void Function(String? message)? onProgress,
  }) async {
    int attempts = 0;
    final maxAttempts = SystemConcurrency.pollingMaxAttempts.value;

    while (true) {
      final response = await _dio.get(
        '/execution/executions/$executionId/render',
        queryParameters: {'lang': lang, 'profile_id': variant},
      );

      final data = response.data;
      if (response.statusCode == 202 ||
          (data is Map<String, dynamic> &&
              data['status']?.toString().toLowerCase() == 'pending')) {
        final msg =
            data is Map<String, dynamic> ? data['message'] as String? : null;
        onProgress?.call(msg);

        attempts++;
        if (attempts >= maxAttempts) {
          throw AppException.network(
            'Timeout waiting for synthesis to complete.',
          ).copyWith(extensions: const {'error_code': 'UPSTREAM_TIMEOUT'});
        }
        await Future.delayed(const Duration(seconds: 2));
        continue;
      }

      return ReportDataDto.fromJson(data as Map<String, dynamic>);
    }
  }

  /// Manually overrides an atom's score and logic.
  Future<GenericStatusResponseDto> overrideAtom({
    required String executionId,
    required String atomId,
    required Map<String, dynamic> payload,
  }) async {
    final response = await _dio.patch(
      '/execution/executions/$executionId/atoms/$atomId/override',
      data: payload,
    );
    return GenericStatusResponseDto.fromJson(
      response.data as Map<String, dynamic>,
    );
  }
}
