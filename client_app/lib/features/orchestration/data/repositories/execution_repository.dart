import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';

import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';

part 'execution_repository.g.dart';

/// Repository for managing Audit Execution data.
///
/// Handles interaction with the `/executions` endpoints of the backend API.
/// Uses strict functional error handling via [TaskEither].
@Riverpod(keepAlive: true)
ExecutionRepository executionRepository(Ref ref) {
  return ExecutionRepository(ref.watch(apiClientProvider));
}

class ExecutionRepository {
  final Dio _client;

  ExecutionRepository(this._client);

  /// Fetches the most recent executions from the backend.
  ///
  /// Endpoint: `GET /executions/recent`
  /// Query Params:
  /// - `limit`: Optional limit on number of results (default 5).
  ///
  /// Returns a [TaskEither] containing:
  /// - Left: [Exception] (Network error, Server error)
  /// - Right: [List<Execution>] (Success)
  TaskEither<Exception, List<Execution>> fetchExecutions({int limit = 5}) {
    return TaskEither.tryCatch(
      () async {
        final response = await _client.get<List<dynamic>>(
          '/executions/recent',
          queryParameters: {'limit': limit},
        );

        final List<dynamic> data = response.data as List<dynamic>;
        return data
            .map((json) => Execution.fromJson(json as Map<String, dynamic>))
            .toList();
      },
      (error, stackTrace) {
        // TODO: Map to domain specific exceptions if needed
        return Exception('Failed to fetch executions: $error');
      },
    );
  }

  /// Fetches a single execution by ID.
  ///
  /// Endpoint: `GET /executions/{id}`
  TaskEither<Exception, Execution> getExecution(String id) {
    return TaskEither.tryCatch(
      () async {
        final response = await _client.get<Map<String, dynamic>>(
          '/executions/$id',
        );
        return Execution.fromJson(response.data!);
      },
      (error, stackTrace) => Exception('Failed to fetch execution $id: $error'),
    );
  }
}
