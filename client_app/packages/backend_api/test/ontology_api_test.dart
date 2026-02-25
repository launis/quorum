import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for OntologyApi
void main() {
  final instance = BackendApi().getOntologyApi();

  group(OntologyApi, () {
    // Delete Dimension
    //
    // Deletes a dimension if it is not used in any matrix.
    //
    //Future<DimensionDeleteResponse> deleteDimensionV1ConfigOntologyDimensionsDimIdDelete(String dimId) async
    test('test deleteDimensionV1ConfigOntologyDimensionsDimIdDelete', () async {
      // TODO
    });

    // Delete Dimension
    //
    // Deletes a dimension if it is not used in any matrix.
    //
    //Future<DimensionDeleteResponse> deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0(String dimId) async
    test('test deleteDimensionV1ConfigOntologyDimensionsDimIdDelete_0', () async {
      // TODO
    });

    // Get Known Dimensions
    //
    // Returns specific allowed dimension IDs from the ontology table.  Auto-seeds defaults if table is empty.  Args:     repo (RepositoryDep): Repository dependency.  Returns:     list[DimensionDefinition]: Sorted list of dimensions.
    //
    //Future<List<DimensionDefinition>> getKnownDimensionsV1ConfigOntologyDimensionsGet() async
    test('test getKnownDimensionsV1ConfigOntologyDimensionsGet', () async {
      // TODO
    });

    // Get Known Dimensions
    //
    // Returns specific allowed dimension IDs from the ontology table.  Auto-seeds defaults if table is empty.  Args:     repo (RepositoryDep): Repository dependency.  Returns:     list[DimensionDefinition]: Sorted list of dimensions.
    //
    //Future<List<DimensionDefinition>> getKnownDimensionsV1ConfigOntologyDimensionsGet_0() async
    test('test getKnownDimensionsV1ConfigOntologyDimensionsGet_0', () async {
      // TODO
    });

    // Update Dimension
    //
    // Updates an existing dimension.
    //
    //Future<DimensionDefinition> updateDimensionV1ConfigOntologyDimensionsDimIdPut(String dimId, DimensionDefinition dimensionDefinition) async
    test('test updateDimensionV1ConfigOntologyDimensionsDimIdPut', () async {
      // TODO
    });

    // Update Dimension
    //
    // Updates an existing dimension.
    //
    //Future<DimensionDefinition> updateDimensionV1ConfigOntologyDimensionsDimIdPut_0(String dimId, DimensionDefinition dimensionDefinition) async
    test('test updateDimensionV1ConfigOntologyDimensionsDimIdPut_0', () async {
      // TODO
    });

  });
}
