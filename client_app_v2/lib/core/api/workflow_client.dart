import 'package:dio/dio.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_client.g.dart';

/// Workflow API Client Provider
@riverpod
WorkflowClient workflowClient(Ref ref) {
  return WorkflowClient(ref.watch(apiClientProvider));
}

/// Client for interacting with the V2 Workflows API.
class WorkflowClient {
  final Dio _dio;

  WorkflowClient(this._dio);

  /// Fetches the dynamically required inputs UI schema for a specific workflow.
  Future<WorkflowUiSchema> getWorkflowUiSchema(String workflowId) async {
    final response = await _dio.get('/api/v2/workflows/$workflowId/ui_schema');
    return WorkflowUiSchema.fromJson(response.data as Map<String, dynamic>);
  }
}
