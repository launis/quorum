# backend_api.api.ExecutionV1Api

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createExecutionV1ExecutePost**](ExecutionV1Api.md#createexecutionv1executepost) | **POST** /v1/execute/ | Create Execution
[**deleteExecutionV1ExecuteExecutionIdDelete**](ExecutionV1Api.md#deleteexecutionv1executeexecutioniddelete) | **DELETE** /v1/execute/{execution_id} | Delete Execution
[**executeWorkflowRouteV1ExecuteWorkflowIdPost**](ExecutionV1Api.md#executeworkflowroutev1executeworkflowidpost) | **POST** /v1/execute/{workflow_id} | Execute a Workflow (Direct)


# **createExecutionV1ExecutePost**
> ExecutionResponse createExecutionV1ExecutePost(authorization)

Create Execution

Creates a new execution for a given workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionV1Api();
final String authorization = authorization_example; // String | 

try {
    final response = api.createExecutionV1ExecutePost(authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionV1Api->createExecutionV1ExecutePost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionResponse**](ExecutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteExecutionV1ExecuteExecutionIdDelete**
> ExecutionDeleteResponse deleteExecutionV1ExecuteExecutionIdDelete(executionId, authorization)

Delete Execution

Delete an execution record.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionV1Api();
final String executionId = executionId_example; // String | 
final String authorization = authorization_example; // String | 

try {
    final response = api.deleteExecutionV1ExecuteExecutionIdDelete(executionId, authorization);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionV1Api->deleteExecutionV1ExecuteExecutionIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **executionId** | **String**|  | 
 **authorization** | **String**|  | [optional] 

### Return type

[**ExecutionDeleteResponse**](ExecutionDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **executeWorkflowRouteV1ExecuteWorkflowIdPost**
> Map<String, Object> executeWorkflowRouteV1ExecuteWorkflowIdPost(workflowId, requestBody)

Execute a Workflow (Direct)

Direct execution endpoint.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getExecutionV1Api();
final String workflowId = workflowId_example; // String | 
final Map<String, Object> requestBody = Object; // Map<String, Object> | 

try {
    final response = api.executeWorkflowRouteV1ExecuteWorkflowIdPost(workflowId, requestBody);
    print(response);
} on DioException catch (e) {
    print('Exception when calling ExecutionV1Api->executeWorkflowRouteV1ExecuteWorkflowIdPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowId** | **String**|  | 
 **requestBody** | [**Map&lt;String, Object&gt;**](Object.md)|  | 

### Return type

**Map&lt;String, Object&gt;**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

