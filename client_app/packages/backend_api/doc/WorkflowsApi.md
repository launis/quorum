# backend_api.api.WorkflowsApi

## Load the API package
```dart
import 'package:backend_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**createWorkflowV1ConfigWorkflowsPost**](WorkflowsApi.md#createworkflowv1configworkflowspost) | **POST** /v1/config/workflows | Create Workflow
[**deleteWorkflowV1ConfigWorkflowsWfIdDelete**](WorkflowsApi.md#deleteworkflowv1configworkflowswfiddelete) | **DELETE** /v1/config/workflows/{wf_id} | Delete Workflow
[**getWorkflowV1ConfigWorkflowsWfIdGet**](WorkflowsApi.md#getworkflowv1configworkflowswfidget) | **GET** /v1/config/workflows/{wf_id} | Get Workflow
[**getWorkflowsV1ConfigWorkflowsGet**](WorkflowsApi.md#getworkflowsv1configworkflowsget) | **GET** /v1/config/workflows | List Workflows
[**updateWorkflowV1ConfigWorkflowsWfIdPut**](WorkflowsApi.md#updateworkflowv1configworkflowswfidput) | **PUT** /v1/config/workflows/{wf_id} | Update Workflow
[**validateFlowV1ConfigWorkflowsValidateFlowPost**](WorkflowsApi.md#validateflowv1configworkflowsvalidateflowpost) | **POST** /v1/config/workflows/validate-flow | Validate Flow


# **createWorkflowV1ConfigWorkflowsPost**
> WorkflowConfigDefinition createWorkflowV1ConfigWorkflowsPost(workflowConfigCreate)

Create Workflow

Create a new workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getWorkflowsApi();
final WorkflowConfigCreate workflowConfigCreate = ; // WorkflowConfigCreate | 

try {
    final response = api.createWorkflowV1ConfigWorkflowsPost(workflowConfigCreate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling WorkflowsApi->createWorkflowV1ConfigWorkflowsPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowConfigCreate** | [**WorkflowConfigCreate**](WorkflowConfigCreate.md)|  | 

### Return type

[**WorkflowConfigDefinition**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteWorkflowV1ConfigWorkflowsWfIdDelete**
> ConfigWorkflowDeleteResponse deleteWorkflowV1ConfigWorkflowsWfIdDelete(wfId)

Delete Workflow

Delete a workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getWorkflowsApi();
final String wfId = wfId_example; // String | 

try {
    final response = api.deleteWorkflowV1ConfigWorkflowsWfIdDelete(wfId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling WorkflowsApi->deleteWorkflowV1ConfigWorkflowsWfIdDelete: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wfId** | **String**|  | 

### Return type

[**ConfigWorkflowDeleteResponse**](ConfigWorkflowDeleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWorkflowV1ConfigWorkflowsWfIdGet**
> WorkflowConfigDefinition getWorkflowV1ConfigWorkflowsWfIdGet(wfId)

Get Workflow

Get a specific workflow.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getWorkflowsApi();
final String wfId = wfId_example; // String | 

try {
    final response = api.getWorkflowV1ConfigWorkflowsWfIdGet(wfId);
    print(response);
} on DioException catch (e) {
    print('Exception when calling WorkflowsApi->getWorkflowV1ConfigWorkflowsWfIdGet: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wfId** | **String**|  | 

### Return type

[**WorkflowConfigDefinition**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWorkflowsV1ConfigWorkflowsGet**
> List<WorkflowConfigDefinition> getWorkflowsV1ConfigWorkflowsGet()

List Workflows

List all workflows.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getWorkflowsApi();

try {
    final response = api.getWorkflowsV1ConfigWorkflowsGet();
    print(response);
} on DioException catch (e) {
    print('Exception when calling WorkflowsApi->getWorkflowsV1ConfigWorkflowsGet: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**List&lt;WorkflowConfigDefinition&gt;**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateWorkflowV1ConfigWorkflowsWfIdPut**
> WorkflowConfigDefinition updateWorkflowV1ConfigWorkflowsWfIdPut(wfId, workflowConfigUpdate)

Update Workflow

Update a workflow definition.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getWorkflowsApi();
final String wfId = wfId_example; // String | 
final WorkflowConfigUpdate workflowConfigUpdate = ; // WorkflowConfigUpdate | 

try {
    final response = api.updateWorkflowV1ConfigWorkflowsWfIdPut(wfId, workflowConfigUpdate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling WorkflowsApi->updateWorkflowV1ConfigWorkflowsWfIdPut: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wfId** | **String**|  | 
 **workflowConfigUpdate** | [**WorkflowConfigUpdate**](WorkflowConfigUpdate.md)|  | 

### Return type

[**WorkflowConfigDefinition**](WorkflowConfigDefinition.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validateFlowV1ConfigWorkflowsValidateFlowPost**
> ValidationReportResponse validateFlowV1ConfigWorkflowsValidateFlowPost(workflowConfigCreate)

Validate Flow

Dry run validation.

### Example
```dart
import 'package:backend_api/api.dart';

final api = BackendApi().getWorkflowsApi();
final WorkflowConfigCreate workflowConfigCreate = ; // WorkflowConfigCreate | 

try {
    final response = api.validateFlowV1ConfigWorkflowsValidateFlowPost(workflowConfigCreate);
    print(response);
} on DioException catch (e) {
    print('Exception when calling WorkflowsApi->validateFlowV1ConfigWorkflowsValidateFlowPost: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflowConfigCreate** | [**WorkflowConfigCreate**](WorkflowConfigCreate.md)|  | 

### Return type

[**ValidationReportResponse**](ValidationReportResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

