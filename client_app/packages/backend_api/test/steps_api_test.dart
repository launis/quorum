import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for StepsApi
void main() {
  final instance = BackendApi().getStepsApi();

  group(StepsApi, () {
    // Create Step
    //
    // Creates a new step. Pydantic validator adapts legacy input to DB schema.
    //
    //Future<StepDefinition> createStepV1ConfigStepsPost(StepDefinition stepDefinition) async
    test('test createStepV1ConfigStepsPost', () async {
      // TODO
    });

    // Delete Step
    //
    // Deletes a step.
    //
    //Future<StepDeleteResponse> deleteStepV1ConfigStepsStepIdDelete(String stepId) async
    test('test deleteStepV1ConfigStepsStepIdDelete', () async {
      // TODO
    });

    // Get Step
    //
    // Retrieves a single step by ID.
    //
    //Future<StepDefinition> getStepV1ConfigStepsStepIdGet(String stepId) async
    test('test getStepV1ConfigStepsStepIdGet', () async {
      // TODO
    });

    // List Steps
    //
    // Retrieves all defined steps. Pydantic model handles adaptation automatically.
    //
    //Future<List<StepDefinition>> getStepsV1ConfigStepsGet() async
    test('test getStepsV1ConfigStepsGet', () async {
      // TODO
    });

    // Update Step
    //
    // Updates an existing step.
    //
    //Future<StepDefinition> updateStepV1ConfigStepsStepIdPut(String stepId, StepDefinition stepDefinition) async
    test('test updateStepV1ConfigStepsStepIdPut', () async {
      // TODO
    });
  });
}
