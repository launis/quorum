# backend_api.api.AgentsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**listAgentsAgentsGet**](AgentsApi.md#listagentsagentsget) | **GET** /agents/ | List All Agents
[**runAgentAgentsAgentNameRunPost**](AgentsApi.md#runagentagentsagentnamerunpost) | **POST** /agents/{agent_name}/run | Run Specific Agent


# **listAgentsAgentsGet**
> List<AgentDefinition> listAgentsAgentsGet(workflowId)

List All Agents

List all available agents with their metadata, models, and schemas.  Dynamically resolves model strategy based on the selected workflow configuration.  Args:     workflow_id (Optional[str]): Context for model resolution.     registry (RegistryDep): Injected registry service.  Returns:     List[AgentDefinition]: A list of agent definition objects.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAgentsApi();
final String workflowId = workflowId_example; // String | Optional Workflow ID to resolve model strategies contextually.

try {
    final response = api.listAgentsAgentsGet(workflowId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AgentsApi->listAgentsAgentsGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**| Optional Workflow ID to resolve model strategies contextually. | [optional] 

### Return type

[**List&lt;AgentDefinition&gt;**](AgentDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **runAgentAgentsAgentNameRunPost**
> AgentRunResponse runAgentAgentsAgentNameRunPost(agentName, bodyRunAgentAgentsAgentNameRunPost)

Run Specific Agent

Executes a specific agent in isolation with provided inputs.  Args:     agent_name (str): The class name of the agent to run.     inputs (Dict[str, Any]): Input data for the agent's context.     system_instruction (Optional[str]): optional prompt override.     model (Optional[str]): optional model override (strategy key or model name).     repo (RepositoryDep): Database repository.     registry (RegistryDep): Registry dependency for strategy resolution.  Returns:     AgentRunResponse: A DTO containing the execution result.  Raises:     ResourceNotFoundError: If the agent class cannot be loaded.     AppException: If execution fails (400 for validation, 500 for runtime).

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getAgentsApi();
final String agentName = agentName_example; // String | 
final BodyRunAgentAgentsAgentNameRunPost bodyRunAgentAgentsAgentNameRunPost = ; // BodyRunAgentAgentsAgentNameRunPost | 

try {
    final response = api.runAgentAgentsAgentNameRunPost(agentName, bodyRunAgentAgentsAgentNameRunPost);
    print(response);
} on DioException catch (e) {
    print('Exception when calling AgentsApi->runAgentAgentsAgentNameRunPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentName** | **String**|  | 
 **bodyRunAgentAgentsAgentNameRunPost** | [**BodyRunAgentAgentsAgentNameRunPost**](BodyRunAgentAgentsAgentNameRunPost.md)|  | 

### Return type

[**AgentRunResponse**](AgentRunResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

