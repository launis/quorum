import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for WorkflowsApi
void main() {
  final instance = BackendApi().getWorkflowsApi();

  group(WorkflowsApi, () {
    // Create Workflow
    //
    // Create a new workflow.
    //
    //Future<WorkflowConfigDefinition> createWorkflowV1ConfigWorkflowsPost(WorkflowConfigCreate workflowConfigCreate) async
    test('test createWorkflowV1ConfigWorkflowsPost', () async {
      // TODO
    });

    // Delete Workflow
    //
    // Delete a workflow.
    //
    //Future<ConfigWorkflowDeleteResponse> deleteWorkflowV1ConfigWorkflowsWfIdDelete(String wfId) async
    test('test deleteWorkflowV1ConfigWorkflowsWfIdDelete', () async {
      // TODO
    });

    // Get Workflow
    //
    // Get a specific workflow.
    //
    //Future<WorkflowConfigDefinition> getWorkflowV1ConfigWorkflowsWfIdGet(String wfId) async
    test('test getWorkflowV1ConfigWorkflowsWfIdGet', () async {
      // TODO
    });

    // List Workflows
    //
    // List all workflows.
    //
    //Future<List<WorkflowConfigDefinition>> getWorkflowsV1ConfigWorkflowsGet() async
    test('test getWorkflowsV1ConfigWorkflowsGet', () async {
      // TODO
    });

    // Update Workflow
    //
    // Update a workflow definition.
    //
    //Future<WorkflowConfigDefinition> updateWorkflowV1ConfigWorkflowsWfIdPut(String wfId, WorkflowConfigUpdate workflowConfigUpdate) async
    test('test updateWorkflowV1ConfigWorkflowsWfIdPut', () async {
      // TODO
    });

    // Validate Flow
    //
    // Dry run validation.
    //
    //Future<ValidationReportResponse> validateFlowV1ConfigWorkflowsValidateFlowPost(WorkflowConfigCreate workflowConfigCreate) async
    test('test validateFlowV1ConfigWorkflowsValidateFlowPost', () async {
      // TODO
    });
  });
}
