import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for ConfigurationAgentsApi
void main() {
  final instance = BackendApi().getConfigurationAgentsApi();

  group(ConfigurationAgentsApi, () {
    // Create Agent
    //
    // Creates a new AI agent.
    //
    //Future<String> createAgentV1ConfigAgentsPost(AgentComponentResponse agentComponentResponse) async
    test('test createAgentV1ConfigAgentsPost', () async {
      // TODO
    });

    // Delete Agent
    //
    // Deletes an AI agent.
    //
    //Future<bool> deleteAgentV1ConfigAgentsAgentIdDelete(String agentId) async
    test('test deleteAgentV1ConfigAgentsAgentIdDelete', () async {
      // TODO
    });

    // Get Agent
    //
    // Retrieves a single AI agent by ID.  Args:     repo: Repository dependency.     agent_id: Unique identifier for the agent.  Returns:     The matched agent component.      Raises:     ResourceNotFoundError: If the agent does not exist.
    //
    //Future<AgentComponentResponse> getAgentV1ConfigAgentsAgentIdGet(String agentId) async
    test('test getAgentV1ConfigAgentsAgentIdGet', () async {
      // TODO
    });

    // List Agents
    //
    // Retrieves all defined AI agents.  Args:     repo: Repository dependency.  Returns:     List of agent components.  Raises:     AppException: If retrieval fails.
    //
    //Future<List<AgentComponentResponse>> getAgentsV1ConfigAgentsGet() async
    test('test getAgentsV1ConfigAgentsGet', () async {
      // TODO
    });

    // Update Agent
    //
    // Updates an existing AI agent.
    //
    //Future<bool> updateAgentV1ConfigAgentsAgentIdPut(String agentId, ComponentUpdate componentUpdate) async
    test('test updateAgentV1ConfigAgentsAgentIdPut', () async {
      // TODO
    });
  });
}
