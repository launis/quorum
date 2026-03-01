import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:client_app/features/orchestration/domain/models/report_view.dart';
import 'package:flutter/foundation.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:client_app/core/network/sse_client.dart';
import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/domain/models/assessment_view.dart';

part 'execution_repository.g.dart';

/// Repository for managing Audit Execution data.
///
/// Handles interaction with the `/executions` endpoints of the backend API.
/// Uses strict functional error handling via [TaskEither] and [AppError].
@Riverpod(keepAlive: true)
ExecutionRepository executionRepository(Ref ref) {
  return ExecutionRepository(ref.watch(apiClientProvider));
}

class ExecutionRepository {
  final Dio _client;

  ExecutionRepository(this._client);

  /// Helper to map strict Dio errors to [AppError].
  AppError _mapError(Object error) {
    if (error is DioException) {
      if (error.response != null) {
        final statusCode = error.response!.statusCode;
        final data = error.response!.data;
        // Strict API Contract: 'error_code' is the machine-readable key.
        // 'detail' or 'message' is for debugging only.
        final errorCode = data is Map ? data['error_code'] as String? : null;
        final message =
            data is Map ? (data['message'] ?? data['detail']) as String? : null;

        switch (statusCode) {
          case 401:
            return const AppError.unauthorized();
          case 404:
            return AppError.notFound(message ?? 'Resource not found');
          case 400:
          case 422:
            final reason = _mapValidationReason(errorCode);
            return AppError.validation(reason);
          case 500:
          default:
            return AppError.server(message ?? 'Server error', statusCode);
        }
      } else if (error.type == DioExceptionType.connectionTimeout ||
          error.type == DioExceptionType.receiveTimeout) {
        return AppError.network(error);
      }
    }
    return AppError.unknown(error);
  }

  /// Maps backend error strings to strict [ValidationErrorReason] enum.
  ValidationErrorReason _mapValidationReason(String? code) {
    if (code == null) return ValidationErrorReason.unknown;

    return switch (code.toUpperCase()) {
      'VALIDATION_ERROR' ||
      'VALUE_ERROR' ||
      'EMPTY_INPUT' => ValidationErrorReason.emptyInput,
      'INVALID_EMAIL' => ValidationErrorReason.invalidEmail,
      'WEAK_PASSWORD' ||
      'PASSWORD_TOO_SHORT' => ValidationErrorReason.passwordTooWeak,
      'INVALID_DATE' => ValidationErrorReason.invalidDate,
      _ => ValidationErrorReason.unknown,
    };
  }

  /// Initiates a new workflow execution.
  ///
  /// Endpoint: `POST /executions`
  ///
  /// Business Logic:
  /// - Sends `workflow_id` and `inputs` as form-data (to match backend expectation).
  /// - Returns the created execution ID.
  TaskEither<AppError, String> createExecution(ExecutionInput input) {
    return TaskEither.tryCatch(() async {
      // 1. Resolve inputs and encode files to Base64
      final resolvedInputs = <String, dynamic>{
        ...input.inputs,
      };

      for (final entry in input.files.entries) {
        final file = entry.value;
        List<int>? bytes = file.bytes;

        // Fallback to IO if bytes are missing (usually on Desktop/Mobile when picking large files)
        if (bytes == null && !kIsWeb && file.path != null) {
          final ioFile = File(file.path!);
          bytes = await ioFile.readAsBytes();
        }

        if (bytes == null) {
          // CRITICAL FIX: Prevent silent dropping of files (which causes Backend 400).
          throw const AppError.validation(ValidationErrorReason.emptyInput);
        }

        resolvedInputs[entry.key] = {
          'filename': file.name,
          'mime_type': 'application/octet-stream', // Can be refined if needed
          'content_base64': base64Encode(bytes),
        };
      }

      // 2. Build Strict JSON Pydantic-compatible Payload
      final executionRequest = {
        'workflow_id': input.workflowId,
        'organization_id': null, // Organization injected by backend optionally
        'inputs': resolvedInputs,
      };

      // 3. Send as standard application/json
      final response = await _client.post<Map<String, dynamic>>(
        '/executions',
        data: executionRequest,
      );

      final data = response.data!;
      return data['id'] as String;
    }, (error, stackTrace) => _mapError(error));
  }

