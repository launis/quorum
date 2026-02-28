import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for ConfigurationMatricesApi
void main() {
  final instance = BackendApi().getConfigurationMatricesApi();

  group(ConfigurationMatricesApi, () {
    // Create Matrix
    //
    // Creates a new evaluation matrix.
    //
    //Future<String> createMatrixV1ConfigMatricesPost(MatrixComponentResponse matrixComponentResponse) async
    test('test createMatrixV1ConfigMatricesPost', () async {
      // TODO
    });

    // Delete Matrix
    //
    // Deletes an evaluation matrix.
    //
    //Future<bool> deleteMatrixV1ConfigMatricesMatrixIdDelete(String matrixId) async
    test('test deleteMatrixV1ConfigMatricesMatrixIdDelete', () async {
      // TODO
    });

    // List Matrices
    //
    // Retrieves all defined evaluation matrices.  Args:     repo: Repository dependency.  Returns:     List of matrix components.  Raises:     AppException: If retrieval fails.
    //
    //Future<List<MatrixComponentResponse>> getMatricesV1ConfigMatricesGet() async
    test('test getMatricesV1ConfigMatricesGet', () async {
      // TODO
    });

    // Get Matrix
    //
    // Retrieves a single evaluation matrix by ID.  Args:     repo: Repository dependency.     matrix_id: Unique identifier for the matrix.  Returns:     The matched matrix component.  Raises:     ResourceNotFoundError: If the matrix does not exist.
    //
    //Future<MatrixComponentResponse> getMatrixV1ConfigMatricesMatrixIdGet(String matrixId) async
    test('test getMatrixV1ConfigMatricesMatrixIdGet', () async {
      // TODO
    });

    // Update Matrix
    //
    // Updates an existing evaluation matrix.
    //
    //Future<bool> updateMatrixV1ConfigMatricesMatrixIdPut(String matrixId, ComponentUpdate componentUpdate) async
    test('test updateMatrixV1ConfigMatricesMatrixIdPut', () async {
      // TODO
    });
  });
}
