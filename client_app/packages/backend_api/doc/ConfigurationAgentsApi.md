# backend_api.api.ConfigurationAgentsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createAgentV1ConfigAgentsPost**](ConfigurationAgentsApi.md#createagentv1configagentspost) | **POST** /v1/config/agents | Create Agent
[**deleteAgentV1ConfigAgentsAgentIdDelete**](ConfigurationAgentsApi.md#deleteagentv1configagentsagentiddelete) | **DELETE** /v1/config/agents/{agent_id} | Delete Agent
[**getAgentV1ConfigAgentsAgentIdGet**](ConfigurationAgentsApi.md#getagentv1configagentsagentidget) | **GET** /v1/config/agents/{agent_id} | Get Agent
[**getAgentsV1ConfigAgentsGet**](ConfigurationAgentsApi.md#getagentsv1configagentsget) | **GET** /v1/config/agents | List Agents
[**updateAgentV1ConfigAgentsAgentIdPut**](ConfigurationAgentsApi.md#updateagentv1configagentsagentidput) | **PUT** /v1/config/agents/{agent_id} | Update Agent


# **createAgentV1ConfigAgentsPost**
> String createAgentV1ConfigAgentsPost(agentComponentResponse)

Create Agent

Creates a new AI agent.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationAgentsApi();
final AgentComponentResponse agentComponentResponse = ; // AgentComponentResponse | 

try {
    final response = api.createAgentV1ConfigAgentsPost(agentComponentResponse);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationAgentsApi->createAgentV1ConfigAgentsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentComponentResponse** | [**AgentComponentResponse**](AgentComponentResponse.md)|  | 

### Return type

**String**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteAgentV1ConfigAgentsAgentIdDelete**
> bool deleteAgentV1ConfigAgentsAgentIdDelete(agentId)

Delete Agent

Deletes an AI agent.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationAgentsApi();
final String agentId = agentId_example; // String | 

try {
    final response = api.deleteAgentV1ConfigAgentsAgentIdDelete(agentId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationAgentsApi->deleteAgentV1ConfigAgentsAgentIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentId** | **String**|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentV1ConfigAgentsAgentIdGet**
> AgentComponentResponse getAgentV1ConfigAgentsAgentIdGet(agentId)

Get Agent

Retrieves a single AI agent by ID.  Args:     repo: Repository dependency.     agent_id: Unique identifier for the agent.  Returns:     The matched agent component.      Raises:     ResourceNotFoundError: If the agent does not exist.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationAgentsApi();
final String agentId = agentId_example; // String | Agent ID

try {
    final response = api.getAgentV1ConfigAgentsAgentIdGet(agentId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationAgentsApi->getAgentV1ConfigAgentsAgentIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentId** | **String**| Agent ID | 

### Return type

[**AgentComponentResponse**](AgentComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentsV1ConfigAgentsGet**
> List<AgentComponentResponse> getAgentsV1ConfigAgentsGet()

List Agents

Retrieves all defined AI agents.  Args:     repo: Repository dependency.  Returns:     List of agent components.  Raises:     AppException: If retrieval fails.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationAgentsApi();

try {
    final response = api.getAgentsV1ConfigAgentsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationAgentsApi->getAgentsV1ConfigAgentsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;AgentComponentResponse&gt;**](AgentComponentResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAgentV1ConfigAgentsAgentIdPut**
> bool updateAgentV1ConfigAgentsAgentIdPut(agentId, componentUpdate)

Update Agent

Updates an existing AI agent.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getConfigurationAgentsApi();
final String agentId = agentId_example; // String | 
final ComponentUpdate componentUpdate = ; // ComponentUpdate | 

try {
    final response = api.updateAgentV1ConfigAgentsAgentIdPut(agentId, componentUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ConfigurationAgentsApi->updateAgentV1ConfigAgentsAgentIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentId** | **String**|  | 
 **componentUpdate** | [**ComponentUpdate**](ComponentUpdate.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

