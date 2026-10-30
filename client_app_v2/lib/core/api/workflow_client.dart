import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_client.g.dart';

/// Workflow API Client Provider
@Riverpod(keepAlive: true)
WorkflowClient workflowClient(Ref ref) {
  return WorkflowClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with the V2 Workflows API.
class WorkflowClient {
  final Dio _dio;
  final LoggerService? _logger;
  static const StrictOpaqueIdConverter _idValidator = StrictOpaqueIdConverter();

  WorkflowClient(this._dio, [this._logger]);

  /// Fetches the dynamically required inputs UI schema for a specific workflow.
  Future<WorkflowUiSchema> getWorkflowUiSchema(String workflowId) async {
    try {
      _idValidator.fromJson(workflowId);
    } on AppException catch (e, st) {
      _logger?.error(
        'WorkflowClient',
        'Invalid workflowId format "$workflowId" for getWorkflowUiSchema',
        e,
        st,
      );
      rethrow;
    }

    final response = await _dio.get('studio/workflows/$workflowId/ui_schema');
    return WorkflowUiSchema.fromJson(response.data);
  }
}
