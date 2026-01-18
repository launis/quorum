import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/domain/models/execution_input.dart';

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
      // Backend expects 'json_payload' field containing the ExecutionRequest schema
      final executionRequest = {
        'project_id': input.workflowId,
        'settings': input.inputs,
        'description': null, // Optional
      };

      final formDataMap = <String, dynamic>{
        'json_payload': jsonEncode(executionRequest),
      };

      // Add files if present
      for (final entry in input.files.entries) {
        final file = entry.value;
        // Web Safety & OOM Prevention:
        // 1. Prefer bytes if available (Enforced by 'withData: true' for reliability).
        // 2. Fallback to path on IO if bytes missing.
        if (file.bytes != null) {
          formDataMap[entry.key] = MultipartFile.fromBytes(
            file.bytes!,
            filename: file.name,
          );
        } else if (!kIsWeb && file.path != null) {
           formDataMap[entry.key] = await MultipartFile.fromFile(
            file.path!,
            filename: file.name,
          );
        } else {
          // CRITICAL FIX: Prevent silent dropping of files (which causes Backend 400).
          // If neither path (IO) nor bytes (Web/Other) are available, the file is invalid.
          throw const AppError.validation(ValidationErrorReason.emptyInput);
        }
      }

      final formData = FormData.fromMap(formDataMap);

      final response = await _client.post<Map<String, dynamic>>(
        '/executions',
        data: formData,
      );

      final data = response.data as Map<String, dynamic>;
      return data['execution_id'] as String;
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
  Stream<Either<AppError, Execution>> streamExecution(
    String id, {
    Duration interval = const Duration(seconds: 2),
  }) async* {
    while (true) {
      final result = await getExecution(id).run();

      yield result;

      // Check for terminal state to stop polling
      final shouldStop = result.match(
        (error) => true, // Stop on error (or maybe retry? simplistic for now)
        (execution) => _isTerminal(execution.status),
      );

      if (shouldStop) break;

      await Future<void>.delayed(interval);
    }
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
    }, (error, stackTrace) => _mapError(error));
  }
}
