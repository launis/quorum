import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'execution_repository.g.dart';

/// **Execution Repository Provider**
///
/// The single source of truth for accessing Execution data.
/// It abstracts the underlying API network calls and serialization logic.
@riverpod
ExecutionRepository executionRepository(Ref ref) {
  return ExecutionRepository(ref.watch(apiClientProvider));
}

/// **Execution Data Repository**
///
/// Handles all CRUD operations related to [Execution] entities.
///
/// **Responsibility**:
/// - Connects to the `/executions` API endpoints.
/// - Handles serialization of JSON responses into [Execution] domain objects.
/// - Maps network errors (e.g., DioError) into domain-specific exceptions (planned).
class ExecutionRepository {
  final Dio _client;

  /// Creates the repository with the authenticated [_client].
  ExecutionRepository(this._client);

  /// **Fetch Recent Executions**
  ///
  /// Retrieves a list of the most recent workflow executions, scoped to the user's organization.
  ///
  /// **Business Logic**:
  /// - The backend automatically applies multi-tenant scoping based on the User's Role.
  /// - Returns a list sorted by `start_time` descending.
  ///
  /// **Parameters**:
  /// - [limit]: The maximum number of records to return (default: 5).
  ///
  /// **Returns**:
  /// A Future containing a list of [Execution] objects.
  Future<List<Execution>> fetchRecentExecutions({int limit = 5}) async {
    try {
      final response = await _client.get<List<dynamic>>(
        '/executions/recent',
        queryParameters: {'limit': limit},
      );

      final list = response.data ?? [];
      return list
          .map((json) => Execution.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      // In a real app, map DioError to DomainError using fpdart.
      // For now, rethrow or return empty.
      rethrow;
    }
  }

  /// **Start Execution** (Placeholder)
  ///
  /// Initiates a new workflow execution.
  ///
  /// **Note**:
  /// Currently strictly defined to support future implementation. Current mandate
  /// focuses on `fetchRecentExecutions`.
  Future<String> startExecution({
    required String workflowId,
    Map<String, dynamic> inputs = const {},
  }) async {
    // Implementation deferred to Phase 3
    return 'implemented_later';
  }
}
