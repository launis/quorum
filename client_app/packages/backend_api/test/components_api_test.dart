import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for ComponentsApi
void main() {
  final instance = BackendApi().getComponentsApi();

  group(ComponentsApi, () {
    // Create Component
    //
    // Creates a new configuration component.
    //
    //Future<TextComponentResponse> createComponentV1ConfigComponentsPost(ComponentCreate componentCreate) async
    test('test createComponentV1ConfigComponentsPost', () async {
      // TODO
    });

    // Delete Component
    //
    // Deletes a component if it is not referenced by any existing steps OR executions.
    //
    //Future<ComponentDeleteResponse> deleteComponentV1ConfigComponentsCompIdDelete(String compId) async
    test('test deleteComponentV1ConfigComponentsCompIdDelete', () async {
      // TODO
    });

    // Get Component
    //
    // Retrieves a single component by ID or Name.
    //
    //Future<TextComponentResponse> getComponentV1ConfigComponentsCompIdGet(String compId) async
    test('test getComponentV1ConfigComponentsCompIdGet', () async {
      // TODO
    });

    // List Components
    //
    // Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).  Args:     repo (RepositoryDep): Repository dependency.     type (str | None): Optional filter by component type.     exclude_type (list[str] | None): Optional types to exclude (defaults to agents/processors).  Returns:     list[ComponentResponse]: List of configuration components.
    //
    //Future<List<TextComponentResponse>> getComponentsV1ConfigComponentsGet({ String type, List<String> excludeType }) async
    test('test getComponentsV1ConfigComponentsGet', () async {
      // TODO
    });

    // List Registry Components
    //
    // Retrieves all system components directly from the Repository.
    //
    //Future<List<RegistryComponentItem>> listRegistryItemsV1ConfigComponentsRegistryItemsGet() async
    test('test listRegistryItemsV1ConfigComponentsRegistryItemsGet', () async {
      // TODO
    });

    // Update Component
    //
    // Updates an existing component's content and metadata.  Args:     comp_id (str): The ID of the component to update.     update (ComponentUpdate): The new data.     repo (RepositoryDep): Repository dependency.  Returns:     ComponentResponse: The updated component.  Raises:     HTTPException: If not found (404).
    //
    //Future<TextComponentResponse> updateComponentV1ConfigComponentsCompIdPut(String compId, ComponentUpdate componentUpdate) async
    test('test updateComponentV1ConfigComponentsCompIdPut', () async {
      // TODO
    });

  });
}
