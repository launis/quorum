import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_client.g.dart';

// Execution & Time-Bound Task Assignment API Client.

/// Execution API Client Provider
@Riverpod(keepAlive: true)
ExecutionClient executionClient(Ref ref) {
  return ExecutionClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with the V2 Executions and Task Assignments API.
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

  /// Lists workflow execution assignments scoped to the authenticated user/organization.
  Future<List<ExecutionAssignmentResponseDto>> listAssignments() async {
    final response = await _dio.get<List<Object?>>(
      '/execution/executions/assignments',
    );
    final items = response.data;
    if (items == null) {
      final error = AppException.validation(
        'Null response payload received in ExecutionClient.listAssignments',
      );
      _logger?.error(
        'ExecutionClient',
        'Null response data for listAssignments',
        error,
        StackTrace.current,
      );
      throw error;
    }
    final results = <ExecutionAssignmentResponseDto>[];
    for (final item in items) {
      if (item is Map<String, Object?>) {
        results.add(ExecutionAssignmentResponseDto.fromJson(item));
      }
    }
    return results;
  }

  /// Creates a single time-bound workflow execution assignment.
  Future<ExecutionAssignmentResponseDto> createAssignment(
    ExecutionAssignmentCreateDto payload,
  ) async {
    _validateOpaqueId(payload.workflowId, 'workflowId', 'createAssignment');
    if (payload.outputProfileId != null) {
      _validateOpaqueId(
        payload.outputProfileId!,
        'outputProfileId',
        'createAssignment',
      );
    }

    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/assignments',
      data: payload.toJson(),
    );
    return _parseResponse(
      response,
      ExecutionAssignmentResponseDto.fromJson,
      'createAssignment',
    );
  }

  /// Creates a cohort batch (1 to 500 recipients) of time-bound workflow execution assignments.
  Future<ExecutionAssignmentBatchResponseDto> createAssignmentBatch(
    ExecutionAssignmentBatchCreateDto payload,
  ) async {
    _validateOpaqueId(
      payload.workflowId,
      'workflowId',
      'createAssignmentBatch',
    );
    if (payload.outputProfileId != null) {
      _validateOpaqueId(
        payload.outputProfileId!,
        'outputProfileId',
        'createAssignmentBatch',
      );
    }

    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/assignments/batch',
      data: payload.toJson(),
    );
    return _parseResponse(
      response,
      ExecutionAssignmentBatchResponseDto.fromJson,
      'createAssignmentBatch',
    );
  }

  /// Fetches SafeLinks-immune read-only preview metadata for a task assignment token.
  Future<ExecutionAssignmentPreviewDto> previewAssignment(String token) async {
    _validateNonEmptyId(token, 'token', 'previewAssignment');
    final encoded = Uri.encodeQueryComponent(token.trim());
    final response = await _dio.get<Map<String, Object?>>(
      '/execution/executions/assignments/preview?token=$encoded',
    );
    return _parseResponse(
      response,
      ExecutionAssignmentPreviewDto.fromJson,
      'previewAssignment',
    );
  }

  /// Executes combined Just-In-Time (JIT) user onboarding + 2FA for a task assignee.
  Future<TokenExchangeResponseDto> onboardAssignee({
    required String token,
    required ExecutionAssignmentOnboardingRequestDto payload,
  }) async {
    _validateNonEmptyId(token, 'token', 'onboardAssignee');
    final encoded = Uri.encodeQueryComponent(token.trim());
    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/assignments/onboard?token=$encoded',
      data: payload.toJson(),
    );
    return _parseResponse(
      response,
      TokenExchangeResponseDto.fromJson,
      'onboardAssignee',
    );
  }

  /// Rotates the assignment token and resends the task magic-link email.
  Future<ExecutionAssignmentResponseDto> resendAssignmentEmail(
    String assignmentId,
  ) async {
    _validateOpaqueId(assignmentId, 'assignmentId', 'resendAssignmentEmail');
    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/assignments/$assignmentId/resend',
    );
    return _parseResponse(
      response,
      ExecutionAssignmentResponseDto.fromJson,
      'resendAssignmentEmail',
    );
  }

  /// Explicitly activates a task assignment and starts its relative countdown timer.
  Future<ExecutionAssignmentResponseDto> activateAssignment(
    String assignmentId,
  ) async {
    _validateOpaqueId(assignmentId, 'assignmentId', 'activateAssignment');
    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/assignments/$assignmentId/activate',
    );
    return _parseResponse(
      response,
      ExecutionAssignmentResponseDto.fromJson,
      'activateAssignment',
    );
  }

  /// Auto-saves assignee draft inputs on an active task assignment.
  Future<ExecutionAssignmentResponseDto> saveAssignmentDraft({
    required String assignmentId,
    required ExecutionAssignmentDraftDto payload,
  }) async {
    _validateOpaqueId(assignmentId, 'assignmentId', 'saveAssignmentDraft');
    final response = await _dio.put<Map<String, Object?>>(
      '/execution/executions/assignments/$assignmentId/draft',
      data: payload.toJson(),
    );
    return _parseResponse(
      response,
      ExecutionAssignmentResponseDto.fromJson,
      'saveAssignmentDraft',
    );
  }

  /// Submits the final assignee inputs and starts the workflow execution.
  Future<ExecutionRecord> submitAssignment({
    required String assignmentId,
    required ExecutionAssignmentSubmitDto payload,
  }) async {
    _validateOpaqueId(assignmentId, 'assignmentId', 'submitAssignment');
    final response = await _dio.post<Map<String, Object?>>(
      '/execution/executions/assignments/$assignmentId/submit',
      data: payload.toJson(),
    );
    return _parseResponse(
      response,
      ExecutionRecord.fromJson,
      'submitAssignment',
    );
  }
}
