import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for ConfigModelsApi
void main() {
  final instance = BackendApi().getConfigModelsApi();

  group(ConfigModelsApi, () {
    // Delete Model Config
    //
    // Delete a specific provider strategy configuration.  Enforces Reference Integrity (Workflow Usage) and System Integrity (Default Strategy). Strictly requires 'provider/strategy' format.
    //
    //Future deleteModelConfigV1ConfigModelsProviderIdDelete(String providerId) async
    test('test deleteModelConfigV1ConfigModelsProviderIdDelete', () async {
      // TODO
    });

    // Get Agent Mappings
    //
    // Get the current Agent to Model Strategy mappings. Returns: dict[str, str] mapping Agent IDs to \"provider/strategy\" strings.
    //
    //Future<Map<String, String>> getAgentMappingsV1ConfigModelsMappingsGet() async
    test('test getAgentMappingsV1ConfigModelsMappingsGet', () async {
      // TODO
    });

    // List Model Options
    //
    // Fetch available model options from external providers (Google, OpenAI).
    //
    //Future<ModelOptionsResponse> listModelOptionsV1ConfigModelsOptionsGet() async
    test('test listModelOptionsV1ConfigModelsOptionsGet', () async {
      // TODO
    });

    // List Models
    //
    // List all available LLM providers and their current configuration.  Supports nested structure: models[provider][strategy]. Returns flattened list with id=\"{provider}/{strategy}\".
    //
    //Future<List<LLMProviderConfig>> listModelsV1ConfigModelsGet() async
    test('test listModelsV1ConfigModelsGet', () async {
      // TODO
    });

    // Test Model Connection
    //
    // Execute an ephemeral LLM request to test credentials/latency.  Does NOT use the database configuration unless strategy_id is specifically requested. Returns status=\"error\" instead of 500 for expected connection failures (User Feedback).
    //
    //Future<AdHocTestResponse> testModelConnectionV1ConfigModelsTestPost(AdHocTestRequest adHocTestRequest) async
    test('test testModelConnectionV1ConfigModelsTestPost', () async {
      // TODO
    });

    // Update Agent Mappings
    //
    // Update Agent to Model Strategy mappings.  Expects dict mapping Agent IDs to \"provider/strategy\" strings.
    //
    //Future<Map<String, String>> updateAgentMappingsV1ConfigModelsMappingsPut(Map<String, String> requestBody) async
    test('test updateAgentMappingsV1ConfigModelsMappingsPut', () async {
      // TODO
    });

    // Update Model Config
    //
    // Update configuration for a specific provider strategy.  'provider_id' MUST be complex path 'provider/strategy'. Legacy flat IDs are strictly rejected.
    //
    //Future<LLMProviderConfig> updateModelConfigV1ConfigModelsProviderIdPut(String providerId, LLMProviderConfig lLMProviderConfig) async
    test('test updateModelConfigV1ConfigModelsProviderIdPut', () async {
      // TODO
    });

  });
}
