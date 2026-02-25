import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for ExecutionV1Api
void main() {
  final instance = BackendApi().getExecutionV1Api();

  group(ExecutionV1Api, () {
    // Create Execution
    //
    // Creates a new execution for a given workflow.
    //
    //Future<ExecutionResponse> createExecutionV1ExecutePost({ String authorization }) async
    test('test createExecutionV1ExecutePost', () async {
      // TODO
    });

    // Delete Execution
    //
    // Delete an execution record.
    //
    //Future<ExecutionDeleteResponse> deleteExecutionV1ExecuteExecutionIdDelete(String executionId, { String authorization }) async
    test('test deleteExecutionV1ExecuteExecutionIdDelete', () async {
      // TODO
    });

    // Execute a Workflow (Direct)
    //
    // Direct execution endpoint.
    //
    //Future<Map<String, Object>> executeWorkflowRouteV1ExecuteWorkflowIdPost(String workflowId, Map<String, Object> requestBody) async
    test('test executeWorkflowRouteV1ExecuteWorkflowIdPost', () async {
      // TODO
    });

  });
}
