import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for ConfigurationOutputsApi
void main() {
  final instance = BackendApi().getConfigurationOutputsApi();

  group(ConfigurationOutputsApi, () {
    // Create Output Config
    //
    // Creates a new output configuration.
    //
    //Future<String> createOutputV1ConfigOutputsPost(ConfigComponentResponse configComponentResponse) async
    test('test createOutputV1ConfigOutputsPost', () async {
      // TODO
    });

    // Delete Output Config
    //
    // Deletes an output configuration.
    //
    //Future<bool> deleteOutputV1ConfigOutputsOutputIdDelete(String outputId) async
    test('test deleteOutputV1ConfigOutputsOutputIdDelete', () async {
      // TODO
    });

    // Get Output Configuration
    //
    // Retrieves a single output configuration by ID.  Args:     repo: Repository dependency.     output_id: Unique identifier for the output config.  Returns:     The matched config component.  Raises:     ResourceNotFoundError: If the config does not exist.
    //
    //Future<ConfigComponentResponse> getOutputV1ConfigOutputsOutputIdGet(String outputId) async
    test('test getOutputV1ConfigOutputsOutputIdGet', () async {
      // TODO
    });

    // List Output Configurations
    //
    // Retrieves all defined output configurations.  Args:     repo: Repository dependency.  Returns:     List of output config components.  Raises:     AppException: If retrieval fails.
    //
    //Future<List<ConfigComponentResponse>> getOutputsV1ConfigOutputsGet() async
    test('test getOutputsV1ConfigOutputsGet', () async {
      // TODO
    });

    // Update Output Config
    //
    // Updates an existing output configuration.
    //
    //Future<bool> updateOutputV1ConfigOutputsOutputIdPut(String outputId, ComponentUpdate componentUpdate) async
    test('test updateOutputV1ConfigOutputsOutputIdPut', () async {
      // TODO
    });
  });
}
