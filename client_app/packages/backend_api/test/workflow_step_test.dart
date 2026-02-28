import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

// tests for WorkflowStep
void main() {
  final WorkflowStep? instance = /* WorkflowStep(...) */ null;
  // TODO add properties to the entity

  group(WorkflowStep, () {
    // Unique step identifier, e.g., 'safety_check'
    // String id
    test('to test the property `id`', () async {
      // TODO
    });

    // String slug
    test('to test the property `slug`', () async {
      // TODO
    });

    // Human-readable name of the step
    // String name
    test('to test the property `name`', () async {
      // TODO
    });

    // String description
    test('to test the property `description`', () async {
      // TODO
    });

    // Registry Task Name (matches @register_task name)
    // String taskKey
    test('to test the property `taskKey`', () async {
      // TODO
    });

    // Maps task inputs to state values. Example: {'text': '$inputs.history_text'}
    // Map<String, String> inputs
    test('to test the property `inputs`', () async {
      // TODO
    });

    // Optional static config for the task
    // Map<String, Object> config
    test('to test the property `config`', () async {
      // TODO
    });

    // UI Helper: True if this step references a task_key not in the backend registry.
    // bool isMissingRegistry (default value: false)
    test('to test the property `isMissingRegistry`', () async {
      // TODO
    });
  });
}
