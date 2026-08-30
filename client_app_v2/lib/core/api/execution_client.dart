import 'package:dio/dio.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_client.g.dart';

/// Execution API Client Provider
@Riverpod(keepAlive: true)
ExecutionClient executionClient(Ref ref) {
  return ExecutionClient(ref.watch(apiClientProvider));
}

/// Client for interacting with the V2 Executions API.
///
/// Adheres to the De-Generator Policy: Returns raw JSON maps instead of
/// generated Dart models to allow maximum flexibility for SDUI responses.
class ExecutionClient {
  final Dio _dio;

  ExecutionClient(this._dio);

  /// Starts a new workflow execution using [ExecutionCreateRequestDto].
  ///
  /// Validates Fail-Fast: Any HTTP errors like 400 or 500 will be caught by
  /// the ErrorInterceptor and thrown as an AppException.
  Future<Map<String, dynamic>> startExecution({
    required ExecutionCreateRequestDto request,
  }) async {
    final response = await _dio.post(
      '/execution/executions/',
      data: request.toJson(),
    );

    return response.data as Map<String, dynamic>;
  }

  /// Manually triggers a backend Rehydration for an interrupted/FAILED execution.
  /// Used alongside Riverpod Mutations for Optimistic UI updates.
  Future<Map<String, dynamic>> resumeExecution(String executionId) async {
    final response = await _dio.post(
      '/execution/executions/$executionId/resume',
    );
    return response.data as Map<String, dynamic>;
  }

  /// Retrieves the current status and results of an execution.
  Future<Map<String, dynamic>> getExecutionStatus(String executionId) async {
    final response = await _dio.get('/execution/executions/$executionId');
    return response.data as Map<String, dynamic>;
  }

  /// Retrieves the dynamically assembled SDUI render blueprint for an execution.
  Future<Map<String, dynamic>> renderExecution(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    final response = await _dio.get(
      '/execution/executions/$executionId/render',
      queryParameters: {'lang': lang, 'profile_id': variant},
    );
    return response.data as Map<String, dynamic>;
  }

  /// Manually overrides an atom's score and logic (Epic 91 Phase 4).
  Future<Map<String, dynamic>> overrideAtom({
    required String executionId,
    required String atomId,
    required Map<String, dynamic> payload,
  }) async {
    final response = await _dio.patch(
      '/execution/executions/$executionId/atoms/$atomId/override',
      data: payload,
    );
    return response.data as Map<String, dynamic>;
  }
}
