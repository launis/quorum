import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for ConfigurationDimensionsApi
void main() {
  final instance = BackendApi().getConfigurationDimensionsApi();

  group(ConfigurationDimensionsApi, () {
    // Create Dimension
    //
    // Creates a new evaluation dimension.
    //
    //Future<String> createDimensionV1ConfigDimensionsPost(DimensionDefinition dimensionDefinition) async
    test('test createDimensionV1ConfigDimensionsPost', () async {
      // TODO
    });

    // Delete Dimension
    //
    // Deletes an evaluation dimension.
    //
    //Future<bool> deleteDimensionV1ConfigDimensionsDimensionIdDelete(String dimensionId) async
    test('test deleteDimensionV1ConfigDimensionsDimensionIdDelete', () async {
      // TODO
    });

    // Get Dimension
    //
    // Retrieves a single evaluation dimension by ID.  Args:     repo: Repository dependency.     dimension_id: Unique identifier for the dimension.  Returns:     The matched dimension component.  Raises:     ResourceNotFoundError: If the dimension does not exist.
    //
    //Future<DimensionDefinition> getDimensionV1ConfigDimensionsDimensionIdGet(String dimensionId) async
    test('test getDimensionV1ConfigDimensionsDimensionIdGet', () async {
      // TODO
    });

    // List Dimensions
    //
    // Retrieves all defined evaluation dimensions.  Args:     repo: Repository dependency.  Returns:     List of dimension components.  Raises:     AppException: If retrieval fails.
    //
    //Future<List<DimensionDefinition>> getDimensionsV1ConfigDimensionsGet() async
    test('test getDimensionsV1ConfigDimensionsGet', () async {
      // TODO
    });

    // Update Dimension
    //
    // Updates an existing evaluation dimension.
    //
    //Future<bool> updateDimensionV1ConfigDimensionsDimensionIdPut(String dimensionId, ComponentUpdate componentUpdate) async
    test('test updateDimensionV1ConfigDimensionsDimensionIdPut', () async {
      // TODO
    });

  });
}