  /// Cancels a running workflow execution.
  ///
  /// Endpoint: `DELETE /executions/{id}/cancel`
  TaskEither<AppError, void> cancelExecution(String id) {
    return TaskEither.tryCatch(() async {
      await _client.delete('/executions/$id/cancel');
    }, (error, stackTrace) => _mapError(error));
  }

  /// Deletes an execution permanently.
  ///
  /// Endpoint: `DELETE /executions/{id}`
  TaskEither<AppError, void> deleteExecution(String id) {
    return TaskEither.tryCatch(() async {
      await _client.delete('/executions/$id');
    }, (error, stackTrace) => _mapError(error));
  }

  /// Fetches the most recent executions from the backend.
  ///
  /// Endpoint: `GET /executions/recent`
  /// Query Params:
  /// - `limit`: Optional limit on number of results (default 5).
  TaskEither<AppError, List<Execution>> fetchExecutions({int limit = 5}) {
    return TaskEither.tryCatch(() async {
      final response = await _client.get<List<dynamic>>(
        '/executions/recent',
        queryParameters: {'limit': limit},
      );

      final List<dynamic> data = response.data as List<dynamic>;
      return data
          .map((json) => Execution.fromJson(json as Map<String, dynamic>))
          .toList();
    }, (error, stackTrace) => _mapError(error));
  }

  /// Fetches a single execution by ID.
  ///
  /// Endpoint: `GET /executions/{id}`
  TaskEither<AppError, Execution> getExecution(String id) {
    return TaskEither.tryCatch(() async {
      final response = await _client.get<Map<String, dynamic>>(
        '/executions/$id',
      );
      return Execution.fromJson(response.data!);
    }, (error, stackTrace) => _mapError(error));
  }

  /// Streams the execution status by polling the API.
  ///
  /// Yields updates every [interval] until the execution reaches a terminal state.
  /// Terminal states: completed, failed, rejected, interrupted.
  /// Streams the execution status via SSE (Server-Sent Events).
  ///
  /// Endpoint: `GET /executions/{id}/events`
  Stream<Execution> streamExecution(String id) {
    // Request RAW view for full Execution model
    final url = '/executions/$id/events?view=raw';

    // We utilize the SseClient helper
    final stream = SseClient.connect<Execution>(
      url: url,
      parser: (json) => Execution.fromJson(json),
      dio: _client,
    );

    return stream;
  }

  /// Streams the execution as an AssessmentView (BFF).
  ///
  /// Endpoint: `GET /executions/{id}/events`
  Stream<AssessmentView> streamAssessment(String id) {
    // Request ASSESSMENT view for UI-optimized model
    final url = '/executions/$id/events?view=assessment';

    return SseClient.connect<AssessmentView>(
      url: url,
      parser: (json) => AssessmentView.fromJson(json),
      dio: _client,
    );
  }

  /// Checks if the status is final/terminal.
  bool _isTerminal(ExecutionStatus status) {
    return switch (status) {
      ExecutionStatus.completed ||
      ExecutionStatus.failed ||
      ExecutionStatus.rejected ||
      ExecutionStatus.interrupted => true,
      _ => false,
    };
  }

  /// Fetches complete raw execution data for debugging/reporting.
  ///
  /// Endpoint: `GET /executions/{id}/raw`
  ///
  /// Returns:
  /// - All agent outputs (step_guard, step_analyst, etc.)
  /// - Hook outputs (aux_data)
  /// - Timing information (duration_seconds)
  /// - Full workflow state
  TaskEither<AppError, Map<String, dynamic>> getRawExecutionData(String id) {
    return TaskEither.tryCatch(() async {
      final response = await _client.get<Map<String, dynamic>>(
        '/executions/$id/raw',
      );
      return response.data!;
      return response.data!;
    }, (error, stackTrace) => _mapError(error));
  }

  /// Fetches the UI View Report (BFF) for an execution.
  ///
  /// Endpoint: `GET /executions/{id}/view`
  TaskEither<AppError, ReportView> getReportView(String id) {
    return TaskEither.tryCatch(() async {
      final response = await _client.get<Map<String, dynamic>>(
        '/executions/$id/view',
      );
      debugPrint(
        '[ExecutionRepository] getReportView($id) SUCCESS: ${response.statusCode}',
      );
      return ReportView.fromJson(response.data!);
    }, (error, stackTrace) => _mapError(error));
  }
}
