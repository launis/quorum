import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_repository.g.dart';

@Riverpod(keepAlive: true)
WorkflowRepository workflowRepository(Ref ref) {
  return WorkflowRepository(ref.watch(apiClientProvider));
}

class WorkflowRepository {
  final Dio _client;

  WorkflowRepository(this._client);

  AppError _mapError(Object error) {
    if (error is DioException) {
      if (error.response != null) {
        final statusCode = error.response!.statusCode;
        final data = error.response!.data;
        final message = data is Map ? data['detail'] as String? : null;

        return AppError.server(message ?? 'Server error', statusCode);
      }
      return AppError.network(error);
    }
    return AppError.unknown(error);
  }

  /// Fetches all visible workflows from the backend.
  ///
  /// Endpoint: `GET /builder/workflows`
  TaskEither<AppError, List<Workflow>> fetchWorkflows() {
    return TaskEither.tryCatch(() async {
      final response = await _client.get<List<dynamic>>('/builder/workflows');

      final data = response.data as List<dynamic>;
      return data
          .map((json) => Workflow.fromJson(json as Map<String, dynamic>))
          .toList();
    }, (error, stackTrace) => _mapError(error));
  }
}
