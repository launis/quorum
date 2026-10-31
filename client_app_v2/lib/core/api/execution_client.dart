import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_client.g.dart';

/// Execution API Client Provider
@Riverpod(keepAlive: true)
ExecutionClient executionClient(Ref ref) {
  return ExecutionClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with the V2 Executions API.
class ExecutionClient {
  final Dio _dio;
  final LoggerService? _logger;
  static const StrictOpaqueIdConverter _idValidator = StrictOpaqueIdConverter();

  ExecutionClient(this._dio, [this._logger]);

  void _validateOpaqueId(String id, String fieldName, String methodName) {
    try {
      _idValidator.fromJson(id);
    } on AppException catch (e, st) {
      _logger?.error(
        'ExecutionClient',
        'Invalid $fieldName format "$id" for $methodName',
        e,
        st,
      );
      rethrow;
    }
  }

  void _validateNonEmptyId(String id, String fieldName, String methodName) {
    if (id.trim().isEmpty) {
      final error = AppException.validation(
        'Invalid $fieldName: "$id". Identifier must not be empty.',
      );
      _logger?.error(
        'ExecutionClient',
        'Empty $fieldName for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
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
        'Null response payload received in ExecutionClient.$methodName',
      );
      _logger?.error(
        'ExecutionClient',
        'Null response data for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return parser(data);
  }

  /// Starts a new workflow execution using [ExecutionCreateRequestDto].
  ///
  /// Validates Fail-Fast: Any HTTP errors like 400 or 500 will be caught by
  /// the ErrorInterceptor and thrown as an AppException.
  Future<ExecutionRecord> startExecution({
    required ExecutionCreateRequestDto request,
  }) async {
    _validateOpaqueId(request.workflowId, 'workflowId', 'startExecution');
    if (request.profileId != null) {
      _validateOpaqueId(request.profileId!, 'profileId', 'startExecution');
    }

    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/',
      data: request.toJson(),
    );

    return _parseResponse(response, ExecutionRecord.fromJson, 'startExecution');
  }

  /// Manually triggers a backend Rehydration for an interrupted/FAILED execution.
  /// Used alongside Riverpod Mutations for Optimistic UI updates.
  Future<ExecutionRecord> resumeExecution(String executionId) async {
    _validateOpaqueId(executionId, 'executionId', 'resumeExecution');

    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/$executionId/resume',
    );
    return _parseResponse(
      response,
      ExecutionRecord.fromJson,
      'resumeExecution',
    );
  }

  /// Retrieves the current status and results of an execution.
  Future<ExecutionRecord> getExecutionStatus(String executionId) async {
    _validateOpaqueId(executionId, 'executionId', 'getExecutionStatus');

    final response = await _dio.get<Map<String, Object?>>(
      '/execution/executions/$executionId',
    );
    return _parseResponse(
      response,
      ExecutionRecord.fromJson,
      'getExecutionStatus',
    );
  }

  /// Manually overrides an atom's score and logic.
  Future<GenericStatusResponseDto> overrideAtom({
    required String executionId,
    required String atomId,
    required HumanOverrideRequestDto payload,
  }) async {
    _validateOpaqueId(executionId, 'executionId', 'overrideAtom');
    _validateNonEmptyId(atomId, 'atomId', 'overrideAtom');

    final response = await _dio.patch<Map<String, Object?>>(
      '/execution/executions/$executionId/atoms/$atomId/override',
      data: payload.toJson(),
    );
    return _parseResponse(
      response,
      GenericStatusResponseDto.fromJson,
      'overrideAtom',
    );
  }
}
