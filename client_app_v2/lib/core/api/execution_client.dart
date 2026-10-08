import 'package:dio/dio.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
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

    return ExecutionRecord.fromJson(response.data);
  }

  /// Manually triggers a backend Rehydration for an interrupted/FAILED execution.
  /// Used alongside Riverpod Mutations for Optimistic UI updates.
  Future<ExecutionRecord> resumeExecution(String executionId) async {
    final response = await _dio.post(
      '/execution/executions/$executionId/resume',
    );
    return ExecutionRecord.fromJson(response.data);
  }

  /// Retrieves the current status and results of an execution.
  Future<ExecutionRecord> getExecutionStatus(String executionId) async {
    final response = await _dio.get('/execution/executions/$executionId');
    return ExecutionRecord.fromJson(response.data);
  }

  /// Manually overrides an atom's score and logic.
  Future<GenericStatusResponseDto> overrideAtom({
    required String executionId,
    required String atomId,
    required HumanOverrideRequestDto payload,
  }) async {
    final response = await _dio.patch(
      '/execution/executions/$executionId/atoms/$atomId/override',
      data: payload.toJson(),
    );
    return GenericStatusResponseDto.fromJson(response.data);
  }
}
