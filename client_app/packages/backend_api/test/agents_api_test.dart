import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for AgentsApi
void main() {
  final instance = BackendApi().getAgentsApi();

  group(AgentsApi, () {
    // List All Agents
    //
    // List all available agents with their metadata, models, and schemas.  Dynamically resolves model strategy based on the selected workflow configuration.  Args:     workflow_id (Optional[str]): Context for model resolution.     registry (RegistryDep): Injected registry service.  Returns:     List[AgentDefinition]: A list of agent definition objects.
    //
    //Future<List<AgentDefinition>> listAgentsAgentsGet({ String workflowId }) async
    test('test listAgentsAgentsGet', () async {
      // TODO
    });

    // Run Specific Agent
    //
    // Executes a specific agent in isolation with provided inputs.  Args:     agent_name (str): The class name of the agent to run.     inputs (Dict[str, Any]): Input data for the agent's context.     system_instruction (Optional[str]): optional prompt override.     model (Optional[str]): optional model override (strategy key or model name).     repo (RepositoryDep): Database repository.     registry (RegistryDep): Registry dependency for strategy resolution.  Returns:     AgentRunResponse: A DTO containing the execution result.  Raises:     ResourceNotFoundError: If the agent class cannot be loaded.     AppException: If execution fails (400 for validation, 500 for runtime).
    //
    //Future<AgentRunResponse> runAgentAgentsAgentNameRunPost(String agentName, BodyRunAgentAgentsAgentNameRunPost bodyRunAgentAgentsAgentNameRunPost) async
    test('test runAgentAgentsAgentNameRunPost', () async {
      // TODO
    });

  });
}
